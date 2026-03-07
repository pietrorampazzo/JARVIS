
import { chromium } from "patchright";
import fs from "fs";

async function diag() {
    const userDataDir = "C:\\Users\\pietr\\AppData\\Local\\notebooklm-mcp\\Data\\chrome_profile";
    const notebookUrl = "https://notebooklm.google.com/notebook/2592b46f-b4bd-495c-9255-f09271e99b8b";

    console.log("🚀 Launching DIAG browser (HEADLESS)...");
    const context = await chromium.launchPersistentContext(userDataDir, {
        headless: true,
        channel: "chrome",
        args: ["--disable-blink-features=AutomationControlled"]
    });

    try {
        const page = await context.newPage();
        console.log(`🌐 Navigating to ${notebookUrl}...`);
        await page.goto(notebookUrl, { waitUntil: "networkidle", timeout: 60000 });

        console.log("⌛ Waiting 10s...");
        await new Promise(r => setTimeout(r, 10000));

        await page.screenshot({ path: "diag-headless.png", fullPage: true });
        console.log("📸 Screenshot saved to diag-headless.png");

    } catch (error) {
        console.error("❌ Error:", error);
    } finally {
        await context.close();
    }
}

diag();
