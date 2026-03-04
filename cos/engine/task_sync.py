"""
JARVIS Task Sync v1.0 (Bidirectional)
Sincroniza o estado [x]/[ ] das tasks entre os TODO.md de cada projeto
e o TODO.md global do JARVIS.

Lógica: [x] sempre vence. Se uma task está marcada como concluída em
qualquer lado, o outro lado é atualizado para refletir isso.

Executado pelo jarvis_pulse.py a cada batida horária.
"""

import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent  # cos/
JARVIS_ROOT = BASE_DIR.parent            # JARVIS/

sys.path.insert(0, str(BASE_DIR / "core"))
from shared import get_config

# Regex para encontrar checkboxes markdown
# Captura: prefixo (espaço/tab + - ou *), estado ([ ] ou [x] ou [/]), texto da task
TASK_RE = re.compile(r'^(\s*[-*]\s*)\[([ x/])\]\s*(.+)$', re.IGNORECASE)


def normalize_task_text(text: str) -> str:
    """Normaliza o texto da task para comparação, removendo formatação extra."""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)        # colapsa espaços
    text = text.rstrip('.')                   # remove ponto final
    return text.lower()


def parse_tasks(filepath: Path) -> list[dict]:
    """Lê um arquivo .md e retorna lista de tasks com linha, estado e texto."""
    tasks = []
    if not filepath.exists():
        return tasks

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        m = TASK_RE.match(line.rstrip('\r\n'))
        if m:
            prefix = m.group(1)
            state = m.group(2).lower()    # ' ', 'x', '/'
            raw_text = m.group(3)
            tasks.append({
                "line_num": i,
                "prefix": prefix,
                "state": state,
                "raw_text": raw_text,
                "normalized": normalize_task_text(raw_text),
                "original_line": line,
            })
    return tasks


def sync_tasks_bidirectional(file_a: Path, file_b: Path) -> dict:
    """
    Sincroniza tasks entre dois arquivos markdown.
    Regra: [x] sempre vence sobre [ ] e [/].
    Retorna dict com contagem de mudanças.
    """
    tasks_a = parse_tasks(file_a)
    tasks_b = parse_tasks(file_b)

    if not tasks_a or not tasks_b:
        return {"changes_a": 0, "changes_b": 0}

    # Índice: texto normalizado → lista de tasks
    index_b = {}
    for t in tasks_b:
        key = t["normalized"]
        if key not in index_b:
            index_b[key] = []
        index_b[key].append(t)

    changes_a = 0
    changes_b = 0

    # Para cada task em A, procura em B
    for task_a in tasks_a:
        key = task_a["normalized"]
        if key not in index_b:
            continue  # Task só existe em A, nada pra sincronizar

        for task_b in index_b[key]:
            # Se um marcou [x] e o outro não
            if task_a["state"] == "x" and task_b["state"] != "x":
                task_b["new_state"] = "x"
                changes_b += 1
            elif task_b["state"] == "x" and task_a["state"] != "x":
                task_a["new_state"] = "x"
                changes_a += 1

    # Aplica mudanças em A
    if changes_a > 0:
        _apply_changes(file_a, tasks_a)

    # Aplica mudanças em B
    if changes_b > 0:
        _apply_changes(file_b, tasks_b)

    return {"changes_a": changes_a, "changes_b": changes_b}


def _apply_changes(filepath: Path, tasks: list[dict]):
    """Reescreve o arquivo aplicando os new_state onde necessário."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for task in tasks:
        if "new_state" not in task:
            continue
        line_num = task["line_num"]
        old_line = lines[line_num]
        # Substitui apenas o checkbox mantendo todo o resto
        new_line = TASK_RE.sub(
            lambda m: f'{m.group(1)}[{task["new_state"]}] {m.group(3)}',
            old_line.rstrip('\r\n')
        ) + '\n'
        lines[line_num] = new_line

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)


def run_full_sync() -> dict:
    """
    Executa o sync bidirecional entre o TODO.md do JARVIS e cada projeto.
    Retorna resumo das mudanças.
    """
    projects_config = get_config("projects")
    if not projects_config:
        return {"status": "no_config"}

    jarvis_todo = JARVIS_ROOT / "TODO.md"
    if not jarvis_todo.exists():
        return {"status": "no_jarvis_todo"}

    results = {}
    projects = projects_config.get("projects", [])

    for proj in projects:
        proj_id = proj.get("id", "unknown")
        proj_path = proj.get("path")
        todo_file = proj.get("observe", {}).get("todo_file")

        if not proj_path or not todo_file:
            continue

        proj_todo = Path(proj_path) / todo_file

        # Evita sincronizar o JARVIS consigo mesmo
        if proj_todo.resolve() == jarvis_todo.resolve():
            continue

        if not proj_todo.exists():
            continue

        result = sync_tasks_bidirectional(jarvis_todo, proj_todo)
        total = result["changes_a"] + result["changes_b"]

        if total > 0:
            results[proj_id] = result
            print(f"  🔄 [{proj_id}] {result['changes_a']} ← JARVIS | Projeto → {result['changes_b']}")

    return results


if __name__ == "__main__":
    print("=== 🔄 JARVIS Task Sync (Bidirecional) ===\n")
    results = run_full_sync()
    total_changes = sum(r["changes_a"] + r["changes_b"] for r in results.values()) if results and isinstance(results, dict) and "status" not in results else 0
    if total_changes > 0:
        print(f"\n✅ Sync concluído! {total_changes} task(s) sincronizada(s).")
    else:
        print("\n✅ Tudo já está sincronizado. Nenhuma diferença encontrada.")
