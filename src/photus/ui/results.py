"""UC07-UC10 — HTML builders do Histórico, Resultado da Avaliação, Top 3 e exclusão.

Funções puras (dict -> str) para ficarem testáveis sem subir o Gradio. Todo
elemento de texto tem regra de cor própria em `theme.py` (o CSS base do Gradio
sobrescreve cor herdada em tags nuas como span/p).
"""

from __future__ import annotations

import html as _html
from datetime import datetime, timezone

from photus.ui.theme import anchor_badge_html, route_badge_html, status_badge_html

BATCH_STATUS_BADGE = {
    "concluido": ("photus-badge-status-approved", "● Concluído"),
    "em_processamento": ("photus-badge-status-processing", "● Em Processamento"),
    "erro": ("photus-badge-status-rejected", "● Erro"),
}

FILTER_LABELS = [
    ("todas", "Todas"),
    ("aprovado", "Aprovadas"),
    ("indefinido", "Indefinidas"),
    ("reprovado", "Reprovadas"),
]

_SCORE_BAR_COLOR = {
    "aprovado": "var(--photus-success)",
    "indefinido": "var(--photus-warning)",
    "reprovado": "var(--photus-error)",
    "revisao_humana": "var(--photus-llm)",
}

_RANK_LABEL = {1: "1º Lugar", 2: "2º Lugar", 3: "3º Lugar"}


def _e(value: object) -> str:
    return _html.escape(str(value if value is not None else ""))


