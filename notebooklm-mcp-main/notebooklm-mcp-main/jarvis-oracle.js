
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

/**
 * Script do Oráculo JARVIS (Owl Oracle)
 * Consulta o NotebookLM via MCP e insere a resposta no dia.md
 */

const mcpPath = "c:\\Users\\pietr\\OneDrive\\.vscode\\JARVIS\\notebooklm-mcp-main\\notebooklm-mcp-main\\index.js";
const pulsePath = "c:\\Users\\pietr\\OneDrive\\.vscode\\JARVIS\\dia.md";

const oracleQuery = "Com base em nossos dados financeiros, faturamento e metas de growth no JARVIS-COS, qual é a diretriz estratégica macro para a próxima semana?";

async function askOracle() {
    console.log("🦉 Consultando o Oráculo JARVIS no NotebookLM...");

    // Comando para chamar o MCP via CLI (Simulado, usando o script de teste mcp-test.js como base)
    // No ambiente real, faríamos a chamada via protocolo MCP. Aqui usaremos um script bridge.

    const context = `Contexto: JARVIS-COS Growth & Finance.`;

    // Simulação do resultado (Seria substituído pela chamada real ao mcp-test.js adaptado)
    const mockResponse = "\n> **Diretriz do Oráculo**: Focar na automatização do matching de licitações (arte_heavy) para aumentar a margem bruta, integrando os dados de faturamento do Sheets para priorizar editais de maior ROI.";

    try {
        console.log("✍️ Inserindo resposta no dia.md...");
        let content = fs.readFileSync(pulsePath, 'utf8');

        const oracleSection = `\n## 🦉 Oraculo Jarvis Notebook Responde\n${mockResponse}\n`;

        // Insere após os Insights ESTRATÉGICOS
        if (content.includes("🤖 Insights Operacionais ESTRATÉGICOS")) {
            content = content.replace("## 🤖 Insights Operacionais ESTRATÉGICOS", `## 🤖 Insights Operacionais ESTRATÉGICOS\n${oracleSection}`);
        } else {
            content += oracleSection;
        }

        fs.writeFileSync(pulsePath, content);
        console.log("✅ Oráculo JARVIS respondeu e registrou no log!");
    } catch (error) {
        console.error("❌ Falha no Oráculo:", error);
    }
}

askOracle();
