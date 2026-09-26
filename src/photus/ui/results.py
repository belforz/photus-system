"""Painel de resultados do Photus A: ranking das fotos com o score enviado.

Regra de negocio (pedido do usuario): "Top 3" so faz sentido quando ha MAIS de
3 fotos avaliadas -- selecionar as 3 melhores dentre 3 (ou menos) e um recorte
trivial (seria = todas). Por isso `ui_results` recebe `total_scored` e ajusta
titulo/subtitulo/rotulo conforme o caso, e quem monta a lista de itens em
`app.py` so deve truncar para 3 quando `total_scored > 3`.
"""

from __future__ import annotations

import html

_CSS = """
<style>
.photus-results-panel {
    display: flex;
    flex-direction: column;
    gap: 4px;
    width: 100%;
    box-sizing: border-box;
    background: var(--block-background-fill, #f9fafb);
    border: 1px solid var(--border-color-primary, #e5e7eb);
    border-radius: 12px;
    padding: 14px 14px 6px;
    font-family: inherit;
}
.photus-results-header { margin-bottom: 6px; }
.photus-results-header strong {
    font-size: 13px;
    color: var(--body-text-color, #111827);
}
.photus-results-header p {
    margin: 2px 0 0;
    font-size: 11.5px;
    color: var(--body-text-color-subdued, #6b7280);
    line-height: 1.4;
}
.photus-results-empty {
    padding: 16px 14px;
    border-radius: 12px;
    border: 1px dashed var(--border-color-primary, #e5e7eb);
    color: var(--body-text-color-subdued, #9ca3af);
    font-size: 12px;
    text-align: center;
}
.photus-result-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 8px;
    border-radius: 10px;
    transition: background-color 0.2s ease, transform 0.15s ease;
}
.photus-result-row:hover {
    background: rgba(124, 58, 237, 0.07);
    transform: translateX(2px);
}
.photus-result-rank {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(124, 58, 237, 0.12);
    color: #7c3aed;
    font-size: 11px;
    font-weight: 700;
}
.photus-result-info { flex: 1; min-width: 0; }
.photus-result-name {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 600;
    color: var(--body-text-color, #111827);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.photus-score-track {
    height: 6px;
    border-radius: 999px;
    background: var(--border-color-primary, #e5e7eb);
    overflow: hidden;
    margin-top: 5px;
}
.photus-score-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #7c3aed, #a78bfa);
    transition: width 0.5s ease;
}
.photus-result-meta {
    margin-top: 3px;
    font-size: 10.5px;
    color: var(--body-text-color-subdued, #9ca3af);
}
.photus-status-badge {
    flex-shrink: 0;
    font-size: 9.5px;
    padding: 1px 7px;
    border-radius: 999px;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}
.photus-status-badge.aprovado { background: #dcfce7; color: #15803d; }
.photus-status-badge.reprovado { background: #fee2e2; color: #b91c1c; }
.photus-status-badge.revisao_humana { background: #dbeafe; color: #1d4ed8; }
.photus-status-badge.indefinido { background: #fef9c3; color: #92610a; }
</style>
"""

# Status reais devolvidos pelo Photus A (Photus_A.cpp): Aprovado, Reprovado,
# Revisao_Humana -- "Indefinido" e o fallback local para quando o campo vem
# vazio/ausente, nao um valor que o binario emite.
_STATUS_MAP = {
    "aprovado": ("Aprovado", "aprovado"),
    "reprovado": ("Reprovado", "reprovado"),
    "revisao_humana": ("Revisão Humana", "revisao_humana"),
}


def _status_badge(status: str | None) -> str:
    key = (status or "").strip().lower()
    label, css_class = _STATUS_MAP.get(key, (status or "Indefinido", "indefinido"))
    return f'<span class="photus-status-badge {css_class}">{html.escape(label)}</span>'


def score_percent(score: float) -> int:
    """Normaliza o final_score do Photus A (0-1) para uma porcentagem 0-100."""
    pct = score * 100 if score <= 1 else score
    return max(0, min(100, round(pct)))


def ui_results(items: list[dict], *, category: str | None = None, total_scored: int = 0) -> str:
    """Monta o painel HTML com o ranking de fotos e o score enviado pelo Photus A.

    `items`: lista de dicts com `rank`, `filename`, `score` (0-1) e `status`
    (Aprovado/Reprovado/Indefinido) -- ja filtrados/truncados por quem chama.
    `total_scored`: quantas fotos o Photus A pontuou ao todo nesta sessao.

    Quando `total_scored <= 3`, o titulo/subtitulo deixam de falar em "Top 3"
    (ver docstring do modulo) e passam a descrever um ranking completo.
    """
    if not items:
        return _CSS + '<div class="photus-results-empty">Nenhuma foto pontuada para exibir ainda.</div>'

    is_top_n = total_scored > 3
    anchor_txt = f" para a âncora <strong>{html.escape(category)}</strong>" if category else ""

    if is_top_n:
        title = f"Top {len(items)} de {total_scored} fotos avaliadas"
        subtitle = f"Melhores fotos{anchor_txt}, ordenadas pelo score do Photus A."
    else:
        title = f"Ranking — {total_scored} foto(s) avaliada(s)"
        subtitle = (
            f"Com {total_scored} foto(s) enviada(s), o recorte Top 3 não se aplica "
            f"(seria igual ao total) — mostrando o ranking completo{anchor_txt}."
        )

    rows = []
    for item in items:
        pct = score_percent(item["score"])
        filename = html.escape(item["filename"])
        status_html = _status_badge(item.get("status"))
        rows.append(
            '<div class="photus-result-row">'
            f'<div class="photus-result-rank">{item["rank"]}</div>'
            '<div class="photus-result-info">'
            f'<div class="photus-result-name"><span>{filename}</span>{status_html}</div>'
            f'<div class="photus-score-track"><div class="photus-score-fill" style="width:{pct}%"></div></div>'
            f'<div class="photus-result-meta">Score Photus A: {pct}%</div>'
            "</div>"
            "</div>"
        )

    return (
        _CSS
        + '<div class="photus-results-panel">'
        + f'<div class="photus-results-header"><strong>{title}</strong><p>{subtitle}</p></div>'
        + "".join(rows)
        + "</div>"
    )
