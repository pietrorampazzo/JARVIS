# 🧠 JARVIS: Manual de Manipulação & Arquitetura RAG

Este manual detalha como o JARVIS utiliza o **NotebookLM MCP** para gerenciar a memória de longo prazo e apoiar as decisões do COS (Cognitive Operating System).

## 🏗️ Estrutura de Arquivos Necessária (O "Cérebro")

Para que o sistema funcione de forma análoga e auxiliar ao COS, os seguintes pilares de memória devem residir no NotebookLM:

| Tipo | Conteúdo | Função no COS |
|---|---|---|
| **Estatutário** | `COS_FOUNDATION.md`, `JARVIS_SOUL.md` | Define pesos, regras e a constituição do agente. |
| **Mapa** | `JARVIS_REGISTRY.md` | Localiza todos os módulos e identidades ativos. |
| **Histórico** | `Daily Logs (Snapshot JSON/XLSX)` | Permite auditoria retroativa de performance e score. |
| **Executivo** | `CORE_ROADMAP.md` + READMEs de projetos | Fornece o "Vetor de Direção" para assistência guiada. |
| **Contextual** | Deep Research (Editais, Docs Técnicos) | Alimenta o RAG com dados ultra-específicos (ex: Instrumentos Musicais). |

---

## 🏎️ As Habilidades de Manipulação (Skills)

O ecossistema JARVIS dispõe de um conjunto de habilidades para manipular dados de forma fluida. Aqui estão as principais agrupadas por fluxo:

### 🛠️ Catálogo de Habilidades Técnicas (27 Tools)

Aqui está a lista completa das ferramentas que o JARVIS utiliza para manipular o NotebookLM programaticamente:

#### GESTÃO DE BIBLIOTECA
1.  `list_notebooks`: Lista todos os notebooks na biblioteca.
2.  `get_notebook`: Detalhes específicos de um notebook por ID.
3.  `add_notebook`: Registra um novo notebook no sistema.
4.  `remove_notebook`: Remove o registro de um notebook.
5.  `update_notebook`: Atualiza metadados (tópicos, descrição).
6.  `search_notebooks`: Busca notebooks por termos.
7.  `get_library_stats`: Estatísticas globais do acervo.
8.  `select_notebook`: Alterna o notebook ativo padrão.
9.  `list_notebooks_from_nblm`: Scraper para descobrir notebooks fora do JARVIS.

#### GESTÃO DE SESSÕES & RAG
10. `list_sessions`: Lista conversas ativas.
11. `close_session`: Encerra uma sessão específica.
12. `reset_session`: Limpa o histórico sem fechar a sessão.
13. `ask_question`: O motor RAG (pergunta e resposta indexada).

#### INJEÇÃO DE DADOS (INPUT)
14. `add_source`: A skill mestra para injetar Arquivos, URLs, YouTube ou Drive.
15. `delete_source`: Remove fontes obsoletas.
16. `create_note`: Cria anotações manuais no Studio.
17. `convert_note_to_source`: Eleva uma nota ao status de fonte indexada.
18. `save_chat_to_note`: Transforma uma conversa inteira em uma nota de estudo.

#### SÍNTESE & EXPORTAÇÃO (OUTPUT)
19. `generate_content`: Cria Áudio, Vídeo, Infográficos, Reports ou Tabelas.
20. `download_content`: Exporta o conteúdo gerado para o sistema local.

#### INFRAESTRUTURA & SEGURANÇA
21. `setup_auth`: Dashboard de login inicial.
22. `re_auth`: Troca de conta ou renovação de token.
23. `de_auth`: Logout completo e limpeza de dados.
24. `get_health`: Status de saúde e autenticação do servidor.
25. `cleanup_data`: Limpeza profunda de logs e perfis de navegador.
26. `auto_discover_notebook`: Inteligência de metadados para novos itens.
27. `list_content`: Listagem crua de tudo que há no notebook.

---

## 🔄 Fluxo de Manipulação Input/Output

### Ciclo de Entrada (Audit Loop)
1. **Sentinel** detecta mudança Git ou Card Trello.
2. **JARVIS** gera um resumo desta mudança.
3. **Skill `create_note`** injeta este resumo no NotebookLM.
4. **Skill `convert_note_to_source`** torna o resumo perene para consultas futuras.

### Ciclo de Saída (Briefing Loop)
1. **JARVIS** pergunta ao NotebookLM: "Qual o gap entre as metas Q1 e o progresso atual?".
2. **Skill `generate_content`** cria um `Report` técnico.
3. **Skill `download_content`** traz o report para o seu painel de Mission Control.

---
*Documento registrado na Base de Conhecimento JARVIS — 27/02/2026*
