from __future__ import annotations

import html
from datetime import datetime

import gradio as gr

from photus.auth_client import AuthClientError, authenticate_user, register_user, update_profile
from photus.config import SESSION_BROWSER_SECRET
from photus.ui.theme import USER_TYPE_LABEL, avatar_initials

EMPTY_SESSION = {
    "token": None,
    "user_id": None,
    "name": None,
    "email": None,
    "user_type": None,
    "created_at": None,
}


def _screen(*, login=False, signup=False, profile=False, app=False):
    """gr.update tuple for (login_group, signup_group, profile_group, app_group, topbar)."""
    topbar_visible = profile or app
    return (
        gr.update(visible=login),
        gr.update(visible=signup),
        gr.update(visible=profile),
        gr.update(visible=app),
        gr.update(visible=topbar_visible),
    )


def _format_member_since(created_at: str | None) -> str:
    if not created_at:
        return (
            '<p class="photus-member-since-label">Membro Desde</p>'
            '<p class="photus-member-since-value">—</p>'
        )
    try:
        value = datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        value = created_at
    return (
        f'<p class="photus-member-since-label">Membro Desde</p>'
        f'<p class="photus-member-since-value">{html.escape(value)}</p>'
    )


def _profile_header_html(session: dict) -> str:
    initials = html.escape(avatar_initials(session.get("name")))
    name = html.escape(session.get("name") or "")
    type_label = html.escape(USER_TYPE_LABEL.get(session.get("user_type") or "", session.get("user_type") or ""))
    return (
        '<div class="photus-profile-header">'
        f'<div class="photus-avatar">{initials}</div>'
        f'<div><p class="photus-profile-name">{name}</p>'
        f'<span class="photus-badge">{type_label}</span></div>'
        "</div>"
    )


