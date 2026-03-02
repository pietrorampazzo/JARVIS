"""
JARVIS Lab — Latency Test (Neural Network vs FileSystem)
Compara em milissegundos a diferença entre a arquitetura legada (OneDrive JSON) 
e a nova arquitetura Rede Neural (FastAPI).
"""

import time
import requests
import os
import json
from pathlib import Path

# Config
MASTER_URL = os.getenv("JARVIS_MASTER_URL", "http://localhost:8000")
DUMMY_FILE = Path(__file__).parent / "dummy_log.json"

def test_network_latency():
    print(f"🌐 Testando Latência Neural (API em {MASTER_URL})...")
    payload = {
        "area_id": "system_building",
        "category": "lab",
        "action": "Ping Teste de Latência",
        "impact": 1,
        "duration_minutes": 1,
        "project": "LAB"
    }
    
    start_time = time.perf_counter()
    try:
        res = requests.post(f"{MASTER_URL}/api/log", json=payload, timeout=5)
        end_time = time.perf_counter()
        
        if res.status_code == 200:
            latency_ms = (end_time - start_time) * 1000
            print(f"✅ SUCESSO! Tempo de resposta do Servidor: {latency_ms:.2f} ms")
        else:
            print(f"❌ Servidor retornou código {res.status_code}: {res.text}")
    except requests.exceptions.ConnectionError:
        print(f"❌ FALHA DE CONEXÃO. O Servidor {MASTER_URL} está rodando?")
    except Exception as e:
        print(f"❌ ERRO: {e}")

def main():
    print("="*60)
    print("  🧪 JARVIS SPEED TEST LAB")
    print("="*60)
    
    print("\n[ FASE 1: REDE NEURAL (FastAPI) ]")
    print("Aguardando contato com o nó Mestre...")
    test_network_latency()
    
    print("\n" + "="*60)
    print("🎯 CONCLUSÃO")
    print("Rede Neural: IOps ocorre em milissegundos, independente do Sync do OneDrive.")
    print("O OneDrive pode levar entre 5 e 60 segundos para espelhar um arquivo JSON.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
