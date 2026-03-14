# COS MANUAL — Cognitive Operating System
> **Versão:** 1.0 | **Data:** 2026-02-27

---

## 🎯 O Que É o COS

O COS é o seu **sistema de governança pessoal** integrado ao Antigravity. Ele:
- Registra cada atividade produtiva em JSON (Event Logger)
- Calcula score diário por área e global (Score Engine)
- Detecta tendências e antecipa problemas (Predictive Engine)
- Aplica regras de confronto baseadas em dados (Governance Engine)
- Entrega briefings às 08h, 13h e 19h
- Sobe relatórios para o notebook **JARVIS** no NotebookLM

---

## 📁 Estrutura de Pastas

```
JARVIS/
├── COS_FOUNDATION.md          ← Documento base de toda a arquitetura
├── COS_MANUAL.md              ← Este arquivo
├── cos/
│   ├── config/
│   │   ├── areas.json         ← 5 áreas + pesos
│   │   ├── rules.json         ← Regras de governança
│   │   └── thresholds.json    ← Limiares de score
│   ├── logger/
│   │   └── event_logger.py    ← 📌 USE ESTE para logar atividades
│   ├── engine/
│   │   ├── score_engine.py    ← Calcula score diário
│   │   ├── predictive_engine.py ← Analisa tendências
│   │   └── governance_rules.py  ← Aplica regras + confronto
│   ├── briefings/
│   │   ├── morning_brief.py   ← 08:00
│   │   ├── midday_check.py    ← 13:00
│   │   └── eod_audit.py       ← 19:00
│   ├── integrations/
│   │   └── notebooklm_client.py ← Upload para JARVIS
│   └── logs/
│       └── YYYY-MM-DD.json    ← Logs diários (auto-gerados)
└── .agent/
    ├── skills/
    │   ├── cos_logger/        ← Skill de log automático
    │   └── cos_briefing/      ← Skill de geração de briefing
    └── workflows/
        ├── daily_briefing.md
        └── log_project_activity.md
```

---

## 🚀 Guia de Início Rápido

### 1. Verificar que Python está disponível
```powershell
python --version
```

### 2. Registrar seu primeiro evento
```powershell
cd "c:\Users\pietr\OneDrive\.vscode\JARVIS"

python cos\logger\event_logger.py `
  --area system_building `
  --category dev `
  --action "Configurei o COS pela primeira vez" `
  --impact 5 `
  --duration 60
```

### 3. Ver o score do dia
```powershell
python cos\engine\score_engine.py
```

### 4. Gerar morning briefing
```powershell
python cos\briefings\morning_brief.py
```

---

## 📋 Comandos Principais

### Event Logger (mais usado)

| Comando | Descrição |
|---------|-----------|
| `python cos\logger\event_logger.py --area <id> --action "<texto>" --impact <1-5>` | Loga evento |
| `python cos\logger\event_logger.py --list` | Lista eventos de hoje |
| `python cos\logger\event_logger.py --summary` | Resumo JSON do dia |

**IDs de Área:**
```
economic_output       → Licitações, pipeline, receita
system_building       → Scripts, automação, bugs
execution_discipline  → Tarefas, plano, disciplina
energy_body           → Saúde, academia, organização
relations_influence   → Clientes, networking, conteúdo
```

### Engines

| Comando | Descrição |
|---------|-----------|
| `python cos\engine\score_engine.py` | Score completo do dia |
| `python cos\engine\score_engine.py --date 2026-02-26` | Score de data específica |
| `python cos\engine\predictive_engine.py --days 7` | Análise preditiva 7 dias |
| `python cos\engine\governance_rules.py` | Intervenções ativas agora |

### Briefings

| Comando | Descrição |
|---------|-----------|
| `python cos\briefings\morning_brief.py` | Morning Brief (salva em output/) |
| `python cos\briefings\midday_check.py` | Midday Check |
| `python cos\briefings\eod_audit.py --save` | EOD Audit + salva .md |

### NotebookLM JARVIS

| Comando | Descrição |
|---------|-----------|
| `python cos\integrations\notebooklm_client.py --upload-log today` | Prepara log do dia para JARVIS |
| `python cos\integrations\notebooklm_client.py --upload-brief <path>` | Prepara briefing para JARVIS |

---

## ⏰ Configurando Cronjobs (Windows Task Scheduler)

### Método 1 — PowerShell Script único

Crie o arquivo `cos\run_briefing.ps1`:

```powershell
# Seleciona briefing pelo horário
$hour = (Get-Date).Hour
$basePath = "c:\Users\pietr\OneDrive\.vscode\JARVIS"

