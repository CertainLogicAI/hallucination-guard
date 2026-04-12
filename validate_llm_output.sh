#!/usr/bin/env bash
set -euo pipefail

# Usage: validate_llm_output.sh "<prompt>" "<answer>"
# Returns "VALID" or "INVALID"

prompt="$1"
answer="$2"

# Helper: lower‑case both strings for case‑insensitive matching
lc_prompt=$(echo "$prompt" | tr '[:upper:]' '[:lower:]')
lc_answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]')

# Validation rules – simple keyword/phrase checks for each regulatory domain
case "$lc_prompt" in
  *fda*)
    if [[ "$lc_answer" =~ "21 cfr part" ]] || [[ "$lc_answer" =~ "fda" ]]; then
      echo "VALID"
    else
      echo "INVALID"
    fi
    ;;
  *iec*62304*)
    if [[ "$lc_answer" =~ "software lifecycle" ]] || [[ "$lc_answer" =~ "process" ]]; then
      echo "VALID"
    else
      echo "INVALID"
    fi
    ;;
  *gdpr*)
    if [[ "$lc_answer" =~ "article 22" ]] || [[ "$lc_answer" =~ "automated decision" ]]; then
      echo "VALID"
    else
      echo "INVALID"
    fi
    ;;
  *nist*)
    if [[ "$lc_answer" =~ "identify" ]] && [[ "$lc_answer" =~ "protect" ]] && [[ "$lc_answer" =~ "detect" ]] && [[ "$lc_answer" =~ "respond" ]] && [[ "$lc_answer" =~ "recover" ]]; then
      echo "VALID"
    else
      echo "INVALID"
    fi
    ;;
  *iso*27001*)
    if [[ "$lc_answer" =~ "control" ]] || [[ "$lc_answer" =~ "a.18.2" ]]; then
      echo "VALID"
    else
      echo "INVALID"
    fi
    ;;
  *sec*)
    if [[ "$lc_answer" =~ "disclosure" ]] || [[ "$lc_answer" =~ "investment advice" ]]; then
      echo "VALID"
    else
      echo "INVALID"
    fi
    ;;
  *iec*62443*)
    if [[ "$lc_answer" =~ "security" ]] && [[ "$lc_answer" =~ "level" ]]; then
      echo "VALID"
    else
      echo "INVALID"
    fi
    ;;
  *eu*ai*act*)
    if [[ "$lc_answer" =~ "high-risk" ]] && [[ "$lc_answer" =~ "healthcare" ]]; then
      echo "VALID"
    else
      echo "INVALID"
    fi
    ;;
  *)
    echo "INVALID"
    ;;
esac