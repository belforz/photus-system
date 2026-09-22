
from __future__ import annotations

import html

from photus.ui.theme import anchor_badge_html, route_badge_html

STEPS = [
    "Criando Lote de Avaliação...",
    "Analisando texto no Photus B...",
    "Roteando para âncora estética ou jargão técnico...",
]


def ui_modal(
    stage: int,
    *,
    done: bool = False,
    failed: bool = False,
    category: str | None = None,
    route_type: str | None = None,
    fallback_notice: bool = False,
) -> str:
    """Monta o HTML do card do modal (stepper + badges + estados de exceção).

    `stage` é o índice (0-2) da etapa ativa em STEPS; `failed` marca essa
    etapa como erro (A1/RNF06); `done=True` marca todas como concluídas e
    habilita a pré-visualização da rota (category/route_type).
    """
    steps_html = []
    for i, label in enumerate(STEPS):
        if failed and i == stage:
            state, icon = "failed", "!"
        elif done or i < stage:
            state, icon = "done", "✓"
        elif i == stage:
            state, icon = "active", ""
        else:
            state, icon = "pending", ""
        steps_html.append(
            f'<div class="photus-modal-step {state}"><div class="icon">{icon}</div><span>{html.escape(label)}</span></div>'
        )

    body = (
        '<p class="photus-modal-title">Processando Lote</p>'
        '<p class="photus-modal-subtitle">Aguarde enquanto classificamos a âncora semântica do seu lote.</p>'
        f'<div class="photus-modal-steps">{"".join(steps_html)}</div>'
    )

    if failed:
        body += (
            '<div class="photus-exception-card">'
            '<span class="photus-exception-status">status: erro</span>'
            '<p class="photus-exception-title">⚠️ Falha de Conexão Photus B</p>'
            '<p class="photus-exception-body">O motor semântico demorou a responder. '
            "Seu lote foi colocado em fila para nova tentativa.</p>"
            '<p class="photus-exception-note">Estado "erro" persistido sem travar a UI (RNF06).</p>'
            "</div>"
        )
    elif done and category and route_type:
        body += (
            '<div class="photus-modal-divider"></div>'
            '<p class="photus-modal-route-label">Pré-visualização da Rota</p>'
            f'<div class="photus-modal-badges">{anchor_badge_html(category)}{route_badge_html(route_type)}</div>'
        )
        if fallback_notice:
            body += (
                '<div class="photus-exception-card fallback">'
                '<span class="photus-exception-status">fallback</span>'
                '<p class="photus-exception-title">⚙️ Aplicando calibrações globais de estilo</p>'
                '<p class="photus-exception-body">Mapeamento genérico aplicado com aviso discreto ao usuário.</p>'
                '<p class="photus-exception-note">Fallback silencioso (RF16) — nenhuma ação bloqueante.</p>'
                "</div>"
            )

    return body
