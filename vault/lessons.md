# 🧠 JARVIS Memory: Lessons Learned

Registro de padrões, bugs evitados e lições aprendidas durante a orquestração do ecossistema.

## Padrões de Sucesso
- [2026-03-22] **Arquivamento de Tasks**: Centralização no Vault mantém TODOs leves e focados.
- [2026-03-22] **Cron Architecture**: Uso de `schtasks` garante persistência após reboot em Windows.

## Erros e Correções (Self-Improvement)
- **JSON Encoding**: Sempre utilizar `utf-8-sig` no `load_json` (shared.py) para evitar erros de BOM em arquivos Windows.
- **Ambientes Virtuais de Skills**: Agentes em `.antigravity/skills/` possuem `.venv` próprios. Injeções globais não funcionam; dependências devem ser instaladas no binário do venv.
- **Orphan Modules**: Ao deletar scripts, SEMPRE verificar o orquestrador `jarvis_pulse.py` para evitar `ModuleNotFoundError`.
- **Conditional Trigger**: Watchers devem preferir análise de dados (Excel/DB) em vez de logs de texto (Markdown) para maior precisão.
