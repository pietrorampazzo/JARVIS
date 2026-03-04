"""
COS — Midday Check v1.0 (13:00)
Checkpoint tático do meio-dia: progresso, desvios, ajuste recomendado.
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "engine"))
from score_engine import calculate_daily_score
from governance_rules import evaluate_governance

sys.path.insert(0, str(BASE_DIR / "engine"))
import gerador_dia

LOGS_DIR = BASE_DIR / "logs"

def get_morning_events_count() -> int:
    """Conta eventos logados na parte da manhã (até 13h)."""
    log_path = LOGS_DIR / f"{date.today().isoformat()}.json"
    if not log_path.exists():
        return 0
    with open(log_path, "r", encoding="utf-8") as f:
        events = json.load(f)
    morning_events = [
        e for e in events
        if datetime.fromisoformat(e["timestamp"]).hour < 13
    ]
    return len(morning_events)


def get_progress_percent() -> float:
    """Estima % de progresso baseado nos eventos da manhã vs meta mínima."""
    events_count = get_morning_events_count()
    # Meta: ao menos 3 eventos de impacto relevante por manhã
    return min((events_count / 3) * 100, 100)


def generate_midday_check() -> str:
    now = datetime.now()
    score = calculate_daily_score()
    governance = evaluate_governance()
    progress = get_progress_percent()
    morning_events = get_morning_events_count()

    lines = []
    lines.append("=" * 62)
    lines.append(f"  ☀️  MIDDAY ENFORCEMENT — {now.strftime('%d/%m/%Y %H:%M')}")
    lines.append("=" * 62)

    # Progresso parcial
    bar_full = int(progress / 10)
    bar = "█" * bar_full + "▒" * (10 - bar_full)
    lines.append(f"\n  📊 PROGRESSO PARCIAL: {progress:.0f}%")
    lines.append(f"  [{bar}]  {morning_events} eventos logados esta manhã")

    # Score parcial
    lines.append(f"\n  Score Global Parcial: {score['global_score']:.0f}/100")

    # Desvios detectados
    if governance["interventions"]:
        lines.append(f"\n  ⚠️  DESVIOS DETECTADOS ({governance['intervention_count']}):")
        for iv in governance["interventions"][:2]:
            lines.append(f"  → {iv['message']}")
    else:
        lines.append(f"\n  ✅ Sem desvios críticos detectados.")

    # Ajuste recomendado
    lines.append(f"\n  🎯 AJUSTE RECOMENDADO")
    if progress < 60:
        lines.append(f"  → Você está abaixo de 60% de progresso. Acelere fechamento de tarefas.")
    elif progress < 85:
        lines.append(f"  → Bom ritmo. Finalize as tarefas de alta prioridade antes das 17h.")
    else:
        lines.append(f"  → Excelente manhã! Mantenha o foco nas tarefas de sistema na tarde.")

    # Comunicação pendente
    lines.append(f"\n  💬 VERIFICAR COMUNICAÇÃO")
    lines.append(f"  → Algum follow-up pendente de clientes/parceiros? Log: --area relations_influence")

    lines.append("\n" + "=" * 62)
    lines.append(f"  🕕 Próximo check: 19:00 — End-of-Day Audit")
    lines.append("=" * 62 + "\n")

    return "\n".join(lines)


if __name__ == "__main__":
    brief = generate_midday_check()
    print(brief)
    
    # Atualiza o estado global no dia.md
    print("Atualizando dia.md...")
    gerador_dia.build_dia_md()
