"""
JARVIS — Pipeline Sentinel Identity v1.0
Analisa gargalos estruturais no pipeline do Trello e gera alertas de governança.

Esta identidade foca em:
- Habilitações paradas (Gargalo de escala)
- Vencimentos em estágios ativos (Risco de perda)
- Dispersão entre múltiplos boards (Monitoramento de Foco)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Integrar com o core
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.shared import get_config, get_latest_snapshot

def analyze_pipeline_bottlenecks(board_name: str = "arte_comercial") -> list[dict]:
    """Detecta gargalos críticos no board."""
    snapshot = get_latest_snapshot(board_name)
    if not snapshot:
        return []

    config = get_config("trello_config")
    stages = config.get("pipeline_stages", {})
    
    alerts = []
    
    # 1. Analisar HABILITADO (O gargalo identificado anteriormente)
    habilitados = snapshot.get("cards_by_list", {}).get("HABILITADO", [])
    if len(habilitados) > 40:
        alerts.append({
            "identity": "Pipeline Sentinel",
            "priority": "HIGH",
            "type": "bottleneck",
            "message": f"🚨 GARGALO DE ESCALA: {len(habilitados)} licitações travadas em 'HABILITADO'. "
                       f"O fluxo de caixa futuro está represado. Necessário revisar status desses pregões.",
            "evidence": f"Board: {board_name} | Lista: HABILITADO | Qtd: {len(habilitados)}"
        })

    # 2. Analisar Vencimentos Críticos (PROPOSTAS e PREGAO)
    critical_lists = ["PROPOSTAS - PIEZO", "PROPOSTAS - ARTE", "PREGAO", "PREPARANDO"]
    overdue_count = 0
    for lst in critical_lists:
        cards = snapshot.get("cards_by_list", {}).get(lst, [])
        overdue_count += sum(1 for c in cards if c.get("overdue") and not c.get("closed"))

    if overdue_count > 5:
        alerts.append({
            "identity": "Pipeline Sentinel",
            "priority": "CRITICAL",
            "type": "risk",
            "message": f"🚨 RISCO DE PERDA: {overdue_count} licitações em estágios ativos estão com data VENCIDA. "
                       f"Ações imediatas de follow-up ou atualização de cronograma são mandatórias.",
            "evidence": f"Overdue active: {overdue_count}"
        })

    return alerts

def get_sentinel_report() -> str:
    alerts = analyze_pipeline_bottlenecks()
    if not alerts:
        return "✅ Pipeline Sentinel: Sem anomalias estruturais detectadas."
    
    lines = ["🤖 PIPELINE SENTINEL — Intervenções Ativas:"]
    for a in alerts:
        lines.append(f"  [{a['priority']}] {a['message']}")
    return "\n".join(lines)

if __name__ == "__main__":
    print(get_sentinel_report())
