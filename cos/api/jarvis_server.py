"""
JARVIS Network - Servidor Mestre (FastAPI)
Roda na LenovoPeti. Recebe conexões HTTP REST da rede local / Tailscale.
Objetivo: Eliminar gargalos de concorrência e delays de FileSystem (OneDrive).
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
import sys
import json
from pathlib import Path
from datetime import datetime

# Path Injection p/ acessar o Core
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from logger.event_logger import log_event
from engine.score_engine import calculate_daily_score
from engine.bridge_exporter import get_latest_score, get_projects_health

app = FastAPI(title="JARVIS COS Master API", version="1.0.0")

# --- MODELOS ---
class LogEventRequest(BaseModel):
    area_id: str
    category: str
    action: str
    impact: int
    duration_minutes: int
    project: str = ""

# --- ENDPOINTS ---
@app.get("/")
def health_check():
    """Valida se o JARVIS Proxy está online."""
    return {"status": "online", "system": "JARVIS COS Master"}


@app.post("/api/log")
async def receive_log(event: LogEventRequest):
    """
    Recebe um evento do logger (Antigravity ou OpenClaw) e escreve localmente.
    Evita conflito de concorrência, pois FastAPI serializa/lida com I/O de forma segura.
    """
    try:
        logged_event = log_event(
            area=event.area_id,
            category=event.category,
            action=event.action,
            impact=event.impact,
            duration_minutes=event.duration_minutes,
            project=event.project
        )
        return {
            "status": "success", 
            "message": "Evento registrado no Cérebro (Master)",
            "event": logged_event
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro Interno: {str(e)}")


@app.get("/api/state")
def get_system_state():
    """
    Retorna o estado global (Score, Saúde dos Projetos) direto da memória/disco do Master.
    """
    state = {
        "timestamp": datetime.now().isoformat(),
        "global_score": get_latest_score(),
        "projects_health": get_projects_health(),
    }
    return state


if __name__ == "__main__":
    # Roda nativamente para exposição na LAN/Tailscale
    # 0.0.0.0 permite que outras máquinas na mesma rede VPN acessem
    uvicorn.run("jarvis_server:app", host="0.0.0.0", port=8000, reload=True)
