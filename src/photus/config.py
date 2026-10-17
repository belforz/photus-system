import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MAX_PHOTOS = 20
UPLOAD_ROOT = PROJECT_ROOT / "data" / "uploads"

PHOTUS_UC_URL = os.getenv("PHOTUS_UC_URL", "http://localhost:8001").rstrip("/")
PHOTUS_UC_TIMEOUT_SECONDS = float(os.getenv("PHOTUS_UC_TIMEOUT_SECONDS", "15"))

# UC06 — o Pré-processador/Photus A rodam no photus-uc (BackgroundTask); o
# front só acompanha por polling em GET /batches/{id}.
EVALUATION_POLL_INTERVAL_SECONDS = float(os.getenv("EVALUATION_POLL_INTERVAL_SECONDS", "2.0"))
EVALUATION_POLL_TIMEOUT_SECONDS = float(os.getenv("EVALUATION_POLL_TIMEOUT_SECONDS", "180"))

SESSION_BROWSER_SECRET = os.getenv("PHOTUS_SESSION_SECRET", "photus-dev-session-secret")
