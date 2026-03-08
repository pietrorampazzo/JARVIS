# 🤖 Manual do JARVIS

Bem-vindo à nova estrutura simplificada do seu Sistema Operacional Cognitivo.

## 💓 O Heartbeat (Pulso)
A metodologia de "Morning/Midday/EOD" foi substituída por um **Heartbeat de 1 hora**.

- **O que ele faz?**
    - Sincroniza suas Tasks entre projetos.
    - Atualiza o seu `dia.md` com insights da IA (Gemini).
    - Calcula seu Score de produtividade e Gaps para a meta.
    - Executa o ritual do Oráculo às 04:00 da manhã.

- **Como reconfigurar?**
    - Se precisar reinstalar o agendamento no Windows, execute:
      `powershell -ExecutionPolicy Bypass -File cos\heartbeat\setup_heartbeat.ps1`

## 📂 Organização de Pastas

- `/cos`: O "Coração" do sistema (Engines, Heartbeat, Core, Logs).
- `/tools`: Scripts utilitários (ex: `get_overdue.py`, `board_import.py`, `project_analyzer.py`).
- `/docs`: Documentação técnica e notas de pesquisa.
- `/data`: Bases de dados e snapshots.

## 📝 O arquivo `dia.md`
Este é o seu painel de controle diário. Ele é atualizado a cada hora pelo Heartbeat. Use-o para ter uma visão rápida de:
1. Pipeline de Licitações.
2. Insights Estratégicos da IA.
3. Lista Global de Tasks pendentes.

## 🛠️ Manutenção
- **Não delete** a pasta `cos/logs`, ela contém todo o seu histórico de atividades.
- Mantenha a raiz limpa: novos scripts devem ir para `tools/` e novos documentos para `docs/`.

---
*Assinado: JARVIS Engine*
