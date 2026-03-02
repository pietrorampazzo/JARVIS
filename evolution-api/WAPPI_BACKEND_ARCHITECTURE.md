# 📘 WAPPI — Manual Completo de Arquitetura Backend

> **Versão:** 1.0
> **Data:** 2026-02-24
> **Objetivo:** Documentar TODA a arquitetura backend necessária para que o Wappi funcione como um CRM automatizado por IA via WhatsApp, integrado com Evolution API e LLMs.

---

## 📐 1. Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  Dashboard │ Agentes IA │ Kanban │ Contatos │ Grupos │ Inbox   │
└──────┬───────────────┬──────────────────────────┬───────────────┘
       │ REST (HTTP)   │ WebSocket (Socket.io)    │ REST
       ▼               ▼                          ▼
┌──────────────┐ ┌──────────────┐ ┌───────────────────────────┐
│  API Server  │ │  WS Gateway  │ │    Evolution API (WhatsApp)│
│  (Supabase   │ │  (Socket.io) │ │  - Envio/recebimento msgs │
│   Edge Fns)  │ │              │ │  - QR Code / Instâncias   │
└──────┬───────┘ └──────┬───────┘ │  - Grupos / Participantes │
       │                │         └────────────┬──────────────┘
       ▼                ▼                      │
┌──────────────────────────────┐               │
│     PostgreSQL (Supabase)    │◄──────────────┘
│  Leads, Agentes, Mensagens,  │     Webhooks
│  Grupos, Logs, Métricas      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   LLM Engine (OpenAI / etc) │
│  - Tool Calling              │
│  - Persona do Agente         │
│  - Qualificação automática   │
└──────────────────────────────┘
```

### Comunicação

| Tipo              | Protocolo                               | Uso                                          |
| ----------------- | --------------------------------------- | -------------------------------------------- |
| Comandos de dados | HTTP REST (POST/GET/PUT/DELETE)         | CRUD de leads, agentes, configurações      |
| Tempo real        | WebSocket (Socket.io)                   | Mensagens chegando, movimentação de Kanban |
| WhatsApp          | Evolution API (REST + WebSocket nativo) | Envio/recebimento de mensagens               |

---

## 🗄️ 2. Modelagem do Banco de Dados (PostgreSQL)

### 2.1 Tabela `agents` — Agentes de IA

```sql
CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  product VARCHAR(200),
  persona TEXT NOT NULL,              -- Prompt comportamental completo
  payment_link VARCHAR(500),          -- URL de checkout/pagamento
  mode VARCHAR(20) NOT NULL DEFAULT 'FULL',  -- FULL | PROSPECTING | ATTENDING
  avatar_url VARCHAR(500),
  whatsapp_instance_id VARCHAR(100),  -- ID da instância na Evolution API
  is_active BOOLEAN DEFAULT true,
  is_connected BOOLEAN DEFAULT false, -- Status do WhatsApp
  
  -- Métricas acumuladas
  leads_handled INTEGER DEFAULT 0,
  leads_converted INTEGER DEFAULT 0,
  
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS: Cada usuário só vê seus agentes
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own agents" ON agents
  FOR ALL USING (auth.uid() = user_id);
```

### 2.2 Tabela `leads` — Oportunidades / Contatos do CRM

```sql
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  
  name VARCHAR(200) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(200),
  website VARCHAR(500),
  avatar_url VARCHAR(500),
  
  -- Funil
  stage VARCHAR(20) NOT NULL DEFAULT 'lead',
  -- Valores: lead | cadence | connected | qualified | converted | lost
  
  deal_value DECIMAL(12,2) DEFAULT 0,
  tags TEXT[] DEFAULT '{}',
  
  -- Origem
  source VARCHAR(50),  -- manual | import | group_extraction | organic
  source_group_id UUID REFERENCES groups(id) ON DELETE SET NULL,
  
  -- Controle de cadência
  cadence_step INTEGER DEFAULT 0,       -- Qual etapa de prospecção
  max_attempts INTEGER DEFAULT 5,
  last_contact_at TIMESTAMPTZ,
  next_contact_at TIMESTAMPTZ,
  is_paused BOOLEAN DEFAULT false,
  
  -- Resultado
  lost_reason VARCHAR(200),
  converted_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_leads_stage ON leads(user_id, stage);
