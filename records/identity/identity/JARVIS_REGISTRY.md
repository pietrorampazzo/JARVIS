# JARVIS REGISTRY — Mapa de Identidades do Sistema
> **Versão:** 1.0 | **Última atualização:** 2026-02-27  
> **Propósito:** Fonte única de verdade sobre todos os módulos, identidades e integrações do JARVIS COS.  
> Consulte este arquivo antes de criar novos módulos ou modificar existentes.

---

## 🗺️ VISÃO GERAL DA ARQUITETURA

```
JARVIS/
│
├── 📋 COS_FOUNDATION.md       ← Missão, pesos, regras de governança
├── 🧠 JARVIS_SOUL.md          ← Constituição do agente (personalidade + protocolo)
├── 📖 JARVIS_REGISTRY.md      ← ESTE ARQUIVO — mapa de identidades
│
├── cos/
│   ├── core/                  ← Módulo Central (Caminhos, Configs, Logs)
│   ├── config/                ← Configurações (áreas, regras, limiares, Trello)
│   ├── logger/                ← Registro append-only de eventos
│   ├── engine/                ← Cálculo de score, governança, previsão, sentinel
│   ├── briefings/             ← Relatórios por janela horária + pipeline
│   ├── integrations/          ← Trello API, NotebookLM
│   └── logs/                  ← YYYY-MM-DD.json (dados reais)
│
└── .agent/
    ├── skills/                ← cos_briefing, cos_logger
    └── workflows/             ← daily_briefing, log_project_activity
```

---

## 🧩 IDENTIDADES — MÓDULOS DO SISTEMA

### 1. CORE SHARED (Central de Utilidades)
| Campo | Valor |
|---|---|
| **ID** | `core_shared` |
| **Arquivo** | `cos/core/shared.py` |
| **Função** | Centraliza caminhos (BASE_DIR), carregamento de JSON/Log/Env e codificação UTF-8 |
| **Exportações** | `get_config`, `get_today_log`, `get_latest_snapshot`, `load_env` |
| **Quem chama** | Quase todos os scripts (unificação de lógica) |

---

### 2. EVENT LOGGER
| Campo | Valor |
|---|---|
| **ID** | `event_logger` |
| **Arquivo** | `cos/logger/event_logger.py` |
| **Função** | Registra eventos produtivos em JSON append-only |
| **Input** | `--area`, `--category`, `--action`, `--impact` (1-5), `--duration`, `--project` |
| **Output** | `cos/logs/YYYY-MM-DD.json` |
| **Dependências** | `core_shared` |
| **Quem chama** | Skills `cos_logger`, workflows, agent manual |

---

### 3. SCORE ENGINE
| Campo | Valor |
|---|---|
| **ID** | `score_engine` |
| **Arquivo** | `cos/engine/score_engine.py` |
| **Função** | Calcula score diário por área (0–100) e global ponderado |
| **Dependências** | `core_shared`, logs do dia |
| **Quem chama** | `governance_rules`, `morning_brief`, `midday_check`, `eod_audit` |

---

### 4. PIPELINE SENTINEL (Vigília de Licitações)
| Campo | Valor |
|---|---|
| **ID** | `pipeline_sentinel` |
| **Arquivo** | `cos/engine/pipeline_sentinel.py` |
| **Função** | Analisa gargalos estruturais no Trello (ex: Habilitações paradas, datas vencidas) |
| **Identificadores** | `SENTINEL-BOTTLENECK`, `SENTINEL-RISK` |
| **Dependências** | `core_shared`, último snapshot Trello |
| **Quem chama** | `governance_rules`, `pipeline_report` |

---

### 5. GOVERNANCE ENGINE (O Governador)
| Campo | Valor |
|---|---|
| **ID** | `governance_rules` |
| **Arquivo** | `cos/engine/governance_rules.py` |
| **Função** | O cérebro de decisão. Consolida Score + Predição + Sentinel para agir |
| **Regras ativas** | RULE-001, RULE-002, SENTINEL-*, PREDICTIVE-* |
| **Dependências** | `score_engine`, `predictive_engine`, `pipeline_sentinel` |
| **Quem chama** | Todos os briefings (Morning, Midday, EOD) |

---

### 6. PREDICTIVE ENGINE (O Analista)
| Campo | Valor |
|---|---|
| **ID** | `predictive_engine` |
| **Arquivo** | `cos/engine/predictive_engine.py` |
| **Função** | Analisa tendências dos últimos N dias e gera alertas preditivos |
| **Dependências** | `score_engine`, `core_shared` |
| **Quem chama** | `governance_rules`, briefings |

---

