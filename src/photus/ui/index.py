import gradio as gr

from photus.ui.auth import build_auth_ui
from photus.ui.submission import build_submission_ui


def ui_layout(process_pipeline):
    with gr.Blocks(title="Photus — Demo do Ecossistema") as demo:
        app_group = gr.Column(visible=False, render=False)

        auth = build_auth_ui(app_group)

        with app_group:
            gr.Markdown(
                """
                # Photus System
                """
            )
            # gr.Markdown(
            #     """
            #     Template inicial representando o fluxo:
            #     `Upload → Pasta de staging → Photus B (SBERT) → Preprocessor → Photus A (OpenCV + Random Forest) → Top 3`
            #     """
            # )

            submission = build_submission_ui(process_pipeline, auth["session_state"])

        app_group.render()

        demo.load(fn=submission["reset_fn"], outputs=submission["reset_outputs"]).then(
            fn=auth["bootstrap_fn"],
            inputs=[auth["session_state"]],
            outputs=auth["bootstrap_outputs"],
        )

    return demo
