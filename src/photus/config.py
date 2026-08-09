import os
from pathlib import Path

# Raiz do projeto (dois níveis acima de src/photus)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

MAX_PHOTOS = 20
UPLOAD_ROOT = PROJECT_ROOT / "data" / "uploads"

# Photus B roda como servico HTTP separado (repo irmao photus-b, `uv run main.py`).
PHOTUS_B_URL = os.getenv("PHOTUS_B_URL", "http://localhost:8000").rstrip("/")
PHOTUS_B_TIMEOUT_SECONDS = float(os.getenv("PHOTUS_B_TIMEOUT_SECONDS", "15"))
