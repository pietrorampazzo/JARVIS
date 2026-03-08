"""
JARVIS Pulse v1.0 (Hourly Touchpoint)
Substitui os antigos briefings (morning, midday, eod) por um pulso horário unificado.
Gera o flash update na tela, reescreve o dia.md e exibe a Calculadora de Gap para atingimento de metas.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Ajuste de encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent.parent # JARVIS/
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "cos" / "engine")) # Para scripts locais que não usam pacotes

from cos.engine.score_engine import calculate_daily_score
from cos.engine.governance_rules import evaluate_governance
from cos.engine.predictive_engine import get_predictive_alerts
from cos.engine import gerador_dia
from cos.engine import oracle_sync
from cos.engine import task_sync


def print_score_gap(gaps: dict):
    if not gaps:
        print("  🏆 Você já atingiu o patamar de Dia Excelente! Mantenha a barra alta.")
        return

    print("\n  🎯 CALCULADORA DE GAP:")
    
    if "good" in gaps:
        good = gaps["good"]
        print(f"  → Faltam {good['missing']:.1f} pontos para um [{good['label']}] ({good['target']}).")
        print("    Dica: 1 tarefa de Impacto 5 em Output Econômico rende ~20 a 25 pontos líquidos.")
        
    if "excellent" in gaps:
        exc = gaps["excellent"]
        print(f"  → Faltam {exc['missing']:.1f} pontos para um [{exc['label']}] ({exc['target']}).")
        print("    Dica: Deep Work constante (duração alta + impacto) + fechamento de ciclos.")


def print_pulse_report():
    now = datetime.now()
    hour = now.hour
    
    # Executar as engines
    score_data = calculate_daily_score()
    gov_data = evaluate_governance()
    
    is_morning = (hour >= 7 and hour < 10)
    is_eod = (hour >= 18)

    print("=" * 64)
    if is_morning:
        print(f"  🌅 MORNING DIRECTIVE — {now.strftime('%d/%m/%Y %H:%M')}")
    elif is_eod:
        print(f"  🌙 END-OF-DAY AUDIT — {now.strftime('%d/%m/%Y %H:%M')}")
    else:
        print(f"  ⚡ HOURLY PULSE — {now.strftime('%d/%m/%Y %H:%M')}")
    print("=" * 64)
    
    classification = score_data['classification']
    emoji = score_data['emoji']
    global_score = score_data['global_score']
    
    print(f"\n  📊 STATUS ATUAL: {global_score}/100 ({emoji} {classification})")
    
    # Gap Calculator
    print_score_gap(score_data.get("gaps", {}))
    
    print(f"\n  ⚖️  GOVERNANÇA (Pulse-check):")
    interventions = gov_data.get("interventions", [])
    if interventions:
        for iv in interventions:
            print(f"  [{iv['priority']}] {iv['message']}")
    else:
        print("  ✅ Nenhuma intervenção ativa. Caminho livre.")
        
    if gov_data.get("actions"):
        print("\n  📋 DIREÇÃO IMEDIATA:")
        for action in gov_data["actions"]:
            print(f"  • {action}")
            
    if is_morning:
        alerts = get_predictive_alerts(3)
        critical_alerts = [a for a in alerts if a["priority"] in ["critical", "high"]]
        if critical_alerts:
            print("\n  🔮 ALERTAS PREDITIVOS PARA HOJE:")
            for a in critical_alerts[:2]:
                print(f"  → {a['message']}")

    print("\n" + "=" * 64)
    
    # Sync bidirecional de TODOs antes de gerar o dia.md
    print("  🔄 Sincronizando Tasks entre projetos (Bidirecional)...")
    task_sync.run_full_sync()
    
    # Atualiza o Frontend Markdown e o Gemini Insight
    print("  🔄 Sincronizando Inteligência e gerando dia.md...")
    gerador_dia.build_dia_md()
    
    if hour == 4:
        print("\n" + "=" * 64)
        print("  🧠 INICIANDO RITUAL DE ORQUESTRAÇÃO ESTRATÉGICA (ORÁCULO)")
        print("=" * 64)
        oracle_sync.upload_eod_report()

    print("=" * 64 + "\n")


if __name__ == "__main__":
    print_pulse_report()
