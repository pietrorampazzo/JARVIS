@echo off
title Wappi - WhatsApp Local
echo.
echo ========================================
echo   WAPPI - Motor WhatsApp Local
echo ========================================
echo.
echo Iniciando servidor de controle...
echo Deixe esta janela aberta enquanto usar o WhatsApp.
echo.
cd /d "%~dp0"
node server.js
pause
