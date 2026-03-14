# 🕒 Protocolo Operacional Diário JARVIS

Este documento define a dinâmica real de como JARVIS e Pietro trabalham em conjunto para atingir as metas estratégicas.

## 🌅 1. Morning Directive (08:00) — O Vetor
**O que acontece:** O JARVIS envia uma mensagem no seu WhatsApp.
- **Análise**: Score do dia anterior + Tendência semanal.
- **Interação**: Você pode responder com "Iniciar Dia" ou pedir ajuste de foco.
- **Ping**: "Bom dia, Pietro. 🚀 Hoje o foco é ARTE (Metodologia Lifecycle). Score ontem: 82. Top 3 tarefas enviadas no Trello. Vamos decolar?"

## ☀️ 2. Colaboração em Fluxo (Cada 30 min)
**O que acontece:** O JARVIS atua como seu par. Ele revisa os tópicos ativos e as pastas de entrada de Markdowns.
- **Análise**: O que foi produzido nos últimos 30min? Há algum input novo na pasta `inputs/`?
- **Interação**: "Pietro, vi que você avançou no plano de ARTE. Sugiro revisarmos o tópico 'Licitação' agora para não perder o timing do sistema."
- **Objetivo**: Garantir que a cadência de 10x não caia e que o "Mission Control" esteja sempre atualizado.

## 🌙 3. End-of-Day Audit (19:00) — A Memória
**O que acontece:** Fechamento do dia e consolidação de memória.
- **Análise**: Score Final (0-100).
- **Ação**: Sincronização automática dos logs no NotebookLM.
- **Ping**: "Dia finalizado com Score 82. Excelente tração em ARTE. Sincronizando logs... Metas para amanhã já mapeadas."

---

## ⚡ Colaboração Autonôma (Dinâmica de 'Par')

O JARVIS analisa seus logs de 30 em 30 minutos para garantir **eficiência máxima**:

1.  **Fontes de Dados (Extração)**:
    - `cos/logs/YYYY-MM-DD.json`: Extração de `action`, `impact` e `duration_minutes`.
    - `.jarvis/brain/*.md`: Comparação com os Roadmaps de ARTE, WAPPI e XP BARSI.
    - `inputs/`: Monitoramento de novos direcionamentos manuais.

2.  **Dashboards Reais de Cadência (30 min)**:
    A cada pílula de alinhamento, o JARVIS apresenta:
    - **Fator de Impacto**: Média de impacto das ações nos últimos 30min vs. Meta (Impacto > 4).
    - **Cognitive Sync**: O quão próximo as ações estão do Plano Estratégico (0-100%).
    - **Insights de Otimização**: "Você gastou 30min em layout. IA sugere focar em Lógica de API agora para destravar o WAPPI."

3.  **Processamento de Markdowns**: Se você joga um arquivo em `inputs/`, o JARVIS integra ao cérebro e devolve a análise no próximo ciclo de 30 min.

## 📊 Como sua performance é medida?
Tudo converge para o **Score Engine**:
- **35%**: Você trouxe dinheiro? (Movimentou Trello/Licitação).
- **25%**: Você melhorou o sistema? (Criou automação/docs).
- **20%**: Você cumpriu o que disse? (Fechou o Top 3).
- **20%**: Energia e Networking.

---
*Protocolo registrado na Base de Conhecimento JARVIS — 27/02/2026*
