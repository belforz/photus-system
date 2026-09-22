
from __future__ import annotations

import mimetypes
from pathlib import Path

from photus.auth_client import AuthClientError, error_detail
from photus.config import PHOTUS_UC_TIMEOUT_SECONDS, PHOTUS_UC_URL

import httpx
from loguru import logger


def submit_evaluation_batch(token: str, input_text: str, files: list) -> dict:
    url = f"{PHOTUS_UC_URL}/batches"
    headers = {"Authorization": f"Bearer {token}"}

    opened = []
    try:
        file_tuples = []
        for f in files:
            path = Path(f.name if hasattr(f, "name") else f)
            handle = open(path, "rb")
            opened.append(handle)
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            file_tuples.append(("photos", (path.name, handle, content_type)))

        try:
            resp = httpx.post(
                url,
                data={"input_text": input_text},
                files=file_tuples,
                headers=headers,
                timeout=PHOTUS_UC_TIMEOUT_SECONDS,
            )
        except httpx.RequestError as e:
            raise AuthClientError(
                f"Não foi possível conectar ao serviço de contas em {url}. "
                f"Ele está rodando (`uv run uvicorn main:app --port 8001` no repo photus-uc)? Detalhe: {e}"
            ) from e
    finally:
        for handle in opened:
            handle.close()

    if resp.status_code == 201:
        result = resp.json()
        logger.info(
            "Photus UC: lote {} criado -> status={}, ancora={}, rota={}",
            result.get("id"),
            result.get("status"),
            result.get("classified_anchor"),
            result.get("classification_route"),
        )
        return result
    raise AuthClientError(error_detail(resp), status_code=resp.status_code)
