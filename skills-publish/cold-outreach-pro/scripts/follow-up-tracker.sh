#!/usr/bin/env bash
# Follow-up Tracker — manages outreach pipeline state
# Usage: 
#   ./follow-up-tracker.sh init [output-file]      — create new tracker
#   ./follow-up-tracker.sh add <name> <email> [file] — add prospect
#   ./follow-up-tracker.sh status [file]            — show pipeline summary
#   ./follow-up-tracker.sh due [file]               — show overdue follow-ups

set -uo pipefail

ACTION="${1:?Usage: follow-up-tracker.sh <init|add|status|due> [args]}"
DEFAULT_FILE="workspace/artifacts/outreach-pipeline.md"

case "$ACTION" in
  init)
    OUTPUT="${2:-$DEFAULT_FILE}"
    mkdir -p "$(dirname "$OUTPUT")"
    cat > "$OUTPUT" << 'TRACKER'
# Outreach Pipeline
**Created:** DATE_PLACEHOLDER
**Last Updated:** DATE_PLACEHOLDER

## Active Prospects

| # | Name | Email | Company | Stage | Last Touch | Next Action | Due Date | Notes |
|---|------|-------|---------|-------|------------|-------------|----------|-------|
| 1 | | | | Researching | | | | |

## Stage Definitions
| Stage | Meaning | Next Step |
|-------|---------|-----------|
| Researching | Gathering intel, not yet contacted | Send Touch 1 |
| Touch 1 Sent | Cold email sent | Wait 3 days → Touch 2 |
| Touch 2 Sent | Follow-up sent | Wait 2 days → Touch 3 |
| Touch 3 Sent | LinkedIn connection/DM | Wait 3 days → Touch 4 |
| Touch 4 Sent | Value bomb sent | Wait 6 days → Touch 5 |
| Touch 5 Sent | Breakup email sent | Wait 7 days → Archive |
| Replied | Got a response | Respond within 24hrs |
| Meeting Set | Call/demo scheduled | Prepare + show up |
| Won | Converted | Deliver + ask for referral |
| Lost | Said no or ghosted | Archive, revisit in 90 days |
| Nurture | Not now, but interested | Monthly check-in |

## Pipeline Stats
- **Total prospects:** 0
- **Active (Touch 1-5):** 0
- **Replied:** 0
- **Meetings set:** 0
- **Won:** 0
- **Lost:** 0
- **Reply rate:** 0%
- **Meeting rate:** 0%

## Weekly Review Checklist
- [ ] All overdue follow-ups sent
- [ ] New prospects added (target: 10/week)
- [ ] Pipeline stats updated
- [ ] A/B test results reviewed
- [ ] Lost prospects analyzed (why?)
- [ ] Won prospects: asked for referral?

## Notes & Learnings
<!-- What's working, what's not, patterns you notice -->

TRACKER
    sed -i "s/DATE_PLACEHOLDER/$(date +%Y-%m-%d)/g" "$OUTPUT"
    echo "✅ Pipeline tracker created: $OUTPUT"
    ;;

  add)
    NAME="${2:?Usage: follow-up-tracker.sh add <name> <email> [file]}"
    EMAIL="${3:?Missing email}"
    FILE="${4:-$DEFAULT_FILE}"
    if [ ! -f "$FILE" ]; then
      echo "❌ Tracker not found: $FILE — run 'init' first"
      exit 1
    fi
    # Count existing prospects to get next number
    COUNT=$(grep -c "^| [0-9]" "$FILE" 2>/dev/null || echo "0")
    NEXT=$((COUNT + 1))
    # Insert new row after the header row
    sed -i "/^| # | Name/a | $NEXT | $NAME | $EMAIL | | Researching | — | Research + send Touch 1 | $(date -d '+1 day' +%Y-%m-%d 2>/dev/null || date -v+1d +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d) | |" "$FILE"
    echo "✅ Added prospect #$NEXT: $NAME ($EMAIL)"
    ;;

  status)
    FILE="${2:-$DEFAULT_FILE}"
    if [ ! -f "$FILE" ]; then
      echo "❌ Tracker not found: $FILE"
      exit 1
    fi
    echo "=== Pipeline Status ==="
    TOTAL=$(grep -c "^| [0-9]" "$FILE" 2>/dev/null || echo "0")
    ACTIVE=$(grep -c "Touch [1-5] Sent" "$FILE" 2>/dev/null || echo "0")
    REPLIED=$(grep -c "Replied" "$FILE" 2>/dev/null || echo "0")
    MEETINGS=$(grep -c "Meeting Set" "$FILE" 2>/dev/null || echo "0")
    WON=$(grep -c "Won" "$FILE" 2>/dev/null || echo "0")
    echo "Total: $TOTAL | Active: $ACTIVE | Replied: $REPLIED | Meetings: $MEETINGS | Won: $WON"
    if [ "$TOTAL" -gt 0 ] && [ "$REPLIED" -gt 0 ]; then
      RATE=$((REPLIED * 100 / TOTAL))
      echo "Reply rate: ${RATE}%"
    fi
    ;;

  due)
    FILE="${2:-$DEFAULT_FILE}"
    if [ ! -f "$FILE" ]; then
      echo "❌ Tracker not found: $FILE"
      exit 1
    fi
    TODAY=$(date +%Y-%m-%d)
    echo "=== Overdue Follow-ups (as of $TODAY) ==="
    grep "^| [0-9]" "$FILE" | while IFS='|' read -r _ num name email company stage lasttouch nextaction duedate notes _; do
      duedate=$(echo "$duedate" | xargs)
      name=$(echo "$name" | xargs)
      stage=$(echo "$stage" | xargs)
      if [ -n "$duedate" ] && [[ "$duedate" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] && [[ "$duedate" < "$TODAY" || "$duedate" == "$TODAY" ]]; then
        echo "⏰ $name ($stage) — due: $duedate"
      fi
    done
    ;;

  *)
    echo "Usage: follow-up-tracker.sh <init|add|status|due> [args]"
    exit 1
    ;;
esac