### 7. MORNING BRIEFING
| Campo | Valor |
|---|---|
| **ID** | `morning_brief` |
| **Arquivo** | `cos/briefings/morning_brief.py` |
| **Janela** | 08:00 |
| **Função** | Directive do dia baseado em predições e estado de governança |
| **Dependências** | `governance_rules`, `predictive_engine` |

---

### 8. MIDDAY CHECK
| Campo | Valor |
|---|---|
| **ID** | `midday_check` |
| **Arquivo** | `cos/briefings/midday_check.py` |
| **Janela** | 13:00 |
| **Função** | Enforcement suave: ajuste de curso no meio do dia |
| **Dependências** | `governance_rules` |

---

### 9. EOD AUDIT
| Campo | Valor |
|---|---|
| **ID** | `eod_audit` |
| **Arquivo** | `cos/briefings/eod_audit.py` |
| **Janela** | 19:00 |
| **Função** | Auditoria final do dia + exportação/versionamento |
| **Dependências** | `governance_rules`, `pipeline_report` |

---

### 10. PIPELINE REPORT
| Campo | Valor |
|---|---|
| **ID** | `pipeline_report` |
| **Arquivo** | `cos/briefings/pipeline_report.py` |
| **Função** | Visão visual das movimentações do dia no Trello |

---

### 11. PROJECT SENTINEL (Vigília de Desenvolvimento)
| Campo | Valor |
|---|---|
| **ID** | `project_sentinel` |
| **Arquivo** | `cos/integrations/project_analyzer.py` |
| **Função** | Monitora atividade Git e maturidade de docs em projetos registrados |
| **Config** | `cos/config/projects.json` |
| **Dependências** | `core_shared`, Git CLI |
| **Quem chama** | `governance_rules`, briefings |

---

### 12. TRELLO & BOARD OPERATIONS
| Identidade | Arquivo | Função |
|---|---|---|
| `trello_client` | `cos/integrations/trello_client.py` | API básica e Sync sugerido |
| `board_import` | `cos/integrations/board_import.py` | Snapshot JSON estruturado |
| `notebook_manual` | `notebooklm_manipulation_manual.md` | Guia de 29 habilidades e fluxos I/O RAG |


---

## 📊 IDENTIDADES — ÁREAS COS

| ID | Nome | Peso | O que conta |
|---|---|---|---|
| `economic_output` | Output Econômico | **35%** | Licitações, propostas, receita, pipeline |
| `system_building` | Construção de Sistema | **25%** | Automação, scripts, bugs, features |
| `execution_discipline` | Execução & Disciplina | **20%** | Tarefas fechadas, plano cumprido |
| `energy_body` | Energia & Corpo | **10%** | Sono, treino, alimentação |
| `relations_influence` | Relações & Influência | **10%** | Follow-ups, conteúdo, networking |

---

## 🗂️ IDENTIDADES — PIPELINE TRELLO (Arte Comercial)

| Lista | Stage | Prioridade | Mapeado → COS |
|---|---|---|---|
| `Compras.Gov` | prospeccao | 🔵 1 | `economic_output` · impacto 2 |
| `PREPARANDO` | preparacao | 🟡 2 | `economic_output` · impacto 3 |
| `PROPOSTAS - PIEZO` | proposta | 🟠 3 | `economic_output` · impacto 4 |
| `PROPOSTAS - ARTE` | proposta | 🟠 3 | `economic_output` · impacto 4 |
| `PREGAO` | disputa | 🔴 4 | `economic_output` · impacto 4 |
| `HABILITADO` | habilitacao | 🟣 5 | `economic_output` · impacto 4 |
| `EMPENHO` | ganho_parcial | 🟢 6 | `economic_output` · impacto 5 |
| `ENVIADO` | entrega | 🟢 7 | `economic_output` · impacto 4 |
| `RECEBIDO` | concluido | ✅ 8 | `economic_output` · impacto 5 |
| `GANHOS - ARTE` | ganho_final | 🏆 8 | `economic_output` · impacto 5 |
| `PERDIDOS` | perdido | ❌ — | Não mapeado (histórico) |
| `DESCART` | descartado | 🗑️ — | Não mapeado (histórico) |
| `DADOS` | referencia | 📋 — | Não mapeado |

**Board ativo:** `Arte Comercial` · ID: `68569b7191cc868682152923`

---

## 🔌 IDENTIDADES — INTEGRAÇÕES

| ID | Serviço | Status | Config |
|---|---|---|---|
| `trello` | Trello REST API | ✅ Ativo | `cos/config/.env` |
| `notebooklm` | NotebookLM MCP | ✅ Ativo | MCP via Antigravity |
| `gemini` | Google Gemini API | 🔲 Planejado | `GEMINI_API_KEY` no `.env` |
| `openrouter` | Open Router (LLMs) | 🔲 Planejado | `OPENROUTER_API_KEY` no `.env` |
| `railway` | Agent deployment | 🔲 Fase 5 | — |

