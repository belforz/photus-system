import time
from datetime import datetime
from uuid import uuid4

import gradio as gr
from loguru import logger

from photus.auth_client import AuthClientError
from photus.config import (
    EVALUATION_POLL_INTERVAL_SECONDS,
    EVALUATION_POLL_TIMEOUT_SECONDS,
    MAX_PHOTOS,
    UPLOAD_ROOT,
)
from photus.evaluation_batch_client import get_evaluation_batch, submit_evaluation_batch
from photus.ui.evaluation import diagnostics_html, lote_monitor_html
from photus.ui.index import ui_layout
from photus.ui.modal import ui_modal
from photus.ui.status import ui_status
from photus.ui.theme import AUTH_CSS, dropzone_update, input_update
from photus.utils import _save_photos


def process_pipeline(text, files, chat_history, session):
    chat_history = chat_history or []
    no_text = not text or not text.strip()
    no_files = not files
    token = (session or {}).get("token")

    if no_text or no_files:
        chat_history.append({
            "role": "assistant",
            "content": "⚠️ Preencha a descrição e anexe ao menos uma foto antes de submeter o lote.",
        })
        yield (
            chat_history, [("", None)], ui_status(0, failed=True),
            gr.update(visible=False), "", gr.update(visible=False),
            input_update(error=no_text), dropzone_update(error=no_files),
            gr.update(visible=True, value="Preencha a descrição ou anexe ao menos uma foto."),
            gr.update(visible=False), "", "",
        )
        return

    if len(files) > MAX_PHOTOS:
        chat_history.append({
            "role": "assistant",
            "content": f"⚠️ Você enviou {len(files)} fotos, o máximo é {MAX_PHOTOS}. Removi o excedente.",
        })
        files = files[:MAX_PHOTOS]

    chat_history.append({"role": "user", "content": text})
    highlight_value = [(text, None)]

    def _base(
        pipeline_stage, *, modal_visible=True, modal_content="", close_visible=False,
        monitor_visible=False, monitor_content="", diagnostics_content="", **status_kwargs,
    ):
        return (
            chat_history, highlight_value, ui_status(pipeline_stage, **status_kwargs),
            gr.update(visible=modal_visible), modal_content, gr.update(visible=close_visible),
            input_update(), dropzone_update(), gr.update(visible=False),
            gr.update(visible=monitor_visible), monitor_content, diagnostics_content,
        )

    logger.info(f"Recebido upload de {len(files)} foto(s) e texto: {text}")
    yield _base(0, modal_content=ui_modal(0))
    time.sleep(0.3)

  
    session_id = f"{uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_dir = UPLOAD_ROOT / session_id
    saved_paths = _save_photos(files, session_dir)
    chat_history.append({"role": "assistant", "content": f"📁 {len(saved_paths)} foto(s) salvas em `{session_dir}`"})
    logger.info(f"Fotos salvas em: {session_dir}")
    yield _base(1, modal_content=ui_modal(0))
    time.sleep(0.3)

  
    yield _base(2, modal_content=ui_modal(1))
    try:
        batch_result = submit_evaluation_batch(token, text, files)
    except AuthClientError as e:
        logger.error(f"Falha ao submeter o lote no Photus UC: {e}")
        chat_history.append({"role": "assistant", "content": f"❌ Falha ao submeter o lote: {e}"})
        yield _base(2, modal_content=ui_modal(1, failed=True), close_visible=True, failed=True)
        return

    if batch_result["status"] == "erro":
        logger.warning(f"Lote {batch_result['id']} marcado como erro (Photus B indisponível).")
        chat_history.append({
            "role": "assistant",
            "content": "❌ Photus B indisponível — o lote foi registrado com status `erro` para nova tentativa.",
        })
        yield _base(2, modal_content=ui_modal(1, failed=True), close_visible=True, failed=True)
        return

    category = batch_result["classified_anchor"] or "global"
    route_type = batch_result["classification_route"] or "fast_track"
    fallback_notice = category == "global"
    highlight_value = [(text, category)]

    chat_history.append({
        "role": "assistant",
        "content": f"🧭 Lote `{batch_result['id']}` classificado — âncora **{category}**, rota `{route_type}`.",
    })
    yield _base(
        2,
        modal_content=ui_modal(2, done=True, category=category, route_type=route_type, fallback_notice=fallback_notice),
    )
    time.sleep(1.2)
    yield _base(2, modal_visible=False)
    time.sleep(0.2)
    yield _base(2, modal_visible=False, done=True)

    # ---- UC06: avaliação técnica (Pré-processador + Photus A) ----
    # Roda em background no photus-uc; aqui só fazemos polling de
    # GET /batches/{id} até o status sair de `em_processamento`. O progresso
    # não é granular (o engine roda uma vez para o lote inteiro: 0/N -> N/N).
    batch_id = batch_result["id"]
    try:
        detail = get_evaluation_batch(token, batch_id)
    except AuthClientError as e:
        logger.error(f"Falha ao consultar status do lote {batch_id}: {e}")
        chat_history.append({
            "role": "assistant",
            "content": f"❌ Falha ao consultar o status da avaliação técnica: {e}",
        })
        yield _base(2, modal_visible=False, done=True)
        return

    chat_history.append({
        "role": "assistant",
        "content": "⚙️ Avaliação técnica (Pré-processador + Photus A) iniciada em segundo plano.",
    })
    yield _base(2, modal_visible=False, done=True, monitor_visible=True, monitor_content=lote_monitor_html(detail))

    start = time.monotonic()
    while detail["status"] == "em_processamento":
        if time.monotonic() - start > EVALUATION_POLL_TIMEOUT_SECONDS:
            chat_history.append({
                "role": "assistant",
                "content": "⚠️ A avaliação técnica está demorando mais que o esperado. "
                           "O lote continua em processamento no Photus UC.",
            })
            yield _base(
                2, modal_visible=False, done=True,
                monitor_visible=True, monitor_content=lote_monitor_html(detail),
            )
            return
        time.sleep(EVALUATION_POLL_INTERVAL_SECONDS)
        try:
            detail = get_evaluation_batch(token, batch_id)
        except AuthClientError as e:
            logger.error(f"Falha ao consultar status do lote {batch_id}: {e}")
            chat_history.append({
                "role": "assistant",
                "content": f"❌ Falha ao consultar o status da avaliação técnica: {e}",
            })
            yield _base(
                2, modal_visible=False, done=True,
                monitor_visible=True, monitor_content=lote_monitor_html(detail),
            )
            return
        yield _base(2, modal_visible=False, done=True, monitor_visible=True, monitor_content=lote_monitor_html(detail))

    if detail["status"] == "concluido":
        chat_history.append({
            "role": "assistant",
            "content": f"✅ Avaliação técnica concluída — {detail['evaluated_photos']} de "
                       f"{detail['total_photos']} fotos avaliadas.",
        })
    else:
        chat_history.append({
            "role": "assistant",
            "content": "❌ A avaliação técnica terminou em erro. As fotos já avaliadas foram preservadas.",
        })

    yield _base(
        2, modal_visible=False, done=True, monitor_visible=True,
        monitor_content=lote_monitor_html(detail), diagnostics_content=diagnostics_html(detail),
    )


def main():
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    demo = ui_layout(process_pipeline)
    demo.launch(
        theme=gr.themes.Soft(primary_hue="violet", secondary_hue="slate"),
        css=AUTH_CSS,
    )


if __name__ == "__main__":
    main()
