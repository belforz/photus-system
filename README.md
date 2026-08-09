# Photus System

Front (Gradio) do ecossistema Photus: recebe fotos + uma frase descrevendo a vibe desejada, e orquestra o pipeline `Upload → Pasta de staging → Photus B (SBERT) → Preprocessor → Photus A (OpenCV + Random Forest) → Top 3`.

## Rodando

Photus B roda como serviço HTTP separado (repo irmão `photus-b`) e precisa estar de pé antes do front:

```bash
# terminal 1 — repo photus-b
cd ../photus-b
uv run main.py                 # sobe em http://localhost:8000

# terminal 2 — este repo
cd photus-system
uv run main.py                 # sobe a UI Gradio
```

Variáveis de ambiente opcionais (front → Photus B):

| Variável | Padrão | Descrição |
|---|---|---|
| `PHOTUS_B_URL` | `http://localhost:8000` | Base URL do serviço Photus B |
| `PHOTUS_B_TIMEOUT_SECONDS` | `15` | Timeout da chamada HTTP ao Photus B |

## Conector com o Photus B

`src/photus/photus_b_client.py` chama `POST {PHOTUS_B_URL}/v1/categorize` e é usado no Stage 2 do pipeline (`src/photus/app.py::process_pipeline`) para categorizar a frase do usuário. Se o Photus B estiver fora do ar ou responder com erro, `categorize_text` levanta `PhotusBClientError`, que o pipeline captura e exibe no chat sem derrubar a UI.

Ver [../photus-b/docs/API.md](../photus-b/docs/API.md) para o contrato completo da API.
