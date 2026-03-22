"""
JARVIS Cron Architect v1.0
Gerencia o agendamento de tarefas recorrentes no Windows via Task Scheduler.
Permite definir jobs via cron.json e sincronizá-los com o sistema operacional.
"""

import sys
import json
import subprocess
import os
from pathlib import Path

# Setup caminhos
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
CRON_CONFIG = BASE_DIR / "engine" / "config" / "cron.json"

def load_cron():
    if CRON_CONFIG.exists():
        try:
            with open(CRON_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"jobs": []}

def save_cron(data):
    CRON_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    with open(CRON_CONFIG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sync_with_windows():
    print("🔄 [CRON] Sincronizando com Windows Task Scheduler...")
    data = load_cron()
    python_exe = sys.executable
    
    for job in data.get("jobs", []):
        if not job.get("enabled", True):
            # Tenta remover se estiver desativado
            subprocess.run(["schtasks", "/Delete", "/TN", f"JARVIS_{job['name']}", "/F"], capture_output=True)
            continue
            
        name = job["name"]
        script = BASE_DIR / job["script"]
        freq = job.get("frequency", "HOURLY") # MINUTE, HOURLY, DAILY, WEEKLY
        modifier = job.get("modifier", "1")
        
        if not script.exists():
            print(f"  ⚠ Script não encontrado para job '{name}': {script}")
            continue

        # Comando schtasks para criação/update
        cmd = [
            "schtasks", "/Create", "/F",
            "/TN", f"JARVIS_{name}",
            "/TR", f'"{python_exe}" "{script}"',
            "/SC", freq,
            "/MO", modifier,
            "/ST", job.get("start_time", "00:00")
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"  ✅ Job '{name}' sincronizado ({freq} a cada {modifier}).")
        except Exception as e:
            print(f"  ❌ Erro ao sincronizar job '{name}': {e}")

def add_job(name, script_rel_path, frequency="HOURLY", modifier="1", start_time="00:00"):
    data = load_cron()
    # Verifica se já existe
    for job in data["jobs"]:
        if job["name"] == name:
            job.update({"script": script_rel_path, "frequency": frequency, "modifier": modifier, "start_time": start_time, "enabled": True})
            break
    else:
        data["jobs"].append({
            "name": name,
            "script": script_rel_path,
            "frequency": frequency,
            "modifier": modifier,
            "start_time": start_time,
            "enabled": True
        })
    
    save_cron(data)
    print(f"✨ Job '{name}' adicionado ao cron.json.")
    sync_with_windows()

def list_jobs():
    data = load_cron()
    print("\n📋 JOBS AGENDADOS NO JARVIS:")
    if not data["jobs"]:
        print("  (Nenhum job cadastrado)")
        return
        
    for job in data["jobs"]:
        status = "ON" if job.get("enabled", True) else "OFF"
        print(f"  [{status}] {job['name']} -> {job['script']} ({job['frequency']} - mod:{job['modifier']})")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="JARVIS Cron Architect")
    parser.add_argument("action", choices=["list", "sync", "add"], help="Ação a ser executada")
    parser.add_argument("--name", help="Nome do job")
    parser.add_argument("--script", help="Caminho relativo do script (ex: engine/monitoring/jarvis_pulse.py)")
    parser.add_argument("--freq", default="HOURLY", help="Frequência (MINUTE, HOURLY, DAILY)")
    parser.add_argument("--mod", default="1", help="Modificador (ex: a cada 15 min -> freq:MINUTE, mod:15)")
    
    args = parser.parse_args()
    
    if args.action == "list":
        list_jobs()
    elif args.action == "sync":
        sync_with_windows()
    elif args.action == "add":
        if not args.name or not args.script:
            print("❌ Erro: --name e --script são obrigatórios para 'add'.")
        else:
            add_job(args.name, args.script, args.freq, args.mod)
