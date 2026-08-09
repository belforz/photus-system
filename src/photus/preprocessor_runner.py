import json
import subprocess
from pathlib import Path

from loguru import logger

from photus.config import PROJECT_ROOT

# Preprocessor vive como repositorio irmao de photus-system.
PREPROCESSOR_ROOT = PROJECT_ROOT.parent / "ai-pre-process-images"
PREPROCESSOR_SCRIPT = PREPROCESSOR_ROOT / "scripts" / "run.sh"
IMAGES_INDEX_PATH = PREPROCESSOR_ROOT / "local" / "images_index.json"

DEFAULT_TIMEOUT_SECONDS = 180
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp", ".bmp"}

_RESULT_MARKER = "Pipeline result:\n"


class PreprocessorRunError(RuntimeError):
    """Raised when the preprocessor script fails to normalize a batch of photos."""


def run_preprocessor(session_dir: Path, category_code: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> list[dict]:
    """Runs the C++ preprocessor over every photo in `session_dir`, tagged with `category_code`.

    Ao contrario do Photus A, o preprocessor grava saida em caminhos relativos ao proprio
    repo (local/json/, local/images_index.json), entao roda com cwd=PREPROCESSOR_ROOT em vez
    de um tempdir isolado -- isso faz esses arquivos se acumularem no lugar certo entre chamadas.
    Os resultados por foto (ImageMetadata) sao extraidos direto do stdout, ja que
    local/images_index.json e um indice global compartilhado entre sessoes, nao um output
    isolado por chamada.
    """
    if not PREPROCESSOR_SCRIPT.exists():
        raise PreprocessorRunError(
            f"scripts/run.sh nao encontrado em {PREPROCESSOR_SCRIPT}. Confira o repo ai-pre-process-images."
        )

    proc = subprocess.run(
        ["bash", str(PREPROCESSOR_SCRIPT), "--dir", str(Path(session_dir).resolve()), "--category", category_code],
        cwd=PREPROCESSOR_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if proc.stderr:
        logger.debug("preprocessor stderr:\n{}", proc.stderr)

    if proc.returncode != 0:
        raise PreprocessorRunError(
            f"preprocessor terminou com exit={proc.returncode}: {(proc.stderr or proc.stdout)[-2000:]}"
        )

    results = _parse_pipeline_results(proc.stdout)
    if not results:
        raise PreprocessorRunError(
            f"preprocessor rodou (exit=0) mas nao retornou nenhum resultado valido:\n{proc.stdout[-2000:]}"
        )

    expected = _count_photos(session_dir)
    if len(results) < expected:
        logger.warning(
            "preprocessor normalizou apenas {}/{} foto(s) da sessao {}", len(results), expected, session_dir
        )
    else:
        logger.info("preprocessor normalizou {} foto(s) da sessao {}", len(results), session_dir)

    return results


def _parse_pipeline_results(stdout: str) -> list[dict]:
    """Extrai cada bloco de ImageMetadata JSON impresso apos 'Pipeline result:' no stdout.

    O stdout mistura logs coloridos com um bloco JSON por foto processada, entao usamos
    json.JSONDecoder.raw_decode para extrair so o objeto, ignorando o que vem antes/depois.
    """
    decoder = json.JSONDecoder()
    results = []
    search_from = 0
    while True:
        marker_idx = stdout.find(_RESULT_MARKER, search_from)
        if marker_idx == -1:
            break
        json_start = marker_idx + len(_RESULT_MARKER)
        try:
            obj, end = decoder.raw_decode(stdout, json_start)
            results.append(obj)
            search_from = end
        except json.JSONDecodeError:
            logger.warning("Falha ao parsear bloco de resultado do preprocessor no offset {}", marker_idx)
            search_from = json_start
    return results


def _count_photos(session_dir: Path) -> int:
    return sum(1 for p in Path(session_dir).iterdir() if p.suffix.lower() in SUPPORTED_EXTS)


def session_entries(saved_paths: list[Path], types: set[str]) -> list[dict]:
    """Filters this session's rows out of the shared images_index.json by filename and type.

    images_index.json e um indice global que acumula entradas de toda sessao ja processada
    (dedupado por path), entao filtramos por filename e, para o tipo "original", tambem pelo
    path exato desta sessao -- os demais tipos (color_gray, thumbnail, ...) sao derivados do
    filename e nao carregam o path de sessao.
    """
    if not IMAGES_INDEX_PATH.exists():
        raise PreprocessorRunError(
            f"images_index.json nao encontrado em {IMAGES_INDEX_PATH}. Rode o Preprocessor antes."
        )

    session_paths = {Path(p).resolve() for p in saved_paths}
    session_filenames = {Path(p).name for p in saved_paths}

    index = json.loads(IMAGES_INDEX_PATH.read_text())
    entries = []
    for img in index.get("images", []):
        if img.get("type") not in types or img.get("filename") not in session_filenames:
            continue
        if img.get("type") == "original" and Path(img.get("path", "")).resolve() not in session_paths:
            continue
        entries.append(img)
    return entries
