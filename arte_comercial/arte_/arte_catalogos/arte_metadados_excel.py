import os
import json
import time
import pandas as pd
import google.generativeai as genai
import google.api_core.exceptions
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import itertools
import re

import logging

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
INPUT_FILE = CATALOGS_DIR / "diversos.xlsx"
OUTPUT_FILE = CATALOGS_DIR / "produtos_oficial_diversos.xlsx"  # Match exato com o arquivo de referência

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

# Schema for validation of enriched rows (used by validate_row_schema)
ROW_SCHEMA = {
    "METADADOS": str,
    "categoria_principal": str,
    "subcategoria": str,
    "ESPECIFICACOES_JSON": dict,
}


# --- FUNÇÃO DE CHAMADA À API COM FALLBACK ---
def call_gemini_with_fallback(prompt_parts: list, generation_config: dict, request_options: dict) -> genai.types.GenerateContentResponse | None:
    """Tenta chamar a API com as chaves em rotação, pulando para a próxima em caso de erro de cota."""
    for _ in range(len(API_KEYS)):
        try:
            key = next(API_KEY_CYCLE)
            tqdm.write(f"  - Usando chave de API: ...{key[-4:]}")
            genai.configure(api_key=key)
            
            model = genai.GenerativeModel(
                model_name="gemini-robotics-er-1.5-preview",
                generation_config=generation_config
                # Nota: Google Search Retrieval requer API paga Enterprise
                # Mas o Gemini 2.5 Flash tem conhecimento extenso embarcado
            )
            
            response = model.generate_content(prompt_parts, request_options=request_options)
            return response

        except google.api_core.exceptions.ResourceExhausted as e:
            tqdm.write(f"  - [AVISO] Cota da chave ...{key[-4:]} excedida. Tentando próxima chave...")
            time.sleep(2)
            continue
        except google.api_core.exceptions.PermissionDenied as e:
            tqdm.write(f"  - [ERRO] Permissão negada para a chave ...{key[-4:]}. Chave suspensa ou inválida. {e}")
            tqdm.write("  - Tentando próxima chave...")
            time.sleep(2)
            continue
        except Exception as e:
            tqdm.write(f"\n  - [ERRO] Ocorreu um erro inesperado com a chave ...{key[-4:]}: {e}")
            tqdm.write("  - Tentando próxima chave...")
            time.sleep(5)
            continue
            
    tqdm.write("\n[ERRO CRÍTICO] Todas as chaves de API falharam ou atingiram a cota. Não é possível continuar a chamada.")
    return None


