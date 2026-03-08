"""
JARVIS Daemon v1.0 — O Coração Eterno
Script de monitoramento contínuo que roda 24/7.

Ciclo de Operação:
  08:00 — 04:00: Pulse horário (task_sync + dia.md + score)
  04:00:          Oracle EOD (Upload dia.md + Consulta Oráculo)
  04:01 — 07:59: Modo Sleep (sem pulse, sistema descansando)

Executar:
  python jarvis_daemon.py          → Roda o daemon em loop
  python jarvis_daemon.py --once   → Roda um único ciclo e sai
"""

import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# Ajuste de encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent  # cos/
sys.path.insert(0, str(BASE_DIR / "engine"))
sys.path.insert(0, str(BASE_DIR / "briefings"))

# ══════════════════════════════════════════════
# JANELA DE OPERAÇÃO
# ══════════════════════════════════════════════
HOUR_START = 8     # Início do ciclo diário
HOUR_END = 4       # Fim do ciclo (madrugada seguinte)
HOUR_ORACLE = 4    # Hora exata do ritual do Oráculo
PULSE_INTERVAL_MINUTES = 60  # Intervalo entre pulses


def is_operating_hours(hour: int) -> bool:
    """Verifica se estamos dentro da janela de operação (08:00 até 04:00)."""
    if HOUR_START <= HOUR_END:
        return HOUR_START <= hour < HOUR_END
    else:
        # Janela que cruza a meia-noite (ex: 08 até 04)
        return hour >= HOUR_START or hour < HOUR_END


def minutes_until_next_window() -> int:
    """Calcula quantos minutos restam até o próximo horário de início."""
    now = datetime.now()
    next_start = now.replace(hour=HOUR_START, minute=0, second=0, microsecond=0)
    if now >= next_start:
        next_start += timedelta(days=1)
    delta = (next_start - now).total_seconds() / 60
    return int(delta)


def run_pulse_cycle():
    """Executa um ciclo completo do Pulse: sync + dia.md + score."""
    now = datetime.now()
    hour = now.hour

    print("\n" + "█" * 64)
    print(f"  ⚡ JARVIS DAEMON PULSE — {now.strftime('%d/%m/%Y %H:%M')}")
    print("█" * 64)

    try:
        # 1. Task Sync Bidirecional
        import task_sync
        print("\n  🔄 [1/3] Sincronizando Tasks entre projetos...")
        results = task_sync.run_full_sync()
        total = sum(r["changes_a"] + r["changes_b"] for r in results.values()) if isinstance(results, dict) and "status" not in results else 0
        if total > 0:
            print(f"       → {total} task(s) sincronizada(s).")
        else:
            print("       → Tudo sincronizado.")

        # 2. Pulse Report (Score + Governança + Gap)
        from score_engine import calculate_daily_score
        from governance_rules import evaluate_governance
        score_data = calculate_daily_score()
        gov_data = evaluate_governance()

        classification = score_data['classification']
        emoji = score_data['emoji']
        global_score = score_data['global_score']

        print(f"\n  📊 [2/3] STATUS: {global_score:.0f}/100 ({emoji} {classification})")

        # Gap
        gaps = score_data.get("gaps", {})
        if gaps:
            if "good" in gaps:
                print(f"       → Faltam {gaps['good']['missing']:.1f} pts para [{gaps['good']['label']}]")
            if "excellent" in gaps:
                print(f"       → Faltam {gaps['excellent']['missing']:.1f} pts para [{gaps['excellent']['label']}]")
        else:
            print("       → 🏆 Patamar Excelente atingido!")

        # Governança
        interventions = gov_data.get("interventions", [])
        if interventions:
            criticals = [i for i in interventions if i['priority'] == 'CRITICAL']
            if criticals:
                print(f"\n  ⚠️  ALERTAS CRÍTICOS: {len(criticals)}")
                for c in criticals[:2]:
                    print(f"       → {c['message'][:80]}...")

        # 3. Gerar dia.md
        print(f"\n  📝 [3/5] Gerando dia.md...")
        import gerador_dia
        gerador_dia.build_dia_md()

        # 4. ARTE Edital Quality Check
        print(f"\n  📄 [4/5] Verificando qualidade do pipeline Edital...")
        try:
            ARTE_DIR = BASE_DIR.parent.parent / "arte_"
            edital_logger_path = ARTE_DIR / "arte_edital" / "edital_quality_logger.py"
            if edital_logger_path.exists():
                sys.path.insert(0, str(ARTE_DIR / "arte_edital"))
                import edital_quality_logger
                eq_report = edital_quality_logger.quick_status()
                print(f"       → Editais: {eq_report.get('total_editais', '?')} | "
                      f"Itens: {eq_report.get('total_itens', '?')} | "
                      f"Taxa TR: {eq_report.get('taxa_tr', '?')}%")
            else:
                print("       → Logger não encontrado, pulando.")
        except Exception as e:
            print(f"       → Erro no quality check: {e}")

        # 5. ARTE Heavy Performance Metrics
        print(f"\n  🎯 [5/5] Métricas do Matching (arte_heavy)...")
        try:
            ARTE_DIR = BASE_DIR.parent.parent / "arte_"
            sys.path.insert(0, str(ARTE_DIR / "arte_heavy"))
            import arte_perf_tracker
            sessions = arte_perf_tracker.parse_log()
            if sessions:
                last = sessions[-1]
                total_queries = sum(s["total"] for s in sessions)
                total_false = sum(s["false_negatives"] for s in sessions)
                rate_flag = "🚨" if last["rate_limited"] > 0 else "✅"
                print(f"       → Última sessão: {last['start_time']} | "
                      f"ATENDE: {last['atende_rate']:.0f}% | "
                      f"Rate-Limited: {last['rate_limited']} {rate_flag}")
                print(f"       → Global: {total_queries} queries | "
                      f"Falsos negativos: {total_false}")
                arte_perf_tracker.save_metrics(sessions)
            else:
                print("       → Sem sessões no log.")
        except Exception as e:
            print(f"       → Erro nas métricas: {e}")

    except Exception as e:
        print(f"\n  ❌ ERRO NO PULSE: {e}")
        traceback.print_exc()

    print("\n" + "█" * 64)


