# Photus System

Front (Gradio) do ecossistema Photus: recebe fotos + uma frase descrevendo a vibe desejada, e orquestra o pipeline `Upload → Pasta de staging → Photus B (SBERT) → Preprocessor → Photus A (OpenCV + Random Forest) → Top 3`.

## Rodando

Photus B (categorização) e Photus UC (cadastro/login/perfil) rodam como serviços HTTP
separados (repos irmãos `photus-b` e `photus-uc`) e precisam estar de pé antes do front:

```bash
# terminal 1 — repo photus-b
cd ../photus-b
uv run main.py                                          # sobe em http://localhost:8000

# terminal 2 — repo photus-uc
cd ../photus-uc
uv run alembic upgrade head                              # cria a tabela usuario (sqlite local por padrão)
uv run uvicorn main:app --port 8001                      # sobe em http://localhost:8001

# terminal 3 — este repo
cd photus-system
uv run main.py                                           # sobe a UI Gradio em http://localhost:7860
```

Sem tela de cadastro/login/perfil o Photus UC não precisa estar rodando para o pipeline
de fotos funcionar, mas a UI vai ficar travada na tela de login/cadastro — é a porta de
entrada obrigatória do app (ver `src/photus/ui/auth.py`).

Variáveis de ambiente opcionais:

| Variável | Padrão | Descrição |
|---|---|---|
| `PHOTUS_B_URL` | `http://localhost:8000` | Base URL do serviço Photus B |
| `PHOTUS_B_TIMEOUT_SECONDS` | `15` | Timeout da chamada HTTP ao Photus B |
| `PHOTUS_UC_URL` | `http://localhost:8001` | Base URL do serviço Photus UC (auth/perfil) |
| `PHOTUS_UC_TIMEOUT_SECONDS` | `15` | Timeout da chamada HTTP ao Photus UC |
| `PHOTUS_SESSION_SECRET` | `photus-dev-session-secret` | Chave de criptografia da sessão (JWT) salva no navegador (`gr.BrowserState`). Troque em produção. |

## Conector com o Photus B

`src/photus/photus_b_client.py` chama `POST {PHOTUS_B_URL}/v1/categorize` e é usado no Stage 2 do pipeline (`src/photus/app.py::process_pipeline`) para categorizar a frase do usuário. Se o Photus B estiver fora do ar ou responder com erro, `categorize_text` levanta `PhotusBClientError`, que o pipeline captura e exibe no chat sem derrubar a UI.

Ver [../photus-b/docs/API.md](../photus-b/docs/API.md) para o contrato completo da API.

## Gestão de Acesso (Sprint 1 — UC01/UC02/UC03)

Telas de Cadastro, Login e Perfil (`src/photus/ui/auth.py`), implementadas a partir do
protótipo Figma da sprint 1 e integradas ao backend real `photus-uc` via
`src/photus/auth_client.py`:

| Ação | Endpoint no `photus-uc` |
|---|---|
| Cadastrar-se (UC01) | `POST /usuarios` |
| Autenticar-se (UC02) | `POST /auth/login` |
| Atualizar Perfil (UC03) | `PATCH /usuarios/me` |

A sessão (token JWT + dados públicos do usuário) fica em `gr.BrowserState`, persistida no
`localStorage` do navegador — sobrevive a reload de página e a restart do servidor Gradio
(por isso a secret fixa via `PHOTUS_SESSION_SECRET`).

**Limitação conhecida:** o campo "Membro Desde" só é populado logo após o cadastro
(`POST /usuarios` retorna `criado_em`); o login (`POST /auth/login`) e a atualização de
perfil (`PATCH /usuarios/me`) não devolvem essa data, então a tela de Perfil mostra "—"
quando o usuário chega via login. Resolver isso exigiria um endpoint `GET /usuarios/me`
no `photus-uc`, que não existe nesta sprint.
