STAGES = [
    "Upload",
    "Pasta de staging",
    "Photus B (SBERT)",
    "Preprocessor",
    "Photus A (OpenCV + RF)",
    "Top 3",
]

_CSS = """
<style>
.pipeline-container {
    display: flex;
    align-items: flex-start;
    flex-wrap: wrap;
    width: 100%;
    box-sizing: border-box;
    background: var(--block-background-fill, #f9fafb);
    border: 1px solid var(--border-color-primary, #e5e7eb);
    border-radius: 12px;
    padding: 18px 12px 14px;
    font-family: inherit;
}
.pipeline-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    flex: 1 1 0;
    min-width: 58px;
}
.pipeline-step .dot {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    border: 2px solid var(--border-color-primary, #d1d5db);
    color: var(--body-text-color-subdued, #9ca3af);
    background: transparent;
    transition: all 0.25s ease;
}
.pipeline-step .label {
    font-size: 10.5px;
    text-align: center;
    color: var(--body-text-color-subdued, #9ca3af);
    line-height: 1.25;
}
.pipeline-step.completed .dot {
    background: #7c3aed;
    border-color: #7c3aed;
    color: #fff;
}
.pipeline-step.completed .label { color: #7c3aed; font-weight: 600; }
.pipeline-step.active .dot {
    border-color: #7c3aed;
    color: #7c3aed;
    box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.15);
}
.pipeline-step.active .label { color: #7c3aed; font-weight: 700; }
.pipeline-step.failed .dot {
    background: #ef4444;
    border-color: #ef4444;
    color: #fff;
}
.pipeline-step.failed .label { color: #ef4444; font-weight: 700; }
.pipeline-connector {
    flex: 0 1 20px;
    height: 2px;
    margin-top: 12px;
    background: var(--border-color-primary, #d1d5db);
    transition: background 0.25s ease;
}
.pipeline-connector.completed { background: #7c3aed; }
</style>
"""


def ui_status(stage: int, *, done: bool = False, failed: bool = False) -> str:
    items = []
    for i, label in enumerate(STAGES):
        if done:
            state, icon = "completed", "✓"
        elif failed and i == stage:
            state, icon = "failed", "!"
        elif i < stage:
            state, icon = "completed", "✓"
        elif i == stage:
            state, icon = "active", str(i + 1)
        else:
            state, icon = "pending", str(i + 1)

        items.append(
            f'<div class="pipeline-step {state}">'
            f'<div class="dot">{icon}</div>'
            f'<div class="label">{label}</div>'
            f"</div>"
        )
        if i < len(STAGES) - 1:
            connector_state = "completed" if (done or i < stage) else ""
            items.append(f'<div class="pipeline-connector {connector_state}"></div>')

    return _CSS + f'<div class="pipeline-container">{"".join(items)}</div>'
