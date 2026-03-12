"""
JARVIS Knowledge Engine v1.0
Faz a curadoria e população dos arquivos de conhecimento no Google Drive.
- Consolida logs por pátio de projeto.
- Gera Snapshots de estado (Estrutura + Git + Status).
- Prepara o terreno para o Oráculo (NotebookLM).
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, date

# Integrar com o core
BASE_DIR = Path(__file__).parent.parent.parent
DIA_MD_PATH = BASE_DIR / "dia.md"
sys.path.insert(0, str(BASE_DIR))

from cos.core.shared import get_config, get_today_log, load_json, LOGS_DIR

def get_drive_path(filename: str) -> Path:
    config = get_config("oracle")
    return Path(config["drive_path"]) / filename

def format_event(event: dict) -> str:
    ts = event.get("timestamp", "").split("T")[-1][:8]
    cat = event.get("category", "INFO").upper()
    msg = event.get("message", "")
    return f"[{ts}] {cat}: {msg}\n"

def update_logs(full_sync=False):
    """Consolida os logs históricos e diários nos arquivos por projeto."""
    print(f"📋 [KNOWLEDGE] Consolidando logs ({'FULL SYNC' if full_sync else 'DAILY'})...")
    
    all_events = load_json(LOGS_DIR / "cos_events.json")
    if not isinstance(all_events, list):
        print("   ⚠️ Arquivo cos_events.json não encontrado ou inválido.")
        return

    # Se não for full_sync, filtra apenas os de hoje
    today = date.today().isoformat()
    events_to_process = all_events if full_sync else [e for e in all_events if e.get("timestamp", "").startswith(today)]

    if not events_to_process:
        print("   ⚠️ Nenhum evento para processar.")
    else:
        # Mapeamento de palavras-chave para arquivos
        mapping = {
            "ARTE": ["arte", "licitacao", "matching", "master", "edital"],
            "WAPPI": ["wappi", "whatsapp", "evolution", "crm"],
            "JARVIS": ["jarvis", "core", "pulse", "governance", "heartbeat", "knowledge"]
        }

        project_logs = {proj: [] for proj in mapping}
        
        for event in events_to_process:
            msg_lower = event.get("message", "").lower()
            action_lower = event.get("action", "").lower()
            combined = msg_lower + " " + action_lower
            
            for proj, keywords in mapping.items():
                if any(k in combined for k in keywords) or event.get("project", "").upper() == proj:
                    project_logs[proj].append(format_event(event))
                    break

        for proj, lines in project_logs.items():
            if lines:
                path = get_drive_path(f"{proj}_Logs.txt")
                mode = "w" if full_sync else "a"
                with open(path, mode, encoding="utf-8") as f:
                    if full_sync:
                        f.write(f"# LOGS HISTÓRICOS CONSOLIDADOS: {proj}\n")
                        f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.writelines(lines)
                print(f"   ✅ {len(lines)} eventos do cos_events sincronizados para {proj}")

    # Parte 2: Ingestão de logs externos (Tecnicos)
    print("🔬 [KNOWLEDGE] Processando logs técnicos (Raw logs)...")
    projects_config = get_config("projects")
    for p in projects_config.get("projects", []):
        proj_id_raw = p["id"].lower()
        target_proj = "JARVIS" if proj_id_raw == "jarvis" else ("ARTE" if proj_id_raw == "arte_" else ("WAPPI" if proj_id_raw == "wappi" else None))
        
        if not target_proj: continue
        
        log_files = p.get("observe", {}).get("logs", [])
        if not log_files and target_proj == "ARTE": # Fallback manual para o que vimos
             log_files = ["logs/notebook_pipeline.log", "logs/notebook_heavy.log"]
        
        if log_files:
            drive_log_path = get_drive_path(f"{target_proj}_Logs.txt")
            with open(drive_log_path, "a", encoding="utf-8") as f_out:
                f_out.write(f"\n\n--- LOGS TÉCNICOS ({datetime.now().strftime('%Y-%m-%d')}) ---\n")
                for rel_path in log_files:
                    abs_log = Path(p["path"]) / rel_path
                    if abs_log.exists():
                        print(f"   📂 Lendo log técnico: {target_proj} -> {rel_path}")
                        with open(abs_log, "r", encoding="utf-8", errors="ignore") as f_in:
                            # Pega as últimas 50 linhas para não explodir o arquivo
                            lines = f_in.readlines()
                            f_out.write(f"\n[Sinal de {rel_path}]:\n")
                            f_out.writelines(lines[-50:])
            print(f"   ✅ Logs técnicos de {target_proj} anexados.")

def generate_tree(path: Path, max_depth: int = 2) -> str:
    """Gera uma visão simplificada da árvore de diretórios."""
    output = []
    
    def _walk(current_path, depth):
        if depth > max_depth:
            return
        try:
            items = sorted(list(current_path.iterdir()))
            for item in items:
                if item.name.startswith(('.', '__')) or item.name in ['node_modules', 'venv', '.venv', 'dist']:
                    continue
                
                indent = "  " * depth
                symbol = "📂" if item.is_dir() else "📄"
                output.append(f"{indent}{symbol} {item.name}")
                if item.is_dir():
                    _walk(item, depth + 1)
        except:
            pass

    output.append(f"Raiz: {path.name}")
    _walk(path, 0)
    return "\n".join(output)

def update_snapshots():
    """Gera a 'foto' atual de cada projeto."""
    print("📸 [KNOWLEDGE] Gerando Snapshots de estado...")
    projects_config = get_config("projects")
    heartbeat_data = load_json(BASE_DIR / "cos" / "logs" / "jarvis_heartbeat.json")
    
    # Mapeia IDs de projetos para nomes de arquivos no Drive
    target_mapping = {
        "jarvis": "JARVIS",
        "arte_": "ARTE",
        "wappi": "WAPPI"
    }

    for p in projects_config.get("projects", []):
        proj_id_raw = p["id"].lower()
        if proj_id_raw not in target_mapping:
            continue
            
        proj_id = target_mapping[proj_id_raw]
        path = Path(p["path"])
        file_path = get_drive_path(f"{proj_id}_Snapshot.txt")
        
        snapshot = []
        snapshot.append(f"# STATUS ATUAL: {p['name']}")
        snapshot.append(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        snapshot.append(f"Área: {p.get('area', 'N/A')}")
        snapshot.append("-" * 30)
        
        # Git Status
        try:
            git_branch = subprocess.check_output(["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
            snapshot.append(f"Git Branch: {git_branch}")
            git_log = subprocess.check_output(["git", "-C", str(path), "log", "-1", "--format=%s (%cr)"], text=True).strip()
            snapshot.append(f"Último Commit: {git_log}")
        except:
            snapshot.append("Git: Não inicializado ou erro.")

        # Score (se disponível para o projeto)
        if heartbeat_data and proj_id == "JARVIS":
            snapshot.append(f"Score Global: {heartbeat_data.get('score', 0)}")
            snapshot.append(f"Classificação: {heartbeat_data.get('classification', 'N/A')}")

        snapshot.append("\n## ESTRUTURA DE DIRETÓRIOS")
        snapshot.append(generate_tree(path))

        # Adição do TODO.md
        todo_file = next((path / f for f in ["TODO.md", "todo.md"] if (path / f).exists()), None)
        if todo_file:
            snapshot.append("\n## TASKS EM ABERTO (TODO)")
            try:
                with open(todo_file, "r", encoding="utf-8") as f:
                    snapshot.append(f.read())
            except:
                snapshot.append("Erro ao ler TODO.md")
        
        # Escreve (Sobrescreve)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(snapshot))
        print(f"   ✅ Snapshot de {proj_id} atualizado (com TODO).")

def update_dia_historico():
    """Anexa o dia.md atual ao dia.txt no Drive (Histórico de Resumos)."""
    print("📋 [KNOWLEDGE] Atualizando histórico dia.txt...")
    if not DIA_MD_PATH.exists():
        return

    drive_path = get_drive_path("dia.txt")
    with open(DIA_MD_PATH, "r", encoding="utf-8") as f:
        today_content = f.read()

    # Verifica se já postamos hoje para não duplicar
    today_marker = f"### DATA: {date.today().isoformat()}"
    existing_content = ""
    if drive_path.exists():
        with open(drive_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

    if today_marker not in existing_content:
        with open(drive_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n{'='*60}\n")
            f.write(f"{today_marker}\n")
            f.write(f"{'='*60}\n\n")
            f.write(today_content)
        print("   ✅ Dia consolidado anexado ao dia.txt")
    else:
        print("   ℹ️  Dia de hoje já presente no histórico.")

def collect_strategic_decisions():
    """Lê os logs de hoje e extrai as DECISIONs para os arquivos locais de docs/decisions.md de cada projeto."""
    print("💎 [KNOWLEDGE] Minerando decisões estratégicas dos logs...")
    today_events = get_today_log()
    if not today_events:
        return

    projects_config = get_config("projects")
    projects_list = projects_config.get("projects", [])
    
    for event in today_events:
        if event.get("category", "").upper() == "DECISION":
            action = event.get("action", "")
            impact = event.get("impact", 5)
            # Tenta casar o nome do projeto do log com o ID ou Nome da config
            proj_name_log = event.get("project", "").lower()
            
            target_project = None
            for p in projects_list:
                if p["id"].lower() == proj_name_log or p["name"].lower().startswith(proj_name_log):
                    target_project = p
                    break
            
            if not target_project:
                print(f"   ⚠️ Projeto '{proj_name_log}' não encontrado na configuração. Usando JARVIS como padrão.")
                target_project = next((p for p in projects_list if p["id"] == "jarvis"), None)
            
            if not target_project: continue

            proj_path = Path(target_project["path"])
            local_path = proj_path / "JARVIS" / "docs"
            local_file = local_path / "decisions.md"
            
            # Garante que a pasta docs existe
            if not local_path.exists():
                local_path.mkdir(parents=True, exist_ok=True)
            
            # Formata como ADR (Architecture Decision Record)
            ts = event.get("timestamp", "").split("T")[0]
            new_decision = f"\n## {action}\n"
            new_decision += f"**Data**: {ts}\n"
            new_decision += f"**Impacto**: {impact}/5 (Log Automático)\n"
            new_decision += f"**Status**: Executado com Sucesso ✅\n"

            # Lê atual para não duplicar
            current_content = ""
            if local_file.exists():
                with open(local_file, "r", encoding="utf-8") as f:
                    current_content = f.read()
            
            if action not in current_content:
                with open(local_file, "a", encoding="utf-8") as f:
                    f.write(new_decision)
                print(f"   ✨ Nova decisão registrada para {target_project['id']}: {action}")

def update_strategies():
    """
    Sincroniza decisões estratégicas. 
    Lê o que foi gerado em docs/decisions.md e envia para o Oráculo (Estrategia.txt).
    """
    print("🧠 [KNOWLEDGE] Sincronizando Estratégias e ADRs para o Oráculo...")
    projects_config = get_config("projects")
    target_mapping = {"jarvis": "JARVIS", "arte_": "ARTE", "wappi": "WAPPI"}

    for p in projects_config.get("projects", []):
        proj_id_raw = p["id"].lower()
        if proj_id_raw not in target_mapping:
            continue
            
        proj_id = target_mapping[proj_id_raw]
        local_decision_file = Path(p["path"]) / "JARVIS" / "docs" / "decisions.md"
        drive_strategy_path = get_drive_path(f"{proj_id}_Estrategia.txt")

        if local_decision_file.exists():
            print(f"   📂 Lendo decisões de {proj_id}...")
            with open(local_decision_file, "r", encoding="utf-8") as f:
                decisions = f.read()
            
            # Lê o que já está lá para evitar duplicação total
            current_strategy = ""
            if drive_strategy_path.exists():
                with open(drive_strategy_path, "r", encoding="utf-8") as f:
                    current_strategy = f.read()
            
            # Estratégia simples: se o arquivo local mudou, a gente reflete ou anexa 
            # (Aqui vamos sobrescrever o compilado para manter o documento 'limpo' mas com histórico local)
            if decisions.strip() and decisions != current_strategy:
                with open(drive_strategy_path, "w", encoding="utf-8") as f:
                    f.write(f"# {proj_id} STRATEGIC BRAIN\n")
                    f.write(f"Última Sincronia: {datetime.now().strftime('%Y-%m-%d')}\n\n")
                    f.write(decisions)
                print(f"   ✅ Estratégia de {proj_id} atualizada via local /JARVIS/docs/decisions.md")

def run_knowledge_cycle(full_sync=False):
    print(f"\n🧠 [KNOWLEDGE ENGINE] Iniciando ciclo às {datetime.now().strftime('%H:%M:%S')}")
    try:
        collect_strategic_decisions() # Coleta decisões dos logs primeiro
        update_logs(full_sync=full_sync)
        update_snapshots()
        update_dia_historico()
        update_strategies() # Sincroniza os arquivos gerados
        print("🏁 [KNOWLEDGE ENGINE] Ciclo concluído com sucesso.")
    except Exception as e:
        print(f"❌ [KNOWLEDGE ENGINE] Erro no ciclo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-sync", action="store_true", help="Faz a sincronia de todo o histórico de logs.")
    args = parser.parse_args()
    
    run_knowledge_cycle(full_sync=args.full_sync)
