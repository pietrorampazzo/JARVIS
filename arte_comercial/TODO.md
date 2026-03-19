# 🌐 ARTE (Licitações - O Core Econômico)

> *Single Source of Truth para as pendências operacionais deste projeto.*

### 🚀 Prioridades Máximas (Workflow & Pipeline)

- [X] Matching Inteligente: Melhorar precisão do `arte_heavy.py` para >85%.
- [ ] Implementar pipeline completo e contínuo: Edital → Matching → Proposta → Licitei
- [ ] Desenvolver Fluxo automático: Empenho -> Trello -> Planilha de Pedidos.
- [ ] Habilitação: Criar Cronjob para coleta mensal de documentos de habilitação (ARTE & PIEZZO).

### 🌍 Expansão & B2C

- [X] Corrigir site ATA's: Catalogo bonito, Backend e Frontend unidos (artecomercialbrasil.base44.app).
- [ ] Estruturar a "Loginha da Arte" (B2C): Bling (Mercado Livre, Shopee...)

### 🧠 NotebookLM RAG (Memória & Inteligência ARTE)

- [X] Construir Fundação do NLM Client: Blindar contra quedas de sessão (Auto-Relogin) do MCP.
- [X] Construir script de Ingestão de Dados: Upload de editais e manuais da pasta DOWNLOADS.
- [X] Integrar nova arquitetura robusta no `arte_heavy.py`.

### Arte_Edital: Pipeline Core

- [X] Receber ZIP → deszipar recursivamente → achatar estrutura
- [X] Processar RelacaoItens → extrair itens tabelados (`_itens.xlsx`)
- [X] Identificar e renomear Termo de Referência (`termo_referencia.pdf`)
- [/] Extrair tabelas com Camelot → `_referencia.xlsx` (funcional mas instável)
- [ ] Fallback pdfplumber quando Camelot retorna 0 tabelas
- [X] Merge itens + referência → `_master.xlsx` por subpasta
- [X] Concatenar tudo → `summary.xlsx` + `master.xlsx` (filtrado por keywords)

### Arte_Edital: Qualidade & Robustez

- [X] Quality Logger: `edital_quality_logger.py` (detecta bugs por edital)
- [ ] Lidar com PDFs sem texto (OCR via `03_extracao_ocr.py`)
- [ ] Tratar tabelas desconcatenadas (itens divididos em páginas diferentes)
- [ ] Validação: garantir que nenhum item do RelacaoItens fique sem REFERENCIA no merge
- [ ] Log de taxa de completude do TR por edital (meta: >90%)
- [ ] Integrar quality logger no daemon pulse ✅ (Step 4/5)
- [ ] Editais com formatação não-padrão (tabelas em formato livre/texto corrido)
- [ ] PDFs protegidos/scaneados (precisam OCR + limpeza)
- [ ] Colunas com nomes inconsistentes entre editais (Nº vs N vs Item)

### Arte_Heavy: Infraestrutura CI

- [X] Rate-limit Guard: retry automático quando resposta < 5s
- [X] Performance Tracker: `arte_perf_tracker.py` (parseia logs, detecta falsos negativos)
- [X] Métricas JSON: export automático em `arte_heavy/metrics/`
- [X] Integrar tracker no daemon pulse ✅ (Step 5/5)
- [ ] Melhorar instruções do notebook para matching (prompt engineering)
- [ ] Validar conformidade jurídica (PARECER_JURIDICO_IMPUGNACAO preenchido)
- [ ] Validar conformidade técnica (JUSTIFICATIVA_TECNICA com substância)

### Arte_Heavy: Evolução

- [ ] Dashboard de evolução da taxa ATENDE (tracking semanal)
- [ ] Notebook CI ARTE dedicado (alimentado pelo tracker + quality logger)
- [ ] Ajuste de PALAVRAS_CHAVE e PALAVRAS_EXCLUIR baseado em dados reais
- [ ] Threshold de preço: validar se VALOR_FINAL < VALOR_UNIT * 0.70
