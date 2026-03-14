# 🧠 Organização Definitiva do Sistema JARVIS

Esta diretiva define a arquitetura de armazenamento de inteligência, capacidades e processos do seu ambiente de trabalho. A estrutura foi unificada para eliminar redundâncias e garantir um fluxo de informação eficiente.

## 📂 Arquitetura de Pastas

Abaixo da raiz `.jarvis/`, temos três pilares fundamentais:

| Pasta | Nome | Função (O que é) | Conteúdo (Injeção) |
| :--- | :--- | :--- | :--- |
| `brain/` | **Memória** | Repositório de fatos, identidades e regras de negócio estáveis. | Arquivos `.md` estruturados com dados, contextos e histórico. |
| `skills/` | **Capacidades** | Conjunto de ferramentas e "músculos" do agente (MCPs, scripts). | Pastas de Skill com `SKILL.md` e scripts auxiliares (Python/JS). |
| `workflows/` | **Processos** | Sequências de passos e automações para execução de tarefas. | Arquivos `.md` que descrevem fluxos de comandos específicos. |

---

## 🚀 Como Articular cada uma

### 1. Memória (`brain/`)
A articulação aqui é de **Consulta e Persistência**.
- **Onde injetar?** Quando você descobre um fato novo sobre o projeto, muda uma regra de negócio ou define uma nova identidade de agente.
- **Forma de injeção**: Use o JARVIS para escrever documentos markdown claros e concisos. Evite logs brutos; prefira informações destiladas.

### 2. Capacidades (`skills/`)
A articulação aqui é de **Operação Técnica**.
- **Onde injetar?** Quando o sistema precisa de uma nova habilidade técnica (ex: ler arquivos `.rar`, enviar mensagens para um novo canal, consultar uma API externa).
- **Forma de injeção**: Crie uma pasta dentro de `skills/` seguindo o padrão MCP. Mantenha os scripts isolados e bem comentados.

### 3. Processos (`workflows/`)
A articulação aqui é de **Roteirização**.
- **Onde injetar?** Quando uma tarefa é repetitiva, complexa ou exige uma ordem exata de execução para garantir a qualidade (ex: fechamento diário, deploy, análise de editais).
- **Forma de injeção**: Crie arquivos `.md` descrevendo os passos. Use a regra `// turbo` se os comandos forem seguros para execução automática.

---

## 🔟 Exemplos Práticos

1.  **Perfil de Cliente (Brain)**: `.jarvis/brain/business/cliente_x.md` - Armazena as preferências e restrições de um cliente recorrente.
2.  **Regras de Edital (Brain)**: `.jarvis/brain/operations/bid_rules.md` - Lista de critérios de desempate padrão para licitações.
3.  **Extrator de PDF (Skills)**: `.jarvis/skills/pdf_parser/` - Script Python para extrair tabelas complexas de editais.
4.  **Integração Trello (Skills)**: `.jarvis/skills/trello_manager/` - Ferramentas para mover cards via API baseada em gatilhos.
5.  **Briefing Diário (Workflows)**: `.jarvis/workflows/daily_briefing.md` - Sequência para gerar o log do dia e atualizar o `dia.md`.
6.  **Setup de Projeto (Workflows)**: `.jarvis/workflows/init_project.md` - Checklist automático de criação de pastas e arquivos base.
7.  **Análise de Concorrência (Brain)**: `.jarvis/brain/reference/competitors.md` - Tabela com preços e condições de concorrentes mapeados.
8.  **Conversor de Moeda (Skills)**: `.jarvis/skills/currency_fixer/` - Habilidade de converter valores de licitações internacionais em tempo real.
9.  **Fechamento Mensal (Workflows)**: `.jarvis/workflows/monthly_report.md` - Processo de consolidar scores e metas do mês.
10. **Identidade do JARVIS (Brain)**: `.jarvis/brain/identity/personality.md` - Diretrizes de como o agente deve responder e se comportar.
