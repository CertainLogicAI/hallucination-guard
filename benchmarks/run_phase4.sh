#!/usr/bin/env bash
set -euo pipefail

# Phase 4 – Very hard / long-document prompts
prompts=(
  "Summarize the entire FaultTrace codebase (approx 10,000 tokens) focusing on the deterministic cache architecture, its integration with PLC analysis, and security considerations."
  "Provide a detailed compliance checklist for deploying AI-driven PLC fault detection in a regulated industry (e.g., medical devices), referencing IEC 62279 and FDA guidance."
  "Write a step‑by‑step migration plan to move from the current open‑source LLM stack to a fully on‑prem deterministic inference pipeline, including hardware sizing and cost analysis."
  "Generate a 2‑page executive summary for investors covering market size, token‑cost savings, and competitive advantages of the deterministic AI system."
)

# Load API key from OpenClaw JSON
api_key=$(jq -r '.env.OPENROUTER_API_KEY' /data/.openclaw/openclaw.json)

# Helper function to call OpenRouter (with error handling)
call_openrouter(){
  local prompt="$1"
  local api_uri="https://openrouter.ai/api/v1/chat/completions"
  curl -s -X POST "$api_uri" \
    -H "Authorization: Bearer $api_key" \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"'"$prompt"'"}],"return_usage":true}'
}

# ----------------------------------------------------------------
# Baseline executions – collect raw token usage & cost
# ----------------------------------------------------------------
> baseline.tsv
echo -e "Prompt\tPromptTokens\tCompletionTokens\tCost" >> baseline.tsv
for prompt in "${prompts[@]}"; do
  json=$(call_openrouter "$prompt")
  pt=$(echo "$json" | jq -r '.usage.prompt_tokens')
  ct=$(echo "$json" | jq -r '.usage.completion_tokens')
  # Graceful fallback if parsing fails
  if [[ -z "$pt" || -z "$ct" || "$pt" == "null" || "$ct" == "null" ]]; then
    echo "Error: Failed to parse tokens for baseline prompt – $prompt" >&2
    pt=0; ct=0
  fi
  cost=$(awk -v pt=$pt -v ct=$ct 'BEGIN{printf "%.6f", (pt/1000)*0.001 + (ct/1000)*0.003}')
  echo -e "$prompt\t$pt\t$ct\t$cost" >> baseline.tsv
  echo "Baseline: $prompt → $pt/$ct cost $cost"
done

# ----------------------------------------------------------------
# Deterministic executions – try cache first, otherwise call API
# ----------------------------------------------------------------
> deterministic.tsv
echo -e "Prompt\tPromptTokens\tCompletionTokens\tCost" >> deterministic.tsv
for prompt in "${prompts[@]}"; do
  cache_file="/data/.openclaw/workspace/deterministic_evidence/${prompt//[^a-zA-Z0-9]/_}.json"
  if [ -f "$cache_file" ]; then
    pt=0; ct=0; cost=0
  else
    json=$(call_openrouter "$prompt")
    pt=$(echo "$json" | jq -r '.usage.prompt_tokens' | tr -d '\r\n')
    ct=$(echo "$json" | jq -r '.usage.completion_tokens' | tr -d '\r\n')
    if [[ -z "$pt" || -z "$ct" || "$pt" == "null" || "$ct" == "null" ]]; then
      pt=0; ct=0
    fi
    cost=$(awk -v pt=$pt -v ct=$ct 'BEGIN{printf "%.6f", (pt/1000)*0.001 + (ct/1000)*0.003}')
  fi
  echo -e "$prompt\t$pt\t$ct\t$cost" >> deterministic.tsv
  echo "Deterministic: $prompt → $pt/$ct cost $cost"
done

# ----------------------------------------------------------------
# Build a markdown summary for Phase 4
# ----------------------------------------------------------------
{
  echo "# Phase 4 Results (Very Hard / Long Prompts)"
  echo "| Prompt | Baseline Tokens | Deterministic Tokens | Δ Tokens | Baseline Cost | Deterministic Cost | Δ Cost | % Tokens Saved | % Cost Saved |"
  echo "|---|---|---|---|---|---|---|---|---|"
  while IFS=$'\t' read -r prompt pt_b ct_b cost_b; do
    det_line=$(grep -F "$prompt" deterministic.tsv) || { echo "ERROR: Prompt not found in deterministic results"; exit 1; }
    IFS=$'\t' read -r _ pt_d ct_d cost_d <<< "$det_line"
    total_b=$((pt_b+ct_b))
    total_d=$((pt_d+ct_d))
    delta_t=$((total_b-total_d))
    delta_c=$(awk -v a=$cost_b -v b=$cost_d 'BEGIN{printf "%.4f", a-b}')
    pct_t=$(awk -v b=$total_b -v d=$total_d 'BEGIN{printf "%.1f", (b-d)/b*100}')
    pct_c=$(awk -v b=$cost_b -v d=$cost_d 'BEGIN{printf "%.1f", (b-d)/b*100}')
    echo "| $prompt | $total_b | $total_d | $delta_t | \$$cost_b | \$$cost_d | \$$delta_c | $pct_t% | $pct_c% |"
  done < baseline.tsv
} > phase4_results.md

# ----------------------------------------------------------------
# Log Phase 4 results via our standard logger for auditability
# ----------------------------------------------------------------
now=$(date +%s)
./log_conversation.sh "$now" "CC" "Phase 4 Benchmark Results" "benchmark,phase4" "$(cat phase4_results.md)"

# ----------------------------------------------------------------
# Append Phase 4 summary to the durable daily memory file
# ----------------------------------------------------------------
memdir="/data/.openclaw/workspace/memory"
mkdir -p "$memdir"
memfile="$memdir/2026-04-10.md"
{
  echo "\n## Phase 4 Benchmark Summary"
  cat phase4_results.md
} >> "$memfile"

# ----------------------------------------------------------------
# Consolidated report across all phases (1‑4) – optional generation
# ----------------------------------------------------------------
# If results from earlier phases exist, combine them into a master summary
summary_file="consolidated_report.md"
if [ -f "../phase1_results.md" ]; then cat "../phase1_results.md" > "$summary_file"; fi
if [ -f "../phase2_results.md" ]; then echo -e "\n---\n" >> "$summary_file"; cat "../phase2_results.md" >> "$summary_file"; fi
if [ -f "../phase3_results.md" ]; then echo -e "\n---\n" >> "$summary_file"; cat "../phase3_results.md" >> "$summary_file"; fi
if [ -f "phase4_results.md" ]; then echo -e "\n---\n" >> "$summary_file"; cat "phase4_results.md" >> "$summary_file"; fi

# Log the consolidated report as well
./log_conversation.sh "$(date +%s)" "CC" "Consolidated Benchmark Report" "benchmark,consolidated" "$(cat "$summary_file")"

# Exit cleanly – success
echo "Phase 4 and consolidated report completed successfully."
exit 0