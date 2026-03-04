"""
JARVIS Oracle Sync v2.0
Gerencia a comunicação bidirecional com o Oráculo (NotebookLM Pessoal).
- upload_eod_report(): Envia o dia.md consolidado como fonte de conhecimento.
- ask_oracle(): Consulta o Oráculo pedindo diagnóstico e direcionamento.
- populate_primordial(): Envia os dados fundacionais do JARVIS.
- set_instructions(): Define as instruções nativas do Notebook.
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent
DIA_MD_PATH = BASE_DIR / "dia.md"
ARTE_DIR = BASE_DIR.parent / "arte_"
PRIMORDIAL_DIR = BASE_DIR / "tmp_notebook_uploads"

# Add ARTE to path to use NLMClient
sys.path.insert(0, str(ARTE_DIR))

try:
    from arte_notebooks.core.nlm_client import NLMClient
    HAS_NLM = True
except ImportError:
    HAS_NLM = False

# ══════════════════════════════════════════════
# CONFIGURAÇÃO DO ORÁCULO
# ══════════════════════════════════════════════
ORACLE_PROFILE = "pessoal"
ORACLE_NOTEBOOK_ID = "2592b46f-b4bd-495c-9255-f09271e99b8b"

ORACLE_INSTRUCTIONS = """Você é a Mente Arquitetural do JARVIS, o Sistema Operacional Cognitivo.
Sua função não é gerar código imediato, mas atuar como o CTO / Otimizador Supremo da nossa infraestrutura ("Oráculo").

Sua base de conhecimento contém:
1. Nossas métricas de performance (Pontuações de hora em hora).
2. Os logs de erros recorrentes de nossas abstrações (ARTE, OpenClaw, Wappi).
3. Nossas diretrizes de sistema (JARVIS SOUL, REGISTRY, Strategic Goals).

