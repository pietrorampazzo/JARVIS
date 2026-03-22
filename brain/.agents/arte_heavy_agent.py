import os
import sys
import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime

# Setup caminhos
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Caminhos absolutos conforme a estrutura do projeto
ARTE_DIR = BASE_DIR / "arte_comercial" / "arte_" / "arte_heavy"
DOWNLOADS_DIR = BASE_DIR / "arte_comercial" / "downloads"
MASTER_FILE = DOWNLOADS_DIR / "master.xlsx"
OUTPUT_FILE = DOWNLOADS_DIR / "master_heavy.xlsx"
HEAVY_SCRIPT = ARTE_DIR / "arte_heavy.py"

def check_pendencies():
    if not MASTER_FILE.exists():
        print(f"❌ Arquivo mestre {MASTER_FILE} não encontrado.")
        return 0
        
    try:
        # Lê o mestre
        df_master = pd.read_excel(MASTER_FILE)
        if df_master.empty:
            return 0
            
        processed_refs = set()
        if OUTPUT_FILE.exists():
            df_existing = pd.read_excel(OUTPUT_FILE)
            if not df_existing.empty and "STATUS" in df_existing.columns:
                # Considera processados itens com STATUS preenchido
                finished_items = df_existing[df_existing["STATUS"].notna() & (df_existing["STATUS"] != "")]
                processed_refs = set(finished_items["REFERENCIA"].astype(str).tolist())
        
        # Itens no mestre que não estão no output (ou sem status)
        to_process = df_master[~df_master["REFERENCIA"].astype(str).isin(processed_refs)]
        return len(to_process)
        
    except Exception as e:
        print(f"❌ Erro ao analisar arquivos Excel: {e}")
        return 0

def run_heavy_matching():
    print(f"🚀 [WATCHER] {datetime.now().strftime('%H:%M:%S')} - Pendências reais detectadas! Iniciando arte_heavy.py...")
    try:
        # Executa o script de matching no diretório correto
        result = subprocess.run([sys.executable, str(HEAVY_SCRIPT)], cwd=str(ARTE_DIR), capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Matching concluído com sucesso.")
        else:
            print(f"⚠ Erro no matching: {result.stderr}")
    except Exception as e:
        print(f"❌ Falha ao executar script: {e}")

if __name__ == "__main__":
    pending_count = check_pendencies()
    print(f"🔍 [WATCHER] Comparando Master vs Heavy: {pending_count} itens pendentes.")
    
    if pending_count > 0:
        run_heavy_matching()
    else:
        print("💤 Pipeline sincronizado. Nada para processar.")
