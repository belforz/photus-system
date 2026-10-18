import gradio as gr

from photus.ui.auth import build_auth_ui
from photus.ui.history import build_history_ui
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

            with gr.Row(elem_classes=["photus-nav"]):
                nav_new_btn = gr.Button("Nova Avaliação", size="sm", elem_classes=["photus-nav-btn"])
                nav_history_btn = gr.Button("Histórico", size="sm", elem_classes=["photus-nav-btn"])

            with gr.Column(visible=True) as new_view:
                submission = build_submission_ui(process_pipeline, auth["session_state"])

            history = build_history_ui(auth["session_state"], new_view, nav_new_btn, nav_history_btn)

        app_group.render()

        # RF14: trocar de sessão (login/logout) volta à Nova Avaliação e limpa o
        # que o usuário anterior via no Histórico/Resultado.
        # Isso inclui o formulário da Nova Avaliação (texto, fotos, miniaturas,
        # monitor e diagnóstico), que antes só era limpo ao carregar a página.
        for trigger in (auth["login_btn"], *auth["logout_buttons"]):
            trigger.click(fn=history["reset_fn"], outputs=history["reset_outputs"])
            trigger.click(fn=submission["reset_fn"], outputs=submission["reset_outputs"])

        demo.load(fn=submission["reset_fn"], outputs=submission["reset_outputs"]).then(
            fn=auth["bootstrap_fn"],
            inputs=[auth["session_state"]],
            outputs=auth["bootstrap_outputs"],
        )

    return demo
