# 🐳 Photus System - Docker Setup

## Para Professor: Como Usar

### Usar com Docker Compose

O container inicia Photus UC, Photus B e Photus System pelo `entrypoint.sh`.
Antes de subir, deixe `../photus-b/.env` disponível no host, com
`MISTRAL_API_KEY`, `HF_API_KEY` e `LLM_VALID_MODELS` configurados. O arquivo
e injetado em runtime; nao o adicione ao Git nem a imagem Docker. Para usar
outro caminho (inclusive em outra maquina), defina `PHOTUS_B_ENV_FILE`:

```bash
PHOTUS_B_ENV_FILE=/caminho/privado/photus-b.env docker compose up --build -d
```

```bash
docker compose up --build
```

Para executar em segundo plano:

```bash
docker compose up --build -d
```

Por padrão, o Photus System acessa o Photus B em `http://localhost:8000`,
dentro do mesmo container. A API também fica disponível no localhost do host na porta 8000.

Para encerrar:

```bash
docker compose down
```

### 1. Pull da imagem no Docker Hub
```bash
docker pull belforzz/photus-system:latest
```

A imagem publicada precisa ter sido reconstruída e enviada depois da alteração
do `entrypoint.sh`; fazer pull de uma versão antiga não inicia o Photus B.

### 2. Rodar o container
```bash
docker run \
  --name photus-system \
  --env-file /caminho/privado/photus-b.env \
  -p 7860:7860 -p 8001:8001 -p 127.0.0.1:8000:8000 \
  -v photus_uc_data:/app/photus-uc/data \
  belforzz/photus-system:latest
```

O volume `photus_uc_data` guarda o SQLite fora da camada descartável do
container. O arquivo de ambiente deve existir na maquina que executa o
`docker run`; ele nao vem no pull da imagem.

### 3. Ver o banco

Na raiz deste projeto, execute fora de qualquer container:

```bash
./scripts/ver-banco-docker.sh
```

O script cria ou inicia o container com o volume persistente e mostra as
tabelas e os registros do banco.

### 4. Acessar
- **Photus System UI**: http://localhost:7860
- **Photus UC API**: http://localhost:8001
- **Photus B API**: http://localhost:8000/health

---

## Para Desenvolvedor: Como Buildear e Subir no Docker Hub

### 1. Build local
```bash
cd /caminho/para/photus-system
docker build -t belforzz/photus-system:latest .
```

### 2. Testar localmente
```bash
docker run --env-file /caminho/privado/photus-b.env -p 7860:7860 -p 8001:8001 -p 127.0.0.1:8000:8000 belforzz/photus-system:latest
```

### 3. Fazer login no Docker Hub
```bash
docker login
# Digite seu username e password
```

### 4. Push para Docker Hub
```bash
docker push belforzz/photus-system:latest
```

### (Opcional) Adicionar tag de versão
```bash
docker tag belforzz/photus-system:latest belforzz/photus-system:v1.0.0
docker push belforzz/photus-system:v1.0.0
```

---

## Estrutura

- **Dockerfile**: Clona os três repos e configura o ambiente
- **entrypoint.sh**: Inicia Photus UC (8001), Photus B (8000) e Photus System (7860)

## Variáveis de Ambiente

Se precisar customizar:
```bash
docker run \
  --env-file /caminho/privado/photus-b.env \
  -p 7860:7860 -p 8001:8001 -p 127.0.0.1:8000:8000 \
  -e PHOTUS_UC_URL=http://localhost:8001 \
  -e PHOTUS_B_URL=http://localhost:8000 \
  belforzz/photus-system:latest
```

## Logs

Para ver logs em tempo real:
```bash
docker logs -f photus-system
```

## Parar o container
```bash
docker stop <container_id>
```

---

## 🚨 Troubleshooting

### "Connection refused" entre serviços
Os três serviços compartilham `localhost` dentro do container. Se houver erro,
verifique `docker logs photus-system` e `curl http://localhost:8000/health`.

### Photus UC não inicia
Verifique se há dependências faltando no `pyproject.toml` do photus-uc.

### Gradio não abre
Tente acessar `http://0.0.0.0:7860` ou `http://container-ip:7860` em vez de `localhost`.
