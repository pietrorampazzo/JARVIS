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
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from google import genai
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
                        todos.append(content) # sem limite rígido para preservar formatação do template
            except Exception:
                pass
                
    return "\n\n".join(todos) if todos else ""


def get_planilhas_summary() -> str:
    """Lê os arquivos master.xlsx, master_heavy.xlsx e master_heavy_ultra.xlsx e retorna um bloco markdown de sumário."""
    if not HAS_PANDAS:
        return "> ⚠️ `pandas` não instalado. Execute `pip install pandas openpyxl` para ativar este sumário.\n"

    # Configurar o path das planilhas a partir da config de projetos
    projects_config = get_config("projects")
    arte_path = None
    if projects_config:
        for proj_data in projects_config.get("projects", []):
            if "arte" in proj_data.get("id", "").lower() or "arte" in proj_data.get("name", "").lower():
                arte_path = proj_data.get("path")
                break

    if not arte_path:
        # Fallback: tentar path padrão
        arte_path = r"c:\Users\pietr\OneDrive\.vscode\arte_"

    downloads_path = Path(arte_path) / "DOWNLOADS"
    master_path = downloads_path / "master.xlsx"
    heavy_path = downloads_path / "master_heavy.xlsx"
    ultra_path = downloads_path / "master_heavy_ultra.xlsx"

    lines = []
    lines.append("\n### 📊 Inteligência de Planilhas (ARTE)\n")

    def fmt_brl(valor):
        try:
            return f"R$ {valor:_.2f}".replace("_", ".").replace(",", ",").replace(".", ",", 1) if valor < 1000 else "R$ {:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return f"R$ {valor:.2f}"

    # --- master.xlsx ---
    if master_path.exists():
        try:
            df_m = pd.read_excel(master_path)
            total_itens_m = len(df_m)
            licit_unicas_m = df_m["ARQUIVO"].nunique() if "ARQUIVO" in df_m.columns else 0
            valor_total_m = df_m["VALOR_TOTAL"].sum() if "VALOR_TOTAL" in df_m.columns else 0

            # Saldo por mês usando TIMESTAMP
            saldo_mes_str = ""
            if "TIMESTAMP" in df_m.columns:
                df_m["_dt"] = pd.to_datetime(df_m["TIMESTAMP"], errors="coerce")
                df_m["_mes"] = df_m["_dt"].dt.to_period("M")
                por_mes = df_m.groupby("_mes")["ARQUIVO"].nunique().sort_index()
                MESES_PT = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
                partes = []
                for periodo, qtd in por_mes.items():
                    nome_mes = MESES_PT.get(periodo.month, str(periodo.month))
                    partes.append(f"{nome_mes}/{str(periodo.year)[2:]}: {qtd}")
                saldo_mes_str = " · ".join(partes) if partes else "Sem datas."

            lines.append(f"**📋 master.xlsx** — `{total_itens_m}` itens | `{licit_unicas_m}` licitações | Potencial: `{fmt_brl(valor_total_m)}`")
            if saldo_mes_str:
                lines.append(f"  - Processadas por mês: {saldo_mes_str}")
        except Exception as e:
            lines.append(f"**📋 master.xlsx** — ⚠️ Erro ao ler: {e}")
    else:
        lines.append("**📋 master.xlsx** — Arquivo não encontrado.")

    # --- master_heavy.xlsx ---
    if heavy_path.exists():
        try:
            df_h = pd.read_excel(heavy_path)
            total_itens_h = len(df_h)
            licit_unicas_h = df_h["ARQUIVO"].nunique() if "ARQUIVO" in df_h.columns else 0
            valor_total_h = df_h["VALOR_TOTAL"].sum() if "VALOR_TOTAL" in df_h.columns else 0
            valor_venda_h = df_h["VALOR_FINAL"].sum() if "VALOR_FINAL" in df_h.columns else 0

            # Itens sem proposta (sem VALOR_FINAL preenchido)
            pendentes_h = 0
            if "VALOR_FINAL" in df_h.columns:
                pendentes_h = df_h["VALOR_FINAL"].isna().sum() + (df_h["VALOR_FINAL"] == 0).sum()
            elif "JUSTIFICATIVA_TECNICA" in df_h.columns:
                pendentes_h = df_h["JUSTIFICATIVA_TECNICA"].isna().sum()

            lines.append(f"**🧠 master_heavy.xlsx** — `{total_itens_h}` itens | `{licit_unicas_h}` licitações | Pendentes: `{pendentes_h}` | Potencial Edital: `{fmt_brl(valor_total_h)}` | Proposta Total: `{fmt_brl(valor_venda_h)}`")
        except Exception as e:
            lines.append(f"**🧠 master_heavy.xlsx** — ⚠️ Erro ao ler: {e}")
    else:
        lines.append("**🧠 master_heavy.xlsx** — Arquivo não encontrado.")

    # --- master_heavy_ultra.xlsx ---
    if ultra_path.exists():
        try:
            df_u = pd.read_excel(ultra_path)
            total_itens_u = len(df_u)
            licit_unicas_u = df_u["ARQUIVO"].nunique() if "ARQUIVO" in df_u.columns else 0
            valor_total_u = df_u["VALOR_TOTAL"].sum() if "VALOR_TOTAL" in df_u.columns else 0
            valor_venda_u = df_u["PRECO_VENDA"].sum() if "PRECO_VENDA" in df_u.columns else 0

            # Status de matching
            status_str = ""
            if "STATUS" in df_u.columns:
                status_counts = df_u["STATUS"].value_counts(dropna=True)
                partes_s = [f"`{s}`: {c}" for s, c in status_counts.items()]
                status_str = " · ".join(partes_s)

            lines.append(f"**⚡ master_heavy_ultra.xlsx** — `{total_itens_u}` itens | `{licit_unicas_u}` licitações | Potencial Edital: `{fmt_brl(valor_total_u)}` | Preço Venda: `{fmt_brl(valor_venda_u)}`")
            if status_str:
                lines.append(f"  - Status Matching: {status_str}")
        except Exception as e:
            lines.append(f"**⚡ master_heavy_ultra.xlsx** — ⚠️ Erro ao ler: {e}")
    else:
        lines.append("**⚡ master_heavy_ultra.xlsx** — Arquivo não encontrado.")

    return "\n".join(lines) + "\n"


