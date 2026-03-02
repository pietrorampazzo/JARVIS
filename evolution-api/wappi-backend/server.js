import 'dotenv/config';
import express from 'express';
import http from 'http';
import cors from 'cors';
import { Server } from 'socket.io';
import { createClient } from '@supabase/supabase-js';
import axios from 'axios';
import cron from 'node-cron';

// Configurações Globais (.env)
const PORT = process.env.PORT || 4000;
const EVOLUTION_API_URL = process.env.EVOLUTION_API_URL || 'http://localhost:8080';
const EVOLUTION_API_KEY = process.env.EVOLUTION_API_KEY || '429683C4C977415CAAFCCE10F7D57E11'; // Chave mestra global
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://sua-url.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || 'sua-key';

// Inicializa API e Supabase Admin
const app = express();
app.use(cors());
app.use(express.json());

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY, {
    auth: { autoRefreshToken: false, persistSession: false }
});

const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

// ==========================================
// 1. WEBSOCKET GATEWAY (Real-Time com Frontend)
// ==========================================
io.on('connection', (socket) => {
    console.log(`[WS] Cliente conectado: ${socket.id}`);

    // O Frontend deve enviar join_room com o UUID logado
    socket.on('join_room', ({ user_id }) => {
        socket.join(user_id);
        console.log(`[WS] Cliente ${socket.id} entrou na sala: ${user_id}`);
    });

    // Takeover humano: humano assume conversa
    socket.on('typing', ({ user_id, lead_id }) => {
        socket.to(user_id).emit('notification', {
            type: 'typing', title: 'Atendimento', body: 'Humano assumindo a conversa via painel'
        });
    });

    socket.on('disconnect', () => {
        console.log(`[WS] Cliente ${socket.id} desconectado.`);
    });
});

// ==========================================
// 2. EVOLUTION API RECEIVER (Webhook Listener)
// ==========================================
app.post('/api/webhooks/evolution', async (req, res) => {
    try {
        const { event, instance, data } = req.body;

        // Processamento de Novas Mensagens (Inbound ou Outbound do WhatsApp)
        if (event === 'messages.upsert') {
            const msg = data.message;
            if (!msg) return res.status(200).send('OK');

            const remoteJid = data.key.remoteJid;       // "5511999990001@s.whatsapp.net"
            const phoneClean = remoteJid.split('@')[0]; // "5511999990001"
            const fromMe = data.key.fromMe;
            const textMessage = msg.conversation || msg.extendedTextMessage?.text || '';

            console.log(`\n[WHATSAPP] [${instance}] de ${phoneClean}: ${textMessage}`);

            // -------------------------------------------------------------
            // WORKFLOW DA INJEÇÃO DO CRM:
            // A. Achar o Agente pelo 'instance' (nome da IA)
            // B. Achar o Lead pelo 'phone'. Se não existir, criar Orgânico.
            // C. Salvar Histórico (Message Table)
            // D. Notificar Frontend (Socket)
            // E. Acionar LLM se fromMe = false e HumanTakeover = false
            // -------------------------------------------------------------

            const { data: agent } = await supabase.from('agents').select('*').eq('whatsapp_instance_id', instance).single();
            if (!agent) {
                console.log(`[WARN] Mensagem recebida de agente não mapeado no Supabase: ${instance}`);
                return res.status(200).send('OK');
            }

            // Procura Lead pelo telefone e Agent ID
            let { data: lead } = await supabase.from('leads').select('*').eq('phone', phoneClean).eq('agent_id', agent.id).single();
            let isNewLead = false;

            // Cadastro Orgânico (Lead chegou pelo WhatsApp)
            if (!lead && !fromMe) {
                const fallbackName = data.pushName || `Lead ${phoneClean.slice(-4)}`;
                const { data: newLead, error } = await supabase.from('leads').insert({
                    user_id: agent.user_id,
                    agent_id: agent.id,
                    name: fallbackName,
                    phone: phoneClean,
                    source: 'organic',
                    stage: 'lead'
                }).select().single();

                if (!error && newLead) {
                    lead = newLead;
                    isNewLead = true;
                    // Notifica Kanban no Dashboard: Lead Criado
                    io.to(agent.user_id).emit('lead_created', { lead });
                }
            }

            if (lead && textMessage) {
                // Salva na Tabela de Histórico de Conversa do CRM
                const { data: savedMsg } = await supabase.from('messages').insert({
                    lead_id: lead.id,
                    agent_id: agent.id,
                    direction: fromMe ? 'outbound' : 'inbound',
                    sender: fromMe ? 'system' : 'lead',
                    content: textMessage,
                    status: 'delivered'
                }).select().single();

                // Emite atualização para o Inbox da UI
                io.to(agent.user_id).emit('new_message', { lead_id: lead.id, message: savedMsg });
            }

            // TODO: Motor de Processamento LLM Integrado (Caso 'msg.fromMe' == false)
        }

        // Rotina obrigatória p/ WhatsApp Event Hub: Libera o Worker da Evolution
        res.status(200).send('Webhook processado pela Arquitetura Wappi');
    } catch (error) {
        console.error('Erro Webhook:', error);
        res.status(500).send('Error');
    }
});

// ==========================================
// 3. CRONJOBS (Rotinas Backend Automatizadas)
// ==========================================

// Cron 6.4 - Sincronização de Status do WhatsApp (A cada 2 Minutos)
cron.schedule('*/2 * * * *', async () => {
    console.log('[CRON] Sincronizando status de Agentes na Evolution API...');

    // Busca agentes ativos que possuem uma Instância Wappi atrelada
    const { data: agents } = await supabase.from('agents').select('id, user_id, whatsapp_instance_id').eq('is_active', true);

    if (agents && agents.length > 0) {
        for (const ag of agents) {
            if (!ag.whatsapp_instance_id) continue;

            try {
                const res = await axios.get(`${EVOLUTION_API_URL}/instance/connectionState/${ag.whatsapp_instance_id}`, {
                    headers: { 'apikey': EVOLUTION_API_KEY }
                });

                const currentState = res.data?.instance?.state || 'close';
                const isConnected = currentState === 'open';

                // Atualiza banco e avisa frontend se houver mudança de bolinha verde/vermelha
                await supabase.from('agents').update({ is_connected: isConnected }).eq('id', ag.id);
                io.to(ag.user_id).emit('agent_status', { agent_id: ag.id, is_connected: isConnected });

            } catch (err) {
                // Fallback se Evolution retornar erro 404 (instância apagada/inválida)
                await supabase.from('agents').update({ is_connected: false }).eq('id', ag.id);
                io.to(ag.user_id).emit('agent_status', { agent_id: ag.id, is_connected: false });
            }
        }
    }
});

// Cron 6.1 - Controle de Cadência (A cada 5 minutos)
// Varre funil de todos os Leads prospectando
cron.schedule('*/5 * * * *', () => {
    // Futuramente: Implementar loop para supabase SELECT * FROM leads WHERE stage = 'cadence'
    console.log('[CRON] Cadência verificada.');
});

// ==========================================
// 4. START SERVER
// ==========================================
server.listen(PORT, () => {
    console.log(`🚀 [WAPPI BACKEND SERVER] Ativo na porta ${PORT}`);
    console.log(`🔄 [CRONS] Tarefas agendadas inicializadas`);
});
