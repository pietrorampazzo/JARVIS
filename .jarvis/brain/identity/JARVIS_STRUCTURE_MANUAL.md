# 🗂️ Racional Estrutural e Organizacional: O Cérebro JARVIS (COS)

Este documento define **o que é**, **por que existe** e **para que serve** cada pasta dentro do ecossistema `JARVIS/`. O objetivo é manter o nível organizacional impecável, permitindo que a IA e o Humano saibam exatamente onde cada peça de conhecimento ou automação reside.

---

## 1. 🏛️ Raiz do Projeto (`JARVIS/`)
**Propósito:** O núcleo do ecossistema. Historicamente tinha os Markdowns soltos, mas agora **é 100% limpa**. 
- **Estrutura:** Apenas hospeda as pastas operacionais. Todos os **Documentos Mestres (Markdowns)** moram exclusivamente em `.jarvis/brain/`.

---

## ⚙️ 2. Pasta `cos/` (Cognitive Operating System)
**Propósito:** É o "motor de ação" transversal do JARVIS. Scripts, automações e registros focados na **operação do dia a dia do agente**, independente do cliente final (ARTE ou Barsi).

### 📂 `cos/briefings/`
- **Para que serve:** Scripts que geram os resumos do dia (`morning_brief.py`, `midday_check.py`). 
- **Por que esse nome:** Inspirado em reuniões de alinhamento militar/executivo (Briefings).

### 📂 `cos/config/`
- **Para que serve:** Armazena arquivos `.json` com configurações estáticas (ex: pesos do sistema de pontuação `scoring_config.json`, lista de projetos cadastrados `projects.json`).
- **Por que esse nome:** Concentra variáveis globais de configuração do sistema.

### 📂 `cos/core/`
- **Para que serve:** Lógica central do sistema nervoso do COS. Ex: O `os_core.py` ou motores de cálculo de pontuação diária. Aqui mora a "inteligência dura" local.

### 📂 `cos/engine/`
- **Para que serve:** Scripts que rodam em loop contínuo ou agendados. É o "coração batendo".
- **O Motor Autônomo:** `jarvis_daemon.py`. Este é o **Script Oficial de Background**. Você o executa em um terminal tmux/PM2 e ele fica rodando cronjobs Python (08h Briefing, 13h Check, 19h EOD, e a cada 30 min monitora logs e Evolution API).

### 📂 `cos/integrations/`
- **Para que serve:** Como o JARVIS fala com o mundo externo. 
- **Conteúdo:** `trello_client.py` (Mundo Trello), `evolution_monitor.py` (Mundo WhatsApp/Evolution), `notebooklm_client.py` (Mundo Google/RAG). 
- **Regra:** Nenhum script aqui toma decisões, eles apenas fazem as "pontes" (APIs).

### 📂 `cos/logger/` e `cos/logs/`
- **Para que servem:** O diário irrefutável do sistema. `logger/` tem o script que grava de forma estruturada, e `logs/` tem os arquivos `.json` diários (ex: `2026-02-28.json`).
- **Por que é Vital:** É olhando para os `logs/` que o JARVIS (nos Briefings) sabe o que você fez, quanto tempo levou, e calcula o "Cognitive Sync" (seu alinhamento com a missão).

---

## 🧠 3. Pasta `.jarvis/brain/` (O Cérebro Organizado)
**Propósito:** O "Cofre e Mente Central". Esta é a fonte da verdade de tudo.
- **Regra de Ouro:** NUNCA deixar arquivos soltos na raiz. Tudo segue a taxonomia abaixo.

### 📂 `brain/identity/` — Quem o JARVIS é
Documentos fundacionais que definem a alma, as regras e a arquitetura do sistema.
| Arquivo | Propósito |
|---|---|
| `COS_FOUNDATION.md` | Missão, visão e pilares estratégicos |
| `COS_MANUAL.md` | Regras globais de governança (como a IA opera) |
| `JARVIS_SOUL.md` | Personalidade, tom de voz e identidade do agente |
| `JARVIS_REGISTRY.md` | Protocolos avançados e registro de capacidades |
| `JARVIS_STRUCTURE_MANUAL.md` | Este documento. Explica a arquitetura de pastas |

### 📂 `brain/operations/` — Como o JARVIS opera
Protocolos, dashboards e tarefas ativas. Muda frequentemente.
| Arquivo | Propósito |
|---|---|
| `task.md` | Lista mestre de tarefas pendentes/concluídas |
| `MISSION_CONTROL.md` | Dashboard visual do estado do sistema |
| `daily_operational_protocol.md` | Cadência diária (08h, 13h, 19h, 30min loops) |
| `JARVIS_VIZ_KIT.md` | Padrões visuais para dashboards e gráficos |

### 📂 `brain/business/` — Verticais de Negócio
Documentos que definem as operações de cada área de negócio.
| Arquivo | Propósito |
|---|---|
| `ARTE_LIFECYCLE.md` | Ciclo de vida completo da ARTE (Editais a Empenhos) |
| `XP_BARSI.md` | CRM e inteligência financeira (Grupo Barsi/Pie.Invest) |
| `CORE_ROADMAP.md` | Roadmap visual centralizado de todos os projetos |
| `temp_strategic_goals.md` | Metas estratégicas temporárias |

### 📂 `brain/plans/` — Planos de Implementação
Documentos técnicos de "como vamos construir algo".
| Arquivo | Propósito |
|---|---|
| `implementation_plan_strategic.md` | Plano geral de fases do JARVIS |
| `implementation_plan_evolution.md` | Plano específico da integração Evolution API |

### 📂 `brain/reference/` — Tutoriais e Manuais
Documentos de consulta. Não mudam frequentemente.
| Arquivo | Propósito |
|---|---|
| `antigravity_notebook.md` | Manual de uso do Antigravity + NotebookLM |
| `notebooklm_manipulation_manual.md` | Como manipular notebooks via MCP/Selenium |

---

## 🦞 4. Integrações Isoladas (Sistemas Autônomos)

### 📂 `evolution-api/`
- **O que é:** O Gateway do WhatsApp. Anteriormente chamado de `wappi_evolution/evolution-api-lite`, foi movido para cá para estar sob jurisdição do JARVIS.
- **Por que isolado:** Ele tem seu próprio modelo (Docker, NodeJS, Prisma). Não misturamos código NodeJS pesado do WhatsApp com os scripts Python analíticos do `cos/`. Ele roda em seu canto e o JARVIS fala com ele via `cos/integrations/`.

### 📂 `openclaw/`
- **O que é:** A interface conversacional. É o aplicativo que permite a você conversar naturalmene com o JARVIS. 
- **Por que isolado:** Planejado para rodar em uma máquina secundária (StandAlone) para não consumir recursos computacionais intensos da máquina de trabalho principal.

### 📂 `.agent/` (ou Agent Skills)
- **O que é:** Pasta nativa do Antigravity (IA que codifica).
- **Conteúdo:** Aqui ficam os "Skills" (`cos_briefing`, `cos_logger`). São tutoriais que ensinam a IA as regras específicas sobre como logar algo no seu formato e como gerar um briefing para você.

---

## 🗺️ Resumo da Teoria Arquitetural
A estrutura do JARVIS foi desenhada com **Separação de Preocupações (Separation of Concerns)**:
1. **O que pensar?** Lemos os `.md` na Raiz.
2. **Como processar dados?** Usamos o `cos/`.
3. **Como falar com o WhatsApp?** Usamos `evolution-api/`.
4. **Onde lembrar eternamente?** Registramos `.json` em `cos/logs/` e upamos os `.md` pro `NotebookLM`.
