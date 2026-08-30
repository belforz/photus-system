#!/bin/bash
set -e

echo "Iniciando Photus System..."

# Criar diretórios necessários
mkdir -p /app/photus-system/data/uploads
mkdir -p /app/photus-uc/data 2>/dev/null || true

# Função para tratamento de sinais (Ctrl+C)
cleanup() {
    echo "Encerrando serviços..."
    kill $UC_PID $SYSTEM_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGTERM SIGINT

# Iniciar Photus UC (FastAPI) em background
echo "Iniciando Photus UC na porta 8001..."
cd /app/photus-uc
uv run uvicorn main:app --host 0.0.0.0 --port 8001 &
UC_PID=$!
sleep 2

# Iniciar Photus System (Gradio) em foreground
echo "Iniciando Photus System na porta 7860..."
cd /app/photus-system
uv run python main.py &
SYSTEM_PID=$!

# Aguardar término
wait $SYSTEM_PID

# Se Photus System terminar, encerrar tudo
cleanup
