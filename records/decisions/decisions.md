## Decisão 001: O Renascimento (Rebirth)
**Data**: 2026-03-08
- Faxina Geral (Phase 1 & 2): Deletamos mais de 15 scripts obsoletos.
- Heartbeat: Substituição do CRON por um pulso horário (jarvis_pulse.py).
- Organização: Separação clara entre /cos (Core), /tools (Utilitários) e /docs.

## Diretrizes de Arquitetura (ADRs)
1. **Heartbeat over Cron**: O sistema deve ser cíclico e ciente do tempo.
2. **Absolute Imports**: Todos os módulos devem usar 'cos.xxx'.
3. **Self-Documentation**: JARVIS_MANUAL.md é a autoridade.

## Grande Limpeza do JARVIS (Phase 1 & 2): Deletamos 15+ scripts obsoletos e centralizamos no Heartbeat
**Data**: 2026-03-08
**Impacto**: 5/5 (Log Automático)
**Status**: Executado com Sucesso ✅
