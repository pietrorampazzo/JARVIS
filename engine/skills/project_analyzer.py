"""
JARVIS — Project Sentinel v1.0
Monitora progresso e documentação de projetos pessoais.
Analisa atividade Git, presença de docs e TODOs pendentes.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Integrar com o motor
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from engine.shared.shared import get_config, load_json

def run_git_command(repo_path: str, command: list) -> str:
    """Executa um comando git e retorna a saída."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + command,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8'
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""

def get_git_status(repo_path: str) -> dict:
    """Extrai informações do git para o projeto."""
    if not (Path(repo_path) / ".git").exists():
        return {"is_repo": False}
    
    last_commit_date = run_git_command(repo_path, ["log", "-1", "--format=%cI"])
    last_commit_msg = run_git_command(repo_path, ["log", "-1", "--format=%s"])
    branch = run_git_command(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
    modified_files = run_git_command(repo_path, ["status", "--porcelain"])
    
    last_dt = None
    idle_days = 999
    if last_commit_date:
        try:
            last_dt = datetime.fromisoformat(last_commit_date)
            idle_days = (datetime.now().astimezone() - last_dt).days
        except:
            pass
            
    return {
        "is_repo": True,
        "branch": branch,
        "last_commit": last_commit_msg,
        "last_date": last_commit_date,
        "idle_days": idle_days,
        "is_dirty": len(modified_files) > 0
    }

def analyze_docs(project_path: str) -> dict:
    """Verifica saúde da documentação."""
    path = Path(project_path)
    has_readme = (path / "README.md").exists() or (path / "readme.md").exists()
    has_plan = (path / "implementation_plan.md").exists() or (path / "plan.md").exists() or (path / "todo.md").exists()
    
    # Simples contagem de TODOs - Otimizado com os.walk
    todo_count = 0
    ignore_dirs = {".git", "node_modules", "dist", "build", "__pycache__", "venv", ".venv"}
    try:
        for root, dirs, files in os.walk(project_path):
            # Modifica dirs in-place para ignorar pastas pesadas
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file.lower() == "todo.md":
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read().lower()
                            todo_count += content.count("- [ ]") + content.count("todo")
                    except:
                        pass
    except:
        pass
        
    return {
        "has_readme": has_readme,
        "has_plan": has_plan,
        "todo_count": todo_count
    }

def scan_projects() -> dict:
    """Escaneia todos os projetos registrados."""
    config = get_config("projects")
    if not config:
        return {"error": "Configurações de projetos não encontradas."}
        
    results = []
    summary = {
        "total": 0,
        "active_today": 0,
        "idle_warning": 0,
        "doc_missing": 0,
        "total_todos": 0
    }
    
    for p in config.get("projects", []):
        path = p["path"]
        if not os.path.exists(path):
            continue
            
        git = get_git_status(path)
        docs = analyze_docs(path)
        
        project_data = {
            "id": p["id"],
            "name": p["name"],
            "area": p["area"],
            "git": git,
            "docs": docs
        }
        
        results.append(project_data)
        summary["total"] += 1
        summary["total_todos"] += docs["todo_count"]
        
        if git.get("is_repo") and git.get("idle_days", 999) == 0:
            summary["active_today"] += 1
        if git.get("is_repo") and git.get("idle_days", 0) >= config["monitoring"]["idle_days_threshold"]:
            summary["idle_warning"] += 1
        if not docs["has_readme"]:
            summary["doc_missing"] += 1
            
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "projects": results
    }

if __name__ == "__main__":
    data = scan_projects()
    print(json.dumps(data, indent=2, ensure_ascii=False))
