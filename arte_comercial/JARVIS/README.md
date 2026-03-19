# ARTE — Licitações & BI (Coordenação JARVIS)

Este diretório é o **Centro de Comando JARVIS** para o projeto ARTE. A partir daqui, o JARVIS daemon audita o progresso, mede performance e sincroniza a visão tática com o COS central.

## 🎯 Objetivos Estratégicos
1. **Escalabilidade:** Transformar a análise de editais em um pipeline 100% autônomo.
2. **Precisão:** Elevar a taxa de acerto do matching de produtos para >90%.
3. **Conversão:** Reduzir o tempo entre o download do edital e o envio da proposta para < 2 horas.

## 🛠️ Componentes de Monitoramento
- **`MANIFEST.md`:** Lista de tarefas táticas e progresso em tempo real.
- **`audit.py`:** Motor de auditoria que gera snapshots e diffs a cada 30 min.
- **`logs/`:** Onde as "caixas pretas" das execuções e decisões da IA são armazenadas.

## 📊 Métricas de Sucesso (KPIs)
- **Health Score:** Meta > 80/100 constante.
- **Matching Quality:** Medido via `arte_heavy_notebook.py`.
- **Throughput:** Quantidade de editais processados por dia.

---
*Gerado e Mantido por JARVIS Daemon*
