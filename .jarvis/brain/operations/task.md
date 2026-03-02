# JARVIS — Task Board por Componente

---

## 🧠 JARVIS CORE (Sistema Operacional Cognitivo)

### Fundação & Briefings
- [x] Testar `midday_check.py` e `score_engine.py`
- [x] Criar `JARVIS_SOUL.md`, `COS_FOUNDATION.md`, `JARVIS_REGISTRY.md`
- [x] Versionar tudo no NotebookLM
- [ ] Testar `morning_brief.py` (rodar às 08h)
- [ ] Integrar clima + notícias licitações ao Morning Brief
- [ ] Midday Alert automático (2h sem log)
- [ ] EOD auto-upload para JARVIS

### Motor Autônomo (Daemon)
- [x] Criar `jarvis_daemon.py` (cronjobs 08h/13h/19h/30min)
- [x] Implementar Loop de 30 min real (Análise de Logs JSON)
- [x] Implementar leitura do `projects.json` + `JARVIS/MANIFEST.md` no daemon (Task Sync)
- [x] Criar `task_sync.py` para sincronização multimanifesto

### Estrutura & Organização
- [x] Reorganizar `.jarvis/brain/` em subpastas (identity/operations/business/plans/reference)
- [x] Limpar raiz do projeto (zero arquivos soltos)
- [x] Criar `JARVIS_STRUCTURE_MANUAL.md`
- [x] Criar `projects.json` com metadados de observação

### Conversacional (OpenClaw)
- [x] Sincronizar Cérebro no OneDrive
- [ ] Configurar Pasta de Inputs (`inputs/`)
- [ ] Validar Fluxo de Conversa via Máquina B (OpenClaw)

### NotebookLM & RAG
- [ ] Dominar gestão de notebooks via MCP
- [ ] Contingência Selenium/XPath se MCP falhar
- [ ] Importar dados históricos para o RAG

---

## 🏛️ ARTE (Licitações & BI)

### Pipeline de Editais
- [ ] Script de Conferência: Trello Card <=> Pastas de Editais
- [ ] Melhorar matching em `arte_heavy_notebook.py` (meta: >85% precisão)
- [ ] Padronizar chaves JSON de metadados (snake_case controlado)
- [ ] Pipeline completo: Edital → Matching → Proposta → Envio

### Automação de Propostas
- [ ] Testar Sistema LICITEI (Robôs de Digitação e Lances)
- [ ] Automatizar Anexos/Propostas via `arte_proposta.py`
- [ ] Integrar output matching com Licitei (input automático)
- [ ] [ULTRA] Coleta Mensal de Habilitação (ARTE & PIEZZO) — Cronjob

### Pós-Pregão & Empenhos
- [ ] Fluxo de Verificação de Itens Adjudicados
- [ ] Validar Fluxo de Homologação Automática
- [ ] Motor de Extração de Empenho (E-mail -> JARVIS)
- [ ] Automatizar Fluxo: Pasta I: -> Trello -> Sheet de Pedidos
- [ ] Monitoramento de Entrega (Correios Integration)

### ATAs & B2C (Expansão)
- [ ] Corrigir Site `artecomercialbrasil.base44.app` (100% Funcional)
- [ ] Metodologia de Recebimento de Propostas por Órgãos
- [ ] Enriquecimento de Mailing (Sistema Autolearn)
- [ ] Montar 'Loginha da Arte' (E-commerce B2C)
- [ ] Integrar Logística para Venda Direta

### Dados Históricos
- [ ] Estruturar `arte_heavy_ultra.xlsx`
- [ ] Definir checklists automatizados no Trello via Agente

### Auditoria JARVIS (Padrão Sidecar)
- [x] Criar Pasta `JARVIS/` no projeto `arte_`
- [x] Padronizar `MANIFEST.md` e `audit.py` (v2.0 Health Check)
- [x] Criar `JARVIS/README.md` estratégico no projeto
- [x] Integrar logs e diffs na pasta `JARVIS/logs/`
- [ ] Instrumentar scripts críticos com chamadas de auditoria (audit_start/end)

### Longo Prazo
- [ ] Dominar API oficial do Governo Brasileiro (NotebookLM)

---

## 💬 WAPPI (WhatsApp & Evolution API)

### Infraestrutura
- [x] Migrar Evolution API Lite para `JARVIS/evolution-api/`
- [x] Criar `evolution_monitor.py` (integração Python)
- [ ] Subir servidor Evolution API (Docker ou npm start)
- [ ] Configurar Webhook global para receber mensagens

### CRM & Automação
- [ ] Implementar cadência automática de prospecção (Cron 6.1)
- [ ] Implementar broadcasts com simulação humana

---

## 💹 XP BARSI & Pie.Invest

### CRM Trello
- [x] Criar `XP_BARSI.md` (Governança)
- [ ] Modelo de Importação Excel -> Trello (Templates/Etiquetas)

### Inteligência & Monitoramento
- [ ] Monitoramento proativo: Grupo BARSI + E-mails XP
- [ ] Redirecionamento automático de oportunidades para Pie.Invest
- [ ] Trigger de Tasks: Crédito, Seguros, Dinheiro Fora

---

**Totais: 24 concluídas | 30 pendentes**
