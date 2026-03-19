"""
JARVIS AUDIT MODULE v2.0 - Auditoria TOTAL do Projeto arte_

Este modulo audita ABSOLUTAMENTE TUDO no projeto arte_:
1. Snapshots completos do sistema de arquivos (hash + tamanho + data)
2. Diffs entre snapshots (o que mudou nos ultimos 30 min)
3. Git diffs (commits recentes)
4. Monitoramento de logs do sistema
5. Execucoes de scripts (audit_start/audit_end)
6. Mudancas na pasta DOWNLOADS

O JARVIS Daemon roda audit_full_cycle() a cada 30 minutos.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import os
import uuid
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

# === PATHS ===
JARVIS_DIR = Path(__file__).parent
PROJECT_ROOT = JARVIS_DIR.parent
LOGS_DIR = JARVIS_DIR / "logs"
AUDIT_LOG = LOGS_DIR / "audit.json"
SNAPSHOT_FILE = LOGS_DIR / "snapshot.json"
DIFF_LOG = LOGS_DIR / "diffs.json"
HEALTH_LOG = LOGS_DIR / "health.json"
MANIFEST_FILE = JARVIS_DIR / "MANIFEST.md"

# Pastas e extensoes a IGNORAR no scan
IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".vscode", "DEPRECATED", "ACHIVE", "achive"}
IGNORE_EXTENSIONS = {".pyc", ".pyo", ".tmp", ".log"}


# =============================================
# 1. SNAPSHOT DO SISTEMA DE ARQUIVOS
# =============================================

def _file_hash(filepath: Path) -> str:
    """Calcula hash MD5 rapido de um arquivo."""
    try:
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, OSError):
        return "error"


def take_snapshot() -> dict:
    """Gera um snapshot completo de todos os arquivos do projeto."""
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "files": {}
    }

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Filtra diretorios ignorados
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for filename in files:
            filepath = Path(root) / filename

            if filepath.suffix in IGNORE_EXTENSIONS:
                continue

            rel_path = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")
            stat = filepath.stat()

            snapshot["files"][rel_path] = {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "hash": _file_hash(filepath)
            }

    snapshot["total_files"] = len(snapshot["files"])
    return snapshot


def save_snapshot(snapshot: dict):
    """Salva o snapshot atual no disco."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)


def load_previous_snapshot() -> dict:
    """Carrega o snapshot anterior para comparacao."""
    if SNAPSHOT_FILE.exists():
        try:
            with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


# =============================================
# 2. DIFF ENTRE SNAPSHOTS (O Coracao da Auditoria)
# =============================================

def compute_diff(old_snapshot: dict, new_snapshot: dict) -> dict:
    """Compara dois snapshots e retorna todas as diferencas."""
    diff = {
        "timestamp": datetime.now().isoformat(),
        "period": {
            "from": old_snapshot.get("timestamp", "unknown"),
            "to": new_snapshot.get("timestamp", "unknown")
        },
        "created": [],
        "modified": [],
        "deleted": [],
        "summary": {}
    }

    old_files = old_snapshot.get("files", {})
    new_files = new_snapshot.get("files", {})

    # Arquivos NOVOS (existem no new mas nao no old)
    for path in new_files:
        if path not in old_files:
            diff["created"].append({
                "path": path,
                "size": new_files[path]["size"],
                "type": Path(path).suffix or "dir"
            })

    # Arquivos MODIFICADOS (existem em ambos mas hash diferente)
    for path in new_files:
        if path in old_files:
            if new_files[path]["hash"] != old_files[path]["hash"]:
                diff["modified"].append({
                    "path": path,
                    "old_size": old_files[path]["size"],
                    "new_size": new_files[path]["size"],
                    "old_modified": old_files[path]["modified"],
                    "new_modified": new_files[path]["modified"]
                })

    # Arquivos DELETADOS (existem no old mas nao no new)
    for path in old_files:
        if path not in new_files:
            diff["deleted"].append({
                "path": path,
                "last_size": old_files[path]["size"]
            })

    diff["summary"] = {
        "created_count": len(diff["created"]),
        "modified_count": len(diff["modified"]),
        "deleted_count": len(diff["deleted"]),
        "total_changes": len(diff["created"]) + len(diff["modified"]) + len(diff["deleted"]),
        "total_files_now": new_snapshot.get("total_files", 0)
    }

    return diff


