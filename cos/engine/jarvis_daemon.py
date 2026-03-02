import schedule
import time
import logging
import subprocess
import os
import json
from datetime import datetime
from pathlib import Path

# Paths absolutos baseados na localização deste script
SCRIPT_DIR = Path(__file__).parent  # cos/engine/
COS_DIR = SCRIPT_DIR.parent          # cos/
LOG_FILE = COS_DIR / "logs" / "daemon.log"
PROJECTS_JSON = COS_DIR / "config" / "projects.json"

# Garante que a pasta de logs existe
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configuração Básica de Logs para o Daemon
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s - JARVIS DAEMON - %(levelname)s - %(message)s'
)

def load_projects():
    """Carrega a lista de projetos do arquivo de configuração."""
    if PROJECTS_JSON.exists():
        try:
            with open(PROJECTS_JSON, "r", encoding="utf-8") as f:
                return json.load(f).get("projects", [])
        except Exception as e:
            logging.error(f"⚠️ Erro ao carregar projects.json: {e}")
    return []

def run_script(script_path, description):
    """Executa um script Python e loga o resultado."""
    logging.info(f"Executando {description} ({script_path})...")
    try:
        # Verifica se o script existe antes de rodar
        if not os.path.exists(script_path):
            logging.warning(f"⏩ Pulando {description}: Script não encontrado em {script_path}")
            return False
            
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"✅ {description} executado com sucesso.")
            return True
        else:
            logging.error(f"❌ Falha no {description}. Erro: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"⚠️ Erro ao tentar executar {description}: {e}")
        return False

# ==========================================
# 🕒 ROTINAS AGENDADAS (CRONJOBS INTERNOS)
# ==========================================

def morning_routine():
    """Gera o Morning Briefing às 08:00"""
    run_script(str(COS_DIR / "briefings" / "morning_brief.py"), "Morning Briefing")

def midday_routine():
    """Roda a checagem de Metade do Dia e o Predictive Engine às 13:00"""
    run_script(str(COS_DIR / "briefings" / "midday_check.py"), "Midday Check")
    run_script(str(SCRIPT_DIR / "predictive_engine.py"), "Predictive Engine")

def evening_routine():
    """Auditoria de Log de Fim de Dia e Cálculo de Scores às 19:00"""
    run_script(str(SCRIPT_DIR / "score_engine.py"), "Score Engine e EOD Audit")

def continuous_monitoring():
    """Monitoramento contínuo (a cada 30 minutos) para todos os projetos"""
    logging.info("--- Iniciando Ciclo de Monitoramento Contínuo ---")
    
    # 0. Atualizar a Ponte OpenClaw
    run_script(str(SCRIPT_DIR / "bridge_exporter.py"), "Bridge Exporter (OpenClaw)")
    
    # 1. Pipeline global
    run_script(str(SCRIPT_DIR / "pipeline_sentinel.py"), "Pipeline Sentinel (Trello/Licitei)")
    
    # 2. Projetos Sidecar (Auditoria Dinâmica)
    projects = load_projects()
    for proj in projects:
        proj_id = proj.get("id")
        proj_path = proj.get("path")
        
        if not proj_id or not proj_path:
            continue
            
        # Tenta localizar o audit.py no padrão Sidecar JARVIS/audit.py
        audit_script = Path(proj_path) / "JARVIS" / "audit.py"
        
        if audit_script.exists():
            run_script(str(audit_script), f"Auditoria Sidecar: {proj_id}")
        else:
            # Fallback para o audit antigo se existir (retrocompatibilidade)
            old_audit = Path(proj_path) / "jarvis_audit.py"
            if old_audit.exists():
                run_script(str(old_audit), f"Auditoria (Antiga): {proj_id}")

    logging.info("--- Ciclo de Monitoramento Contínuo Finalizado ---")

# ==========================================
# 🔧 MAPEAMENTO DA AGENDA
# ==========================================

# Rotinas Diárias Fixas
schedule.every().day.at("08:00").do(morning_routine)
schedule.every().day.at("13:00").do(midday_routine)
schedule.every().day.at("19:00").do(evening_routine)

# Rotinas Contínuas (30 min)
schedule.every(30).minutes.do(continuous_monitoring)

if __name__ == "__main__":
    print("JARVIS Daemon (Motor Autonomo) Iniciado.")
    print(f"Log: {LOG_FILE}")
    print("Monitorando logs e executando cronjobs em background...")
    logging.info("JARVIS Daemon Iniciado.")
    
    # Executa a rotina contínua uma vez ao iniciar para verificação inicial
    continuous_monitoring()

    while True:
        schedule.run_pending()
        time.sleep(60) # Checa a agenda a cada 60 segundos

