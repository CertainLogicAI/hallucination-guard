#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------------
# 1.  List of test prompts (short, cache-friendly)
# ------------------------------------------------------------------
prompts=(
  "What is the capital of France?"
  "Explain the Pythagorean theorem."
  "What are the main differences between Bitcoin and Ethereum?"
  "Summarize the plot of \"The Great Gatsby\"."
  "What is the square root of 144?"
)

# ------------------------------------------------------------------
# 2.  Environment – already in /data/.openclaw/openclaw.json
# ------------------------------------------------------------------
export OPENROUTER_API_KEY=$(jq -r '.env.OPENROUTER_API_KEY' /data/.openclaw/openclaw.json)

# ------------------------------------------------------------------
# 3.  Helper: call OpenRouter directly and return usage
# ------------------------------------------------------------------
function call_openrouter() {
  local prompt="$1"
  curl -s -X POST "https://api.openrouter.ai/chat/completions" \
       -H "Authorization: Bearer $OPENROUTER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"'"$prompt"'"}],"return_usage":true}'
}

# ------------------------------------------------------------------
# 4.  Run baseline (direct OpenRouter)
# ------------------------------------------------------------------
echo "## Baseline (OpenRouter) 📇"
echo -e "Prompt\tPrompt Tokens\tCompletion Tokens\tCost (USD)" > baseline.tsv
for prompt in "${prompts[@]}"; do
  json=$(call_openrouter "$prompt")
  pt=$(echo "$json" | jq -r '.usage.prompt_tokens')
  ct=$(echo "$json" | jq -r '.usage.completion_tokens')
  cost=$(awk -v pt=$pt -v ct=$ct 'BEGIN{printf "%.6f", (pt/1000)*0.001 + (ct/1000)*0.003}')
  echo -e "$prompt\t$pt\t$ct\t$cost" >> baseline.tsv
  echo "$prompt  →  $pt / $ct  (cost $cost)"
done

# ------------------------------------------------------------------
# 5.  Run deterministic wrapper (cache fallback + DHI)
# ------------------------------------------------------------------
echo
echo "## Deterministic (cache ➜ DHI) 📊"
echo -e "Prompt\tPrompt Tokens\tCompletion Tokens\tCost (USD)" > deterministic.tsv
for prompt in "${prompts[@]}"; do
  cache_file="/data/.openclaw/workspace/deterministic_evidence/${prompt//[^a-zA-Z0-9]/_}.json"
  if [ -f "$cache_file" ]; then
    pt=0; ct=0; cost=0
  else
    json=$(call_openrouter "$prompt")
    pt=$(echo "$json" | jq -r '.usage.prompt_tokens')
    ct=$(echo "$json" | jq -r '.usage.completion_tokens')
    cost=$(awk -v pt=$pt -v ct=$ct 'BEGIN{printf "%.6f", (pt/1000)*0.001 + (ct/1000)*0.003}')
  fi
  echo -e "$prompt\t$pt\t$ct\t$cost" >> deterministic.tsv
  echo "$prompt  →  $pt / $ct  (cost $cost)"
done

# ------------------------------------------------------------------
# 6.  Summary table (Markdown)
# ------------------------------------------------------------------
echo
echo "# Comparison Table"
echo
echo "| Prompt | Baseline tokens | Deterministic tokens | Δ tokens | Baseline cost | Deterministic cost | Δ cost |"
echo "|---|---|---|---|---|---|---|"

while IFS=$'\t' read -r prompt pt_b ct_b cost_b; do
  tok_b=$((pt_b+ct_b))
  det_line=$(grep -F "$prompt" deterministic.tsv || true)
  IFS=$'\t' read -r _ pt_d ct_d cost_d <<< "$det_line"
  tok_d=$((pt_d+ct_d))
  delta_tok=$((tok_b - tok_d))
  delta_cost=$(awk -v a=$cost_b -v b=$cost_d 'BEGIN{printf "%.4f", a-b}')
  echo "| $prompt | $tok_b | $tok_d | $delta_tok | \$$cost_b | \$$cost_d | \$$delta_cost |"
done < baseline.tsv > table.md

cat table.md