from __future__ import annotations

import html as _html

from photus.ui.theme import status_badge_html

# UC06 — rótulos amigáveis para as chaves conhecidas do metrics_json real do
# Photus A (confirmado via E2E: o payload tem bem mais campos do que a spec
# da Sprint 3 documentava — artifacts/contrast/dynamic_range/entropy/gradient/
# ratio/saturation_mean/saturation_variance também aparecem). Chaves sem
# entrada aqui caem no fallback `key.replace("_", " ").title()`.
_METRIC_LABELS = {
    "sharpness": "Nitidez (Sharpness / Laplacian Var)",
    "edge_density": "Densidade de Bordas (Edge Density)",
    "exposure_ratio": "Razão de Exposição (Exposure Ratio)",
}
# Barra de intensidade só para métricas com escala 0-1 CONFIRMADA
# (exposure_ratio: "imagem branca=1.0, preta=0.0", docs/testes_sprint3.md).
# sharpness/edge_density e as demais chaves têm faixas não normalizadas (ex.:
# sharpness observado > 46000 num teste real) — um teto inventado rende uma
# barra sempre cheia e engana mais do que ajuda, então essas só mostram o
# valor numérico, sem barra.
_METRIC_BAR_MAX = {
    "exposure_ratio": 1.0,
}
_HARD_RULE_HINTS = ("hard-rule", "hard_rule", "baixa informação", "exposição muito alta")

_GAUGE_COLOR = {
    "aprovado": "var(--photus-success)",
    "indefinido": "var(--photus-warning)",
    "reprovado": "var(--photus-error)",
    "revisao_humana": "var(--photus-llm)",
    "erro": "var(--photus-text-secondary)",
}

_THUMB_STATUS_CLASS = {
    "pendente": ("pending", "⏳"),
    "aprovado": ("approved", "✓"),
    "indefinido": ("undefined", "?"),
    "reprovado": ("rejected", "✕"),
    "revisao_humana": ("human", "👁"),
    "erro": ("engine-error", "⚠"),
}


def _metric_bar_html(key: str, value: object) -> str:
    try:
        numeric = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return ""
    label = _METRIC_LABELS.get(key, key.replace("_", " ").title())
    cap = _METRIC_BAR_MAX.get(key)
    if cap is None:
        return (
            '<div class="photus-diag-metric-row">'
            f'<div class="head"><span>{_html.escape(label)}</span><b>{numeric:.2f}</b></div>'
            "</div>"
        )
    pct = max(0.0, min(1.0, numeric / cap)) * 100
    return (
        '<div class="photus-diag-metric-row">'
        f'<div class="head"><span>{_html.escape(label)}</span><b>{numeric:.2f}</b></div>'
        '<div class="photus-diag-metric-track">'
        f'<div class="photus-diag-metric-fill" style="width:{pct:.0f}%"></div>'
        "</div></div>"
    )


def gauge_html(score: float | None, status: str) -> str:
    color = _GAUGE_COLOR.get(status, "var(--photus-accent)")
    if score is None:
        return (
            '<div class="photus-diag-gauge-col">'
            '<div class="photus-diag-gauge" style="background: var(--photus-border);">'
            '<span class="photus-diag-gauge-value">—</span></div>'
            '<span class="photus-diag-gauge-label">score_final</span></div>'
        )
    pct = max(0.0, min(1.0, score)) * 100
    return (
        '<div class="photus-diag-gauge-col">'
        f'<div class="photus-diag-gauge" style="background: conic-gradient({color} {pct:.0f}%, var(--photus-border) {pct:.0f}%);">'
        f'<span class="photus-diag-gauge-value">{score:.2f}</span></div>'
        '<span class="photus-diag-gauge-label">score_final</span></div>'
    )


