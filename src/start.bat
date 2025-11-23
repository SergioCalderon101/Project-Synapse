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
echo [1/3] Activando entorno virtual...
call ..\venv\Scripts\activate.bat

REM Verificar archivo .env
if not exist "..\.env" (
    echo.
    echo [ADVERTENCIA] Archivo .env no encontrado
    echo Copiando .env.example a .env...
    copy "..\.env.example" "..\.env" >nul
    echo.
    echo [IMPORTANTE] Edita el archivo .env y agrega tu API key de OpenAI
    echo.
    pause
)

REM Instalar dependencias si es necesario
echo [2/3] Verificando dependencias...
pip show pydantic-settings >nul 2>&1
if errorlevel 1 (
    echo Instalando pydantic-settings...
    pip install pydantic-settings
)

REM Iniciar servidor
echo [3/3] Iniciando servidor...
echo.
python run.py

pause
