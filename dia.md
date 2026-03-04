# ☀️ Status do Dia: 04/03/2026

> **Última atualização:** 13:01 | **Score Atual:** 24/100 (🚨 Dia Ineficiente)

# 📊 Resumo do Status:

* Total de Tasks: 86
* Concluídas: 20 (23%)
* Pendentes: 66 (76%)

Resumo dia até agora:

- 4 tasks concluidas hoje
- 24% de esforço melhorado hoje.

## 1) 📌 TASKS EM ABERTO (Global)

### 🧠 JARVIS CORE (Infraestrutura)

* Concluídas:

  * [x] Desenvolver arquitetura de memória longa otimizada para Gemini.
  * [x] Integrar todos os status da saúde do sistema no RAG Rápido.
  * [x] Gerenciar task_sync de forma distribuída.

# 🏛️ ARTE (Licitações - O Core Econômico)
> *Single Source of Truth para as pendências operacionais deste projeto.*

### 🚀 Prioridades Máximas (Workflow & Pipeline)
- [x] Matching Inteligente: Melhorar precisão do `arte_heavy_notebook.py` para >85%.
- [ ] Implementar pipeline completo e contínuo: Edital → Matching → Proposta → Licitei 
- [ ] Desenvolver Fluxo automático: Empenho -> Trello -> Planilha de Pedidos.
- [ ] Habilitação: Criar Cronjob para coleta mensal de documentos de habilitação (ARTE & PIEZZO).

### 🌍 Expansão & B2C
- [ ] Corrigir site ATA's: Catalogo bonito, Backend e Frontend unidos (artecomercialbrasil.base44.app).
- [ ] Estruturar a "Loginha da Arte" (B2C): Bling (Mercado Livre, Shopee...)

### 🧠 NotebookLM RAG (Memória & Inteligência ARTE)
- [x] Construir Fundação do NLM Client: Blindar contra quedas de sessão (Auto-Relogin) do MCP.
- [x] Construir script de Ingestão de Dados: Upload de editais e manuais da pasta DOWNLOADS.
- [x] Integrar nova arquitetura robusta no `arte_heavy_notebook.py`.

---

## 📄 arte_edital — Módulo de Ingestão (Fechar Módulo)

### Pipeline Core
- [x] Receber ZIP → deszipar recursivamente → achatar estrutura
- [x] Processar RelacaoItens → extrair itens tabelados (`_itens.xlsx`)
- [x] Identificar e renomear Termo de Referência (`termo_referencia.pdf`)
- [/] Extrair tabelas com Camelot → `_referencia.xlsx` (funcional mas instável)
- [ ] Fallback pdfplumber quando Camelot retorna 0 tabelas
- [x] Merge itens + referência → `_master.xlsx` por subpasta
- [x] Concatenar tudo → `summary.xlsx` + `master.xlsx` (filtrado por keywords)

### Qualidade & Robustez
- [x] Quality Logger: `edital_quality_logger.py` (detecta bugs por edital)
- [ ] Lidar com PDFs sem texto (OCR via `03_extracao_ocr.py`)
- [ ] Tratar tabelas desconcatenadas (itens divididos em páginas diferentes)
- [ ] Validação: garantir que nenhum item do RelacaoItens fique sem REFERENCIA no merge
- [ ] Log de taxa de completude do TR por edital (meta: >90%)
- [ ] Integrar quality logger no daemon pulse ✅ (Step 4/5)

### Gargalos Conhecidos
- [ ] Editais com formatação não-padrão (tabelas em formato livre/texto corrido)
- [ ] PDFs protegidos/scaneados (precisam OCR + limpeza)
- [ ] Colunas com nomes inconsistentes entre editais (Nº vs N vs Item)

---

## 🎯 arte_heavy — Módulo de Matching (Melhoria Contínua)

### Infraestrutura CI
- [x] Rate-limit Guard: retry automático quando resposta < 5s
- [x] Performance Tracker: `arte_perf_tracker.py` (parseia logs, detecta falsos negativos)
- [x] Métricas JSON: export automático em `arte_heavy/metrics/`
- [x] Integrar tracker no daemon pulse ✅ (Step 5/5)

