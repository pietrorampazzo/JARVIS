"""
JARVIS BRIDGE EXPORTER
Exporta o estado atual do ecossistema JARVIS para consumo do OpenClaw.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Paths
COS_DIR = Path(__file__).parent.parent
BRIDGE_DIR = COS_DIR / "bridge"
PROJECTS_JSON = COS_DIR / "config" / "projects.json"
BRIDGE_FILE = BRIDGE_DIR / "JARVIS_STATE.json"

def get_latest_score():
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = COS_DIR / "logs" / f"{today}.json"
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("score", 0.0)
        except: pass
    return 0.0

def get_projects_health():
    health_data = {}
    if PROJECTS_JSON.exists():
        try:
            with open(PROJECTS_JSON, "r", encoding="utf-8") as f:
                projects = json.load(f).get("projects", [])
                for p in projects:
                    p_id = p.get("id")
                    p_path = p.get("path")
                    if not p_id or not p_path: continue
                    
                    health_file = Path(p_path) / "JARVIS" / "logs" / "health.json"
                    if health_file.exists():
                        try:
                            with open(health_file, "r", encoding="utf-8") as hf:
                                h_data = json.load(hf)
                                # Se for lista (histórico), pega o último
                                if isinstance(h_data, list):
                                    health_data[p_id] = h_data[-1]
                                else:
                                    health_data[p_id] = h_data
                        except: pass
        except: pass
    return health_data

def export_state():
    state = {
        "timestamp": datetime.now().isoformat(),
        "global_score": get_latest_score(),
        "projects_health": get_projects_health(),
        "system_status": "OPERACIONAL",
        "daemon_active": True,
        "identity": "JARVIS COS v1.0",
        "description": "Cérebro Operacional de Pietro Rampazzo"
    }
    
    with open(BRIDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    
    # Também gera um TXT para leitura rápida por agentes LLM sem parsing JSON
    with open(BRIDGE_DIR / "JARVIS_STATUS.txt", "w", encoding="utf-8") as f:
        f.write(f"JARVIS STATE @ {state['timestamp']}\n")
        f.write(f"Global Score: {state['global_score']}/100\n")
        f.write("Project Health:\n")
        for p, h in state['projects_health'].items():
            f.write(f"  - {p}: {h.get('verdict', 'N/A')} ({h.get('score', 0)}/100)\n")

    print(f"✅ Estado exportado para {BRIDGE_FILE}")

if __name__ == "__main__":
    export_state()
