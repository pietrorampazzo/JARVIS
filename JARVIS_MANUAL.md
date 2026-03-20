# 🧠 JARVIS NEXUS: Arquitetura V4 & Manual Operacional

> *"A execução é a única métrica real da inteligência. Reduza o problema à sua física; se o processo não move a agulha, elimine-o." – Princípio de Otimização.*

Este manual documenta a topografia arquitetural e o modelo de tomada de decisões do ecossistema JARVIS após a mega-reestruturação que visou aniquilar redundâncias, reduzir latência e escalar inteligência real (Agent Swarm).

---

## 🏛️ 1. Snapshot Topográfico (O File System)

Toda a entropia foi eliminada. A raiz do JARVIS é dividida cirurgicamente em **Órgãos Funcionais**:

```text
C:\JARVIS
├── ⚙️ engine/                  # O Código (Motor)
│   ├── agents/                 # Os Soldados (I.A Pesada)
│   │   ├── __init__.py         # O "Agent Registry" Polimórfico
│   │   ├── auditor_agent.py    # O Carrasco da Quarentena (Corta Código)
│   │   └── high_performance.py # Estrategista do Trello
│   │
│   ├── core/                   # A Placa-Mãe (Infra)
│   │   ├── gateway.py          # Conector Universal com LLMs (Gemini/Claude)
│   │   ├── logger.py           # Rastreador Silencioso (Salva em vault/logs)
│   │   └── telemetry.py        # Mede tamanho de payloads e milissegundos
│   │
│   ├── mcp/                    # O Cérebro Estendido (Model Context Protocol)
│   │   ├── notebook_mcp.py     # O Servidor (Indexa vault/knowledge/)
│   │   └── mcp_gateway.py      # O Cliente (A ponte RAG/ReAct para os Agentes)
│   │
│   ├── pulse/                  # A Orquestração de Tempo
│   │   ├── maestro.py          # O Despachante Supremo
│   │   ├── router.py           # O Roteador Cognitivo (Decide quem acorda)
│   │   └── chronicle.py        # Compilador de memórias semanais
│   │
│   └── skills/                 # Os Braços (Zero Token)
│       ├── trello.py           # Lê Kanban
│       └── excel.py            # Lê pipelines
│
├── 🗄️ vault/                   # O Cofre (Dados e Memória)
│   ├── trace_log.md            # Ledger Contínuo de decisões (O Diário do Maestro)
│   ├── audit_log.md            # Ledger das Sextas-feiras
│   ├── chronicles_log.md       # Ledger de Estratégias Semanais
│   ├── telemetry.json          # Dados de milissegundos e peso
│   ├── /knowledge              # A base de PDFs e Manuais pro MCP RAG ler
│   └── /logs/                  # Eventos silenciados (`nexus_events.json`)
│
├── 🧠 prompts/                 # A Personalidade
│   ├── bilionario.md
│   ├── musk_systems.md
│   └── naval_leverage.md
│
└── 🏭 arte_comercial/          # Projeto Externo Isolado (Fábrica de Editais)
```

---

## ⚡ 2. Como Funciona a Execução Dinâmica (O Fluxo de Sangue)

O JARVIS não opera mais em linhas hardcoded. Nós abolimos o processo burocrático em favor de um **Sistema de Fila Baseado em Sensores (Roteamento Cognitivo)**.

### Passo a Passo de um Pulso (Execution Pulse):
1. **Percepção Limpa (Skills):** O `Maestro` acorda e bate no Trello e Excel via código Python nativo (`engine/skills/`). Demora menos de 1 segundo. Ele percebe o estado do tabuleiro.
2. **A Matriz do Swarm (Router):** O Maestro envia a situação bruta (ex: "Quantos clientes na XP?", "Que dia da semana é hoje?") para o arquivo `engine/pulse/router.py`. 
3. **Dispatch (Roteador Cognitivo):** O `router` avalia as condições baseadas em regras eficientes e decide: *"Hoje é sexta, acordem o HighPerformance e o Auditor"*. Ele joga a string `["HIGH_PERFORMANCE", "AUDITOR"]` de volta.
4. **Acionamento Polimórfico:** O Maestro varre a lista, busca os nomes dentro de `engine/agents/__init__.py` e dispara a função única `.process()` de cada um deles. Se você plugar mais 50 Agentes no código amanhã, o Maestro não precisa ser alterado em uma vírgula.
5. **O Append Contínuo:** Nenhum mili-arquivo de snapshot é criado (Adeus caos de `.json`). A resposta dos Agentes é costurada na parte de baixo do Livro-Razão Único: `vault/trace_log.md`.

---

## 📚 3. O Cérebro MCP (A Máquina de RAG)

A conquista suprema de economia e precisão é a infraestrutura MCP.

Se um agente precisa responder algo complexo (Ex: "Limites da API X" ou "Regras de Ouro de Negociação"):
1. O Agente é forçado via *Prompt Engineering* a seguir o **Protocolo ReAct**. Ao invés de alucinar ou pedir as regras no terminal, ele devolve invisivelmente um bloco de JSON pedindo para usar o MCP.
2. O `mcp_gateway.py` engole o JSON e avisa ao Servidor: *"Ei NotebookMCP, ache o arquivo `api_mock.md` e devolva a linha de limites"*.
3. O servidor (que vigia a pasta `vault/knowledge/`) cata o documento na força bruta e cospe de volta para a IA.
4. A IA lê e formula a síntese matadora no log. 

---

## 💀 4. O Sistema Imunológico (Quarentena AST)

O `AuditorAgent` opera um regime de checagem contra entropia: toda sexta-feira ele lê todos os arquivos `.py`. 
Para não ser destrutivo e apagar coisas úteis que ainda estão sendo construídas (Falsos Mortos), programamos uma **Consciência Temporal (AST Grace Period)**. Qualquer arquivo tocado ou alterado há menos de 3 dias é imune à Navalha. O resto, se não tem uso interligado, é marcado pra abate.
