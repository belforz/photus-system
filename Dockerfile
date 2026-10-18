# syntax=docker/dockerfile:1
#
# Photus System: imagem unica com Gradio (7860) + Photus UC (8001) + Photus B (8000) + photus-engine (8002).
# UC, B e engine vem prontos das imagens publicadas; so o front (este repo) e construido aqui.
#
#   docker build --pull -t belforzz/photus-system:latest .        # --pull busca as ultimas :latest
#   docker build --pull --build-arg PHOTUS_TAG=v0.0.0 -t ... .    # trava uma versao das dependencias

ARG PHOTUS_REGISTRY=belforzz
ARG PHOTUS_TAG=latest

FROM ${PHOTUS_REGISTRY}/photus-uc:${PHOTUS_TAG} AS photus-uc
FROM ${PHOTUS_REGISTRY}/photus-b:${PHOTUS_TAG} AS photus-b

# ------------------------------------------------------------ front (Gradio)
FROM python:3.12-slim-bookworm AS system-build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

WORKDIR /app/photus-system
COPY pyproject.toml uv.lock .python-version ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project
COPY README.md main.py ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ------------------------------------------------------------------ runtime
# Base = photus-engine: ja traz as libs de runtime do OpenCV e os binarios C++ em /opt (engine fica em /app).
FROM ${PHOTUS_REGISTRY}/photus-engine:${PHOTUS_TAG} AS runtime

USER root

COPY --from=photus-b /opt/venv /opt/venv
COPY --from=photus-b /opt/hf /opt/hf
COPY --from=photus-b /app /app/photus-b
COPY --from=photus-uc /app /app/photus-uc
COPY --from=system-build /app/photus-system /app/photus-system
COPY --chmod=755 entrypoint.sh /app/entrypoint.sh

RUN mkdir -p /app/photus-uc/data/uploads /app/photus-system/data/uploads

# PATH sem o venv do engine na frente: cada servico usa o python do proprio venv (ver entrypoint.sh).
ENV PATH="/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin" \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/opt/hf \
    HF_HUB_OFFLINE=1 \
    TOKENIZERS_PARALLELISM=false \
    PHOTUS_UC_URL=http://localhost:8001 \
    PHOTUS_B_URL=http://localhost:8000 \
    PHOTUS_ENGINE_URL=http://localhost:8002 \
    PIPELINE_BACKEND=http \
    DATABASE_URL=sqlite:///./data/photus.db \
    UPLOADS_DIR=/app/photus-uc/data/uploads \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

WORKDIR /app
EXPOSE 7860 8001 8000 8002

# Photus B leva ~1 min carregando o modelo antes de responder /health.
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request as u; [u.urlopen(x, timeout=4) for x in ('http://localhost:8001/health', 'http://localhost:8000/health', 'http://localhost:8002/health', 'http://localhost:7860/')]"

ENTRYPOINT ["/app/entrypoint.sh"]
