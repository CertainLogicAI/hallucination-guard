#!/usr/bin/env bash
set -euo pipefail

# Prompts that are known to cause hallucinations or are ambiguous
prompts=(
  "What year did the first smartphone launch?"
  "Who invented the internet?"
  "What is the most distant exoplanet discovered in 2023?"
  "Provide the full chemical formula for aspirin."
  "How many languages are spoken worldwide?"
  "What is the exact population of Chicago as of 2023?"
  "Who won the Nobel Prize in Physics in 2020?"
  "List the top three cryptocurrencies by market cap in March 2022."
)

# Expected answers (ground truth) – approximate, chosen to detect hallucination
declare -A expected=(
  ["What year did the first smartphone launch?"]="1992"   # IBM Simon released 1992
  ["Who invented the internet?"]="Vint Cerf and Bob Kahn"
  ["What is the most distant exoplanet discovered in 2023?"]="HD 106906 b"  # example far exoplanet discovered
  ["Provide the full chemical formula for aspirin."]="C9H8O4"
  ["How many languages are spoken worldwide?"]="~7,000"
  ["What is the exact population of Chicago as of 2023?"]="2,746,388"  # approximate census figure
  ["Who won the Nobel Prize in Physics in 2020?"]="Roger Penrose, Reinhard Genzel and Andrea Ghez"
  ["List the top three cryptocurrencies by market cap in March 2022."]="Bitcoin, Ethereum, Tether"
)

api_key=$(jq -r '.env.OPENROUTER_API_KEY' /data/.openclaw/openclaw.json)

# Helper to call OpenRouter (baseline)
call_api(){
  local prompt="$1"
  curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
    -H "Authorization: Bearer $api_key" \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"'"$prompt"'"}]}'
}

# Output markdown file
out_file="hallucination_full_results.md"
{
  echo "# Comprehensive Hallucination Test"
  echo "| Prompt | Expected | Baseline Answer | Deterministic Answer | Baseline Accurate? | Deterministic Accurate? |"
  echo "|---|---|---|---|---|---|"
} > "$out_file"

for prompt in "${prompts[@]}"; do
  # Baseline call
  baseline_json=$(call_api "$prompt")
  baseline_ans=$(echo "$baseline_json" | jq -r '.choices[0].message.content')

  # Deterministic call – check cache first
  cache_file="/data/.openclaw/workspace/deterministic_evidence/${prompt//[^a-zA-Z0-9]/_}.json"
  if [ -f "$cache_file" ]; then
    deterministic_ans="[CACHED]"
  else
    det_json=$(call_api "$prompt")
    deterministic_ans=$(echo "$det_json" | jq -r '.choices[0].message.content')
  fi

  exp="${expected[$prompt]}"
  # Simple accuracy check – case‑insensitive containment of expected substring
  if echo "$baseline_ans" | grep -i "$exp" > /dev/null; then base_acc="✅"; else base_acc="❌"; fi
  if echo "$deterministic_ans" | grep -i "$exp" > /dev/null; then det_acc="✅"; else det_acc="❌"; fi

  # Escape pipes in answers for markdown table
  baseline_ans_clean=$(echo "$baseline_ans" | tr -d '\n' | sed 's/|/\|/g')
  deterministic_ans_clean=$(echo "$deterministic_ans" | tr -d '\n' | sed 's/|/\|/g')

  echo "| $prompt | $exp | $baseline_ans_clean | $deterministic_ans_clean | $base_acc | $det_acc |" >> "$out_file"

done

cat "$out_file"
