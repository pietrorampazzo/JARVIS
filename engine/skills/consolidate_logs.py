import sys
import json
import os
from pathlib import Path
from datetime import date

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Caminhos
BASE_DIR = Path(__file__).parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
MASTER_FILE = LOGS_DIR / "events_master.json"

all_events = []

# Carrega eventos existentes se houver
if MASTER_FILE.exists():
    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        try:
            all_events = json.load(f)
        except:
            pass

# Lista arquivos de data
for f in sorted(LOGS_DIR.glob("????-??-??.json")):
    print(f"🔄 Lendo {f.name}...")
    with open(f, "r", encoding="utf-8") as file:
        try:
            events = json.load(file)
            # Evita duplicidade se já houver algo no master
            for ev in events:
                if ev not in all_events:
                    all_events.append(ev)
        except Exception as e:
            print(f"❌ Erro ao ler {f.name}: {e}")

# Salva no Master
with open(MASTER_FILE, "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)

print(f"✅ Sincronização concluída! {len(all_events)} eventos totais no {MASTER_FILE.name}")

# Não vamos deletar os antigos ainda por segurança, o usuário pode fazer isso depois.
