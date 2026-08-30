import httpx
from loguru import logger

from photus.config import PHOTUS_UC_TIMEOUT_SECONDS, PHOTUS_UC_URL


class AuthClientError(RuntimeError):
    """Raised when Photus UC (auth/perfil) rejects a request or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _request(method: str, path: str, *, json: dict | None = None, token: str | None = None) -> httpx.Response:
    url = f"{PHOTUS_UC_URL}{path}"
    headers = {"Authorization": f"Bearer {token}"} if token else None
    try:
        return httpx.request(method, url, json=json, headers=headers, timeout=PHOTUS_UC_TIMEOUT_SECONDS)
    except httpx.RequestError as e:
        raise AuthClientError(
            f"Não foi possível conectar ao serviço de contas em {url}. "
            f"Ele está rodando (`uv run uvicorn main:app --port 8001` no repo photus-uc)? Detalhe: {e}"
        ) from e


def _error_detail(resp: httpx.Response) -> str:
    try:
        body = resp.json()
    except ValueError:
        return resp.text[:300]

    detail = body.get("detail")
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):  # erro de validação (422) do FastAPI/Pydantic
        return "; ".join(f"{'.'.join(str(p) for p in item.get('loc', []))}: {item.get('msg')}" for item in detail)
    return str(detail) if detail is not None else resp.text[:300]


def register_user(name: str, email: str, password: str, user_type: str) -> dict:
    """POST /usuarios — creates the account. Raises AuthClientError(status_code=409) if the e-mail already exists."""
    resp = _request(
        "POST",
        "/usuarios",
        # NB: JSON keys (nome/senha/tipo_usuario) match the photus-uc backend contract, kept as-is.
        json={"nome": name, "email": email, "senha": password, "tipo_usuario": user_type},
    )
    if resp.status_code == 201:
        logger.info("Photus UC: user {} registered", email)
        return resp.json()
    raise AuthClientError(_error_detail(resp), status_code=resp.status_code)


def authenticate_user(email: str, password: str) -> dict:
    """POST /auth/login — authenticates and returns the JWT token + public user data."""
    resp = _request("POST", "/auth/login", json={"email": email, "senha": password})
    if resp.status_code == 200:
        logger.info("Photus UC: successful login for {}", email)
        return resp.json()
    raise AuthClientError(_error_detail(resp), status_code=resp.status_code)


def update_profile(token: str, *, name: str | None = None, email: str | None = None, password: str | None = None) -> dict:
    """PATCH /usuarios/me — updates the provided fields of the authenticated user."""
    body = {k: v for k, v in {"nome": name, "email": email, "senha": password}.items() if v}
    resp = _request("PATCH", "/usuarios/me", json=body, token=token)
    if resp.status_code == 200:
        logger.info("Photus UC: profile updated (usuario_id via token)")
        return resp.json()
    raise AuthClientError(_error_detail(resp), status_code=resp.status_code)
