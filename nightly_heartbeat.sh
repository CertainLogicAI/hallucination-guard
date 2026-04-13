#!/bin/bash

# Heartbeat runner for nightly memory integrity check
# Retries until success (max 3 attempts, 30s apart)

SCRIPT="/data/.openclaw/workspace/integrity_scan.sh"
KG_SCRIPT="/data/.openclaw/workspace/knowledge-graph/update_kg.py"
MAX_RETRIES=3
RETRY_DELAY=30
LOG_FILE="/data/.openclaw/workspace/logs/heartbeat_integrity.log"
mkdir -p $(dirname "$LOG_FILE")

echo "=== Starting nightly memory integrity check ===" | tee -a "$LOG_FILE"

for attempt in $(seq 1 "$MAX_RETRIES"); do
  echo "Attempt $attempt of $MAX_RETRIES" | tee -a "$LOG_FILE"
  if "$SCRIPT" --full >> "$LOG_FILE" 2&& echo "SUCCESS" | tee -a "$LOG_FILE"; then
    echo "=== Nightly check completed successfully ===" | tee -a "$LOG_FILE"
    exit 0
  else
    echo "FAILED (attempt $attempt)" | tee -a "$LOG_FILE"
    if [ "$attempt" -lt "$MAX_RETRIES" ]; then
      echo "Retrying in $RETRY_DELAY seconds..." | tee -a "$LOG_FILE"
      sleep "$RETRY_DELAY"
    fi
  fi
done

echo "=== All attempts failed. Check logs for details. ===" | tee -a "$LOG_FILE"
exit 1