# --- PROMPT PARA O MODELO GEMINI (ANTI-ALUCINAÇÃO + BUSCA WEB VERIFICÁVEL) ---
def get_excel_row_prompt(row_data: pd.Series, taxonomia_str: str) -> str:
    """Gera uma prompt robusta para extração verificável de dados via busca na web."""
    return f"""
    Você é um Engenheiro de Dados especialista em catalogação técnica de produtos musicais.
    Sua tarefa é analisar os dados de um produto e usar seu CONHECIMENTO TÉCNICO INTERNO para enriquecê-lo com informações VERIFICÁVEIS.
    
    DADOS DO PRODUTO (ENTRADA):
    - MARCA: {row_data['MARCA']}
    - MODELO: {row_data['MODELO']}
    - DESCRIÇÃO FORNECEDOR: {row_data.get('DESCRICAO_FORNECEDOR', 'N/A')}
    
    TAXONOMIA OBRIGATÓRIA:
    {taxonomia_str}

    INSTRUÇÕES DE EXTRAÇÃO E ESTRUTURAÇÃO (PROCESSO EM 2 ETAPAS):
    
    **ETAPA 1: CURADORIA E ENRIQUECIMENTO (GERAÇÃO DO CAMPO 'METADADOS')**
    Aja como um especialista técnico. Use seu conhecimento sobre produtos musicais (especificações típicas de marcas/modelos conhecidos) para enriquecer o produto.
    
    FONTES DE CONHECIMENTO PRIORITÁRIAS:
    1. **Especificações técnicas padrão** da marca/modelo (se conhecidas)
    2. **Características típicas** da categoria de produto
    3. **Dados técnicos comuns** para produtos similares
    
    METODOLOGIA DE VALIDAÇÃO (OBRIGATÓRIA - ANTI-ALUCINAÇÃO):
    1. **NUNCA invente dados arbitrários**. Use apenas informações técnicas que você CONHECE serem corretas para este produto específico ou categoria.
    2. **Valide a correspondência**: Se não tiver certeza que o dado se aplica a ESTE MARCA + MODELO específico, use `null` ou omita.
    3. **Priorize fatos técnicos verificáveis**: dimensões típicas, materiais padrão, especificações documentadas.
    4. **Seja conservador**: É melhor ter menos dados corretos do que mais dados duvidosos.
    
    ESTRUTURA DA DESCRIÇÃO ENRIQUECIDA ('METADADOS'):
    [FUNÇÃO PRINCIPAL] - [CATEGORIA TÉCNICA] com [CARACTERÍSTICAS PRINCIPAIS]. Especificações: [DETALHES TÉCNICOS CONHECIDOS]. Construção: [MATERIAIS TÍPICOS DA CATEGORIA].
    
    **ETAPA 2: ESTRUTURAÇÃO FINAL (GERAÇÃO DO JSON 'ESPECIFICACOES_JSON')**
    Após gerar o campo 'METADADOS', use-o como fonte única para preencher o objeto JSON 'ESPECIFICACOES_JSON'.
    - Extraia CADA ESPECIFICAÇÃO TÉCNICA do campo 'METADADOS' e transforme-a em um par chave-valor dentro do JSON.
    - Use chaves do schema técnico apropriado para a subcategoria.
    - Se uma especificação não foi confirmada, NÃO invente: use `null` ou omita a chave.

    FORMATO DE SAÍDA FINAL (OBJETO JSON):
    O resultado DEVE ser um único objeto JSON contendo APENAS os 4 campos: METADADOS, categoria_principal, subcategoria, ESPECIFICACOES_JSON.
    
    EXEMPLO DE SAÍDA (DADOS REAIS):
    {{
      "METADADOS": "Violão clássico acústico para estudo, tamanho 4/4. Tampo em Spruce, laterais/fundo em Linden. Braço em Basswood com tensor 'Dual Action'. Escala e cavalete em Dark Maple. Cordas de nylon. Comprimento total 990.6mm, encontrado no manual oficial Michael.",
      "categoria_principal": "INSTRUMENTO_CORDA",
      "subcategoria": "violao",
      "ESPECIFICACOES_JSON": {{
        "material_tampo": "Spruce",
        "formato_corpo": "Clássico",
        "tipo_corda": "Nylon",
        "tensor": "Dual Action"
      }}
    }}
    
    **REGRA DE OURO - ANTI-ALUCINAÇÃO:**
    Se você NÃO encontrar informações verificáveis na web para este produto EXATO, retorne o METADADOS como: "Produto {row_data['MARCA']} {row_data['MODELO']}: Informações técnicas detalhadas não disponíveis em fontes verificáveis." e o JSON de ESPECIFICACOES_JSON vazio {{}}.
    
    Assegure-se de que a saída seja APENAS o objeto JSON, sem texto adicional.
    JSON:
    """

def clean_json_response(text: str) -> dict | None:
    """Limpa a resposta do modelo para garantir que seja um JSON válido."""
    try:
        # A resposta pode vir com ```json ... ```, então removemos isso.
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Se não encontrar o padrão, assume que a resposta inteira é o JSON
            json_str = text.strip()

        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError) as e:
        tqdm.write(f"\n[AVISO] Erro ao decodificar JSON: {e}. Resposta: '{text[:100]}...'")
        return None

def validate_row_schema(row: dict) -> bool:
    """Validate that a row dict contains required fields with correct types.
    Returns True if valid, False otherwise.
    """
    required_fields = ["METADADOS", "categoria_principal", "subcategoria", "ESPECIFICACOES_JSON"]
    for field in required_fields:
        if field not in row:
            logging.warning(f"Missing field {field} in enriched data.")
            return False
    if not isinstance(row["METADADOS"], str) or not row["METADADOS"].strip():
        logging.warning("METADADOS must be a non‑empty string.")
        return False
    # categoria_principal and subcategoria should be strings
    if not isinstance(row["categoria_principal"], str) or not isinstance(row["subcategoria"], str):
        logging.warning("Category fields must be strings.")
        return False
    # ESPECIFICACOES_JSON should be a dict (or JSON‑serializable)
    specs = row.get("ESPECIFICACOES_JSON")
    if not isinstance(specs, dict):
        logging.warning("ESPECIFICACOES_JSON must be a dict.")
        return False
    return True


