# Plano de Implementação: Motor Evolution API (Monitoramento XP Barsi)

Este plano descreve a integração do JARVIS com a Evolution API para monitorar conversas no Grupo BARSI e redirecionar oportunidades para o Grupo Pie.Invest.

## Mudanças Propostas

### JARVIS Integrations

#### [NEW] [evolution_monitor.py](file:///c:/Users/pietr/OneDrive/.vscode/JARVIS/cos/integrations/evolution_monitor.py)
Script Python principal para interagir com a Evolution API.
- **Função**: Conectar à API, listar instâncias, e configurar webhooks ou polling de mensagens.
- **Monitoramento**: Focar no JID do Grupo BARSI.
- **Análise**: Enviar mensagens suspeitas para análise de intenção (Oportunidade/Seguro/Crédito).
- **Redirecionamento**: Disparar para o JID do Grupo Pie.Invest.

#### [MODIFY] [XP_BARSI.md](file:///c:/Users/pietr/OneDrive/.vscode/JARVIS/XP_BARSI.md)
Atualizar o status do motor de monitoramento de "Pendente" para "Em Implementação".

#### [MODIFY] [MISSION_CONTROL.md](file:///c:/Users/pietr/OneDrive/.vscode/JARVIS/MISSION_CONTROL.md)
Adicionar status em tempo real do Evolution Monitor.

## Verificação

### Testes Manuais
- Executar `evolution_monitor.py` em modo debug.
- Simular uma mensagem no Grupo BARSI (mock) e verificar se o redirecionamento ocorre.
- Validar a criação de cards no Trello baseados nas oportunidades captadas.
