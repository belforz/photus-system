import shutil
from pathlib import Path


def _save_photos(files, session_dir: Path):
    """Copies the uploaded files to a session directory and returns the saved paths."""
    session_dir = Path(session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    for f in files:
        src = Path(f.name if hasattr(f, "name") else f)
        dst = session_dir / src.name
        shutil.copyfile(src, dst)
        saved_paths.append(dst)
    return saved_paths


def clean():
    """Reseta o estado da UI: chat e highlight."""
    return [], [("", None)]
