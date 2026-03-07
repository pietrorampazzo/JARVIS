
import { chromium } from "patchright";
import fs from "fs";

async function run() {
    const userDataDir = "C:\\Users\\pietr\\AppData\\Local\\notebooklm-mcp\\Data\\chrome_profile";
    const notebookUrl = "https://notebooklm.google.com/notebook/2592b46f-b4bd-495c-9255-f09271e99b8b";
    const pdfPath = "C:\\Users\\pietr\\OneDrive\\.vscode\\arte_\\DOWNLOADS\\CATALOGOS\\FOLDERS\\Yamaha - Cordas - Baterias - Sopros e Arcos.pdf";

    console.log("🚀 Launching visible browser...");
    const context = await chromium.launchPersistentContext(userDataDir, {
        headless: false,
        channel: "chrome",
        args: ["--disable-blink-features=AutomationControlled"]
    });

    try {
        const page = await context.newPage();
        console.log(`🌐 Navigating...`);
        await page.goto(notebookUrl, { waitUntil: "domcontentloaded", timeout: 60000 });

        console.log("⌛ Waiting for stabilization...");
        await new Promise(r => setTimeout(r, 15000));
        await page.screenshot({ path: "step1-nav.png" });

        console.log("🔍 Checking for button...");
        const addBtn = page.locator('button:has-text("Adicionar fontes")').first();
        if (await addBtn.count() > 0) {
            console.log("🖱️ Clicking Add Button...");
            await addBtn.click();
        } else {
            console.log("⚠️ Button not found by text, trying by aria-label...");
            await page.click('[aria-label*="Adicionar fonte"]');
        }

        await new Promise(r => setTimeout(r, 3000));
        await page.screenshot({ path: "step2-menu.png" });

        console.log("🖱️ Clicking Local Files...");
        await page.click('text="Arquivos locais", text="Enviar arquivos"');

        await new Promise(r => setTimeout(r, 3000));
        console.log("📤 Injecting PDF...");
        await page.setInputFiles('input[type="file"]', pdfPath);
        console.log("✅ Injected!");

        console.log("⌛ Final wait (30s)...");
        await new Promise(r => setTimeout(r, 30000));
        await page.screenshot({ path: "step3-done.png" });
        console.log("🎉 Done!");

    } catch (err) {
        console.error("❌ Error:", err);
        try { await page.screenshot({ path: "step-err.png" }); } catch { }
    } finally {
        await context.close();
    }
}

run();
