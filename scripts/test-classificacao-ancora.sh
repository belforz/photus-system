#!/bin/bash
# Teste guiado do fluxo "Classificar âncora semântica" (matriz de testes TC-S2-04..07).
#
# Parte 1: chama Photus B (:8000) direto, um texto representativo por âncora,
#          e confere se a âncora obtida bate com a esperada.
# Parte 2: loga em Photus UC (:8001) com um usuário de teste e cria um lote real
#          (POST /batches, texto + fotos) — o mesmo caminho que a UI Gradio usa.
#
# Fotos de calibração por âncora (Unsplash/Pexels/Wikimedia, já no repo, fora do
# Git via .gitignore) ficam em data/uploads/calib_<ancora>_<timestamp>/.
#
# Uso: ./scripts/test-classificacao-ancora.sh [PHOTUS_B_URL] [PHOTUS_UC_URL]
set -u

B_URL="${1:-http://localhost:8000}"
UC_URL="${2:-http://localhost:8001}"

echo "== Parte 1: classificação direta via Photus B ($B_URL) =="
echo

declare -a cases=(
  "vitalidade|foto de esporte com ação e movimento físico intenso, corrida, salto, adrenalina"
  "solenidade|ambiente calmo, sereno e simétrico, tudo no lugar, composição estilizada e elegante"
  "conexao|foto de rosto humano em close extremo, sorriso e olhar direto, calor humano e afeto"
  "distanciamento|cena dominada pela escuridão, lugar vazio e abandonado, sensação de solidão total"
  "simplicidade|foto comum do dia a dia, sem produção, cena de cozinha na rotina, momento espontâneo"
  "conflito|foto de confusão e desordem urbana, rua suja e multidão agitada, cena caótica e tensa"
  "nostalgia|fotografia com cara de antiga, polaroid, cores desbotadas, granulado, atmosfera retrô"
  "sublime|foto de paisagem enorme e impressionante, montanha, oceano, horizonte infinito, pôr do sol"
  "corporativo|foto profissional para linkedin, executivo sério em estúdio, fundo liso, formal"
  "noturno|foto de festa, balada à noite, amigos dançando, euforia, luzes e música eletrônica"
  "tecnico|deixa o fundo desfocado e borrado, quero bokeh forte, abertura grande, profundidade de campo rasa"
)

pass=0
fail=0
printf "%-14s %-14s %-8s %-8s %-8s %s\n" "ESPERADO" "OBTIDO" "CONF" "TECN." "FALLBACK" "STATUS"
printf '%.0s-' {1..70}; echo

for c in "${cases[@]}"; do
  IFS='|' read -r expected text <<< "$c"
  resp=$(curl -s -X POST "$B_URL/v1/categorize" -H "Content-Type: application/json" \
    -d "$(python3 -c "import json,sys; print(json.dumps({'text': sys.argv[1]}))" "$text")")
  got=$(echo "$resp" | python3 -c "import json,sys; print(json.load(sys.stdin).get('category_code','ERR'))" 2>/dev/null || echo "ERR")
  conf=$(echo "$resp" | python3 -c "import json,sys; print(f\"{json.load(sys.stdin).get('confidence',0):.3f}\")" 2>/dev/null || echo "-")
  tech=$(echo "$resp" | python3 -c "import json,sys; print(json.load(sys.stdin).get('technical'))" 2>/dev/null || echo "-")
  fb=$(echo "$resp" | python3 -c "import json,sys; print(json.load(sys.stdin).get('used_fallback'))" 2>/dev/null || echo "-")
  [ "$got" == "$expected" ] && { status="OK"; pass=$((pass+1)); } || { status="MISMATCH"; fail=$((fail+1)); }
  printf "%-14s %-14s %-8s %-8s %-8s %s\n" "$expected" "$got" "$conf" "$tech" "$fb" "$status"
done
echo
echo "Parte 1: $pass OK / $fail mismatch (de $((pass+fail)))"

echo
echo "== Parte 2: lote real via Photus UC ($UC_URL) — mesmo caminho da UI =="
echo

read -rp "Email do usuário de teste [leandro@teste.com]: " EMAIL
EMAIL="${EMAIL:-leandro@teste.com}"
read -rp "Senha [SenhaForte#123]: " SENHA
SENHA="${SENHA:-SenhaForte#123}"
read -rp "Âncora a testar (ex: vitalidade, nostalgia, noturno...) [vitalidade]: " ANCORA
ANCORA="${ANCORA:-vitalidade}"

DIR=$(ls -d data/uploads/calib_${ANCORA}_* 2>/dev/null | head -1)
if [ -z "$DIR" ]; then
  echo "Nenhuma pasta calib_${ANCORA}_* encontrada em data/uploads/. Abortando parte 2."
  exit 1
fi
echo "Usando fotos de: $DIR"

TOKEN=$(curl -s -X POST "$UC_URL/auth/login" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json,sys;print(json.dumps({'email':sys.argv[1],'senha':sys.argv[2]}))" "$EMAIL" "$SENHA")" \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "Falha no login. Confira as credenciais."
  exit 1
fi

CURL_ARGS=()
for f in $(ls "$DIR"/*.jpg "$DIR"/*.jpeg "$DIR"/*.png 2>/dev/null | head -3); do
  CURL_ARGS+=(-F "photos=@$f;type=image/jpeg")
done

resp=$(curl -s -X POST "$UC_URL/batches" \
  -H "Authorization: Bearer $TOKEN" \
  -F "input_text=quero fotos com a vibe de ${ANCORA}" \
  "${CURL_ARGS[@]}")

echo "$resp" | python3 -m json.tool
status=$(echo "$resp" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null)
echo
if [ "$status" == "erro" ]; then
  echo "Lote com status 'erro' — Photus UC não conseguiu falar com Photus B."
  echo "Confira: o photus-uc está usando a env var PHOTUS_B_BASE_URL (não PHOTUS_B_URL)?"
else
  echo "Lote criado com sucesso, status=$status."
fi
