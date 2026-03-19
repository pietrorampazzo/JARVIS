import os
import re
import shutil
import requests

# =============================
# 🔐 CONFIGURAÇÕES TRELLO
# =============================
API_KEY = "683cba47b43c3a1cfb10cf809fecb685"
TOKEN = "ATTA89e63b1ce30ca079cef748f3a99cda25de9a37f3ba98c35680870835d6f2cae034C088A8"

BOARD_ID = "fFeL1Gw8"  # shortLink do board Arte Comercial

LIST_NAMES_VALIDAS = {"Compras.Gov", "PREPARANDO"}

# =============================
# 📂 CAMINHOS
# =============================
PASTA_EDITAIS = r"C:\Users\pietr\OneDrive\.vscode\arte_\DOWNLOADS\EDITAIS"
PASTA_ARQUIVO_MORTO = r"C:\Users\pietr\OneDrive\Área de Trabalho\ARTE\01_EDITAIS"

# =============================
# 🔧 FUNÇÕES AUXILIARES
# =============================
def trello_get(url, params=None):
    if params is None:
        params = {}
    params.update({"key": API_KEY, "token": TOKEN})
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def obter_listas_do_board():
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
    listas = trello_get(url)
    return {lista["id"]: lista["name"] for lista in listas}


def obter_cards_da_lista(list_id):
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    return trello_get(url)


def extrair_uasg_pregao(nome_card):
    """
    Espera algo como:
    Uasg: 153037
    Pregão Eletrônico 900222025
    """
    uasg = re.search(r"Uasg:\s*(\d+)", nome_card, re.IGNORECASE)
    pregao = re.search(r"(Pregão|Dispensa).*?(\d{6,})", nome_card, re.IGNORECASE)

    if uasg and pregao:
        return f"{uasg.group(1)}_{pregao.group(2)}"
    return None


# =============================
# 🚀 EXECUÇÃO PRINCIPAL
# =============================
def main():
    print("--- Buscando listas do Trello... ---")
    listas = obter_listas_do_board()

    listas_validas_ids = [
        list_id for list_id, name in listas.items()
        if name in LIST_NAMES_VALIDAS
    ]

    print(f"Listas consideradas: {LIST_NAMES_VALIDAS}")

    pastas_validas_trello = set()

    for list_id in listas_validas_ids:
        cards = obter_cards_da_lista(list_id)
        for card in cards:
            chave = extrair_uasg_pregao(card["name"])
            if chave:
                pastas_validas_trello.add(chave)

    print(f"OK: {len(pastas_validas_trello)} editais ativos no Trello")

    # Garante que a pasta destino existe
    os.makedirs(PASTA_ARQUIVO_MORTO, exist_ok=True)

    print("--- Verificando pastas locais... ---")
    for nome_pasta in os.listdir(PASTA_EDITAIS):
        caminho_pasta = os.path.join(PASTA_EDITAIS, nome_pasta)

        if not os.path.isdir(caminho_pasta):
            continue

        # valida padrão uasg_pregao
        if not re.match(r"^\d+_\d+$", nome_pasta):
            print(f"Aviso: Ignorado (padrao invalido): {nome_pasta}")
            continue

        if nome_pasta not in pastas_validas_trello:
            destino = os.path.join(PASTA_ARQUIVO_MORTO, nome_pasta)
            print(f"Movendo edital antigo: {nome_pasta}")
            shutil.move(caminho_pasta, destino)

    print("Limpeza concluída com sucesso.")


if __name__ == "__main__":
    main()
