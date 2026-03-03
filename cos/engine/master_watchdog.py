import time
import socket
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Setup paths
JARVIS_DIR = Path("C:/Users/pietr/OneDrive/.vscode/JARVIS")
LOG_DIR = JARVIS_DIR / "cos" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
WATCHDOG_LOG = LOG_DIR / "master_watchdog.log"

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - [WATCHDOG] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# File handler
file_handler = logging.FileHandler(WATCHDOG_LOG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def check_openclaw_port(port=18789):
    """Verifica se o OpenClaw esta rodando na porta especificada."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        result = s.connect_ex(('127.0.0.1', port))
        return result == 0

def start_openclaw():
    """Inicia o servidor do OpenClaw em background."""
    logging.warning("OpenClaw gateway (Petroll) offline. Iniciando...")
    try:
        # Usa creationflags=subprocess.CREATE_NEW_CONSOLE para rodar solto no windows
        creation_flags = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0x10)
        subprocess.Popen(
            ["openclaw", "gateway", "--port", "18789"],
            creationflags=creation_flags,
            shell=True
        )
        logging.info("OpenClaw gateway iniciado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao iniciar o OpenClaw: {e}")

def run_watchdog():
    logging.info("--- Master Watchdog JARVIS Iniciado ---")
    while True:
        try:
            # Verifica saude do Petroll (OpenClaw)
            if not check_openclaw_port(18789):
                start_openclaw()
            else:
                logging.info("OpenClaw gateway online (detectado na porta 18789).")

        except Exception as e:
            logging.error(f"Erro critico no loop do watchdog: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    run_watchdog()
