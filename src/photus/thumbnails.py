from __future__ import annotations

import base64
import io
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

from loguru import logger
from PIL import Image, ImageOps

from photus.auth_client import AuthClientError
from photus.evaluation_batch_client import get_batch_photo_bytes

THUMB_MAX_SIDE = 520
_CACHE_LIMIT = 300
_cache: OrderedDict[str, str] = OrderedDict()


def _to_data_uri(raw: bytes) -> str:
    with Image.open(io.BytesIO(raw)) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        img.thumbnail((THUMB_MAX_SIDE, THUMB_MAX_SIDE))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _load_one(token: str, batch_id: str, photo_id: str) -> str | None:
    if photo_id in _cache:
        _cache.move_to_end(photo_id)
        return _cache[photo_id]
    try:
        uri = _to_data_uri(get_batch_photo_bytes(token, batch_id, photo_id))
    except (AuthClientError, OSError, ValueError) as e:
        logger.warning("Miniatura indisponível ({}/{}): {}", batch_id, photo_id, e)
        return None
    _cache[photo_id] = uri
    while len(_cache) > _CACHE_LIMIT:
        _cache.popitem(last=False)
    return uri


def load_thumbnails(token: str, detail: dict) -> dict[str, str]:
    """photo_id -> data URI (miniatura JPEG). Fotos sem arquivo legível ficam de fora."""
    batch_id = detail["id"]
    photos = detail.get("photos", [])
    with ThreadPoolExecutor(max_workers=6) as pool:
        uris = list(pool.map(lambda p: _load_one(token, batch_id, p["id"]), photos))
    return {p["id"]: uri for p, uri in zip(photos, uris) if uri}
