---
description: Loga automaticamente uma atividade produtiva no COS Event Logger ao final de qualquer tarefa relevante
---

# Workflow: Log Project Activity

Registra qualquer atividade significativa concluída no COS.

## Passos

1. Identificar a tarefa concluída e mapear para a área correta:
   - Script/automação/bug/feature → `system_building`
   - Licitação/proposta/follow-up → `economic_output`
   - Tarefa/plano/disciplina → `execution_discipline`
   - Energia/saúde/organização → `energy_body`
   - Networking/clientes/conteúdo → `relations_influence`

// turbo
2. Executar o log da atividade:
   ```powershell
   python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\logger\event_logger.py" `
     --area <area_id> `
     --category <categoria> `
     --action "<descricao_curta_da_acao>" `
     --impact <1-5> `
     --duration <minutos_gastos> `
     --project "<nome_do_projeto>"
   ```

// turbo
3. Verificar se o log foi criado corretamente:
   ```powershell
   python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\logger\event_logger.py" --list
   ```

4. Confirmar ao usuário: "✅ Atividade logada: [ação] | Impacto [X]/5 | [Área]"

5. (Opcional) Se for fim de sessão, gerar o score do dia:
   ```powershell
   python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\engine\score_engine.py"
   ```
