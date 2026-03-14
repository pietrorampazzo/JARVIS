---
description: Realiza o commit e push de todos os projetos do workspace configurados no JARVIS.
---

Este workflow automatiza o processo de salvar e enviar as alterações de todos os repositórios Git ativos no workspace.

// turbo
1. Executar o script de commit global:
   `python c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\engine\workspace_committer.py`

2. O script irá:
   - Identificar projetos no `config/projects.json`.
   - Executar `git add .`, `git commit` e `git push` em cada um.
   - Mostrar o resumo final no terminal.
   - Registrar detalhes em `cos/logs/workspace_commit.log`.