CREATE INDEX idx_leads_agent ON leads(agent_id);
CREATE INDEX idx_leads_phone ON leads(phone);

ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own leads" ON leads
  FOR ALL USING (auth.uid() = user_id);
```

### 2.3 Tabela `messages` — Histórico de Conversas

```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE NOT NULL,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  
  direction VARCHAR(10) NOT NULL,  -- inbound | outbound
  sender VARCHAR(20) NOT NULL,     -- ai | lead | human | system
  content TEXT NOT NULL,
  media_url VARCHAR(500),
  media_type VARCHAR(50),          -- image | audio | video | document
  
  -- Metadados da Evolution API
  evolution_message_id VARCHAR(100),
  whatsapp_timestamp TIMESTAMPTZ,
  status VARCHAR(20) DEFAULT 'sent', -- sent | delivered | read | failed
  
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_messages_lead ON messages(lead_id, created_at DESC);

ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own messages" ON messages
  FOR ALL USING (
    EXISTS (SELECT 1 FROM leads WHERE leads.id = messages.lead_id AND leads.user_id = auth.uid())
  );
```

### 2.4 Tabela `activity_logs` — Log de Atividades do Sistema

```sql
CREATE TABLE activity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  
  action VARCHAR(50) NOT NULL,
  -- Valores: imported | stage_changed | message_sent | message_received |
  --          qualified | converted | lost | paused | resumed | assigned |
  --          tag_added | tag_removed | deal_updated
  
  description TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',  -- Dados extras (ex: {from_stage: "lead", to_stage: "cadence"})
  
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_activity_lead ON activity_logs(lead_id, created_at DESC);
```

### 2.5 Tabela `groups` — Grupos de WhatsApp

```sql
CREATE TABLE groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  
  whatsapp_group_id VARCHAR(100) NOT NULL,  -- JID do grupo na Evolution
  name VARCHAR(300) NOT NULL,
  description TEXT,
  participant_count INTEGER DEFAULT 0,
  
  -- Controle de extração
  last_extracted_at TIMESTAMPTZ,
  extracted_count INTEGER DEFAULT 0,
  
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE groups ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own groups" ON groups
  FOR ALL USING (auth.uid() = user_id);
```

### 2.6 Tabela `broadcasts` — Disparos em Massa

```sql
CREATE TABLE broadcasts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  
  type VARCHAR(20) NOT NULL,         -- direct (1:1) | group (dentro do grupo)
  target_group_id UUID REFERENCES groups(id) ON DELETE SET NULL,
  
  message_template TEXT NOT NULL,
  media_url VARCHAR(500),
  
  -- Agendamento
  status VARCHAR(20) DEFAULT 'pending', -- pending | running | paused | completed | failed
  scheduled_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  
  -- Progresso
  total_recipients INTEGER DEFAULT 0,
  sent_count INTEGER DEFAULT 0,
  failed_count INTEGER DEFAULT 0,
  
  -- Config de simulação humana
  min_delay_seconds INTEGER DEFAULT 15,  -- Delay mínimo entre envios
  max_delay_seconds INTEGER DEFAULT 90,  -- Delay máximo (randomizado)
  simulate_typing BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE broadcasts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own broadcasts" ON broadcasts
  FOR ALL USING (auth.uid() = user_id);
```

### 2.7 Tabela `settings` — Configurações do Usuário

```sql
CREATE TABLE settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  
  evolution_api_url VARCHAR(500),
  evolution_api_key_encrypted TEXT,    -- Criptografado no backend
  openai_api_key_encrypted TEXT,       -- Criptografado no backend
  
  webhook_url_messages VARCHAR(500),
  webhook_url_status VARCHAR(500),
  
  default_max_attempts INTEGER DEFAULT 5,
  default_cadence_interval_hours INTEGER DEFAULT 24,
  
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own settings" ON settings
  FOR ALL USING (auth.uid() = user_id);
