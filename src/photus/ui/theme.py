"""CSS global aplicado ao gr.Blocks -- ajustes de fluidez visual (transicoes
suaves, cantos arredondados, hover states) sobre os elementos marcados com
`elem_classes` nos componentes (ver ui/index.py). Escopado a essas classes
proprias em vez de seletores internos do Gradio, que mudam entre versoes.
"""

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
"""
