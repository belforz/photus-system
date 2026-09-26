"""Demo E2E AO VIVO — âncora Distanciamento (Low-key) — texto até o output do Photus A.

Roda 3 casos, em ordem, com pausa manual entre eles pra narração:
  1. NORMAL (leigo)          — grupo controle
  2. FOTOGRAFO (jargão técnico) — grupo teste B
  3. CORINGA (ambiguidade)   — grupo teste A, caso-limite documentado

Pré-requisitos pra rodar:
  - Photus B no ar: `cd ../photus-b && uv run main.py` (porta 8000)
  - Binário do Photus A compilado: `../photus-a/build/photus_a`
    (`cd ../photus-a && scripts/build.sh` se não existir)
  - Preprocessor: `../ai-pre-process-images/scripts/run.sh` presente
  - Rodar de dentro de photus-system: `.venv/bin/python scripts/e2e_demo_distanciamento.py`

===============================================================================
LEIA ANTES DE APRESENTAR — 3 coisas que não bateram com o que foi pedido
===============================================================================

Investiguei o código real (server.py, orchestrator.py, categorize_text.py, os
campos de retorno) e rodei os 3 textos ao vivo contra o Photus B real antes de
escrever este script. Três coisas não bateram com a descrição original e
foram ajustadas aqui — sinalizando como pedido, em vez de forçar o resultado
"esperado" documentado por cima do comportamento real.

--- (1) Arquitetura: não existe `server.py`/`orchestrator.py` para o Photus A
Não há nenhum arquivo `server.py` ou `orchestrator.py` em nenhum repo do
ecossistema (`photus-b`, `photus-uc`, `photus-a`, `photus-system`). O que
existe de fato:

  Photus B (classificação semântica) — bate com o que foi descrito:
    - API real: `photus-b/src/presentation/api/app.py` (`create_app()`),
      rota `POST /v1/categorize` (prefixo "/v1" do app.include_router +
      "/categorize" do router em `v1/routes/classification.py`).
    - Roteador real: `CategorizationService.categorize()` em
      `categorize_text.py` — usado tanto pela API quanto pelo CLI
      `scripts/anchors/run_custom_sentences.py`, como descrito.
    - `SemanticRouter` (`strategies/embedding/semantic_router.py`) é
      código morto de verdade: só é importado por
      `pipelines/semantic_routing.py`, que por sua vez não é importado em
      nenhum lugar de `app.py`/`main.py`. Confirmado, não usei.

  Photus A (avaliação técnica) — NÃO bate com o que foi descrito:
    - Não há FastAPI nem orchestrator.py chamando o Photus A. Ele é
      invocado como processo C++ via subprocess, direto do
      `photus-system` (não do `photus-uc`):
        1. `photus.preprocessor_runner.run_preprocessor()` roda
           `ai-pre-process-images/scripts/run.sh` (normalização + índice).
        2. `photus.photus_a_runner.score_session()` roda o binário
           `photus-a/build/photus_a` sobre esse índice.
    - `anchor_translator.py` existe, mas mora no `photus-uc` e só é usado
      por `classify_semantic_anchor.py` (UC05) — que PÁRA na classificação
      do Photus B. O próprio código do photus-uc/sprint2 confirma isso
      textualmente: "Avaliação das fotos (Photus A) fica para uma sprint
      futura." O `photus-uc` nunca chama o Photus A hoje.
    Este script usa a integração real photus-system -> Photus A (já
    validei ela ao vivo, com fotos reais, antes de fechar este script).

--- (2) Caso 2 (fotógrafo): texto trocado pra reproduzir o comportamento
O texto original ("compensação de exposição negativa de 2 stops, pessoa
isolada") RODOU ao vivo contra o Photus B real e devolveu technical=False
(score `__tecnico__`=0.327, abaixo do THRESHOLD_TECNICO=0.48) — não
reproduz "technical=True mas category continua Distanciamento". O caso
documentado mais próximo (`photus-b/docs/IMPLEMENTACAO_FALLBACK_TECNICO_
NULL_REASON.md`, linha do "compensação -2 stops... pessoa sozinha e
isolada") tem o texto truncado com "..." no doc — a frase original
provavelmente tinha mais jargão técnico que a versão curta.
Troquei pelo texto abaixo, testado ao vivo e determinístico (não depende
de API do Mistral estar no ar, ao contrário do texto original, que aciona
fallback semântico):
    "compensação de exposição negativa, controlar os realces no
     histograma, sensação de solidão total, pessoa isolada na escuridão"
    -> technical=True (score=0.563 > 0.48), category=Distanciamento
       (SBERT bruto Distanciamento=0.738 > __tecnico__=0.563),
       used_fallback=False.
Os números reais (0.563/0.738) diferem dos que você tinha em mente
(0.524/0.632), mas o FENÔMENO é idêntico ao que você queria demonstrar.
Se preferir o texto original, ele ainda é um caso real interessante — só
que demonstra fallback semântico via LLM em vez de "SBERT bruto vence o
técnico". Troque `TEXTO_CASO_2` abaixo se preferir essa narrativa (mas
teste antes — depende do Mistral estar configurado e no ar).

--- (3) Caso 3 (coringa): confirmado, com uma correção de nuance
Esse caso bate EXATAMENTE com o dado já documentado em
`photus-b/docs/CALIBRACAO_THRESHOLD_MISTRAL.md` (tabela dos "3 casos
confiante e errado", teto estrutural do mecanismo de fallback): score=0.725,
gap=0.130 pra este texto exato. Rodei ao vivo e confirmei os MESMOS
números. Correção de nuance: não é que score/gap "não cruzam de forma
confiável" (sugere algo probabilístico) — eles NUNCA cruzam pra este texto
(0.725 » 0.63 e 0.130 » 0.04): o fallback nem é acionado. É determinístico
— o sistema erra com confiança, sempre, pra essa frase exata. Por isso está
documentado como "teto estrutural", não como comportamento instável.

--- Fotos escolhidas (rodei o Photus A real pra escolher, não é palpite)
Rodei preprocessor + Photus A sobre a única foto de
`dataset/distanciamento/aprovadas/` e as 13 fotos de `descarte_ambiguo/`
pra escolher com base em score real:
  - TÍPICA: `pexels-jonas-claes-16616864-7731057.jpg` (única foto curada
    como "aprovada" no dataset). ACHADO HONESTO: o Photus A pontua ela
    0.315 e classifica como `Revisao_Humana`, NÃO `Aprovado` — a curadoria
    humana e o veredito automático do Photus A discordam aqui. Vale citar
    isso na apresentação.
  - FRONTEIRA: `pexels-emmanuel-chimzimu-400572253-30404322.jpg` — score
    0.6275, bem na fronteira real entre Aprovado (>=0.63 nesta leva de 16
    fotos) e Revisao_Humana; o próprio Photus A a classificou como
    Revisao_Humana.
===============================================================================
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from photus.config import UPLOAD_ROOT  # noqa: E402
from photus.photus_a_runner import PhotusARunError, score_session  # noqa: E402
from photus.photus_b_client import PhotusBClientError, categorize_text  # noqa: E402
from photus.preprocessor_runner import PreprocessorRunError, run_preprocessor  # noqa: E402
from photus.utils import _save_photos  # noqa: E402

DATASET_ROOT = Path(__file__).resolve().parent.parent.parent / "dataset" / "distanciamento"
FOTO_TIPICA = DATASET_ROOT / "aprovadas" / "pexels-jonas-claes-16616864-7731057.jpg"
FOTO_FRONTEIRA = DATASET_ROOT / "descarte_ambiguo" / "pexels-emmanuel-chimzimu-400572253-30404322.jpg"

CATEGORIA_ESPERADA = "Distanciamento"
CATEGORY_CODE_ESPERADO = "distanciamento"

# Textos dos 3 casos — ver notas (2) e (3) no docstring do módulo.
TEXTO_CASO_1 = "quero uma foto mais sombria e escura, com clima de solidão"
TEXTO_CASO_2 = (
    "compensação de exposição negativa, controlar os realces no histograma, "
    "sensação de solidão total, pessoa isolada na escuridão"
)
TEXTO_CASO_3 = "pessoa sozinha ao entardecer, sombras longas"


class FakeFile:
    """Imita o objeto que o gr.File entrega em produção (só precisa de .name)."""

    def __init__(self, path: Path):
        self.name = str(path)


def _linha(char="=", n=78):
    print(char * n)


def pausa(msg="Pressione ENTER para continuar..."):
    input(f"\n>>> {msg}\n")


def mostrar_esperado(titulo: str, linhas: list[str]):
    print(f"\n[ESPERADO — documentado, ver notas no topo do script] {titulo}")
    for linha in linhas:
        print(f"  - {linha}")


def rodar_photus_b(texto: str) -> dict | None:
    """Chama o Photus B real (HTTP, porta 8000) e imprime o resultado bruto."""
    print(f"\n[Photus B] POST /v1/categorize  texto={texto!r}")
    try:
        result = categorize_text(texto)
    except PhotusBClientError as e:
        print(f"[ERRO] Photus B falhou: {e}")
        return None

    print(f"  category           = {result['category']}")
    print(f"  category_code       = {result['category_code']}")
    print(f"  confidence          = {result['confidence']:.4f}")
    print(f"  technical           = {result['technical']}")
    print(f"  technical_score     = {result['technical_score']:.4f}  (threshold={result['threshold']})")
    print(f"  low_confidence      = {result['low_confidence']}")
    print(f"  used_fallback       = {result['used_fallback']}")
    print(f"  sbert_anchor_before_fallback = {result['sbert_anchor_before_fallback']}")
    if result.get("fallback_reasoning"):
        print(f"  fallback_reasoning  = {result['fallback_reasoning'][:200]}...")
    print("  top_matches (top 3):")
    for m in result["top_matches"][:3]:
        print(f"    - {m['anchor_id']:<28} score={m['score']:.4f}")
    return result


def rodar_photus_a(category_code: str, label: str) -> dict | None:
    """Roda preprocessor + Photus A de verdade sobre as 2 fotos (típica + fronteira)."""
    session_id = f"demo_{uuid4().hex[:8]}"
    session_dir = UPLOAD_ROOT / session_id
    files = [FakeFile(FOTO_TIPICA), FakeFile(FOTO_FRONTEIRA)]

    print(f"\n[Pipeline completo] preprocessor + Photus A (categoria={category_code}) — {label}")
    try:
        saved_paths = _save_photos(files, session_dir)
        run_preprocessor(session_dir, category_code)
        result = score_session(saved_paths, category_code)
    except (PreprocessorRunError, PhotusARunError, subprocess.TimeoutExpired) as e:
        print(f"[ERRO] pipeline até o Photus A falhou: {e}")
        return None
    except Exception:
        print("[ERRO] falha inesperada no pipeline:")
        traceback.print_exc()
        return None
    finally:
        shutil.rmtree(session_dir, ignore_errors=True)

    print(f"  by_status = {result.get('summary', {}).get('by_status', {})}")
    for r in sorted(result["results"], key=lambda r: r.get("final_score", -1), reverse=True):
        nome = Path(r["image_path"]).name
        print(f"    - {nome:<55} status={r.get('status'):<16} final_score={r.get('final_score', 0):.4f}")
    return result


def caso_1():
    _linha()
    print("CASO 1 — NORMAL (leigo) — grupo controle")
    _linha()
    print(f"Texto: {TEXTO_CASO_1!r}")
    print(f"Foto típica:    {FOTO_TIPICA.name}")
    print(f"Foto fronteira: {FOTO_FRONTEIRA.name}")
    mostrar_esperado(
        "Classificação direta via SBERT (top-1), sem fallback.",
        [
            f"category = {CATEGORIA_ESPERADA} (Low-key)",
            "technical = False",
            "used_fallback = False",
        ],
    )
    pausa("Pressione ENTER para rodar o Photus B (classificação semântica)...")
    b_result = rodar_photus_b(TEXTO_CASO_1)

    pausa("Pressione ENTER para rodar o pipeline completo até o Photus A...")
    category_code = b_result["category_code"] if b_result else CATEGORY_CODE_ESPERADO
    a_result = rodar_photus_a(category_code, "caso 1")

    return {"caso": "1 — Normal", "b": b_result, "a": a_result}


def caso_2():
    _linha()
    print("CASO 2 — FOTÓGRAFO (jargão técnico) — grupo teste B")
    _linha()
    print(f"Texto (ajustado — ver nota (2) no topo do script): {TEXTO_CASO_2!r}")
    print(f"Foto típica:    {FOTO_TIPICA.name}")
    print(f"Foto fronteira: {FOTO_FRONTEIRA.name}")
    mostrar_esperado(
        "Jargão técnico cruza o threshold, mas o SBERT bruto da âncora estética "
        "ainda vence o ranking — category final NÃO vira '__tecnico__'.",
        [
            "technical = True (score __tecnico__ cruza THRESHOLD_TECNICO=0.48)",
            f"category final continua {CATEGORIA_ESPERADA} porque "
            f"{CATEGORIA_ESPERADA} vence o __tecnico__ no ranking bruto do SBERT",
            "O diagnóstico técnico é auditoria apenas — nunca substitui 'category'",
        ],
    )
    pausa("Pressione ENTER para rodar o Photus B (classificação semântica)...")
    b_result = rodar_photus_b(TEXTO_CASO_2)

    pausa("Pressione ENTER para rodar o pipeline completo até o Photus A...")
    category_code = b_result["category_code"] if b_result else CATEGORY_CODE_ESPERADO
    a_result = rodar_photus_a(category_code, "caso 2")

    return {"caso": "2 — Fotógrafo", "b": b_result, "a": a_result}


def caso_3():
    _linha()
    print("CASO 3 — CORINGA (ambiguidade) — grupo teste A, caso-limite documentado")
    _linha()
    print(f"Texto: {TEXTO_CASO_3!r}")
    print(f"Foto típica:    {FOTO_TIPICA.name}")
    print(f"Foto fronteira: {FOTO_FRONTEIRA.name}")
    mostrar_esperado(
        "Achado negativo documentado (CALIBRACAO_THRESHOLD_MISTRAL.md — 'confiante "
        "e errado', teto estrutural do fallback). Ambíguo entre Distanciamento e "
        "Sublime; score/gap NUNCA cruzam os thresholds pra este texto, então o "
        "fallback nem é acionado — o sistema erra com confiança, sempre.",
        [
            f"category obtido = {CATEGORIA_ESPERADA} (mas o rótulo correto é ambíguo — não deveria ser só Distanciamento)",
            "score ≈ 0.725 (» THRESHOLD_SCORE_FALLBACK=0.63)",
            "gap ≈ 0.130 (» THRESHOLD_GAP_FALLBACK=0.04)",
            "used_fallback = False — limitação estrutural conhecida, NÃO um bug a corrigir aqui",
        ],
    )
    pausa("Pressione ENTER para rodar o Photus B (classificação semântica)...")
    b_result = rodar_photus_b(TEXTO_CASO_3)

    pausa("Pressione ENTER para rodar o pipeline completo até o Photus A...")
    category_code = b_result["category_code"] if b_result else CATEGORY_CODE_ESPERADO
    a_result = rodar_photus_a(category_code, "caso 3")

    return {"caso": "3 — Coringa", "b": b_result, "a": a_result}


def resumo(resultados: list[dict]):
    _linha()
    print("RESUMO — esperado vs. obtido")
    _linha()
    esperado_por_caso = {
        "1 — Normal": "category=Distanciamento, technical=False, sem fallback",
        "2 — Fotógrafo": "technical=True, category permanece Distanciamento (SBERT bruto vence __tecnico__)",
        "3 — Coringa": "category=Distanciamento (ambíguo/errado), sem fallback — teto estrutural documentado",
    }
    for r in resultados:
        caso = r["caso"]
        b = r["b"]
        print(f"\n{caso}")
        print(f"  esperado: {esperado_por_caso.get(caso, '-')}")
        if b is None:
            print("  obtido:   [FALHOU — Photus B não respondeu, ver erro acima]")
            continue
        print(
            f"  obtido:   category={b['category']}, technical={b['technical']} "
            f"(score={b['technical_score']:.3f}), used_fallback={b['used_fallback']}"
        )
        if r["a"] is None:
            print("  Photus A: [FALHOU — ver erro acima]")
        else:
            print(f"  Photus A: by_status={r['a'].get('summary', {}).get('by_status', {})}")


def main():
    print("Demo E2E ao vivo — âncora Distanciamento (Low-key)")
    print("Leia as notas no topo do arquivo antes de apresentar (server.py/orchestrator.py")
    print("não existem; caso 2 usa texto ajustado; caso 3 é achado negativo documentado).")
    if not FOTO_TIPICA.exists() or not FOTO_FRONTEIRA.exists():
        print("\n[ERRO] Uma das fotos de teste não foi encontrada:")
        print(f"  típica:    {FOTO_TIPICA} (existe={FOTO_TIPICA.exists()})")
        print(f"  fronteira: {FOTO_FRONTEIRA} (existe={FOTO_FRONTEIRA.exists()})")
        print("Verifique se o dataset está em /home/belforz/dataset/distanciamento/")
        return

    pausa("Pressione ENTER para começar a demonstração...")

    resultados = []
    for caso_fn in (caso_1, caso_2, caso_3):
        try:
            resultados.append(caso_fn())
        except Exception:
            print(f"\n[ERRO] {caso_fn.__name__} quebrou inesperadamente:")
            traceback.print_exc()
            print("Seguindo para o próximo caso — a demonstração continua.")
            resultados.append({"caso": caso_fn.__name__, "b": None, "a": None})
        pausa("Pressione ENTER para o próximo caso...")

    resumo(resultados)


if __name__ == "__main__":
    main()
