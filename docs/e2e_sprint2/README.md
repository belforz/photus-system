# Evidências E2E — Sprint 2 (via container), 2026-09-26

Validação manual do fluxo TC-S2-01..09 (ver `Plano_Testes_Photus_Sprint2.xlsx`)
contra os três serviços rodando dentro de um único container Docker
(`belforzz/photus-system:latest`, container `bold_elbakyan`, portas 7860/8001/8000
mapeadas para o host), sem mocks. Testado pelo navegador real do usuário
(Claude in Chrome), com upload de arquivos JPG reais (não simulados via canvas).

> **Screenshots:** capturados com `save_to_disk` durante a sessão (várias
> dezenas, cobrindo cada cenário abaixo). Não consegui localizar o caminho
> real desses arquivos no disco do host a partir das minhas próprias
> ferramentas de shell — o mecanismo parece entregar o PNG só para o lado do
> cliente da extensão, não para um caminho que eu enxergo. Se você conseguir
> ver/baixar essas imagens pela sua própria sessão do Chrome/Claude, me avise
> onde elas caíram que eu componho este documento com os arquivos de verdade
> embutidos; por ora descrevo cada captura em texto, na ordem em que rodou.

## Cenário 1 — TC-S2-01 / TC-S2-05: submissão válida, rota fast_track

Texto "céu dourado ao entardecer, sensação de calma e nostalgia" + 2 fotos
JPG reais (`praia-dourada-01.jpg`, `ceu-nostalgico-02.jpg`, geradas via PIL,
~5KB cada). Upload real via input de arquivo (não JS/canvas). Resultado:

- Contador atualizou para "2 / 20 imagens anexadas"; miniaturas reais
  (laranja/roxo) renderizadas com nome do arquivo sobreposto.
- Modal "Processando Lote" abriu com o stepper de 3 etapas.
- Log do container: `Photus UC: lote <uuid> criado -> status=em_processamento,
  ancora=nostalgia, rota=fast_track`.
- "Texto com âncora destacada" mostrou a tag `nostalgia` sobre a frase
  completa após o fechamento do modal.

## Cenário 2 — TC-S2-04: jargão técnico → rota tecnico

Texto trocado para "f/1.8, ISO 200, 1/500s, 50mm, luz lateral suave" (mesmas
2 fotos). Log do container confirmou:
`ancora=nostalgia, rota=tecnico` — a âncora semântica mais próxima
(SBERT) continua sendo reportada mesmo quando a rota é `tecnico`; só o campo
`classification_route` muda, não `classified_anchor`. Isso é comportamento
esperado do `ClassifySemanticAnchor` do photus-uc, não um bug — só não fica
óbvio olhando só a UI (o badge de âncora não muda, o de rota é que fica
escondido dentro do modal, que fecha rápido demais pra capturar o print a
tempo nas duas tentativas que fiz).

## Cenário 3 — TC-S2-02: limite de 20 fotos excedido — bug real encontrado e corrigido

Upload de 21 fotos JPG reais de uma vez (`lote-01.jpg` .. `lote-21.jpg`).

**Comportamento observado ANTES da correção:** o contador ficava em "20/20"
(a 21ª foto sumia da lista) e o banner "Limite excedido" não aparecia —
mesmo a 21ª foto tendo sido de fato anexada e depois descartada
silenciosamente.

**Causa:** `_on_files_change` (em `src/photus/ui/submission.py`) fazia
`gr.update(value=trimmed)` no próprio `files_input` que disparou o evento
`.change()`. O Gradio não distingue uma atualização programática de uma
interação do usuário, então essa escrita re-disparava o mesmo callback com a
lista já cortada para 20 (dentro do limite) — a segunda passada calculava
`over_limit=False` e sobrescrevia o banner "Limite excedido" (`visible=True`)
de volta para `visible=False`, quase instantaneamente.

