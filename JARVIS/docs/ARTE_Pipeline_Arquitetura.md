# ARTE Pipeline — Arquitetura Completa e Bugs Conhecidos

## Pipeline de Ingestão de Editais (arte_edital/)

O pipeline recebe uma pasta zipada de edital de licitação pública e deve entregar um orçamento planilhado.

### Fluxo Completo:
1. **01_ingestao_edital.py**: Recebe ZIP → descompacta recursivamente → achata estrutura de pastas
2. **Identificação**: RelacaoItens.pdf (lista de itens) + Termo de Referência (especificações técnicas)
3. **04_pipeline_extracao.py**: Limpa rodapés do PDF → extrai tabelas com Camelot → grava Excel
4. **05_joint_master.py**: Merge itens + referência → summary.xlsx → master.xlsx (filtrado)

### Formato dos Dados:
- `{nome_edital}_itens.xlsx`: Nº, DESCRICAO, QTDE, VALOR_UNIT, VALOR_TOTAL
- `{nome_edital}_referencia.xlsx`: ITEM, REFERENCIA (especificação técnica detalhada)
- `{nome_edital}_master.xlsx`: merge dos dois acima
- `master.xlsx`: todos editais concatenados, filtrados por palavras-chave do nosso catálogo

### Scripts Auxiliares:
- `02_limpeza_rodape.py`: Remove rodapés repetitivos de PDFs
- `03_extracao_ocr.py`: OCR para PDFs scaneados
- `03_extracao_tabelas.py`: Extração de tabelas (Camelot)
- `04_leitura_ia_edital.py`: Leitura com IA (Gemini) para extração de dados

---

## Pipeline de Matching (arte_heavy/)

Recebe o `master.xlsx` e faz o matching inteligente de cada item com nosso catálogo via NotebookLM.

### Fluxo:
1. Lê `master.xlsx` com itens pendentes
2. Para cada item: monta query "{REFERENCIA} por até R$ {VALOR_UNIT * 0.70}"
3. Envia para NotebookLM (notebook com catálogo de produtos)
4. Parseia resposta: STATUS, marca_sugerida, modelo_sugerido, VALOR, JUSTIFICATIVA_TECNICA
5. Salva em `master_heavy.xlsx` com STATUS: ATENDE / ATENDE COM RESSALVAS / NÃO ATENDE

### Rate-Limit Guard (v1.1):
- Se resposta < 5s e STATUS = "NÃO ATENDE" → provável rate-limit silencioso
- Pausa 60s e retry (até 2x)
- Se persistir → STATUS = "RATE_LIMITED" para reprocessamento

---

## BUGS CONHECIDOS E GARGALOS

### arte_edital:
1. **Termo de Referência não encontrado**: Muitos editais vêm com PDFs nomeados de forma inconsistente. O script busca o PDF que NÃO é "RelacaoItens" e renomeia para "termo_referencia.pdf", mas falha quando há múltiplos PDFs ou nenhum.
2. **Tabelas quebradas entre páginas**: Camelot não concatena tabelas que cruzam page breaks. Itens ficam divididos ou dados ficam em linhas separadas.
3. **Dados sujos**: Editais públicos não seguem padrão. Colunas com nomes variáveis (Nº, N, Item, Nro_Item), valores monetários com formatos diferentes (R$, vírgula vs ponto).
4. **PDFs protegidos/scaneados**: Alguns PDFs são imagens scaneadas que precisam OCR. O script `03_extracao_ocr.py` existe mas não está integrado no pipeline principal.
5. **Formato livre/texto corrido**: Alguns TRs descrevem itens em parágrafos ao invés de tabelas — Camelot retorna 0 tabelas.
6. **Permission denied**: `master_heavy.xlsx` aberto no Excel impede salvamento.

### arte_heavy:
1. **Rate-limit silencioso**: NotebookLM retorna "NÃO ATENDE" em < 3s quando rate-limited (vs 20-40s normal). Guard implementado na v1.1.
2. **Falsos negativos**: 49 itens marcados "NÃO ATENDE" por rate-limit na sessão de 03/03/2026.
3. **Checkpoint recomeçando do zero**: Em algumas sessões, o progresso anterior não é detectado e o script reprocessa itens já computados.
4. **Respostas vazias do NotebookLM**: Quando "answer" vem como string vazia, o parser marca como NÃO ATENDE.

---

## MÉTRICAS ATUAIS (04/03/2026)

### Performance do Matching:
- Total queries processadas: 136
- Taxa ATENDE (sessões saudáveis): ~60-75%
- Taxa ATENDE (sessões rate-limited): 0%
- Falsos negativos detectados: 49
- Tempo médio por query (normal): 35-45s
- Tempo médio por query (rate-limited): 2-3s

### Quality do Pipeline Edital:
- Medido pelo `edital_quality_logger.py` (JSON em `arte_edital/logs/`)
