import subprocess
import os
import json
import logging
from datetime import datetime
from pathlib import Path

import sys
from datetime import datetime
from pathlib import Path

# Configuração de caminhos
SCRIPT_DIR = Path(__file__).parent
COS_DIR = SCRIPT_DIR.parent
PROJECTS_JSON = COS_DIR / "config" / "projects.json"
LOG_FILE = COS_DIR / "logs" / "workspace_commit.log"

# Garante que a pasta de logs existe
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configuração de logs
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s - WORKSPACE COMMIT - %(levelname)s - %(message)s'
)

def load_projects():
    """Carrega a lista de projetos do arquivo de configuração."""
    if PROJECTS_JSON.exists():
        try:
            with open(PROJECTS_JSON, "r", encoding="utf-8") as f:
                return json.load(f).get("projects", [])
        except Exception as e:
            logging.error(f"Erro ao carregar projects.json: {e}")
    return []

def run_git_command(cwd, command):
    """Executa um comando git em um diretório específico."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True # Necessário para Windows se o comando git estiver no PATH
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def commit_and_push_all(custom_message=None):
    projects = load_projects()
    summary = []
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if custom_message:
        commit_message = f"JARVIS: {custom_message} [{timestamp}]"
    else:
        commit_message = f"JARVIS: Global Workspace Commit [{timestamp}]"
    
    print(f"\n🚀 Iniciando Global Workspace Commit...")
    print(f"📝 Mensagem: {commit_message}")
    logging.info(f"--- Início do Ciclo de Commit Global | Msg: {commit_message} ---")
    
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
            
        print(f"📦 Processando: {proj_name}...")
        
        # 1. git add .
        success, out = run_git_command(proj_path, "git add .")
        if not success:
            logging.error(f"❌ erro em 'git add' para {proj_name}: {out}")
            continue
            
        # 2. git status (para ver se há algo para commitar)
        success, out = run_git_command(proj_path, "git status --porcelain")
        if not out:
            logging.info(f"✅ {proj_name}: Nada para commitar.")
            print(f"   - Nada para commitar.")
            summary.append(f"{proj_name}: Clean")
            continue
            
        # 3. git commit
        success, out = run_git_command(proj_path, f'git commit -m "{commit_message}"')
        if not success:
            logging.error(f"❌ erro em 'git commit' para {proj_name}: {out}")
            summary.append(f"{proj_name}: Erro no Commit")
            continue
            
        # 4. git push
        success, out = run_git_command(proj_path, "git push")
        if success:
            logging.info(f"🚀 {proj_name}: Commit e Push realizados com sucesso!")
            print(f"   - Concluído com sucesso.")
            summary.append(f"{proj_name}: Sucesso")
        else:
            logging.error(f"❌ erro em 'git push' para {proj_name}: {out}")
            print(f"   - Erro no Push.")
            summary.append(f"{proj_name}: Erro no Push")

    print(f"\n🏁 Resumo Final:")
    for s in summary:
        print(f" - {s}")
    
    logging.info("--- Ciclo de Commit Global Finalizado ---")

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    commit_and_push_all(msg)
