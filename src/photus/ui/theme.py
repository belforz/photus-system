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

.photus-card {
    background: var(--photus-surface) !important;
    border-radius: 12px;
    padding: 32px 40px !important;
    max-width: 560px;
    margin: 40px auto;
}
.photus-eyebrow, .photus-eyebrow * { color: var(--photus-accent) !important; font-weight: 700; font-size: 12px; letter-spacing: .05em; margin: 0; }
.photus-title, .photus-title * { color: var(--photus-text-primary) !important; font-size: 26px; font-weight: 700; margin: 4px 0 2px; }
.photus-subtitle, .photus-subtitle * { color: var(--photus-text-secondary) !important; font-size: 14px; margin: 0 0 8px; font-weight: 400; }
.photus-footer-text, .photus-footer-text * { color: var(--photus-text-secondary) !important; font-size: 13px; }

.photus-card .block,
.photus-card .form,
.photus-topbar .block,
.photus-topbar .form {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.photus-card label > span,
.photus-card fieldset > span,
.photus-topbar label > span,
.photus-topbar fieldset > span {
    background: transparent !important;
    padding: 0 !important;
    color: var(--photus-text-secondary) !important;
}

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
.photus-help-text { margin: 2px 0 8px; }
.photus-help-text, .photus-help-text * { color: var(--photus-text-secondary) !important; font-size: 12px !important; }
.photus-help-text.error-text, .photus-help-text.error-text * { color: var(--photus-error) !important; font-weight: 600; }

.photus-btn-primary { background: var(--photus-accent) !important; color: #fff !important; border: none !important; }
.photus-btn-primary:hover { background: var(--photus-accent-hover) !important; }
.photus-btn-secondary { background: var(--photus-surface-input) !important; border: 1px solid var(--photus-border) !important; color: var(--photus-text-primary) !important; }
.photus-btn-danger { background: var(--photus-error) !important; color: #fff !important; border: none !important; }
.photus-btn-ghost { background: transparent !important; border: none !important; color: var(--photus-accent) !important; font-weight: 600 !important; box-shadow: none !important; }
.photus-btn-primary, .photus-btn-secondary, .photus-btn-danger {
    border-radius: 8px !important; font-weight: 600 !important; font-size: 15px !important;
}

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

.photus-card.photus-card-wide { max-width: 720px; }

.photus-hint-block { margin: 8px 0 4px; display: flex; flex-direction: column; gap: 6px; }
.photus-hint-block p { color: var(--photus-text-secondary) !important; font-size: 12.5px !important; margin: 0 !important; display: flex; align-items: center; gap: 8px; }
.photus-hint-block .photus-badge-pill { flex-shrink: 0; font-size: 10.5px; padding: 2px 9px; }

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

.photus-dropzone label, .photus-highlight label {
    background: var(--photus-surface-input) !important;
    color: var(--photus-accent) !important;
    border: none !important;
    box-shadow: none !important;
}

.photus-counter-badge {
    display: inline-block; border: 1px solid var(--photus-accent); color: var(--photus-accent) !important;
    font-size: 12px; font-weight: 700; border-radius: 999px; padding: 4px 12px;
}
.photus-counter-badge.over-limit { border-color: var(--photus-error); color: var(--photus-error) !important; }
.photus-counter-row { display: flex; justify-content: space-between; align-items: center; margin: 4px 0; }
.photus-counter-row, .photus-counter-row * { color: var(--photus-text-secondary); }

.photus-thumb-gallery.grid-wrap, .photus-thumb-gallery .grid-wrap { background: transparent !important; }
.photus-thumb-gallery { background: transparent !important; border: none !important; }
.photus-thumb-gallery img { border-radius: 8px !important; }
.photus-thumb-gallery .caption-label { color: var(--photus-text-secondary) !important; }

.photus-action-bar { display: flex; gap: 12px; justify-content: flex-end; margin-top: 8px; }

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

/* ---- UC06: Monitor de Execução do Pipeline + Diagnóstico por Foto ---- */
.photus-badge-status-approved { border-color: var(--photus-success); color: var(--photus-success); background: rgba(16, 185, 129, 0.08); }
.photus-badge-status-undefined { border-color: var(--photus-warning); color: var(--photus-warning); background: rgba(245, 158, 11, 0.08); }
.photus-badge-status-rejected { border-color: var(--photus-error); color: var(--photus-error); background: rgba(239, 68, 68, 0.08); }
.photus-badge-status-human { border-color: var(--photus-llm); color: var(--photus-llm); background: rgba(167, 139, 250, 0.08); }
.photus-badge-status-error { border-color: var(--photus-text-secondary); color: var(--photus-text-secondary); background: rgba(156, 163, 175, 0.08); }
.photus-badge-status-pending { border-color: var(--photus-border); color: var(--photus-text-secondary); background: transparent; }

.photus-lote-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin: 4px 0 14px; flex-wrap: wrap; }
.photus-lote-id-label { color: var(--photus-text-secondary); font-size: 11px; font-weight: 700; letter-spacing: .04em; margin: 0; text-transform: uppercase; }
.photus-lote-id-value { color: var(--photus-text-primary); font-size: 18px; font-weight: 700; margin: 2px 0 6px; }

.photus-progress-row { margin-bottom: 6px; font-size: 13px; }
.photus-progress-row .label { color: var(--photus-text-primary); font-weight: 600; }
.photus-progress-track { width: 100%; height: 8px; border-radius: 999px; background: var(--photus-surface-input); border: 1px solid var(--photus-border); overflow: hidden; }
.photus-progress-fill { height: 100%; border-radius: 999px; background: var(--photus-accent); transition: width 0.4s ease; }
.photus-progress-fill.done { background: var(--photus-success); }
.photus-progress-fill.failed { background: var(--photus-error); }
.photus-progress-fill.processing {
    background: repeating-linear-gradient(45deg, var(--photus-accent), var(--photus-accent) 10px, rgba(99, 102, 241, 0.5) 10px, rgba(99, 102, 241, 0.5) 20px);
    background-size: 200% 100%;
    animation: photus-stripes 1s linear infinite;
}
@keyframes photus-stripes { from { background-position: 0 0; } to { background-position: 40px 0; } }

.photus-thumb-status-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
.photus-thumb-status-card { width: 84px; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.photus-thumb-status-dot {
    width: 30px; height: 30px; border-radius: 999px; display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; border: 2px solid var(--photus-border); color: var(--photus-text-secondary);
}
.photus-thumb-status-dot.approved { background: var(--photus-success); border-color: var(--photus-success); color: #fff; }
.photus-thumb-status-dot.rejected { background: var(--photus-error); border-color: var(--photus-error); color: #fff; }
.photus-thumb-status-dot.undefined { background: var(--photus-warning); border-color: var(--photus-warning); color: #fff; }
.photus-thumb-status-dot.human { background: var(--photus-llm); border-color: var(--photus-llm); color: #fff; }
.photus-thumb-status-dot.engine-error { background: var(--photus-text-secondary); border-color: var(--photus-text-secondary); color: var(--photus-bg); }
.photus-thumb-status-name { font-size: 10px; color: var(--photus-text-secondary); text-align: center; max-width: 84px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.photus-diag-grid { display: flex; flex-direction: column; gap: 14px; margin-top: 4px; }
.photus-diag-card { background: var(--photus-surface-input); border: 1px solid var(--photus-border); border-radius: 10px; padding: 16px 18px; display: flex; gap: 18px; flex-wrap: wrap; }
.photus-diag-main { flex: 1 1 240px; min-width: 220px; }
.photus-diag-filename { color: var(--photus-text-primary); font-weight: 700; font-size: 13px; margin: 0 0 8px; }
.photus-diag-gauge-col { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 0 0 110px; }
.photus-diag-gauge { width: 84px; height: 84px; border-radius: 50%; display: flex; align-items: center; justify-content: center; position: relative; }
.photus-diag-gauge::before { content: ""; position: absolute; inset: 8px; border-radius: 50%; background: var(--photus-surface-input); }
.photus-diag-gauge-value { position: relative; z-index: 1; font-size: 16px; font-weight: 700; color: var(--photus-text-primary); }
.photus-diag-gauge-label { font-size: 10px; color: var(--photus-text-secondary); text-align: center; }

.photus-diag-metrics { margin-top: 10px; display: flex; flex-direction: column; gap: 8px; }
.photus-diag-metric-row .head { display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 2px; }
.photus-diag-metric-row .head span { color: var(--photus-text-secondary); }
.photus-diag-metric-row .head b { color: var(--photus-text-primary); font-weight: 700; }
.photus-diag-metric-track { height: 5px; border-radius: 999px; background: var(--photus-border); overflow: hidden; }
.photus-diag-metric-fill { height: 100%; background: var(--photus-accent); border-radius: 999px; }
.photus-diag-details { margin-top: 8px; font-size: 12px; color: var(--photus-text-secondary); font-style: italic; }
.photus-diag-details.hard-rule { color: var(--photus-error); font-style: normal; font-weight: 600; }

/* ---- Sprint 4: navegação, Histórico (UC07), Resultado (UC08/UC09), Exclusão (UC10) ---- */
.photus-nav { gap: 8px !important; margin-bottom: 14px; }
.photus-nav-btn { background: var(--photus-surface) !important; border: 1px solid var(--photus-border) !important; color: var(--photus-text-primary) !important; border-radius: 8px !important; font-weight: 600 !important; max-width: 180px; }
.photus-nav-btn:hover { border-color: var(--photus-accent) !important; }

.photus-page { max-width: 1040px; margin: 0 auto; width: 100%; gap: 14px !important; }
.photus-page .block, .photus-page .form { background: transparent !important; border: none !important; box-shadow: none !important; }
.photus-page-head { margin: 0 0 4px; }
.photus-page-title { color: var(--photus-text-primary); font-size: 26px; font-weight: 700; margin: 0; }
.photus-page-sub { color: var(--photus-text-secondary); font-size: 13px; margin: 2px 0 0; }
.photus-muted { color: var(--photus-text-secondary); font-size: 12px; }

.photus-history-toolbar { align-items: center !important; gap: 12px !important; }
.photus-search input { padding: 10px 14px !important; }
.photus-banner-success, .photus-banner-success * { color: var(--photus-success) !important; }

.photus-history-row {
    background: var(--photus-surface) !important; border: 1px solid var(--photus-border) !important;
    border-radius: 10px !important; padding: 10px 14px !important; align-items: center !important; gap: 10px !important;
    flex-wrap: nowrap !important;
}
.photus-history-row .block, .photus-history-row .form { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }
.photus-history-html { flex: 1 1 auto !important; min-width: 0 !important; }
.photus-history-main { display: grid; grid-template-columns: 130px minmax(0, 1fr) 130px 70px 150px; gap: 14px; align-items: center; }
.photus-history-date { color: var(--photus-text-secondary); font-size: 12.5px; }
.photus-history-text { color: var(--photus-text-primary); font-size: 14px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.photus-history-qty { color: var(--photus-text-primary); font-size: 13px; }
.photus-history-anchor, .photus-history-status { display: flex; }
.photus-row-btn { flex: 0 0 auto !important; min-width: 150px !important; }
.photus-btn-icon-danger { flex: 0 0 44px !important; min-width: 44px !important; background: rgba(239, 68, 68, 0.12) !important; border: 1px solid var(--photus-error) !important; color: var(--photus-error) !important; border-radius: 8px !important; }
.photus-btn-icon-danger:hover { background: rgba(239, 68, 68, 0.25) !important; }
.photus-badge-status-processing { border-color: var(--photus-accent); color: var(--photus-accent); background: rgba(99, 102, 241, 0.1); }

.photus-empty-state { text-align: center; background: var(--photus-surface); border: 1px dashed var(--photus-border); border-radius: 12px; padding: 40px 20px; }
.photus-empty-icon { font-size: 40px; margin-bottom: 8px; }
.photus-empty-title { color: var(--photus-text-primary); font-size: 18px; font-weight: 700; margin: 0 0 4px; }
.photus-empty-body { color: var(--photus-text-secondary); font-size: 13px; margin: 0; }
.photus-empty-state.denied { border-color: var(--photus-error); background: rgba(239, 68, 68, 0.06); }

.photus-delete-modal { height: fit-content !important; flex: 0 0 auto !important; align-self: center !important; }
.photus-delete-icon { width: 48px; height: 48px; border-radius: 50%; margin: 0 auto 12px; background: rgba(239, 68, 68, 0.15); color: var(--photus-error); border: 2px solid var(--photus-error); display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 800; }
.photus-delete-quote { color: var(--photus-text-primary); font-size: 13px; font-style: italic; text-align: center; margin: 0 0 10px; }

.photus-back-btn { align-self: flex-start; max-width: 220px; }
.photus-result-head { display: flex; justify-content: space-between; gap: 18px; flex-wrap: wrap; background: var(--photus-surface); border: 1px solid var(--photus-border); border-radius: 12px; padding: 18px 22px; }
.photus-result-head-main { flex: 1 1 380px; min-width: 0; }
.photus-result-head-side { text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.photus-result-phrase { color: var(--photus-text-primary); font-size: 20px; font-weight: 700; margin: 4px 0 10px; }
.photus-result-lote { color: var(--photus-text-primary); font-size: 16px; font-weight: 700; margin: 0; }
.photus-result-chips { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.photus-dot { color: var(--photus-text-secondary); }

.photus-notice { border-radius: 10px; padding: 12px 16px; font-size: 13px; font-weight: 600; border: 1px solid; }
.photus-notice.processing { color: var(--photus-accent); border-color: var(--photus-accent); background: rgba(99, 102, 241, 0.08); }
.photus-notice.failed { color: var(--photus-error); border-color: var(--photus-error); background: rgba(239, 68, 68, 0.08); }

.photus-section-head { margin: 10px 0 2px; }
.photus-section-title { color: var(--photus-text-primary); font-size: 18px; font-weight: 700; margin: 0; }
.photus-star { color: #f5c542; }

.photus-top3-grid, .photus-photo-grid { gap: 14px !important; flex-wrap: wrap !important; align-items: stretch !important; }
.photus-top3-grid > .photus-photo-card { flex: 1 1 280px !important; }
.photus-photo-grid > .photus-photo-card { flex: 0 1 calc(25% - 14px) !important; min-width: 200px !important; }
.photus-photo-card { background: var(--photus-surface) !important; border: 1px solid var(--photus-border) !important; border-radius: 12px !important; overflow: hidden; padding: 0 !important; gap: 0 !important; }
.photus-photo-card .block, .photus-photo-card .form { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }
.photus-photo-card > button { margin: 0 12px 12px !important; width: calc(100% - 24px) !important; }
.photus-photo-card.top3.rank-1 { border-color: #f5c542 !important; }
.photus-photo-card.top3.rank-2 { border-color: #cbd5e1 !important; }
.photus-photo-card.top3.rank-3 { border-color: #cd8a52 !important; }

.photus-photo-media { position: relative; aspect-ratio: 4 / 3; background: var(--photus-surface-input); }
.photus-photo-media.big { aspect-ratio: 3 / 2; }
.photus-photo-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.photus-photo-img.placeholder { display: flex; align-items: center; justify-content: center; font-size: 34px; color: var(--photus-text-secondary); }
.photus-photo-body { padding: 10px 12px 8px; }
.photus-photo-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.photus-photo-name { color: var(--photus-text-primary); font-size: 12.5px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.photus-photo-score { display: flex; justify-content: space-between; margin: 8px 0 4px; }
.photus-photo-score span { color: var(--photus-text-secondary); font-size: 11.5px; }
.photus-photo-score b { color: var(--photus-text-primary); font-size: 11.5px; }
.photus-photo-bar { height: 5px; border-radius: 999px; background: var(--photus-border); overflow: hidden; margin-bottom: 6px; }
.photus-photo-bar > div { height: 100%; border-radius: 999px; }
.photus-photo-bar.big { height: 6px; margin-top: 6px; }

.photus-top3-chip, .photus-rank-chip { position: absolute; top: 8px; left: 8px; z-index: 2; font-size: 11px; font-weight: 700; border-radius: 999px; padding: 3px 10px; background: #f5c542; color: #1a1d24; }
.photus-rank-chip.rank-2 { background: #cbd5e1; }
.photus-rank-chip.rank-3 { background: #cd8a52; color: #fff; }
.photus-top3-score { font-size: 26px; font-weight: 800; margin: 10px 0 0; color: var(--photus-text-primary); }
.photus-top3-score span { font-size: 12px; font-weight: 600; color: var(--photus-text-secondary); }
.photus-top3-score.rank-1 { color: #f5c542; }
.photus-top3-score.rank-2 { color: #cbd5e1; }
.photus-top3-score.rank-3 { color: #cd8a52; }
.photus-photo-bar.big.rank-1 > div { background: #f5c542; }
.photus-photo-bar.big.rank-2 > div { background: #cbd5e1; }
.photus-photo-bar.big.rank-3 > div { background: #cd8a52; }

.photus-filter-chips .wrap { display: flex; flex-wrap: wrap; gap: 8px; }
.photus-filter-chips label { border: 1px solid var(--photus-border) !important; background: var(--photus-surface) !important; color: var(--photus-text-primary) !important; border-radius: 999px !important; padding: 5px 14px !important; font-size: 12.5px !important; }
.photus-filter-chips label:has(input:checked) { background: var(--photus-accent) !important; border-color: var(--photus-accent) !important; color: #fff !important; }
.photus-filter-chips label span { color: inherit !important; }
.photus-filter-chips input[type="radio"] { display: none !important; }

.photus-drawer-overlay { position: fixed !important; inset: 0 !important; background: rgba(0, 0, 0, 0.55) !important; z-index: 1100 !important; display: flex !important; flex-direction: row !important; justify-content: flex-end !important; }
.photus-drawer { background: var(--photus-surface) !important; border-left: 1px solid var(--photus-border) !important; width: min(460px, 96vw); height: 100vh; overflow-y: auto; padding: 22px 22px 28px !important; gap: 12px !important; }
.photus-drawer .block, .photus-drawer .form { background: transparent !important; border: none !important; box-shadow: none !important; }
.photus-drawer-img { width: 100%; border-radius: 10px; margin: 6px 0 12px; display: block; }
.photus-drawer-raw { margin-top: 12px; }
.photus-drawer-raw summary { color: var(--photus-accent); font-size: 12px; font-weight: 600; cursor: pointer; }
.photus-drawer-raw pre { background: var(--photus-surface-input); color: var(--photus-text-secondary); border: 1px solid var(--photus-border); border-radius: 8px; padding: 10px; font-size: 11px; overflow-x: auto; max-height: 320px; }

@media (max-width: 820px) {
    .photus-history-main { grid-template-columns: 1fr 1fr; }
    .photus-history-row { flex-wrap: wrap !important; }
    .photus-photo-grid > .photus-photo-card { flex: 1 1 calc(50% - 14px) !important; }
}
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


STATUS_BADGE = {
    "pendente": ("photus-badge-status-pending", "⏳ Na fila"),
    "aprovado": ("photus-badge-status-approved", "✓ Aprovado"),
    "indefinido": ("photus-badge-status-undefined", "? Indefinido"),
    "reprovado": ("photus-badge-status-rejected", "✕ Reprovado"),
    "revisao_humana": ("photus-badge-status-human", "👁 Revisão Humana"),
    "erro": ("photus-badge-status-error", "⚠ Erro"),
}


def status_badge_html(status: str) -> str:
    import html as _html

    css_class, label = STATUS_BADGE.get(status, ("photus-badge-status-pending", status))
    return f'<span class="photus-badge-pill {css_class}">{_html.escape(label)}</span>'


def input_update(*, error: bool = False):
    classes = ["photus-input", "field-error"] if error else ["photus-input"]
    return gr.update(elem_classes=classes)


def dropzone_update(*, error: bool = False):
    classes = ["photus-dropzone", "field-error"] if error else ["photus-dropzone"]
    return gr.update(elem_classes=classes)
