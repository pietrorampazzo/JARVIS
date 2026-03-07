
import { BrowserSession } from "./src/session/browser-session.js";
import { AuthManager } from "./src/auth/auth-manager.js";
import { SharedContextManager } from "./src/session/shared-context-manager.js";
import { log } from "./src/utils/logger.js";
import path from "path";

async function runUpload() {
    const notebookUrl = "https://notebooklm.google.com/notebook/2592b46f-b4bd-495c-9255-f09271e99b8b";
    const pdfPath = "C:\\Users\\pietr\\OneDrive\\.vscode\\arte_\\DOWNLOADS\\CATALOGOS\\FOLDERS\\Yamaha - Cordas - Baterias - Sopros e Arcos.pdf";

    log.info("🚀 Starting PDF upload to JARVIS...");

    const authManager = new AuthManager();
    const contextManager = new SharedContextManager(authManager);
    const session = new BrowserSession("upload-session", contextManager, authManager, notebookUrl);

    try {
        await session.init();
        log.info("🌐 Session initialized. Uploading PDF...");

        await session.addSource(pdfPath, (msg) => {
            console.log(`[PROGRESS] ${msg}`);
            return Promise.resolve();
        });

        log.success("✅ PDF upload completed successfully!");

    } catch (error) {
        log.error(`❌ Upload failed: ${error}`);
    } finally {
        await session.close();
        await contextManager.closeContext();
    }
}

runUpload();
