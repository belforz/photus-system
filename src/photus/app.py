import subprocess
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import gradio as gr
from loguru import logger

from photus.config import MAX_PHOTOS, UPLOAD_ROOT
from photus.photus_a_runner import PhotusARunError, score_session
from photus.photus_b_client import PhotusBClientError, categorize_text
from photus.preprocessor_runner import PreprocessorRunError, run_preprocessor, session_entries
from photus.ui.index import ui_layout
from photus.ui.status import ui_status
from photus.utils import _build_highlight_value, _save_photos

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
    session_id =  f"{uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_dir = UPLOAD_ROOT / session_id
    saved_paths = _save_photos(files, session_dir)
    chat_history.append({"role": "assistant", "content": f"📁 {len(saved_paths)} foto(s) salvas em `{session_dir}`"})
    logger.info(f"Fotos salvas em: {session_dir}")
    yield chat_history, highlight_value, gallery, ui_status(1)
    time.sleep(0.3)

    # Stage 2 — Photus B (SBERT): roteamento semântico do texto
    yield chat_history, highlight_value, gallery, ui_status(2)
    try:
        category_result = categorize_text(text)
    except PhotusBClientError as e:
        logger.error(f"Falha ao chamar Photus B: {e}")
        chat_history.append({"role": "assistant", "content": f"❌ Photus B falhou: {e}"})
        yield chat_history, highlight_value, gallery, ui_status(2, failed=True)
        return

    category = category_result["category"]
    confidence = category_result["confidence"]
    anchor_words = category_result["top_matches"][0]["anchor_phrase"].split() if category_result["top_matches"] else []
    highlight_value = _build_highlight_value(text, category, anchor_words)

    if category_result["technical"]:
        chat_history.append({
            "role": "assistant",
            "content": f"🔧 Pedido técnico detectado (score {category_result['technical_score']:.2f}) — roteado para o Mistral.",
        })
    else:
        chat_history.append({
            "role": "assistant",
            "content": f"🧭 Photus B identificou a categoria **{category}** (confiança {confidence:.2f}).",
        })
    yield chat_history, highlight_value, gallery, ui_status(2)
    time.sleep(0.3)

    # Stage 3 — Preprocessor: normalização das fotos antes do Photus A
    yield chat_history, highlight_value, gallery, ui_status(3)
    try:
        preproc_results = run_preprocessor(session_dir, category_result["category_code"])
    except PreprocessorRunError as e:
        logger.error(f"Falha ao rodar o preprocessor: {e}")
        chat_history.append({"role": "assistant", "content": f"❌ Preprocessor falhou: {e}"})
        yield chat_history, highlight_value, gallery, ui_status(3, failed=True)
        return

    chat_history.append({
        "role": "assistant",
        "content": (
            f"🧪 Preprocessor normalizou {len(preproc_results)} foto(s) "
            f"(categoria `{category_result['category_code']}`)."
        ),
    })
    yield chat_history, highlight_value, gallery, ui_status(3)
    time.sleep(0.3)

    # Stage 4 — Photus A (OpenCV + Random Forest): scoring das fotos
    yield chat_history, highlight_value, gallery, ui_status(4)
    try:
        photus_a_result = score_session(saved_paths, category_result["category_code"])
    except (PhotusARunError, PreprocessorRunError, subprocess.TimeoutExpired) as e:
        logger.error(f"Photus A falhou: {e}")
        chat_history.append({"role": "assistant", "content": f"❌ Photus A falhou: {e}"})
        yield chat_history, highlight_value, gallery, ui_status(4, failed=True)
        return

    scored = photus_a_result["results"]
    by_status = photus_a_result.get("summary", {}).get("by_status", {})
    logger.info(f"Photus A run {photus_a_result.get('run_id')}: {by_status}")
    chat_history.append({
        "role": "assistant",
        "content": f"🧠 Photus A pontuou {len(scored)} foto(s) — {by_status}",
    })
    yield chat_history, highlight_value, gallery, ui_status(4)
    time.sleep(0.3)

    # Stage 5 — Top 3: seleção final por score
    ranked = sorted((r for r in scored if "final_score" in r), key=lambda r: r["final_score"], reverse=True)
    top3 = ranked[:3]

    try:
        thumbnails = {img["filename"]: img["path"] for img in session_entries(saved_paths, {"thumbnail"})}
    except PreprocessorRunError as e:
        logger.warning(f"Sem thumbnails para a galeria, usando as fotos originais: {e}")
        thumbnails = {}

    gallery = [thumbnails.get(Path(r["image_path"]).name, r["image_path"]) for r in top3]

    if top3:
        chat_history.append({
            "role": "assistant",
            "content": "🏆 Top " + str(len(top3)) + " selecionadas: "
            + ", ".join(Path(r["image_path"]).name for r in top3),
        })
    else:
        chat_history.append({"role": "assistant", "content": "⚠️ Nenhuma foto pontuada para compor o Top 3."})

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
