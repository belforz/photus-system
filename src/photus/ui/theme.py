# Paleta e componentes visuais extraídos do protótipo Figma (sprint-1,
# nCVHiSAC6J7OECKp8ID1dR) — telas 01-Cadastro / 02-Login / 03-Perfil — e da
# sprint-2 (zhmI5yLobBrLprX8KKW5EW) — telas de submissão/roteamento.

import gradio as gr

AUTH_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

:root {
    --photus-bg: #121214;
    --photus-surface: #20242d;
    --photus-surface-input: #1a1d24;
    --photus-border: #33363f;
    --photus-accent: #6366f1;
    --photus-accent-hover: #4f46e5;
    --photus-success: #10b981;
    --photus-error: #ef4444;
    --photus-warning: #f59e0b;
    --photus-llm: #a78bfa;
    --photus-text-primary: #f5f5f7;
    --photus-text-secondary: #9ca3af;
}

.gradio-container {
    background: var(--photus-bg) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}

/* ---------- Topbar ---------- */
.photus-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--photus-surface) !important;
    border: 1px solid var(--photus-border);
    border-radius: 12px;
    padding: 14px 24px !important;
    margin-bottom: 20px;
}
.photus-topbar .logo, .photus-topbar .logo * { color: var(--photus-accent) !important; font-weight: 700; font-size: 15px; letter-spacing: .04em; }
.photus-topbar .session, .photus-topbar .session * { color: var(--photus-text-secondary) !important; font-size: 13px; }
.photus-topbar .session strong, .photus-topbar .session b { color: var(--photus-text-primary) !important; }

/* ---------- Card ---------- */
.photus-card {
    background: var(--photus-surface) !important;
    border-radius: 12px;
    padding: 32px 40px !important;
    max-width: 560px;
    margin: 40px auto;
}
/* Gradio Markdown renderiza o texto dentro de um <p>/<h*> filho que carrega a
   cor padrao do tema (quase preta) com especificidade maior que a nossa
   classe no container — por isso miramos tambem os descendentes (*). */
.photus-eyebrow, .photus-eyebrow * { color: var(--photus-accent) !important; font-weight: 700; font-size: 12px; letter-spacing: .05em; margin: 0; }
.photus-title, .photus-title * { color: var(--photus-text-primary) !important; font-size: 26px; font-weight: 700; margin: 4px 0 2px; }
.photus-subtitle, .photus-subtitle * { color: var(--photus-text-secondary) !important; font-size: 14px; margin: 0 0 8px; font-weight: 400; }
.photus-footer-text, .photus-footer-text * { color: var(--photus-text-secondary) !important; font-size: 13px; }

/* Gradio wraps every component in generic .block/.form chrome (light theme
   colors by default) — inside our dark cards/topbar we strip that chrome so
   only our own classes control the look. Scoped so the pipeline screen
   (outside these containers) keeps its original Soft-theme styling. */