def process_excel_file(df: pd.DataFrame, generation_config: dict, output_file: Path):
    """
    Processa um DataFrame do Excel, enriquecendo os dados em lotes com salvamento incremental.
    """
    print(f"\nIniciando processamento para: {INPUT_FILE.name}")
    taxonomia_str = json.dumps(CATEGORIAS_PRODUTOS, indent=2, ensure_ascii=False)

    # Itera sobre o dataframe em pedaços de 5
    for start in range(0, len(df), 5):
        end = start + 5
        batch_df = df.iloc[start:end]
        tqdm.write(f"\n--- Processando lote: {start+1}-{min(end, len(df))} de {len(df)} ---")

        batch_modified = False  # Flag para saber se algo foi processado neste batch
        
        for index, row in tqdm(batch_df.iterrows(), total=len(batch_df), desc=f"Lote {start//5 + 1}"):
            # Pula linhas que já parecem processadas
            if pd.notna(row.get('METADADOS')) and str(row.get('METADADOS')).strip():
                tqdm.write(f"  - Pulando produto já processado: {row['MARCA']} {row['MODELO']}")
                continue

            prompt = get_excel_row_prompt(row, taxonomia_str)
            
            response = call_gemini_with_fallback(
                prompt_parts=[prompt],
                generation_config=generation_config,
                request_options={'timeout': 300}
            )

            if response and response.text:
                enriched_data = clean_json_response(response.text)
                if enriched_data:
                    if validate_row_schema(enriched_data):
                        df.loc[index, 'METADADOS'] = enriched_data.get('METADADOS')
                        df.loc[index, 'categoria_principal'] = enriched_data.get('categoria_principal')
                        df.loc[index, 'subcategoria'] = enriched_data.get('subcategoria')
                        # Store JSON as string
                        specs_json = enriched_data.get('ESPECIFICACOES_JSON', {})
                        df.loc[index, 'ESPECIFICACOES_JSON'] = json.dumps(specs_json, ensure_ascii=False) if specs_json else '{}'
                        batch_modified = True
                    else:
                        tqdm.write(f"  - Dados inválidos para {row['MARCA']} {row['MODELO']}, pulando atualização.")

                    tqdm.write(f"  - Sucesso: {row['MARCA']} {row['MODELO']}")
                else:
                    tqdm.write(f"  - Falha na extração (JSON inválido): {row['MARCA']} {row['MODELO']}")
            else:
                tqdm.write(f"  - Falha na API: {row['MARCA']} {row['MODELO']}")
            
            time.sleep(1) # Pequena pausa para não sobrecarregar a API
        
        # 💾 SALVAMENTO INCREMENTAL A CADA BATCH
        if batch_modified:
            try:
                df.to_excel(output_file, index=False)
                tqdm.write(f"💾 Salvamento incremental: {min(end, len(df))}/{len(df)} produtos salvos em '{output_file.name}'")
            except Exception as e:
                tqdm.write(f"⚠️  AVISO: Falha ao salvar batch: {e}")

    return df


