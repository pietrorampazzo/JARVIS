import pandas as pd
import json
import os

EXCEL_PATH = r'C:\Users\pietr\OneDrive\.vscode\JARVIS\records\persons\CLIENTES XP.xlsx'
JSON_CATALOG = r'C:\Users\pietr\OneDrive\.vscode\JARVIS\engine\integrations\whatsapp\contacts_catalog.json'

def extract_clients():
    try:
        df = pd.read_excel(EXCEL_PATH)
        
        # Carregar catálogo existente ou criar novo
        catalog = {}
        if os.path.exists(JSON_CATALOG):
            with open(JSON_CATALOG, 'r', encoding='utf-8') as f:
                catalog = json.load(f)
        
        count = 0
        for _, row in df.iterrows():
            nome = str(row.get('Nome', row.iloc[1])) # Segundo o df.columns, Nome é a segunda coluna
            fone = str(row.get('TELEFONE', row.iloc[2])) # TELEFONE é a terceira
            
            # Limpeza do fone
            digits = "".join(filter(str.isdigit, fone))
            if digits:
                if len(digits) <= 11:
                    digits = "55" + digits
                
                # Atualiza ou adiciona ao catálogo
                catalog[digits] = {
                    "name": nome,
                    "type": "cliente"
                }
                count += 1
        
        with open(JSON_CATALOG, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        
        print(f"Sucesso: {count} clientes processados e salvos no catálogo.")
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    extract_clients()
