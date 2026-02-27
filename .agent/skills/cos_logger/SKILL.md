---
name: cos_logger
description: Registra eventos produtivos no COS Event Logger após qualquer tarefa concluída no Antigravity. Use sempre ao final de uma sessão de trabalho ou quando uma tarefa significativa for completada.
---

# Skill: COS Logger

## Quando Usar

Esta skill deve ser ativada **automaticamente** ao final de qualquer:
- Tarefa completada no Agent Manager
- Script criado ou modificado com sucesso
- Bug resolvido
- Feature entregue
- Documento importantye gerado (walkthrough, implementation_plan, etc.)

## Instruções

Após concluir uma tarefa, execute os seguintes passos:

### 1. Identificar a Área
Mapeie a tarefa concluída para uma das 5 áreas:
| Ação | Área ID |
|------|---------|
| Licitação, proposta, follow-up comercial | `economic_output` |
| Script, automação, bug, feature, infra | `system_building` |
| Organização, disciplina, plano cumprido | `execution_discipline` |
| Saúde, academia, organização pessoal | `energy_body` |
| Cliente, parceiro, conteúdo, networking | `relations_influence` |

### 2. Definir Impacto (1-5)
| Score | Quando usar |
|-------|-------------|
| 5 | Movimento estratégico — impacto direto em meta principal |
| 4 | Alta relevância — avanço real e mensurável |
| 3 | Produtivo — trabalho relevante entregue |
| 2 | Tarefa pequena — contribuição modesta |
| 1 | Baixo impacto — rotineiro |

### 3. Executar o Log

```powershell
# Formato básico
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\logger\event_logger.py" `
  --area <area_id> `
  --category <categoria> `
  --action "<descricao_da_acao>" `
  --impact <1-5> `
  --duration <minutos> `
  --project "<nome_do_projeto>"
```

### Exemplos Prontos

**Script criado:**
```powershell
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\logger\event_logger.py" --area system_building --category dev --action "Criou event_logger.py funcional com CLI" --impact 5 --duration 45 --project "JARVIS"
```

**Briefing gerado:**
```powershell
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\logger\event_logger.py" --area execution_discipline --category briefing --action "Gerou morning briefing COS" --impact 3 --duration 5 --project "COS"
```

**Bug resolvido:**
```powershell
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\logger\event_logger.py" --area system_building --category dev --action "Corrigiu bug no score_engine.py" --impact 4 --duration 30 --project "JARVIS"
```

### 4. Confirmar o Log

Após executar, confirme ao usuário:
> "✅ Atividade logada no COS: [ação] — Impacto [X]/5 — Área: [nome_da_área]"

## Regra Importante

**Nunca logar sem evidência real.** O log só ocorre se a tarefa foi de fato concluída.
Se a tarefa foi apenas iniciada, use `--action "Iniciou [tarefa]"` com impacto 1.
