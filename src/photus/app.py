import time
from datetime import datetime

import gradio as gr
from loguru import logger

from photus.config import MAX_PHOTOS, UPLOAD_ROOT
from photus.ui.index import ui_layout
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
        yield chat_history, [("", None)], None
        return

    if not files:
        chat_history.append({"role": "assistant", "content": "⚠️ Envie pelo menos 1 foto (máximo 20)."})
        yield chat_history, [("", None)], None
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

    # Step 0 — upload recebido
    logger.info(f"Recebido upload de {len(files)} foto(s) e texto: {text}")
    yield chat_history, highlight_value, gallery
    time.sleep(0.3)

    # Step 1 — salva as fotos na pasta de staging da sessão
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = UPLOAD_ROOT / session_id
    saved_paths = _save_photos(files, session_dir)
    chat_history.append({"role": "assistant", "content": f"📁 {len(saved_paths)} foto(s) salvas em `{session_dir}`"})
    logger.info(f"Fotos salvas em: {session_dir}")
    yield chat_history, highlight_value, gallery

    # TODO Step 2 — pré-processamento do texto de entrada
    # TODO Step 3 — roteamento semântico (Photus B / SBERT)
    # TODO Step 4 — preprocess act
    # TODO Step 5 — Photus A (OpenCV + Random Forest)
    # TODO Step 6 — cálculo de scores finais do Photus A
    # TODO Step 7 — seleção do top 3 e resumo final

    chat_history.append({
        "role": "assistant",
        "content": "🚧 Próximas etapas do pipeline (Photus B, preprocessamento e Photus A) ainda não implementadas.",
    })
    yield chat_history, highlight_value, gallery


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    demo = ui_layout(process_pipeline)
    demo.launch(theme=gr.themes.Soft(primary_hue="violet", secondary_hue="slate"))


if __name__ == "__main__":
    main()
