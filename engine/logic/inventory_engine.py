"""
COS — Inventory Engine v1.0
Monitora pastas de propostas no Google Drive e gera snapshots para o Score Engine.
"""

import json
import sys
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List

# Setup caminhos
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

CONFIG_DIR = BASE_DIR / "engine" / "config"
INVENTORY_DIR = BASE_DIR / "engine" / "integrations" / "inventory"

# Pastas alvo (Google Drive e Local)
TARGET_PATHS = {
    "ARTE_DRIVE": Path(r"I:\Meu Drive\arte_comercial\PROPOSTAS"),
    "PIEZZO_DRIVE": Path(r"I:\Meu Drive\PIEZZO\PPROPOSTAS"),
    "LOCAL_EDITAIS": Path(r"C:\Users\pietr\OneDrive\Área de Trabalho\ARTE\01_EDITAIS"),
    "LOCAL_DOWNLOADS": Path(r"c:\Users\pietr\OneDrive\.vscode\arte_\DOWNLOADS")
}

def get_folder_inventory(path: Path) -> List[Dict]:
    """Escaneia a pasta e retorna lista de arquivos com metadados."""
    if not path.exists():
        print(f"⚠️ Pasta não encontrada: {path}")
        return []
    
    inventory = []
    # Escaneia apenas arquivos na raiz da pasta de propostas (ou recursivo se desejar)
    for item in path.glob("**/*"):
        if item.is_file():
            stats = item.stat()
            inventory.append({
                "name": item.name,
                "path": str(item),
                "size": stats.st_size,
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stats.st_ctime).isoformat()
            })
    return inventory

def run_inventory() -> Dict:
    """Executa o inventário completo e retorna o snapshot."""
    print("  🔄 Escaneando pastas de propostas...")
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "date": date.today().isoformat(),
        "sources": {}
    }
    
    total_files = 0
    for name, path in TARGET_PATHS.items():
        files = get_folder_inventory(path)
        snapshot["sources"][name] = {
            "path": str(path),
            "count": len(files),
            "files": files
        }
        total_files += len(files)
        print(f"    ✅ {name}: {len(files)} arquivos encontrados.")
        
    snapshot["total_count"] = total_files
    return snapshot

def save_snapshot(snapshot: Dict) -> Path:
    """Salva o snapshot em JSON."""
    INVENTORY_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"propostas_{date.today().isoformat()}.json"
    out_path = INVENTORY_DIR / filename
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    return out_path

def find_previous_snapshot() -> Path:
    """Busca o snapshot do dia anterior (ou o mais recente disponível)."""
    if not INVENTORY_DIR.exists():
        return None
    
    snapshots = sorted(list(INVENTORY_DIR.glob("propostas_*.json")), reverse=True)
    # Pegamos o segundo mais recente (o primeiro é o que acabamos de criar)
    if len(snapshots) > 1:
        return snapshots[1]
    return None

def calculate_delta(current: Dict, previous: Dict) -> Dict:
    """Calcula a diferença entre dois snapshots."""
    delta = {
        "new_files": [],
        "removed_files": [],
        "new_count": 0
    }
    
    if not previous:
        return delta
    
    curr_files = set()
    for source in current["sources"].values():
        for f in source["files"]:
            curr_files.add(f["name"])
            
    prev_files = set()
    for source in previous["sources"].values():
        for f in source["files"]:
            prev_files.add(f["name"])
    
    delta["new_files"] = list(curr_files - prev_files)
    delta["removed_files"] = list(prev_files - curr_files)
    delta["new_count"] = len(delta["new_files"])
    
    return delta

def main():
    snapshot = run_inventory()
    save_snapshot(snapshot)
    
    prev_path = find_previous_snapshot()
    if prev_path:
        with open(prev_path, "r", encoding="utf-8") as f:
            previous = json.load(f)
        delta = calculate_delta(snapshot, previous)
        print(f"  📊 Delta: {delta['new_count']} novas propostas detectadas.")
    else:
        print("  ℹ️ Primeiro snapshot do inventário. Delta será calculado na próxima execução.")

if __name__ == "__main__":
    main()
