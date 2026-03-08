"""
COS — Arquivador dia.md v1.0
Script desenhado para rodar às 23:59.
Ele pega o conteúdo do dia.md, salva na pasta histórico e limpa o dia.md para o dia seguinte.
"""

import sys
import shutil
from pathlib import Path
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent.parent
DIA_MD_PATH = BASE_DIR / "dia.md"
HISTORICO_DIR = BASE_DIR / "cos" / "logs" / "historico_dias"

sys.path.insert(0, str(BASE_DIR / "cos" / "engine"))
import gerador_dia

def rotina_meia_noite():
    if not HISTORICO_DIR.exists():
        HISTORICO_DIR.mkdir(parents=True, exist_ok=True)
        
    hoje_iso = date.today().isoformat()
    destino = HISTORICO_DIR / f"dia_{hoje_iso}.md"
    
    # 1. Copia o arquivo atual para o histórico
    if DIA_MD_PATH.exists():
        shutil.copy2(DIA_MD_PATH, destino)
        print(f"✅ Arquivo dia.md arquivado com sucesso em {destino.name}")
    else:
        print("⚠️ Arquivo dia.md não encontrado para arquivamento.")
        
    # 2. Reseta o dia.md para amanhã (apenas formatando o template zerado)
    print("🔄 Resetando template para o próximo dia...")
    
    header = f"""# ☀️ Status do Dia: Amanhã
> **Última atualização:** 00:00 | **Score Atual:** 0/100

## 1) 📌 TASKS EM ABERTO (Global)
> *[Lembrete] Atualize este checklist diariamente com suas pendências manuais.*

## 2) 🏢 PIPELINE DE LICITAÇÕES (Resumo Rápido)
- Aguardando primeira execução do dia...

## 3) 👁️ MONITORAMENTO E INSIGHTS (Gerado por IA)
> *Esta seção é reescrita automaticamente pela Engine JARVIS.*

Sem eventos logados ainda.
"""
    with open(DIA_MD_PATH, "w", encoding="utf-8") as f:
        f.write(header)
        
    print("✅ Rotina de meia-noite concluída.")

if __name__ == "__main__":
    rotina_meia_noite()
