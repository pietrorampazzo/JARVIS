"""
COS — Board Import v1.0
Lê estrutura completa de um board Trello e gera snapshot JSON estruturado.
Ideal para auditoria, análise e integração com o Score Engine.

Uso:
  python board_import.py                     → importa board padrão do .env
  python board_import.py --board-id <ID>     → board específico
  python board_import.py --summary           → resumo executivo no terminal
  python board_import.py --open-only         → apenas cards em aberto
"""

import json
import sys
import argparse
from datetime import datetime, date
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
ENV_FILE = CONFIG_DIR / ".env"
SNAPSHOTS_DIR = BASE_DIR / "integrations" / "snapshots"

TRELLO_API_BASE = "https://api.trello.com/1"


# ─────────────────────────────────────────────
#  Credenciais
# ─────────────────────────────────────────────

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


def get_credentials() -> tuple[str, str]:
    env = load_env()
    api_key = env.get("TRELLO_API_KEY", "")
    token = env.get("TRELLO_TOKEN", "")
    if not api_key or not token:
        print("❌ Credenciais não configuradas em cos/config/.env")
        sys.exit(1)
    return api_key, token


def get_default_board_id() -> str:
    return load_env().get("TRELLO_BOARD_ID", "")


# ─────────────────────────────────────────────
#  HTTP
# ─────────────────────────────────────────────

def trello_get(endpoint: str, params: dict = None) -> dict | list:
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
        print(f"❌ Erro {e.code}: {body}")
        sys.exit(1)


# ─────────────────────────────────────────────
#  Importação
# ─────────────────────────────────────────────

def import_board(board_id: str, open_only: bool = False) -> dict:
    """
    Importa estrutura completa do board:
    - informações do board
    - todas as listas
    - todos os cards com label e data
    Retorna dict estruturado pronto para JSON.
    """
    print(f"  🔄 Buscando dados do board {board_id}...")

    # Board info
    board_info = trello_get(f"boards/{board_id}", {
        "fields": "id,name,url,dateLastActivity"
    })

    # Listas
    lists = trello_get(f"boards/{board_id}/lists", {"fields": "id,name,pos"})
    list_map = {lst["id"]: lst["name"] for lst in lists}

    # Cards
    card_filter = "open" if open_only else "all"
    cards_raw = trello_get(f"boards/{board_id}/cards/{card_filter}", {
        "fields": "id,name,desc,idList,labels,due,dateLastActivity,url,closed"
    })

    # Organizar por lista
    cards_by_list: dict = {lst["name"]: [] for lst in lists}
    stats = {
        "total": len(cards_raw),
        "open": 0,
        "closed": 0,
        "with_due": 0,
        "overdue": 0,
        "won": 0,
        "suspended": 0,
        "by_list": {}
    }

    now_str = datetime.now().isoformat()

    for card in cards_raw:
        list_name = list_map.get(card["idList"], "Sem Lista")

        # Labels
        labels = [lb["name"] for lb in card.get("labels", []) if lb.get("name")]

        # Due date
        due_iso = card.get("due")
        due_str = None
        overdue = False
        if due_iso:
            stats["with_due"] += 1
            due_dt = datetime.fromisoformat(due_iso.replace("Z", "+00:00"))
            due_str = due_dt.strftime("%Y-%m-%d")
            if due_dt.replace(tzinfo=None) < datetime.now() and not card.get("closed"):
                overdue = True
                stats["overdue"] += 1

        # Status
        if "⚡ GANHO" in labels:
            stats["won"] += 1
        if "⌛ SUSPENSA" in labels:
            stats["suspended"] += 1

        if card.get("closed"):
            stats["closed"] += 1
        else:
            stats["open"] += 1

        card_data = {
            "id": card["id"],
            "name": card["name"],
            "list": list_name,
            "labels": labels,
            "due": due_str,
            "overdue": overdue,
            "last_activity": card.get("dateLastActivity", "")[:10] if card.get("dateLastActivity") else None,
            "url": card.get("url", ""),
            "closed": card.get("closed", False),
        }
        # Inclui desc apenas se preenchida (economiza espaço)
        if card.get("desc", "").strip():
            card_data["desc"] = card["desc"][:500]  # cap 500 chars

        if list_name in cards_by_list:
            cards_by_list[list_name].append(card_data)
        else:
            cards_by_list[list_name] = [card_data]

    # Stats por lista
    for lst_name, lst_cards in cards_by_list.items():
        stats["by_list"][lst_name] = len(lst_cards)

    snapshot = {
        "imported_at": now_str,
        "board": {
            "id": board_info["id"],
            "name": board_info["name"],
            "url": board_info.get("url", ""),
            "last_activity": board_info.get("dateLastActivity", "")[:10]
        },
        "stats": stats,
        "lists": [lst["name"] for lst in lists],
        "cards_by_list": cards_by_list
    }

    return snapshot


