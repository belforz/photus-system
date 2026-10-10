from __future__ import annotations

from pathlib import Path

import gradio as gr

from photus.config import MAX_PHOTOS
from photus.ui.status import ui_status
from photus.utils import clean


def _counter_html(count: int) -> str:
    over = count > MAX_PHOTOS
    css_class = "photus-counter-badge over-limit" if over else "photus-counter-badge"
    return f'<span class="{css_class}">{count} / {MAX_PHOTOS} imagens anexadas</span>'


def _thumbnails(files) -> list:
    return [(f.name, Path(f.name).name) for f in (files or [])]


def build_submission_ui(process_pipeline, session_state):
    with gr.Row():
        with gr.Column(scale=1, elem_classes=["photus-card", "photus-card-wide"]) as submission_group:
            gr.Markdown("PHOTUS", elem_classes=["photus-eyebrow"])
            gr.Markdown("## Nova Avaliação", elem_classes=["photus-title"])
            gr.Markdown(
                "Descreva a estética ou os parâmetros desejados e envie as fotografias para roteamento semântico.",
                elem_classes=["photus-subtitle"],
            )

            text_input = gr.Textbox(
                label="Descreva a estética ou os parâmetros desejados",
                placeholder="Ex.: fotos com luz de fim de tarde suave, clima bucólico e nostálgico...",
                lines=3,
                elem_classes=["photus-input"],
            )
            gr.HTML(
                '<div class="photus-hint-block">'
                '<p><span class="photus-badge-pill photus-badge-route-fast">LEIGO</span> '
                '"Fotos com luz de fim de tarde suave, clima bucólico e nostálgico."</p>'
                '<p><span class="photus-badge-pill photus-badge-route-tecnico">TÉCNICO</span> '
                '"f/1.8, ISO 200, 1/500s, 50mm, luz lateral suave."</p>'
                "<p>Mínimo 5 caracteres (opcional).</p>"
                "</div>"
            )

            files_input = gr.File(
                label=f"Fotografias do lote (máximo {MAX_PHOTOS} imagens) — .jpg .jpeg .png",
                file_count="multiple",
                file_types=["image"],
                elem_classes=["photus-dropzone"],
            )

            with gr.Row(elem_classes=["photus-counter-row"]):
                gr.Markdown("Fotografias anexadas")
                counter_badge = gr.HTML(value=_counter_html(0))

            limit_banner = gr.Markdown(
                "Limite excedido: selecione no máximo 20 fotos por lote.",
                visible=False,
                elem_classes=["photus-banner-error"],
            )
            field_error_banner = gr.Markdown(visible=False, elem_classes=["photus-banner-error"])

            thumb_gallery = gr.Gallery(
                show_label=False,
                columns=4,
                height="auto",
                object_fit="cover",
                elem_classes=["photus-thumb-gallery"],
            )

            with gr.Row(elem_classes=["photus-action-bar"]):
                clear_btn = gr.Button("Limpar Seleção", elem_classes=["photus-btn-secondary"])
                submit_btn = gr.Button(
                    "Submeter Lote para Avaliação", elem_classes=["photus-btn-primary"], interactive=False
                )

            gr.Markdown("### Photus B — SBERT / classificação de sentimento", elem_classes=["photus-subtitle"])
            highlight_output = gr.HighlightedText(
                label="Texto com âncora destacada",
                combine_adjacent=True,
                show_legend=True,
                elem_classes=["photus-highlight"],
            )

        with gr.Column(scale=1) as status_group:
            pipeline_status = gr.HTML(value=ui_status(0), elem_id="pipeline_status", visible=False)
            chatbot = gr.Chatbot(height=300, visible=False)

    with gr.Column(visible=False, elem_classes=["photus-modal-overlay"]) as modal_group:
        with gr.Column(elem_classes=["photus-modal-card"]):
            modal_html = gr.HTML(value="")
            modal_close_btn = gr.Button("Fechar", elem_classes=["photus-btn-ghost"], visible=False)

    def _on_files_change(files):
        files = files or []
        count = len(files)
        over_limit = count > MAX_PHOTOS
        return (
            _counter_html(count),
            _thumbnails(files),
            gr.update(visible=over_limit),
            gr.update(interactive=count > 0 and not over_limit),
        )

    files_input.change(
        fn=_on_files_change,
        inputs=[files_input],
        outputs=[counter_badge, thumb_gallery, limit_banner, submit_btn],
    )

    pipeline_outputs = [
        chatbot,
        highlight_output,
        pipeline_status,
        modal_group,
        modal_html,
        modal_close_btn,
        text_input,
        files_input,
        field_error_banner,
    ]

    submit_btn.click(
        fn=process_pipeline, inputs=[text_input, files_input, chatbot, session_state], outputs=pipeline_outputs
    )
    modal_close_btn.click(fn=lambda: gr.update(visible=False), outputs=[modal_group])

    reset_outputs = [
        chatbot,
        highlight_output,
        pipeline_status,
        modal_group,
        modal_html,
        modal_close_btn,
        text_input,
        files_input,
        field_error_banner,
        thumb_gallery,
        counter_badge,
        limit_banner,
    ]

    def _reset():
        chat, highlight = clean()
        return (
            chat,
            highlight,
            ui_status(0),
            gr.update(visible=False),
            "",
            gr.update(visible=False),
            gr.update(value="", elem_classes=["photus-input"]),
            gr.update(value=None, elem_classes=["photus-dropzone"]),
            gr.update(visible=False),
            [],
            _counter_html(0),
            gr.update(visible=False),
        )

    clear_btn.click(fn=_reset, outputs=reset_outputs)

    return {
        "group": submission_group,
        "status_group": status_group,
        "modal_group": modal_group,
        "reset_fn": _reset,
        "reset_outputs": reset_outputs,
    }
