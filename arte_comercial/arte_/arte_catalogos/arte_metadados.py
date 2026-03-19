import os
import json
import time
import pandas as pd
import google.generativeai as genai
import google.api_core.exceptions
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import pdfplumber
from openpyxl import load_workbook
import itertools

# Carrega as variáveis de ambiente
load_dotenv()

# Carrega todas as chaves da API e cria um iterador cíclico
API_KEYS = [value for name, value in os.environ.items() if name.startswith("GOOGLE_API_KEY")]
if not API_KEYS:
    raise ValueError("Nenhuma chave no formato 'GOOGLE_API_KEY...' encontrada no arquivo .env.")
print(f"Encontradas {len(API_KEYS)} chaves de API para usar em rotação.")
API_KEY_CYCLE = itertools.cycle(API_KEYS)

# --- CONSTANTES DE DIRETÓRIO ---
ROOT_DIR = Path(__file__).parent.parent
DOWNLOADS_DIR = ROOT_DIR / "DOWNLOADS"
CATALOGS_DIR = DOWNLOADS_DIR / "CATALOGOS"
METADATA_OUTPUT_DIR = DOWNLOADS_DIR / "METADADOS"
OUTPUT_FILE = METADATA_OUTPUT_DIR / "produtos_metadados_v2_hibrido.xlsx"

# --- TAXONOMIA DE PRODUTOS ---
CATEGORIAS_PRODUTOS = {
    "EQUIPAMENTO_AUDIO": ["interface_audio","mesa_som_mixer","mesa_analogica","sistema_iem","processador_dsp","pedal_efeitos","fone_ouvido"],
    "MICROFONE": ["microfone_dinamico","microfone_condensador","microfone_instrumento","microfone_sem_fio","microfone_lapela","microfone_shotgun","microfone_gooseneck"],
    "EQUIPAMENTO_SOM" : ["caixa_som_passiva","caixa_som_ativa","sistema_array","amplificador_potencia","caixa_som_portatil"],
    "INSTRUMENTO_SOPRO": ["corneta","cornetão","tuba","saxofone","trompa","bombardino","trombone","flugelhorn","trompete","flauta","clarinete","oboé","pianica"],
    "INSTRUMENTO_CORDA": ["violao","violino","contra_baixo","guitarra","ukulele","violoncelo","acessorio_instrumento_corda","acessorio_cordas","cavaquinho","viola"],
    "INSTRUMENTO_TECLADO": ["piano_acustico","piano_digital","sintetizador","controlador_midi","glockenspiel","metalofone","acordeon" ],
    "INSTRUMENTO_PERCUSSAO": ["bateria_acustica","bateria_eletronica","sextoton","quintoton","quadriton","repinique","tantan","rebolo","surdo_mao","cuica","zabumba","caixa_guerra","bombo_fanfarra","lira_marcha","tarol","malacacheta","caixa_bateria","pandeiro","tamborim","reco_reco","agogô","triangulo","chocalho","afuche","cajon","bongo","conga","djembé","timbal","atabaque","berimbau","tam_tam","caxixi","carilhao","xequerê","prato","xilofone"],
    "ACESSORIO_MUSICAL": ["suporte_instrumento","pele_percussao","talabarte","case_bag","carrinho_transporte","suporte_microfone","cabos_audio","banco_teclado","pedal_bumbo","palheta","afinador","metronomo","estante_partitura","bocal_trompete","baqueta","surdina","chimbal_hihat","capotraste","captador_instrumento","bateria_acessorio","carregador_bateria","bateria_recarregavel","arco_instrumento_corda","cordas","acessorio_iluminacao","estandarte","oleo_lubrificante","cabeçote_amplificado","arco_instrumento","fonte_energia"],
    "EQUIPAMENTO_TECNICO": ["ssd","fonte_energia","switch_rede","projetor","drone","iluminacao_de_palco","iluminacao_led","iluminador_led"]
}

