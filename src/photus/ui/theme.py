"""CSS global aplicado ao gr.Blocks -- ajustes de fluidez visual (transicoes
suaves, cantos arredondados, hover states) sobre os elementos marcados com
`elem_classes` nos componentes (ver ui/index.py). Escopado a essas classes
proprias em vez de seletores internos do Gradio, que mudam entre versoes.
"""

from __future__ import annotations

import html

GLOBAL_CSS = """
.photus-input textarea, .photus-input input {
    border-radius: 10px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.photus-input textarea:focus, .photus-input input:focus {
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}

.photus-dropzone {
    border-radius: 12px !important;
    transition: border-color 0.2s ease, background-color 0.2s ease;
}
.photus-dropzone:hover {
    border-color: #7c3aed !important;
}

.photus-btn {
    border-radius: 10px !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.photus-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.22);
}
.photus-btn:active {
    transform: translateY(0);
}

.photus-gallery {
    border-radius: 12px !important;
    overflow: hidden;
}
.photus-gallery .thumbnail-item, .photus-gallery img {
    transition: transform 0.2s ease;
}
.photus-gallery .thumbnail-item:hover img {
    transform: scale(1.04);
}

.photus-route-panel {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin: 2px 0 10px;
}
.photus-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 700;
    border: 1px solid;
}
.photus-badge-anchor { border-color: #7c3aed; color: #7c3aed; background: rgba(124, 58, 237, 0.08); }
.photus-badge-route-fast { border-color: #10b981; color: #10b981; background: rgba(16, 185, 129, 0.08); }
.photus-badge-route-llm { border-color: #3b82f6; color: #3b82f6; background: rgba(59, 130, 246, 0.08); }
.photus-badge-route-tecnico { border-color: #f59e0b; color: #f59e0b; background: rgba(245, 158, 11, 0.08); }
.photus-route-badges { display: flex; gap: 8px; flex-wrap: wrap; }
.photus-fallback-note {
    background: rgba(59, 130, 246, 0.07);
    border: 1px solid #3b82f6;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 11.5px;
    color: var(--body-text-color-subdued, #475569);
}
.photus-fallback-note strong { color: #3b82f6; }
"""


ROUTE_BADGE = {
    "fast_track": ("photus-badge-route-fast", "⚡ Fast Track (SBERT)"),
    "fallback": ("photus-badge-route-llm", "⚡ Fallback(LLM)"),
    "tecnico": ("photus-badge-route-tecnico", "⚡ Interpretação Literal Técnica"),
}


def route_badge_html(route_type: str) -> str:
    css_class, label = ROUTE_BADGE.get(route_type, ("photus-badge-route-fast", route_type))
    return f'<span class="photus-badge-pill {css_class}">{label}</span>'


def anchor_badge_html(category: str) -> str:
    return f'<span class="photus-badge-pill photus-badge-anchor">[ {html.escape(category)} ]</span>'


def route_preview_html(
    category: str,
    route_type: str,
    *,
    sbert_anchor_before_fallback: str | None = None,
    sbert_top1_score: float | None = None,
) -> str:
    badges = anchor_badge_html(category) + route_badge_html(route_type)
    body = f'<div class="photus-route-panel"><div class="photus-route-badges">{badges}</div>'

    if route_type == "fallback" and sbert_anchor_before_fallback:
        score_txt = f" (score {sbert_top1_score:.3f})" if sbert_top1_score is not None else ""
        body += (
            '<div class="photus-fallback-note">'
            f"<strong>SBERT sozinho</strong> apontou <strong>{html.escape(sbert_anchor_before_fallback)}</strong>"
            f"{score_txt} — o fallback Mistral LLM resgatou para <strong>{html.escape(category)}</strong>."
            "</div>"
        )

    body += "</div>"
    return body
