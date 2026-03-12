import subprocess
import sys
from pathlib import Path

def query_oracle():
    """Consulta o NotebookLM (Oráculo) para obter um insight profético."""
    print("🔮 [ORACLE] Consultando a sabedoria do NoteBookLM...")
    
    skill_path = Path(r"C:\Users\pietr\.antigravity\skills\notebooklm")
    python_exe = skill_path / ".venv" / "Scripts" / "python.exe"
    script_path = skill_path / "scripts" / "ask_question.py"
    
    notebook_url = "https://notebooklm.google.com/notebook/e23ea047-7f1e-4c93-b6d2-f3dd6b912104"
    
    question = (
        "Aja como o Oráculo do JARVIS. Baseado nos logs, snapshots e estratégias de JARVIS, ARTE e WAPPI das últimas horas, "
        "forneça um insight profético de uma frase (estilo místico com o emoji de coruja) e um resumo técnico de 3 pontos "
        "relevantes sobre o estado atual do ecossistema. Foque no progresso real e gargalos."
    )

    try:
        import os
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        cmd = [
            str(python_exe),
            str(script_path),
            "--question", question,
            "--notebook-url", notebook_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', env=env)
        
        if result.returncode == 0:
            output = result.stdout
            # Tenta extrair a parte entre os delimitadores de '=' se existirem
            if "============================================================" in output:
                parts = output.split("============================================================")
                answer = parts[1].strip() if len(parts) > 1 else output
            else:
                answer = output
            
            # Remove o lembrete de follow-up que o script anexa
            answer = answer.split("EXTREMELY IMPORTANT: Is that ALL you need to know?")[0].strip()
            return answer
        else:
            print(f"❌ [ORACLE] Falha na consulta: {result.stderr}")
            return "O Oráculo está em silêncio no momento. A névoa ainda não se dissipou."
            
    except Exception as e:
        print(f"❌ [ORACLE] Erro inesperado: {e}")
        return "O Oráculo está em silêncio no momento. A névoa ainda não se dissipou."

if __name__ == "__main__":
    print(query_oracle())
