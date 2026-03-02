"""
COS — Event Logger v1.0
Sistema de registro de eventos da vida (append-only).
Uso: python event_logger.py --area economic_output --category licitacao --action edital_analisado --impact 4 --duration 30
"""

import json
import argparse
from datetime import datetime, date
from pathlib import Path
import sys
import os
import requests

sys.stdout.reconfigure(encoding='utf-8')

# Diretório raiz do COS
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"


def load_areas() -> dict:
    """Carrega áreas válidas do config."""
    with open(CONFIG_DIR / "areas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return {a["id"]: a for a in data["areas"]}


def get_log_path(log_date: date = None) -> Path:
    """Retorna o caminho do arquivo de log do dia."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    d = log_date or date.today()
    return LOGS_DIR / f"{d.isoformat()}.json"


def load_today_log() -> list:
    """Carrega os eventos do dia atual."""
    log_path = get_log_path()
    if log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(events: list, log_date: date = None) -> None:
    """Salva o log do dia (append-only via substituição completa)."""
    log_path = get_log_path(log_date)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)


def log_event(
    area: str,
    category: str,
    action: str,
    impact: int,
    duration_minutes: int = 0,
    source: str = "manual",
    notes: str = "",
    project: str = ""
) -> dict:
    """
    Registra um evento no log do dia.
    
    Args:
        area: ID da área (ex: 'economic_output')
        category: Categoria da ação (ex: 'licitacao', 'dev', 'saude')
        action: Descrição da ação realizada
        impact: Impacto de 1 a 5
        duration_minutes: Tempo gasto em minutos
        source: Fonte do log ('manual', 'trello', 'git', 'script')
        notes: Observações adicionais
        project: Nome do projeto relacionado

    Returns:
        dict com o evento registrado
    """
    areas = load_areas()
    if area not in areas:
        raise ValueError(
            f"Área '{area}' inválida. Áreas válidas: {list(areas.keys())}"
        )
    if not (1 <= impact <= 5):
        raise ValueError("Impacto deve ser de 1 a 5.")

    event = {
        "timestamp": datetime.now().isoformat(),
        "area": area,
        "area_name": areas[area]["name"],
        "category": category,
        "action": action,
        "impact": impact,
        "duration_minutes": duration_minutes,
        "source": source,
        "project": project,
        "notes": notes
    }

    # Despacho Inteligente (Local vs Rede Neural)
    master_url = os.getenv("JARVIS_MASTER_URL")
    if master_url:
        try:
            payload = {
                "area_id": area,
                "category": category,
                "action": action,
                "impact": impact,
                "duration_minutes": duration_minutes,
                "project": project
            }
            res = requests.post(f"{master_url}/api/log", json=payload, timeout=5)
            if res.status_code == 200:
                print(f"[JARVIS Network] Evento sincronizado com o Master node ({master_url})")
            else:
                print(f"⚠️ Erro ao syncar com Master: {res.text}. Salvando local fallback.")
                events = load_today_log()
                events.append(event)
                save_log(events)
        except Exception as e:
            print(f"⚠️ Node Master inalcançável: {e}. Salvando local fallback.")
            events = load_today_log()
            events.append(event)
            save_log(events)
    else:
        # Modo Monolítico Tradicional
        events = load_today_log()
        events.append(event)
        save_log(events)

    print(f"\n✅ EVENTO LOGADO")
    print(f"   Área:     {areas[area]['name']}")
    print(f"   Ação:     {action}")
    print(f"   Impacto:  {'⭐' * impact} ({impact}/5)")
    print(f"   Duração:  {duration_minutes}min")
    print(f"   Modo:     {'Rede Neural' if master_url else 'Monolítico (Local)'}\n")

    return event


def list_today_events() -> None:
    """Exibe os eventos registrados hoje."""
    events = load_today_log()
    if not events:
        print("📭 Nenhum evento registrado hoje ainda.")
        return

    print(f"\n📋 EVENTOS DE HOJE — {date.today().strftime('%d/%m/%Y')}")
    print("=" * 60)
    for i, e in enumerate(events, 1):
        ts = datetime.fromisoformat(e["timestamp"]).strftime("%H:%M")
        impact_stars = "⭐" * e["impact"]
        duration = f"{e['duration_minutes']}min" if e["duration_minutes"] > 0 else "—"
        print(f"  {i:02d}. [{ts}] [{e['area_name'][:12]:<12}] {e['action']}")
        print(f"       Impacto: {impact_stars}  |  Duração: {duration}  |  Fonte: {e['source']}")
    print(f"\n  Total: {len(events)} eventos registrados\n")


def get_today_summary() -> dict:
    """Retorna resumo estruturado dos eventos do dia."""
    events = load_today_log()
    areas = load_areas()

    summary = {
        "date": date.today().isoformat(),
        "total_events": len(events),
        "total_duration_minutes": sum(e.get("duration_minutes", 0) for e in events),
        "by_area": {}
    }

    for area_id, area_info in areas.items():
        area_events = [e for e in events if e["area"] == area_id]
        summary["by_area"][area_id] = {
            "name": area_info["name"],
            "weight": area_info["weight"],
            "events": len(area_events),
            "total_impact": sum(e["impact"] for e in area_events),
            "total_duration": sum(e.get("duration_minutes", 0) for e in area_events),
            "actions": [e["action"] for e in area_events]
        }

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="COS Event Logger — Registre atividades produtivas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python event_logger.py --area economic_output --category licitacao --action "Analisou edital SECOM" --impact 4 --duration 45
  python event_logger.py --area system_building --category dev --action "Criou script de automação" --impact 5 --duration 90
  python event_logger.py --area energy_body --category saude --action "Academia 1h" --impact 3 --duration 60
  python event_logger.py --list
        """
    )

    parser.add_argument("--area", type=str, help="ID da área estratégica")
    parser.add_argument("--category", type=str, default="geral", help="Categoria da ação")
    parser.add_argument("--action", type=str, help="Descrição da ação realizada")
    parser.add_argument("--impact", type=int, choices=[1,2,3,4,5], default=3, help="Impacto (1-5)")
    parser.add_argument("--duration", type=int, default=0, help="Duração em minutos")
    parser.add_argument("--source", type=str, default="manual", help="Fonte do log")
    parser.add_argument("--project", type=str, default="", help="Projeto relacionado")
    parser.add_argument("--notes", type=str, default="", help="Observações")
    parser.add_argument("--list", action="store_true", help="Lista eventos de hoje")
    parser.add_argument("--summary", action="store_true", help="Exibe resumo de hoje")

    args = parser.parse_args()

    if args.list:
        list_today_events()
    elif args.summary:
        summary = get_today_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif args.area and args.action:
        log_event(
            area=args.area,
            category=args.category,
            action=args.action,
            impact=args.impact,
            duration_minutes=args.duration,
            source=args.source,
            project=args.project,
            notes=args.notes
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
