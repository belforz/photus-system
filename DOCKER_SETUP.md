# 🐳 Photus System - Docker Setup

## Para Professor: Como Usar

### 1. Pull da imagem no Docker Hub
```bash
docker pull belforz/photus-system:latest
```

### 2. Rodar o container
```bash
docker run -p 7860:7860 -p 8001:8001 belforz/photus-system:latest
```

### 3. Acessar
- **Photus System UI**: http://localhost:7860
- **Photus UC API**: http://localhost:8001

---

## Para Desenvolvedor: Como Buildear e Subir no Docker Hub

### 1. Build local
```bash
cd /caminho/para/photus-system
docker build -t belforz/photus-system:latest .
```

### 2. Testar localmente
```bash
docker run -p 7860:7860 -p 8001:8001 belforz/photus-system:latest
```

### 3. Fazer login no Docker Hub
```bash
docker login
# Digite seu username e password
```

### 4. Push para Docker Hub
```bash
docker push belforz/photus-system:latest
```

### (Opcional) Adicionar tag de versão
```bash
docker build -t belforz/photus-system:v1.0.0 .
docker push belforz/photus-system:v1.0.0
```

---

## Estrutura

- **Dockerfile**: Clona ambos os repos e configura o ambiente
- **entrypoint.sh**: Script que roda Photus UC (8001) + Photus System (7860) em paralelo

## Variáveis de Ambiente

Se precisar customizar:
```bash
docker run \
  -p 7860:7860 \
  -p 8001:8001 \
  -e PHOTUS_UC_URL=http://localhost:8001 \
  -e PHOTUS_B_URL=http://localhost:8000 \
  belforz/photus-system:latest
```

## Logs

Para ver logs em tempo real:
```bash
docker run -it -p 7860:7860 -p 8001:8001 belforz/photus-system:latest
```

## Parar o container
```bash
docker stop <container_id>
```

---

## 🚨 Troubleshooting

### "Connection refused" entre serviços
Ambos estão configurados para comunicar em `localhost`, que dentro do container é compartilhado. Se ainda tiver erro, verifique as portas no `docker run`.

### Photus UC não inicia
Verifique se há dependências faltando no `pyproject.toml` do photus-uc.

### Gradio não abre
Tente acessar `http://0.0.0.0:7860` ou `http://container-ip:7860` em vez de `localhost`.