**Correção aplicada** (uncommitted em `src/photus/ui/submission.py` — ver
`git diff`): parei de truncar a lista programaticamente. Agora o front só
bloqueia o envio (`submit_btn` fica `interactive=False`) e mantém o banner
visível enquanto `count > 20`; a lista completa (21 itens) permanece visível
e o usuário remove o excedente pelos botões `[x]` nativos de cada arquivo —
isso também bate mais literalmente com a redação da spec ("o sistema
bloqueia o envio", não "o sistema descarta fotos por conta própria").

**Comportamento observado DEPOIS da correção** (reproduzido contra o
container reiniciado com o patch, via `docker cp` + `docker restart`):
- Contador "21 / 20 imagens anexadas" em vermelho, persistente.
- Banner vermelho "Limite excedido: selecione no máximo 20 fotos por lote."
  persistente (não pisca e some mais).
- Botão "Submeter Lote para Avaliação" desabilitado.
- Removendo 1 foto (clique no `[x]` de `lote-21.jpg`): contador volta a
  "20 / 20" em cor normal, banner some, botão reabilita — tudo consistente.

**Atenção:** o patch está aplicado no arquivo do repo (host) e foi copiado
para dentro do container rodando (`docker cp` + `docker restart`) só para
poder validar o fix ao vivo nesta sessão — **ainda não foi commitado nem
rebuildado na imagem `belforzz/photus-system:latest`**. Se vocês fizerem
`docker compose down`/recriar o container a partir da imagem publicada sem
antes commitar/rebuildar, esse fix se perde. Rode `git diff
src/photus/ui/submission.py` pra conferir antes de decidir se commita.

## Cenário 4 — TC-S2-03: validação de campo vazio (A2)

1 foto anexada (`horizonte-03.jpg`), campo de descrição vazio, clique em
"Submeter Lote para Avaliação". Resultado:
- Borda vermelha no campo de texto.
- Banner vermelho "Preencha a descrição ou anexe ao menos uma foto." visível
  logo abaixo do contador "1 / 20 imagens anexadas".
- Nenhuma chamada ao Photus UC (bloqueio client-side).

## Cenário 5 — TC-S2-09: falha do Photus B (RNF06) — testado com o processo pausado, não morto

Em vez de derrubar o processo do Photus B (o que reinicia o container
inteiro — o `entrypoint.sh` usa `wait -n "$UC_PID" "$B_PID" "$SYSTEM_PID"` e
mata todo mundo se qualquer um dos três sair), usei `SIGSTOP` no processo do
Photus B de dentro do próprio container (`os.kill(<pid>, signal.SIGSTOP)`
via um python -c, já que a imagem não tem `kill`/`pgrep`) — simula um
serviço travado/sem resposta sem matar nada. Depois do teste, `SIGCONT` pra
religar.

Resultado, com texto "retrato em preto e branco, atmosfera dramática e
intensa" + 1 foto:
- Modal ficou preso em "Analisando texto no Photus B..." por ~15-18s.
- Card de exceção apareceu: badge "status: erro", "⚠️ Falha de Conexão
  Photus B", corpo explicando a fila de nova tentativa, nota "RNF06", botão
  "Fechar" (testado — fecha corretamente).
- **Achado, não corrigido:** o log do container mostra que, desta vez, foi o
  **photus-system** que abandonou a chamada a `POST /batches` por timeout
  próprio (`AuthClientError: ... timed out`), não o `photus-uc` respondendo
  HTTP 201 com `status=erro` como no teste anterior (sessão de 22/09). Isso
  porque `PHOTUS_UC_TIMEOUT_SECONDS` (client do photus-system) e
  `PHOTUS_B_TIMEOUT_SECONDS` (client do photus-uc) estão configurados para o
  mesmo valor (15s) — é uma corrida: às vezes o photus-uc consegue terminar
  seu próprio timeout e responder "erro" graciosamente antes, às vezes o
  photus-system desiste primeiro. Visualmente o usuário vê o mesmo card nos
  dois casos (RNF06 não quebra a UI de qualquer forma), mas o timeout do
  cliente externo devia ter uma folga a mais que o do cliente interno pra
  sempre dar chance do caminho gracioso completar primeiro. Não mexi nisso
  nesta sessão — é uma sugestão de ajuste de configuração, não um bug
  visível ao usuário.
- Depois do `SIGCONT`: `/health` do Photus B voltou a `200 ok` e uma nova
  submissão (mesmo texto) classificou normalmente como `solenidade` /
  `fast_track` — confirma que o sistema realmente não trava depois da falha
  (RNF06 cumprido na prática, mesmo com a corrida de timeout acima).

## Ambiente

| Serviço | Como verificado |
| :--- | :--- |
| Container | `docker ps` → `bold_elbakyan`, imagem `belforzz/photus-system:latest`, portas `7860`, `8001`, `8000` mapeadas |
| photus-b | `curl http://127.0.0.1:8000/health` |
| photus-uc | `curl http://127.0.0.1:8001/health` |
| photus-system | `curl http://127.0.0.1:7860` |

Conta usada: sessão já autenticada como "Leandro Belfor" (persistida no
`localStorage` do Chrome do usuário de uma sessão anterior).
