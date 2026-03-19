import os
import json
import time
import pandas as pd
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import pdfplumber

# =====================================================================
# CONFIGURAÇÕES E CONSTANTES
# =====================================================================

load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Erro ao configurar a API do Gemini. Verifique sua GOOGLE_API_KEY no .env: {e}")
    exit()

# --- ARQUIVOS DE ENTRADA E SAÍDA ---
PDF_ANALISAR = Path(r"C:\Users\pietr\OneDrive\.vscode\arte_\DOWNLOADS\EDITAIS\980139_900022026\termo_referencia_limpo.pdf")# Coloque o PDF na mesma pasta do script
OUTPUT_DIR = Path(__file__).parent
OUTPUT_FILE = OUTPUT_DIR / "edital_resultado_robusto.xlsx"

# --- TAXONOMIA DE PRODUTOS ---
CATEGORIAS_PRODUTOS = {
    "EQUIPAMENTO_AUDIO": ["interface_audio", "mesa_som_mixer", "mesa_analogica", "sistema_iem", "processador_dsp", "pedal_efeitos", "fone_ouvido"],
    "MICROFONE": ["microfone_dinamico", "microfone_condensador", "microfone_instrumento", "microfone_sem_fio", "microfone_lapela", "microfone_shotgun", "microfone_gooseneck"],
    "EQUIPAMENTO_SOM": ["caixa_som_passiva", "caixa_som_ativa", "sistema_array", "amplificador_potencia", "caixa_som_portatil"],
    "INSTRUMENTO_SOPRO": ["corneta", "cornetão", "tuba", "saxofone", "trompa", "bombardino", "trombone", "flugelhorn", "trompete", "flauta", "clarinete", "oboé", "pianica"],
    "INSTRUMENTO_CORDA": ["violao", "violino", "contra_baixo", "guitarra", "ukulele", "violoncelo", "acessorio_instrumento_corda", "acessorio_cordas", "cavaquinho", "viola"],
    "INSTRUMENTO_TECLADO": ["piano_acustico", "piano_digital", "sintetizador", "controlador_midi", "glockenspiel", "metalofone", "acordeon"],
    "INSTRUMENTO_PERCUSSAO": ["bateria_acustica", "bateria_eletronica", "sextoton", "quintoton", "quadriton", "repinique", "tantan", "rebolo", "surdo_mao", "cuica", "zabumba", "caixa_guerra", "bombo_fanfarra", "lira_marcha", "tarol", "malacacheta", "caixa_bateria", "pandeiro", "tamborim", "reco_reco", "agogô", "triangulo", "chocalho", "afuche", "cajon", "bongo", "conga", "djembé", "timbal", "atabaque", "berimbau", "tam_tam", "caxixi", "carilhao", "xequerê", "prato", "xilofone"],
    "ACESSORIO_MUSICAL": ["suporte_instrumento", "pele_percussao", "talabarte", "case_bag", "carrinho_transporte", "suporte_microfone", "cabos_audio", "banco_teclado", "pedal_bumbo", "palheta", "afinador", "metronomo", "estante_partitura", "bocal_trompete", "baqueta", "surdina", "chimbal_hihat", "capotraste", "captador_instrumento", "bateria_acessorio", "carregador_bateria", "bateria_recarregavel", "arco_instrumento_corda", "cordas", "acessorio_iluminacao", "estandarte", "oleo_lubrificante", "cabeçote_amplificado", "arco_instrumento", "fonte_energia"],
    "EQUIPAMENTO_TECNICO": ["ssd", "fonte_energia", "switch_rede", "projetor", "drone", "iluminacao_de_palco", "iluminacao_led", "iluminador_led"]
}

# =====================================================================
# FUNÇÕES DE PROMPT E AUXILIARES
# =====================================================================