def save_snapshot(snapshot: dict, board_name: str) -> Path:
    """Salva o snapshot em JSON com timestamp."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{board_name.lower().replace(' ', '_')}_{date.today().isoformat()}.json"
    out_path = SNAPSHOTS_DIR / filename
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    return out_path


def print_summary(snapshot: dict) -> None:
    """Exibe resumo executivo no terminal."""
    board = snapshot["board"]
    stats = snapshot["stats"]

    print(f"\n{'='*65}")
    print(f"  📊 SNAPSHOT — {board['name']}")
    print(f"  Importado em: {snapshot['imported_at'][:16].replace('T', ' ')}")
    print(f"{'='*65}")
    print(f"\n  📦 CARDS")
    print(f"  {'Total:':<22} {stats['total']}")
    print(f"  {'Abertos:':<22} {stats['open']}")
    print(f"  {'Fechados:':<22} {stats['closed']}")
    print(f"  {'Com vencimento:':<22} {stats['with_due']}")
    print(f"  {'Vencidos:':<22} {stats['overdue']} ⚠️" if stats['overdue'] else f"  {'Vencidos:':<22} 0")
    print(f"\n  🏆 LICITAÇÕES GANHAS: {stats['won']}")
    print(f"  ⌛ SUSPENSAS:         {stats['suspended']}")

    print(f"\n  📂 POR LISTA:")
    for lst_name, count in stats["by_list"].items():
        if count > 0:
            bar = "█" * min(count // 10 + 1, 20)
            print(f"  {'  ' + lst_name[:28]:<30} {count:>4}  {bar}")

    print(f"\n{'='*65}")
    print(f"  💾 Snapshot salvo em: cos/integrations/snapshots/")
    print(f"{'='*65}\n")


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="COS — Board Import (Trello → JSON Estruturado)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python board_import.py
  python board_import.py --summary
  python board_import.py --open-only
  python board_import.py --board-id 68569b7191cc868682152923
        """
    )
    parser.add_argument("--board-id", type=str, default="",
                        help="Board ID (padrão: TRELLO_BOARD_ID do .env)")
    parser.add_argument("--summary", action="store_true",
                        help="Exibe resumo executivo no terminal")
    parser.add_argument("--open-only", action="store_true",
                        help="Importa apenas cards abertos")
    parser.add_argument("--json", action="store_true",
                        help="Output do snapshot em JSON no terminal")
    args = parser.parse_args()

    board_id = args.board_id or get_default_board_id()
    if not board_id:
        print("❌ TRELLO_BOARD_ID não configurado.")
        print(f"   Adicione em: {ENV_FILE}")
        sys.exit(1)

    snapshot = import_board(board_id, open_only=args.open_only)
    board_name = snapshot["board"]["name"]

    # Sempre salva o snapshot
    out_path = save_snapshot(snapshot, board_name)
    print(f"  ✅ Snapshot salvo: {out_path}")

    if args.summary or not args.json:
        print_summary(snapshot)

    if args.json:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
