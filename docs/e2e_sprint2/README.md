# Evidências E2E — Sprint 2 (Submissão + Roteamento Semântico)

Validação manual do fluxo completo (UC04 + UC05) com os três serviços reais
rodando lado a lado, sem mocks: `photus-system` (front, porta 7860),
`photus-uc` (auth + `POST /batches`, porta 8001) e `photus-b` (classificação
semântica, porta 8000). Rodado em 2026-09-22.

> **Nota sobre as evidências:** o navegador usado para os testes (Browser
> pane do Claude Code) não expõe um jeito de salvar os screenshots tirados
> durante a sessão como arquivos PNG — as capturas ficam só visíveis na
> conversa, não no disco. Por isso este documento traz evidência em texto
> (mensagens exatas da UI, logs do servidor com IDs de lote reais, HTML
> renderizado) em vez de imagens. Cada cenário abaixo foi conferido
> visualmente durante a sessão antes de ser registrado aqui.

## Ambiente

| Serviço | Porta | Como subiu |
| :--- | :--- | :--- |
| `photus-b` | 8000 | `cd photus-b && uv run main.py` |
| `photus-uc` | 8001 | `cd photus-uc && uv run uvicorn main:app --port 8001` (com `.env`: `PHOTUS_B_BASE_URL=http://localhost:8000` — o default do Settings aponta pra 8001, que colide com a própria porta do photus-uc quando os dois sobem localmente sem docker-compose) |
| `photus-system` | 7860 | `cd photus-system && .venv/bin/python main.py` |

Conta de teste: `sprint2.tester@photus.dev` (tipo `leigo`).

## Cenário 1 — Tela de login (estado deslogado)

Navegação direta pra `http://127.0.0.1:7860` sem sessão salva no
`localStorage`. Renderiza o card "Entrar no Photus" centralizado, tema
escuro (`#121214` fundo / `#20242d` card / `#6366f1` accent), sem topbar
(oculta corretamente enquanto deslogado — confirmado também via
`document.querySelectorAll('.photus-topbar')` retornando `[]` nesse
estado). Nenhum defeito encontrado no cabeçalho/topo da tela de login.

## Cenário 2 — Validação A2 (campo vazio)

Anexada 1 foto, campo de texto deixado vazio, clique em "Submeter Lote para
Avaliação". Resultado observado:

- Banner vermelho: **"Preencha a descrição ou anexe ao menos uma foto."**
- Borda vermelha aplicada tanto no textarea quanto no dropzone
  (`elem_classes` trocadas para incluir `field-error`).
- Nenhuma chamada ao Photus UC é feita (validação client-side barra antes).

## Cenário 3 — Submissão válida (UC04 → UC05, rota `fast_track`)

Texto: *"céu dourado ao entardecer, sensação de calma e nostalgia"* + 1-2
fotos sintéticas (PNGs gerados via `canvas.toBlob` no próprio browser, sem
depender de upload de arquivo real do SO). Log real do `photus-system`
(stdout, timestamps locais):

```
2026-09-22 16:51:36.652 | INFO | process_pipeline:55 - Recebido upload de 1 foto(s) e texto: céu dourado ao entardecer, sensação de calma e nostalgia
2026-09-22 16:51:36.968 | INFO | process_pipeline:64 - Fotos salvas em: .../data/uploads/e623f7d9802c4ec19197fa1922efc8fa_20260922_165136
2026-09-22 16:51:39.820 | INFO | evaluation_batch_client:submit_evaluation_batch:47 - Photus UC: lote 6b5741ff-7ef8-465b-b5bf-b5b11d7eeb5c criado -> status=em_processamento, ancora=nostalgia, rota=fast_track
```

Repetido mais 2x na mesma sessão (lotes `620927ef-...` e `5e409d4a-...`),
sempre com o mesmo resultado determinístico (`ancora=nostalgia`,
`rota=fast_track`) pro mesmo texto — os IDs de lote (`6b5741ff...`) são
UUIDs reais emitidos pelo `photus-uc`, não valores mockados.