```

---

## 🔌 3. API Endpoints (Edge Functions / Supabase Functions)

### 3.1 Agentes de IA

| Método | Endpoint                    | Descrição                           |
| ------- | --------------------------- | ------------------------------------- |
| GET     | `/api/agents`             | Lista todos os agentes do usuário    |
| POST    | `/api/agents`             | Cria novo agente                      |
| PUT     | `/api/agents/:id`         | Atualiza agente (nome, persona, modo) |
| DELETE  | `/api/agents/:id`         | Remove agente                         |
| POST    | `/api/agents/:id/toggle`  | Ativa/pausa agente                    |
| POST    | `/api/agents/:id/connect` | Gera QR Code via Evolution API        |
| GET     | `/api/agents/:id/qrcode`  | Retorna QR Code atual                 |
| GET     | `/api/agents/:id/status`  | Status de conexão WhatsApp           |

### 3.2 Leads / CRM

| Método | Endpoint                      | Descrição                                   |
| ------- | ----------------------------- | --------------------------------------------- |
| GET     | `/api/leads`                | Lista leads (filtros: stage, agent_id, tags)  |
| GET     | `/api/leads/:id`            | Detalhes do lead com histórico               |
| POST    | `/api/leads`                | Cria lead manualmente                         |
| PUT     | `/api/leads/:id`            | Atualiza lead (nome, email, valor, etc.)      |
| PUT     | `/api/leads/:id/stage`      | Move lead de etapa no funil                   |
| DELETE  | `/api/leads/:id`            | Remove lead                                   |
| POST    | `/api/leads/import`         | Importa leads via CSV/XLSX                    |
| POST    | `/api/leads/bulk-action`    | Ação em massa (excluir, reatribuir, pausar) |
| GET     | `/api/leads/:id/messages`   | Histórico de mensagens do lead               |
| GET     | `/api/leads/:id/activities` | Log de atividades do lead                     |

**Corpo do Import (POST `/api/leads/import`):**

```json
{
  "file_url": "https://storage.../file.csv",
  "column_mapping": {
    "name": "Nome Completo",
    "phone": "Telefone"
  },
  "agent_id": "uuid-do-agente",
  "tags": ["importado", "campanha-fev"]
}
```

### 3.3 Mensagens / Chat

| Método | Endpoint                         | Descrição                              |
| ------- | -------------------------------- | ---------------------------------------- |
| GET     | `/api/inbox`                   | Lista conversas ativas (com último msg) |
| GET     | `/api/inbox/:lead_id`          | Mensagens de uma conversa                |
| POST    | `/api/inbox/:lead_id/send`     | Envia mensagem humana (takeover)         |
| POST    | `/api/inbox/:lead_id/takeover` | Assume controle humano (pausa IA)        |
| POST    | `/api/inbox/:lead_id/release`  | Devolve controle para IA                 |

### 3.4 Grupos

| Método | Endpoint                         | Descrição                         |
| ------- | -------------------------------- | ----------------------------------- |
| GET     | `/api/groups`                  | Lista grupos que o agente participa |
| POST    | `/api/groups/sync`             | Sincroniza grupos da Evolution API  |
| POST    | `/api/groups/:id/extract`      | Extrai participantes do grupo       |
| GET     | `/api/groups/:id/participants` | Lista participantes extraídos      |

### 3.5 Broadcasts / Disparos

| Método | Endpoint                       | Descrição                |
| ------- | ------------------------------ | -------------------------- |
| GET     | `/api/broadcasts`            | Lista disparos             |
| POST    | `/api/broadcasts`            | Cria novo disparo          |
| PUT     | `/api/broadcasts/:id/pause`  | Pausa disparo em andamento |
| PUT     | `/api/broadcasts/:id/resume` | Retoma disparo             |
| DELETE  | `/api/broadcasts/:id`        | Cancela disparo            |

**Corpo do Broadcast:**

```json
{
  "type": "direct",
  "agent_id": "uuid",
  "target_leads": ["uuid1", "uuid2"],
  "message_template": "Olá {name}, tudo bem? ...",
  "scheduled_at": "2026-02-25T10:00:00Z",
  "min_delay_seconds": 15,
  "max_delay_seconds": 90,
  "simulate_typing": true
}
```

### 3.6 Dashboard / Métricas

| Método | Endpoint                          | Descrição                               |
| ------- | --------------------------------- | ----------------------------------------- |
| GET     | `/api/dashboard/kpis`           | KPIs globais (leads, conversão, receita) |
| GET     | `/api/dashboard/funnel`         | Dados do gráfico de funil                |
| GET     | `/api/dashboard/messages-chart` | Enviadas vs Recebidas por dia             |
| GET     | `/api/dashboard/agents-ranking` | Performance por agente                    |

### 3.7 Configurações

| Método | Endpoint                          | Descrição                      |
| ------- | --------------------------------- | -------------------------------- |
| GET     | `/api/settings`                 | Configurações do usuário      |
| PUT     | `/api/settings`                 | Atualiza configurações         |
| POST    | `/api/settings/test-connection` | Testa conexão com Evolution API |

---

## 🤖 4. Motor de IA — Fluxo de Processamento

### 4.1 Fluxo de Mensagem Recebida

```
Mensagem chega (WhatsApp)
    │
    ▼
