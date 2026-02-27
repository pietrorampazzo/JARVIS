"""
COS — Predictive Engine v1.0
Analisa tendências de 3/7/30 dias e gera alertas preditivos.
"""

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import sys
from pathlib import Path
from datetime import date, timedelta

# Integrar com o core
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from cos.core.shared import get_config
from cos.engine.score_engine import calculate_daily_score

def get_scores_range(days: int) -> list[dict]:
    """Retorna lista de scores dos últimos N dias."""
    scores = []
    today = date.today()
    for i in range(days):
        d = today - timedelta(days=i)
        try:
            score = calculate_daily_score(d)
            scores.append(score)
        except Exception:
            pass
    return scores[::-1]  # mais antigo primeiro


def calculate_trend(scores: list[dict], field: str = "global_score") -> float:
    """Calcula tendência linear simples (slope)."""
    if len(scores) < 2:
        return 0.0
    values = [s[field] for s in scores]
    n = len(values)
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    return round(numerator / denominator if denominator != 0 else 0.0, 3)


def detect_economic_decline(scores: list[dict], min_days: int = 3) -> bool:
    """Verifica se Output Econômico caiu por N dias consecutivos."""
    if len(scores) < min_days:
        return False
    recent = scores[-min_days:]
    economic = [s["areas"].get("economic_output", {}).get("score", 0) for s in recent]
    # Verifica se cada dia foi menor que o anterior
    return all(economic[i] <= economic[i-1] for i in range(1, len(economic)))


def detect_dispersion(scores: list[dict]) -> bool:
    """Verifica se Score de Disciplina está em queda by 2 dias."""
    if len(scores) < 2:
        return False
    recent = [s["areas"].get("execution_discipline", {}).get("score", 0) for s in scores[-2:]]
    return recent[-1] < 55 and recent[-1] < recent[0]


def get_predictive_alerts(days: int = 7) -> list[dict]:
    """
    Gera lista de alertas preditivos baseados em tendências.
    Returns lista de dicts com {type, priority, message, evidence}
    """
    thresholds = get_config("thresholds")
    scores = get_scores_range(days)
    alerts = []

    if len(scores) < 2:
        return [{"type": "info", "priority": "low", "message": "Dados insuficientes para análise preditiva. Continue registrando eventos.", "evidence": ""}]

    global_trend = calculate_trend(scores)
    current_score = scores[-1]["global_score"] if scores else 0

    # --- ALERTA 1: Tendência global negativa ---
    if global_trend < -2:
        projected = current_score + (global_trend * 3)
        alerts.append({
            "type": "performance_decline",
            "priority": "high",
            "message": f"⚠️ TENDÊNCIA NEGATIVA DETECTADA: Score global caindo {abs(global_trend):.1f} pts/dia. "
                       f"Projeção em 3 dias: {max(projected, 0):.0f}/100.",
            "evidence": f"Trend 7d: {global_trend:.2f} | Score atual: {current_score}"
        })

    # --- ALERTA 2: Queda econômica consecutiva ---
    if detect_economic_decline(scores):
        alerts.append({
            "type": "economic_decline",
            "priority": "critical",
            "message": "🚨 FOCO ECONÔMICO OBRIGATÓRIO: Output Econômico em queda há 3+ dias. "
                       "Pipeline pode estar travado. Ação imediata necessária.",
            "evidence": f"Economic scores: {[round(s['areas'].get('economic_output', {}).get('score', 0), 1) for s in scores[-3:]]}"
        })

    # --- ALERTA 3: Dispersão operacional ---
    if detect_dispersion(scores):
        alerts.append({
            "type": "operational_dispersion",
            "priority": "medium",
            "message": "⚠️ DISPERSÃO DETECTADA: Disciplina caindo e abaixo de 55. "
                       "Você está abrindo mais tarefas do que fechando.",
            "evidence": f"Discipline score: {scores[-1]['areas'].get('execution_discipline', {}).get('score', 0):.0f}"
        })

    # --- ALERTA 4: Score global baixo persistente ---
    if len(scores) >= 3:
        last_3 = [s["global_score"] for s in scores[-3:]]
        if all(s < 55 for s in last_3):
            alerts.append({
                "type": "sustained_underperformance",
                "priority": "high",
                "message": f"🚨 3 DIAS DE BAIXA PERFORMANCE ({', '.join(str(round(s)) for s in last_3)}). "
                           "O sistema está detectando padrão de sabotagem estrutural.",
                "evidence": f"Scores: {last_3}"
            })

    if not alerts:
        alerts.append({
            "type": "positive",
            "priority": "info",
            "message": f"✅ Tendência ESTÁVEL/POSITIVA nos últimos {days} dias. Mantenha o ritmo.",
            "evidence": f"Trend: {global_trend:+.2f} pts/dia"
        })

    return alerts


def print_predictive_report(days: int = 7) -> None:
    alerts = get_predictive_alerts(days)
    scores = get_scores_range(days)

    print(f"\n{'='*60}")
    print(f"  🔮 ANÁLISE PREDITIVA — Últimos {days} dias")
    print(f"{'='*60}")

    if scores:
        print(f"  Tendência global: {calculate_trend(scores):+.2f} pts/dia")
        scores_line = " → ".join(str(round(s["global_score"])) for s in scores)
        print(f"  Evolução: {scores_line}")

    print(f"\n  Alertas ({len(alerts)}):")
    for a in alerts:
        print(f"\n  [{a['priority'].upper()}] {a['message']}")
        if a.get("evidence"):
            print(f"  Evidência: {a['evidence']}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="COS Predictive Engine")
    parser.add_argument("--days", type=int, default=7, help="Janela de análise em dias")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    if args.json:
        alerts = get_predictive_alerts(args.days)
        print(json.dumps(alerts, ensure_ascii=False, indent=2))
    else:
        print_predictive_report(args.days)
