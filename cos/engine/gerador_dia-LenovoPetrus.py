"""
COS — Gerador Dia.md v1.0
Centraliza e sintetiza os eventos do dia em um markdown amigável (dia.md) para leitura pelo OpenClaw e pelo usuário.
Utiliza Gemini AI para gerar insights inteligentes da seção de Monitoramento.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import date, datetime

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent.parent
DIA_MD_PATH = BASE_DIR / "dia.md"

sys.path.insert(0, str(BASE_DIR / "cos" / "core"))
from shared import get_config, get_today_log, load_env, get_latest_snapshot

sys.path.insert(0, str(BASE_DIR / "cos" / "engine"))
from score_engine import calculate_daily_score


def get_git_summary() -> str:
    """Busca o log dos commits de hoje nos repositórios monitorados."""
    projects_config = get_config("projects")
    if not projects_config:
        return "Nenhum projeto monitorado."
        
    summary = []
    today_str = date.today().isoformat()
    
    projects_list = projects_config.get("projects", [])
    for proj_data in projects_list:
        proj_name = proj_data.get("name", proj_data.get("id", "Unknown"))
        path_str = proj_data.get("path")
        if not path_str:
            continue
            
        proj_path = Path(path_str)
        if proj_path.exists() and (proj_path / ".git").exists():
            try:
                # Usa subprocesso rodando um git log superficial
                result = subprocess.run(
                    ["git", "log", "--since=midnight", "--oneline"],
                    cwd=proj_path, capture_output=True, text=True
                )
                output = result.stdout.strip()
                if output:
                    summary.append(f"Projeto [{proj_name}]:\n{output}")
                else:
                    # Alternativa: verificar se há diff ou files unstaged
                    result_st = subprocess.run(
                        ["git", "status", "-s"],
                        cwd=proj_path, capture_output=True, text=True
                    )
                    st_out = result_st.stdout.strip()
                    if st_out:
                        summary.append(f"Projeto [{proj_name}]:\n{len(st_out.splitlines())} arquivos modificados não commitados.")
            except Exception as e:
                pass
                
    return "\n\n".join(summary) if summary else "Nenhuma alteração de código detectada hoje."

def get_todos_content() -> str:
    """Lê os arquivos TODO ou pendências dos projetos monitorados."""
    projects_config = get_config("projects")
    if not projects_config:
        return ""
        
    todos = []
    projects_list = projects_config.get("projects", [])
    for proj_data in projects_list:
        proj_name = proj_data.get("name", proj_data.get("id", "Unknown"))
        path_str = proj_data.get("path")
        todo_file = proj_data.get("observe", {}).get("todo_file")
        
        if not path_str or not todo_file:
            continue
            
        todo_path = Path(path_str) / todo_file
        if todo_path.exists():
            try:
                with open(todo_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        todos.append(f"### [Projeto {proj_name}]\n{content[:1000]}") # limite razoável
            except Exception:
                pass
                
    return "\n\n".join(todos) if todos else ""

def generate_ai_insights(score_data, logs_data, git_summary, pipeline_str, todos_content) -> str:
    """Consome a API do Gemini para gerar a seção 3 do dia.md."""
    if not HAS_GENAI:
        return "⚠️ Erro: `google.generativeai` não instalado. Instale via `pip install -U google-generativeai`."
        
    env = load_env()
    api_key = env.get("GEMINI_API_KEY", "")
    if not api_key:
        return "⚠️ Erro: GEMINI_API_KEY não encontrada no arquivo `.env`."
        
    genai.configure(api_key=api_key)
    
    genai.configure(api_key=api_key)
    
    prompt = f'''
Você é a Engine de Monitoramento do JARVIS (Cognitive Operating System).
Sua missão é gerar diretamente o texto Markdown formatado para a seção "3) 👁️ MONITORAMENTO E INSIGHTS (Gerado por IA)" focado em atividades operacionais, esforços e insights direcionados e confrontadores (se necessário) para o usuário PIETRO.

- Score do Dia: {score_data["global_score"]}/100.
- Classificação: {score_data["classification"]}

- Logs de Produção (Tarefas feitas hoje):
{logs_data}

- Trello Pipeline Snapshot:
{pipeline_str}

- Modificações em Códigos (Git):
{git_summary}

- Pendências e TODOs dos Sistemas (Use isso para saber o que "FALTA Fazer"):
{todos_content}

**RETORNO EXIGIDO EM MARKDOWN (sem cabeçalhos H1/H2 fora dos solicitados):**
Retorne APENAS:
### 📊 Índice de Esforço
- Liste 3 pontos onde ele gastou mais tempo baseado nos logs, com qualificadores (Alto/Baixo).

### 🤖 Insights Operacionais (Sintetizados)
- 3 a 4 bullet points no máximo. Fale diretamente com o usuário ("Você fez...", "Você gastou...").
- Se houve muito log em "Construção de Sistema", alerte que isso é bom para a infraestrutura, mas não pode parar as licitações.
- Seja prescritivo e confronte-o caso haja muita configuração e pouca entrega (baseado nos logs e diffs).
- Indique gargalos caso a produção econômica esteja baixa.

Não faça nenhuma saudação inicial. Entregue apenas o markdown em formatação pura a partir do "### 📊 Índice de Esforço".
'''

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        text = response.text.replace("```markdown", "").replace("```", "").strip()
        return text
    except Exception as e:
        return f"⚠️ Erro ao comunicar com a API do Gemini: {str(e)}"

def count_tasks_from_todos(todos_content: str):
    """Conta as tasks a partir do markdown de TODOs."""
    total = 0
    done = 0
    pending = 0
    for line in todos_content.splitlines():
        line_str = line.strip()
        if line_str.startswith("- [ ]") or line_str.startswith("* [ ]"):
            total += 1
            pending += 1
        elif line_str.startswith("- [x]") or line_str.startswith("* [x]"):
            total += 1
            done += 1
    return total, done, pending

def build_dia_md():
    now = datetime.now()
    score = calculate_daily_score()
    logs = get_today_log()
    git_summary = get_git_summary()
    trello_snap = get_latest_snapshot()
    todos_content = get_todos_content()
    
    # 1) Estatísticas das Tasks
    total_tasks, done_tasks, pending_tasks = count_tasks_from_todos(todos_content)
    done_pct = int((done_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    pending_pct = int((pending_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    # Quantas concluidas hoje? Vendo logs.
    concluidas_hoje = len(logs)
    
    # Montagem do Resumo
    header = f"""# ☀️ Status do Dia: {now.strftime('%d/%m/%Y')}