Evolution API recebe
    │
    ▼ Webhook POST
    │
Backend recebe webhook
    │
    ├─► Salva em `messages` (direction: inbound)
    ├─► Registra em `activity_logs`
    ├─► Emite evento WebSocket → Frontend atualiza Inbox
    │
    ▼
Verifica se lead existe (by phone)
    │
    ├─ NÃO → Cria lead na coluna "lead"
    │
    ├─ SIM → Carrega contexto:
    │         - Persona do agente
    │         - Últimas 20 mensagens
    │         - Stage atual do lead
    │         - Valor do negócio
    │         - Tags
    │
    ▼
Verifica se chat está em "takeover humano"
    │
    ├─ SIM → Não processa IA, apenas notifica humano
    │
    ├─ NÃO → Envia para LLM com System Prompt:
    │
    ▼
┌─────────────────────────────────────────────────┐
│              SYSTEM PROMPT DA LLM               │
│                                                 │
│  Você é {agent.name}.                          │
│  {agent.persona}                                │
│                                                 │
│  Produto: {agent.product}                       │
│  Link de pagamento: {agent.payment_link}        │
│  Modo: {agent.mode}                             │
│  Stage atual: {lead.stage}                      │
│                                                 │
│  TOOLS DISPONÍVEIS:                             │
│  - moveToStage(stage): Move lead no funil       │
│  - addTag(tag): Adiciona etiqueta               │
│  - setDealValue(value): Define valor do negócio │
│  - sendPaymentLink(): Envia link de pagamento   │
│  - markAsLost(reason): Marca como perdido       │
│  - requestHumanTakeover(reason): Pede ajuda     │
│                                                 │
│  REGRAS:                                        │
│  1. Responda APENAS em português brasileiro     │
│  2. Nunca revele que é uma IA                   │
│  3. Seja natural e conversacional               │
│  4. Se o lead disser "não" 3x, marque perdido   │
│  5. Se pedir para falar com humano, faça        │
│     requestHumanTakeover                        │
└─────────────────────────────────────────────────┘
    │
    ▼
LLM retorna resposta + tool calls
    │
    ├─► Executa tool calls:
    │   ├─ moveToStage → UPDATE leads SET stage = ?
    │   │   └─► Emite WebSocket: "kanban_update"
    │   ├─ addTag → UPDATE leads SET tags = array_append(tags, ?)
    │   ├─ setDealValue → UPDATE leads SET deal_value = ?
    │   ├─ sendPaymentLink → Envia msg com link
    │   └─ markAsLost → UPDATE leads SET stage = 'lost'
    │
    ├─► Salva resposta em `messages` (direction: outbound, sender: ai)
    ├─► Envia resposta via Evolution API (POST /message/sendText)
    ├─► Registra em `activity_logs`
    └─► Emite WebSocket → Frontend atualiza
