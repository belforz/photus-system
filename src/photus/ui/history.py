"""Sprint 4 — Histórico de Lotes (UC07), Resultado (UC08/UC09) e Exclusão (UC10).

Três "telas" dentro do app autenticado: Nova Avaliação (existente), Histórico e
Resultado. A navegação só alterna visibilidade. Listas e galerias usam
`gr.render` para ter botões reais por linha/foto.
"""

from __future__ import annotations

import html as _html
import json

import gradio as gr
from loguru import logger

from photus.auth_client import AuthClientError
from photus.evaluation_batch_client import (
    delete_evaluation_batch,
    get_evaluation_batch,
    list_evaluation_batches,
)
from photus.thumbnails import load_thumbnails
from photus.ui.evaluation import diagnostic_card_html
from photus.ui.results import (
    apply_filter,
    delete_modal_html,
    denied_html,
    filter_choices,
    filter_history,
    gallery_title_html,
    history_empty_html,
    history_header_html,
    history_row_html,
    photo_card_html,
    result_header_html,
    result_notice_html,
    top3_card_html,
    top3_photos,
    top3_title_html,
)

POLL_SECONDS = 3.0
SESSION_EXPIRED = "Sessão expirada. Faça login novamente."


def _token(session: dict | None) -> str | None:
    return (session or {}).get("token")


def _drawer_html(photo: dict, thumbs: dict[str, str]) -> str:
    uri = thumbs.get(photo.get("id", ""))
    img = f'<img class="photus-drawer-img" src="{uri}" alt="">' if uri else ""
    raw = photo.get("metrics_json")
    raw_html = (
        '<details class="photus-drawer-raw"><summary>metricas_json (bruto)</summary>'
        f"<pre>{_html.escape(json.dumps(raw, ensure_ascii=False, indent=2))}</pre></details>"
        if raw
        else '<p class="photus-muted">Sem métricas técnicas registradas para esta fotografia.</p>'
    )
    return (
        '<p class="photus-lote-id-label">Métricas Técnicas</p>'
        f"{img}{diagnostic_card_html(photo)}{raw_html}"
    )


