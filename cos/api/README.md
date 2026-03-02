# 🧠 JARVIS C.O.S - Server API (FastAPI)

Este diretório contém o servidor Mestre da rede neural do JARVIS.

## O Que é Isso?
Para obtermos I/O (Input/Output) instantâneo entre diferentes computadores ou Agentes de IA (ex: Seu note de desenvolvimento escrevendo um Log, enquanto o OpenClaw no LenovoPeti está mandando uma resposta no WhatsApp), nós descartamos transferências lerdas usando o OneDrive.
A máquina **LenovoPeti** rodará este servidor FastAPI e concentrará toda a leitura/gravação oficial de arquivos e consulta de pontuação em tempo real.

## Como Iniciar o Servidor (Na LenovoPeti)
Pressione `Win + R`, digite `powershell` e cole:
```powershell
cd C:\Users\pietr\OneDrive\.vscode\JARVIS\cos\api
.\start_server.ps1
```
*(O servidor subirá na porta 8000 e ficará esperando conexões).*

## Como Conectar a sua Máquina de Dev (Antigravity Node)
Na sua máquina pessoal, você configura uma Variável de Ambiente que fará os scripts (como o `event_logger`) pararem de tentar escrever no OneDrive e passarem a enviar um "POST" pra LenovoPeti.

Abra o PowerShell como Administrador na sua máquina de uso e rode:
```powershell
# Se for rede local Wi-Fi, use o IP da Lenovo. Se usar Tailscale (Recomendado), use o IP mágico do TS.
[System.Environment]::SetEnvironmentVariable('JARVIS_MASTER_URL', 'http://SEU_IP_AQUI:8000', 'User')
```

Reinicie todos os terminais para ele puxar a env-var.
Ao logar um evento agora, aparecerá no log `Modo: Rede Neural`.
