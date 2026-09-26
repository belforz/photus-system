import gradio as gr

from photus.config import MAX_PHOTOS
from photus.ui.results import ui_results
from photus.ui.status import ui_status
from photus.utils import clean


def ui_layout_pipeline():
    return gr.HTML(value=ui_status(0), elem_id="pipeline_status")


def ui_layout(process_pipeline):
    with gr.Blocks(title="Photus — Demo do Ecossistema") as demo:
        gr.Markdown(
            """
            # Photus System
            Template inicial representando o fluxo:
            `Upload → Pasta de staging → Photus B (SBERT) → Preprocessor → Photus A (OpenCV + Random Forest) → Top 3`
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                text_input = gr.Textbox(
                    label="Input",
                    placeholder="ex: quero uma foto com energia, movimento, sol forte...",
                    lines=3,
                    elem_classes=["photus-input"],
                )
                files_input = gr.File(
                    label=f"Upload de fotos (max. {MAX_PHOTOS})",
                    file_count="multiple",
                    file_types=["image"],
                    elem_classes=["photus-dropzone"],
                )
                with gr.Row():
                    btn_process = gr.Button(" Processar", variant="primary", elem_classes=["photus-btn"])
                    btn_clean = gr.Button(" Limpar", elem_classes=["photus-btn"])

                gr.Markdown("### Photus B — SBERT / classificação de sentimento")
                highlight_output = gr.HighlightedText(
                    label="Texto com âncora destacada",
                    combine_adjacent=True,
                    show_legend=True,
                )

            with gr.Column(scale=1):
                gr.Markdown("### Status do pipeline")
                pipeline_status = ui_layout_pipeline()
                chatbot = gr.Chatbot(height=300)

                gr.Markdown("### Photus A — resultado da avaliação")
                gallery_output = gr.Gallery(
                    label="Fotos avaliadas",
                    columns=3,
                    height=260,
                    elem_classes=["photus-gallery"],
                )
                results_output = gr.HTML(value=ui_results([], total_scored=0))


        outputs = [chatbot, highlight_output, gallery_output, results_output, pipeline_status]

        def _reset():
            chat, highlight, gallery, results_html = clean()
            return chat, highlight, gallery, results_html, ui_status(0)

        btn_process.click(
            fn=process_pipeline,
            inputs=[text_input, files_input, chatbot],
            outputs=outputs,
        )
        btn_clean.click(
            fn=_reset,
            inputs=[],
            outputs=outputs,
        )
        demo.load(
            fn=_reset,
            inputs=[],
            outputs=outputs,
        )

    return demo
