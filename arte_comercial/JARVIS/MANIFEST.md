# 🤖 JARVIS MANIFEST — Instruções para o Daemon

> Este arquivo é lido pelo `jarvis_daemon.py` do projeto JARVIS.
> Ele define O QUE monitorar, COMO medir progresso e ONDE encontrar os dados.

---

## 📐 Estrutura do Projeto

| Pasta/Módulo       | Propósito                                         | Scripts Chave                                       |
| ------------------- | -------------------------------------------------- | --------------------------------------------------- |
| `arte_edital/`    | Pipeline de ingestão de editais (01→05)          | `01_ingestao_edital.py` → `05_joint_master.py` |
| `arte_heavy/`     | Matching IA de produtos vs editais                 | `arte_heavy_B.py`, `arte_heavy_notebook.py`     |
| `arte_metadados/` | Extração de metadados de catálogos PDF          | `arte_metadados.py`, `arte_metadados_excel.py`  |
| `arte_code/`      | Scripts consolidados (versões estáveis)          | `arte_pipeline.py`, `arte_download.py`          |
| `arte_notebooks/` | Integração com Google NotebookLM                 | `ask_artenotebook.py`                             |
| `DOWNLOADS/`      | Dados operacionais (Editais, Propostas, Planilhas) | —                                                  |
| `logs/`           | Logs de execução dos scripts                     | `arte_heavy.log`, `notebook_pipeline.log`       |

---

## 📊 Métricas de Progresso (O que o Daemon deve medir)

### 1. Atividade de Scripts (Performance)

- **Fonte**: `logs/jarvis_audit.json` (gerado pelo módulo `jarvis_audit.py`).
- **Métricas**: Tempo de execução, status (success/error), nº de itens processados.
- **Scripts Críticos**: `arte_heavy_B.py`, `arte_heavy_notebook.py`, `01_ingestao_edital.py`.

### 2. Volume de Dados (DOWNLOADS/)

- **Contar**: Nº de pastas em `DOWNLOADS/EDITAIS/` (= nº de editais ativos).
- **Contar**: Nº de arquivos em `DOWNLOADS/PROPOSTAS/` (= propostas em preparação).
- **Monitorar**: Data de modificação de `master_heavy_ultra.xlsx` (planilha mestre).

### 3. Mudanças Estruturais (Código)

- **Git diff**: Verificar se houve commits recentes no repositório `arte_`.
- **Novos arquivos**: Alertar se surgirem scripts novos ou se algum for deletado.

---

## 🏷️ #TASKS Ativas (Medição de Progresso)
> 🔀 **Migradas**: Todas as tarefas operacionais e arquiteturais deste projeto agora residem e são lidas exclusivamente a partir do arquivo `TODO.md` na raiz do projeto. O JARVIS Daemon observa o `TODO.md` diretamente.

---

## 🔔 Regras de Alerta para o Daemon

| Condição                                 | Ação                              |
| ------------------------------------------ | ----------------------------------- |
| `jarvis_audit.json` sem entrada há >24h | ⚠️ Alerta: Projeto arte_ inativo  |
| Pasta `DOWNLOADS/EDITAIS/` mudou         | 📥 Log: Novo edital detectado       |
| `master_heavy_ultra.xlsx` modificado     | 📊 Log: Planilha mestre atualizada  |
| Algum script falhou (status: error)        | 🔴 Alerta: Falha em script crítico |
| #TASK marcada como `[x]`                 | ✅ Log: Progresso registrado        |
