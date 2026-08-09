from pathlib import Path

# Raiz do projeto (dois níveis acima de src/photus)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

MAX_PHOTOS = 20
UPLOAD_ROOT = PROJECT_ROOT / "data" / "uploads"