def get_page_extraction_prompt(page_text: str, categorias_json: str) -> str:
    """Constrói o prompt para extrair e enriquecer todos os itens de uma única página."""
    return f"""
    Você é um Engenheiro de Dados especialista em análise de documentos de licitação.
    Sua tarefa é analisar o texto de UMA ÚNICA PÁGINA de um edital e extrair todos os itens de produto que encontrar.

    **Texto da Página para Análise:**
    ---
    {page_text}
    ---

    **Instruções:**
    1.  Identifique cada item de produto listado no texto.
    2.  Para cada item, extraia as seguintes informações diretamente do texto: 'Nº', 'REFERENCIA' (marca/modelo de referência), 'QTDE', 'VALOR_UNIT', 'VALOR_TOTAL'.
    3.  Analise a descrição do item para determinar sua 'CATEGORIA' e 'SUBCATEGORIA' com base na taxonomia fornecida. Se não se encaixar, use 'OUTROS'.
    4.  Crie um objeto JSON ('JSON') contendo as especificações técnicas detalhadas (marca, modelo, características). Este campo NUNCA deve ser vazio.
    5.  Se valores numéricos como QTDE ou VALOR não forem encontrados para um item, use 0.

    **Taxonomia de Categorias Válidas:**
    ```json
    {categorias_json}
    ```

    **Formato de Saída Obrigatório:**
    Sua resposta deve ser uma lista de objetos JSON. Cada objeto representa um item e deve conter TODAS as 8 chaves: "Nº", "REFERENCIA", "QTDE", "VALOR_UNIT", "VALOR_TOTAL", "JSON", "CATEGORIA", "SUBCATEGORIA".
    Retorne APENAS a lista JSON, começando com `[` e terminando com `]`.
    """

def clean_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas para numérico e preenche valores não encontrados com 0."""
    num_cols = ['QTDE', 'VALOR_UNIT', 'VALOR_TOTAL']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def call_gemini(prompt: str) -> str:
    """Chama a API Gemini e retorna o texto da resposta, com tratamento de erro."""
    try:
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro na chamada da API Gemini: {e}")
        time.sleep(5)
        return "[]" # Retorna uma lista vazia em caso de erro

# =====================================================================
# FUNÇÃO PRINCIPAL
# =====================================================================

def main():
    """Orquestra o processo de extração e enriquecimento do edital, página por página."""
    if not PDF_ANALISAR.exists():
        print(f"[ERRO] O arquivo '{PDF_ANALISAR}' não foi encontrado.")
        print("Por favor, coloque o PDF do edital na mesma pasta deste script ou ajuste a variável 'PDF_ANALISAR'.")
        return

    print(f"Iniciando análise do edital: {PDF_ANALISAR.name}")
    all_items = []
    categorias_str = json.dumps(CATEGORIAS_PRODUTOS, indent=2, ensure_ascii=False)

    try:
        with pdfplumber.open(PDF_ANALISAR) as pdf:
            for page in tqdm(pdf.pages, desc="Analisando páginas do edital"):
                page_text = page.extract_text()
                if not page_text or not page_text.strip():
                    continue

                prompt = get_page_extraction_prompt(page_text, categorias_str)
                response_text = call_gemini(prompt)

                try:
                    # Limpa a resposta para garantir que seja um JSON válido
                    cleaned_text = response_text.strip().replace("```json", "").replace("```", "").strip()
                    page_items = json.loads(cleaned_text)
                    if page_items:
                        all_items.extend(page_items)
                        tqdm.write(f"  - {len(page_items)} itens encontrados na página {page.page_number}.")
                except json.JSONDecodeError:
                    tqdm.write(f"\n[AVISO] Falha ao decodificar JSON na página {page.page_number}. Resposta da IA ignorada.")

                time.sleep(1) # Pausa leve entre páginas

        if not all_items:
            print("Nenhum item foi extraído do documento. Encerrando.")
            return

        print("\nConsolidando e limpando os dados extraídos...")
        df_final = pd.DataFrame(all_items)

        # Garante que todas as colunas necessárias existam
        required_cols = ['Nº', 'REFERENCIA', 'QTDE', 'VALOR_UNIT', 'VALOR_TOTAL', 'JSON', 'CATEGORIA', 'SUBCATEGORIA']
        for col in required_cols:
            if col not in df_final.columns:
                df_final[col] = None

        # Converte o campo JSON para string para salvar no Excel
        df_final['JSON'] = df_final['JSON'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)

        df_final = clean_numeric_columns(df_final)
        df_final = df_final[required_cols] # Reordena para a ordem final

        print(f"Salvando {len(df_final)} itens em: {OUTPUT_FILE}")
        df_final.to_excel(OUTPUT_FILE, index=False, engine='openpyxl')
        print("\n✅ Processo concluído com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o processamento: {e}")

if __name__ == "__main__":
    main()
