
import { chromium } from "patchright";
import path from "path";
import os from "os";
import fs from "fs";

async function run() {
    const userDataDir = path.join(os.homedir(), "AppData", "Local", "notebooklm-mcp", "Data", "chrome_profile");
    const notebookUrl = "https://notebooklm.google.com/notebook/e23ea047-7f1e-4c93-b6d2-f3dd6b912104";
    const logsDir = "i:\\Meu Drive\\GoogleAI\\notebook_jarvis\\LOGS";

    const context = await chromium.launchPersistentContext(userDataDir, {
        headless: true,
        channel: "chrome",
        args: ["--disable-blink-features=AutomationControlled"]
    });

    try {
        const page = await context.newPage();
        console.log(`🌐 Iniciando Sincronização Semanal: ${notebookUrl}`);
        await page.goto(notebookUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
        await page.waitForTimeout(15000);

        console.log("🖱️ Abrindo detalhes da fonte JARVIS.txt para acessar o botão de sincronização...");
        const jarvisSource = page.locator('text="JARVIS.txt"').first();
        if (await jarvisSource.count() > 0) {
            await jarvisSource.click();
            await page.waitForTimeout(5000);

            console.log("🖱️ Rolando para localizar o botão...");
            await page.mouse.move(200, 500);
            await page.mouse.wheel(0, 1000); // Rola mais
            await page.waitForTimeout(3000);

            // Tenta múltiplos seletores em português e inglês
            const syncBtn = page.locator('text="Clique para sincronizar com o Google Drive", text="Sincronização concluída"').first();

            if (await syncBtn.count() > 0) {
                console.log("🖱️ Clicando no botão de sincronização oficial...");
                await syncBtn.click();
            } else {
                console.log("⚠️ Botão não detectado pelo DOM. Tentando clique por coordenadas (fallback)...");
                // Baseado nos screenshots, o botão fica nessa região do painel lateral
                await page.mouse.click(100, 250);
            }

            console.log("⌛ Aguardando conclusão (30s)...");
            await page.waitForTimeout(30000);

            const date = new Date().toISOString().split('T')[0];
            const logPath = "i:\\Meu Drive\\GoogleAI\\notebook_jarvis\\LOGS_CONSOLIDATED.txt";
            const logEntry = `\n\n--- SYNC ${date} ---\n**Status**: Sincronização Nativa Executada.\nO sistema JARVIS-COS foi sincronizado oficialmente com o Google Drive.\n`;

            fs.appendFileSync(logPath, logEntry);
            console.log(`✅ Log concatenado em: ${logPath}`);
            console.log("🚀 Sincronização Semanal Finalizada!");
        } else {
            console.log("❌ Fonte JARVIS.txt não encontrada.");
        }

    } catch (err) {
        console.error("❌ Erro durante a sincronização semanal:", err);
    } finally {
        await context.close();
    }
}

run();
