import sys
import json
from datetime import datetime

sys.path.insert(0, 'C:\\Users\\pietr\\OneDrive\\.vscode\\JARVIS')
from cos.core.shared import get_latest_snapshot

snapshot = get_latest_snapshot('arte_comercial')
if not snapshot:
    print("Snapshot nao encontrado")
    sys.exit(0)

critical_lists = ["PROPOSTAS - PIEZO", "PROPOSTAS - ARTE", "PREGAO", "PREPARANDO"]

overdue_cards = []
for lst in critical_lists:
    cards = snapshot.get("cards_by_list", {}).get(lst, [])
    for c in cards:
        due = c.get("due")
        if due and not c.get("dueComplete"):
            try:
                due_date = datetime.strptime(due[:10], "%Y-%m-%d")
                if due_date < datetime.now():
                    overdue_cards.append({
                        "name": c.get("name"),
                        "list": lst,
                        "url": c.get("shortUrl")
                    })
            except:
                pass

print(f"Total vencidas: {len(overdue_cards)}\n")
for c in overdue_cards:
    print(f"- {c['name']}")
    print(f"  Lista: {c['list']}")
    print(f"  URL: {c['url']}\n")
