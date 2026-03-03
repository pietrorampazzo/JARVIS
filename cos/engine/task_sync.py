"""
🤖 JARVIS TASK SYNC — Sincronizador de Tasks do Ecossistema

Este script lê o projects.json, localiza os manifestos de cada projeto
e consolida a visão tática (tasks pendentes/concluídas) no JARVIS.
"""

import sys
import io

# Fix para Windows Encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import os
from pathlib import Path
from datetime import datetime

# Paths JARVIS
JARVIS_ROOT = Path("c:/Users/pietr/OneDrive/.vscode/JARVIS")
PROJECTS_JSON = JARVIS_ROOT / "cos" / "config" / "projects.json"


def load_projects():
    if PROJECTS_JSON.exists():
        with open(PROJECTS_JSON, "r", encoding="utf-8") as f:
            return json.load(f).get("projects", [])
    return []


def extract_tasks_from_todo(todo_path):
    tasks = {"pending": [], "done": []}
    if os.path.exists(todo_path):
        try:
            with open(todo_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("- [ ]"):
                        tasks["pending"].append(line.replace("- [ ]", "").strip())
                    elif line.startswith("- [x]"):
                        tasks["done"].append(line.replace("- [x]", "").strip())
        except Exception as e:
            print(f"Error reading {todo_path}: {e}")
    return tasks


def run_sync():
    print(f"--- JARVIS Task Sync ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---\n")
    projects = load_projects()
    
    summary = {}

    for proj in projects:
        proj_id = proj.get("id")
        proj_path = Path(proj.get("path", ""))
        todo_rel = proj.get("observe", {}).get("todo_file")
        
        if not todo_rel or not proj_id:
            continue
            
        todo_full = proj_path / todo_rel
        
        if todo_full.exists():
            print(f"Sincronizando: {proj_id}...")
            tasks = extract_tasks_from_todo(todo_full)
            summary[proj_id] = tasks
            
            print(f"   Done: {len(tasks['done'])}")
            print(f"   Pending: {len(tasks['pending'])}")
            for t in tasks["pending"]:
                print(f"      - {t}")
        else:
            # print(f"Manifesto não encontrado para {proj_id}")
            pass

    print("\n--- Sincronização Concluída ---")
    return summary


if __name__ == "__main__":
    run_sync()
