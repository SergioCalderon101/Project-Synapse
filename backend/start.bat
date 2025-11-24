@echo off
REM Script de inicio rápido para Synapse AI en Windows
REM =================================================

echo.
echo ============================================
echo   SYNAPSE AI - Inicio Rapido
echo ============================================
echo.

REM Verificar si existe el entorno virtual
if not exist "..\venv\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado
    echo Por favor ejecuta: python -m venv venv
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [1/2] Activando entorno virtual...
call ..\venv\Scripts\activate.bat

REM Verificar archivo .env
if not exist "..\config\.env" (
    echo.
    echo [ADVERTENCIA] Archivo .env no encontrado
    echo Copiando .env.example a .env...
    copy "..\config\.env.example" "..\config\.env" >nul
    echo.
    echo [IMPORTANTE] Edita el archivo .env y agrega tu API key de OpenAI
    echo.
    pause
)

REM Iniciar servidor
echo [2/2] Iniciando servidor...
echo.
python app.py

pause
