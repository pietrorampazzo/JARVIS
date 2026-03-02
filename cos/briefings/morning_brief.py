"""
COS — Morning Briefing v1.0 (08:00)
Gera o relatório de direção estratégica do dia.
"""

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"

sys.path.insert(0, str(BASE_DIR / "engine"))
from score_engine import calculate_daily_score
from predictive_engine import get_predictive_alerts, get_scores_range
from governance_rules import evaluate_governance

sys.path.insert(0, str(BASE_DIR / "integrations"))
from openclaw_notifier import send_notification


def get_yesterday_score() -> dict:
    yesterday = date.today() - timedelta(days=1)
    return calculate_daily_score(yesterday)


def get_top_priorities(governance: dict) -> list[str]:
    priorities = []
    if governance["critical_area"]:
        area_name = governance["critical_area"].get("name", "")
        area_score = governance["critical_area"].get("score", 0)
        priorities.append(f"🔴 Reforçar '{area_name}' (score atual: {area_score:.0f})")
    priorities.append("🔵 1 avanço de Output Econômico (pipeline, licitação ou follow-up)")
    priorities.append("🟢 Fechar pelo menos 2 tarefas que estão abertas")
    return priorities[:5]


def generate_morning_brief() -> str:
    now = datetime.now()
    yesterday_score = get_yesterday_score()
    governance = evaluate_governance()
    alerts = get_predictive_alerts(3)
    scores_3d = get_scores_range(3)

    critical_alert = next(
        (a for a in alerts if a["priority"] in ["critical", "high"]), None
    )

    # Montar briefing
    lines = []
    lines.append("=" * 62)
    lines.append(f"  🌅  MORNING DIRECTIVE — {now.strftime('%A, %d de %B de %Y')}")
    lines.append(f"  COS v1.0  |  {now.strftime('%H:%M')}")
    lines.append("=" * 62)

    # Score de ontem
    lines.append(f"\n  📊 PERFORMANCE ONTEM")
    lines.append(f"  Score Global: {yesterday_score['global_score']}/100 — {yesterday_score['emoji']} {yesterday_score['classification']}")
    if scores_3d:
        trend_line = " → ".join(str(round(s["global_score"])) for s in scores_3d)
        lines.append(f"  Tendência 3d: {trend_line}")

    # Área crítica
    if governance.get("critical_area") and governance["critical_area"].get("score", 100) < 70:
        ca = governance["critical_area"]
        lines.append(f"\n  ⚠️  ÁREA CRÍTICA: {ca['name']} ({ca['score']:.0f}/100)")
        lines.append(f"  → Requer atenção prioritária hoje.")

    # Foco do dia
    lines.append(f"\n  🎯 FOCO OBRIGATÓRIO DO DIA")
    if governance.get("interventions"):
        iv = governance["interventions"][0]
        focus_action = iv.get("recommended_action", "economic_focus").replace("_", " ").title()
        lines.append(f"  → {focus_action}")
    else:
        lines.append(f"  → Manter consistência operacional e avançar em Output Econômico")

    # Top prioridades
    priorities = get_top_priorities(governance)
    lines.append(f"\n  🔥 TOP PRIORIDADES")
    for i, p in enumerate(priorities, 1):
        lines.append(f"  {i}. {p}")

    # Alertas críticos
    if critical_alert:
        lines.append(f"\n  🚨 ALERTA ESTRATÉGICO")
        lines.append(f"  {critical_alert['message']}")

    # Movimento estratégico
    lines.append(f"\n  🚀 MOVIMENTO ESTRATÉGICO DO DIA")
    lines.append(f"  → Identifique 1 ação que melhora o SISTEMA, não só entrega uma tarefa.")

    # Bloqueios ativos
    if governance.get("interventions"):
        lines.append(f"\n  ⛔ BLOQUEIOS ATIVOS ({governance['intervention_count']})")
        for iv in governance["interventions"][:2]:
            lines.append(f"  • [{iv['rule']}] {iv['type'].upper()}")

    lines.append("\n" + "=" * 62)
    lines.append("  💬 Log atividades: python cos/logger/event_logger.py --area <area> --action <acao>")
    lines.append("=" * 62 + "\n")

    return "\n".join(lines)


def save_brief_to_file(content: str) -> Path:
    """Salva o briefing em arquivo .md para upload ao JARVIS."""
    output_dir = BASE_DIR / "briefings" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"morning_{date.today().isoformat()}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Morning Briefing — {date.today().strftime('%d/%m/%Y')}\n\n")
        f.write("```\n")
        f.write(content)
        f.write("```\n")
    return out_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="COS Morning Briefing (08:00)")
    parser.add_argument("--save", action="store_true", help="Salva em arquivo .md")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    args = parser.parse_args()

    brief = generate_morning_brief()
    print(brief)

    # Disparo Pró-ativo via OpenClaw
    send_notification(brief, priority="briefing")

    if args.save:
        path = save_brief_to_file(brief)
        print(f"💾 Briefing salvo em: {path}")
