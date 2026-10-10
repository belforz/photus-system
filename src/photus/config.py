import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MAX_PHOTOS = 20
UPLOAD_ROOT = PROJECT_ROOT / "data" / "uploads"

PREPROCESSOR_IMAGES_ROOT = PROJECT_ROOT.parent / "ai-pre-process-images" / "images"

PHOTUS_UC_URL = os.getenv("PHOTUS_UC_URL", "http://localhost:8001").rstrip("/")
PHOTUS_UC_TIMEOUT_SECONDS = float(os.getenv("PHOTUS_UC_TIMEOUT_SECONDS", "15"))

SESSION_BROWSER_SECRET = os.getenv("PHOTUS_SESSION_SECRET", "photus-dev-session-secret")
