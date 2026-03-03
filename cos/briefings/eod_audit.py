"""
COS — End-of-Day Audit v1.0 (19:00)
Auditoria final do dia: score, ganhos, perdas e ajuste para amanhã.
"""

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "engine"))
from score_engine import calculate_daily_score, print_score_report
from predictive_engine import get_predictive_alerts
from governance_rules import evaluate_governance

sys.path.insert(0, str(BASE_DIR / "engine"))
import gerador_dia

LOGS_DIR = BASE_DIR / "logs"


def get_all_day_events() -> list:
    log_path = LOGS_DIR / f"{date.today().isoformat()}.json"
    if not log_path.exists():
        return []
    with open(log_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_day_narrative(score: dict, events: list) -> list[str]:
    """Gera narrativa textual do que aconteceu no dia."""
    lines = []
    by_area = score["areas"]

    best_area = score["best_area"]
    worst_area = score["critical_area"]

    lines.append(f"🏆 Melhor performance: {best_area['name']} ({best_area['score']:.0f}/100)")
    lines.append(f"⚠️  Área mais fraca:   {worst_area['name']} ({worst_area['score']:.0f}/100)")

    total_duration = sum(e.get("duration_minutes", 0) for e in events)
    hours = total_duration // 60
    minutes = total_duration % 60
    lines.append(f"⏱️  Tempo produtivo registrado: {hours}h {minutes}min")
    lines.append(f"📋  Total de eventos: {len(events)}")

    high_impact = [e for e in events if e["impact"] >= 4]
    if high_impact:
        lines.append(f"\n  🎯 Movimentos de alto impacto:")
        for e in high_impact[:3]:
            lines.append(f"     • [{e['area_name'][:15]}] {e['action']}")

    return lines


def save_eod_report(content: str):
    output_dir = BASE_DIR / "briefings" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"eod_{date.today().isoformat()}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# End-of-Day Audit — {date.today().strftime('%d/%m/%Y')}\n\n")
        f.write("```\n" + content + "```\n")
    return out_path


def generate_eod_audit() -> str:
    now = datetime.now()
    score = calculate_daily_score()
    events = get_all_day_events()
    governance = evaluate_governance()
    alerts = get_predictive_alerts(3)
    narrative = build_day_narrative(score, events)

    lines = []
    lines.append("=" * 62)
    lines.append(f"  🌙  END-OF-DAY AUDIT — {now.strftime('%d/%m/%Y %H:%M')}")
    lines.append("=" * 62)

    # Score final
    lines.append(f"\n  📊 SCORE FINAL DO DIA: {score['global_score']:.0f}/100")
    lines.append(f"  {score['emoji']} {score['classification']}")

    # Por área
    lines.append(f"\n  Por Área:")
    for area_id, data in score["areas"].items():
        bar = "█" * int(data["score"] / 10) + "▒" * (10 - int(data["score"] / 10))
        lines.append(f"  {data['name'][:25]:<25} {data['score']:>5.0f}  [{bar}]")

    # Narrativa do dia
    lines.append(f"\n  📖 RESUMO DO DIA:")
    for line in narrative:
        lines.append(f"  {line}")

    # Onde perdeu energia
    losing_areas = [
        (k, v) for k, v in score["areas"].items()
        if v["score"] < 50
    ]
    if losing_areas:
        lines.append(f"\n  ⚡ ONDE PERDEU ENERGIA:")
        for area_id, data in losing_areas:
            lines.append(f"  → {data['name']}: {data['score']:.0f}/100 — Precisa de atenção amanhã")

    # Onde ganhou vantagem
    winning_areas = [(k, v) for k, v in score["areas"].items() if v["score"] >= 75]
    if winning_areas:
        lines.append(f"\n  ✅ ONDE GANHOU VANTAGEM:")
        for area_id, data in winning_areas:
            lines.append(f"  → {data['name']}: {data['score']:.0f}/100")

    # Alertas para amanhã
    critical_alerts = [a for a in alerts if a["priority"] in ["critical", "high"]]
    if critical_alerts:
        lines.append(f"\n  🔮 AJUSTE PARA AMANHÃ:")
        for a in critical_alerts[:2]:
            lines.append(f"  → {a['message']}")
    else:
        lines.append(f"\n  🔮 AMANHÃ: Mantenha a consistência. Foco em Output Econômico.")

    lines.append("\n" + "=" * 62)
    lines.append(f"  🌅 Próximo briefing: amanhã às 08:00")
    lines.append("=" * 62 + "\n")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="COS End-of-Day Audit (19:00)")
    parser.add_argument("--save", action="store_true", help="Salva em arquivo .md")
    args = parser.parse_args()

    audit = generate_eod_audit()
    print(audit)
    
    # Atualiza RAG no dia.md
    print("Atualizando dia.md...")
    gerador_dia.build_dia_md()

    if args.save:
        path = save_eod_report(audit)
        print(f"💾 Auditoria salva em: {path}")
