import subprocess
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Configuração de caminhos
SCRIPT_DIR = Path(__file__).parent
COS_DIR = SCRIPT_DIR.parent
PROJECTS_JSON = COS_DIR / "config" / "projects.json"
LOG_FILE = COS_DIR / "logs" / "workspace_pull.log"

# Garante que a pasta de logs existe
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configuração de logs
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s - WORKSPACE PULL - %(levelname)s - %(message)s'
)

def load_projects():
    """Carrega a lista de projetos do arquivo de configuração."""
    if PROJECTS_JSON.exists():
        try:
            with open(PROJECTS_JSON, "r", encoding="utf-8") as f:
                return json.load(f).get("projects", [])
        except Exception as e:
            logging.error(f"Erro ao carregar projects.json: {e}")
            print(f"❌ Erro ao carregar projects.json: {e}")
    else:
        logging.error(f"Arquivo projects.json não encontrado em: {PROJECTS_JSON}")
        print(f"❌ Arquivo projects.json não encontrado.")
    return []

def run_git_command(cwd, command):
    """Executa um comando git em um diretório específico."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True 
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def pull_all():
    projects = load_projects()
    summary = []
    
    print(f"\n🚀 Iniciando Global Workspace Pull...")
    logging.info("--- Início do Ciclo de Pull Global ---")
    
    for proj in projects:
        proj_name = proj.get("name", proj.get("id", "Unknown"))
        proj_path = proj.get("path")
        
        if not proj_path or not os.path.exists(proj_path):
            logging.warning(f"⏩ Pulando {proj_name}: Caminho não encontrado ({proj_path})")
            continue
            
        git_dir = Path(proj_path) / ".git"
        if not git_dir.exists():
            logging.info(f"⏩ Pulando {proj_name}: Não é um repositório git.")
            continue
            
        print(f"📥 Processando: {proj_name}...")
        
        # 1. git pull
        success, out = run_git_command(proj_path, "git pull")
        if success:
            if "Already up to date" in out:
                logging.info(f"✅ {proj_name}: Já está atualizado.")
                print(f"   - Já está atualizado.")
                summary.append(f"{proj_name}: Up to date")
            else:
                logging.info(f"🚀 {proj_name}: Pull realizado com sucesso! Detalhes: {out}")
                print(f"   - Atualizado com sucesso.")
                summary.append(f"{proj_name}: Atualizado")
        else:
            logging.error(f"❌ Erro em 'git pull' para {proj_name}: {out}")
            print(f"   - Erro no Pull.")
            summary.append(f"{proj_name}: ERRO")

    print(f"\n🏁 Resumo Final do Pull:")
    for s in summary:
        print(f" - {s}")
    
    logging.info("--- Ciclo de Pull Global Finalizado ---")

if __name__ == "__main__":
    pull_all()
