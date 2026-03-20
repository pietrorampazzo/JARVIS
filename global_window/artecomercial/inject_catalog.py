import json
import re

def update_client():
    with open('C:/Users/pietr/OneDrive/.vscode/global_window/artecomercial/parsed_produtos.json', 'r', encoding='utf-8') as f:
        produtos_json = f.read()

    with open('C:/Users/pietr/OneDrive/.vscode/global_window/artecomercial/src/api/base44Client.ts', 'r', encoding='utf-8') as f:
        content = f.read()

    # Usando regex para encontrar o bloco `return [ ... ];` dentro de `Produto: { list: ... }`
    # Como é um bloco fixo, vamos procurar pelo comentário e fechar no `];` antes de `Marca:`
    
    start_marker = '// e referencie aqui como "/images/produtos/sua-imagem.jpg"'
    end_marker = '            }\n        },\n        Marca:'
    
    start_idx = content.find(start_marker) + len(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        new_content = content[:start_idx] + f'\n                return {produtos_json};\n' + content[end_idx:]
        
        with open('C:/Users/pietr/OneDrive/.vscode/global_window/artecomercial/src/api/base44Client.ts', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Mock atualizado com sucesso!")
    else:
        print("Erro: Não foi possível localizar os marcadores para substituição.")

if __name__ == "__main__":
    update_client()