def build_auth_ui(app_group: gr.Column):
    """Monta topbar + telas de cadastro/login/perfil e devolve o session_state
    para o caller poder gatear conteudo autenticado (ex.: o pipeline em app_group)."""

    session_state = gr.BrowserState(
        dict(EMPTY_SESSION), storage_key="photus_session", secret=SESSION_BROWSER_SECRET
    )

    with gr.Row(elem_classes=["photus-topbar"], visible=False) as topbar:
        gr.Markdown("PHOTUS", elem_classes=["logo"])
        session_label = gr.Markdown("Convidado", elem_classes=["session"])
        with gr.Row():
            btn_topbar_profile = gr.Button("Perfil", elem_classes=["photus-btn-ghost"], size="sm")
            btn_topbar_logout = gr.Button("Sair", elem_classes=["photus-btn-ghost"], size="sm")

    # ------------------------------------------------------------------ #
    # Cadastro — UC01
    # ------------------------------------------------------------------ #
    with gr.Column(visible=True, elem_classes=["photus-card"]) as signup_group:
        gr.Markdown("PHOTUS", elem_classes=["photus-eyebrow"])
        gr.Markdown("## Criar Conta", elem_classes=["photus-title"])
        gr.Markdown("Acesse a plataforma de curadoria fotográfica contextual", elem_classes=["photus-subtitle"])
        signup_banner = gr.Markdown(visible=False, elem_classes=["photus-banner-error"])
        signup_name = gr.Textbox(
            label="Nome Completo", placeholder="Ex.: Leandro Belfor", max_lines=1, elem_classes=["photus-input"]
        )
        signup_email = gr.Textbox(
            label="E-mail", placeholder="seu.email@dominio.com", type="email", elem_classes=["photus-input"]
        )
        signup_email_error = gr.Markdown(visible=False, elem_classes=["photus-help-text", "error-text"])
        signup_password = gr.Textbox(
            label="Senha", placeholder="Digite sua senha segura", type="password", elem_classes=["photus-input"]
        )
        signup_password_toggle = gr.Checkbox(label="Mostrar senha", value=False)
        gr.Markdown("Mínimo 8 caracteres (armazenado com hash bcrypt).", elem_classes=["photus-help-text"])
        signup_user_type = gr.Radio(
            choices=[
                (
                    "Usuário Leigo — Busco avaliar fotos por sensações, estilo e linguagem natural.",
                    "leigo",
                ),
                (
                    "Fotógrafo — Busco análise técnica detalhada, parâmetros de câmera e iluminação.",
                    "fotografo",
                ),
            ],
            value="leigo",
            label="Como você se identifica?",
            elem_classes=["photus-radio-cards"],
        )
        signup_btn = gr.Button("Criar Conta", elem_classes=["photus-btn-primary"])
        signup_goto_login = gr.Button("Já possui uma conta? Faça login", elem_classes=["photus-btn-ghost"])

    # ------------------------------------------------------------------ #
    # Login — UC02
    # ------------------------------------------------------------------ #
    with gr.Column(visible=False, elem_classes=["photus-card"]) as login_group:
        gr.Markdown("PHOTUS", elem_classes=["photus-eyebrow"])
        gr.Markdown("## Entrar no Photus", elem_classes=["photus-title"])
        gr.Markdown("Bem-vindo de volta", elem_classes=["photus-subtitle"])
        login_banner = gr.Markdown(visible=False, elem_classes=["photus-banner-error"])
        login_email = gr.Textbox(
            label="E-mail", placeholder="seu.email@dominio.com", type="email", elem_classes=["photus-input"]
        )
        login_password = gr.Textbox(label="Senha", placeholder="Digite sua senha", type="password", elem_classes=["photus-input"])
        login_password_toggle = gr.Checkbox(label="Mostrar senha", value=False)
        login_btn = gr.Button("Entrar", elem_classes=["photus-btn-primary"])
        login_goto_signup = gr.Button("Ainda não tem conta? Cadastre-se", elem_classes=["photus-btn-ghost"])

    # ------------------------------------------------------------------ #
    # Perfil — UC03
    # ------------------------------------------------------------------ #
    with gr.Column(visible=False, elem_classes=["photus-card"]) as profile_group:
        profile_back_btn = gr.Button("← Voltar", elem_classes=["photus-btn-ghost"])
        profile_success_banner = gr.Markdown(visible=False, elem_classes=["photus-banner-success"])
        profile_error_banner = gr.Markdown(visible=False, elem_classes=["photus-banner-error"])
        profile_header = gr.HTML()
        gr.Markdown("Dados Pessoais", elem_classes=["photus-subtitle"])
        profile_name = gr.Textbox(label="Nome", max_lines=1, elem_classes=["photus-input"])
        profile_email = gr.Textbox(label="E-mail", type="email", elem_classes=["photus-input"])
        profile_member_since = gr.HTML()
        profile_save_btn = gr.Button("Salvar Alterações", elem_classes=["photus-btn-primary"])
        profile_cancel_btn = gr.Button("Cancelar / Descartar", elem_classes=["photus-btn-secondary"])
        profile_logout_btn = gr.Button("Sair da Conta (Logout)", elem_classes=["photus-btn-danger"])

    # ------------------------------------------------------------------ #
    # Wiring
    # ------------------------------------------------------------------ #

    signup_password_toggle.change(
        fn=lambda show: gr.update(type="text" if show else "password"),
        inputs=[signup_password_toggle],
        outputs=[signup_password],
    )
    login_password_toggle.change(
        fn=lambda show: gr.update(type="text" if show else "password"),
        inputs=[login_password_toggle],
        outputs=[login_password],
    )

    def _handle_signup(name, email, password, user_type):
        # NB: always returns the full tuple (banners + screen visibility) instead of
        # chaining .success(), which fires whenever the function doesn't raise — including
        # the error branches below, which catch AuthClientError and return normally.
        name = (name or "").strip()
        email = (email or "").strip()
        if len(name) < 3 or not email or not password:
            return (
                gr.update(visible=True, value="Preencha todos os campos obrigatórios."),
                gr.update(visible=False),
                gr.update(),
                *_screen(signup=True),
            )
        if len(password) < 8:
            return (
                gr.update(visible=True, value="A senha deve ter no mínimo 8 caracteres."),
                gr.update(visible=False),
                gr.update(),
                *_screen(signup=True),
            )
        try:
            register_user(name, email, password, user_type)
        except AuthClientError as e:
            if e.status_code == 409:
                message = "Este e-mail já está cadastrado no sistema."
                return gr.update(visible=False), gr.update(visible=True, value=message), gr.update(), *_screen(signup=True)
            if e.status_code == 422:
                message = "Preencha todos os campos obrigatórios corretamente."
            else:
                message = str(e)
            return gr.update(visible=True, value=message), gr.update(visible=False), gr.update(), *_screen(signup=True)
        return gr.update(visible=False), gr.update(visible=False), gr.update(value=email), *_screen(login=True)

    signup_btn.click(
        fn=_handle_signup,
        inputs=[signup_name, signup_email, signup_password, signup_user_type],
        outputs=[
            signup_banner,
            signup_email_error,
            login_email,
            login_group,
            signup_group,
            profile_group,
            app_group,
            topbar,
        ],
    )

    def _handle_login(email, password, session):
        email = (email or "").strip()
        if not email or not password:
            return gr.update(visible=True, value="Preencha e-mail e senha."), session, gr.update()
        try:
            result = authenticate_user(email, password)
        except AuthClientError:
            return (
                gr.update(visible=True, value="E-mail ou senha inválidos. Verifique suas credenciais."),
                session,
                gr.update(),
            )
        new_session = {
            **EMPTY_SESSION,
            "token": result["access_token"],
            "user_id": result["usuario_id"],
            "name": result["nome"],
            "email": result["email"],
            "user_type": result["tipo_usuario"],
        }
        return gr.update(visible=False), new_session, gr.update(value=f"Sessão: **{result['nome']}**")

    login_btn.click(
        fn=_handle_login,
        inputs=[login_email, login_password, session_state],
        outputs=[login_banner, session_state, session_label],
    ).then(
        # .then() (not .success()) on purpose: visibility is always re-derived from the
        # resulting session_state, so both the error path (token stays None) and the
        # success path land on the correct screen.
        fn=lambda session: _screen(app=True) if session.get("token") else _screen(login=True),
        inputs=[session_state],
        outputs=[login_group, signup_group, profile_group, app_group, topbar],
    )

    login_goto_signup.click(
        fn=lambda: (*_screen(signup=True), gr.update(visible=False)),
        outputs=[login_group, signup_group, profile_group, app_group, topbar, login_banner],
    )
    signup_goto_login.click(
        fn=lambda: (*_screen(login=True), gr.update(visible=False), gr.update(visible=False)),
        outputs=[login_group, signup_group, profile_group, app_group, topbar, signup_banner, signup_email_error],
    )

    def _open_profile(session):
        if not session or not session.get("token"):
            return (
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(visible=False),
                gr.update(visible=False),
                *_screen(login=True),
            )
        return (
            _profile_header_html(session),
            session.get("name") or "",
            session.get("email") or "",
            _format_member_since(session.get("created_at")),
            gr.update(visible=False),
            gr.update(visible=False),
            *_screen(profile=True),
        )

    btn_topbar_profile.click(
        fn=_open_profile,
        inputs=[session_state],
        outputs=[
            profile_header,
            profile_name,
            profile_email,
            profile_member_since,
            profile_success_banner,
            profile_error_banner,
            login_group,
            signup_group,
            profile_group,
            app_group,
            topbar,
        ],
    )

    profile_back_btn.click(
        fn=lambda: _screen(app=True),
        outputs=[login_group, signup_group, profile_group, app_group, topbar],
    )

    def _handle_logout():
        return dict(EMPTY_SESSION), gr.update(value="Convidado"), *_screen(login=True)

    for btn in (btn_topbar_logout, profile_logout_btn):
        btn.click(
            fn=_handle_logout,
            outputs=[session_state, session_label, login_group, signup_group, profile_group, app_group, topbar],
        )

    def _handle_profile_save(name, email, session):
        if not session or not session.get("token"):
            return gr.update(visible=False), gr.update(visible=True, value="Sessão expirada. Faça login novamente."), session
        try:
            result = update_profile(
                session["token"],
                name=(name or "").strip() or None,
                email=(email or "").strip() or None,
            )
        except AuthClientError as e:
            if e.status_code == 409:
                message = "O e-mail informado já está em uso por outro usuário."
            elif e.status_code == 401:
                return gr.update(visible=False), gr.update(visible=True, value="Sessão expirada. Faça login novamente."), dict(EMPTY_SESSION)
            else:
                message = str(e)
            return gr.update(visible=False), gr.update(visible=True, value=message), session
        updated_session = {**session, "name": result["nome"], "email": result["email"], "user_type": result["tipo_usuario"]}
        return gr.update(visible=True, value="Perfil atualizado com sucesso!"), gr.update(visible=False), updated_session

    profile_save_btn.click(
        fn=_handle_profile_save,
        inputs=[profile_name, profile_email, session_state],
        outputs=[profile_success_banner, profile_error_banner, session_state],
    ).then(
        fn=lambda session: (
            _profile_header_html(session)
            if session.get("token")
            else '<p class="photus-profile-name">Sessão expirada</p>'
        ),
        inputs=[session_state],
        outputs=[profile_header],
    ).then(
        fn=lambda session: (*_screen(profile=True),) if session.get("token") else (*_screen(login=True),),
        inputs=[session_state],
        outputs=[login_group, signup_group, profile_group, app_group, topbar],
    ).then(
        fn=lambda session: gr.update(value=f"Sessão: **{session['name']}**") if session.get("token") else gr.update(value="Convidado"),
        inputs=[session_state],
        outputs=[session_label],
    )

    profile_cancel_btn.click(
        fn=lambda session: (
            session.get("name") or "",
            session.get("email") or "",
            gr.update(visible=False),
            gr.update(visible=False),
        ),
        inputs=[session_state],
        outputs=[profile_name, profile_email, profile_success_banner, profile_error_banner],
    )

    def _bootstrap(session):
        if session and session.get("token"):
            return (*_screen(app=True), gr.update(value=f"Sessão: **{session.get('name')}**"))
        return (*_screen(login=True), gr.update(value="Convidado"))

    return {
        "session_state": session_state,
        "groups": [login_group, signup_group, profile_group, topbar],
        "bootstrap_fn": _bootstrap,
        "bootstrap_outputs": [login_group, signup_group, profile_group, app_group, topbar, session_label],
    }