### Qualidade do Matching
- [ ] Reprocessar 49 itens RATE_LIMITED da sessão de 03/03
- [ ] Melhorar instruções do notebook para matching (prompt engineering)
- [ ] Adicionar campo STATUS = "RATE_LIMITED" ao filtro de reprocessamento
- [ ] Validar conformidade jurídica (PARECER_JURIDICO_IMPUGNACAO preenchido)
- [ ] Validar conformidade técnica (JUSTIFICATIVA_TECNICA com substância)

### Evolução
- [ ] Dashboard de evolução da taxa ATENDE (tracking semanal)
- [ ] Notebook CI ARTE dedicado (alimentado pelo tracker + quality logger)
- [ ] Ajuste de PALAVRAS_CHAVE e PALAVRAS_EXCLUIR baseado em dados reais
- [ ] Threshold de preço: validar se VALOR_FINAL < VALOR_UNIT * 0.70

# Wappi - Status Completo e Roadmap (TODO)

## 📊 Resumo Executivo

O projeto Wappi (Sales Platform via WhatsApp com IA) está com a **Fase 1 (Fundação)** e **Fase 2 (CRM Kanban)** concluídas no **Frontend**. O **Backend** FastAPI (Python) ainda está no estágio inicial de scaffolding.

A integração de autenticação via **Supabase** (E-mail/Senha e OAuth Google) está implemetada no Frontend, necessitando apenas da configuração das credenciais Google no painel do Supabase.

---

## 🖥️ Frontend (React + Vite + Tailwind)

**Status:** Avançado (Fases 1 e 2 Concluídas)
**Diretório:** `/frontend_web`

### O que já está pronto [✓]

- [X] **Configuração Base:** Vite, React, React Router, TailwindCSS.
- [X] **Estrutura de Rotas e Layout:** `DashboardLayout` e `ProtectedRoute` garantindo que telas sensíveis só sejam acessadas após o login.
- [X] **Gestão de Agentes de IA (`/agents`):** Dashboard construído para o usuário ver os "empregados de IA" (status, leads conversados e taxas).
- [X] **Página de Login (`/auth`):** Componente funcional com E-mail/Senha e botão de Login com Google integrado à engine do Supabase Auth.
- [X] **Landing Page (`/`):** Visual moderno clone do Lovable App, com cor primária verde (`#1FAD53`).
- [X] **Painel de Configurações (`/settings`):** Portado do HTML estático para React (Gestão de chaves da Evolution API e OpenAI, visualização de perfil).
- [X] **CRM / Kanban Board (`/kanban`):** Pipeline interativo criado com `@hello-pangea/dnd`, colunas (New Leads, Qualifying, Negotiation, Won) com cards arrastáveis em tempo real na interface.

- [x] O que falta fazer [ ]
- [ ] Construir página de Métricas do Dashboard (`/dashboard`).
- [x] Construir página do Inbox/Caixa de Entrada (`/inbox`).
- [x] Construir página de Contatos e Grupos (`/contacts`).
- [ ] Configurar Socket.io Client para receber eventos do Backend em tempo real e atualizar o Kanban sozinhos.

---

## 🔌 Integrações Backend Pendentes (Eventos de UI)

Para dar vida ao frontend concluído, as seguintes integrações (API REST/Websockets) precisam ser ligadas aos respectivos botões/ações do usuário na interface:

**Página Autenticação (`/auth`)**
- [ ] Ligar `Acessar sua Conta` (Email/Senha) com `supabase.auth.signInWithPassword`.
- [ ] Ligar `Criar Conta` (Email/Senha) com `supabase.auth.signUp`.

**Sidebar & Base Layout**
- [ ] Dropdown de Perfil: Implementar log out (`supabase.auth.signOut`).
- [ ] Sino de Notificações: Conectar a um endpoint de avisos/alertas de erro do agente.

