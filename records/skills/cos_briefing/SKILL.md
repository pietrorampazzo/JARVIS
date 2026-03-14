---
name: cos_briefing
description: Gera e exibe o briefing COS correspondente ao horário atual (Morning 08h, Midday 13h, End-of-Day 19h). Use quando o usuário pedir o briefing do dia ou quando iniciar/encerrar uma sessão de trabalho.
---

# Skill: COS Briefing

## Quando Usar

Execute esta skill quando:
- Usuário iniciar uma sessão de trabalho (Morning Brief)
- Usuário pedir "como estou indo" ou "checkpoint" (Midday ou EOD)
- Horário de checkpoint se aproximar
- Precisar contexto rápido de performance para tomar decisão

## Lógica de Seleção do Briefing

```
Se hora atual < 11:00 → Morning Brief (08:00)
Se hora atual 11:00–17:00 → Midday Check (13:00)  
Se hora atual > 17:00 → End-of-Day Audit (19:00)
```

## Instruções de Execução

### Morning Briefing (08:00–11:00)
```powershell
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\briefings\morning_brief.py"
# Com save para JARVIS:
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\briefings\morning_brief.py" --save
```

### Midday Check (11:00–17:00)
```powershell
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\briefings\midday_check.py"
```

### End-of-Day Audit (17:00+)
```powershell
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\briefings\eod_audit.py"
# Com save para JARVIS:
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\briefings\eod_audit.py" --save
```

### Score Atual (qualquer hora)
```powershell
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\engine\score_engine.py"
```

### Análise Preditiva
```powershell
python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\engine\predictive_engine.py" --days 7
```

## Após Exibir o Briefing

Apresente o briefing ao usuário e pergunte:
> "Quer logar alguma atividade ou revisar as prioridades antes de começar?"

Se houver intervenções críticas (RULE-001, RULE-002), destaque-as explicitamente.
