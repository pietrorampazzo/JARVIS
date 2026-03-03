---
name: notebooklm
description: Utilize a suíte MCP do NotebookLM para realizar pesquisas profundas, consultar histórico de decisões, estudar logs diários e atuar como a Memória de Longo Prazo do JARVIS (Segunda Brain).
---

# Skill: NotebookLM (Second Brain & Deep Research)

## Quando Usar

Sempre que o usuário pedir para:
- Consultar documentação contida no NotebookLM.
- "Estudar" ou fazer "deep research" em tópicos guardados no JARVIS.
- Perguntar sobre por que uma decisão arquitetural foi feita no passado.
- Resgatar relatórios (briefings) ou resumos de logs históricos de dias passados.
- Gerar podcasts, vídeos ou documentação rica (usando `mcp_notebooklm_generate_content`).

## ⚙️ Setup Opcional & Health Check

Antes de mergulhar na pesquisa, verifique a saúde da conexão para garantir que está autorizado:
Use a tool `mcp_notebooklm_get_health` para checar.
- Se `authenticated: false`, você pode precisar pedir autorização ou rodar `mcp_notebooklm_setup_auth`, mas comunique o usuário antes.

## 🧠 Como Pesquisar (Deep Research Protocol)

Nunca faça UMA ÚNICA pergunta para problemas complexos. Use a **Estratégia Multi-Passagem (Session RAG)**:

1. **Start Broad:** Chame `mcp_notebooklm_ask_question` sem `session_id` para uma visão geral do seu tópico, e capture o `session_id` que ele retornar.
2. **Go Specific:** Chame a mesma tool usando o MESMO `session_id` para aprofundar nos métodos, dependências, etc.
3. **Cover Pitfalls:** Re-chame com o MESMO `session_id` exigindo saber sobre "gaps, edge cases e gotchas" para ter certeza que você (Agente) tem tudo que precisa antes de codificar.
4. **Implementação:** Somente após 2 ou 3 passagens investigativas, forneça a resposta ou a codificação final para o usuário do Antigravity.

## 📓 Seleção de Notebook

Se não tiver certeza de qual Notebook investigar, liste-os:
```json
// Chame list_notebooks
mcp_notebooklm_list_notebooks({})
```
Ou ative um especificamente se o contexto mudar:
```json
// Chame select_notebook
mcp_notebooklm_select_notebook({ id: "UUID-AQUI" })
```

## 🎥 Extra: Geração de Conteúdo

O módulo suporta `mcp_notebooklm_generate_content`. Você pode gerar Podcasts de Arquitetura (`audio_overview`) ou Briefings Diários em formato relatório PDF ("report"). Utilize conforme o usuário peça relatórios mais "físicos" ou "multimídia".