def generate_ai_insights(score_data, logs_data, git_summary, pipeline_str, todos_content) -> str:
    """Consome a API do Gemini para gerar a seção 3 do dia.md."""
    if not HAS_GENAI:
        return "⚠️ Erro: `google-genai` não instalado. Instale via `pip install -U google-genai`."
        
    env = load_env()
    api_key = env.get("GEMINI_API_KEY", "")
    if not api_key:
        return "⚠️ Erro: GEMINI_API_KEY não encontrada no arquivo `.env`."
        
    client = genai.Client(api_key=api_key)
    
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

- REGRAS DE NEGÓCIO ARTE (Crucial para seus insights):
  * "Compras.Gov": A ação exigida é baixar os editais recém-descobertos.
  * "PREPARANDO": A ação exigida é fazer o estudo orçamentário via `arte_heavy_notebook.py` e verificar quantos itens orçar via `master.xlsx`.
  * "HABILITADO": Significa vitória na disputa técnica. O card fica parado aqui aguardando o envio do contrato/ATA oficial do governo. Não é gargalo. Oportunidade futura: Levar ATAs assinadas para a "Lojinha online B2C".

**RETORNO EXIGIDO EM MARKDOWN (sem cabeçalhos H1/H2 fora dos solicitados):**
Retorne APENAS:
### 📊 Índice de Esforço
- Liste 3 pontos onde ele gastou mais tempo baseado nos logs, com qualificadores (Alto/Baixo).

### 🤖 Insights Operacionais ESTRATÉGICOS (Sintetizados)
- 3 a 5 bullet points no máximo. Fale diretamente com o usuário de forma prescritiva e inteligente, como um co-piloto ("Você tem X em Preparação, rode o arte_heavy...").
- Interprete os logs vs o estado do Pipeline baseado nas REGRAS DE NEGÓCIO. Dê conselhos práticos e não genéricos. Se há cards em Compras.Gov, lembre-o de baixar os editais. Se há cards em Preparando, lembre-o da planilha master.
- Se houve muito log em "Construção de Sistema", alerte que isso é bom para a infraestrutura, mas não pode parar as licitações se o pipeline estiver carente.
- Indique onde está o fluxo de dinheiro parado no pipeline e o que fazer. Se há muitos habilitados, elogie o volume aguardando contrato B2C.

