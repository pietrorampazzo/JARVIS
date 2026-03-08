# JARVIS Monitoring Brief
> Guia rápido de interpretação de métricas e ciclo de vida do COS.

## 📊 O Ciclo Diário
Para que seu monitoramento seja eficaz, seguimos este ritual:
1. **08:00 - Morning Brief**: O JARVIS te envia no WhatsApp/Telegram (via OpenClaw) o plano de batalha e score acumulado.
2. **Durante o dia**: Use `/log_project_activity` ou fale naturalmente com o OpenClaw para registrar progressos.
3. **13:00 - Midday Check**: Auditoria de desvios. Se o score estiver baixo, o JARVIS irá te confrontar.
4. **19:00 - EOD Audit**: Resumo do impacto real do dia e upload para a memória do NotebookLM.

## 📈 Entendendo os Scores
- **90-100 (Ultra Output)**: Velocidade máxima. Prossiga com projetos de alto risco.
- **70-89 (High Impact)**: Ritmo sustentável. Foco em fechar tasks abertas.
- **50-69 (Warning Range)**: Algo está bloqueando sua execução. Revise o `task.md`.
- **< 50 (Critical)**: Risco estratégico. O sistema aplicará as **Regras de Governança (RULE-001)**.

## 🔗 Integração OpenClaw
- **Comando Manual**: `python "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\integrations\openclaw_notifier.py" "Sua mensagem"`
- **Skill Sync**: O OpenClaw lê `JARVIS_STATE.json` para saber seu contexto atual antes de responder.
