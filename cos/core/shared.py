"""
JARVIS Core — Shared Utilities v1.0
Centraliza caminhos, carregamento de configurações e utilitários comuns.
"""

import json
import sys
from pathlib import Path
from datetime import date, datetime

# Forçar UTF-8 no Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Caminhos Base de forma dinâmica
BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = BASE_DIR / "cos" / "config"
LOGS_DIR = BASE_DIR / "cos" / "logs"
INTEGRATIONS_DIR = BASE_DIR / "cos" / "integrations"
SNAPSHOTS_DIR = INTEGRATIONS_DIR / "snapshots"
OUTPUT_DIR = BASE_DIR / "cos" / "briefings" / "output"

def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_env() -> dict:
    env = {}
    env_file = CONFIG_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

def get_config(name: str) -> dict:
    """Carrega configuração pelo nome (ex: 'areas', 'rules', 'trello_config')."""
    return load_json(CONFIG_DIR / f"{name}.json")

def get_today_log() -> list:
    return load_json(LOGS_DIR / f"{date.today().isoformat()}.json") or []

def get_latest_snapshot(board_name: str = "arte_comercial") -> dict:
    snapshots = sorted(SNAPSHOTS_DIR.glob(f"{board_name}_*.json"), reverse=True)
    return load_json(snapshots[0]) if snapshots else {}
