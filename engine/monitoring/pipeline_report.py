"""
COS — Pipeline Report v1.0
Relatório diário de movimentação do pipeline de licitações (Trello → COS).

Compara o snapshot de hoje com o de ontem para detectar:
- Cards que avançaram no pipeline
- Cards ganhos, perdidos, descartados
- Nouveaux cards (novas oportunidades)
- Cards removidos
- Status geral do pipeline ativo

Uso:
  python pipeline_report.py                  → relatório completo
  python pipeline_report.py --save           → salva em .md
  python pipeline_report.py --import-first   → importa antes de reportar
  python pipeline_report.py --json           → output JSON
"""

import json
import sys
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
SNAPSHOTS_DIR = BASE_DIR / "integrations" / "snapshots"
OUTPUT_DIR = BASE_DIR.parent / "logs" / "briefings"
TRELLO_CONFIG_FILE = CONFIG_DIR / "trello_config.json"


# ─────────────────────────────────────────────
#  Carregamento de Snapshots
# ─────────────────────────────────────────────

def load_config() -> dict:
    if TRELLO_CONFIG_FILE.exists():
        with open(TRELLO_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def find_snapshot(target_date: date) -> Path | None:
    """Encontra o snapshot mais recente para a data dada."""
    pattern = f"*_{target_date.isoformat()}.json"
    matches = list(SNAPSHOTS_DIR.glob(pattern))
    return matches[0] if matches else None


def find_latest_snapshot() -> Path | None:
    """Encontra o snapshot mais recente disponível."""
    snapshots = sorted(SNAPSHOTS_DIR.glob("*.json"), reverse=True)
    return snapshots[0] if snapshots else None


def load_snapshot(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_card_index(snapshot: dict) -> dict:
    """Cria índice {card_id: {name, list, labels, due, ...}} do snapshot."""
    index = {}
    for list_name, cards in snapshot.get("cards_by_list", {}).items():
        for card in cards:
            index[card["id"]] = {
                "name": card["name"],
                "list": list_name,
                "labels": card.get("labels", []),
                "due": card.get("due"),
                "overdue": card.get("overdue", False),
                "last_activity": card.get("last_activity"),
                "closed": card.get("closed", False),
            }
    return index


# ─────────────────────────────────────────────
#  Diff Engine
# ─────────────────────────────────────────────

def diff_snapshots(prev: dict, curr: dict) -> dict:
    """
    Compara dois snapshots e retorna o diff:
    - moved: cards que mudaram de lista
    - new: novos cards
    - removed: cards que sumiram
    - won: cards que foram para GANHOS / EMPENHO / RECEBIDO
    - lost: cards que foram para PERDIDOS
    - discarded: cards que foram para DESCART
    """
    prev_idx = build_card_index(prev)
    curr_idx = build_card_index(curr)

    config = load_config()
    pipeline_stages = config.get("pipeline_stages", {})
    win_lists = {"GANHOS - ARTE", "EMPENHO", "RECEBIDO"}
    loss_lists = {"PERDIDOS"}
    discard_lists = {"DESCART"}

    moved = []
    new_cards = []
    removed = []
    won = []
    lost = []
    discarded = []
    suspended = []

    # Cards presentes em ambos
    all_ids = set(prev_idx.keys()) | set(curr_idx.keys())

    for card_id in all_ids:
        in_prev = card_id in prev_idx
        in_curr = card_id in curr_idx

        if in_prev and in_curr:
            p = prev_idx[card_id]
            c = curr_idx[card_id]

            # Mudou de lista?
            if p["list"] != c["list"]:
                move = {
                    "id": card_id,
                    "name": c["name"],
                    "from_list": p["list"],
                    "to_list": c["list"],
                    "labels": c["labels"],
                    "due": c.get("due"),
                }
                moved.append(move)
                if c["list"] in win_lists:
                    won.append(move)
                elif c["list"] in loss_lists:
                    lost.append(move)
                elif c["list"] in discard_lists:
                    discarded.append(move)
                elif "⌛ SUSPENSA" in c["labels"] and "⌛ SUSPENSA" not in p["labels"]:
                    suspended.append(move)

        elif not in_prev and in_curr:
            c = curr_idx[card_id]
            new_cards.append({
                "id": card_id,
                "name": c["name"],
                "list": c["list"],
                "labels": c["labels"],
                "due": c.get("due"),
            })

        elif in_prev and not in_curr:
            p = prev_idx[card_id]
            removed.append({
                "id": card_id,
                "name": p["name"],
                "list": p["list"],
            })

    return {
        "period": {
            "from": prev.get("imported_at", "")[:10],
            "to": curr.get("imported_at", "")[:10],
        },
        "moved": moved,
        "won": won,
        "lost": lost,
        "discarded": discarded,
        "suspended": suspended,
        "new_cards": new_cards,
        "removed": removed,
    }


# ─────────────────────────────────────────────
#  Pipeline Status (snapshot atual)
# ─────────────────────────────────────────────

def get_pipeline_status(snapshot: dict) -> dict:
    """Analisa o status atual do pipeline ativo."""
    config = load_config()
    stages = config.get("pipeline_stages", {})
    active_stages = {
        k: v for k, v in stages.items()
        if v["priority"] >= 1 and v["stage"] not in ("perdido", "descartado", "referencia")
    }
    priority_order = sorted(active_stages.keys(), key=lambda k: active_stages[k]["priority"])

    cards_by_list = snapshot.get("cards_by_list", {})
    pipeline = []
    for lst in priority_order:
        cards = cards_by_list.get(lst, [])
        if cards:
            pipeline.append({
                "list": lst,
                "stage": stages[lst]["stage"],
                "color": stages[lst]["color"],
                "count": len(cards),
                "cards": cards
            })

    return pipeline


# ─────────────────────────────────────────────
#  Formatação do Relatório
# ─────────────────────────────────────────────

def generate_report(snapshot: dict, diff: dict | None = None) -> str:
    now = datetime.now()
    config = load_config()
    pipeline = get_pipeline_status(snapshot)
    stats = snapshot.get("stats", {})
    board_name = snapshot.get("board", {}).get("name", "Arte Comercial")

    lines = []
    lines.append("=" * 65)
    lines.append(f"  🗂️  PIPELINE REPORT — {board_name}")
    lines.append(f"  {now.strftime('%d/%m/%Y %H:%M')}  |  COS v1.0")
    lines.append("=" * 65)

    # ── Pipeline Ativo ──
    total_active = sum(s["count"] for s in pipeline)
    lines.append(f"\n  📊 PIPELINE ATIVO ({total_active} licitações)")
    lines.append(f"  {'-'*55}")
    for stage in pipeline:
        bar = "█" * min(stage["count"], 30)
        lines.append(
            f"  {stage['color']} {stage['list']:<22} {stage['count']:>3} cards  {bar}"
        )

    # ── Headline Stats ──
    lines.append(f"\n  🏆 GANHAS (total histórico): {stats.get('won', 0)}")
    lines.append(f"  ❌ PERDIDAS (total histórico): {len(snapshot.get('cards_by_list', {}).get('PERDIDOS', []))}")
    lines.append(f"  🗑️  DESCARTADAS: {len(snapshot.get('cards_by_list', {}).get('DESCART', []))}")
    lines.append(f"  ⌛ SUSPENSAS: {stats.get('suspended', 0)}")

    # ── Diff (se disponível) ──
    if diff:
        lines.append(f"\n  🔄 MOVIMENTAÇÕES DESDE ONTEM")
        lines.append(f"  {'-'*55}")

        if diff["won"]:
            lines.append(f"\n  🏆 AVANÇOS PARA GANHO/EMPENHO ({len(diff['won'])}):")
            for c in diff["won"]:
                lines.append(f"  → {c['name'][:50]}")
                lines.append(f"     {c['from_list']} → {c['to_list']}")

        if diff["lost"]:
            lines.append(f"\n  ❌ MARCADAS COMO PERDIDAS ({len(diff['lost'])}):")
            for c in diff["lost"]:
                lines.append(f"  → {c['name'][:50]}")

        if diff["discarded"]:
            lines.append(f"\n  🗑️  DESCARTADAS ({len(diff['discarded'])}):")
            for c in diff["discarded"][:5]:
                lines.append(f"  → {c['name'][:50]}")

        if diff["new_cards"]:
            lines.append(f"\n  🆕 NOVAS OPORTUNIDADES ({len(diff['new_cards'])}):")
            for c in diff["new_cards"][:5]:
                lines.append(f"  → [{c['list']}] {c['name'][:45]}")

        moved_other = [
            m for m in diff["moved"]
            if m not in diff["won"] + diff["lost"] + diff["discarded"]
        ]
        if moved_other:
            lines.append(f"\n  ↔️  MOVIMENTOS EM PIPELINE ({len(moved_other)}):")
            for c in moved_other[:8]:
                lines.append(f"  → {c['name'][:40]}")
                lines.append(f"     {c['from_list']} → {c['to_list']}")

        if not any([diff["won"], diff["lost"], diff["discarded"], diff["new_cards"], moved_other]):
            lines.append(f"\n  ─ Nenhuma movimentação detectada desde ontem.")

    else:
        lines.append(f"\n  ℹ️  Sem snapshot anterior para comparar. Execute amanhã para ver diff.")

    # ── Vencimentos Críticos ──
    critical_cards = []
    for lst_cards in snapshot.get("cards_by_list", {}).values():
        for card in lst_cards:
            if card.get("overdue") and not card.get("closed"):
                list_name = card.get("list", "?")
                config_stage = config.get("pipeline_stages", {}).get(list_name, {})
                if config_stage.get("priority", 0) > 0:
                    critical_cards.append(card)

    if critical_cards:
        lines.append(f"\n  ⚠️  LICITAÇÕES ATIVAS COM DATA VENCIDA ({len(critical_cards)}):")
        for c in critical_cards[:5]:
            lines.append(f"  → [{c.get('list', '?')}] {c['name'][:45]} | Venc: {c.get('due', '?')}")
        if len(critical_cards) > 5:
            lines.append(f"     ... e mais {len(critical_cards) - 5}")

    lines.append(f"\n{'='*65}")
    lines.append(f"  \ud83d\udcc1 Snapshot: engine/integrations/snapshots/")
    lines.append(f"  🔄 Próxima atualização recomendada: amanhã 08:00")
    lines.append("=" * 65 + "\n")

    return "\n".join(lines)


def save_report(content: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"pipeline_{date.today().isoformat()}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Pipeline Report — {date.today().strftime('%d/%m/%Y')}\n\n")
        f.write("```\n" + content + "```\n")
    return out_path


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="COS — Pipeline Report Diário (Trello)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python pipeline_report.py
  python pipeline_report.py --import-first
  python pipeline_report.py --save
  python pipeline_report.py --json
        """
    )
    parser.add_argument("--import-first", action="store_true",
                        help="Importa snapshot fresco antes de gerar relatório")
    parser.add_argument("--save", action="store_true",
                        help="Salva relatório em .md")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON do diff")
    args = parser.parse_args()

    # Importa snapshot fresco se pedido
    if args.import_first:
        print("  🔄 Importando snapshot atualizado do Trello...")
        import_script = BASE_DIR / "skills" / "board_manager.py"
        result = subprocess.run(
            [sys.executable, str(import_script)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  ❌ Erro no import: {result.stderr}")
            sys.exit(1)
        print("  ✅ Snapshot importado com sucesso.")

    # Carrega snapshot de hoje
    today_path = find_snapshot(date.today())
    if not today_path:
        today_path = find_latest_snapshot()
        if not today_path:
            print("❌ Nenhum snapshot encontrado. Execute com --import-first")
            sys.exit(1)
        print(f"  ℹ️  Usando snapshot mais recente: {today_path.name}")

    curr_snapshot = load_snapshot(today_path)

    # Tenta carregar snapshot de ontem para diff
    yesterday_path = find_snapshot(date.today() - timedelta(days=1))
    diff = None
    if yesterday_path:
        prev_snapshot = load_snapshot(yesterday_path)
        diff = diff_snapshots(prev_snapshot, curr_snapshot)
        print(f"  📊 Comparando com snapshot de ontem: {yesterday_path.name}")

    if args.json and diff:
        print(json.dumps(diff, ensure_ascii=False, indent=2))
        return

    report = generate_report(curr_snapshot, diff)
    print(report)

    if args.save:
        out = save_report(report)
        print(f"  💾 Relatório salvo em: {out}")


if __name__ == "__main__":
    main()