```

### 4.2 Modos de Atuação

| Modo                  | Comportamento                                                                    |
| --------------------- | -------------------------------------------------------------------------------- |
| **FULL**        | IA faz tudo: prospecta, qualifica, negocia, envia link de pagamento, fecha venda |
| **PROSPECTING** | IA apenas prospecta e qualifica. Ao qualificar, faz `requestHumanTakeover`     |
| **ATTENDING**   | IA não prospecta. Só responde quando o lead inicia conversa. Ideal para SAC    |

### 4.3 Tool Calling — Definição para OpenAI

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "moveToStage",
        "description": "Move o lead para uma nova etapa do funil de vendas",
        "parameters": {
          "type": "object",
          "properties": {
            "stage": {
              "type": "string",
              "enum": ["lead", "cadence", "connected", "qualified", "converted", "lost"]
            },
            "reason": { "type": "string" }
          },
          "required": ["stage"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "addTag",
        "description": "Adiciona uma etiqueta ao lead",
        "parameters": {
          "type": "object",
          "properties": {
            "tag": { "type": "string" }
          },
          "required": ["tag"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "setDealValue",
        "description": "Define o valor do negócio em reais",
        "parameters": {
          "type": "object",
          "properties": {
            "value": { "type": "number" }
          },
          "required": ["value"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "sendPaymentLink",
        "description": "Envia o link de pagamento configurado para o lead"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "markAsLost",
        "description": "Marca o lead como perdido",
        "parameters": {
          "type": "object",
          "properties": {
            "reason": { "type": "string" }
          },
          "required": ["reason"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "requestHumanTakeover",
        "description": "Solicita intervenção humana na conversa",
        "parameters": {
          "type": "object",
          "properties": {
            "reason": { "type": "string" }
          },
          "required": ["reason"]
        }
      }
    }
  ]
}
```

---

## 🔄 5. WebSocket Events (Socket.io)

### 5.1 Eventos do Servidor → Frontend

| Evento                 | Payload                               | Quando                                      |
| ---------------------- | ------------------------------------- | ------------------------------------------- |
| `new_message`        | `{ lead_id, message }`              | Nova mensagem chegou ou foi enviada pela IA |
| `kanban_update`      | `{ lead_id, from_stage, to_stage }` | Lead mudou de coluna no funil               |
| `lead_created`       | `{ lead }`                          | Novo lead criado (import, grupo, orgânico) |
| `lead_updated`       | `{ lead_id, changes }`              | Lead atualizado (tags, valor, etc.)         |
| `agent_status`       | `{ agent_id, is_connected }`        | Status de conexão do agente mudou          |
| `broadcast_progress` | `{ broadcast_id, sent, total }`     | Progresso do disparo em massa               |
| `takeover_request`   | `{ lead_id, reason }`               | IA pediu intervenção humana               |
| `notification`       | `{ type, title, body }`             | Notificação genérica para o usuário     |

### 5.2 Eventos do Frontend → Servidor

| Evento               | Payload         | Quando                                       |
| -------------------- | --------------- | -------------------------------------------- |
| `join_room`        | `{ user_id }` | Frontend conecta e entra na sala do usuário |
| `subscribe_lead`   | `{ lead_id }` | Usuário abriu chat de um lead específico   |
| `unsubscribe_lead` | `{ lead_id }` | Usuário saiu do chat                        |
| `typing`           | `{ lead_id }` | Humano está digitando                       |

---

## ⏰ 6. Cronjobs / Rotinas Agendadas

### 6.1 Cadência Automática

```text
Intervalo: A cada 5 minutos
Lógica:
  1. SELECT * FROM leads WHERE stage = 'cadence' 
     AND next_contact_at <= NOW() AND is_paused = false
  2. Para cada lead:
     a. Incrementa cadence_step
     b. Se cadence_step > max_attempts → moveToStage('lost')
     c. Senão → Monta prompt de prospecção #N
     d. Envia via Evolution API
     e. Atualiza next_contact_at = NOW() + intervalo_randomico
```

