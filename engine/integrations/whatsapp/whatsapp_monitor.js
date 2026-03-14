const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const { QRCodeTerminal } = require('qrcode-terminal');
const qrcode = require('qrcode-terminal');
const pino = require('pino');
const fs = require('fs-extra');
const path = require('path');
const { spawn } = require('child_process');
require('dotenv').config();

// ============================================
// CONFIGURAÇÕES
// ============================================
const AUTH_DIR = path.join(__dirname, 'auth_info');
const LOGS_FILE = path.join(__dirname, '../../../logs/events_master.json');
const RAW_LOGS_FILE = path.join(__dirname, '../../../logs/whatsapp_pietro.json');
const GEMINI_SCRIPT = path.join(__dirname, 'prompt_monitor.py');
const CONFIG_FILE = path.join(__dirname, 'config.json');
const CONTACTS_CATALOG_FILE = path.join(__dirname, 'contacts_catalog.json');

let config = { MONITORED_GROUPS: {}, MONITOR_PRIVATE: true };
let contactsCatalog = {};

async function loadConfig() {
    try {
        if (await fs.pathExists(CONFIG_FILE)) {
            config = await fs.readJson(CONFIG_FILE);
        }
        if (await fs.pathExists(CONTACTS_CATALOG_FILE)) {
            contactsCatalog = await fs.readJson(CONTACTS_CATALOG_FILE);
            console.log(`[INIT] ${Object.keys(contactsCatalog).length} Contatos catalogados carregados.`);
        }
    } catch (e) {
        console.error("Erro ao carregar configurações:", e.message);
    }
}
loadConfig();

// ============================================
// AUXILIARES
// ============================================
async function logToJarvis(action, notes = "", impact = 3, area = "relationship_monitoring", category = "whatsapp") {
    try {
        const logs = await fs.readJson(LOGS_FILE);
        const newEntry = {
            timestamp: new Date().toISOString(),
            area: area,
            area_name: "Monitoramento de Relações",
            category: category,
            action: action,
            impact: impact,
            duration_minutes: 0,
            source: "whatsapp_monitor",
            project: "JARVIS",
            notes: notes
        };
        logs.push(newEntry);
        await fs.writeJson(LOGS_FILE, logs, { spaces: 2 });
        console.log(`[JARVIS LOG] ${action}`);
    } catch (error) {
        console.error("Erro ao gravar log no JARVIS:", error.message);
    }
}

async function registrarMensagemOtimizada(sender, type, message) {
    try {
        let logs = [];
        if (await fs.pathExists(RAW_LOGS_FILE)) {
            logs = await fs.readJson(RAW_LOGS_FILE);
        }
        
        // Formato 4 campos conforme solicitado pelo usuário
        logs.push({
            timestamp: new Date().toISOString(),
            sender: sender,
            tipo: type,
            mensagem: message
        });
        
        // Mantém apenas os últimos 2000 logs para evitar explosão de tokens
        if (logs.length > 2000) logs = logs.slice(-2000);

        await fs.writeJson(RAW_LOGS_FILE, logs, { spaces: 2 });
    } catch (error) {
        console.error("Erro ao gravar log otimizado no WhatsApp:", error.message);
    }
}

async function chamarIA(phoneNumber, messageContent, isGroup = false, groupMetadata = null) {
    return new Promise((resolve) => {
        const args = [GEMINI_SCRIPT, phoneNumber, messageContent, isGroup ? "true" : "false", JSON.stringify(groupMetadata || {})];
        const pyProcess = spawn('python', args);

        let stdoutData = '';
        pyProcess.stdout.on('data', (data) => { stdoutData += data.toString(); });
        pyProcess.on('close', (code) => {
            if (code !== 0) resolve(null);
            try {
                const result = JSON.parse(stdoutData.trim());
                resolve(result);
            } catch (e) {
                resolve(null);
            }
        });
    });
}

