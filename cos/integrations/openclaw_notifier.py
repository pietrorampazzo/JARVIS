"""
JARVIS -> OPENCLAW NOTIFIER
Ponte de comunicação para que o JARVIS (Back-End) consiga despachar mensagens proativas
para o usuário através do OpenClaw (Front-End Conversacional).
"""

import subprocess
import logging
import sys

def send_notification(message: str, priority: str = "normal"):
    """
    Despacha uma mensagem via CLI do OpenClaw.
    O OpenClaw, rodando na LenovoPeti, entregará a mensagem pelo último canal ativo (WhatsApp/Telegram).
    """
    logging.info(f"Enviando notificação pró-ativa (Prioridade: {priority})...")
    
    # Prepara o comando
    # O OpenClaw usa: openclaw message send --message "Texto"
    cmd = ["openclaw", "message", "send", "--message", message]
    
    # Se for alta prioridade, podemos querer formatar com emojis ou prefixos
    if priority == "high":
        cmd[4] = f"🚨 *[JARVIS CRITICAL]* 🚨\n{message}"
    elif priority == "briefing":
        cmd[4] = f"📊 *[JARVIS BRIEFING]*\n{message}"
        
    try:
        # Executa em background para não travar o daemon
        # No Windows, shell=True permite achar binários globais facilmente
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            logging.info("✅ Notificação enviada ao OpenClaw com sucesso.")
            return True
        else:
            logging.error(f"❌ Falha ao notificar via OpenClaw: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Erro ao invocar CLI OpenClaw: {str(e)}")
        return False

if __name__ == "__main__":
    # Teste simples CLI
    if len(sys.argv) > 1:
        send_notification(" ".join(sys.argv[1:]), "normal")
    else:
        print("Uso: python openclaw_notifier.py 'Mensagem de teste'")
