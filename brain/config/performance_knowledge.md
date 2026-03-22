# 📊 Base de Conhecimento de Performance: Extração de Editais

Este documento registra os padrões de sucesso e engines recomendadas para cada tipo de edital, permitindo que o Agente ARTE Edital execute a estratégia **Zero Token**.

## 🛡️ Padrões de Sucesso

| Órgão / Tipo | Engine Recomendada | Padrão de Concatenação | Nota de Performance |
| :--- | :--- | :--- | :--- |
| Compras.gov | Docling | Regex: `^ITEM \d+` | Alta: Estrutura previsível |
| Prefeituras (MG) | OCR (Tesseract) | Vision Check via Gemini | Baixa/Média: Tabelas sem borda |
| Padrão RelacaoItens | Camelot (Lattice) | Direto (Fixed Column) | Altíssima: Quase 100% Zero Token |

## 🧠 Aprendizado Recente (Fase 1)
- [ ] Mapear padrões da Prefeitura de BH (Scaneados)
- [ ] Validar extração de editais em .pdf com OCR vs Docling
