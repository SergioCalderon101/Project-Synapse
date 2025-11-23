#!/bin/bash
# Script de inicio rápido para Synapse AI en Linux/Mac
# ======================================================

echo ""
echo "============================================"
echo "   SYNAPSE AI - Inicio Rápido"
echo "============================================"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "../venv" ]; then
    echo "[ERROR] Entorno virtual no encontrado"
    echo "Por favor ejecuta: python3 -m venv venv"
    exit 1
fi

# Activar entorno virtual
echo "[1/3] Activando entorno virtual..."
source ../venv/bin/activate

# Verificar archivo .env
if [ ! -f "../.env" ]; then
    echo ""
    echo "[ADVERTENCIA] Archivo .env no encontrado"
    echo "Copiando .env.example a .env..."
    cp ../.env.example ../.env
    echo ""
    echo "[IMPORTANTE] Edita el archivo .env y agrega tu API key de OpenAI"
    echo ""
    read -p "Presiona Enter para continuar..."
fi

# Instalar dependencias si es necesario
echo "[2/3] Verificando dependencias..."
pip show pydantic-settings > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Instalando pydantic-settings..."
    pip install pydantic-settings
fi

# Iniciar servidor
echo "[3/3] Iniciando servidor..."
echo ""
python run.py
