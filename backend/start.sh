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
echo "[1/2] Activando entorno virtual..."
source ../venv/bin/activate

# Verificar archivo .env
if [ ! -f "../config/.env" ]; then
    echo ""
    echo "[ADVERTENCIA] Archivo .env no encontrado"
    echo "Copiando .env.example a .env..."
    cp ../config/.env.example ../config/.env
    echo ""
    echo "[IMPORTANTE] Edita el archivo .env y agrega tu API key de OpenAI"
    echo ""
    read -p "Presiona Enter para continuar..."
fi

# Iniciar servidor
echo "[2/2] Iniciando servidor..."
echo ""
python app.py
