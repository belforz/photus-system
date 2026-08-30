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

# Clonar ambos os repositórios
RUN git clone --depth 1 --branch release/eg-soft https://github.com/belforz/photus-system.git photus-system && \
    git clone --depth 1 --branch main https://github.com/belforz/photus-uc.git photus-uc

# Sincronizar dependências do photus-system
WORKDIR /app/photus-system
RUN uv sync --no-dev

# Sincronizar dependências do photus-uc (sem instalar o projeto como pacote)
WORKDIR /app/photus-uc
RUN uv sync --no-dev --no-install-project

# Voltar para raiz
WORKDIR /app

# Copiar entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expor portas
EXPOSE 7860 8001

# Variáveis de ambiente para comunicação entre serviços
ENV PHOTUS_UC_URL=http://localhost:8001
ENV PHOTUS_B_URL=http://localhost:8000
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Executar entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
