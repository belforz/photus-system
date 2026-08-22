import json
import re
import shutil
from pathlib import Path


def _build_highlight_value(text: str, anchor: str, matched_words: list):
    """Builds the value for gr.HighlightText: list of (segment, label|None)."""
    if not text.strip():
        return [(text, None)]

    text_lower = {w.lower() for w in matched_words}
    parts = re.split(r"(\s+)", text)  # preserva espaços
    out = []
    for part in parts:
        key = re.sub(r"[^\w]", "", part.lower())
        if len(key) >= 3 and any(key in w or w in key for w in text_lower):
            out.append((part, anchor))
        else:
            out.append((part, None))
    return out


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


def _save_photus_a_output(session_dir: Path, result: dict) -> Path:
    """Persists the Photus A result JSON alongside the session's photos, for traceability."""
    output_path = Path(session_dir) / "photus_a_output.json"
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return output_path


def clean():
    """Reseta o estado da UI: chat, highlight e galeria."""
    return [], [("", None)], None
