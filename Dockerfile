# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema (git para clonar repos, uv para gerenciar pacotes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# cache-bust -> clone -> uv sync por repositório.

ADD https://api.github.com/repos/belforz/photus-system/commits/release/eg-soft /tmp/photus-system-rev.json
RUN git clone --depth 1 --branch release/eg-soft https://github.com/belforz/photus-system.git photus-system
WORKDIR /app/photus-system
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

ADD https://api.github.com/repos/belforz/photus-uc/commits/main /tmp/photus-uc-rev.json
RUN git clone --depth 1 --branch main https://github.com/belforz/photus-uc.git /app/photus-uc
WORKDIR /app/photus-uc
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

ADD https://api.github.com/repos/belforz/photus-b/commits/master /tmp/photus-b-rev.json
RUN git clone --depth 1 --branch master https://github.com/belforz/photus-b.git /app/photus-b
WORKDIR /app/photus-b
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

# Voltar para raiz
WORKDIR /app

# Copiar entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expor portas
EXPOSE 7860 8001 8000

# Variáveis de ambiente para comunicação entre serviços
ENV PHOTUS_UC_URL=http://localhost:8001
ENV PHOTUS_B_URL=http://localhost:8000
ENV DATABASE_URL=sqlite:///./data/photus.db
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Executar entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
