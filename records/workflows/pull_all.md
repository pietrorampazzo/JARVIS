---
description: Realiza o git pull de todos os projetos do workspace configurados no JARVIS.
---

Este workflow automatiza o processo de atualizar todos os repositórios Git ativos no workspace, trazendo as alterações mais recentes do servidor remoto.

// turbo
1. Executar o script de pull global:
   `python c:\Users\pietr\OneDrive\.vscode\JARVIS\engine\logic\workspace_puller.py`

2. O script irá:
   - Identificar projetos no `engine/config/projects.json`.
   - Executar `git pull` em cada repositório válido.
   - Mostrar o resumo das atualizações no terminal.
   - Registrar detalhes em `engine/logs/workspace_pull.log`.

> [!TIP]
> Use este comando sempre que começar a trabalhar para garantir que todos os seus projetos estejam sincronizados.