### 6.2 Limpeza de Leads Inativos

```text
Intervalo: Diariamente às 03:00
Lógica:
  1. Leads em 'connected' sem resposta há 7 dias → mover para 'lost'
  2. Leads em 'cadence' que excederam max_attempts → mover para 'lost'
```

### 6.3 Processamento de Broadcasts

```text
Intervalo: A cada 30 segundos
Lógica:
  1. SELECT * FROM broadcasts WHERE status = 'running'
  2. Para cada broadcast:
     a. Pega próximo destinatário não enviado
     b. Envia via Evolution API
     c. Aguarda delay randomizado (min_delay ~ max_delay)
     d. Atualiza sent_count
     e. Se todos enviados → status = 'completed'
```

### 6.4 Sincronização de Status

```text
Intervalo: A cada 2 minutos
Lógica:
  1. Para cada agente ativo:
     a. GET /instance/connectionState na Evolution API
     b. Atualiza is_connected no banco
     c. Emite agent_status via WebSocket
```

---

## 🔗 7. Integração com Evolution API

### 7.1 Endpoints Utilizados

| Ação                 | Método | Endpoint Evolution                                |
| ---------------------- | ------- | ------------------------------------------------- |
| Criar instância       | POST    | `/instance/create`                              |
| Conectar (QR Code)     | GET     | `/instance/connect/{instance}`                  |
| Status da conexão     | GET     | `/instance/connectionState/{instance}`          |
| Enviar texto           | POST    | `/message/sendText/{instance}`                  |
| Enviar mídia          | POST    | `/message/sendMedia/{instance}`                 |
| Listar grupos          | GET     | `/group/fetchAllGroups/{instance}`              |
| Participantes do grupo | GET     | `/group/participants/{instance}?groupJid={jid}` |
| Enviar para grupo      | POST    | `/message/sendText/{instance}` (com groupJid)   |
| Configurar webhook     | POST    | `/webhook/set/{instance}`                       |

### 7.2 Configuração de Webhooks

```json
POST /webhook/set/{instance}
{
  "url": "https://seu-backend.com/api/webhooks/evolution",
  "webhook_by_events": true,
  "events": [
    "MESSAGES_UPSERT",
    "MESSAGES_UPDATE", 
    "CONNECTION_UPDATE",
    "QRCODE_UPDATED"
  ]
}
```

### 7.3 Payload do Webhook `MESSAGES_UPSERT`

```json
{
  "event": "messages.upsert",
  "instance": "agent-carlos",
  "data": {
    "key": {
      "remoteJid": "5511999990001@s.whatsapp.net",
      "fromMe": false,
      "id": "3EB0A1B2C3D4"
    },
    "message": {
      "conversation": "Olá, quero saber mais sobre o produto"
    },
    "messageTimestamp": 1740000000,
    "pushName": "João Silva"
  }
}
```

---

## 🛡️ 8. Segurança

### 8.1 Autenticação

- **Supabase Auth** para login/registro de usuários
- **JWT** em todas as requisições API
- **RLS (Row Level Security)** em todas as tabelas — cada usuário só acessa seus dados

### 8.2 Criptografia de Chaves

- API Keys (Evolution, OpenAI) são criptografadas no banco com `pgcrypto`
- Nunca expostas no frontend — apenas usadas nas Edge Functions

### 8.3 Rate Limiting

- Limite de 100 req/min por usuário na API
- Limite de envio do Evolution API respeitado (para evitar ban do WhatsApp)

### 8.4 Validação

- Todos os inputs validados com Zod no backend
- Sanitização de HTML/scripts em mensagens
- Phone numbers normalizados para formato E.164

---

## 📊 9. Queries para Dashboard (KPIs)

### Total de Leads

```sql
SELECT COUNT(*) FROM leads WHERE user_id = $1;
```

### Taxa de Conversão

```sql
SELECT 
  ROUND(
    COUNT(*) FILTER (WHERE stage = 'converted')::decimal / 
    NULLIF(COUNT(*), 0) * 100, 1
  ) as conversion_rate
FROM leads WHERE user_id = $1;
```

