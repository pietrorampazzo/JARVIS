"""
COS — NotebookLM Client v1.0
Integração com o MCP do NotebookLM para upload de briefings e logs para o notebook JARVIS.
"""

import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent.parent

# Nome do notebook alvo no NotebookLM
JARVIS_NOTEBOOK_NAME = "JARVIS"


def run_mcp_command(tool: str, params: dict) -> dict:
    """
    Executa um comando no servidor MCP do NotebookLM.
    Retorna o resultado como dict.

    Nota: Esta função assume que o MCP do NotebookLM está configurado
    e acessível via stdio pelo Antigravity.
    """
    # Em contexto Antigravity, o MCP é chamado diretamente pelo agente.
    # Esta função serve como interface de referência.
    raise NotImplementedError(
        f"MCP deve ser chamado via Antigravity Agent Manager.\n"
        f"Tool: {tool}\nParams: {json.dumps(params, ensure_ascii=False, indent=2)}"
    )


def upload_morning_brief(brief_path: Path) -> str:
    """
    Faz upload do morning briefing para o notebook JARVIS.
    
    Em produção, o agente Antigravity deve:
    1. list_notebooks → encontrar JARVIS
    2. add_source_text → com o conteúdo do briefing
    """
    if not brief_path.exists():
        return "❌ Arquivo de briefing não encontrado."

    with open(brief_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Instrução para o agente Antigravity
    instruction = f"""
Para fazer upload deste briefing ao NotebookLM JARVIS, o agente deve:

1. Usar list_notebooks para encontrar o notebook '{JARVIS_NOTEBOOK_NAME}'
2. Usar add_source_text com:
   - notebook_id: <id do JARVIS>
   - title: "Morning Brief {date.today().strftime('%d-%m-%Y')}"
   - content: (conteúdo abaixo)

CONTEÚDO:
{content}
    """
    print(instruction)
    return instruction


def upload_log_summary(log_date: Optional[date] = None) -> str:
    """
    Prepara resumo do log do dia para upload ao JARVIS.
    """
    log_date = log_date or date.today()
    log_path = BASE_DIR / "logs" / f"{log_date.isoformat()}.json"

    if not log_path.exists():
        return f"❌ Log de {log_date} não encontrado."

    with open(log_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    # Construir resumo markdown
    lines = [f"# COS Log — {log_date.strftime('%d/%m/%Y')}\n"]
    lines.append(f"**Total de eventos:** {len(events)}\n")

    by_area: dict = {}
    for e in events:
        area = e.get("area_name", e.get("area", "?"))
        if area not in by_area:
            by_area[area] = []
        ts = e["timestamp"][11:16]
        lines_entry = f"- [{ts}] **{e['action']}** (Impacto: {e['impact']}/5, {e.get('duration_minutes', 0)}min)"
        by_area[area].append(lines_entry)

    for area_name, entries in by_area.items():
        lines.append(f"\n## {area_name}")
        lines.extend(entries)

    summary_md = "\n".join(lines)
    
    # Salvar localmente também
    jarvis_dir = BASE_DIR / "integrations" / "jarvis_uploads"
    jarvis_dir.mkdir(parents=True, exist_ok=True)
    out_path = jarvis_dir / f"log_summary_{log_date.isoformat()}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(summary_md)

    print(f"📄 Resumo gerado: {out_path}")
    print(f"\n📤 Para upload ao JARVIS, use o MCP add_source_text com o conteúdo acima.")
    return summary_md


def generate_skill_artifact_doc(skill_name: str, description: str) -> str:
    """Gera documento markdown para documentar uma skill no JARVIS."""
    content = f"""# Skill: {skill_name}

**Data de criação:** {date.today().strftime('%d/%m/%Y')}
**Projeto:** COS — Cognitive Operating System

## Descrição
{description}

## Localização
`.agent/skills/{skill_name}/SKILL.md`

## Status
✅ Ativa
"""
    jarvis_dir = BASE_DIR / "integrations" / "jarvis_uploads"
    jarvis_dir.mkdir(parents=True, exist_ok=True)
    out_path = jarvis_dir / f"skill_{skill_name}_{date.today().isoformat()}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📄 Artefato de skill gerado: {out_path}")
    return content


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="COS NotebookLM Client (JARVIS)")
    parser.add_argument("--upload-log", type=str, default="today", help="Upload log de data (YYYY-MM-DD ou 'today')")
    parser.add_argument("--upload-brief", type=str, help="Path do arquivo de briefing .md para upload")
    parser.add_argument("--skill-doc", nargs=2, metavar=("NOME", "DESCRICAO"), help="Gera doc de skill para JARVIS")
    args = parser.parse_args()

    if args.upload_log:
        d = date.today() if args.upload_log == "today" else date.fromisoformat(args.upload_log)
        upload_log_summary(d)

    if args.upload_brief:
        upload_morning_brief(Path(args.upload_brief))

    if args.skill_doc:
        generate_skill_artifact_doc(args.skill_doc[0], args.skill_doc[1])