// ============================================
// BAILEYS CORE
// ============================================
async function startMonitor() {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
    const { version } = await fetchLatestBaileysVersion();

    const sock = makeWASocket({
        version,
        auth: state,
        logger: pino({ level: 'silent' }),
        printQRInTerminal: true,
        browser: ['JARVIS Monitor', 'Chrome', '1.0.0']
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        if (qr) {
            console.log('Escanear QR Code para iniciar o monitoramento JARVIS:');
            qrcode.generate(qr, { small: true });
        }
        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            if (shouldReconnect) startMonitor();
        } else if (connection === 'open') {
            console.log('✅ JARVIS WhatsApp Monitor Conectado!');
            logToJarvis("Monitoramento WhatsApp iniciado", "Sessão estabelecida com sucesso");
            
            // Listar grupos logo após a conexão
            listarGrupos(sock);
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        if (m.type !== 'notify') return;

        for (const msg of m.messages) {
            if (!msg.message || msg.key.fromMe) continue;

            const remoteJid = msg.key.remoteJid;
            
            // Filtro de Segurança: Ignorar Newsletters e Canais
            if (remoteJid.endsWith('@newsletter') || remoteJid.endsWith('@broadcast')) continue;

            const isGroup = remoteJid.endsWith('@g.us');
            const groupConfig = config.MONITORED_GROUPS[remoteJid];

            // Filtro: Se for grupo, monitora apenas se estiver na config.
            // Se for privado, monitora se MONITOR_PRIVATE for true.
            if (isGroup && !groupConfig) continue;
            if (!isGroup && !config.MONITOR_PRIVATE) continue;
            if (msg.key.fromMe && !isGroup) continue; // Ignora minhas mensagens no privado, mas talvez queira monitorar no grupo.

            const sender = isGroup ? msg.key.participant : remoteJid;
            const phoneNumber = sender.replace(/\D/g, '');
            const contactInfo = contactsCatalog[phoneNumber];
            
            const text = msg.message.conversation || msg.message.extendedTextMessage?.text || "";
            if (!text) continue;

            const senderLabel = contactInfo ? contactInfo.name : (isGroup ? `Grupo: ${groupConfig.name}` : sender);
            const senderType = contactInfo ? contactInfo.type : (isGroup ? "grupo" : "desconhecido");

            console.log(`[MONITOR] ${senderLabel} (${senderType}): ${text.slice(0, 50)}...`);

            // Registrar log otimizado (4 campos: timestamp, sender, tipo, mensagem)
            await registrarMensagemOtimizada(senderLabel, senderType, text);

            // Análise via IA (Filtro de Oportunidades)
            const analise = await chamarIA(sender, text, isGroup, groupConfig || { jid: remoteJid });

            const isPrioridade = analise && analise.importante;
            const isVip = contactInfo && (contactInfo.type === 'cliente' || contactInfo.type === 'socio');

            if (isPrioridade || isVip) {
                let titulo = analise?.titulo || `Mensagem de ${senderType}`;
                if (isVip) titulo = `[PRIORIDADE: ${senderType.toUpperCase()}] ${senderLabel}: ${text.slice(0, 20)}...`;

                await logToJarvis(
                    titulo,
                    `De: ${senderLabel} | Tipo: ${senderType} | Conteúdo: ${text} | Análise: ${analise ? analise.motivo : 'Prioridade VIP'}`,
                    isVip ? 5 : (analise ? analise.impacto : 3),
                    analise ? analise.area : (groupConfig ? groupConfig.area : "relationship_monitoring"),
                    isVip ? `priority_${senderType}` : (groupConfig ? groupConfig.category : "whatsapp_private")
                );
            }
        }
    });
    
    // Comando para listar grupos
    // sock.ev.on('groups.upsert', (groups) => { console.log("Novos Grupos:", groups); });
}

async function listarGrupos(sock) {
    try {
        console.log("\n--- LISTANDO GRUPOS PARA MONITORAMENTO ---");
        await logToJarvis("Iniciando listagem de grupos", "Buscando metadados de grupos do WhatsApp");
        
        const groups = await sock.groupFetchAllParticipating();
        const infoGrupos = Object.values(groups).map(g => ({
            id: g.id,
            subject: g.subject
        }));
        
        console.table(infoGrupos);
        console.log("-------------------------------------------\n");
        
        const reportPath = path.join(__dirname, 'grupos_disponiveis.json');
        await fs.writeJson(reportPath, infoGrupos, { spaces: 2 });
        await logToJarvis("Grupos listados com sucesso", `Encontrados ${infoGrupos.length} grupos. Arquivo: ${reportPath}`);
    } catch (error) {
        console.error("Erro ao listar grupos:", error.message);
        await logToJarvis("Falha ao listar grupos", error.message, 4);
    }
}

startMonitor();