### Receita Gerada

```sql
SELECT COALESCE(SUM(deal_value), 0) as total_revenue
FROM leads WHERE user_id = $1 AND stage = 'converted';
```

### Funil de Vendas

```sql
SELECT stage, COUNT(*) as count
FROM leads WHERE user_id = $1
GROUP BY stage
ORDER BY CASE stage
  WHEN 'lead' THEN 1
  WHEN 'cadence' THEN 2
  WHEN 'connected' THEN 3
  WHEN 'qualified' THEN 4
  WHEN 'converted' THEN 5
  WHEN 'lost' THEN 6
END;
```

### Mensagens por Dia (últimos 7 dias)

```sql
SELECT 
  DATE(created_at) as day,
  COUNT(*) FILTER (WHERE direction = 'outbound') as sent,
  COUNT(*) FILTER (WHERE direction = 'inbound') as received
FROM messages m
JOIN leads l ON l.id = m.lead_id
WHERE l.user_id = $1 AND m.created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY day;
```

### Ranking de Agentes

```sql
SELECT 
  a.name,
  a.leads_handled,
  a.leads_converted,
  ROUND(a.leads_converted::decimal / NULLIF(a.leads_handled, 0) * 100, 1) as rate
FROM agents a
WHERE a.user_id = $1 AND a.leads_handled > 0
ORDER BY rate DESC;
```

---

## 🚀 10. Deploy e Infraestrutura

### Stack Recomendada

| Componente           | Tecnologia                                                 |
| -------------------- | ---------------------------------------------------------- |
| Banco de Dados       | Supabase PostgreSQL                                        |
| Auth                 | Supabase Auth                                              |
| API / Edge Functions | Supabase Edge Functions (Deno)                             |
| WebSocket Gateway    | Servidor Node.js dedicado (Socket.io) ou Supabase Realtime |
| LLM                  | OpenAI GPT-4o (via API)                                    |
| WhatsApp             | Evolution API (self-hosted ou cloud)                       |
| Fila de Jobs         | pg_cron (Supabase) ou BullMQ (Redis)                       |
| Storage              | Supabase Storage (mídia recebida)                         |

### Variáveis de Ambiente (Secrets)

```text
EVOLUTION_API_URL=https://api.evolution.example.com
EVOLUTION_API_KEY=sua-chave-aqui
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
WEBHOOK_SECRET=segredo-para-validar-webhooks
```

---

## 📋 11. Checklist de Implementação

### Fase 1 — Fundação

- [ ] Setup do banco com todas as tabelas e RLS
- [ ] Autenticação (login, registro, recuperação de senha)
- [ ] CRUD de Agentes
- [ ] CRUD de Leads
- [ ] CRUD de Configurações (API Keys)

### Fase 2 — Integração WhatsApp

- [ ] Integração com Evolution API (criar instância, QR Code)
- [ ] Recebimento de webhooks (messages.upsert)
- [ ] Envio de mensagens (sendText, sendMedia)
- [ ] Sync de status de conexão

### Fase 3 — Motor de IA

- [ ] Processamento de mensagens com LLM
- [ ] Tool Calling (moveToStage, addTag, etc.)
- [ ] System prompt dinâmico por agente
- [ ] Cadência automática (cronjob)

### Fase 4 — Tempo Real

- [ ] WebSocket gateway (ou Supabase Realtime)
- [ ] Eventos de Kanban em tempo real
- [ ] Inbox com atualizações live
- [ ] Notificações de takeover

### Fase 5 — Grupos e Broadcast

- [ ] Sincronização de grupos
- [ ] Extração de participantes
- [ ] Motor de broadcast com delays randomizados
- [ ] Simulação de digitação

### Fase 6 — Dashboard e Métricas

- [ ] KPIs em tempo real
- [ ] Gráfico de funil
- [ ] Evolução de mensagens
- [ ] Ranking de agentes

---

> **Este documento deve ser usado como referência principal para a construção do backend do Wappi. Cada módulo descrito aqui corresponde diretamente a uma tela/funcionalidade do frontend já implementado.**
