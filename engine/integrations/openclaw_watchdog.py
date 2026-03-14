"""
JARVIS — OpenClaw Watchdog v1.0
Mantém o processo do OpenClaw sempre ativo.
Se o processo cair, ele reinicia automaticamente com backoff exponencial.

Uso:
    python openclaw_watchdog.py                  # Modo silencioso (padrão)
    python openclaw_watchdog.py --verbose        # Mais logs
    python openclaw_watchdog.py --dry-run        # Simula sem subir o processo

Registra logs em: logs/openclaw_watchdog.log
"""

import subprocess
import sys
import time
import logging
import signal
import argparse
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent.parent

# Comando para iniciar o OpenClaw (ajuste se necessário)
OPENCLAW_CMD = ["openclaw", "start"]

# Intervalo de checagem em segundos (a cada 15s verifica se o processo está vivo)
CHECK_INTERVAL_SEC = 15

# Backoff: espera crescente entre reinicializações consecutivas (para evitar loop de crash)
# Sequência: 5s, 10s, 20s, 40s, 60s (máximo)
BACKOFF_INITIAL_SEC = 5
BACKOFF_MAX_SEC = 60

# Número máximo de reinicializações em 10 minutos antes de alertar e reduzir tentativas
MAX_RESTARTS_IN_WINDOW = 5
RESTART_WINDOW_SEC = 600  # 10 minutos

LOG_PATH = BASE_DIR / "logs" / "openclaw_watchdog.log"

# ─────────────────────────────────────────────────────────────────────────────
# SETUP DE LOGGING
# ─────────────────────────────────────────────────────────────────────────────

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Garantir UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WATCHDOG] %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("openclaw_watchdog")

# ─────────────────────────────────────────────────────────────────────────────
# CONTROLE DE SINAL (Ctrl+C gracioso)
# ─────────────────────────────────────────────────────────────────────────────

_shutdown = False
_current_proc = None


def _handle_signal(signum, frame):
    global _shutdown
    log.info(f"Sinal {signum} recebido. Encerrando watchdog graciosamente...")
    _shutdown = True
    if _current_proc and _current_proc.poll() is None:
        log.info("Enviando SIGTERM ao OpenClaw...")
        _current_proc.terminate()


signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────────────────────

def is_openclaw_running_standalone() -> bool:
    """Verifica via tasklist se há algum processo 'openclaw' rodando no sistema."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq openclaw.exe"],
            capture_output=True, text=True
        )
        return "openclaw.exe" in result.stdout.lower()
    except Exception:
        return False


def start_openclaw(dry_run: bool = False):
    """Inicia o OpenClaw em background e retorna o Popen."""
    log.info(f"🚀 Iniciando OpenClaw: {' '.join(OPENCLAW_CMD)}")
    if dry_run:
        log.info("[DRY-RUN] Simulando inicialização — nenhum processo real criado.")
        return None
    try:
        proc = subprocess.Popen(
            OPENCLAW_CMD,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        log.info(f"✅ OpenClaw iniciado com PID {proc.pid}")
        return proc
    except FileNotFoundError:
        log.error("❌ Comando 'openclaw' não encontrado. Verifique se está no PATH.")
        return None
    except Exception as e:
        log.error(f"❌ Erro ao iniciar OpenClaw: {e}")
        return None


def notify_jarvis(message: str):
    """Registra uma mensagem de alerta via o notifier do JARVIS (best-effort)."""
    try:
        notifier_path = BASE_DIR / "engine" / "shared" / "openclaw_notifier.py"
        if notifier_path.exists():
            subprocess.run(
                ["python", str(notifier_path), message],
                timeout=5, capture_output=True
            )
    except Exception:
        pass  # Silencia — o watchdog não pode depender do notifier para funcionar


# ─────────────────────────────────────────────────────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def run_watchdog(dry_run: bool = False, verbose: bool = False):
    global _current_proc, _shutdown

    if verbose:
        log.setLevel(logging.DEBUG)

    log.info("=" * 60)
    log.info("  JARVIS — OpenClaw Watchdog INICIADO")
    log.info(f"  Check interval : {CHECK_INTERVAL_SEC}s")
    log.info(f"  Backoff inicial: {BACKOFF_INITIAL_SEC}s (máx. {BACKOFF_MAX_SEC}s)")
    log.info(f"  Log: {LOG_PATH}")
    log.info("=" * 60)

    restart_times = []          # timestamps das últimas reinicializações
    consecutive_restarts = 0    # para cálculo do backoff
    backoff = BACKOFF_INITIAL_SEC

    # Inicia o processo pela primeira vez
    _current_proc = start_openclaw(dry_run)

    while not _shutdown:
        time.sleep(CHECK_INTERVAL_SEC)

        if _shutdown:
            break

        # Verifica se o processo ainda está vivo
        proc_alive = False
        if _current_proc is not None:
            if _current_proc.poll() is None:
                proc_alive = True  # processo ainda rodando
                consecutive_restarts = 0
                backoff = BACKOFF_INITIAL_SEC
                if verbose:
                    log.debug(f"💚 OpenClaw ativo (PID {_current_proc.pid})")
            else:
                exit_code = _current_proc.returncode
                log.warning(f"⚠️  OpenClaw encerrou inesperadamente. Exit code: {exit_code}")
        elif not dry_run:
            # Processo nunca foi criado (erro de PATH etc.)
            log.warning("⚠️  Processo inexistente. Verificando se está rodando globalmente...")
            if is_openclaw_running_standalone():
                log.info("✅ OpenClaw detectado via tasklist — monitorando externamente.")
                proc_alive = True

        if not proc_alive and not dry_run:
            # Limpar lista de reinicializações antigas (fora da janela de 10min)
            now = time.time()
            restart_times = [t for t in restart_times if now - t < RESTART_WINDOW_SEC]

            if len(restart_times) >= MAX_RESTARTS_IN_WINDOW:
                log.error(
                    f"🚨 OpenClaw reiniciou {MAX_RESTARTS_IN_WINDOW}x em {RESTART_WINDOW_SEC//60} minutos. "
                    f"Possível loop de crash. Aguardando {backoff}s antes de tentar novamente..."
                )
                notify_jarvis(
                    f"🚨 [JARVIS WATCHDOG] OpenClaw entrou em loop de crash ({MAX_RESTARTS_IN_WINDOW} reinicializações "
                    f"em {RESTART_WINDOW_SEC//60} min). Intervenção manual pode ser necessária."
                )
            else:
                log.info(f"⏳ Aguardando {backoff}s antes de reiniciar...")

            time.sleep(backoff)

            if _shutdown:
                break

            log.info(f"🔄 Reiniciando OpenClaw (tentativa #{consecutive_restarts + 1})...")
            _current_proc = start_openclaw(dry_run)
            restart_times.append(time.time())
            consecutive_restarts += 1

            # Backoff exponencial com teto
            backoff = min(backoff * 2, BACKOFF_MAX_SEC)

    log.info("🛑 Watchdog encerrado.")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JARVIS — OpenClaw Watchdog")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem iniciar processo real")
    parser.add_argument("--verbose", action="store_true", help="Log detalhado")
    args = parser.parse_args()

    run_watchdog(dry_run=args.dry_run, verbose=args.verbose)
