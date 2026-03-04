"""
COS — Governance Rules Engine v1.0
Aplica regras de governança e gera intervenções baseadas em dados.
"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import sys
from pathlib import Path
from datetime import date, datetime

# Integrar com o core
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from cos.core.shared import get_config, get_today_log, HEARTBEAT_FILE
from cos.engine.score_engine import calculate_daily_score
from cos.engine.predictive_engine import get_predictive_alerts, get_scores_range
from cos.engine.pipeline_sentinel import analyze_pipeline_bottlenecks
from cos.integrations.project_analyzer import scan_projects
from cos.integrations.openclaw_notifier import send_notification

def get_open_tasks_count() -> int:
    """Conta tarefas em aberto (eventos sem par 'concluido')."""
    events = get_today_log()
    started = sum(1 for e in events if "iniciou" in e.get("action", "").lower() or "started" in e.get("action", "").lower())
    finished = sum(1 for e in events if "concluiu" in e.get("action", "").lower() or "finished" in e.get("action", "").lower() or "entregou" in e.get("action", "").lower())
    return max(started - finished, 0)

def evaluate_governance() -> dict:
    """
    Avalia o estado atual e retorna intervenções necessárias.
    """
    rules = get_config("rules")
    today_score = calculate_daily_score()
    predictive_alerts = get_predictive_alerts(7)
    pipeline_alerts = analyze_pipeline_bottlenecks()
    project_data = scan_projects()
    
    interventions = []
    actions = []

    # --- REGRA 001: Foco Econômico Obrigatório ---
    scores_3d = get_scores_range(3)
    if len(scores_3d) >= 3:
        econ_scores = [s["areas"].get("economic_output", {}).get("score", 0) for s in scores_3d]
        if all(econ_scores[i] <= econ_scores[i-1] for i in range(1, len(econ_scores))):
            interventions.append({
                "rule": "RULE-001",
                "priority": "CRITICAL",
                "type": "mandatory",
                "message": f"🚨 RULE-001 ATIVADA: {rules['confrontation_template'].format(evidence=f'Output Econômico caindo há 3 dias consecutivos ({[round(s) for s in econ_scores]})', action='Pare o que está fazendo. Foco total em pipeline e receita agora.')}",
                "recommended_action": "economic_focus_mandatory"
            })

    # --- REGRA 002: Dispersão Operacional ---
    discipline_score = today_score["areas"].get("execution_discipline", {}).get("score", 0)
    if discipline_score < 55:
        open_tasks = get_open_tasks_count()
        if open_tasks >= 2:
            interventions.append({
                "rule": "RULE-002",
                "priority": "HIGH",
                "type": "alert",
                "message": f"⚠️ DISPERSÃO OPERACIONAL: Você está desperdiçando potencial. "
                           f"Evidência: {open_tasks} tarefas abertas, disciplina em {discipline_score:.0f}/100. "
                           f"Ajuste imediato: feche pelo menos 2 tarefas antes de iniciar qualquer nova.",
                "recommended_action": "close_pending_tasks"
            })

    # --- Intervenções de Projetos (Project Sentinel) ---
    proj_summary = project_data.get("summary", {})
    if proj_summary.get("doc_missing", 0) > 0:
        interventions.append({
            "rule": "SENTINEL-DOCS",
            "priority": "MEDIUM",
            "type": "documentation",
            "message": f"⚠️ MATURIDADE DE SISTEMA BAIXA: {proj_summary['doc_missing']}/{proj_summary['total']} projetos sem README.md. "
                       f"O JARVIS não consegue te guiar no escuro. Crie documentação básica para seus projetos.",
            "recommended_action": "create_project_docs"
        })
    
    if proj_summary.get("idle_warning", 0) > 0:
        interventions.append({
            "rule": "SENTINEL-IDLE",
            "priority": "HIGH",
            "type": "project_abandonment",
            "message": f"🔔 ALERTA DE ABANDONO: {proj_summary['idle_warning']} projetos parados há mais de 3 dias. "
                       f"Projetos 'frios' tendem a morrer. Decida: retomar ou arquivar.",
            "recommended_action": "review_idle_projects"
        })

    # --- Intevenções de Pipeline (Pipeline Sentinel) ---
    for alert in pipeline_alerts:
        interventions.append({
            "rule": "SENTINEL-" + alert["type"].upper(),
            "priority": alert["priority"],
            "type": alert["type"],
            "message": alert["message"],
            "recommended_action": "review_trello_pipeline",
            "evidence": alert.get("evidence", "")
        })

    # --- Alertas Preditivos como Intervenções ---
    for alert in predictive_alerts:
        if alert["priority"] in ["critical", "high"]:
            interventions.append({
                "rule": "PREDICTIVE",
                "priority": alert["priority"].upper(),
                "type": alert["type"],
                "message": alert["message"],
                "recommended_action": alert["type"],
                "evidence": alert.get("evidence", "")
            })

    # Definir ações recomendadas para o dia
    critical_area = today_score.get("critical_area", {})
    if critical_area.get("score", 100) < 50:
        actions.append(f"🎯 FOCO PRIORITÁRIO: {critical_area.get('name', '')} — score {critical_area.get('score', 0):.0f}")

    if proj_summary.get("total_todos", 0) > 1000:
        actions.append(f"📦 DÍVIDA TÉCNICA CRÍTICA: {proj_summary['total_todos']} TODOs detectados. Hora de um dia 'Clean Up'.")

    result = {
        "timestamp": datetime.now().isoformat(),
        "current_score": today_score["global_score"],
        "classification": today_score["classification"],
        "interventions": interventions,
        "intervention_count": len(interventions),
        "actions": actions,
        "critical_area": today_score.get("critical_area", {}),
        "mode": "adaptive"
    }

    # ---- FAST RAG HEARTBEAT INJECTION ----
    # Save a minified lightweight state for fast access without recalculation
    try:
        with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": result["timestamp"],
                "score": result["current_score"],
                "classification": result["classification"],
                "interventions_active": result["intervention_count"],
                "critical_area": result["critical_area"],
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        import traceback
        import sys
        print(f"Erro ao salvar heartbeat: {e}\n{traceback.format_exc()}", file=sys.stderr)

    return result


def print_governance_report() -> None:
    result = evaluate_governance()

    print(f"\n{'='*60}")
    print(f"  ⚖️  GOVERNANCE ENGINE — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    print(f"  Score Global: {result['current_score']}/100 — {result['classification']}")

    if result["interventions"]:
        print(f"\n  🚨 INTERVENÇÕES ATIVAS ({result['intervention_count']}):")
        for iv in result["interventions"]:
            print(f"\n  [{iv['priority']}] {iv['message']}")
            # Disparo Proativo via OpenClaw para alertas CRITICAL ou HIGH
            if iv['priority'] in ["CRITICAL", "HIGH"]:
                send_notification(iv['message'], priority="high")
    else:
        print(f"\n  ✅ Nenhuma intervenção necessária no momento.")

    if result["actions"]:
        print(f"\n  📋 AÇÕES RECOMENDADAS:")
        for a in result["actions"]:
            print(f"  • {a}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="COS Governance Rules Engine")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    if args.json:
        result = evaluate_governance()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_governance_report()
