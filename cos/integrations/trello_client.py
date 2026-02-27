"""
COS — Trello Client v1.0
Integração com a Trello REST API para monitoramento de cards de licitações.

Configuração:
  1. Crie cos/config/.env com TRELLO_API_KEY e TRELLO_TOKEN
  2. Execute: python trello_client.py --list-boards  (para descobrir o Board ID)
  3. Preencha TRELLO_BOARD_ID no .env
  4. Execute: python trello_client.py --list-cards   (ver cards de licitação)

Uso:
  python trello_client.py --list-boards
  python trello_client.py --list-cards
  python trello_client.py --list-cards --board-id <ID>
  python trello_client.py --card-detail <CARD_ID>
  python trello_client.py --sync-log                (sugere logs de eventos COS)
"""

import json
import sys
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
ENV_FILE = CONFIG_DIR / ".env"
TRELLO_CONFIG_FILE = CONFIG_DIR / "trello_config.json"

TRELLO_API_BASE = "https://api.trello.com/1"


# ─────────────────────────────────────────────
#  Configuração / Credenciais
# ─────────────────────────────────────────────

def load_env() -> dict:
    """Carrega variáveis do arquivo .env (simples key=value)."""
    env = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def get_credentials() -> tuple[str, str]:
    """Retorna (api_key, token). Lança erro se não configurado."""
    env = load_env()
    api_key = env.get("TRELLO_API_KEY", "")
    token = env.get("TRELLO_TOKEN", "")
    if not api_key or not token:
        print("❌ TRELLO_API_KEY e TRELLO_TOKEN não configurados!")
        print(f"   Edite o arquivo: {ENV_FILE}")
        print("   Obtenha suas credenciais em: https://trello.com/app-key")
        sys.exit(1)
    return api_key, token


def get_default_board_id() -> str:
    """Retorna o Board ID padrão do .env, se configurado."""
    env = load_env()
    return env.get("TRELLO_BOARD_ID", "")


def load_trello_config() -> dict:
    """Carrega mapeamento de listas Trello → COS."""
    if TRELLO_CONFIG_FILE.exists():
        with open(TRELLO_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ─────────────────────────────────────────────
#  Chamadas REST
# ─────────────────────────────────────────────

def trello_get(endpoint: str, params: dict = None) -> dict | list:
    """Faz requisição GET à API do Trello."""
    api_key, token = get_credentials()
    base_params = {"key": api_key, "token": token}
    if params:
        base_params.update(params)
    query = urllib.parse.urlencode(base_params)
    url = f"{TRELLO_API_BASE}/{endpoint}?{query}"
    try:
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"❌ Erro {e.code} na Trello API: {body}")
        sys.exit(1)


# ─────────────────────────────────────────────
#  Boards
# ─────────────────────────────────────────────

def list_boards() -> list:
    """Lista todos os boards do usuário autenticado."""
    boards = trello_get("members/me/boards", {"fields": "id,name,url,closed"})
    active = [b for b in boards if not b.get("closed")]
    return active


def print_boards(boards: list) -> None:
    print(f"\n{'='*60}")
    print(f"  📋 SEUS BOARDS NO TRELLO ({len(boards)} ativos)")
    print(f"{'='*60}")
    for b in boards:
        print(f"  {'ID':<28}  Nome")
        break
    print(f"  {'-'*58}")
    for b in boards:
        print(f"  {b['id']:<28}  {b['name']}")
    print(f"\n  💡 Copie o ID do board de licitações e salve em:")
    print(f"     {ENV_FILE}  →  TRELLO_BOARD_ID=<id>")
    print(f"{'='*60}\n")


# ─────────────────────────────────────────────
#  Listas do Board
# ─────────────────────────────────────────────

def get_board_lists(board_id: str) -> list:
    """Retorna todas as listas de um board."""
    return trello_get(f"boards/{board_id}/lists", {"fields": "id,name,pos"})


# ─────────────────────────────────────────────
#  Cards
# ─────────────────────────────────────────────

def get_board_cards(board_id: str) -> list:
    """Retorna todos os cards abertos de um board com lista e labels."""
    return trello_get(
        f"boards/{board_id}/cards",
        {
            "fields": "id,name,desc,idList,labels,due,dateLastActivity,url",
            "filter": "open"
        }
    )


def get_card_detail(card_id: str) -> dict:
    """Retorna detalhes completos de um card."""
    return trello_get(
        f"cards/{card_id}",
        {"fields": "id,name,desc,idList,labels,due,dateLastActivity,url"}
    )


def enrich_cards_with_list_name(cards: list, board_id: str) -> list:
    """Adiciona o nome da lista a cada card."""
    lists = get_board_lists(board_id)
    list_map = {lst["id"]: lst["name"] for lst in lists}
    for card in cards:
        card["list_name"] = list_map.get(card["idList"], "Desconhecida")
    return cards


def print_cards(cards: list) -> None:
    """Exibe lista de cards formatada."""
    print(f"\n{'='*70}")
    print(f"  🗂️  CARDS DO BOARD — {date.today().strftime('%d/%m/%Y')}")
    print(f"{'='*70}")
    if not cards:
        print("  📭 Nenhum card encontrado.")
        print(f"{'='*70}\n")
        return

    # Agrupa por lista
    by_list: dict = {}
    for card in cards:
        lst = card.get("list_name", "?")
        by_list.setdefault(lst, []).append(card)

    for lista_name, lista_cards in by_list.items():
        print(f"\n  📂 {lista_name} ({len(lista_cards)} cards)")
        print(f"  {'-'*60}")
        for c in lista_cards:
            due = ""
            if c.get("due"):
                due_dt = datetime.fromisoformat(c["due"].replace("Z", "+00:00"))
                due = f" | 📅 Venc: {due_dt.strftime('%d/%m/%Y')}"
            labels = ", ".join(lb["name"] for lb in c.get("labels", []) if lb.get("name"))
            label_str = f" | 🏷️ {labels}" if labels else ""
            print(f"  • {c['name'][:55]}{due}{label_str}")
            print(f"    ID: {c['id']}")

    print(f"\n  Total: {len(cards)} cards")
    print(f"{'='*70}\n")


