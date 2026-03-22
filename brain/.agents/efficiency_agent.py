"""
JARVIS Efficiency Agent v1.0
Auditoria automatizada de workspace para detecção de obsolescência.
- Pastas órfãs (não registradas no projects.json).
- Projetos inativos (sem commits há >30 dias).
- Scripts órfãos (arquivos .py sem importações).
"""

import sys
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime, timedelta

# Setup caminhos
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from engine.shared.shared import get_config, load_json, EXECUTIVE_LOG_PATH
except ImportError:
    # Fallback se rodar isolado
    def get_config(name): return {}
    def load_json(p): return {}
    EXECUTIVE_LOG_PATH = None

# Lista de arquivos/pastas que NUNCA devem ser marcados como obsoletos
EFFICIENCY_IGNORE = {
    "scripts": [
        "notebooklm_client.py",
        "board_manager.py",
        "consolidate_logs.py"
    ],
    "folders": [
        "global_window",
        "whatsapp",
        ".git",
        ".vscode"
    ]
}

def check_dangling_folders():
    print("🔍 [EFFICIENCY] Verificando pastas órfãs no root...")
    workspace_root = Path("c:/Users/pietr/OneDrive/.vscode")
    projects_config = get_config("projects")
    registered_paths = [Path(p["path"]).resolve() for p in projects_config.get("projects", [])]
    
    dangling = []
    if workspace_root.exists():
        for item in workspace_root.iterdir():
            if item.is_dir() and item.name not in ["JARVIS", ".git", "node_modules", ".venv", "venv"] + EFFICIENCY_IGNORE["folders"]:
                if item.resolve() not in registered_paths:
                    dangling.append(item.name)
    return dangling

def check_project_activity():
    print("🔍 [EFFICIENCY] Auditando atividade dos projetos...")
    projects = get_config("projects").get("projects", [])
    inactives = []
    
    for p in projects:
        p_path = Path(p["path"])
        if not p_path.exists():
            inactives.append(f"{p['name']} (Caminho inconsistente)")
            continue
            
        try:
            # Pega data do último commit em segundos (unix timestamp)
            last_ts = subprocess.check_output(
                ["git", "-C", str(p_path), "log", "-1", "--format=%ct"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            
            last_date = datetime.fromtimestamp(int(last_ts))
            weeks_ago = (datetime.now() - last_date).days // 7
            
            if weeks_ago >= 4:
                inactives.append(f"{p['name']} (Inativo há {weeks_ago} semanas)")
        except:
            # Sem Git ou erro
            pass
            
    return inactives

def check_orphan_scripts():
    print("🔍 [EFFICIENCY] Procurando scripts órfãos na Engine...")
    engine_path = BASE_DIR / "engine"
    all_py_files = list(engine_path.rglob("*.py"))
    
    # Scripts candidatos (ignora inits e o próprio agente)
    scripts = [f for f in all_py_files if f.name != "__init__.py" and f.name != "efficiency_agent.py" and f.name not in EFFICIENCY_IGNORE["scripts"]]
    orphans = []
    
    for script in scripts:
        module_name = script.stem
        found = False
        
        # Busca simples: nome do módulo em outros arquivos
        for other_script in all_py_files:
            if other_script == script: continue
            try:
                with open(other_script, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if f"import {module_name}" in content or f"from . import {module_name}" in content or f"from engine" in content and module_name in content:
                        found = True
                        break
            except:
                pass
        
        # Verifica também o jarvis_pulse.py
        if not found:
            pulse_path = engine_path / "monitoring" / "jarvis_pulse.py"
            if pulse_path.exists():
                with open(pulse_path, "r", encoding="utf-8", errors="ignore") as f:
                    if module_name in f.read():
                        found = True
                        
        if not found:
            orphans.append(str(script.relative_to(engine_path)))
            
    return orphans

def run_audit():
    print(f"\n🚀 [EFFICIENCY AGENT] Relatório de Saúde do Workspace — {datetime.now().strftime('%d/%m/%Y')}")
    print("="*60)
    
    # 1. Pastas Órfãs
    dangling = check_dangling_folders()
    print("\n📦 PASTAS ÓRFÃS (Não registradas no projects.json):")
    if dangling:
        for d in dangling: print(f"  ⚠ {d}")
    else:
        print("  ✅ Nenhuma pasta órfã detectada.")
        
    # 2. Inatividade
    inactives = check_project_activity()
    print("\n💤 PROJETOS INATIVOS (> 30 dias):")
    if inactives:
        for i in inactives: print(f"  ⚠ {i}")
    else:
        print("  ✅ Todo o ecossistema está pulsando.")
        
    # 3. Scripts Órfãos
    orphans = check_orphan_scripts()
    print("\n📄 SCRIPTS ÓRFÃOS (Sem referências de importação):")
    if orphans:
        for o in orphans: print(f"  ⚠ {o}")
    else:
        print("  ✅ Todos os scripts da Engine parecem integrados.")
    
    print("\n" + "="*60)
    print("🏁 [EFFICIENCY] Auditoria Concluída.\n")

if __name__ == "__main__":
    run_audit()
