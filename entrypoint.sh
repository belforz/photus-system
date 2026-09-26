#!/bin/bash
set -e

echo "Iniciando Photus System..."

# O Settings do photus-uc (pydantic-settings) lê a env var PHOTUS_B_BASE_URL,
# não PHOTUS_B_URL. Sem isso, o default embutido (localhost:8001, a própria
# porta do photus-uc) prevalece e toda classificação de lote falha com
# status "erro" (POST /v1/categorize cai no próprio photus-uc -> 404).
export PHOTUS_B_BASE_URL="${PHOTUS_B_URL}"

# Criar diretórios necessários
mkdir -p /app/photus-system/data/uploads
mkdir -p /app/photus-uc/data 2>/dev/null || true

echo "Banco SQLite: /app/photus-uc/data/photus.db"
echo "DATABASE_URL: ${DATABASE_URL}"
echo "Volume de dados: /app/photus-uc/data"
if [ -f /app/photus-uc/data/photus.db ]; then
    echo "Banco existente encontrado; os dados serão preservados."
else
    echo "Banco ainda não existe; será criado pelas migrações."
fi

# Função para tratamento de sinais (Ctrl+C)
cleanup() {
    local status=${1:-0}
    echo "Encerrando serviços..."
    kill "$UC_PID" "$SYSTEM_PID" "$B_PID" 2>/dev/null || true
    exit "$status"
}

trap cleanup SIGTERM SIGINT

# Inicializar schema do banco do Photus UC
echo "Aplicando migracoes do banco (alembic upgrade head)..."
cd /app/photus-uc
uv run alembic upgrade head
echo "Banco pronto. Tabelas:"
uv run python - <<'PY'
import sqlite3

connection = sqlite3.connect("/app/photus-uc/data/photus.db")
tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
).fetchall()
print("  " + ", ".join(table[0] for table in tables))
connection.close()
PY

# Iniciar Photus UC (FastAPI) em background
echo "Iniciando Photus UC na porta 8001..."
cd /app/photus-uc
uv run uvicorn main:app --host 0.0.0.0 --port 8001 &
UC_PID=$!
sleep 2

# Iniciar Photus B (FastAPI) em background
echo "Iniciando Photus B na porta 8000..."
cd /app/photus-b
uv run python main.py &
B_PID=$!

# Iniciar Photus System (Gradio) em foreground
echo "Iniciando Photus System na porta 7860..."
cd /app/photus-system
uv run python main.py &
SYSTEM_PID=$!

#Informar URLs de acesso
echo "Photus UC está rodando em: http://localhost:8001"
echo "Photus B está rodando em: http://localhost:8000"
echo "Photus System está rodando em: http://localhost:7860"

# Encerrar tudo se qualquer serviço terminar
if wait -n "$UC_PID" "$B_PID" "$SYSTEM_PID"; then
    cleanup
else
    echo "Um dos serviços terminou com erro."
    cleanup 1
fi
