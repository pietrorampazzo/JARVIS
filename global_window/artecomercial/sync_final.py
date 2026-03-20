import pandas as pd
import json
import os

file_path = r"c:\Users\pietr\OneDrive\.vscode\global_window\artecomercial\PIEZZO_ATAS.xlsx"
out_path = r"c:\Users\pietr\OneDrive\.vscode\global_window\artecomercial\src\api\base44Client.ts"

def parse_price(val):
    if pd.isna(val): return 0.0
    if isinstance(val, (int, float)): return float(val)
    s = str(val).replace('R$', '').replace(' ', '').strip()
    if not s: return 0.0
    last_comma = s.rfind(',')
    last_dot = s.rfind('.')
    try:
        if last_comma > last_dot: s = s.replace('.', '').replace(',', '.')
        elif last_dot > last_comma: s = s.replace(',', '')
        elif last_comma != -1: s = s.replace(',', '.')
        return float(s)
    except: return 0.0

df = pd.read_excel(file_path)
produtos = []
itens_ata = []

imagem_map = {
    "SHURE": "/images/produtos/shure-sistema.jpg",
    "SUMAY": "/images/produtos/sumay-slim-box.jpg",
    "SOUNDVOICE": "/images/produtos/soundvoice-delphi.jpg",
    "SMART": "/images/produtos/smart-tripe.jpg",
    "THOMASTIK": "/images/produtos/thomastik-peter.jpg",
    "STONE": "/images/produtos/sumay-stone.jpg"
}

# Configurações de caminhos de arquivos de imagem
IMG_DIR = r"C:\Users\pietr\OneDrive\.vscode\global_window\artecomercial\public\images\produtos"

def get_img(marca, modelo, uasg, edital, item_num):
    # Limpeza de dados
    uasg_s = str(uasg).strip()
    edital_s = str(edital).replace('/', '').replace('\\', '').strip()
    # Garante que item_num seja inteiro (evita "1.0")
    try:
        item_s = str(int(float(str(item_num).replace(',', '.'))))
    except:
        item_s = str(item_num).strip()

    # Padrões de nomes para testar
    # 1. Sem sufixo (ex: UASG_EDITAL_ITEM.jpg)
    # 2. Com sufixo _1 (ex: UASG_EDITAL_ITEM_1.jpg)
    patterns = [
        f"{uasg_s}_{edital_s}_{item_s}",
        f"{uasg_s}_{edital_s}_{item_s}_1"
    ]
    
    extensions = ['.webp', '.jpg', '.png', '.jpeg', '.JPG', '.PNG', '.WEBP']
    
    for pattern in patterns:
        for ext in extensions:
            file_name = f"{pattern}{ext}"
            file_path_check = os.path.join(IMG_DIR, file_name)
            if os.path.exists(file_path_check):
                # print(f" MATCH: {file_name}") # Ativar se precisar de muito log
                return f"/images/produtos/{file_name}"

    # print(f" NO PHOTO: {patterns[0]}")
    # 2. Heurísticas baseadas em marca/modelo (Fallback)
    m, mod = str(marca).upper(), str(modelo).upper()
    if "SHURE" in m: return imagem_map["SHURE"]
    if "SUMAY" in m and "STONE" in mod: return imagem_map["STONE"]
    if "SUMAY" in m: return imagem_map["SUMAY"]
    if "SOUNDVOICE" in m: return imagem_map["SOUNDVOICE"]
    if "SMART" in m: return imagem_map["SMART"]
    if "THOMASTIK" in m: return imagem_map["THOMASTIK"]
    if "VIOLÃO" in mod: return "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&q=80&w=800"
    if any(x in mod for x in ["BAQUETA", "MACETA", "MAÇANETA"]): return "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&q=80&w=800"
    if any(x in mod for x in ["PALHETA", "BOQUILHA"]): return "https://images.unsplash.com/photo-1573871661642-1594917452df?auto=format&fit=crop&q=80&w=800"
    if any(x in mod for x in ["PELE", "BOMBO", "CAIXA", "FANFARRA"]): return "https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17?auto=format&fit=crop&q=80&w=800"
    if any(x in mod for x in ["MICROFONE", "LAPELA"]): return "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?auto=format&fit=crop&q=80&w=800"
    if any(x in mod for x in ["PEDESTAL", "SUPORTE", "TRIPÉ"]): return "https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&q=80&w=800"
    return "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&q=80&w=800"

