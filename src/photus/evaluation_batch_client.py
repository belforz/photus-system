
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


def get_evaluation_batch(token: str, batch_id: str) -> dict:
    """UC06 — consulta o lote (status + fotos avaliadas) para o Monitor/Diagnóstico."""
    url = f"{PHOTUS_UC_URL}/batches/{batch_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = httpx.get(url, headers=headers, timeout=PHOTUS_UC_TIMEOUT_SECONDS)
    except httpx.RequestError as e:
        raise AuthClientError(
            f"Não foi possível conectar ao serviço de contas em {url}. Detalhe: {e}"
        ) from e

    if resp.status_code == 200:
        return resp.json()
    raise AuthClientError(error_detail(resp), status_code=resp.status_code)


def _authed_request(method: str, path: str, token: str) -> httpx.Response:
    url = f"{PHOTUS_UC_URL}{path}"
    try:
        return httpx.request(
            method, url, headers={"Authorization": f"Bearer {token}"}, timeout=PHOTUS_UC_TIMEOUT_SECONDS
        )
    except httpx.RequestError as e:
        raise AuthClientError(
            f"Não foi possível conectar ao serviço de contas em {url}. Detalhe: {e}"
        ) from e


def list_evaluation_batches(token: str) -> list[dict]:
    """UC07 — histórico de lotes do usuário autenticado (mais recente primeiro)."""
    resp = _authed_request("GET", "/batches", token)
    if resp.status_code == 200:
        return resp.json()
    raise AuthClientError(error_detail(resp), status_code=resp.status_code)


def delete_evaluation_batch(token: str, batch_id: str) -> None:
    """UC10 — exclui o lote e, em cascata, as fotos avaliadas."""
    resp = _authed_request("DELETE", f"/batches/{batch_id}", token)
    if resp.status_code == 204:
        logger.info("Photus UC: lote {} excluído", batch_id)
        return
    raise AuthClientError(error_detail(resp), status_code=resp.status_code)


def get_batch_photo_bytes(token: str, batch_id: str, photo_id: str) -> bytes:
    """Bytes da foto original do lote (só o proprietário acessa — RF14)."""
    resp = _authed_request("GET", f"/batches/{batch_id}/photos/{photo_id}/image", token)
    if resp.status_code == 200:
        return resp.content
    raise AuthClientError(error_detail(resp), status_code=resp.status_code)