def format_datetime(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        value = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        # O backend grava em UTC; o SQLite devolve sem fuso (Postgres devolve com).
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        value = value.astimezone()
        return value.strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return str(iso)


def batch_status_badge_html(status: str) -> str:
    css, label = BATCH_STATUS_BADGE.get(status, ("photus-badge-status-pending", status))
    return f'<span class="photus-badge-pill {css}">{_e(label)}</span>'


def _truncate(text: str, limit: int = 90) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


# ------------------------------------------------------------------ UC07


def history_header_html(total: int, shown: int, query: str, *, title: bool = True) -> str:
    if total == 0:
        sub = "Somente lotes da sua conta"
    elif query:
        sub = f"Somente lotes da sua conta · {shown} de {_plural(total, 'avaliação', 'avaliações')}"
    else:
        sub = f"Somente lotes da sua conta · {_plural(total, 'avaliação', 'avaliações')}"
    title_html = '<p class="photus-page-title">Meu Histórico de Curadorias</p>' if title else ""
    return f'<div class="photus-page-head">{title_html}<p class="photus-page-sub">{_e(sub)}</p></div>'


def history_row_html(item: dict) -> str:
    anchor = item.get("classified_anchor")
    anchor_html = anchor_badge_html(anchor) if anchor else '<span class="photus-muted">—</span>'
    text = item.get("input_text", "")
    return (
        '<div class="photus-history-main">'
        f'<span class="photus-history-date">{_e(format_datetime(item.get("created_at")))}</span>'
        f'<span class="photus-history-text" title="{_e(text)}">{_e(_truncate(text))}</span>'
        f'<span class="photus-history-anchor">{anchor_html}</span>'
        f'<span class="photus-history-qty">{_e(_plural(item.get("total_photos", 0), "foto", "fotos"))}</span>'
        f'<span class="photus-history-status">{batch_status_badge_html(item.get("status", ""))}</span>'
        "</div>"
    )


def history_empty_html(*, filtered: bool = False) -> str:
    if filtered:
        title, body = "Nenhum lote encontrado", "Nenhuma solicitação combina com a sua busca."
    else:
        title = "Você ainda não realizou nenhuma avaliação"
        body = "Quando você submeter fotografias para curadoria, os lotes aparecem aqui."
    return (
        '<div class="photus-empty-state">'
        '<div class="photus-empty-icon">🗂️</div>'
        f'<p class="photus-empty-title">{_e(title)}</p>'
        f'<p class="photus-empty-body">{_e(body)}</p></div>'
    )


def filter_history(items: list[dict], query: str) -> list[dict]:
    query = (query or "").strip().lower()
    if not query:
        return items
    return [i for i in items if query in (i.get("input_text") or "").lower()]


# ------------------------------------------------------------------ UC10


def delete_modal_html(item: dict | None) -> str:
    n = (item or {}).get("total_photos", 0)
    text = (item or {}).get("input_text", "")
    removed = (
        f"o lote e todas as {n} fotografias avaliadas associadas a ele"
        if n != 1
        else "o lote e a fotografia avaliada associada a ele"
    )
    return (
        '<div class="photus-delete-icon">!</div>'
        '<p class="photus-modal-title" style="text-align:center;">Excluir Lote de Avaliação?</p>'
        f'<p class="photus-delete-quote">“{_e(_truncate(text, 80))}”</p>'
        f'<p class="photus-modal-subtitle" style="text-align:center;">'
        f"Esta ação é permanente e removerá {_e(removed)}.</p>"
    )


# ------------------------------------------------------------------ UC08 / UC09


def result_header_html(detail: dict) -> str:
    anchor = detail.get("classified_anchor")
    route = detail.get("classification_route")
    chips = []
    if anchor:
        chips.append(anchor_badge_html(anchor))
    if route:
        chips.append(route_badge_html(route))
    chips_html = '<span class="photus-dot">•</span>'.join(chips)
    hint = (
        "Busca no singular → seção Top 3 ativa"
        if detail.get("is_singular")
        else "Busca no plural → galeria completa ordenada por score"
    )
    return (
        '<div class="photus-result-head">'
        '<div class="photus-result-head-main">'
        '<p class="photus-lote-id-label">Frase original da solicitação</p>'
        f'<p class="photus-result-phrase">“{_e(detail.get("input_text"))}”</p>'
        f'<div class="photus-result-chips">{chips_html}<span class="photus-muted">ⓘ {_e(hint)}</span></div>'
        "</div>"
        '<div class="photus-result-head-side">'
        f'<p class="photus-result-lote">Lote #{_e(str(detail.get("id", ""))[:8])}</p>'
        f'<p class="photus-muted">Enviado em {_e(format_datetime(detail.get("created_at")))}</p>'
        f'{batch_status_badge_html(detail.get("status", ""))}'
        "</div></div>"
    )


def result_notice_html(detail: dict) -> str:
    """A2 (UC08): lote ainda em processamento ou terminado em erro."""
    status = detail.get("status")
    done, total = detail.get("evaluated_photos", 0), detail.get("total_photos", 0)
    if status == "em_processamento":
        return (
            '<div class="photus-notice processing">'
            f"Avaliação em andamento — {done} de {total} fotografias avaliadas. "
            "Esta tela se atualiza sozinha; você também pode voltar mais tarde.</div>"
        )
    if status == "erro":
        return (
            '<div class="photus-notice failed">A avaliação técnica deste lote terminou em erro. '
            "As fotografias avaliadas antes da falha foram preservadas.</div>"
        )
    return ""


def sort_photos(photos: list[dict]) -> list[dict]:
    return sorted(
        photos,
        key=lambda p: (p.get("final_score") is None, -(p.get("final_score") or 0), p.get("file_name", "")),
    )


def top3_photos(detail: dict) -> list[dict]:
    """UC09: só aparece se a frase é singular; as fotos já vêm marcadas (`is_top3`) pelo backend."""
    if not detail.get("is_singular"):
        return []
    return sort_photos([p for p in detail.get("photos", []) if p.get("is_top3")])


def filter_choices(detail: dict) -> list[tuple[str, str]]:
    photos = detail.get("photos", [])
    choices = []
    for key, label in FILTER_LABELS:
        n = len(photos) if key == "todas" else sum(1 for p in photos if p.get("evaluation_status") == key)
        choices.append((f"{label} ({n})", key))
    return choices


def apply_filter(photos: list[dict], key: str) -> list[dict]:
    photos = sort_photos(photos)
    return photos if key in (None, "", "todas") else [p for p in photos if p.get("evaluation_status") == key]


def top3_title_html(count: int) -> str:
    sub = (
        "As fotografias aprovadas com maior score final para o seu pedido."
        if count
        else "Nenhuma fotografia aprovada neste lote — não há fotos para compor o Top 3."
    )
    return (
        '<div class="photus-section-head">'
        '<p class="photus-section-title"><span class="photus-star">★</span> Top 3 Mais Representativas para sua Solicitação</p>'
        f'<p class="photus-page-sub">{_e(sub)}</p></div>'
    )


def gallery_title_html(shown: int, total: int) -> str:
    return (
        '<div class="photus-section-head">'
        '<p class="photus-section-title">Todas as Fotografias do Lote</p>'
        f'<p class="photus-page-sub">Ordenadas por score final, da mais para a menos aderente · '
        f"mostrando {shown} de {total}</p></div>"
    )


def _thumb_html(photo: dict, thumbs: dict[str, str]) -> str:
    uri = thumbs.get(photo.get("id", ""))
    if uri:
        return f'<img class="photus-photo-img" src="{uri}" alt="{_e(photo.get("file_name"))}" loading="lazy">'
    return '<div class="photus-photo-img placeholder">📷</div>'


def _score_html(photo: dict) -> str:
    score = photo.get("final_score")
    if score is None:
        return '<p class="photus-photo-score"><span>Sem score</span></p>'
    pct = max(0.0, min(1.0, float(score))) * 100
    color = _SCORE_BAR_COLOR.get(photo.get("evaluation_status", ""), "var(--photus-accent)")
    return (
        f'<p class="photus-photo-score"><span>Score: {score:.2f}</span><b>{pct:.0f}%</b></p>'
        f'<div class="photus-photo-bar"><div style="width:{pct:.0f}%;background:{color};"></div></div>'
    )


def photo_card_html(photo: dict, thumbs: dict[str, str]) -> str:
    top = '<span class="photus-top3-chip">★ Top 3</span>' if photo.get("is_top3") else ""
    return (
        f'<div class="photus-photo-media">{top}{_thumb_html(photo, thumbs)}</div>'
        '<div class="photus-photo-body">'
        '<div class="photus-photo-row">'
        f'<span class="photus-photo-name" title="{_e(photo.get("file_name"))}">{_e(photo.get("file_name"))}</span>'
        f'{status_badge_html(photo.get("evaluation_status", "pendente"))}</div>'
        f"{_score_html(photo)}</div>"
    )


def top3_card_html(photo: dict, rank: int, thumbs: dict[str, str]) -> str:
    score = photo.get("final_score")
    score_txt = f"{score:.2f}" if score is not None else "—"
    pct = f"{max(0.0, min(1.0, float(score))) * 100:.0f}%" if score is not None else ""
    return (
        f'<div class="photus-photo-media big"><span class="photus-rank-chip rank-{rank}">★ {_RANK_LABEL.get(rank, f"{rank}º")}</span>'
        f"{_thumb_html(photo, thumbs)}</div>"
        '<div class="photus-photo-body">'
        '<div class="photus-photo-row">'
        f'<span class="photus-photo-name" title="{_e(photo.get("file_name"))}">{_e(photo.get("file_name"))}</span>'
        f'{status_badge_html(photo.get("evaluation_status", "pendente"))}</div>'
        f'<p class="photus-top3-score rank-{rank}">{_e(score_txt)} <span>{_e(pct)}</span></p>'
        f'<div class="photus-photo-bar big rank-{rank}"><div style="width:{pct or "0%"};"></div></div></div>'
    )


def denied_html(message: str | None = None) -> str:
    msg = message or "Acesso negado. Você não tem permissão para visualizar este lote."
    return (
        '<div class="photus-empty-state denied">'
        '<div class="photus-empty-icon">🔒</div>'
        '<p class="photus-empty-title">403 — Acesso negado</p>'
        f'<p class="photus-empty-body">{_e(msg)}</p></div>'
    )
