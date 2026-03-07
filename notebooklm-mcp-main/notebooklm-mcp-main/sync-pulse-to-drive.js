
import fs from 'fs';
import path from 'path';
import os from 'os';

/**
 * Script para Sincronizar Logs do Pulse (dia.md) para o Drive (LOGS_CONSOLIDATED.txt)
 * Protocolo de Conhecimento Imutável do JARVIS-COS
 */

const pulseFilePath = "c:\\Users\\pietr\\OneDrive\\.vscode\\JARVIS\\dia.md";
const driveLogPath = "i:\\Meu Drive\\GoogleAI\\notebook_jarvis\\LOGS_CONSOLIDATED.txt";

async function syncLogs() {
    try {
        console.log("🔍 Lendo Log Diário do Pulse...");

        if (!fs.existsSync(pulseFilePath)) {
            console.error(`❌ Arquivo Pulse não localizado em: ${pulseFilePath}`);
            return;
        }

        const logContent = fs.readFileSync(pulseFilePath, 'utf8');
        const date = new Date().toLocaleDateString('pt-BR');

        const entryHeader = `\n\n========================================\n📅 LOG DE ATIVIDADE - ${date}\n========================================\n`;
        const consolidatedEntry = entryHeader + logContent;

        console.log("✍️ Concatenando no Drive (Imutável)...");
        fs.appendFileSync(driveLogPath, consolidatedEntry);

        console.log("✅ Sincronia Pulse -> Drive concluída com sucesso!");
    } catch (error) {
        console.error("❌ Erro na sincronia de logs:", error);
    }
}

syncLogs();
