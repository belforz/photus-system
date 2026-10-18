#!/bin/bash
set -e

echo "Iniciando Photus System..."

# Cada servico roda com o python do proprio venv (copiados das imagens publicadas).
ENGINE_PY=/app/.venv/bin/python
B_PY=/opt/venv/bin/python
UC_PY=/app/photus-uc/.venv/bin/python
SYSTEM_PY=/app/photus-system/.venv/bin/python

# O Settings do photus-uc (pydantic-settings) lê PHOTUS_B_BASE_URL e PHOTUS_ENGINE_BASE_URL;
# sem isso os defaults embutidos apontam para portas erradas e a classificação falha.
export PHOTUS_B_BASE_URL="${PHOTUS_B_URL}"
export PHOTUS_ENGINE_BASE_URL="${PHOTUS_ENGINE_URL}"

# Criar diretórios necessários
mkdir -p /app/photus-system/data/uploads
mkdir -p /app/photus-uc/data "${UPLOADS_DIR}"

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
    kill "$ENGINE_PID" "$B_PID" "$UC_PID" "$SYSTEM_PID" 2>/dev/null || true
    exit "$status"
}

trap cleanup SIGTERM SIGINT

# Inicializar schema do banco do Photus UC
echo "Aplicando migracoes do banco (alembic upgrade head)..."
cd /app/photus-uc
"$UC_PY" -m alembic upgrade head
echo "Banco pronto. Tabelas:"
"$UC_PY" - <<'PY'
import sqlite3

connection = sqlite3.connect("/app/photus-uc/data/photus.db")
tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
).fetchall()
print("  " + ", ".join(table[0] for table in tables))
connection.close()
PY

# photus-engine (pré-processador + Photus A): um único worker, um lote por vez.
echo "Iniciando photus-engine na porta 8002..."
cd /app
"$ENGINE_PY" -m uvicorn engine.app:app --host 0.0.0.0 --port 8002 --workers 1 &
ENGINE_PID=$!

# Photus B (roteamento semântico): carrega o modelo antes de aceitar conexões.
echo "Iniciando Photus B na porta 8000..."
cd /app/photus-b
HOST=0.0.0.0 PORT=8000 "$B_PY" main.py &
B_PID=$!

echo "Iniciando Photus UC na porta 8001..."
cd /app/photus-uc
"$UC_PY" -m uvicorn main:app --host 0.0.0.0 --port 8001 &
UC_PID=$!

echo "Iniciando Photus System na porta 7860..."
cd /app/photus-system
"$SYSTEM_PY" main.py &
SYSTEM_PID=$!

#Informar URLs de acesso
echo "Photus UC está rodando em: http://localhost:8001"
echo "Photus B está rodando em: http://localhost:8000"
echo "photus-engine está rodando em: http://localhost:8002"
echo "Photus System está rodando em: http://localhost:7860"

# Encerrar tudo se qualquer serviço terminar
if wait -n "$ENGINE_PID" "$B_PID" "$UC_PID" "$SYSTEM_PID"; then
    cleanup
else
    echo "Um dos serviços terminou com erro."
    cleanup 1
fi