if ($hour -lt 11) {
    python "$basePath\cos\briefings\morning_brief.py" --save
} elseif ($hour -lt 17) {
    python "$basePath\cos\briefings\midday_check.py"
} else {
    python "$basePath\cos\briefings\eod_audit.py" --save
}
```

### Método 2 — Configurar no Task Scheduler

**Abrir Task Scheduler:**
```
Win+R → taskschd.msc → Enter
```

**Criar Tarefa: Morning Brief**
1. Click "Create Basic Task"
2. Name: `COS Morning Brief`
3. Trigger: Daily, 08:00
4. Action: Start a Program
   - Program: `powershell`
   - Arguments: `-ExecutionPolicy Bypass -File "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\run_briefing.ps1"`

**Criar Tarefa: Midday Check**
- Repetir acima com horário 13:00
- Name: `COS Midday Check`

**Criar Tarefa: EOD Audit**
- Repetir acima com horário 19:00
- Name: `COS EOD Audit`

### Método 3 — Criar todas via PowerShell

```powershell
# Executar como Administrador
$psScript = "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\run_briefing.ps1"

# Morning Brief - 08:00
$action = New-ScheduledTaskAction -Execute "powershell" -Argument "-ExecutionPolicy Bypass -File `"$psScript`""
$trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
Register-ScheduledTask -TaskName "COS Morning Brief" -Action $action -Trigger $trigger -RunLevel Highest

# Midday Check - 13:00
$trigger2 = New-ScheduledTaskTrigger -Daily -At "13:00"
Register-ScheduledTask -TaskName "COS Midday Check" -Action $action -Trigger $trigger2 -RunLevel Highest

# EOD Audit - 19:00
$trigger3 = New-ScheduledTaskTrigger -Daily -At "19:00"
Register-ScheduledTask -TaskName "COS EOD Audit" -Action $action -Trigger $trigger3 -RunLevel Highest

Write-Host "✅ 3 tarefas agendadas com sucesso!"
```

---

## 🤝 Uso com o ClawdBot (Rascunho Colaborativo)

### Sessão Diária Ideal

```
08:00  → Task Scheduler roda morning_brief.py automaticamente
         → Você abre o Antigravity/ClawdBot
         → Revisou o briefing? Use /daily_briefing

Durante o dia:
         → A cada tarefa concluída: use /log_project_activity
         → Qualquer momento: "Mostra meu score atual"

13:00  → Midday check automático via Task Scheduler
         → ClawdBot detecta desvios e te chama

19:00  → EOD Audit automático
         → Upload para JARVIS via notebooklm_client.py
```

### Comandos Rápidos no ClawdBot

```
/daily_briefing           → Gera briefing do horário atual
/log_project_activity     → Loga atividade concluída
```

Ou em linguagem natural:
```
"Analisou o score de hoje"
"Logar que finalizei o script X com 45 minutos"
"O que está crítico no meu COS?"
"Análise preditiva dos últimos 7 dias"
```

---

## 🧠 Integração com NotebookLM (JARVIS)

O notebook **JARVIS** é a memória de longo prazo do COS.

### Seções do Notebook JARVIS

| Seção | Conteúdo | Frequência de Update |
|-------|----------|---------------------|
| `JARVIS_FOUNDATION` | COS_FOUNDATION.md | 1x (ou ao revisar) |
| `JARVIS_DAILY_LOGS` | Briefings + scores diários | Diário (via eod --save) |
| `JARVIS_PROJECT_LOGS` | Atividades por projeto | Ao concluir projetos |
| `JARVIS_SKILLS` | Skills criadas documentadas | Ao criar novas skills |
| `JARVIS_DECISIONS` | Decisões arquiteturais | Ao tomar decisões importantes |
| `JARVIS_WEEKLY` | Review semanal de performance | Toda segunda-feira |