.photus-card .block,
.photus-card .form,
.photus-topbar .block,
.photus-topbar .form {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Gradio (tema Soft) desenha o texto do label como um "chip" com fundo lilás
   claro (pill) — ilegível/deslocado sobre os cards escuros. Neutraliza em
   qualquer label dentro dos nossos cards/topbar, não só nos inputs. O label
   de grupo do gr.Radio usa <fieldset><span> em vez de <label><span>, por
   isso miramos os dois casos. */
.photus-card label > span,
.photus-card fieldset > span,
.photus-topbar label > span,
.photus-topbar fieldset > span {
    background: transparent !important;
    padding: 0 !important;
    color: var(--photus-text-secondary) !important;
}

/* ---------- Inputs (gr.Textbox / gr.Radio reskin) ---------- */
.photus-input label > span:first-child {
    color: var(--photus-text-secondary) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.photus-input input, .photus-input textarea {
    background: var(--photus-surface-input) !important;
    border: 1px solid var(--photus-border) !important;
    border-radius: 8px !important;
    color: var(--photus-text-primary) !important;
    font-size: 15px !important;
    padding: 12px 14px !important;
}
/* Rede de seguranca: o Gradio as vezes mede o auto-grow do textarea antes do
   layout/CSS estabilizar e trava um inline style.height gigante (bug de
   timing). max-height com !important vence o inline style e mantem o campo
   compacto mesmo se isso acontecer de novo — os campos aqui sao todos
   single-line (max_lines=1 / type="email"/"password"). */
.photus-input textarea {
    max-height: 46px !important;
    resize: none !important;
}
.photus-input input:focus, .photus-input textarea:focus {
    border-color: var(--photus-accent) !important;
    box-shadow: 0 0 0 1px var(--photus-accent) !important;
}
.photus-input.field-error input, .photus-input.field-error textarea {
    border-color: var(--photus-error) !important;
}
/* NB: nunca usar margin negativa aqui. O Gradio anima blocos que aparecem/
   mudam de posicao com um FLIP (measure start rect -> animate para o rect
   final via --start-top/--start-height etc.) e uma margem negativa faz esse
   calculo de delta disparar, travando o elemento com uma altura absurda
   (~800px) que "engole" visualmente o conteudo seguinte. Margem positiva
   pequena, sem negativos. */
.photus-help-text { margin: 2px 0 8px; }
.photus-help-text, .photus-help-text * { color: var(--photus-text-secondary) !important; font-size: 12px !important; }
.photus-help-text.error-text, .photus-help-text.error-text * { color: var(--photus-error) !important; font-weight: 600; }

/* ---------- Buttons ---------- */
.photus-btn-primary { background: var(--photus-accent) !important; color: #fff !important; border: none !important; }
.photus-btn-primary:hover { background: var(--photus-accent-hover) !important; }
.photus-btn-secondary { background: var(--photus-surface-input) !important; border: 1px solid var(--photus-border) !important; color: var(--photus-text-primary) !important; }
.photus-btn-danger { background: var(--photus-error) !important; color: #fff !important; border: none !important; }
.photus-btn-ghost { background: transparent !important; border: none !important; color: var(--photus-accent) !important; font-weight: 600 !important; box-shadow: none !important; }
.photus-btn-primary, .photus-btn-secondary, .photus-btn-danger {
    border-radius: 8px !important; font-weight: 600 !important; font-size: 15px !important;
}

/* ---------- Radio cards (tipo de perfil) ---------- */
.photus-radio-cards .wrap { display: flex; flex-direction: column; gap: 10px; }
.photus-radio-cards label {
    border: 1px solid var(--photus-border) !important;
    background: var(--photus-surface) !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    color: var(--photus-text-primary) !important;
    font-size: 14px !important;
    white-space: normal !important;
}
.photus-radio-cards label:has(input:checked) {
    border: 2px solid var(--photus-accent) !important;
}

/* ---------- Banners / toasts inline ---------- */
.photus-banner-error, .photus-banner-error * {
    background: transparent;
    color: var(--photus-error) !important;
    font-size: 13px;
    font-weight: 600;
}
.photus-banner-error {
    background: rgba(239, 68, 68, 0.12) !important;
    border: 1px solid var(--photus-error);
    border-radius: 8px;
    padding: 12px 16px !important;
}
.photus-banner-success, .photus-banner-success * {
    background: transparent;
    color: var(--photus-success) !important;
    font-size: 13px;
    font-weight: 600;
}
.photus-banner-success {
    background: rgba(16, 185, 129, 0.12) !important;
    border: 1px solid var(--photus-success);
    border-radius: 8px;
    padding: 10px 16px !important;
}

/* ---------- Perfil: avatar + badge ---------- */
.photus-avatar {
    width: 56px; height: 56px; border-radius: 50%;
    background: var(--photus-accent); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 18px; flex-shrink: 0;
}
.photus-profile-header { display: flex; align-items: center; gap: 16px; margin-bottom: 4px; }
.photus-profile-name { color: var(--photus-text-primary); font-size: 20px; font-weight: 700; margin: 0; }
.photus-badge {
    display: inline-block; border: 1px solid var(--photus-accent); color: var(--photus-accent);
    font-size: 12px; font-weight: 600; border-radius: 999px; padding: 3px 10px; margin-top: 4px;
}
.photus-member-since-label { color: var(--photus-text-secondary); font-size: 13px; font-weight: 600; margin: 0; }
.photus-member-since-value { color: var(--photus-text-primary); font-size: 14px; margin: 2px 0 0; }

/* ---------- Sprint 2: Submissao (UC04) — card largo ---------- */
.photus-card.photus-card-wide { max-width: 720px; }

.photus-hint-block { margin: 8px 0 4px; display: flex; flex-direction: column; gap: 6px; }
.photus-hint-block p { color: var(--photus-text-secondary) !important; font-size: 12.5px !important; margin: 0 !important; display: flex; align-items: center; gap: 8px; }
.photus-hint-block .photus-badge-pill { flex-shrink: 0; font-size: 10.5px; padding: 2px 9px; }

/* ---------- Dropzone (gr.File reskin) ---------- */
.photus-dropzone.block { background: var(--photus-surface-input) !important; }
.photus-dropzone, .photus-dropzone .wrap {
    border: 1.5px dashed var(--photus-border) !important;
    border-radius: 10px !important;
    background: var(--photus-surface-input) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.photus-dropzone:hover, .photus-dropzone .wrap:hover {
    border-color: var(--photus-accent) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}
.photus-dropzone .wrap, .photus-dropzone .wrap * { color: var(--photus-text-secondary) !important; }
.photus-dropzone .wrap svg { color: var(--photus-accent) !important; stroke: var(--photus-accent) !important; }
.photus-dropzone.field-error, .photus-dropzone.field-error .wrap { border-color: var(--photus-error) !important; }

/* Gradio's own floating-label chip (lilac bg / violet text, tema Soft claro)
   vaza em componentes sem elem_classes=photus-input (gr.File, gr.HighlightedText)
   — reskinamos direto no <label>, que aqui carrega o texto sem <span> filho. */
.photus-dropzone label, .photus-highlight label {
    background: var(--photus-surface-input) !important;
    color: var(--photus-accent) !important;
    border: none !important;
    box-shadow: none !important;
}

/* ---------- Contador / badge de limite ---------- */
.photus-counter-badge {
    display: inline-block; border: 1px solid var(--photus-accent); color: var(--photus-accent) !important;
    font-size: 12px; font-weight: 700; border-radius: 999px; padding: 4px 12px;
}
.photus-counter-badge.over-limit { border-color: var(--photus-error); color: var(--photus-error) !important; }
.photus-counter-row { display: flex; justify-content: space-between; align-items: center; margin: 4px 0; }
.photus-counter-row, .photus-counter-row * { color: var(--photus-text-secondary); }

/* ---------- Grid de miniaturas (preview) ---------- */
.photus-thumb-gallery.grid-wrap, .photus-thumb-gallery .grid-wrap { background: transparent !important; }
.photus-thumb-gallery { background: transparent !important; border: none !important; }
.photus-thumb-gallery img { border-radius: 8px !important; }
.photus-thumb-gallery .caption-label { color: var(--photus-text-secondary) !important; }

.photus-action-bar { display: flex; gap: 12px; justify-content: flex-end; margin-top: 8px; }

/* ---------- Modal de Processamento / Roteamento (UC05) ---------- */
.photus-modal-overlay {
    position: fixed !important;
    inset: 0 !important;
    background: rgba(0, 0, 0, 0.6) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    z-index: 1000 !important;
}
.photus-modal-card {
    background: var(--photus-surface) !important;
    border: 1px solid var(--photus-border) !important;
    border-radius: 12px !important;
    padding: 28px 32px !important;
    max-width: 440px !important;
    width: 90vw;
}
.photus-modal-title { color: var(--photus-text-primary); font-size: 19px; font-weight: 700; margin: 0 0 4px; }
.photus-modal-subtitle { color: var(--photus-text-secondary); font-size: 13px; margin: 0 0 20px; }
.photus-modal-steps { display: flex; flex-direction: column; gap: 14px; margin-bottom: 4px; }
.photus-modal-step { display: flex; align-items: center; gap: 12px; font-size: 14px; font-weight: 600; color: var(--photus-text-secondary); }
.photus-modal-step .icon {
    width: 22px; height: 22px; border-radius: 50%; flex-shrink: 0; box-sizing: border-box;
    display: flex; align-items: center; justify-content: center; font-size: 12px;
    border: 2px solid var(--photus-border); color: var(--photus-text-secondary);
}
.photus-modal-step.done { color: var(--photus-text-primary); }
.photus-modal-step.done .icon { background: var(--photus-success); border-color: var(--photus-success); color: #fff; }
.photus-modal-step.active { color: var(--photus-text-primary); }
.photus-modal-step.active .icon { border-color: var(--photus-accent); border-top-color: transparent; animation: photus-spin 0.8s linear infinite; }
.photus-modal-step.failed .icon { background: var(--photus-error); border-color: var(--photus-error); color: #fff; }
.photus-modal-step.failed { color: var(--photus-error); }
@keyframes photus-spin { to { transform: rotate(360deg); } }

.photus-modal-divider { border-top: 1px solid var(--photus-border); margin: 16px 0 14px; }
.photus-modal-route-label { color: var(--photus-text-secondary); font-size: 12px; font-weight: 600; margin: 0 0 8px; }
.photus-modal-badges { display: flex; gap: 8px; flex-wrap: wrap; }

.photus-badge-pill { display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 4px 12px; font-size: 12px; font-weight: 700; border: 1px solid; }
.photus-badge-anchor { border-color: var(--photus-accent); color: var(--photus-accent); background: rgba(99, 102, 241, 0.08); }
.photus-badge-route-fast { border-color: var(--photus-success); color: var(--photus-success); background: rgba(16, 185, 129, 0.08); }
.photus-badge-route-llm { border-color: var(--photus-llm); color: var(--photus-llm); background: rgba(167, 139, 250, 0.08); }
.photus-badge-route-tecnico { border-color: var(--photus-warning); color: var(--photus-warning); background: rgba(245, 158, 11, 0.08); }

.photus-exception-card { background: rgba(239, 68, 68, 0.08); border: 1px solid var(--photus-error); border-radius: 10px; padding: 14px 16px; margin-top: 14px; }
.photus-exception-card.fallback { background: rgba(156, 163, 175, 0.08); border-color: var(--photus-border); }
.photus-exception-status {
    display: inline-block; border: 1px solid var(--photus-error); color: var(--photus-error);
    font-size: 11px; font-weight: 700; border-radius: 999px; padding: 1px 8px; margin-bottom: 6px;
}
.photus-exception-card.fallback .photus-exception-status { border-color: var(--photus-text-secondary); color: var(--photus-text-secondary); }
.photus-exception-title { color: var(--photus-text-primary); font-size: 14px; font-weight: 700; margin: 2px 0 4px; }
.photus-exception-body { color: var(--photus-text-secondary); font-size: 13px; margin: 0 0 6px; }
.photus-exception-note { color: var(--photus-error); font-size: 12px; font-weight: 600; margin: 0; }
.photus-exception-card.fallback .photus-exception-note { color: var(--photus-text-secondary); font-weight: 500; }
"""


def avatar_initials(name: str | None) -> str:
    if not name or not name.strip():
        return "?"
    parts = name.strip().split()
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


USER_TYPE_LABEL = {
    "leigo": "Leigo",
    "fotografo": "Fotógrafo",
}

# Rota de classificacao (rota_classificacao) devolvida pelo Photus B, mapeada para
# o badge visual do protótipo Figma (sprint-2, tela "Modal de Processamento").
ROUTE_BADGE = {
    "fast_track": ("photus-badge-route-fast", "⚡ Fast Track (SBERT)"),
    "fallback": ("photus-badge-route-llm", "🧠 Refinamento LLM (Mistral)"),
    "tecnico": ("photus-badge-route-tecnico", "📷 Interpretação Literal Técnica"),
}


def route_badge_html(route_type: str) -> str:
    css_class, label = ROUTE_BADGE.get(route_type, ("photus-badge-route-fast", route_type))
    return f'<span class="photus-badge-pill {css_class}">{label}</span>'


def anchor_badge_html(category: str) -> str:
    import html as _html

    return f'<span class="photus-badge-pill photus-badge-anchor">[ {_html.escape(category)} ]</span>'


def input_update(*, error: bool = False):
    classes = ["photus-input", "field-error"] if error else ["photus-input"]
    return gr.update(elem_classes=classes)


def dropzone_update(*, error: bool = False):
    classes = ["photus-dropzone", "field-error"] if error else ["photus-dropzone"]
    return gr.update(elem_classes=classes)
