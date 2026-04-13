#!/usr/bin/env bash
# /data/.openclaw/workspace/openrouter.sh
# Usage: openrouter.sh <model> "<prompt>"

set -euo pipefail

DEFAULT_MODEL="anthropic/claude-opus-4.6-fast"
MODEL="${1:-$DEFAULT_MODEL}"
PROMPT="${2:-hello}"

OPENROUTER_KEY="${OPENROUTER_KEY:-}"

if [[ -z "$OPENROUTER_KEY" ]]; then
  echo "ERROR: Set OPENROUTER_KEY env var first"
  exit 1
fi

curl -sS "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_KEY" \
  -H "Content-Type: application/json" \
  --data-raw "{\"model\": \"$MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}], \"temperature\": 0.7}"