**Página Kanban (`/kanban`)**
- [ ] Ligar `Adicionar Lead` a um Modal para criar Lead e chamar endpoint POST `/leads`.
- [ ] Ligar botões de filtro (`Filtrar Kanban`, `Métricas Mensais`) à consultas customizadas no BD.
- [ ] Drag-and-Drop: Ao soltar um card em nova coluna, fazer requisição PUT para atualizar o `status` do lead no BD.

**Página de Agentes (`/agents`)**
- [ ] Botão Salvar (Novo/Editar Agente): Chamar endpoint POST/PUT `/agents` para salvar JSON com Configurações e Prompt.
- [ ] Botão Gerar Identidade por IA: Puxar endpoint que consuma OpenAI para retornar cor em Hex.
- [ ] Drag-and-drop de Arquivos (Base de Conhecimento): Fazer upload de documentos (PDF/Txt) para bucket do Supabase (Storage) e gerar embeddings.
- [ ] Alternador de Status (Ativar/Pausar agente): Requisição PATCH para status do banco.
- [ ] Deletar Agente: Requisição DELETE em `/agents/{id}`.

**Página do Inbox (`/inbox`)**
- [ ] Barra de busca lateral: Filtrar conversas via query param no Backend ou index search no BD.
- [ ] Cliques nas conversas: Chamar endpoint `/messages/{lead_id}` para carregar histórico real.
- [ ] Input de Mensagem de Texto & Enter/Botão Enviar: Chamar endpoint POST `/messages/send` via Evolution API, simulando como se fosse o agente (intervenção humana).
- [ ] Adicionar Anexos (Clip) e Áudio (Mic): Implementar envio de multimidia através da Evolution API.

**Página de Contatos (`/contacts`)**
- [ ] Ligar botões de Ordenação de tabela das colunas com Backend (Query Params `?sort=name&desc=true`).
- [ ] Ligar `Importar`: Disparar modal de upload de CSV para processamento Batch no servidor.
- [ ] Ligar `Criar Contato`: Modal de criação e chamada POST `/contacts`.
- [ ] Ações em Massa (Checkbox marcardos): Chamar deleção ou atualização via array de IDs.
- [ ] Dropdown `Atribuir Proprietário` e `Filtros Avançados`: Fetch em proprietários e execução de queries complexas.
- [ ] Paginação: Controlar Skip/Limit integrados com a query do backend.

**Página de Configurações (`/settings`)**
- [ ] Botões `Salvar Credenciais` (Evolution, OpenAI): Salvar/atualizar secrets em tabela segura do Supabase (ou Vault).
- [ ] Alterar plano/pagamento: Integrar com Stripe/gateway.

---

## ⚙️ Backend (FastAPI - Python)

**Status:** Inicial (Scaffolding apenas)
**Diretório:** `/backend_api` (O antigo `web_server.py` na raiz foi descontinuado em favor desta nova arquitetura).

### O que já está pronto [✓]

- [X] Estrutura inicial do FastAPI (`main.py`).
- [X] Configuração base do banco de dados SQLAlchemy (`core/database.py`).
- [X] Middleware de CORS inicial para o React.

### O que falta fazer [ ]

- [ ] **Criar Endpoints REST API:**
  - [ ] Rotas CRUD para Leads (que vão popular o Kanban do frontend ao invés de dummy data).
  - [ ] Rotas de Gestão de Agentes / Personas.
  - [ ] Rotas para salvar configurações (Chaves de API).
- [ ] **Integração Evolution API:**
  - [ ] Subir/conectar servidor Evolution API.
  - [ ] Criar Webhooks (`/webhook/v1/messages` e `/status`) no FastAPI para receber dados da Evolution.
  - [ ] Implementar broadcasts com simulação de digitação humana (delay e status "typing").
- [ ] **Integração do Motor de IA (OpenAI):**
  - [ ] Refatorar os scripts standalone de extração para dentro de serviços rodando em background (Workers).
  - [ ] Criar o loop de processamento da IA: (Recebe WhatsApp -> Classifica Intenção -> Gera Resposta baseada na Persona -> Chama Evolution API para Responder).
  - [ ] Configurar cadência automática de prospecção (Cron jobs).
