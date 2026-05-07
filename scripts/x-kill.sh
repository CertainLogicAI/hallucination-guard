#!/usr/bin/env bash
# X Posting Emergency Kill Switch
# Usage: ./x-kill.sh [reason]
# Disables all X-posting crons, clears scheduled content, locks review gate.

set -euo pipefail

REASON="${1:-Emergency stop - no reason given}"
LOGFILE="/data/.openclaw/workspace/logs/x-kill-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$(dirname "$LOGFILE")"

exec > >(tee -a "$LOGFILE") 2>&1

echo "=== X KILL SWITCH ACTIVATED ==="
echo "Time: $(date -Iseconds)"
echo "Reason: $REASON"
echo "User: ${SUDO_USER:-$USER}"
echo ""

# 1. List and remove all X-posting crons
X_CRONS=$(cd /data/.openclaw/workspace && openclaw cron list 2>/dev/null | grep -i "x-" | awk '{print $1}' || true)
if [ -n "$X_CRONS" ]; then
    echo "Removing X crons:"
    for id in $X_CRONS; do
        echo "  - $id"
        openclaw cron remove "$id" 2>/dev/null || echo "    (already removed or unknown)"
    done
else
    echo "No active X crons found."
fi

# 2. Clear scheduled tweet content
echo ""
echo "Clearing scheduled content..."
rm -f /data/.openclaw/workspace/marketing/content_output/*.md

# 3. Lock review gate
LOCK_FILE="/data/.openclaw/workspace/marketing/content_output/approved_slots.json"
echo '{"emergency_lock": true, "reason": "'"$REASON"'", "locked_at": "'"$(date -Iseconds)"'", "by": "'"${SUDO_USER:-$USER}"'"}' > "$LOCK_FILE"
echo "Review gate LOCKED."

# 4. Log to memory
MEMORY_ENTRY="
## $(date +%Y-%m-%d) — X Kill Switch Deployed

- **Time:** $(date -Iseconds)
- **Reason:** $REASON
- **Crons removed:** ${X_CRONS:-none}
- **Content cleared:** yes
- **Review gate locked:** yes
- **Log:** $LOGFILE

### Recovery Required
- [ ] Root cause fixed
- [ ] Anton approves re-enable
- [ ] Dry-run passes
- [ ] Re-enable lowest-risk cron, monitor 24h
"

echo "$MEMORY_ENTRY" >> /data/.openclaw/workspace/memory/$(date +%Y-%m-%d).md
echo "Memory log updated."

# 5. Verify silence
echo ""
echo "=== VERIFICATION ==="
REMAINING=$(cd /data/.openclaw/workspace && openclaw cron list 2>/dev/null | grep -ic "x-" || echo "0")
if [ "$REMAINING" -eq 0 ]; then
    echo "✅ All X crons cleared."
else
    echo "⚠️  $REMAINING X-pattern crons still active — investigate!"
fi

CONTENT_COUNT=$(ls /data/.openclaw/workspace/marketing/content_output/*.md 2>/dev/null | wc -l)
if [ "$CONTENT_COUNT" -eq 0 ]; then
    echo "✅ No scheduled content remaining."
else
    echo "⚠️  $CONTENT_COUNT content files still present:"
    ls /data/.openclaw/workspace/marketing/content_output/*.md 2>/dev/null
fi

echo ""
echo "=== KILL SWITCH COMPLETE ==="
echo "Log: $LOGFILE"
echo "Next: Investigate root cause. Do NOT re-enable without Anton approval."
echo ""
