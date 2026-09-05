#!/bin/sh
set -eu

IMAGE="${IMAGE:-belforzz/photus-system:v0.0.4}"
CONTAINER="${CONTAINER:-photus-system}"
VOLUME="${VOLUME:-photus_uc_data}"
DATABASE="/app/photus-uc/data/photus.db"

command -v docker >/dev/null 2>&1 || {
    echo "Erro: execute este script fora de outro container, em um terminal com Docker disponível." >&2
    exit 1
}

docker volume create "$VOLUME" >/dev/null

if ! docker container inspect "$CONTAINER" >/dev/null 2>&1; then
    echo "Criando container $CONTAINER com o volume persistente $VOLUME..."
    docker run -d \
        --name "$CONTAINER" \
        -p 7860:7860 \
        -p 8001:8001 \
        -v "$VOLUME:/app/photus-uc/data" \
        "$IMAGE" >/dev/null
else
    mounted_volume="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/app/photus-uc/data"}}{{.Name}}{{end}}{{end}}' "$CONTAINER")"
    if [ "$mounted_volume" != "$VOLUME" ]; then
        echo "Erro: o container $CONTAINER não usa o volume $VOLUME." >&2
        echo "Remova-o manualmente e execute este script novamente:" >&2
        echo "  docker rm -f $CONTAINER" >&2
        exit 1
    fi

    if [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER")" != "true" ]; then
        docker start "$CONTAINER" >/dev/null
    fi
fi

echo "Aguardando o banco ser criado..."
attempt=0
while ! docker exec "$CONTAINER" test -f "$DATABASE" >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 30 ]; then
        echo "Erro: o banco não foi criado. Veja os logs com: docker logs $CONTAINER" >&2
        exit 1
    fi
    sleep 1
done

docker exec -i "$CONTAINER" python - <<'PY'
import sqlite3

database = "/app/photus-uc/data/photus.db"
connection = sqlite3.connect(database)
tables = [row[0] for row in connection.execute(
    "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
)]
print("Banco:", database)
print("Tabelas:", ", ".join(tables) or "nenhuma")
for table in tables:
    print("\n[" + table + "]")
    columns = [row[1] for row in connection.execute("PRAGMA table_info(\"" + table + "\")")]
    print(" | ".join(columns))
    for row in connection.execute("SELECT * FROM \"" + table + "\""):
        print(" | ".join(str(value) for value in row))
connection.close()
PY