- [ ] **Socket.io Server:** Instalar e configurar o `python-socketio` para empurrar eventos da Evolution API direto para a tela do React.

---

## 🔐 Pendências de Configuração (Crucial)

- [ ] **Google Auth no Supabase:**
  - Acessar Painel Supabase -> Authentication -> Providers.
  - Ativar Google (`Enable Google`).
  - Configurar `Client ID` e `Client Secret` do Google Cloud Console.
  - Salvar para o botão do frontend funcionar 100%.

### 💹 XP BARSI & Pie.Invest

* Pendentes:

  * [ ] Modelo de Importação Excel -> Trello (Templates/Etiquetas).
  * [ ] Monitoramento proativo do Grupo BARSI + E-mails da XP.
  * [ ] Gatilhos automáticos para oportunidades de Crédito e Seguros.

## 2) 🏢 PIPELINE DE LICITAÇÕES: 108 Licitações

📊 PIPELINE ATIVO — 108 licitações

🔵 Compras.Gov                  1   (prospeccao)
🟡 PREPARANDO                   9   (preparacao)
🟠 PROPOSTAS - PIEZO            10  (proposta)
🟠 PROPOSTAS - ARTE             13  (proposta)
🔴 PREGAO                       2   (disputa)
🟣 HABILITADO                   47  (habilitacao)
🟢 EMPENHO                      3   (ganho_parcial)
🟢 ENVIADO                      3   (entrega)
✅ RECEBIDO                     1   (concluido)
🏆 GANHOS - ARTE                19  (ganho_final)
─────────────────────────────
🏆 Total histórico GANHAS: 72
❌ PERDIDAS: 323 | 🗑️ DESCART: 116
⚠️  HABILITAÇÕES VENCIDAS: 86

## 3) 👁️ MONITORAMENTO E INSIGHTS (Gerado por IA)

> *Esta seção é reescrita automaticamente pela Engine JARVIS.*

### 📊 Índice de Esforço
- **Alto:** Construção da arquitetura MCP Multi-Profile para Gemini NotebookLM (180m).
- **Alto:** Integração do JARVIS Oracle (Sincronização MCP Automática) (90m).
- **Médio:** Criação do Pipeline de Ingestão Local para NotebookLM (Markdown/PDF) (60m).

### 🤖 Insights Operacionais ESTRATÉGICOS (Sintetizados)
- Seu foco em "Construção de Sistema" foi intenso, com 6 horas dedicadas à infraestrutura JARVIS/NotebookLM. Embora vital para a fundação, o Score do Dia de 23.5% sinaliza uma desconexão com o fluxo de valor imediato, resultando em um "Dia Ineficiente".
- O pipeline de Licitações está com **1 card em "Compras.Gov"**: Baixe o edital *imediatamente* para não perder o prazo. E com **9 cards em "PREPARANDO"**: Priorize o `arte_heavy_notebook.py` e o `master.xlsx` para iniciar o estudo orçamentário. Este é o seu gargalo operacional mais urgente.
- Você tem um volume expressivo de **47 cards em "HABILITADO"** aguardando contratos. Este é capital parado. Embora não seja um gargalo técnico seu, este volume representa o futuro da "Lojinha da Arte" (B2C) e merece acompanhamento ativo para acelerar o fechamento dos processos.
- As pendências em `arte_edital` (ex: OCR, tratamento de tabelas não-padrão) e `arte_heavy` (ex: reprocessar itens RATE_LIMITED, otimizar prompts) indicam que a qualidade dos seus módulos de ingestão e matching ainda exige atenção. Isso pode estar impactando diretamente a eficiência do processamento dos editais em "PREPARANDO" e deve ser atacado em conjunto com as tarefas operacionais.
- Suas inúmeras modificações não commitadas em 5 projetos (JARVIS CORE, ARTE, Wappi, Arte RWA, Binance Bot) podem indicar uma fragmentação do foco. Tente consolidar entregas em menos frentes para maximizar a sensação de progresso e a eficiência, especialmente dado o seu score diário.