# ─────────────────────────────────────────────
#  Sync → Log COS
# ─────────────────────────────────────────────

def suggest_cos_logs(cards: list) -> list:
    """
    Analisa cards modificados recentemente e sugere logs para o COS.
    Filtra cards movidos nas últimas 24h.
    """
    config = load_trello_config()
    list_to_cos = config.get("list_to_cos", {})
    suggestions = []

    cutoff = datetime.now().astimezone() - timedelta(hours=24)

    for card in cards:
        last_activity_str = card.get("dateLastActivity", "")
        if not last_activity_str:
            continue
        last_activity = datetime.fromisoformat(
            last_activity_str.replace("Z", "+00:00")
        )
        if last_activity < cutoff:
            continue  # Não mexido nas últimas 24h

        list_name = card.get("list_name", "")
        mapping = list_to_cos.get(list_name)
        if not mapping:
            continue  # Lista não mapeada no config

        suggestions.append({
            "card_id": card["id"],
            "card_name": card["name"],
            "list_name": list_name,
            "last_activity": last_activity.strftime("%d/%m/%Y %H:%M"),
            "cos_area": mapping["area"],
            "cos_category": mapping["category"],
            "cos_impact": mapping["impact"],
            "cos_duration": mapping.get("duration_minutes", 60),
            "action_template": mapping["action_template"].replace(
                "{card_name}", card["name"]
            ),
        })

    return suggestions


def print_sync_suggestions(suggestions: list) -> None:
    """Exibe e permite aprovar sugestões de log."""
    if not suggestions:
        print("\n  📭 Nenhum card movido nas últimas 24h para registrar no COS.")
        return

    print(f"\n{'='*65}")
    print(f"  🔄 SUGESTÕES DE LOG — Trello → COS")
    print(f"{'='*65}")

    sys.path.insert(0, str(BASE_DIR / "logger"))
    from event_logger import log_event

    logged = 0
    for i, s in enumerate(suggestions, 1):
        print(f"\n  [{i}] {s['card_name']}")
        print(f"       Lista:    {s['list_name']}")
        print(f"       Ação:     {s['action_template']}")
        print(f"       Área COS: {s['cos_area']} | Impacto: {s['cos_impact']}/5")
        print(f"       Atividade em: {s['last_activity']}")

        answer = input("\n  → Deseja registrar este evento? [s/n]: ").strip().lower()
        if answer == "s":
            log_event(
                area=s["cos_area"],
                category=s["cos_category"],
                action=s["action_template"],
                impact=s["cos_impact"],
                duration_minutes=s["cos_duration"],
                source="trello",
                project=s["card_name"],
            )
            logged += 1

    print(f"\n  ✅ {logged} de {len(suggestions)} eventos registrados no COS.\n")


def run_sync(board_id: str) -> None:
    """Executa o fluxo completo de sync Trello → COS."""
    print("  🔄 Buscando cards do Trello...")
    cards = get_board_cards(board_id)
    cards = enrich_cards_with_list_name(cards, board_id)
    suggestions = suggest_cos_logs(cards)
    print_sync_suggestions(suggestions)


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="COS — Trello Client (Integração Licitações)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python trello_client.py --list-boards
  python trello_client.py --list-cards
  python trello_client.py --list-cards --board-id <ID>
  python trello_client.py --card-detail <CARD_ID>
  python trello_client.py --sync-log
        """
    )
    parser.add_argument("--list-boards", action="store_true",
                        help="Lista todos os boards do usuário")
    parser.add_argument("--list-cards", action="store_true",
                        help="Lista cards do board de licitações")
    parser.add_argument("--board-id", type=str, default="",
                        help="Board ID (sobrescreve TRELLO_BOARD_ID do .env)")
    parser.add_argument("--card-detail", type=str, metavar="CARD_ID",
                        help="Exibe detalhes de um card específico")
    parser.add_argument("--sync-log", action="store_true",
                        help="Sincroniza cards recentes e sugere logs COS")

    args = parser.parse_args()

    if args.list_boards:
        boards = list_boards()
        print_boards(boards)
        return

    board_id = args.board_id or get_default_board_id()

    if args.card_detail:
        card = get_card_detail(args.card_detail)
        lists = get_board_lists(board_id) if board_id else []
        list_map = {lst["id"]: lst["name"] for lst in lists}
        card["list_name"] = list_map.get(card["idList"], "?")
        print_cards([card])
        return

    if not board_id:
        print("❌ TRELLO_BOARD_ID não configurado.")
        print(f"   1. Rode --list-boards para descobrir o ID do seu board")
        print(f"   2. Adicione TRELLO_BOARD_ID=<id> em {ENV_FILE}")
        sys.exit(1)

    if args.list_cards:
        cards = get_board_cards(board_id)
        cards = enrich_cards_with_list_name(cards, board_id)
        print_cards(cards)
        return

    if args.sync_log:
        run_sync(board_id)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