DIRETRIZES DE RESPOSTA:
- Sempre que questionado sobre otimização, procure o GARGALO RECORRENTE nas anotações (ex: "Vi que o erro de Selenium ocorreu 5 vezes semana passada").
- Proponha Refatorações, delegações de processos em background ou ferramentas mais ágeis.
- Analise as travas e sugira a criação de SUB-AGENTES autônomos e especializados que possam atuar na raiz dos nossos problemas cotidianos (ex: "Sugiro criar um Agente de Retry para a Evolution API focado nos Timeouts do Wappi").
- Conecte problemas parecidos do passado com as travas do presente.
- Mantenha o tom pragmático, consultivo, focado em "Ganho de Escala" (Otimizar ARTE, Wappi, OpenClaw, Investimentos e outros projetos pessoais que vierem aparecer).
- Sempre justifique com métricas dos nossos arquivos base.
- Responda SEMPRE em PT-BR."""


def _get_client():
    """Cria e retorna um NLMClient conectado ao perfil do Oráculo."""
    if not HAS_NLM:
        print("❌ [ORACLE] NLMClient não encontrado. Abortando.")
        return None
    try:
        return NLMClient(profile=ORACLE_PROFILE, auto_connect=True)
    except Exception as e:
        print(f"❌ [ORACLE] Falha ao conectar MCP: {e}")
        return None


def set_instructions():
    """Define as instruções nativas do Notebook Oracle."""
    client = _get_client()
    if not client:
        return

    print("📜 [ORACLE] Definindo instruções do Notebook...")
    payload = {
        "name": "notebook_set_instructions",
        "arguments": {
            "notebook_id": ORACLE_NOTEBOOK_ID,
            "instructions": ORACLE_INSTRUCTIONS
        }
    }
    try:
        resp = client._send_request("tools/call", payload)
        if resp.get('result', {}).get('isError'):
            print(f"❌ [ORACLE] Erro: {resp['result']}")
        else:
            print("✅ [ORACLE] Instruções injetadas com sucesso!")
    except Exception as e:
        print(f"❌ [ORACLE] Falha: {e}")
    finally:
        client.close()


def populate_primordial():
    """Envia os dados fundacionais (SOUL, REGISTRY, Goals) para o Notebook."""
    client = _get_client()
    if not client:
        return

    if not PRIMORDIAL_DIR.exists():
        print(f"❌ [ORACLE] Diretório primordial não encontrado: {PRIMORDIAL_DIR}")
        client.close()
        return

    files = list(PRIMORDIAL_DIR.glob("*.md"))
    print(f"📡 [ORACLE] Enviando {len(files)} fontes primordiais...")

    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                text = f.read()
            payload = {
                "name": "notebook_add_text",
                "arguments": {
                    "notebook_id": ORACLE_NOTEBOOK_ID,
                    "title": fp.name,
                    "text": text
                }
            }
            resp = client._send_request("tools/call", payload)
            if resp.get('result', {}).get('isError'):
                print(f"   ❌ {fp.name}: {resp['result']}")
            else:
                print(f"   ✅ {fp.name}")
            time.sleep(2)
        except Exception as e:
            print(f"   ❌ {fp.name}: {e}")

    client.close()
    print("✅ [ORACLE] População primordial concluída!")


def upload_eod_report():
    """Lê o dia.md e faz o upload pro JARVIS Notebook (Oráculo) via MCP."""
    client = _get_client()
    if not client:
        return

    if not DIA_MD_PATH.exists():
        print(f"❌ [ORACLE] Arquivo {DIA_MD_PATH} inexistente.")
        client.close()
        return

    try:
        with open(DIA_MD_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        today_str = datetime.now().strftime("%Y_%m_%d")
        title = f"JARVIS_Pulse_Relatorio_{today_str}.md"

        payload = {
            "name": "notebook_add_text",
            "arguments": {
                "notebook_id": ORACLE_NOTEBOOK_ID,
                "title": title,
                "text": content
            }
        }

        print(f"📡 [ORACLE] Enviando métricas do dia [{title}]...")
        resp = client._send_request("tools/call", payload)

        if resp.get('result', {}).get('isError'):
            print(f"❌ [ORACLE] Erro ao enviar: {resp['result']}")
        else:
            print(f"✅ [ORACLE] Dia consolidado enviado para Memória Longa.")

    except Exception as e:
        print(f"❌ [ORACLE] Falha: {e}")
    finally:
        client.close()


def ask_oracle(query: str = None) -> str:
    """Consulta o Oráculo pedindo diagnóstico e orientação."""
    client = _get_client()
    if not client:
        return "❌ Sem conexão com o Oráculo."

    if not query:
        query = (
            "Com base em todos os relatórios diários e logs do JARVIS que você possui, "
            "faça um diagnóstico completo da minha operação: "
            "1) Quais são os 3 maiores gargalos recorrentes? "
            "2) Existem padrões de erro que se repetem? "
            "3) Sugira 2 Sub-Agentes autônomos que eu deveria criar para resolver problemas recorrentes. "
            "4) Qual deve ser minha prioridade absoluta amanhã para maximizar Output Econômico? "
            "Seja direto, pragmático e use dados dos relatórios."
        )

    payload = {
        "name": "notebook_query",
        "arguments": {
            "notebook_id": ORACLE_NOTEBOOK_ID,
            "query": query
        }
    }

    try:
        print(f"🔮 [ORACLE] Consultando o Oráculo...")
        resp = client._send_request("tools/call", payload)
        content = resp.get('result', {}).get('content', [{}])
        if content:
            answer = content[0].get('text', 'Sem resposta.')
            try:
                parsed = json.loads(answer)
                return parsed.get("answer", answer)
            except (json.JSONDecodeError, TypeError):
                return answer
        return "Sem resposta do Oráculo."
    except Exception as e:
        return f"❌ Falha ao consultar: {e}"
    finally:
        client.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="JARVIS Oracle Sync")
    parser.add_argument("--populate", action="store_true", help="Envia dados primordiais")
    parser.add_argument("--instructions", action="store_true", help="Define instruções do Notebook")
    parser.add_argument("--upload", action="store_true", help="Envia dia.md atual")
    parser.add_argument("--ask", type=str, nargs="?", const="default", help="Consulta o Oráculo")
    args = parser.parse_args()

    if args.populate:
        populate_primordial()
    elif args.instructions:
        set_instructions()
    elif args.upload:
        upload_eod_report()
    elif args.ask:
        q = None if args.ask == "default" else args.ask
        print(ask_oracle(q))
    else:
        parser.print_help()
