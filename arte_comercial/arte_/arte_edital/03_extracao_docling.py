from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter
import pandas as pd
import os
from pathlib import Path
import re

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()

def process_pdf_with_docling(pdf_path):
    print(f"\n[INFO] Iniciando Docling para: {os.path.basename(pdf_path)}")
    
    # Inicializa o conversor
    converter = DocumentConverter()
    
    # Converte o documento
    result = converter.convert(pdf_path)
    doc = result.document
    
    all_dataframes = []
    
    # Itera pelas tabelas encontradas
    for i, table in enumerate(doc.tables):
        print(f"  [DEBUG] Processando tabela {i+1}...")
        
        # Converte a tabela do Docling para um DataFrame do Pandas
        df = table.export_to_dataframe()
        
        # Limpa os dados
        # Usando 'apply' em vez de 'applymap' para compatibilidade futura
        df = df.apply(lambda x: x.map(clean_text))
        
        # Remove linhas e colunas completamente vazias
        df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
        
        if not df.empty:
            all_dataframes.append(df)
    
    if not all_dataframes:
        print("[WARNING] Nenhuma tabela encontrada pelo Docling.")
        return None

    # Concatenação inteligente
    # No caso de editais, geralmente as tabelas têm o mesmo formato
    # Vamos tentar normalizar o número de colunas
    max_cols = max(df.shape[1] for df in all_dataframes)
    
    normalized_dfs = []
    for df in all_dataframes:
        if df.shape[1] < max_cols:
            # Adiciona colunas vazias se necessário
            for col in range(df.shape[1], max_cols):
                df[f"Vazio_{col}"] = ""
        normalized_dfs.append(df)
        
    final_df = pd.concat(normalized_dfs, ignore_index=True)
    return final_df

def export_to_excel(df, output_path):
    if df is not None and not df.empty:
        df.to_excel(output_path, index=False)
        print(f"[SUCCESS] Arquivo salvo com sucesso em: {output_path}")
    else:
        print("[ERROR] Falha: DataFrame vazio ou inexistente.")

if __name__ == "__main__":
    # Caminho do PDF Limpo (após limpeza de rodapé)
    # Exemplo baseado no que o usuário citou
    pdf_path = r"C:\Users\pietr\OneDrive\.vscode\arte_\DOWNLOADS\EDITAIS\985021_900042026\termo_referencia.pdf"
    
    # Se existir o limpo, usa o limpo
    pdf_limpo = pdf_path.replace(".pdf", "_limpo.pdf")
    if os.path.exists(pdf_limpo):
        pdf_path = pdf_limpo
        print(f"[INFO] Usando versão limpa do PDF: {os.path.basename(pdf_path)}")

    output_dir = os.path.dirname(pdf_path)
    pdf_folder_name = os.path.basename(output_dir)
    output_filename = f"{pdf_folder_name}_referencia_docling.xlsx"
    output_path = os.path.join(output_dir, output_filename)

    df_final = process_pdf_with_docling(pdf_path)
    export_to_excel(df_final, output_path)