> **Última atualização:** {now.strftime('%H:%M')} | **Score Atual:** {score['global_score']:.0f}/100 ({score['emoji']} {score['classification']})

# 📊 Resumo do Status:

* Total de Tasks: {total_tasks}
* Concluídas: {done_tasks} ({done_pct}%)
* Pendentes: {pending_tasks} ({pending_pct}%)

Resumo dia até agora:

- {concluidas_hoje} tasks concluidas hoje
- {score['global_score']:.0f}% de esforço melhorado hoje.

## 1) 📌 TASKS EM ABERTO (Global)
"""

    # Mantendo os conteúdos do TODO (Seção 1) puros e originais exatamente como lidos
    if todos_content:
        header += "\n" + todos_content + "\n"
    else:
        header += "> *Nenhum arquivo TODO detectado nos projetos.*\n"

    # 2) Pipeline de Licitações
    import sys
    sys.path.insert(0, str(BASE_DIR / "cos" / "briefings"))
    try:
        from pipeline_report import get_pipeline_status
        pipeline = get_pipeline_status(trello_snap) if trello_snap else []
    except ImportError:
        pipeline = []
        
    total_active = sum(stage["count"] for stage in pipeline)
    header += f"\n## 2) 🏢 PIPELINE DE LICITAÇÕES: {total_active} Licitações\n\n"
    header += f"📊 PIPELINE ATIVO — {total_active} licitações\n\n"
    
    if pipeline:
        for stage in pipeline:
            lst_name = stage['list']
            # Para agradar o template ideal, injetamos a string
            pad = " " * max(1, 28 - len(lst_name))
            desc = f"({stage.get('stage', '')})" if stage.get("stage") else ""
            header += f"{stage['color']} {lst_name}{pad} {stage['count']:<3} {desc}\n"
    else:
        header += "- Operando sem dados do Trello localmente (Rode `pipeline_report.py --import-first`)\n"

    # Estatísticas Inferiores do Pipeline
    if trello_snap:
        stats = trello_snap.get("stats", {})
        cards_by_list = trello_snap.get("cards_by_list", {})
        perdidas = len(cards_by_list.get('PERDIDOS', []))
        descart= len(cards_by_list.get('DESCART', []))
        
        # Calcular vencidas
        vencidas = 0
        from pipeline_report import load_config
        config = load_config()
        for lst_cards in cards_by_list.values():
            for card in lst_cards:
                if card.get("overdue") and not card.get("closed"):
                    list_name = card.get("list", "?")
                    config_stage = config.get("pipeline_stages", {}).get(list_name, {})
                    if config_stage.get("priority", 0) > 0:
                        vencidas += 1

        header += f"─────────────────────────────\n"
        header += f"🏆 Total histórico GANHAS: {stats.get('won', 0)}\n"
        header += f"❌ PERDIDAS: {perdidas} | 🗑️ DESCART: {descart}\n"
        header += f"⚠️  HABILITAÇÕES VENCIDAS: {vencidas}\n"

    header += "\n## 3) 👁️ MONITORAMENTO E INSIGHTS (Gerado por IA)\n"
    header += "\n> *Esta seção é reescrita automaticamente pela Engine JARVIS.*\n\n"

    # Formatação do Pipeline p/ o prompt Gemini
    pipeline_info = []
    if trello_snap and "cards_by_list" in trello_snap:
        for lst, cards in trello_snap["cards_by_list"].items():
            if len(cards) > 0:
                pipeline_info.append(f"{lst}: {len(cards)} cards")
    pipeline_str = ", ".join(pipeline_info) if pipeline_info else "Nenhum dado do Trello."

    # Logs formatados
    logs_str = ""
    for idx, e in enumerate(logs):
        logs_str += f"- [{e.get('area_name', 'None')}] {e.get('action', 'None')} (impacto {e.get('impact',0)}, duração {e.get('duration_minutes',0)}m)\n"
    if not logs_str:
        logs_str = "Nenhum evento produtivo logado hoje."

    insights = generate_ai_insights(score, logs_str, git_summary, pipeline_str, todos_content)
    
    full_content = header + insights + "\n"
    
    with open(DIA_MD_PATH, "w", encoding="utf-8") as f:
        f.write(full_content)
        
    print(f"✅ Arquivo {DIA_MD_PATH.name} atualizado com sucesso!")

if __name__ == "__main__":
    print("🔄 Atualizando dia.md e consultando Gemini para os Monitoramentos...")
    build_dia_md()
