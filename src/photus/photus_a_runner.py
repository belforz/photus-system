import json
import subprocess
import tempfile
from pathlib import Path

from loguru import logger

from photus.config import PROJECT_ROOT
from photus.preprocessor_runner import session_entries

# Photus A vive como repositorio irmao de photus-system.
PHOTUS_A_ROOT = PROJECT_ROOT.parent / "photus-a"
PHOTUS_A_BIN = PHOTUS_A_ROOT / "build" / "photus_a"

DEFAULT_TIMEOUT_SECONDS = 120
_RELEVANT_TYPES = {"original", "color_gray", "color_hsv"}


class PhotusARunError(RuntimeError):
    """Raised when the Photus A binary fails to produce a valid result."""


def _run_binary(json_input_paths: list[Path], tmp_dir: Path, timeout: int) -> dict:
    output_path = tmp_dir / "output.json"
    proc = subprocess.run(
        [str(PHOTUS_A_BIN), *(str(p) for p in json_input_paths), "--output", str(output_path)],
        # cwd fixo na raiz do photus-a: o binario carrega modelo/YuNet/thresholds por path
        # relativo ao proprio repo (ex: local/technician_model/...). So o output.json e isolado
        # por chamada, via --output apontando para um tempdir absoluto.
        cwd=PHOTUS_A_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if proc.stdout:
        logger.debug("photus_a stdout:\n{}", proc.stdout)
    if proc.stderr:
        logger.warning("photus_a stderr:\n{}", proc.stderr)

    if not output_path.exists():
        raise PhotusARunError(
            f"photus_a nao gerou output.json (exit={proc.returncode}): {proc.stderr[-2000:]}"
        )

    result = json.loads(output_path.read_text())
    if proc.returncode != 0 or result.get("error"):
        logger.error("photus_a run {} terminou com erro: {}", result.get("run_id"), result.get("error"))
    return result


def _check_binary():
    if not PHOTUS_A_BIN.exists():
        raise PhotusARunError(
            f"Binario do Photus A nao encontrado em {PHOTUS_A_BIN}. Rode scripts/build.sh no repo photus-a."
        )


def run_photus_a(json_input_paths: list[Path | str], timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    """Runs the Photus A binary over pre-built JSON files (preproc_report/image_index) and returns output.json."""
    _check_binary()
    resolved = [Path(p).resolve() for p in json_input_paths]
    with tempfile.TemporaryDirectory(prefix="photus_a_run_") as tmp_dir:
        return _run_binary(resolved, Path(tmp_dir), timeout)


def score_session(
    saved_paths: list[Path | str], category_code: str | None = None, timeout: int = DEFAULT_TIMEOUT_SECONDS
) -> dict:
    """Scores one upload session with Photus A, using the Preprocessor's already-normalized outputs.

    Le as entradas (original/color_gray/color_hsv) desta sessao em images_index.json -- escrito
    pelo Preprocessor no Stage 3 -- em vez de reconverter as fotos brutas, e roda o Photus A
    sobre elas.
    """
    _check_binary()
    if not saved_paths:
        raise ValueError("score_session requer ao menos uma imagem.")

    session_images = session_entries(saved_paths, _RELEVANT_TYPES)
    if not session_images:
        raise PhotusARunError(
            "Nenhuma entrada desta sessao encontrada em images_index.json. O Preprocessor rodou antes?"
        )

    index = {"images": session_images}
    if category_code:
        index["category"] = category_code

    with tempfile.TemporaryDirectory(prefix="photus_a_run_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        index_file = tmp_path / "image_index.json"
        index_file.write_text(json.dumps(index))
        return _run_binary([index_file], tmp_path, timeout)
