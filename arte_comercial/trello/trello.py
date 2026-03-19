import requests
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# 🔐 Configurações da API Trello
API_KEY = '683cba47b43c3a1cfb10cf809fecb685'
TOKEN = 'ATTA89e63b1ce30ca079cef748f3a99cda25de9a37f3ba98c35680870835d6f2cae034C088A8'

# =============================================================
# 🆕 ALTERAÇÃO 1: ID da lista “Compras.Gov” (substitui PREPARANDO)
# =============================================================
LISTAS_COMPRAS_GOV = [
    '68ebbe3570442a4a90732a3b',  # Lista "Compras.Gov" no board Arte Comercial
]

# 🧠 Armazena os cards já processados
processed_cards = set()

# =============================================================
# Funções de acesso ao Trello
# =============================================================
def get_cards_in_list(list_id):
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    params = {'key': API_KEY, 'token': TOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# =============================================================
# 🆕 ALTERAÇÃO 2: Agora busca os cards na lista Compras.Gov
# =============================================================
def get_all_comprasgov_cards():
    all_cards = []
    for list_id in LISTAS_COMPRAS_GOV:
        try:
            cards = get_cards_in_list(list_id)
            for card in cards:
                card['source_list_id'] = list_id
            all_cards.extend(cards)
            print(f"📋 {len(cards)} cards encontrados na lista Compras.Gov ({list_id})")
        except Exception as e:
            print(f"❌ Erro ao acessar lista {list_id}: {e}")
    return all_cards

def get_attachments(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}/attachments"
    params = {'key': API_KEY, 'token': TOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def add_auth_to_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query['key'] = [API_KEY]
    query['token'] = [TOKEN]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

# =============================================================
# Extração dos dados do .txt
# =============================================================
def extract_data_from_txt(attachment_id, card_id):
    url = f"https://api.trello.com/1/cards/{card_id}/attachments/{attachment_id}"
    params = {'key': API_KEY, 'token': TOKEN}
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"❌ Erro ao acessar anexo: {response.status_code}")
            return None
        attachment_info = response.json()
        download_url = attachment_info.get('url')
        if not download_url:
            print("❌ URL de download não encontrada")
            return None
        methods = [
            lambda url: add_auth_to_url(url),
            lambda url: (url, {'Authorization': f'OAuth oauth_consumer_key="{API_KEY}", oauth_token="{TOKEN}"'}),
            lambda url: (url, {})
        ]
        for method in methods:
            try:
                if isinstance(method(download_url), tuple):
                    test_url, headers = method(download_url)
                else:
                    test_url = method(download_url)
                    headers = {}
                headers.update({
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "text/plain, */*;q=0.9",
                })
                download_response = requests.get(test_url, headers=headers)
                if download_response.status_code == 200:
                    content = download_response.text.strip()
                    lines = content.splitlines()
                    data = extract_structured_data(lines)
                    return data
            except Exception:
                continue
        print("❌ Todas as tentativas de download falharam")
        return None
    except Exception as e:
        print(f"❌ Erro geral no download: {e}")
        return None

def extract_structured_data(lines):
    data = {
        'new_card_name': None,
        'dia_pregao': None,
        'uasg': None,
        'numero_pregao': None,
        'link_compras_gov': None,
        'downloads_pregao': None,
        'data_do_pregao': None
    }
    try:
        if len(lines) >= 4:
            data['new_card_name'] = f"{lines[1]}\n{lines[2]}\n{lines[3]}"
        for line in lines:
            line = line.strip()
            if 'UASG' in line or 'Uasg' in line:
                uasg_match = re.search(r'(\d{6})', line)
                if uasg_match:
                    data['uasg'] = uasg_match.group(1)
            if 'Pregão' in line or 'Dispensa' in line:
                pregao_match = re.search(r'(\d+/\d{4})', line)
                if pregao_match:
                    data['numero_pregao'] = pregao_match.group(1)
            if 'http' in line and 'compras' in line.lower():
                data['link_compras_gov'] = line.strip()
            datetime_match = re.search(r'(\d{2}/\d{2}/\d{4})\s+às\s+(\d{2}:\d{2})', line)
            if datetime_match:
                data['dia_pregao'] = datetime_match.group(1)
                try:
                    full_dt = f"{datetime_match.group(1)} {datetime_match.group(2)}"
                    dt_obj = datetime.strptime(full_dt, "%d/%m/%Y %H:%M")
                    data['data_do_pregao'] = dt_obj.isoformat()
                except ValueError:
                    pass
            else:
                date_match = re.search(r'(\d{2}/\d{2}/\d{4})', line)
                if date_match:
                    data['dia_pregao'] = date_match.group(1)
                    try:
                        data['data_do_pregao'] = datetime.strptime(date_match.group(1), "%d/%m/%Y").isoformat()
                    except ValueError:
                        pass
        return data
    except Exception as e:
        print(f"❌ Erro ao extrair dados: {e}")
        return None

def normalize_numero_pregao(numero: str) -> str:
    if numero:
        return numero.replace("/", "")
    return numero

def normalize_card_name(card_name: str):
    match_num = re.search(r"(\d+/\d{4})", card_name)
    if match_num:
        numero = match_num.group(1)
        numero_norm = normalize_numero_pregao(numero)
        return re.sub(r"(\d+/\d{4})", numero_norm, card_name)
    return card_name

def update_card_due_date(card_id, due_date_iso):
    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {
        'key': API_KEY,
        'token': TOKEN,
        'due': due_date_iso
    }
    response = requests.put(url, params=params)
    return response.status_code == 200

def update_card_name(card_id, new_name):
    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {
        'key': API_KEY,
        'token': TOKEN,
        'name': new_name
    }
    response = requests.put(url, params=params)
    return response.status_code == 200

def get_compras_gov_links(card_id):
    attachments = get_attachments(card_id)
    compras_links = []
    for attachment in attachments:
        if attachment.get('url') and 'compras.gov' in attachment.get('url', ''):
            compras_links.append(attachment['url'])
    return compras_links

def generate_download_filename(uasg, numero_pregao):
    if uasg and numero_pregao:
        numero_clean = numero_pregao.replace('/', '_')
        return f"U_{uasg}_N_{numero_clean}_E.pdf"
    return None

# =============================================================
# 🆕 ALTERAÇÃO 3: Nova função - Verificar duplicados (UASG + Nº)
# =============================================================
def verificar_cards_duplicados(cards):
    """
    Verifica duplicidade de cards na lista Compras.Gov com base em:
    UASG + número do Pregão (aceitando formatos com ou sem barra).
    """
    combinacoes = {}
    duplicados = []

    for card in cards:
        nome = card.get('name', '').strip()

        # Buscar UASG (aceita "Uasg:", "UASG" ou "uasg")
        uasg_match = re.search(r'UASG[:\s-]*(\d+)', nome, re.IGNORECASE)

        # Buscar número do pregão - aceita "1234/2025" ou "12342025"
        pregao_match = re.search(r'(\d{4,9}(?:/\d{4})?)', nome)

        if uasg_match and pregao_match:
            uasg = uasg_match.group(1).strip()
            pregao = pregao_match.group(1).replace("/", "").strip()
            chave = (uasg, pregao)

            if chave in combinacoes:
                duplicados.append((card['id'], nome))
            else:
                combinacoes[chave] = card['id']

    if duplicados:
        print("\n⚠️ Duplicados encontrados (UASG + Nº Pregão):")
        for dup in duplicados:
            print(f"   - {dup[1]} (id: {dup[0]})")
    else:
        print("\n✅ Nenhum card duplicado encontrado.")


# =============================================================
# Função principal de processamento
# =============================================================
def process_all_cards():
    print("🚀 Iniciando processamento de cards...")
    try:
        all_cards = get_all_comprasgov_cards()
        for card in all_cards:
            attachments = get_attachments(card['id'])
            txt_attachment = next((a for a in attachments if a['name'].endswith('.txt')), None)
            if txt_attachment:
                card_data = extract_data_from_txt(txt_attachment['id'], card['id'])
                if card_data and card_data['new_card_name']:
                    compras_links = get_compras_gov_links(card['id'])
                    if compras_links:
                        card_data['link_compras_gov'] = compras_links[0]
                    
                    download_filename = generate_download_filename(
                        card_data['uasg'],
                        card_data['numero_pregao']
                    )
                    if card_data.get('data_do_pregao'):
                        success_due = update_card_due_date(card['id'], card_data['data_do_pregao'])
                        if success_due:
                            print(f"📆 Data de entrega atualizada para {card_data['data_do_pregao']}")
                        else:
                            print("⚠️ Falha ao atualizar a data de entrega do card.")
                    
                    if download_filename:
                        card_data['downloads_pregao'] = download_filename
                    normalized_name = normalize_card_name(card_data['new_card_name'])
                    update_card_name(card['id'], normalized_name)

        # =============================================================
        # 🆕 ALTERAÇÃO 4: Chamar verificação de duplicados ao final
        # =============================================================
        print("\n🔍 Verificando duplicados...")
        verificar_cards_duplicados(all_cards)

    except Exception as e:
        print(f"❌ Erro: {e}")

# =============================================================
# Execução principal
# =============================================================
if __name__ == "__main__":
    print("\n===============================")
    print("Trello + Google Sheets - Iniciado")
    print("===============================\n")
    process_all_cards()
    print("\n🎉 Processamento concluído!")
