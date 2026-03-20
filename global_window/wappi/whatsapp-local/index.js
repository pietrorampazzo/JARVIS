const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const qrPath = path.join(__dirname, '..', 'public', 'qr.png');
const statusPath = path.join(__dirname, '..', 'public', 'whatsapp-status.json');

const updateStatus = (status, data = {}) => {
    const statusData = { status, timestamp: new Date().toISOString(), ...data };
    try {
        fs.writeFileSync(statusPath, JSON.stringify(statusData, null, 2));
    } catch (e) {
        console.error('Falha ao gravar status:', e.message);
    }
};

async function startWhatsApp() {
    console.log('Iniciando browser...');
    updateStatus('STARTING');

    const browser = await chromium.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    });
    const page = await context.newPage();

    // Detecta se o browser foi fechado manualmente
    browser.on('disconnected', () => {
        console.log('Browser fechado pelo usuário.');
        updateStatus('DISCONNECTED');
        process.exit(0);
    });

    console.log('Navegando para o WhatsApp Web...');
    await page.goto('https://web.whatsapp.com', { waitUntil: 'domcontentloaded', timeout: 60000 });
    console.log('Página carregada, aguardando QR Code ou login...');
    updateStatus('WAITING_QR');

    const monitorLogin = async () => {
        while (true) {
            try {
                // Seletor específico do canvas do QR na nova versão do WhatsApp Web
                const qrCanvas = page.locator('canvas[aria-label]').first();
                const isQrVisible = await qrCanvas.isVisible({ timeout: 2000 }).catch(() => false);

                if (isQrVisible) {
                    console.log('QR Code detectado! Capturando screenshot...');
                    await qrCanvas.screenshot({ path: qrPath });
                    console.log(`QR Code salvo em: ${qrPath}`);
                    updateStatus('QR_AVAILABLE');
                } else {
                    // Tenta detectar se já está logado (barra de pesquisa ou lista de conversas)
                    const chatSidebar = page.locator('#pane-side, [data-testid="chat-list"]').first();
                    const isLoggedIn = await chatSidebar.isVisible({ timeout: 2000 }).catch(() => false);

                    if (isLoggedIn) {
                        console.log('✅ LOGIN DETECTADO! WhatsApp conectado com sucesso!');
                        updateStatus('CONNECTED');
                        if (fs.existsSync(qrPath)) fs.unlinkSync(qrPath);
                        console.log('Browser mantido aberto. Pressione Ctrl+C para encerrar.');
                        // Mantém o processo vivo
                        await new Promise(() => { });
                        break;
                    } else {
                        // Fallback: tenta pegar qualquer canvas (versões diferentes do WhatsApp Web)
                        const anyCanvas = page.locator('canvas').first();
                        const hasCanvas = await anyCanvas.isVisible({ timeout: 1000 }).catch(() => false);
                        if (hasCanvas) {
                            await anyCanvas.screenshot({ path: qrPath });
                            console.log('QR Code (fallback) capturado!');
                            updateStatus('QR_AVAILABLE');
                        } else {
                            console.log('Aguardando carregamento ou QR Code...');
                        }
                    }
                }
            } catch (err) {
                if (err.message.includes('Target') || err.message.includes('closed')) {
                    console.log('Browser encerrado.');
                    updateStatus('DISCONNECTED');
                    process.exit(0);
                }
                console.error('Erro:', err.message);
            }

            await new Promise(resolve => setTimeout(resolve, 3000));
        }
    };

    await monitorLogin();
}

startWhatsApp().catch(err => {
    console.error('Erro fatal ao iniciar WhatsApp Local:', err.message);
    updateStatus('ERROR', { message: err.message });
});
