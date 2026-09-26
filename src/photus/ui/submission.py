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
    """Monta a tela de submissão + modal de roteamento e o painel de status
    do pipeline completo. Devolve os componentes para o caller (ui_layout)
    poder colocá-los dentro do app_group autenticado.

    `session_state` (o `gr.BrowserState` de `build_auth_ui`) é passado como
    input extra de `process_pipeline` — o token do usuário é necessário para
    autenticar a chamada a `POST /batches` no Photus UC."""

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
            # Removido da UI a pedido — mantido (oculto) para não quebrar o
            # wiring de process_pipeline, que ainda lê/escreve nesses componentes:
            # gr.Markdown("### Status do pipeline")
            pipeline_status = gr.HTML(value=ui_status(0), elem_id="pipeline_status", visible=False)
            chatbot = gr.Chatbot(height=300, visible=False)

    # ------------------------------------------------------------------ #
    # Modal de Processamento / Roteamento Semântico (UC05) — overlay
    # ------------------------------------------------------------------ #
    with gr.Column(visible=False, elem_classes=["photus-modal-overlay"]) as modal_group:
        with gr.Column(elem_classes=["photus-modal-card"]):
            modal_html = gr.HTML(value="")
            modal_close_btn = gr.Button("Fechar", elem_classes=["photus-btn-ghost"], visible=False)

    # ------------------------------------------------------------------ #
    # Wiring — contador / miniaturas / limite (Secao 2 / A1)
    # ------------------------------------------------------------------ #

    def _on_files_change(files):
        files = files or []
        count = len(files)
        over_limit = count > MAX_PHOTOS
        # Nao mexer no value de files_input aqui: um gr.update(value=...) no
        # proprio componente que disparou o .change() re-executa este mesmo
        # callback (Gradio nao distingue update programatico de interacao do
        # usuario) — um auto-trim reentraria com a lista ja cortada
        # (over_limit=False) e apagaria o banner "Limite excedido" que acabou
        # de aparecer. Em vez de truncar, so bloqueia o envio (RF07 pede
        # "bloqueia o envio", nao remover fotos por conta propria) — o
        # usuario remove o excedente pelos botoes [x] nativos da lista.
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

    # ------------------------------------------------------------------ #
    # Wiring — submissão (UC04) + roteamento (UC05)
    # ------------------------------------------------------------------ #

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

    # ------------------------------------------------------------------ #
    # Wiring — Limpar Seleção
    # ------------------------------------------------------------------ #

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