**NotebookLM JARVIS:** `https://notebooklm.google.com/notebook/2592b46f-b4bd-495c-9255-f09271e99b8b`

---

## 🧠 PROTOCOLOS DE INTELIGÊNCIA AVANÇADA (NotebookLM MCP)

O JARVIS utiliza o AntiGravity como ponte para transformar o NotebookLM em um banco de dados **RAG (Retrieval-Augmented Generation) Persistente**.

### 1. Funcionalidades de Integração
- **29 Habilidades MCP**: Desbloqueio de funções nativas para manipular notebooks, seções e fontes programaticamente.
- **Autenticação Persistente**: Renovação automática de tokens para uso contínuo sem interrupção humana.

### 2. Adição Programática de Fontes (Deep Research)
- **Injeção em Massa**: O JARVIS pode povoar notebooks via comandos de IA, realizando pesquisas profundas e injetando dezenas de fontes (ex: 50+ recursos) simultaneamente.
- **Micro-Notebooks**: Capacidade de gerar notebooks específicos sobre subtemas (ex: "Metodologia de Matching Jurídico") e preenchê-los de forma autônoma.

### 3. Personal Intelligence (Dados Privados)
- **Google Drive**: Busca e indexação automática de arquivos estratégicos, editais e planos de negócios.
- **Zapier MCP**: Extração de inteligência de e-mails (leads) e calendários diretamente para a memória de longo prazo.

### 4. Vantagem RAG
- **Eficiência de Contexto**: O sistema consulta milhares de fontes sem estourar o limite de tokens, puxando apenas o dado exato para a tarefa.
- **Persistence**: Logs de bugs, docs de software e briefings diários são salvos perenemente.

---

## ⚙️ IDENTIDADES — CONFIGS

| Arquivo | Propósito | Editável |
|---|---|---|
| `cos/config/areas.json` | Áreas, pesos, indicadores | ✅ Sim |
| `cos/config/rules.json` | Templates de regras de governança | ✅ Sim |
| `cos/config/thresholds.json` | Limiares de classificação de score | ✅ Sim |
| `cos/config/trello_config.json` | Mapeamento listas Trello → COS | ✅ Sim |
| `cos/config/projects.json` | Lista de projetos para monitoramento | ✅ Sim |
| `cos/config/.env` | Credenciais (Trello, APIs) | ✅ Sim (nunca commitar) |
| `cos/config/.env.example` | Template de credenciais | 📖 Referência |

---

## 🧰 IDENTIDADES — SKILLS & WORKFLOWS

| ID | Tipo | Arquivo | Quando usar |
|---|---|---|---|
| `cos_briefing` | Skill | `.agent/skills/cos_briefing/SKILL.md` | Início de sessão, checkpoints |
| `cos_logger` | Skill | `.agent/skills/cos_logger/SKILL.md` | Após qualquer tarefa concluída |
| `daily_briefing` | Workflow | `.agent/workflows/daily_briefing.md` | Briefing + Pipeline Report diário |
| `log_project_activity` | Workflow | `.agent/workflows/log_project_activity.md` | Logar atividade produtiva |

---

## 📐 PADRÕES DE DESENVOLVIMENTO

### Criar um novo módulo
1. Crie o arquivo em `cos/<subsistema>/nome_modulo.py`
2. Adicione `sys.stdout.reconfigure(encoding='utf-8')` logo após os imports
3. Registre aqui no JARVIS_REGISTRY.md (copia um bloco acima)
4. Docstring + argparse CLI (`--help` funcional)
5. Adicione ao workflow relevante em `.agent/workflows/`

### Criar uma nova área COS
1. Edite `cos/config/areas.json` (soma de pesos deve ser 1.0)
2. Atualize a tabela de Áreas neste arquivo
3. Documente casos de uso em `COS_FOUNDATION.md`

### Criar uma nova integração
1. Crie `cos/integrations/nome_integracao.py`
2. Adicione variáveis no `cos/config/.env` e `.env.example`
3. Registre na tabela de Integrações acima
4. Atualize `JARVIS_SOUL.md` (seção Integrações Ativas)

### Criar um novo board Trello
1. Adicione o Board ID no `.env` como `TRELLO_BOARD_ID_NOME=<id>`
2. Crie `cos/config/trello_config_nome.json` com mapeamento de listas
3. Adicione entrada no `board_import.py` e `pipeline_report.py`
4. Registre na tabela de Pipeline acima

---

*JARVIS_REGISTRY.md — Consulte antes de criar. Atualize depois de modificar.*
