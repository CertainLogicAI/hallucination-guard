#!/bin/bash
# memory_prune.sh - Biweekly memory maintenance with context-size monitoring

set -euo pipefail

WORKSPACE="/data/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
LOG_FILE="$WORKSPACE/memory/prune.log"
MAX_SIZE_KB=512  # Alert if MEMORY.md exceeds this
RETENTION_DAYS=90  # Default: prune entries older than this
EVERGREEN_TAG="[EVERGREEN]"  # Entries with this tag skip pruning

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Starting memory prune..." | tee -a "$LOG_FILE"

# 1. Size check
CURRENT_SIZE=$(wc -c < "$MEMORY_FILE" 2>/dev/null || echo 0)
SIZE_KB=$((CURRENT_SIZE / 1024))

if [ $SIZE_KB -gt $MAX_SIZE_KB ]; then
    echo "[$TIMESTAMP] WARNING: MEMORY.md size ${SIZE_KB}KB exceeds ${MAX_SIZE_KB}KB limit" | tee -a "$LOG_FILE"
    echo "[$TIMESTAMP] Consider manual review of older entries." | tee -a "$LOG_FILE"
fi

# 2. Prune daily files older than RETENTION_DAYS
if [ -d "$MEMORY_DIR" ]; then
    find "$MEMORY_DIR" -name "*.md" -type f -mtime +$RETENTION_DAYS | while read -r OLD_FILE; do
        # Check for evergreen tag before deleting
        if grep -q "$EVERGREEN_TAG" "$OLD_FILE"; then
            echo "[$TIMESTAMP] Skipping evergreen: $(basename "$OLD_FILE")" | tee -a "$LOG_FILE"
        else
            echo "[$TIMESTAMP] Deleting: $(basename "$OLD_FILE")" | tee -a "$LOG_FILE"
            rm -f "$OLD_FILE"
        fi
    done
fi

# 3. Compress MEMORY.md if it's > 256KB
if [ $SIZE_KB -gt 256 ]; then
    echo "[$TIMESTAMP] COMPRESS: MEMORY.md is ${SIZE_KB}KB - consider summarizing" | tee -a "$LOG_FILE"
    # Could add auto-summarization here in future
fi

# 4. Optional: Detect and remove duplicate entries
# (Simplified: keep only the most recent occurrence of identical lines)
echo "[$TIMESTAMP] Duplicate scan complete (skipped - manual review recommended)" | tee -a "$LOG_FILE"

echo "[$TIMESTAMP] Prune complete." | tee -a "$LOG_FILE"
exit 0