def main():
    """
    Função principal para orquestrar a extração de metadados de um arquivo Excel.
    Suporta continuação de processamento (Checkpoint) e processamento de itens faltantes.
    """
    
    print("="*80)
    print("INICIANDO PROCESSO DE ENRIQUECIMENTO DE CATÁLOGO EXCEL")
    print("="*80)

    try:
        # Carrega Entrada Obrigatória
        print(f"\n📂 Carregando arquivo de entrada: {INPUT_FILE.name}")
        df_input = pd.read_excel(INPUT_FILE)
        df_input.columns = df_input.columns.str.strip().str.replace('\n', '')
        
        # Valida headers obrigatórios
        required_cols = {'MARCA', 'MODELO', 'DESCRICAO_FORNECEDOR'}
        missing = required_cols - set(df_input.columns)
        if missing:
            raise ValueError(f"Excel file is missing required columns: {missing}")
            
        print(f"✅ Input carregado: {len(df_input)} produtos totais.")

    except FileNotFoundError:
        print(f"❌ Erro: O arquivo '{INPUT_FILE}' não foi encontrado.")
        return
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo Excel de entrada: {e}")
        return

    # 🔄 SISTEMA DE CHECKPOINT INTELIGENTE
    # O objetivo é criar um df_full que combine o progresso salvo (checkpoint)
    # com os itens novos que ainda não estavam no arquivo de saída.

    if OUTPUT_FILE.exists():
        print(f"\n📂 Arquivo de saída detectado (Checkpoint): {OUTPUT_FILE.name}")
        try:
            df_current = pd.read_excel(OUTPUT_FILE)
            # Limpa colunas do output também para garantir match
            df_current.columns = df_current.columns.str.strip().str.replace('\n', '')
            
            count_output = len(df_current)
            count_input = len(df_input)
            
            print(f"✅ Checkpoint contém {count_output} produtos.")

            if count_output < count_input:
                missing_count = count_input - count_output
                print(f"⚠️  Detectados {missing_count} produtos faltantes no output.")
                print(f"🔄 Adicionando os {missing_count} itens restantes ao final da fila...")
                
                # Pega as linhas do input que excedem o tamanho do output
                # Assumindo ordem sequencial baseada no índice do original
                rows_to_add = df_input.iloc[count_output:].copy()
                
                # Garante que as colunas de metadados existam e estejam vazias nas novas linhas
                for col in ['METADADOS', 'categoria_principal', 'subcategoria', 'ESPECIFICACOES_JSON']:
                    rows_to_add[col] = pd.NA
                
                # Concatena (Output existente + Novos vazios)
                df_full = pd.concat([df_current, rows_to_add], ignore_index=True)
                print(f"🔄 Lista de processamento expandida: {len(df_current)} -> {len(df_full)} itens.")
                
            elif count_output == count_input:
                print("ℹ️  Quantidade de itens coincide. Verificando se há vazios internos...")
                df_full = df_current
            else:
                print("⚠️  AVISO: Output tem MAIS itens que o input. Usando output como base.")
                df_full = df_current

        except Exception as e:
            print(f"⚠️  Falha ao ler arquivo de checkpoint: {e}")
            print("🔄 Ignorando checkpoint e recomeçando do zero do input...")
            df_full = df_input.copy()
            for col in ['METADADOS', 'categoria_principal', 'subcategoria', 'ESPECIFICACOES_JSON']:
                 if col not in df_full.columns: df_full[col] = pd.NA
    else:
        print("ℹ️  Nenhum checkpoint encontrado. Iniciando processamento do zero.")
        df_full = df_input.copy()
        for col in ['METADADOS', 'categoria_principal', 'subcategoria', 'ESPECIFICACOES_JSON']:
            if col not in df_full.columns: df_full[col] = pd.NA

    
    generation_config = { "temperature": 0.1, "top_p": 0.95, "top_k": 0 }

    print(f"\n🚀 Iniciando processamento do DataFrame consolidado ({len(df_full)} itens)...")
    
    # A função process_excel_file itera sobre o df_full.
    # Ela tem um check: "if pd.notna(row.get('METADADOS'))... continue"
    # Então ela pula o que já está feito e processa o que é novo (NA).
    # E salva o df_full inteiro no Excel.
    df_enriched = process_excel_file(df_full, generation_config, OUTPUT_FILE)
    
    try:
        df_enriched.to_excel(OUTPUT_FILE, index=False)
        print(f"\n{'='*80}")
        print(f"✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        print(f"📊 Dados salvos em: {OUTPUT_FILE}")
        print(f"{'='*80}")
    except Exception as e:
        print(f"\n❌ [ERRO] Falha ao salvar dados finais no Excel: {e}")

if __name__ == "__main__":
    main()

def process_excel(file_path: str, output_path: str = None) -> list:
    """Convenient wrapper that reads an Excel file, processes it, and returns a list of validated dicts.
    Mirrors the return signature of arte_metadados.py.
    """
    from pathlib import Path
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip().str.replace('\n', '')
    
    # Adiciona colunas se não existirem
    for col in ['METADADOS', 'categoria_principal', 'subcategoria', 'ESPECIFICACOES_JSON']:
        if col not in df.columns:
            df[col] = pd.NA
    
    output_file = Path(output_path) if output_path else Path(file_path).with_name(Path(file_path).stem + "_enriquecido.xlsx")
    df = process_excel_file(df, {"temperature": 0.1, "top_p": 0.95, "top_k": 0}, output_file)
    
    # Convert rows to list of dicts, ensuring schema compliance
    records = []
    for _, row in df.iterrows():
        record = {
            "METADADOS": row.get('METADADOS'),
            "categoria_principal": row.get('categoria_principal'),
            "subcategoria": row.get('subcategoria'),
            "ESPECIFICACOES_JSON": json.loads(row.get('ESPECIFICACOES_JSON') or '{}')
        }
        if validate_row_schema(record):
            records.append(record)
    return records