def build_history_ui(session_state, new_view, nav_new_btn, nav_history_btn):
    history_state = gr.State([])
    detail_state = gr.State(None)
    thumbs_state = gr.State({})
    pending_delete = gr.State(None)
    poll_timer = gr.Timer(POLL_SECONDS, active=False)

    # ------------------------------------------------------------ layout
    with gr.Column(visible=False, elem_classes=["photus-page"]) as history_view:
        gr.HTML(
            '<div class="photus-page-head"><p class="photus-page-title">Meu Histórico de Curadorias</p></div>',
            elem_classes=["photus-history-title"],
        )
        with gr.Row(elem_classes=["photus-history-toolbar"]):
            search_box = gr.Textbox(
                placeholder="Buscar pelo texto da solicitação...",
                show_label=False,
                container=False,
                max_lines=1,
                elem_classes=["photus-input", "photus-search"],
            )
            new_eval_btn = gr.Button("+ Nova Avaliação", elem_classes=["photus-btn-primary"])
        history_error = gr.Markdown(visible=False, elem_classes=["photus-banner-error"])
        history_success = gr.Markdown(visible=False, elem_classes=["photus-banner-success"])

        @gr.render(inputs=[history_state, search_box])
        def _render_history(items, query):
            items = items or []
            shown = filter_history(items, query)
            gr.HTML(history_header_html(len(items), len(shown), (query or "").strip(), title=False))
            if not shown:
                gr.HTML(history_empty_html(filtered=bool(items)))
                if not items:
                    first_btn = gr.Button("Criar primeira avaliação", elem_classes=["photus-btn-primary"])
                    first_btn.click(fn=lambda: _nav("new"), outputs=NAV_OUTPUTS)
                return
            for item in shown:
                with gr.Row(elem_classes=["photus-history-row"]):
                    gr.HTML(history_row_html(item), elem_classes=["photus-history-html"])
                    open_btn = gr.Button(
                        "Visualizar Resultados", size="sm", elem_classes=["photus-btn-secondary", "photus-row-btn"]
                    )
                    del_btn = gr.Button(
                        "🗑", size="sm", min_width=44, elem_classes=["photus-btn-icon-danger"]
                    )
                open_btn.click(fn=_make_open_result(item["id"]), inputs=[session_state], outputs=OPEN_RESULT_OUTPUTS)
                del_btn.click(
                    fn=_make_ask_delete(item),
                    outputs=[pending_delete, delete_modal_body, delete_modal_group],
                )

    with gr.Column(visible=False, elem_classes=["photus-page"]) as result_view:
        back_btn = gr.Button("← Voltar ao Histórico", elem_classes=["photus-btn-ghost", "photus-back-btn"])
        result_error = gr.Markdown(visible=False, elem_classes=["photus-banner-error"])
        result_header = gr.HTML()
        result_notice = gr.HTML()

        @gr.render(inputs=[detail_state, thumbs_state])
        def _render_top3(detail, thumbs):
            if not detail or not detail.get("is_singular"):
                return
            top = top3_photos(detail)
            gr.HTML(top3_title_html(len(top)))
            with gr.Row(elem_classes=["photus-top3-grid"]):
                for rank, photo in enumerate(top, start=1):
                    with gr.Column(elem_classes=["photus-photo-card", "top3", f"rank-{rank}"], min_width=0):
                        gr.HTML(top3_card_html(photo, rank, thumbs or {}))
                        btn = gr.Button("Ver Métricas Técnicas", size="sm", elem_classes=["photus-btn-secondary"])
                    btn.click(
                        fn=_make_open_drawer(photo), inputs=[thumbs_state], outputs=[drawer_body, drawer_group]
                    )

        filter_radio = gr.Radio(
            choices=[("Todas (0)", "todas")],
            value="todas",
            show_label=False,
            container=False,
            elem_classes=["photus-filter-chips"],
            visible=False,
        )

        @gr.render(inputs=[detail_state, thumbs_state, filter_radio])
        def _render_gallery(detail, thumbs, flt):
            if not detail:
                return
            photos = apply_filter(detail.get("photos", []), flt)
            gr.HTML(gallery_title_html(len(photos), len(detail.get("photos", []))))
            with gr.Row(elem_classes=["photus-photo-grid"]):
                for photo in photos:
                    with gr.Column(elem_classes=["photus-photo-card"], min_width=0):
                        gr.HTML(photo_card_html(photo, thumbs or {}))
                        btn = gr.Button("Ver Métricas Técnicas", size="sm", elem_classes=["photus-btn-secondary"])
                    btn.click(
                        fn=_make_open_drawer(photo), inputs=[thumbs_state], outputs=[drawer_body, drawer_group]
                    )

    with gr.Column(visible=False, elem_classes=["photus-modal-overlay"]) as delete_modal_group:
        with gr.Column(elem_classes=["photus-modal-card", "photus-delete-modal"]):
            delete_modal_body = gr.HTML()
            with gr.Row():
                delete_cancel_btn = gr.Button("Cancelar", elem_classes=["photus-btn-secondary"])
                delete_confirm_btn = gr.Button("Sim, Excluir Lote", elem_classes=["photus-btn-danger"])

    with gr.Column(visible=False, elem_classes=["photus-drawer-overlay"]) as drawer_group:
        with gr.Column(elem_classes=["photus-drawer"]):
            drawer_close_btn = gr.Button("✕ Fechar", size="sm", elem_classes=["photus-btn-secondary"])
            drawer_body = gr.HTML()

    # --------------------------------------------------------- navegação
    NAV_OUTPUTS = [new_view, history_view, result_view, detail_state, thumbs_state, poll_timer, drawer_group]

    def _nav(target: str):
        return (
            gr.update(visible=target == "new"),
            gr.update(visible=target == "history"),
            gr.update(visible=target == "result"),
            None,
            {},
            gr.Timer(active=False),
            gr.update(visible=False),
        )

    # -------------------------------------------------------------- UC07
    HISTORY_OUTPUTS = [*NAV_OUTPUTS, history_state, history_error, history_success]

    def _open_history(session):
        nav = _nav("history")
        token = _token(session)
        if not token:
            return (*nav, [], gr.update(visible=True, value=SESSION_EXPIRED), gr.update(visible=False))
        try:
            items = list_evaluation_batches(token)
        except AuthClientError as e:
            logger.error(f"Falha ao listar o histórico: {e}")
            message = SESSION_EXPIRED if e.status_code == 401 else f"Não foi possível carregar o histórico: {e}"
            return (*nav, [], gr.update(visible=True, value=message), gr.update(visible=False))
        return (*nav, items, gr.update(visible=False), gr.update(visible=False))

    nav_history_btn.click(fn=_open_history, inputs=[session_state], outputs=HISTORY_OUTPUTS)
    nav_new_btn.click(fn=lambda: _nav("new"), outputs=NAV_OUTPUTS)
    new_eval_btn.click(fn=lambda: _nav("new"), outputs=NAV_OUTPUTS)
    back_btn.click(fn=_open_history, inputs=[session_state], outputs=HISTORY_OUTPUTS)

    # ------------------------------------------------------- UC08 / UC09
    RESULT_OUTPUTS = [detail_state, thumbs_state, result_header, result_notice, filter_radio, result_error, poll_timer]
    OPEN_RESULT_OUTPUTS = [new_view, history_view, result_view, drawer_group, *RESULT_OUTPUTS]

    def _result_updates(detail: dict, thumbs: dict, *, reset_filter: bool):
        radio = gr.update(choices=filter_choices(detail), visible=True)
        if reset_filter:
            radio = gr.update(choices=filter_choices(detail), value="todas", visible=True)
        return (
            detail,
            thumbs,
            result_header_html(detail),
            result_notice_html(detail),
            radio,
            gr.update(visible=False),
            gr.Timer(active=detail.get("status") == "em_processamento"),
        )

    def _error_result(message: str, *, denied: bool = False):
        return (
            None,
            {},
            denied_html(message) if denied else "",
            "",
            gr.update(visible=False),
            gr.update(visible=not denied, value=message),
            gr.Timer(active=False),
        )

    def _make_open_result(batch_id: str):
        def _open(session):
            show = (gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False))
            token = _token(session)
            if not token:
                return (*show, *_error_result(SESSION_EXPIRED))
            try:
                detail = get_evaluation_batch(token, batch_id)
            except AuthClientError as e:
                if e.status_code == 403:  # A1 / RF14
                    logger.warning(f"Acesso negado ao lote {batch_id}")
                    return (*show, *_error_result(str(e), denied=True))
                logger.error(f"Falha ao abrir o lote {batch_id}: {e}")
                message = SESSION_EXPIRED if e.status_code == 401 else str(e)
                return (*show, *_error_result(message))
            thumbs = load_thumbnails(token, detail)
            return (*show, *_result_updates(detail, thumbs, reset_filter=True))

        return _open

    def _refresh_result(session, detail):
        """Tick do timer: reconsulta o lote enquanto estiver em processamento (A2)."""
        token = _token(session)
        if not token or not detail:
            return (gr.skip(),) * 6 + (gr.Timer(active=False),)
        try:
            fresh = get_evaluation_batch(token, detail["id"])
        except AuthClientError as e:
            logger.error(f"Falha ao atualizar o lote {detail['id']}: {e}")
            return (gr.skip(),) * 5 + (gr.update(visible=True, value=str(e)), gr.Timer(active=False))
        thumbs = load_thumbnails(token, fresh)
        return _result_updates(fresh, thumbs, reset_filter=False)

    poll_timer.tick(fn=_refresh_result, inputs=[session_state, detail_state], outputs=RESULT_OUTPUTS)

    def _make_open_drawer(photo: dict):
        def _open(thumbs):
            return _drawer_html(photo, thumbs or {}), gr.update(visible=True)

        return _open

    drawer_close_btn.click(fn=lambda: gr.update(visible=False), outputs=[drawer_group])

    # -------------------------------------------------------------- UC10
    def _make_ask_delete(item: dict):
        def _ask():
            return item, delete_modal_html(item), gr.update(visible=True)

        return _ask

    def _cancel_delete():
        # A2 — nenhuma chamada à API; nada é alterado.
        return None, gr.update(visible=False)

    delete_cancel_btn.click(fn=_cancel_delete, outputs=[pending_delete, delete_modal_group])

    def _confirm_delete(session, item):
        hidden = gr.update(visible=False)
        token = _token(session)
        if not item:
            return gr.skip(), gr.skip(), gr.skip(), None, hidden
        if not token:
            return gr.skip(), gr.update(visible=True, value=SESSION_EXPIRED), hidden, None, hidden
        try:
            delete_evaluation_batch(token, item["id"])
            outcome = gr.update(visible=True, value="Lote excluído com sucesso."), None
        except AuthClientError as e:
            if e.status_code == 403:
                outcome = None, "Acesso negado. Você não tem permissão para excluir este lote."
            elif e.status_code == 404:  # já não existe: só atualiza a lista
                outcome = gr.update(visible=True, value="Este lote já havia sido excluído."), None
            elif e.status_code == 401:
                outcome = None, SESSION_EXPIRED
            else:
                logger.error(f"Falha ao excluir o lote {item['id']}: {e}")
                outcome = None, f"Não foi possível excluir o lote: {e}"
        success, error = outcome
        try:
            items = list_evaluation_batches(token)
        except AuthClientError:
            items = gr.skip()
        return (
            items,
            gr.update(visible=bool(error), value=error or ""),
            success if success is not None else gr.update(visible=False),
            None,
            hidden,
        )

    delete_confirm_btn.click(
        fn=_confirm_delete,
        inputs=[session_state, pending_delete],
        outputs=[history_state, history_error, history_success, pending_delete, delete_modal_group],
    )

    # ------------------------------------------------- reset (login/logout)
    RESET_OUTPUTS = [
        *NAV_OUTPUTS,
        history_state,
        history_error,
        history_success,
        search_box,
        result_header,
        result_notice,
        pending_delete,
        delete_modal_group,
    ]

    def _reset():
        """RF14: ao trocar de sessão nada do usuário anterior pode ficar na tela."""
        return (
            *_nav("new"),
            [],
            gr.update(visible=False),
            gr.update(visible=False),
            "",
            "",
            "",
            None,
            gr.update(visible=False),
        )

    return {"reset_fn": _reset, "reset_outputs": RESET_OUTPUTS}
