
import { chromium } from "patchright";
import path from "path";
import fs from "fs";

async function run() {
    const userDataDir = "C:\\Users\\pietr\\AppData\\Local\\notebooklm-mcp\\Data\\chrome_profile";
    const statePath = "C:\\Users\\pietr\\AppData\\Local\\notebooklm-mcp\\Data\\browser_state\\state.json";
    const notebookUrl = "https://notebooklm.google.com/notebook/2592b46f-b4bd-495c-9255-f09271e99b8b";
    const pdfPath = "C:\\Users\\pietr\\OneDrive\\.vscode\\arte_\\DOWNLOADS\\CATALOGOS\\FOLDERS\\Yamaha - Cordas - Baterias - Sopros e Arcos.pdf";

    console.log("🚀 Starting FINAL HEADLESS upload...");
    console.log(`📍 State: ${statePath} (${fs.existsSync(statePath) ? 'FOUND' : 'NOT FOUND'})`);
    console.log(`📍 PDF: ${pdfPath} (${fs.existsSync(pdfPath) ? 'FOUND' : 'NOT FOUND'})`);

    if (!fs.existsSync(pdfPath)) {
        console.error("❌ PDF missing. Aborting.");
        process.exit(1);
    }

    const context = await chromium.launchPersistentContext(userDataDir, {
        headless: true,
        channel: "chrome",
        storageState: fs.existsSync(statePath) ? statePath : undefined,
        args: ["--disable-blink-features=AutomationControlled", "--no-sandbox"]
    });

    try {
        const page = await context.newPage();
        console.log(`🌐 Navigating to ${notebookUrl}...`);
        await page.goto(notebookUrl, { waitUntil: "networkidle", timeout: 90000 });

        console.log("📸 Taking check screenshot...");
        await page.screenshot({ path: "check-page-headless.png" });

        // Try to detect if we ARE logged in
        const bodyText = await page.innerText('body');
        if (bodyText.includes("Faça login") || bodyText.includes("Sign in")) {
            console.error("❌ Still on login page. Session state may be invalid.");
            await page.screenshot({ path: "login-error.png" });
            return;
        }

        console.log("🔍 Looking for '+ Adicionar fontes'...");
        const addBtn = page.locator('button:has-text("Adicionar fontes"), [aria-label*="Adicionar fonte"]');
        await addBtn.first().waitFor({ state: 'visible', timeout: 30000 });
        await addBtn.first().click({ force: true });

        console.log("🖱️ Clicking 'Arquivos locais'...");
        const uploadBtn = page.locator('text="Arquivos locais", text="Enviar arquivos", text="Upload"');
        await uploadBtn.first().waitFor({ state: 'visible', timeout: 20000 });
        await uploadBtn.first().click({ force: true });

        console.log("📤 Injecting file...");
        const fileInput = page.locator('input[type="file"]');
        await fileInput.setInputFiles(pdfPath);
        console.log("✅ File injected!");

        console.log("⌛ Waiting 40s for upload...");
        await new Promise(r => setTimeout(r, 40000));

        await page.screenshot({ path: "final-verify-headless.png" });
        console.log("🎉 Process finished!");

    } catch (err) {
        console.error("❌ automation error:", err);
        try { await page.screenshot({ path: "last-err.png" }); } catch { }
    } finally {
        await context.close();
    }
}

run();
