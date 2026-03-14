# 🔄 CICLO DE VIDA ARTE — Bid-to-Delivery (Vetor 10x)

Este documento é o racional mestre para a operação da **ARTE Comercial**. Ele define o fluxo de trabalho, os touchpoints de automação e a governança de cada etapa.

---

## 🏗️ 1. FASE DE CAPTAÇÃO (PROSPECÇÃO & EDITAIS)

### 📥 1.1 Download & Triagem
- **Local**: `C:\Users\pietr\OneDrive\.vscode\arte_\DOWNLOADS\EDITAIS`
- **Ação**: Conferência automática entre Pastas Locais <=> Cards no Trello.
- **JARVIS Sentinel**: Identificar se há edital sem card ou card sem edital.

### 🔍 1.2 Matching & Inteligência (arte_heavy)
- **Ferramenta**: `arte_heavy.py` + `arte_heavy_notebook.py` (NotebookLM).
- **Integração de Dados (#TASK)**: Correlação sistemática entre:
    - Lists Trello (**Compras.gov** / **Preparando**)
    - Tabela `master_heavy_notebooks.xlsx`
    - Sistema **Licitei** (Input automático após validação humana/Anselmo).
- **Processo**:
    1. Descompactação e extração de Termos de Referência.
    2. Matching avançado via RAG (NotebookLM).
    3. Avaliação de qualidade e parecer jurídico/técnico (Anselmo).

---

## 📝 2. FASE DE PROPOSTA (EXECUÇÃO)

### ⌨️ 2.1 Digitação & Envio
- **Canais**: Manual (Compras.gov) ou **LICITEI** (ERP).
- **Automação**: Teste de robôs de lances e digitação automática via Licitei (#TASK).
- **Scripts**: `arte_proposta.py` para automação de anexos e propostas.

### 🛡️ 2.2 Manutenção de Habilitação (ULTRA TASK)
- **Janela**: Primeiros dias úteis do mês (**Agendamento via Cronjob**).
- **Ação**: Automatizar coleta de anexos de ARTE Comercial e PIEZZO Comércio.
- **Destino**: `C:\Users\pietr\OneDrive\Área de Trabalho\ARTE\01_EDITAIS`.

---

## 📄 3. FASE DE CONTRATAÇÃO (EMPENHOS)

### 📧 3.1 Gatilho de Recebimento
1. **Input**: E-mail recebido em `pietro@artecomercialbrasil.com.br`.
2. **Processamento JARVIS**:
    - Identificar UASG e Pregão.
    - Criar pasta em: `I:\Meu Drive\arte_comercial\CONTRATOS.GOV`.
    - Mover Card Trello para coluna **"Empenho"**.
    - Anexar Empenho + Orçamento no card.
    - Registrar na [Sheet de Pedidos](https://docs.google.com/spreadsheets/d/1CbGmeGBzczmI3nYNxQnyXDUHqCkv_gPOGqNx1ORMr2I/edit?gid=804217256).

---

## 🌐 4. NOVAS FRENTES (ATAs & B2C)

### 🏷️ 4.1 Portal de ATAs (Venda Direta)
- **Plataforma**: `artecomercialbrasil.base44.app`
- **Metodologia**: Site funcional para recepção de propostas de órgãos públicos (#TASK).
- **Mailing**: Sistema de aprendizado contínuo para enriquecimento da [Sheet de Mailing](https://docs.google.com/spreadsheets/d/1CbGmeGBzczmI3nYNxQnyXDUHqCkv_gPOGqNx1ORMr2I/edit?gid=140875634).

### 🛒 4.2 Loja B2C
- **Status**: Planejamento.
- **Foco**: Comercialização direta para consumidor final.

---

## 🤖 5. PROJETOS DE LONGO PRAZO & CONTINGÊNCIA

### 🧠 5.1 NotebookLM Mastery
- **Estratégia MCP**: Prioritária para gestão de notebooks.
- **Contingência Selenium (#TASK)**: Se o MCP falhar, implementar robô Selenium + XPath para manipulação estruturada (Exclusão/Injeção/Atualização).

### 🏛️ 5.2 Gov API
- **Notebook**: [API Governo Brasileiro](https://notebooklm.google.com/notebook/23df640e-73ae-4d55-990f-2f4639995617)
- **Missão**: Dominar a API oficial para eliminar dependência de scrapers/captchas.
