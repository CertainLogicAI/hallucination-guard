#!/usr/bin/env bash
set -euo pipefail

# Phase 3 – Hard complexity prompts
prompts=(
  "Analyze a large PLC compatibility log for common fault patterns and recommend firmware updates."
  "Design an AI-driven fault prediction model for SCADA systems using historical FaultTrace data."
  "Generate audit-ready documentation for a blockchain-based procurement system, including compliance with GDPR and SEC regulations."
  "Provide a detailed technical report on optimizing token transfers in a high-frequency DeFi protocol."
)

# Load OpenRouter key
api_key=$(jq -r '.env.OPENROUTER_API_KEY' /data/.openclaw/openclaw.json)

# Helper to call OpenRouter and get usage json
call_openrouter(){
  local prompt="$1"
  curl -s -X POST "https://api.openrouter.ai/chat/completions" \
    -H "Authorization: Bearer $api_key" \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"'"$prompt"'"}],"return_usage":true}'
}

# Baseline
echo "## Baseline (OpenRouter)" > baseline.tsv
echo -e "Prompt\tPromptTokens\tCompletionTokens\tCost" >> baseline.tsv
for p in "${prompts[@]}"; do
  json=$(call_openrouter "$p")
  pt=$(echo "$json" | jq -r '.usage.prompt_tokens')
  ct=$(echo "$json" | jq -r '.usage.completion_tokens')
  cost=$(awk -v pt=$pt -v ct=$ct 'BEGIN{printf "%.6f", (pt/1000)*0.001 + (ct/1000)*0.003}')
  echo -e "$p\t$pt\t$ct\t$cost" >> baseline.tsv
  echo "Baseline: $p → $pt/$ct cost $cost"
done

# Deterministic (cache + DHI)
echo "## Deterministic (cache)" > deterministic.tsv
echo -e "Prompt\tPromptTokens\tCompletionTokens\tCost" >> deterministic.tsv
for p in "${prompts[@]}"; do
  cache_file="/data/.openclaw/workspace/deterministic_evidence/${p//[^a-zA-Z0-9]/_}.json"
  if [ -f "$cache_file" ]; then
    pt=0; ct=0; cost=0
  else
    json=$(call_openrouter "$p")
    pt=$(echo "$json" | jq -r '.usage.prompt_tokens')
    ct=$(echo "$json" | jq -r '.usage.completion_tokens')
    cost=$(awk -v pt=$pt -v ct=$ct 'BEGIN{printf "%.6f", (pt/1000)*0.001 + (ct/1000)*0.003}')
  fi
  echo -e "$p\t$pt\t$ct\t$cost" >> deterministic.tsv
  echo "Deterministic: $p → $pt/$ct cost $cost"
done

# Summary table
{
  echo "# Phase 3 Results (Hard Complexity)"
  echo "| Prompt | Baseline Tokens | Deterministic Tokens | Δ Tokens | Baseline Cost | Deterministic Cost | Δ Cost | % Token Savings | % Cost Savings |"
  echo "|---|---|---|---|---|---|---|---|---|"
  while IFS=$'\t' read -r prompt pt_b ct_b cost_b; do
    total_b=$((pt_b+ct_b))
    det_line=$(grep -F "$prompt" deterministic.tsv)
    IFS=$'\t' read -r _ pt_d ct_d cost_d <<< "$det_line"
    total_d=$((pt_d+ct_d))
    delta_t=$((total_b-total_d))
    delta_c=$(awk -v a=$cost_b -v b=$cost_d 'BEGIN{printf "%.4f", a-b}')
    pct_t=$(awk -v b=$total_b -v d=$total_d 'BEGIN{printf "%.1f", (b-d)/b*100}')
    pct_c=$(awk -v b=$cost_b -v d=$cost_d 'BEGIN{printf "%.1f", (b-d)/b*100}')
    echo "| $prompt | $total_b | $total_d | $delta_t | \$$cost_b | \$$cost_d | \$$delta_c | $pct_t% | $pct_c% |"
  done < baseline.tsv
} > phase3_results.md

# Log the result file via our log_conversation script for record
time=$(date +%H:%M:%S)
date=$(date +%Y-%m-%d)
msg_id=$(date +%s)
./log_conversation.sh "$msg_id" "CC" "Phase 3 Benchmark Results" "benchmark,phase3" "$(cat phase3_results.md)"
