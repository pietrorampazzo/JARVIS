import pandas as pd
import json

def parse_excel():
    try:
        # Lendo o arquivo Excel forçando string para não perder formatação de milhares
        df = pd.read_excel('C:/Users/pietr/OneDrive/.vscode/global_window/artecomercial/PIEZZO_ATAS.xlsx', dtype={'VALOR UNIT.': str, 'VALOR UNIT': str})
        
        produtos = []
        for index, row in df.iterrows():
            if pd.isna(row.get('MARCA')) and pd.isna(row.get('MODELO')):
                continue
                
            marca = str(row.get('MARCA', '')).strip()
            modelo = str(row.get('MODELO', '')).strip()
            
            # Tratamento de valor financeiro robusto
            valor_raw = row.get('VALOR UNIT.', row.get('VALOR UNIT', '0'))
            if pd.isna(valor_raw):
                valor = 0.0
            else:
                v_str = str(valor_raw).strip()
                # Remove R$ e espaços
                v_str = v_str.replace('R$', '').strip()
                
                # Para ser agnóstico quanto à localidade, vamos olhar o último ponto e vírgula.
                last_comma = v_str.rfind(',')
                last_dot = v_str.rfind('.')
                
                if last_comma > last_dot:
                    # Vírgula é o separador decimal (Formato BR: 14.100,00 ou 14,00)
                    v_str = v_str.replace('.', '').replace(',', '.')
                elif last_dot > last_comma:
                    # Ponto é o separador decimal (Formato US: 14,100.00 ou 14.00)
                    v_str = v_str.replace(',', '')
                
                try:
                    valor = float(v_str)
                except ValueError:
                    valor = 0.0
                
            # Cria formatação do nome da imagem baseada na marca e modelo (slugify simplificado)
            slug = f"{marca}-{modelo}".lower().replace(' ', '-').replace('/', '-').replace('\\', '-')
            # Remove caracteres especiais se tiver
            import re
            slug = re.sub(r'[^a-zA-Z0-9\-]', '', slug)
            
            # Extração de quantidade da coluna QTD
            qtd_raw = row.get('QTD', 1)
            try:
                qtd = int(float(str(qtd_raw).replace(',', '.'))) # Lida com floats que possam estar no lugar de int (ex: 5.0)
            except ValueError:
                qtd = 1

            produtos.append({
                "id": f"prod-{index + 1}",
                "marca": marca if marca and marca != "nan" else "Diversos",
                "modelo": modelo if modelo and modelo != "nan" else "Produto",
                "preco": valor,
                "quantidade": qtd,
                "categoria": "Catálogo",
                "descricao": f"{marca} {modelo}",
                "imagem": f"/images/produtos/{slug}.jpg",
                "created_date": "2026-03-04T00:00:00.000Z"
            })
            
        with open('C:/Users/pietr/OneDrive/.vscode/global_window/artecomercial/parsed_produtos.json', 'w', encoding='utf-8') as f:
            json.dump(produtos, f, ensure_ascii=False, indent=4)
            
        print(f"Sucesso! {len(produtos)} produtos exportados.")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    parse_excel()
