import httpx
from loguru import logger

from photus.config import PHOTUS_B_TIMEOUT_SECONDS, PHOTUS_B_URL


class PhotusBClientError(RuntimeError):
    """Raised when Photus B fails to categorize the input text."""


def categorize_text(text: str, timeout: float = PHOTUS_B_TIMEOUT_SECONDS) -> dict:
    """Calls Photus B's `/v1/categorize` endpoint and returns the parsed category payload.

    Photus B runs as its own HTTP service (see photus-b/main.py) — sibling repo,
    reachable at PHOTUS_B_URL (default http://localhost:8000).
    """
    url = f"{PHOTUS_B_URL}/v1/categorize"
    try:
        resp = httpx.post(url, json={"text": text}, timeout=timeout)
    except httpx.RequestError as e:
        raise PhotusBClientError(
            f"Nao foi possivel conectar ao Photus B em {url}. "
            f"Ele esta rodando (`uv run main.py` no repo photus-b)? Detalhe: {e}"
        ) from e

    if resp.status_code >= 400:
        raise PhotusBClientError(
            f"Photus B retornou {resp.status_code} para '{text}': {resp.text[:500]}"
        )

    result = resp.json()
    logger.info(
        "Photus B categorizou '{}' -> {} (confidence={:.3f}, technical={})",
        text,
        result.get("category"),
        result.get("confidence", 0.0),
        result.get("technical"),
    )
    return result