Não faça nenhuma saudação inicial. Entregue apenas o markdown em formatação pura a partir do "### 📊 Índice de Esforço".
'''

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
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
    
    # Montagem do Resumo Inicial
    summary_header = f"""# ☀️ Status do Dia: {now.strftime('%d/%m/%Y')}

> **Última atualização:** {now.strftime('%H:%M')} | **Score Atual:** {score['global_score']:.0f}/100 ({score['emoji']} {score['classification']})

# 📊 Resumo do Status:

* Total de Tasks: {total_tasks}
* Concluídas: {done_tasks} ({done_pct}%)
* Pendentes: {pending_tasks} ({pending_pct}%)

Resumo dia até agora:

- {concluidas_hoje} tasks concluidas hoje
- {score['global_score']:.0f}% de esforço melhorado hoje.
"""

    # Preparação dos dados para o Gemini (pipeline_str e logs_str)
    pipeline_info = []
    if trello_snap and "cards_by_list" in trello_snap:
        for lst, cards in trello_snap["cards_by_list"].items():
            if len(cards) > 0:
                pipeline_info.append(f"{lst}: {len(cards)} cards")
    pipeline_str = ", ".join(pipeline_info) if pipeline_info else "Nenhum dado do Trello."

    logs_str = ""
    for idx, e in enumerate(logs):
        logs_str += f"- [{e.get('area_name', 'None')}] {e.get('action', 'None')} (impacto {e.get('impact',0)}, duração {e.get('duration_minutes',0)}m)\n"
    if not logs_str:
        logs_str = "Nenhum evento produtivo logado hoje."

    # 1) Pipeline de Licitações (Visão Operacional — PRIMEIRO)
    import sys
    sys.path.insert(0, str(BASE_DIR / "cos" / "briefings"))
    try:
        from pipeline_report import get_pipeline_status
        pipeline = get_pipeline_status(trello_snap) if trello_snap else []
    except ImportError:
        pipeline = []
        
    total_active = sum(stage["count"] for stage in pipeline)
    pipeline_section = f"\n## 1) 🏢 PIPELINE DE LICITAÇÕES: {total_active} Licitações\n\n"
    pipeline_section += f"📊 PIPELINE ATIVO — {total_active} licitações\n\n"
    
    if pipeline:
        for stage in pipeline:
            lst_name = stage['list']
            pad = " " * max(1, 28 - len(lst_name))
            desc = f"({stage.get('stage', '')})" if stage.get("stage") else ""
            pipeline_section += f"{stage['color']} {lst_name}{pad} {stage['count']:<3} {desc}\n"
    else:
        pipeline_section += "- Operando sem dados do Trello localmente (Rode `pipeline_report.py --import-first`)\n"

    if trello_snap:
        stats = trello_snap.get("stats", {})
        cards_by_list = trello_snap.get("cards_by_list", {})
        perdidas = len(cards_by_list.get('PERDIDOS', []))
        descart= len(cards_by_list.get('DESCART', []))
        
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

        pipeline_section += f"─────────────────────────────\n"
        pipeline_section += f"🏆 Total histórico GANHAS: {stats.get('won', 0)}\n"
        pipeline_section += f"❌ PERDIDAS: {perdidas} | 🗑️ DESCART: {descart}\n"
        pipeline_section += f"⚠️  HABILITAÇÕES VENCIDAS: {vencidas}\n"

    # Sumário das Planilhas ARTE (logo abaixo do pipeline do Trello)
    planilhas_summary = get_planilhas_summary()
    pipeline_section += planilhas_summary

    # 2) Insights Gerados por IA (SEGUNDO — após o pipeline)
    insights_header = "\n## 2) 👁️ MONITORAMENTO E INSIGHTS (Gerado por IA)\n"
    insights_header += "\n> *Esta seção é reescrita automaticamente pela Engine JARVIS.*\n\n"
    insights_content = generate_ai_insights(score, logs_str, git_summary, pipeline_str, todos_content)

    # 3) Tasks em Aberto (Detalhamento - Final do arquivo)
    todos_section = "\n## 3) 📌 TASKS EM ABERTO (Global)\n"
    if todos_content:
        todos_section += "\n" + todos_content + "\n"
    else:
        todos_section += "> *Nenhum arquivo TODO detectado nos projetos.*\n"

    # Interpolação final: header → pipeline → insights → todos
    full_content = summary_header + pipeline_section + insights_header + insights_content + "\n" + todos_section
    
    with open(DIA_MD_PATH, "w", encoding="utf-8") as f:
        f.write(full_content)
        
    print(f"✅ Arquivo {DIA_MD_PATH.name} atualizado com sucesso!")

if __name__ == "__main__":
    print("🔄 Atualizando dia.md e consultando Gemini para os Monitoramentos...")
    build_dia_md()
