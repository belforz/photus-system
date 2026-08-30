# Paleta e componentes visuais extraídos do protótipo Figma (sprint-1,
# nCVHiSAC6J7OECKp8ID1dR) — telas 01-Cadastro / 02-Login / 03-Perfil.


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
.photus-help-text, .photus-help-text * { color: var(--photus-text-secondary) !important; font-size: 12px !important; margin: -10px 0 4px; }
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
