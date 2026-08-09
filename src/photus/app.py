import time
from datetime import datetime

import gradio as gr
from loguru import logger

from photus.config import MAX_PHOTOS, UPLOAD_ROOT
from photus.ui.index import ui_layout
from photus.ui.status import ui_status
from photus.utils import _save_photos

# ---------------------------------------------------------------------------
# Pipeline principal (generator -> vai "acendendo" os steps na UI)
# ---------------------------------------------------------------------------


def process_pipeline(text, files, chat_history):
    chat_history = chat_history or []

    if not text or not text.strip():
        chat_history.append({
            "role": "assistant",
            "content": "⚠️ Descreva a vibe/estética desejada no campo de texto antes de processar.",
        })
        yield chat_history, [("", None)], None, ui_status(0, failed=True)
        return

    if not files:
        chat_history.append({"role": "assistant", "content": "⚠️ Envie pelo menos 1 foto (máximo 20)."})
        yield chat_history, [("", None)], None, ui_status(0, failed=True)
        return

    if len(files) > MAX_PHOTOS:
        chat_history.append({
            "role": "assistant",
            "content": f"⚠️ Você enviou {len(files)} fotos, o máximo é {MAX_PHOTOS}. Removi o excedente.",
        })
        files = files[:MAX_PHOTOS]

    chat_history.append({"role": "user", "content": text})
    highlight_value = [(text, None)]
    gallery = None

    # Stage 0 — Upload recebido
    logger.info(f"Recebido upload de {len(files)} foto(s) e texto: {text}")
    yield chat_history, highlight_value, gallery, ui_status(0)
    time.sleep(0.3)

    # Stage 1 — Pasta de staging: salva as fotos na sessão
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = UPLOAD_ROOT / session_id
    saved_paths = _save_photos(files, session_dir)
    chat_history.append({"role": "assistant", "content": f"📁 {len(saved_paths)} foto(s) salvas em `{session_dir}`"})
    logger.info(f"Fotos salvas em: {session_dir}")
    yield chat_history, highlight_value, gallery, ui_status(1)
    time.sleep(0.3)

    # Stage 2 — Photus B (SBERT): roteamento semântico do texto
    # TODO:
    yield chat_history, highlight_value, gallery, ui_status(2)
    time.sleep(0.3)

    # Stage 3 — Preprocessor: normalização das fotos antes do Photus A
    # TODO: 
    yield chat_history, highlight_value, gallery, ui_status(3)
    time.sleep(0.3)

    # Stage 4 — Photus A (OpenCV + Random Forest): scoring das fotos
    # TODO:
    yield chat_history, highlight_value, gallery, ui_status(4)
    time.sleep(0.3)

    # Stage 5 — Top 3: seleção final
    # TODO: ordenar por score e montar a galeria com as 3 melhores fotos
    chat_history.append({
        "role": "assistant",
        "content": "🚧 Photus B, Preprocessor e Photus A ainda não implementados — pipeline estrutural completo.",
    })
    yield chat_history, highlight_value, gallery, ui_status(5, done=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    demo = ui_layout(process_pipeline)
    demo.launch(theme=gr.themes.Soft(primary_hue="violet", secondary_hue="slate"))


if __name__ == "__main__":
    main()