def save_diff(diff: dict):
    """Salva o diff no historico de diffs."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    history = []
    if DIFF_LOG.exists():
        try:
            with open(DIFF_LOG, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    history.append(diff)

    # Manter apenas os ultimos 48 diffs (24h de historico com ciclos de 30min)
    history = history[-48:]

    with open(DIFF_LOG, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


# =============================================
# 3. GIT DIFF (Commits recentes)
# =============================================

def get_git_status() -> dict:
    """Captura o status do Git no projeto."""
    try:
        # Ultimo commit
        last_commit = subprocess.run(
            ["git", "log", "-1", "--format=%H|%s|%ai"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )

        # Arquivos modificados nao commitados
        git_status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )

        # Diff stat (resumo de linhas alteradas)
        git_diff_stat = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )

        commit_parts = last_commit.stdout.strip().split("|") if last_commit.returncode == 0 else []

        uncommitted = []
        if git_status.returncode == 0:
            for line in git_status.stdout.strip().split("\n"):
                if line.strip():
                    status_code = line[:2].strip()
                    filepath = line[3:].strip()
                    uncommitted.append({"status": status_code, "file": filepath})

        return {
            "last_commit": {
                "hash": commit_parts[0] if len(commit_parts) > 0 else "N/A",
                "message": commit_parts[1] if len(commit_parts) > 1 else "N/A",
                "date": commit_parts[2] if len(commit_parts) > 2 else "N/A"
            },
            "uncommitted_changes": uncommitted,
            "uncommitted_count": len(uncommitted),
            "diff_stat": git_diff_stat.stdout.strip() if git_diff_stat.returncode == 0 else ""
        }
    except FileNotFoundError:
        return {"error": "Git not found"}


# =============================================
# 4. MONITORAMENTO ESPECIFICO DA PASTA DOWNLOADS
# =============================================

def audit_downloads() -> dict:
    """Auditoria detalhada da pasta DOWNLOADS."""
    downloads = PROJECT_ROOT / "DOWNLOADS"
    result = {
        "editais": {"count": 0, "items": []},
        "propostas": {"count": 0, "items": []},
        "catalogos": {"count": 0},
        "planilhas_master": []
    }

    # Editais
    editais_dir = downloads / "EDITAIS"
    if editais_dir.exists():
        items = [d.name for d in editais_dir.iterdir() if d.is_dir()]
        result["editais"] = {"count": len(items), "items": items}

    # Propostas
    propostas_dir = downloads / "PROPOSTAS"
    if propostas_dir.exists():
        items = [f.name for f in propostas_dir.iterdir()]
        result["propostas"] = {"count": len(items), "items": items}

    # Catalogos
    catalogos_dir = downloads / "CATALOGOS"
    if catalogos_dir.exists():
        result["catalogos"]["count"] = len(list(catalogos_dir.iterdir()))

    # Planilhas master
    for f in downloads.iterdir():
        if f.is_file() and f.suffix == ".xlsx":
            result["planilhas_master"].append({
                "name": f.name,
                "size_kb": round(f.stat().st_size / 1024, 1),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })

    return result


# =============================================
# 5. AUDIT DE EXECUCAO DE SCRIPTS (compativel com v1)
# =============================================

def _load_log():
    if AUDIT_LOG.exists():
        try:
            with open(AUDIT_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"runs": [], "events": []}
    return {"runs": [], "events": []}


def _save_log(data):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def audit_start(script_name: str, context: dict = None) -> str:
    """Registra o INICIO de uma execucao de script."""
    run_id = str(uuid.uuid4())[:8]
    log = _load_log()
    entry = {
        "run_id": run_id,
        "script": script_name,
        "started_at": datetime.now().isoformat(),
        "ended_at": None,
        "status": "running",
        "context": context or {},
        "metrics": {},
        "duration_seconds": None
    }
    log["runs"].append(entry)
    _save_log(log)
    print(f"[JARVIS AUDIT] Inicio: {script_name} (run: {run_id})")
    return run_id


def audit_end(run_id: str, status: str = "success", metrics: dict = None):
    """Registra o FIM de uma execucao."""
    log = _load_log()
    for run in log["runs"]:
        if run["run_id"] == run_id:
            run["ended_at"] = datetime.now().isoformat()
            run["status"] = status
            run["metrics"] = metrics or {}
            started = datetime.fromisoformat(run["started_at"])
            ended = datetime.fromisoformat(run["ended_at"])
            run["duration_seconds"] = round((ended - started).total_seconds(), 2)
            print(f"[JARVIS AUDIT] Fim: {run['script']} ({run['duration_seconds']}s) - {status}")
            break
    _save_log(log)


def audit_event(run_id: str, event_type: str, data: dict = None):
    """Registra um EVENTO intermediario."""
    log = _load_log()
    event = {
        "run_id": run_id,
        "event": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": data or {}
    }
    log["events"].append(event)
    _save_log(log)


# =============================================
# 6. CICLO COMPLETO DE AUDITORIA (30 min)
# =============================================

def audit_full_cycle() -> dict:
    """
    CICLO COMPLETO de auditoria. O daemon chama isso a cada 30 minutos.

    1. Tira snapshot novo do sistema de arquivos
    2. Compara com o snapshot anterior (diff)
    3. Captura status do Git
    4. Audita pasta DOWNLOADS
    5. Le tasks pendentes do JARVIS_MANIFEST.md
    6. Salva tudo
    7. Retorna relatorio consolidado
    """
    print("\n=== JARVIS AUDIT: Ciclo Completo ===")
    print(f"Horario: {datetime.now().strftime('%H:%M:%S')}")

    # 1. Snapshot atual
    print("[1/5] Tirando snapshot do sistema de arquivos...")
    new_snapshot = take_snapshot()
    print(f"      {new_snapshot['total_files']} arquivos mapeados.")

    # 2. Diff com snapshot anterior
    print("[2/5] Comparando com snapshot anterior...")
    old_snapshot = load_previous_snapshot()
    diff = None
    if old_snapshot:
        diff = compute_diff(old_snapshot, new_snapshot)
        save_diff(diff)
        s = diff["summary"]
        print(f"      +{s['created_count']} novos | ~{s['modified_count']} modificados | -{s['deleted_count']} deletados")
    else:
        print("      Primeiro snapshot. Nenhum diff disponivel.")

    # 3. Salva novo snapshot (sera o 'old' na proxima rodada)
    save_snapshot(new_snapshot)

    # 4. Git status
    print("[3/5] Verificando status do Git...")
    git = get_git_status()
    print(f"      Ultimo commit: {git.get('last_commit', {}).get('message', 'N/A')}")
    print(f"      Mudancas nao commitadas: {git.get('uncommitted_count', 0)}")

    # 5. Audit DOWNLOADS
    print("[4/5] Auditando pasta DOWNLOADS...")
    downloads = audit_downloads()
    print(f"      Editais: {downloads['editais']['count']} | Propostas: {downloads['propostas']['count']}")

    # 6. Tasks do Manifesto
    print("[5/5] Lendo tasks do MANIFEST.md...")
    tasks_data = {"pending": [], "done": []}
    if MANIFEST_FILE.exists():
        try:
            content = MANIFEST_FILE.read_text(encoding="utf-8")
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("- [ ]"):
                    tasks_data["pending"].append(line.replace("- [ ]", "").strip())
                elif line.startswith("- [x]"):
                    tasks_data["done"].append(line.replace("- [x]", "").strip())
        except Exception as e:
            print(f"      Erro ao ler manifesto: {e}")
    
    print(f"      Tasks: {len(tasks_data['done'])} concluidas | {len(tasks_data['pending'])} pendentes")

    tasks = {
        "pending_count": len(tasks_data["pending"]),
        "done_count": len(tasks_data["done"]),
        "pending_list": tasks_data["pending"],
        "done_list": tasks_data["done"]
    }

    # Relatorio consolidado
    report = {
        "timestamp": datetime.now().isoformat(),
        "filesystem": {
            "total_files": new_snapshot["total_files"],
            "diff": diff["summary"] if diff else "first_run"
        },
        "git": git,
        "downloads": downloads,
        "tasks": tasks,
        "script_runs": _load_log().get("runs", [])[-5:]
    }

    # 7. CLASSIFICACAO DE SAUDE
    print("[HEALTH] Classificando estado do projeto...")
    health = classify_health(report, diff)
    report["health"] = health
    save_health_history(health)

    print(f"      VEREDICTO: {health['verdict']} (Score: {health['score']}/100)")
    for e in health["evidence"]:
        print(f"      {'  [+]' if e['type'] == 'positive' else '  [-]' if e['type'] == 'negative' else '  [!]'} {e['message']}")

    print("\n=== Ciclo Completo Finalizado ===\n")
    return report


# =============================================
# 7. CLASSIFICACAO DE SAUDE DO PROJETO
# =============================================

# Scripts que DEVEM estar sendo executados para considerar progresso real
CRITICAL_SCRIPTS = [
    "arte_heavy_B", "arte_heavy_notebook", "01_ingestao_edital",
    "arte_metadados", "arte_pipeline", "arte_heavy_A_gemini"
]

# Pastas onde mudancas indicam progresso real (nao boilerplate)
PROGRESS_FOLDERS = [
    "DOWNLOADS/EDITAIS", "DOWNLOADS/PROPOSTAS", "arte_heavy/",
    "arte_edital/", "arte_metadados/", "arte_code/"
]

# Pastas onde mudancas sao irrelevantes para medir progresso
NOISE_FOLDERS = ["logs/", ".env", "tools/", "tests/"]


def classify_health(report: dict, diff: dict = None) -> dict:
    """
    Classifica o estado do projeto em 3 categorias:

    EVOLUCAO   = Progresso real, tangivel, mensuravel
    ESTAGNACAO = Nenhuma mudanca significativa, inatividade
    FALHA      = Scripts quebrando, arquivos sumindo, caos

    Retorna score 0-100, veredicto, e lista de evidencias.
    """
    score = 50  # Neutro
    evidence = []

    # --- SINAIS DE EVOLUCAO (+pontos) ---

    if diff and diff != "first_run":
        summary = diff.get("summary", {})

        # Arquivos novos em pastas de progresso
        created = diff.get("created", [])
        progress_creates = [f for f in created if any(f["path"].startswith(p) for p in PROGRESS_FOLDERS)]
        if progress_creates:
            score += 10 * min(len(progress_creates), 3)
            evidence.append({
                "type": "positive",
                "signal": "new_progress_files",
                "message": f"{len(progress_creates)} arquivo(s) novo(s) em pasta de progresso",
                "files": [f["path"] for f in progress_creates[:5]]
            })

        # Scripts modificados (evolucao de codigo)
        modified = diff.get("modified", [])
        code_changes = [f for f in modified if f["path"].endswith(".py") and not any(f["path"].startswith(n) for n in NOISE_FOLDERS)]
        if code_changes:
            score += 5 * min(len(code_changes), 4)
            evidence.append({
                "type": "positive",
                "signal": "code_evolution",
                "message": f"{len(code_changes)} script(s) Python modificado(s)",
                "files": [f["path"] for f in code_changes[:5]]
            })

        # Planilhas master atualizadas
        xlsx_changes = [f for f in modified if f["path"].endswith(".xlsx")]
        if xlsx_changes:
            score += 10
            evidence.append({
                "type": "positive",
                "signal": "data_updated",
                "message": f"Planilha(s) de dados atualizada(s): {', '.join(f['path'] for f in xlsx_changes[:3])}"
            })

        # Nenhuma mudanca = estagnacao
        total_changes = summary.get("total_changes", 0)
        if total_changes == 0:
            score -= 15
            evidence.append({
                "type": "negative",
                "signal": "no_changes",
                "message": "Nenhuma mudanca detectada neste ciclo (30 min)"
            })

    # --- SINAIS DE EVOLUCAO VIA SCRIPTS ---

    runs = report.get("script_runs", [])
    successful_runs = [r for r in runs if r.get("status") == "success"]
    critical_runs = [r for r in successful_runs if r.get("script") in CRITICAL_SCRIPTS]

    if critical_runs:
        score += 15
        evidence.append({
            "type": "positive",
            "signal": "critical_scripts_running",
            "message": f"{len(critical_runs)} script(s) critico(s) executado(s) com sucesso"
        })
    elif runs:
        score += 5
        evidence.append({
            "type": "positive",
            "signal": "scripts_running",
            "message": f"{len(successful_runs)} script(s) executado(s) (nenhum critico)"
        })

    # --- SINAIS DE ESTAGNACAO (-pontos) ---

    # Tasks: muitas pendentes, nenhuma concluida
    tasks = report.get("tasks", {})
    if tasks.get("pending", 0) > 0 and tasks.get("done", 0) == 0:
        score -= 10
        evidence.append({
            "type": "negative",
            "signal": "tasks_stalled",
            "message": f"{tasks['pending']} tasks pendentes, 0 concluidas no MANIFEST"
        })

    # Git: muitos uncommitted sem commit
    git = report.get("git", {})
    uncommitted = git.get("uncommitted_count", 0)
    if uncommitted > 20:
        score -= 10
        evidence.append({
            "type": "negative",
            "signal": "git_debt",
            "message": f"{uncommitted} mudancas nao commitadas (divida tecnica)"
        })
    elif uncommitted > 5:
        score -= 5
        evidence.append({
            "type": "negative",
            "signal": "git_uncommitted",
            "message": f"{uncommitted} mudancas nao commitadas"
        })

    # Planilha mestre antiga
    downloads = report.get("downloads", {})
    for planilha in downloads.get("planilhas_master", []):
        if planilha["name"] in ["master_heavy_ultra.xlsx", "master.xlsx", "master_heavy.xlsx"]:
            mod_date = datetime.fromisoformat(planilha["modified"])
            days_old = (datetime.now() - mod_date).days
            if days_old > 3:
                score -= 10
                evidence.append({
                    "type": "negative",
                    "signal": "stale_master_data",
                    "message": f"{planilha['name']} nao atualizada ha {days_old} dia(s)"
                })

    # --- SINAIS DE FALHA (-pontos criticos) ---

    # Scripts com erro
    failed_runs = [r for r in runs if r.get("status") == "error"]
    if failed_runs:
        score -= 20
        evidence.append({
            "type": "failure",
            "signal": "script_errors",
            "message": f"{len(failed_runs)} script(s) falharam",
            "scripts": [r.get("script") for r in failed_runs]
        })

    # Arquivos deletados inesperadamente
    if diff and diff != "first_run":
        deleted = diff.get("deleted", [])
        critical_deleted = [f for f in deleted if f["path"].endswith(".py") or f["path"].endswith(".xlsx")]
        if critical_deleted:
            score -= 25
            evidence.append({
                "type": "failure",
                "signal": "critical_files_deleted",
                "message": f"{len(critical_deleted)} arquivo(s) critico(s) deletado(s)!",
                "files": [f["path"] for f in critical_deleted]
            })

    # Scripts que nunca terminaram (status: running ha muito tempo)
    stuck_runs = [r for r in runs if r.get("status") == "running" and r.get("started_at")]
    for run in stuck_runs:
        started = datetime.fromisoformat(run["started_at"])
        if (datetime.now() - started).total_seconds() > 3600:  # 1h+
            score -= 15
            evidence.append({
                "type": "failure",
                "signal": "stuck_script",
                "message": f"Script '{run.get('script')}' travado ha mais de 1 hora"
            })

    # --- CLAMP & VEREDICTO ---
    score = max(0, min(100, score))

    if score >= 65:
        verdict = "EVOLUCAO"
    elif score >= 35:
        verdict = "ESTAGNACAO"
    else:
        verdict = "FALHA"

    return {
        "score": score,
        "verdict": verdict,
        "timestamp": datetime.now().isoformat(),
        "evidence": evidence,
        "summary": {
            "positive": len([e for e in evidence if e["type"] == "positive"]),
            "negative": len([e for e in evidence if e["type"] == "negative"]),
            "failure": len([e for e in evidence if e["type"] == "failure"])
        }
    }


def save_health_history(health: dict):
    """Salva o diagnostico no historico de saude."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    history = []
    if HEALTH_LOG.exists():
        try:
            with open(HEALTH_LOG, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    history.append(health)
    history = history[-96:]  # 48h de historico

    with open(HEALTH_LOG, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


# =============================================
# MAIN: Teste direto
# =============================================

if __name__ == "__main__":
    report = audit_full_cycle()
    print(json.dumps(report, indent=2, ensure_ascii=False))
