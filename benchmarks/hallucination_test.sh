#!/usr/bin/env bash
set -euo pipefail

# Hallucination test prompts (known facts)
prompts=(
  "What is the capital of France?"
  "Who wrote 'Romeo and Juliet'?"
  "What year did World War II end?"
  "What is the chemical symbol for gold?"
  "How many planets are in our solar system?"
)

api_key=$(jq -r '.env.OPENROUTER_API_KEY' /data/.openclaw/openclaw.json)

# Expected answers (ground truth)
declare -A answers=(
  ["What is the capital of France?"]="Paris"
  ["Who wrote 'Romeo and Juliet'?"]="William Shakespeare"
  ["What year did World War II end?"]="1945"
  ["What is the chemical symbol for gold?"]="Au"
  ["How many planets are in our solar system?"]="8"
)

echo "# Hallucination Test Results" > hallucination_results.md
echo "| Prompt | Expected | Baseline Answer | Deterministic Answer | Baseline Accurate? | Deterministic Accurate? |" >> hallucination_results.md
echo "|---|---|---|---|---|---|" >> hallucination_results.md

for prompt in "${prompts[@]}"; do
  # Baseline call
  baseline=$(curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
    -H "Authorization: Bearer $api_key" \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"'"$prompt"'"}]}' | jq -r '.choices[0].message.content')
  
  # Deterministic call (cache check + fallback)
  cache_file="/data/.openclaw/workspace/deterministic_evidence/${prompt//[^a-zA-Z0-9]/_}.json"
  if [ -f "$cache_file" ]; then
    deterministic="[CACHED - see cache]"
  else
    deterministic=$(curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
      -H "Authorization: Bearer $api_key" \
      -H "Content-Type: application/json" \
      -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"'"$prompt"'"}]}' | jq -r '.choices[0].message.content')
  fi
  
  expected="${answers[$prompt]}"
  
  # Simple accuracy check (case-insensitive contains)
  if echo "$baseline" | grep -qi "$expected"; then base_acc="✅"; else base_acc="❌"; fi
  if echo "$deterministic" | grep -qi "$expected"; then det_acc="✅"; else det_acc="❌"; fi
  
  echo "| $prompt | $expected | $baseline | $deterministic | $base_acc | $det_acc |" >> hallucination_results.md
done

echo "Hallucination test complete."
cat hallucination_results.md