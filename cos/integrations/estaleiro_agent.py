import sys
import os
import json
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

# Setup paths
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.shared import get_latest_snapshot, get_config

# Setup logging
LOG_FILE = BASE_DIR / "logs" / "estaleiro.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s - ESTALEIRO AGENT - %(levelname)s - %(message)s'
)

# Trello API Setup
CONFIG_DIR = BASE_DIR / "config"
ENV_FILE = CONFIG_DIR / ".env"

def load_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

def get_trello_credentials():
    env = load_env()
    return env.get("TRELLO_API_KEY", ""), env.get("TRELLO_TOKEN", "")

def trello_put(endpoint: str, params: dict):
    api_key, token = get_trello_credentials()
    base_params = {"key": api_key, "token": token}
    base_params.update(params)
    query = urllib.parse.urlencode(base_params).encode("utf-8")
    url = f"https://api.trello.com/1/{endpoint}"
    req = urllib.request.Request(url, data=query, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logging.error(f"Erro ao atualizar Trello ({endpoint}): {e}")
        return None

def trello_post_comment(card_id: str, text: str):
    api_key, token = get_trello_credentials()
    params = {"key": api_key, "token": token, "text": text}
    query = urllib.parse.urlencode(params).encode("utf-8")
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    req = urllib.request.Request(url, data=query, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logging.error(f"Erro ao postar comentario no Trello ({card_id}): {e}")
        return None

TARGET_LISTS = ["PROPOSTAS - PIEZO", "PROPOSTAS - ARTE", "HABILITADO"]

def find_estaleiro_links(attachments: list) -> list:
    """Extrai links que parecem ser do Estaleiro ou Compras.gov."""
    links = []
    for att in attachments:
        url = att.get("url", "").lower()
        if "estaleiro" in url or "compras.gov" in url or "comprasnet" in url or "pncp" in url:
            links.append(att.get("url"))
    return links

def scrape_estaleiro(url: str):
    """
    Função Placeholder para o web scraping real.
    Como os portais do governo geralmente requerem navegação complexa (e às vezes JavaScript),
    esta função será expandida na próxima iteração para extrair dados reais da licitação.
    """
    logging.info(f"Analisando URL: {url}")
    # Simulação de retorno de status
    # status pode ser: 'PENDENTE', 'GANHO', 'PERDIDO'
    return {"status": "PENDENTE", "detalhes": "Aguardando implementação do scraper final."}

def run_agent():
    logging.info("=== Iniciando Agente Estaleiro ===")
    snapshot = get_latest_snapshot("arte_comercial")
    if not snapshot:
        logging.error("Snapshot do Trello não encontrado. Execute board_import.py primeiro.")
        return

    cards_to_process = []
    for lst in TARGET_LISTS:
        cards = snapshot.get("cards_by_list", {}).get(lst, [])
        cards_to_process.extend(cards)

    logging.info(f"Encontrados {len(cards_to_process)} cards nas listas alvo.")

    resumo = {
        "analisados": 0,
        "ganhos": 0,
        "descartados": 0,
        "pendentes": 0
    }

    for card in cards_to_process:
        card_id = card.get("id")
        card_name = card.get("name")
        attachments = card.get("attachments", [])
        
        links = find_estaleiro_links(attachments)
        if not links:
            logging.info(f"Sem link do Estaleiro no card: {card_name}")
            continue

        resumo["analisados"] += 1
        
        for link in links:
            resultado = scrape_estaleiro(link)
            status = resultado["status"]
            
            if status == "GANHO":
                # Lógica para mover para HABILITADO
                # precisariamos mapear o ID da lista "HABILITADO"
                logging.info(f"GANHO: {card_name}")
                trello_post_comment(card_id, "🤖 Estaleiro Agent: Item ganho detectado!")
                resumo["ganhos"] += 1
            elif status == "PERDIDO":
                # Lógica para mover para DESCART
                logging.info(f"PERDIDO: {card_name}")
                trello_post_comment(card_id, "🤖 Estaleiro Agent: Perda confirmada em todos os itens. Encaminhando para descarte.")
                resumo["descartados"] += 1
            else:
                logging.info(f"PENDENTE: {card_name}")
                resumo["pendentes"] += 1

    logging.info("=== Resumo da Execução ===")
    logging.info(json.dumps(resumo, indent=2))
    print(f"✅ Agente Estaleiro finalizado. Analisados: {resumo['analisados']}")
    print(f"Resumo: {resumo}")

if __name__ == "__main__":
    run_agent()