# --- FUNÇÃO DE CHAMADA À API COM FALLBACK ---
def call_gemini_with_fallback(prompt_parts: list, generation_config: dict, request_options: dict) -> genai.types.GenerateContentResponse | None:
    """Tenta chamar a API com as chaves em rotação, pulando para a próxima em caso de erro de cota."""
    for _ in range(len(API_KEYS)): # Tenta no máximo o número de chaves disponíveis
        try:
            key = next(API_KEY_CYCLE)
            tqdm.write(f"  - Usando chave de API: ...{key[-4:]}")
            genai.configure(api_key=key)
            
            model = genai.GenerativeModel(model_name="gemini-2.5-flash", generation_config=generation_config)
            
            response = model.generate_content(prompt_parts, request_options=request_options)
            return response # Sucesso, retorna a resposta

        except google.api_core.exceptions.ResourceExhausted as e:
            tqdm.write(f"  - [AVISO] Cota da chave ...{key[-4:]} excedida. Tentando próxima chave...")
            time.sleep(2) # Pausa antes de tentar a próxima
            continue # Tenta a próxima chave no loop
        except Exception as e:
            tqdm.write(f"\n  - [ERRO] Ocorreu um erro inesperado com a chave ...{key[-4:]}: {e}")
            tqdm.write("  - Tentando próxima chave...")
            time.sleep(5)
            continue
            
    tqdm.write("\n[ERRO CRÍTICO] Todas as chaves de API falharam ou atingiram a cota. Não é possível continuar a chamada.")
    return None


# --- PROMPT PARA O MODELO GEMINI (SCHEMA HÍBRIDO) ---
def get_page_prompt(page_number: int, total_pages: int, marca: str, taxonomia_str: str) -> str:
    """Gera uma prompt específica para a extração de dados de uma única página com o novo schema."""
    return f"""
    Você é um Engenheiro de Dados especialista em VLM e taxonomia de produtos.
    Sua tarefa é analisar o catálogo em PDF anexado, focando EXCLUSIVAMENTE no conteúdo da PÁGINA {page_number} de um total de {total_pages} páginas, para extrair e estruturar os produtos em um SCHEMA HÍBRIDO.

    MARCA DO ARQUIVO: {marca}
    
    TAXONOMIA OBRIGATÓRIA:
    {taxonomia_str}

    INSTRUÇÕES DE EXTRAÇÃO E ESTRUTURAÇÃO (PROCESSO EM 2 ETAPAS):
    
    **ETAPA 1: CURADORIA E ENRIQUECIMENTO (GERAÇÃO DO CAMPO 'METADADOS')**
    Para cada produto encontrado APENAS NESTA PÁGINA, aja como um especialista técnico. Use as informações do PDF como ponto de partida para gerar uma descrição técnica DETALHADA e ENRIQUECIDA no campo 'METADADOS'.
    
    METODOLOGIA DE PESQUISA E VALIDAÇÃO (OBRIGATÓRIA):
    1.  Valide e complete dados técnicos (dimensões, peso, materiais) usando seu conhecimento de manuais técnicos e fontes confiáveis.
    2.  Seja agressivo na busca por informações faltantes.
    3.  Priorize fatos técnicos verificáveis.
    
    ESTRUTURA DA DESCRIÇÃO ENRIQUECIDA ('METADADOS'):
    [FUNÇÃO PRINCIPAL] - [CATEGORIA TÉCNICA] com [CARACTERÍSTICAS PRINCIPAIS]. Especificações: [DETALHES TÉCNICOS]. Construção: [MATERIAIS].
    
    **ETAPA 2: ESTRUTURAÇÃO FINAL (GERAÇÃO DO JSON 'ESPECIFICACOES')**
    Após gerar o campo 'METADADOS', use-o como fonte única para preencher o objeto JSON 'ESPECIFICACOES'.
    - Extraia CADA ESPECIFICAÇÃO TÉCNICA do campo 'METADADOS' e transforme-a em um par chave-valor dentro do JSON.
    - O campo 'DESCRICAO_PDF' deve conter o texto original extraído do documento.

    FORMATO DE SAÍDA FINAL (ARRAY DE OBJETOS JSON):
    O resultado DEVE ser uma única lista (array) de objetos JSON contendo APENAS os 8 campos: MARCA, MODELO, PRECO, DESCRICAO_PDF, METADADOS, categoria_principal, subcategoria, ESPECIFICACOES.
    Se nenhum produto for encontrado na página, retorne uma lista vazia `[]`.

    EXEMPLO DE SAÍDA PARA UM ITEM:
    {{
      "MARCA": "MICHAEL",
      "MODELO": "VM19E",
      "PRECO": 540.00,
      "DESCRICAO_PDF": "Violão Clássico Acústico Michael Antares VM19E - Cordas em Nylon",
      "METADADOS": "Violão clássico acústico para estudo, tamanho 4/4. Tampo em Spruce, laterais/fundo em Linden. Braço em Basswood com tensor 'Dual Action'. Escala e cavalete em Dark Maple. Cordas de nylon. Comprimento total 990.6mm.",
      "categoria_principal": "INSTRUMENTO_CORDA",
      "subcategoria": "violao",
      "ESPECIFICACOES": {{
        "material_tampo": "Spruce",
        "formato_corpo": "Clássico",
        "tipo_corda": "Nylon",
        "tensor": "Dual Action"
      }}
    }}
    
    Assegure-se de que a saída seja APENAS o array JSON, sem nenhum texto, explicação ou ```json ``` adicionais.
    JSON:
    """