Na UI, o modal "Processando Lote" mostrou o stepper de 3 etapas
acendendo em sequência (✓ Criando Lote → spinner Analisando Photus B →
✓ Roteando), seguido da pré-visualização da rota com os badges
`[ nostalgia ]` (âncora) e `⚡ Fast Track (SBERT)` (rota) antes de fechar
sozinho. Após o fechamento, o texto inserido aparece com highlight de
âncora: a seção "Texto com âncora destacada" mostra a tag `nostalgia`
seguida da frase completa destacada (confirmado via extração de texto da
página: `nostalgia` / `céu dourado ao entardecer, sensação de calma e
nostalgia`).

Em um teste anterior na mesma sessão (antes do ajuste de cores), o mesmo
fluxo com o texto *"retrato noturno, cores frias, silêncio urbano"*
classificou como `[ distanciamento ] ⚡ Fast Track (SBERT)` — confirmando
que a âncora varia corretamente conforme o texto de entrada, não é um
valor fixo.

## Cenário 4 — Falha de conexão com o Photus B (A1 / RNF06)

`photus-b` derrubado propositalmente (`kill -9` no processo, porta 8000
parou de responder) enquanto `photus-uc` e `photus-system` continuaram no
ar. Nova submissão com 3 fotos:

- Modal ficou ~15s preso na etapa "Analisando texto no Photus B..." (tempo
  de timeout do `photus-uc` pro Photus B, `PHOTUS_B_TIMEOUT_SECONDS=15`).
- Etapa 2 do stepper virou vermelha (ícone `!`), etapa 3 ficou pendente.
- Card de exceção apareceu: badge `status: erro`, título **"⚠️ Falha de
  Conexão Photus B"**, corpo *"O motor semântico demorou a responder. Seu
  lote foi colocado em fila para nova tentativa."*, nota **"Estado 'erro'
  persistido sem travar a UI (RNF06)."**
- Botão **"Fechar"** ficou visível e, ao clicar, fechou o modal
  corretamente (confirmado — o elemento sumiu da árvore de acessibilidade
  da página depois do clique).
- O `photus-uc` respondeu **HTTP 201** mesmo com a classificação em erro
  (não propagou exceção) — comportamento consistente com o
  `TC-S2-09`/RNF06 documentado em `photus-uc/docs/testes_sprint2.md`.

`photus-b` foi religado logo em seguida e voltou a responder normalmente
(`/health` → `{"status":"ok"}`), deixando o ambiente como estava antes do
teste.

## Cenário 5 — Contador, miniaturas e limite (RF07)

Ao anexar fotos via `input.files` + evento `change`, confirmado ao vivo:

- Badge "X / 20 imagens anexadas" atualiza a cada arquivo adicionado
  (testado 1 → 2 → 3).
- Grid de miniaturas mostra a prévia real de cada imagem (cor sólida do
  PNG sintético) com o nome do arquivo sobreposto.
- Botão "Submeter Lote para Avaliação" fica desabilitado com 0 fotos e
  habilita assim que a primeira é anexada.

(O caso de 21+ fotos disparando o toast "Limite excedido" já tinha sido
verificado em sessão anterior — lógica inalterada nesta rodada.)

## Ajustes de estilo feitos nesta rodada (a pedido do usuário)

- **Bug real corrigido:** o `<label>` nativo do `gr.File` (dropzone) e do
  `gr.HighlightedText` vazava o chip lilás/roxo-claro padrão do tema
  "Soft" do Gradio (`rgb(237,233,254)` fundo, `rgb(139,92,246)` texto) —
  destoava do tema escuro. Agora usa fundo `--photus-surface-input` e
  texto `--photus-accent` (indigo), igual ao resto do card.
- **Cores mais vivas na tela de Nova Avaliação:** as dicas de exemplo
  (leigo/técnico) ganharam badges coloridos reaproveitando as mesmas cores
  das rotas do modal — `LEIGO` em verde (`fast_track`) e `TÉCNICO` em âmbar
  (`tecnico`) — puxando o mesmo fio visual da classificação. O ícone do
  dropzone e a borda no hover também passaram a usar a cor de destaque
  (`--photus-accent`) em vez de cinza neutro.
- O painel "Status do pipeline"/chat de debug (`pipeline_status`/`chatbot`)
  segue oculto por pedido anterior do usuário — mantido assim nesta
  rodada, não foi revertido.
