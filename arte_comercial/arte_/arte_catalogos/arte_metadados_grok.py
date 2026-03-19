"""
arte_metadados_grok.py

Responsabilidade:
1. Varrer um diretório em busca de arquivos .xlsx específicos.
2. Se o arquivo for do tipo "diversos", enriquecer a coluna METADADOS usando a API da xAI (Grok).
3. Se o arquivo for do tipo "produtos_oficial", corrigir JSONs malformados na coluna ESPECIFICACOES usando a API da xAI (Grok).
4. Salvar os resultados em novos arquivos corrigidos.
"""
import os
import json
import time
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
from xai_sdk import Client
from xai_sdk.chat import user

# =====================================================================
# CONFIGURAÇÕES E CONSTANTES
# =====================================================================
load_dotenv()

try:
    xai_api_key = os.getenv("XAI_KEY")
    if not xai_api_key:
        raise ValueError("Chave XAI_KEY não encontrada no arquivo .env")
    client = Client(api_key=xai_api_key)
except Exception as e:
    print(f"Erro ao configurar a API da xAI. Verifique sua XAI_KEY no arquivo .env: {e}")
    exit()

# --- CAMINHOS E MODELOS ---
INPUT_DIR = Path(r"C:\Users\pietr\OneDrive\.vscode\arte_\DOWNLOADS\CATALOGOS")
XAI_MODELS = [
    "grok-4-1-fast-reasoning",
    "grok-4-1-fast",
    "grok-4-1-fast-reasoning-latest",
    "grok-4-1-fast-non-reasoning",
    "grok-4-1-fast-non-reasoning-latest",
]
MODEL_NAME = XAI_MODELS[0] # Usa o primeiro da lista como padrão

# =====================================================================
# FUNÇÕES DE LÓGICA
# =====================================================================

def call_xai_api(prompt_text: str) -> str:
    """Chama a API da xAI (Grok) com um prompt e retorna a resposta em texto."""
    try:
        # Para cada chamada, criamos um chat para garantir que não haja contaminação de contexto
        chat = client.chat.create(model=MODEL_NAME)
        chat.append(user(prompt_text))
        response = chat.sample()
        return response.content
    except Exception as e:
        tqdm.write(f"\n[ERRO NA API] Falha ao chamar a API da xAI: {e}")
        return ""

def process_diversos(file_path: Path):
    """
    Lógica para enriquecer arquivos do tipo 'diversos.xlsx'.
    Busca metadados na internet para a coluna 'METADADOS'.
    """
    print(f"\nProcessando arquivo para ENRIQUECIMENTO: {file_path.name}")
    try:
        df = pd.read_excel(file_path)
        
        if 'METADADOS' not in df.columns:
            df['METADADOS'] = ''

        desc_col = next((col for col in ['DESCRICAO', 'PRODUTO', 'NOME'] if col in df.columns), None)
        if not desc_col:
            print(f"  - [AVISO] Nenhuma coluna de descrição encontrada em {file_path.name}. Pulando arquivo.")
            return

        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Enriquecendo linhas"):
            if pd.notna(row.get('METADADOS')) and row.get('METADADOS', '') != '':
                continue

            product_info = row[desc_col]
            prompt = f"""
            Você é um especialista em produtos musicais. Pesquise na internet e gere uma descrição técnica detalhada e rica (em português) para o seguinte produto: "{product_info}".
            A descrição deve ser um parágrafo único e conter especificações como materiais, dimensões, características técnicas e uso ideal.
            Responda APENAS com o parágrafo da descrição.
            """
            
            metadata = call_xai_api(prompt)
            if metadata:
                df.at[index, 'METADADOS'] = metadata
            
            time.sleep(1)

        output_path = file_path.with_name(f"{file_path.stem}_enriquecido.xlsx")
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"  - ✅ Salvo em: {output_path}")

    except Exception as e:
        print(f"  - [ERRO] Falha ao processar {file_path.name}: {e}")

def process_oficial(file_path: Path):
    """
    Lógica para corrigir arquivos do tipo 'produtos_oficial.xlsx'.
    Corrige JSONs malformados na coluna 'ESPECIFICACOES'.
    """
    print(f"\nProcessando arquivo para CORREÇÃO DE JSON: {file_path.name}")
    try:
        df = pd.read_excel(file_path)

        if 'ESPECIFICACOES' not in df.columns:
            print(f"  - [AVISO] Coluna 'ESPECIFICACOES' não encontrada em {file_path.name}. Pulando arquivo.")
            return

        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Corrigindo JSONs"):
            spec_string = str(row['ESPECIFICACOES'])

            try:
                json.loads(spec_string)
                continue
            except (json.JSONDecodeError, TypeError):
                tqdm.write(f"  - Corrigindo JSON malformado na linha {index+2}...")
                prompt = f"""
                O texto a seguir deveria ser um objeto JSON, mas está malformado. Corrija-o e retorne APENAS o objeto JSON válido e completo. Não adicione comentários, explicações ou markdown.

                JSON Malformado:
                ```
                {spec_string}
                ```
                """
                corrected_json_str = call_xai_api(prompt)
                
                cleaned_str = corrected_json_str.strip().replace("```json", "").replace("```", "").strip()
                try:
                    json.loads(cleaned_str)
                    df.at[index, 'ESPECIFICACOES'] = cleaned_str
                except json.JSONDecodeError:
                    tqdm.write(f"  - [AVISO] A IA não retornou um JSON válido para a linha {index+2}. Mantendo o valor original.")

            time.sleep(1)

        output_path = file_path.with_name(f"{file_path.stem}_corrigido.xlsx")
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"  - ✅ Salvo em: {output_path}")

    except Exception as e:
        print(f"  - [ERRO] Falha ao processar {file_path.name}: {e}")

# =====================================================================
# FUNÇÃO PRINCIPAL
# =====================================================================

def main():
    """
    Varre o diretório de entrada e aplica a lógica de correção apropriada
    para cada tipo de arquivo.
    """
    print(f"Iniciando varredura no diretório: {INPUT_DIR}")
    if not INPUT_DIR.exists():
        print(f"[ERRO] Diretório de entrada não encontrado. Verifique o caminho.")
        return

    for file_name in os.listdir(INPUT_DIR):
        if not file_name.endswith('.xlsx'):
            continue

        file_path = INPUT_DIR / file_name
        
        if "diversos" in file_name.lower():
            process_diversos(file_path)
        elif "produtos_oficial" in file_name.lower():
            process_oficial(file_path)
    
    print("\nProcesso de correção concluído!")

if __name__ == "__main__":
    main()