def clean_json_response(text: str) -> list:
    """Limpa a resposta do modelo para garantir que seja um JSON válido."""
    try:
        cleaned_text = text.strip().replace("```json", "").replace("```", "").strip()
        if not cleaned_text:
            return []
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print(f"\n[AVISO] Erro ao decodificar JSON. Resposta do modelo pode estar mal formatada ou vazia. Erro: {e}")
        return []

def append_to_excel(df_new: pd.DataFrame, output_path: Path):
    """Anexa um DataFrame a um arquivo Excel de forma eficiente, criando ou adicionando sem reescrever."""
    if df_new.empty:
        return

    # Novo schema de colunas
    cols_order = [
        'catalogo_origem', 'pagina_origem', 'MARCA', 'MODELO', 'PRECO', 
        'DESCRICAO_PDF', 'METADADOS', 'categoria_principal', 'subcategoria', 'ESPECIFICACOES'
    ]

    # Garante que o dataframe a ser salvo tenha todas as colunas na ordem certa
    for col in cols_order:
        if col not in df_new.columns:
            df_new[col] = pd.NA
    df_new = df_new[cols_order]

    try:
        if not output_path.exists():
            df_new.to_excel(output_path, index=False, engine='openpyxl')
        else:
            with pd.ExcelWriter(output_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                startrow = writer.sheets['Sheet1'].max_row
                df_new.to_excel(writer, startrow=startrow, index=False, header=False, sheet_name='Sheet1')
    except Exception as e:
        print(f"\n[ERRO] Falha ao salvar dados no Excel: {e}")


def process_catalog_pdf_iteratively(pdf_path: Path, processed_pages: set, generation_config: dict):
    """
    Processa um catálogo PDF página por página, com o novo prompt, pulando páginas
    já processadas e salvando os resultados incrementalmente.
    """
    print(f"\nIniciando processamento para: {pdf_path.name}")
    uploaded_file = None
    
    marca_arquivo = pdf_path.stem.split('_')[0].upper()
    taxonomia_str = json.dumps(CATEGORIAS_PRODUTOS, indent=2, ensure_ascii=False)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
        print(f"  - O documento tem {total_pages} páginas.")

        if all((pdf_path.name, i) in processed_pages for i in range(1, total_pages + 1)):
            print(f"  - Todas as páginas de {pdf_path.name} já foram processadas. Pulando arquivo.")
            return

        print("  - Fazendo upload do arquivo para a File API...")
        # Usa a função de chamada com fallback para o upload também
        response_file = call_gemini_with_fallback(prompt_parts=[pdf_path], generation_config=generation_config, request_options={})
        
        # A API de upload é diferente, vamos simplificar
        key = next(API_KEY_CYCLE)
        genai.configure(api_key=key)
        uploaded_file = genai.upload_file(path=pdf_path, display_name=pdf_path.name)
        print(f"  - Upload concluído com a chave ...{key[-4:]}")

        for page_num in tqdm(range(1, total_pages + 1), desc=f"Analisando {pdf_path.name}", unit="página"):
            if (pdf_path.name, page_num) in processed_pages:
                tqdm.write(f"  - Página {page_num} de {pdf_path.name} já processada. Pulando.")
                continue

            page_prompt = get_page_prompt(page_num, total_pages, marca_arquivo, taxonomia_str)
            
            # Usa a nova função de chamada com fallback
            response = call_gemini_with_fallback(
                prompt_parts=[page_prompt, uploaded_file],
                generation_config=generation_config,
                request_options={'timeout': 600}
            )

            if response:
                products_on_page = clean_json_response(response.text)
                if products_on_page:
                    for product in products_on_page:
                        if 'ESPECIFICACOES' in product and isinstance(product['ESPECIFICACOES'], dict):
                            product['ESPECIFICACOES'] = json.dumps(product['ESPECIFICACOES'])
                    
                    df_page = pd.DataFrame(products_on_page)
                    df_page['catalogo_origem'] = pdf_path.name
                    df_page['pagina_origem'] = page_num
                    append_to_excel(df_page, OUTPUT_FILE)
                
                processed_pages.add((pdf_path.name, page_num))
                tqdm.write(f"  - Página {page_num} processada com sucesso.")
            else:
                 tqdm.write(f"\n  - [FALHA] Falha ao processar a página {page_num} após tentar todas as chaves de API.")

            time.sleep(2)

    except Exception as e:
        print(f"\nOcorreu um erro crítico ao processar o arquivo {pdf_path.name}: {e}")
    
    finally:
        if uploaded_file:
            try:
                # Usa a mesma chave que fez o upload para deletar
                print(f"\n  - Deletando arquivo da API: {uploaded_file.name}")
                genai.delete_file(uploaded_file.name)
            except Exception as delete_error:
                print(f"  - [AVISO] Falha ao deletar arquivo da API: {delete_error}")

def main():
    """
    Função principal para orquestrar a extração de metadados, com sistema de memória
    e salvamento incremental.
    """
    print("Iniciando o processo de extração de metadados de catálogos PDF...")
    METADATA_OUTPUT_DIR.mkdir(exist_ok=True)

    processed_pages = set()
    if OUTPUT_FILE.exists():
        try:
            print(f"Lendo arquivo de saída existente para carregar a memória: {OUTPUT_FILE}")
            df_existing = pd.read_excel(OUTPUT_FILE, engine='openpyxl')
            if 'catalogo_origem' in df_existing.columns and 'pagina_origem' in df_existing.columns:
                for _, row in df_existing.iterrows():
                    if pd.notna(row['catalogo_origem']) and pd.notna(row['pagina_origem']):
                        processed_pages.add((row['catalogo_origem'], int(row['pagina_origem'])))
            print(f"Memória carregada. {len(processed_pages)} páginas já foram processadas anteriormente.")
        except Exception as e:
            print(f"[AVISO] Não foi possível ler o arquivo Excel existente para carregar a memória: {e}")

    generation_config = { "temperature": 0.1, "top_p": 0.95, "top_k": 0 }

    pdf_files = sorted(list(CATALOGS_DIR.glob("*.pdf")))
    if not pdf_files:
        print(f"Nenhum arquivo PDF encontrado em: {CATALOGS_DIR}")
        return
    print(f"Encontrados {len(pdf_files)} catálogos em PDF para processar.")

    for pdf_path in pdf_files:
        process_catalog_pdf_iteratively(pdf_path, processed_pages, generation_config)
        print("\n----------------------------------------------------")
    
    print("\n✅ Processo concluído! Todos os catálogos foram analisados.")
    print(f"Os metadados estão salvos em: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
