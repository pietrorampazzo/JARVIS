---
description: Gera e exibe o briefing COS do dia baseado no horário atual
---

# Workflow: Daily Briefing COS

Executa o briefing correto conforme o horário e registra no log.

## Passos

// turbo
1. Verificar hora atual e executar briefing correspondente:

   **Se antes das 11h — Morning Brief:**
   ```powershell
   python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\briefings\morning_brief.py" --save
   ```

   **Se entre 11h–17h — Midday Check:**
   ```powershell
   python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\briefings\midday_check.py"
   ```

   **Se após 17h — End-of-Day Audit:**
   ```powershell
   python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\briefings\eod_audit.py" --save
   ```

2. Exibir o output completo para o usuário.

// turbo
3. Executar o Pipeline Report do Trello (sempre, independente do horário):
   ```powershell
   python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\briefings\pipeline_report.py" --import-first
   ```
   Exibir o relatório ao usuário destacando:
   - Cards que avançaram no pipeline
   - Novas oportunidades identificadas
   - Licitações vencidas que precisam de atenção

4. Logar a geração do briefing no Event Logger:
   ```powershell
   python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\logger\event_logger.py" --area execution_discipline --category briefing --action "Gerou briefing COS + Pipeline Report" --impact 2 --duration 5
   ```

5. Perguntar ao usuário: "Deseja logar alguma atividade ou revisar as prioridades do pipeline?"
