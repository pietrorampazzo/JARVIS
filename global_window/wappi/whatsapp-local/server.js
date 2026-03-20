const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

const statusPath = path.join(__dirname, '..', 'public', 'whatsapp-status.json');

let whatsappProcess = null;

const isRunning = () => {
    return whatsappProcess && !whatsappProcess.killed;
};

// GET /status - retorna o status atual
app.get('/status', (req, res) => {
    try {
        if (fs.existsSync(statusPath)) {
            const data = JSON.parse(fs.readFileSync(statusPath, 'utf8'));
            res.json({ ...data, processRunning: isRunning() });
        } else {
            res.json({ status: 'DISCONNECTED', processRunning: false });
        }
    } catch {
        res.json({ status: 'DISCONNECTED', processRunning: false });
    }
});

// POST /start - inicia o script do WhatsApp
app.post('/start', (req, res) => {
    if (isRunning()) {
        return res.json({ success: true, message: 'Processo já está rodando' });
    }

    const scriptPath = path.join(__dirname, 'index.js');
    console.log('🚀 Iniciando WhatsApp Local...');

    whatsappProcess = spawn('node', [scriptPath], {
        detached: false,
        stdio: 'pipe',
    });

    whatsappProcess.stdout.on('data', (data) => console.log('[WA]', data.toString().trim()));
    whatsappProcess.stderr.on('data', (data) => console.error('[WA ERR]', data.toString().trim()));
    whatsappProcess.on('exit', (code) => {
        console.log(`[WA] Processo encerrado com código: ${code}`);
        whatsappProcess = null;
    });

    res.json({ success: true, message: 'WhatsApp Local iniciado!' });
});

// POST /stop - para o processo
app.post('/stop', (req, res) => {
    if (whatsappProcess && !whatsappProcess.killed) {
        whatsappProcess.kill('SIGTERM');
        whatsappProcess = null;
        // Limpa o status
        try {
            fs.writeFileSync(statusPath, JSON.stringify({ status: 'DISCONNECTED', timestamp: new Date().toISOString() }));
        } catch { }
        return res.json({ success: true, message: 'Processo encerrado' });
    }
    res.json({ success: false, message: 'Nenhum processo rodando' });
});

app.listen(PORT, () => {
    console.log(`✅ Servidor WhatsApp Local rodando em http://localhost:${PORT}`);
});