def diagnostic_card_html(photo: dict) -> str:
    status = photo.get("evaluation_status", "pendente")
    metrics_json = photo.get("metrics_json") or {}
    metrics = metrics_json.get("metrics") or {}
    face = metrics_json.get("face_metrics")
    details = metrics_json.get("details")
    thresholds_file = metrics_json.get("thresholds_file")

    bars = "".join(_metric_bar_html(k, v) for k, v in metrics.items())
    if face and face.get("confidence") is not None:
        try:
            confidence = float(face["confidence"])
            bars += (
                '<div class="photus-diag-metric-row">'
                '<div class="head"><span>Detecção Facial (YuNet)</span>'
                f"<b>confiança {confidence:.2f}</b></div></div>"
            )
        except (TypeError, ValueError):
            pass

    details_html = ""
    if details:
        is_hard_rule = status == "reprovado" and any(hint in details.lower() for hint in _HARD_RULE_HINTS)
        css = "photus-diag-details hard-rule" if is_hard_rule else "photus-diag-details"
        details_html = f'<p class="{css}">{_html.escape(str(details))}</p>'

    thresholds_html = (
        f'<p class="photus-diag-details">Thresholds: {_html.escape(str(thresholds_file))}</p>'
        if thresholds_file
        else ""
    )

    return (
        '<div class="photus-diag-card">'
        '<div class="photus-diag-main">'
        f'<p class="photus-diag-filename">{_html.escape(photo.get("file_name", ""))}</p>'
        f"{status_badge_html(status)}"
        f'<div class="photus-diag-metrics">{bars}</div>'
        f"{details_html}{thresholds_html}"
        "</div>"
        f'{gauge_html(photo.get("final_score"), status)}'
        "</div>"
    )


def diagnostics_html(detail: dict) -> str:
    photos = [p for p in detail.get("photos", []) if p.get("evaluation_status") != "pendente"]
    if not photos:
        return ""
    cards = "".join(diagnostic_card_html(p) for p in photos)
    return f'<div class="photus-diag-grid">{cards}</div>'


def _thumb_status_html(photo: dict) -> str:
    status = photo.get("evaluation_status", "pendente")
    css, icon = _THUMB_STATUS_CLASS.get(status, ("pending", "⏳"))
    name = _html.escape(photo.get("file_name", ""))
    return (
        '<div class="photus-thumb-status-card">'
        f'<div class="photus-thumb-status-dot {css}">{icon}</div>'
        f'<span class="photus-thumb-status-name" title="{name}">{name}</span></div>'
    )


def lote_monitor_html(detail: dict) -> str:
    status = detail.get("status", "em_processamento")
    total = detail.get("total_photos", 0)
    done = detail.get("evaluated_photos", 0)
    anchor = detail.get("classified_anchor") or "—"
    thresholds_file = detail.get("thresholds_file")

    if status == "em_processamento":
        progress_label = "Avaliando lote — Pré-processador + Photus A em execução..."
        fill_class = "processing"
    elif status == "concluido":
        progress_label = f"Avaliação concluída — {done} de {total} fotos avaliadas."
        fill_class = "done"
    else:
        progress_label = f"Falha na avaliação técnica — {done} de {total} fotos avaliadas antes do erro."
        fill_class = "failed"

    anchor_badge = (
        f'<span class="photus-badge-pill photus-badge-anchor">{_html.escape(str(thresholds_file))}</span>'
        if thresholds_file
        else ""
    )

    thumbs = "".join(_thumb_status_html(p) for p in detail.get("photos", []))
    batch_id = str(detail.get("id") or "—")

    return (
        '<div class="photus-lote-header">'
        '<div><p class="photus-lote-id-label">LOTE EM ANDAMENTO</p>'
        f'<p class="photus-lote-id-value">Lote #{_html.escape(batch_id[:8])}</p></div>'
        '<div style="text-align:right;"><p class="photus-lote-id-label">ÂNCORA ATIVA</p>'
        f'<p class="photus-lote-id-value" style="font-size:14px;">{_html.escape(str(anchor))}</p>{anchor_badge}</div>'
        "</div>"
        '<div class="photus-progress-row"><span class="label">'
        f"{_html.escape(progress_label)}</span></div>"
        '<div class="photus-progress-track">'
        f'<div class="photus-progress-fill {fill_class}" style="width:100%"></div></div>'
        f'<div class="photus-thumb-status-grid">{thumbs}</div>'
    )
