import gradio as gr

from photus.config import MAX_PHOTOS
from photus.utils import clean


def ui_layout(process_pipeline):
    """Monta o layout Gradio. `process_pipeline` é injetado para evitar import
    circular com photus.app (que por sua vez importa este módulo)."""
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
                    label="Vibe / estética desejada",
                    placeholder="ex: quero uma foto com energia, movimento, sol forte...",
                    lines=3,
                )
                files_input = gr.File(
                    label=f"Upload de fotos (max. {MAX_PHOTOS})",
                    file_count="multiple",
                    file_types=["image"],
                )
                with gr.Row():
                    btn_process = gr.Button("▶️ Processar", variant="primary")
                    btn_clean = gr.Button("🧹 Limpar")

                gr.Markdown("### 🧭 Photus B — SBERT / classificação de sentimento")
                highlight_output = gr.HighlightedText(
                    label="Texto com âncora destacada",
                    combine_adjacent=True,
                    show_legend=True,
                )

            with gr.Column(scale=1):
                gr.Markdown("### 🔄 Pipeline")
                chatbot = gr.Chatbot(height=300)

                gr.Markdown("### 🏆 Photus A — top 3 fotos aprovadas")
                gallery_output = gr.Gallery(label="Top 3", columns=3, height=260)

        outputs = [chatbot, highlight_output, gallery_output]

        btn_process.click(
            fn=process_pipeline,
            inputs=[text_input, files_input, chatbot],
            outputs=outputs,
        )
        btn_clean.click(
            fn=clean,
            inputs=[],
            outputs=outputs,
        )
        demo.load(
            fn=clean,
            inputs=[],
            outputs=outputs,
        )

    return demo