for i, row in df.iterrows():
    p_id = f"prod-{i+1}"
    marca = str(row['MARCA'])
    modelo = str(row['MODELO'])
    uasg = str(row['UASG'])
    edital = str(row['EDITAL'])
    item_num = str(row['Nº'])
    preco = parse_price(row['VALOR UNIT.'])
    qtd = int(row['QTD'])
    img = get_img(marca, modelo, uasg, edital, item_num)
    
    produtos.append({
        "id": p_id,
        "marca": marca,
        "modelo": modelo,
        "preco": preco,
        "quantidade": qtd,
        "categoria": "Catálogo",
        "descricao": f"{marca} {modelo} - Edital {row['EDITAL']}",
        "imagem": img,
        "created_date": "2026-03-05T00:00:00.000Z"
    })
    
    itens_ata.append({
        "id": f"item-{i+1}",
        "nome": f"{marca} {modelo}",
        "item": f"{marca} {modelo}", # Necessário para o filtro de busca no frontend
        "descricao": f"Edital: {row['EDITAL']} | UASG: {row['UASG']} | Item: {row['Nº']}",
        "quantidade": qtd,
        "quantidade_registrada": qtd, # Campo esperado em ItensAtas.tsx
        "valor_unitario": preco,
        "marca_nome": marca,
        "status": "disponivel", # Necessário para o filtro padrão "disponível"
        "imagem_url": img,
        "created_date": "2026-03-05T00:00:00.000Z"
    })

content = f"""export const base44 = {{
    entities: {{
        ItemAta: {{
            list: async (order = '-created_date', limit = 200) => {{
                return {json.dumps(itens_ata, indent=16, ensure_ascii=False)};
            }}
        }},
        Produto: {{
            list: async (order = '-created_date', limit = 200) => {{
                return {json.dumps(produtos, indent=16, ensure_ascii=False)};
            }}
        }},
        Marca: {{
            list: async () => {{
                return [
                    {{ id: "m1", nome: "SHURE", logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Shure_logo.svg/1024px-Shure_logo.svg.png" }},
                    {{ id: "m2", nome: "SUMAY", logo: "/images/marcas/sumay.png" }},
                    {{ id: "m3", nome: "PEARL", logo: "/images/marcas/pearl.png" }},
                    {{ id: "m4", nome: "VANDOREN", logo: "/images/marcas/vandoren.png" }},
                    {{ id: "m5", nome: "RMV", logo: "/images/marcas/rmv.png" }},
                    {{ id: "m6", nome: "YAMAHA", logo: "/images/marcas/yamaha.png" }},
                    {{ id: "m7", nome: "TAMA", logo: "/images/marcas/tama.png" }},
                    {{ id: "m8", nome: "D'ADDARIO", logo: "/images/marcas/daddario.png" }},
                    {{ id: "m9", nome: "EVANS", logo: "/images/marcas/evans.png" }},
                    {{ id: "m10", nome: "MICHAEL", logo: "https://michael.com.br/site/img/Michael-Logo.png" }},
                    {{ id: "m11", nome: "SATY", logo: "https://saty.com.br/wp-content/themes/saty/img/logo.png" }},
                    {{ id: "m12", nome: "LUEN", logo: "https://luen.com.br/wp-content/uploads/2021/05/logo-luen.png" }}
                ];
            }}
        }}
    }}
}};
"""

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Sincronização completa concluída para {len(produtos)} itens.")