def run_oracle_ritual():
    """Executa o ritual noturno do Oráculo: Upload + Consulta."""
    now = datetime.now()

    print("\n" + "═" * 64)
    print(f"  🧠 RITUAL DO ORÁCULO — {now.strftime('%d/%m/%Y %H:%M')}")
    print("═" * 64)

    try:
        import oracle_sync

        # 1. Upload do dia.md consolidado
        print("\n  📡 [1/2] Enviando relatório do dia para o Oráculo...")
        oracle_sync.upload_eod_report()

        # 2. Consulta de orientação
        time.sleep(3)  # Espera indexação
        print("\n  🔮 [2/2] Pedindo orientação ao Oráculo...")
        resposta = oracle_sync.ask_oracle()

        print("\n" + "─" * 64)
        print("  📜 RESPOSTA DO ORÁCULO:")
        print("─" * 64)
        print(resposta)
        print("─" * 64)

        # Salva a resposta localmente para referência
        oracle_log_dir = Path(__file__).parent.parent.parent / "cos" / "oracle_logs"
        oracle_log_dir.mkdir(parents=True, exist_ok=True)
        log_file = oracle_log_dir / f"oracle_{now.strftime('%Y_%m_%d')}.md"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"# 🔮 Resposta do Oráculo — {now.strftime('%d/%m/%Y %H:%M')}\n\n")
            f.write(resposta)
        print(f"\n  💾 Resposta salva em: {log_file}")

    except Exception as e:
        print(f"\n  ❌ ERRO NO RITUAL DO ORÁCULO: {e}")
        traceback.print_exc()

    print("═" * 64)


def daemon_loop():
    """Loop principal do daemon. Roda eternamente."""
    print("╔" + "═" * 62 + "╗")
    print("║   🤖 JARVIS DAEMON v1.0 — O Coração Eterno               ║")
    print("║   Operação: 08:00 — 04:00 | Oracle: 04:00 | Sleep: 04-08 ║")
    print("╚" + "═" * 62 + "╝")

    last_pulse_hour = -1
    oracle_done_today = False

    while True:
        now = datetime.now()
        hour = now.hour

        # Reset do flag do Oráculo à meia-noite
        if hour == 0:
            oracle_done_today = False

        # Janela de operação?
        if is_operating_hours(hour):
            # Só roda se mudou de hora (evita duplicatas)
            if hour != last_pulse_hour:
                run_pulse_cycle()
                last_pulse_hour = hour

        # Hora do Oráculo?
        elif hour == HOUR_ORACLE and not oracle_done_today:
            # Último pulse do dia antes do ritual
            if last_pulse_hour != hour:
                run_pulse_cycle()
                last_pulse_hour = hour

            run_oracle_ritual()
            oracle_done_today = True

        else:
            # Modo Sleep
            if hour == HOUR_ORACLE + 1 and last_pulse_hour != -99:
                sleep_mins = minutes_until_next_window()
                print(f"\n  😴 JARVIS dormindo. Próximo pulse em ~{sleep_mins} minutos ({HOUR_START}:00).")
                last_pulse_hour = -99  # Flag para não repetir

        # Dorme 1 minuto entre verificações
        time.sleep(60)


def run_once():
    """Roda um único ciclo: pulse + oracle se for a hora certa."""
    now = datetime.now()
    hour = now.hour

    run_pulse_cycle()

    if hour == HOUR_ORACLE:
        run_oracle_ritual()

    print(f"\n✅ Ciclo único concluído às {now.strftime('%H:%M')}.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="JARVIS Daemon — O Coração Eterno")
    parser.add_argument("--once", action="store_true", help="Roda um único ciclo e sai")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        try:
            daemon_loop()
        except KeyboardInterrupt:
            print("\n\n🛑 JARVIS Daemon encerrado pelo operador. Até logo, Capitão.")