### Como Adicionar ao JARVIS (via MCP)

1. O Antigravity tem acesso ao MCP do NotebookLM
2. Após gerar um briefing com `--save`, o arquivo fica em `cos/briefings/output/`
3. Use o comando no chat: *"Faz upload deste briefing para o notebook JARVIS"*
4. O agente usa `add_source_text` via MCP automaticamente

---

## 📊 Exemplos de Eventos para Logar

### Desenvolvimento
```powershell
# Script criado
python cos\logger\event_logger.py --area system_building --category dev --action "Criou automação de download editais" --impact 5 --duration 90 --project "licitacoes"

# Bug resolvido
python cos\logger\event_logger.py --area system_building --category dev --action "Corrigiu erro de encoding no MCP" --impact 4 --duration 30 --project "JARVIS"
```

### Licitações
```powershell
# Edital analisado
python cos\logger\event_logger.py --area economic_output --category licitacao --action "Analisou edital SECOM n.123/2026" --impact 4 --duration 45 --project "licitacoes"

# Proposta enviada
python cos\logger\event_logger.py --area economic_output --category licitacao --action "Enviou proposta ARP Ministério X" --impact 5 --duration 120 --project "licitacoes"
```

### Saúde e Energia
```powershell
# Academia
python cos\logger\event_logger.py --area energy_body --category saude --action "Treinou 1h musculação" --impact 3 --duration 60

# Organização
python cos\logger\event_logger.py --area energy_body --category organizacao --action "Organizou casa/escritório" --impact 2 --duration 30
```

### Relações e Influência
```powershell
# Follow-up
python cos\logger\event_logger.py --area relations_influence --category followup --action "Follow-up com cliente XP Investimentos" --impact 4 --duration 15

# Conteúdo publicado
python cos\logger\event_logger.py --area relations_influence --category conteudo --action "Publicou post no Instagram (convite)" --impact 3 --duration 20
```

---

## 🔐 Regras que Você Aceitou

O sistema irá confrontar agressivamente quando:

1. **Output Econômico cair 3 dias seguidos** → RULE-001 ATIVADA
2. **3+ tarefas abertas sem fechar nenhuma** → Dispersão operacional
3. **2h+ sem evento logado** → Inatividade detectada
4. **Follow-up atrasado >48h** → Alerta de relacionamento

**Você aceitou:**
- Confronto agressivo baseado em dados
- Execução sempre com consentimento e log
- Receita como prioridade estratégica #1
- Sistema adaptativo (não tirânico)

---

## 🔄 Evolução do Sistema

### Quando adicionar uma nova skill:
1. Criar `.agent/skills/<nome>/SKILL.md`
2. Documentar no JARVIS: `python cos\integrations\notebooklm_client.py --skill-doc <nome> "<descricao>"`
3. Logar: `python cos\logger\event_logger.py --area system_building --action "Criou skill <nome>" --impact 4`

### Revisão semanal (toda segunda-feira):
```powershell
# Score da semana
python cos\engine\predictive_engine.py --days 7

# Governance
python cos\engine\governance_rules.py
```

---

## ⚡ Modo de Emergência: Rascunho Rápido com ClawdBot

Use esta estrutura para pensar em conjunto com o ClawdBot:

```markdown
## Rascunho rápido de hoje
Data: [DATA]
Projeto principal: [PROJETO]
O que preciso fazer: [LISTA DE TASKS]
Bloqueios: [O QUE ESTÁ TRAVADO]
Pergunta estratégica: [SE TIVER]
```

Cole isso no chat do Antigravity e o agente vai:
1. Analisar prioridades
2. Sugerir tasks baseadas no score atual do COS
3. Criar um plano de ação para o dia
4. Logar automaticamente ao concluir

---

*COS v1.0 — Construído com Antigravity + Python + NotebookLM JARVIS*
