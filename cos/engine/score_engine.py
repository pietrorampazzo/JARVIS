"""
COS — Score Engine v1.0
Calcula o score diário por área e o score global ponderado.
"""

import json
import sys
from datetime import date, timedelta
from typing import Optional

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import sys
from pathlib import Path
from datetime import date, datetime

# Integrar com o core
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from cos.core.shared import get_config, get_today_log, load_json, LOGS_DIR


def calculate_area_score(area_events: list, thresholds: dict) -> float:
    """
    Calcula score de uma área (0–100) baseado em:
    - Número de eventos
    - Impacto médio
    - Duração total
    """
    if not area_events:
        return 0.0

    total_impact = sum(e["impact"] for e in area_events)
    avg_impact = total_impact / len(area_events)
    event_count = len(area_events)
    total_duration = sum(e.get("duration_minutes", 0) for e in area_events)

    # Fórmula: impacto médio (0-5) * 12 = 0-60 pts base
    # + bônus por múltiplos eventos (até +20)
    # + bônus por duração substancial (até +20)
    base_score = (avg_impact / 5) * 60
    event_bonus = min(event_count * 5, 20)
    duration_bonus = min((total_duration / 60) * 10, 20)

    score = base_score + event_bonus + duration_bonus
    return min(round(score, 1), 100.0)


def get_classification(score: float, thresholds: dict) -> dict:
    """Retorna classificação do score."""
    levels = thresholds["score_thresholds"]
    for key in ["excellent", "good", "average", "poor"]:
        if score >= levels[key]["min"]:
            return levels[key]
    return levels["poor"]


def calculate_score_gap(current_global_score: float, thresholds: dict) -> dict:
    """
    Calcula os pontos faltantes para atingir as próximas classificações (Bom/Excelente)
    e sugere qual área focar com base nos pesos.
    """
    levels = thresholds["score_thresholds"]
    gaps = {}
    
    good_min = levels["good"]["min"]
    excellent_min = levels["excellent"]["min"]
    
    if current_global_score < good_min:
        gaps["good"] = {
            "target": good_min,
            "missing": round(good_min - current_global_score, 1),
            "label": levels["good"]["label"]
        }
        
    if current_global_score < excellent_min:
        gaps["excellent"] = {
            "target": excellent_min,
            "missing": round(excellent_min - current_global_score, 1),
            "label": levels["excellent"]["label"]
        }
        
    return gaps


def calculate_daily_score(target_date: Optional[date] = None) -> dict:
    """
    Calcula o score completo do dia.
    
    Returns:
        dict com score global, por área, classificação e eventos
    """
    if target_date is None:
        target_date = date.today()

    areas_config = get_config("areas")
    areas = {a["id"]: a for a in areas_config["areas"]}
    thresholds = get_config("thresholds")
    
    # Carregar logs do dia alvo
    log_path = LOGS_DIR / f"{target_date.isoformat()}.json"
    events = load_json(log_path) if log_path.exists() else []

    area_scores = {}
    for area_id, area_info in areas.items():
        area_events = [e for e in events if e["area"] == area_id]
        score = calculate_area_score(area_events, thresholds)
        area_scores[area_id] = {
            "name": area_info["name"],
            "weight": area_info["weight"],
            "score": score,
            "events": len(area_events),
            "weighted_contribution": round(score * area_info["weight"], 2)
        }

    # Score global ponderado
    global_score = sum(
        v["score"] * v["weight"] for v in area_scores.values()
    )
    global_score = round(global_score, 1)

    classification = get_classification(global_score, thresholds)

    # Área mais crítica (menor score ponderado)
    critical_area = min(
        area_scores.items(),
        key=lambda x: x[1]["score"] * x[1]["weight"]
    )

    # Área com melhor performance
    best_area = max(area_scores.items(), key=lambda x: x[1]["score"])

    result = {
        "date": target_date.isoformat(),
        "global_score": global_score,
        "classification": classification["label"],
        "emoji": classification["emoji"],
        "total_events": len(events),
        "critical_area": {
            "id": critical_area[0],
            "name": critical_area[1]["name"],
            "score": critical_area[1]["score"]
        },
        "best_area": {
            "id": best_area[0],
            "name": best_area[1]["name"],
            "score": best_area[1]["score"]
        },
        "areas": area_scores,
        "gaps": calculate_score_gap(global_score, thresholds)
    }

    return result


def print_score_report(score_data: dict) -> None:
    """Exibe relatório de score formatado no terminal."""
    print(f"\n{'='*60}")
    print(f"  📊 SCORE DIÁRIO — {score_data['date']}")
    print(f"{'='*60}")
    print(f"  {score_data['emoji']} Score Global: {score_data['global_score']}/100")
    print(f"  Status:       {score_data['classification']}")
    print(f"  Eventos:      {score_data['total_events']}")
    print(f"\n  Por Área:")
    print(f"  {'Área':<28} {'Score':>6}  {'Contribuição':>12}")
    print(f"  {'-'*50}")
    for area_id, data in score_data["areas"].items():
        bar = "█" * int(data["score"] / 10) + "▒" * (10 - int(data["score"] / 10))
        print(f"  {data['name']:<28} {data['score']:>5.1f}  {bar}")
    print(f"\n  ⚠️  Área Crítica: {score_data['critical_area']['name']} ({score_data['critical_area']['score']:.1f})")
    print(f"  🏆 Melhor Área:  {score_data['best_area']['name']} ({score_data['best_area']['score']:.1f})")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="COS Score Engine")
    parser.add_argument("--date", type=str, default="today", help="Data (YYYY-MM-DD ou 'today')")
    parser.add_argument("--json", action="store_true", help="Output em JSON")
    args = parser.parse_args()

    target = date.today() if args.date == "today" else date.fromisoformat(args.date)
    result = calculate_daily_score(target)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_score_report(result)
