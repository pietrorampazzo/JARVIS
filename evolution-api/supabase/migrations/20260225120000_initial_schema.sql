-- --------------------------------------------------------------------------
-- 1. Tabela `agents` — Agentes de IA
-- --------------------------------------------------------------------------
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

-- --------------------------------------------------------------------------
-- 2. Tabela `groups` — Grupos de WhatsApp (Dependência de leads)
-- --------------------------------------------------------------------------
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

-- --------------------------------------------------------------------------
-- 3. Tabela `leads` — Oportunidades / Contatos do CRM
-- --------------------------------------------------------------------------
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

-- --------------------------------------------------------------------------
-- 4. Tabela `messages` — Histórico de Conversas
-- --------------------------------------------------------------------------
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

-- --------------------------------------------------------------------------
-- 5. Tabela `activity_logs` — Log de Atividades do Sistema
-- --------------------------------------------------------------------------
CREATE TABLE activity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  
  action VARCHAR(50) NOT NULL,
  description TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',  -- Dados extras
  
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_activity_lead ON activity_logs(lead_id, created_at DESC);

-- --------------------------------------------------------------------------
-- 6. Tabela `broadcasts` — Disparos em Massa
-- --------------------------------------------------------------------------
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

-- --------------------------------------------------------------------------
-- 7. Tabela `settings` — Configurações do Usuário
-- --------------------------------------------------------------------------
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
