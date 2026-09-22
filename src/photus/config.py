import os
from pathlib import Path

# Raiz do projeto (dois níveis acima de src/photus)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

MAX_PHOTOS = 20
UPLOAD_ROOT = PROJECT_ROOT / "data" / "uploads"

# Preprocessor (repo irmao) grava thumbnails/variantes fora do projeto; o Gradio
# so serve arquivos de dentro do cwd/tmp por padrao, entao esse dir precisa ser
# passado em allowed_paths no demo.launch().
PREPROCESSOR_IMAGES_ROOT = PROJECT_ROOT.parent / "ai-pre-process-images" / "images"

# Photus UC (cadastro/login/perfil/lotes de avaliacao) roda como servico HTTP separado (repo irmao
# photus-uc, `uv run uvicorn main:app --port 8001`). Porta default != Photus B (8000)
# para nao colidir quando os dois servicos sobem juntos.
PHOTUS_UC_URL = os.getenv("PHOTUS_UC_URL", "http://localhost:8001").rstrip("/")
PHOTUS_UC_TIMEOUT_SECONDS = float(os.getenv("PHOTUS_UC_TIMEOUT_SECONDS", "15"))

# Chave usada para criptografar o gr.BrowserState (sessao/token JWT) salvo no
# localStorage do navegador. Fixa (nao aleatoria) para a sessao sobreviver a
# um restart do servidor Gradio; troque via env em producao.
SESSION_BROWSER_SECRET = os.getenv("PHOTUS_SESSION_SECRET", "photus-dev-session-secret")
