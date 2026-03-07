
import { BrowserSession } from "./src/session/browser-session.js";
import { AuthManager } from "./src/auth/auth-manager.js";
import { SharedContextManager } from "./src/session/shared-context-manager.js";
import { log } from "./src/utils/logger.js";
import path from "path";
import fs from "fs";

async function runTest() {
    log.info("🚀 Starting verification test for NotebookLM Management tools...");

    const authManager = new AuthManager();
    const contextManager = new SharedContextManager(authManager);
    const session = new BrowserSession("test-session", contextManager, authManager, "https://notebooklm.google.com/");

    try {
        // 0. Initialize session
        await session.init();

        // 1. Create a notebook
        const notebookUrl = await session.createNotebook("JARVIS Auto Test", (msg) => {
            console.log(`[PROGRESS] ${msg}`);
            return Promise.resolve();
        });
        log.success(`Notebook created: ${notebookUrl}`);

        // 2. Update instructions
        await session.updateInstructions("Sempre responda em Português do Brasil de forma concisa.", (msg) => {
            console.log(`[PROGRESS] ${msg}`);
            return Promise.resolve();
        });
        log.success("Instructions updated");

        // 3. Add a source (dummy text file)
        const testFilePath = path.resolve("test-source.txt");
        // Create a dummy file
        fs.writeFileSync(testFilePath, "Este é um arquivo de teste para o JARVIS.");

        await session.addSource(testFilePath, (msg) => {
            console.log(`[PROGRESS] ${msg}`);
            return Promise.resolve();
        });
        log.success("Source added");

    } catch (error) {
        log.error(`❌ Test failed: ${error}`);
    } finally {
        await session.close();
        await contextManager.closeContext();
    }
}

runTest();
