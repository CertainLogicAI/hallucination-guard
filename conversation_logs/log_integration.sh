#!/usr/bin/env bash
set -euo pipefail
# --------------------------------------------------------------
# Log‑Memory Integration – reliable, self‑healing observer
# --------------------------------------------------------------

# ---- CONFIG --------------------------------------------------
LOG_DIR="/data/.openclaw/workspace/conversation_logs"
MEMORY_ROOT="/data/.openclaw/workspace/memory"
INDEX_DB="${MEMORY_ROOT}/indices/log_index.db"
MEMORY_FILE="${MEMORY_ROOT}/MEMORY.md"
GAP_FILE="${MEMORY_ROOT}/gaps.md"
ARCHIVE_ROOT="${MEMORY_ROOT}/archive"
mkdir -p "$MEMORY_ROOT" "$ARCHIVE_ROOT" "$(dirname "$INDEX_DB")"

# ---- INITIALISE SQLITE INDEX (auto-creates on first run) ----
if [ ! -f "$INDEX_DB" ]; then
    /data/linuxbrew/.linuxbrew/bin/sqlite3 "$INDEX_DB" <<SQL
CREATE TABLE logs (
    message_id TEXT PRIMARY KEY,
    filename   TEXT,
    title      TEXT,
    tags       TEXT,
    timestamp  TEXT,
    created_at TEXT
);
SQL
fi

# Function: log an error (will be appended to gaps.md)
log_error() { echo "$(date +%s) – $1" >> "$GAP_FILE"; }

# Function: safely add a new log entry to memory
add_to_memory() {
    local msg_id="$1" title="$2" tags="$3" date="$4" time="$5" body="$6"

    # Build entry
    cat <<EOF >> "$MEMORY_FILE"
## Log Entry – $date $time UTC – ID $msg_id
**Title:** $title
**Tags:** $tags
**Message‑ID:** $msg_id
**Timestamp:** $date $time UTC
---
**Content**
$body
EOF

    # Add a tiny index line to MEMORY.md for quick scan
    echo "- Log $msg_id – $title  (see $MEMORY_FILE)" >> "$MEMORY_FILE"

    # Store in SQLite index
    /data/linuxbrew/.linuxbrew/bin/sqlite3 "$INDEX_DB" <<SQL
INSERT OR REPLACE INTO logs
(message_id, filename, title, tags, timestamp, created_at)
VALUES (
    '$msg_id', '$msg_id.md', '$title', '$tags', '$date $time UTC', '$(date +%s)'
);
SQL
}

# Function: archive a daily file after 30 days
archive_daily_log() {
    local daily="$1"
    local yr=$(date -r "$daily" +%Y)
    local m=$(date -r "$daily" +%m)
    local archive_dir="${ARCHIVE_ROOT}/${yr}-${m}"
    mkdir -p "$archive_dir"
    gzip -c "$daily" > "${archive_dir}/${yr}-${m}.01-31.md.gz"
    rm -f "$daily"
}

# Main watch loop
while true; do
    # 1️⃣ Find every *.md that is *newer* than last scan (cached in state file)
    STATE_FILE="${LOG_DIR}/.state"
    LAST_SEEN=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
    NOW=$(date +%s)

    # Find files newer than $LAST_SEEN
    mapfile -t NEW_FILES < <(find "$LOG_DIR" -maxdepth 1 -type f -name "*.md" -newer "$STATE_FILE" 2>/dev/null || true)

    for f in "${NEW_FILES[@]}"; do
        # Skip if file disappeared meanwhile
        [[ ! -f "$f" ]] && continue

        # ---- Extract data -------------------------------------------------
        MSG_ID="${f##*/}"
        MSG_ID="${MSG_ID%.md}"
        TITLE=$(awk -F: '/^title:/ {print $2}' "$f" | sed 's/[[:space:]]*$//')
        TAGS=$(awk -F: '/^tags:/ {print $2}' "$f" | sed 's/[[:space:]]*$//')
        DATE=$(awk -F: '/^date:/ {print $2}' "$f" | sed 's/[[:space:]]*$//')
        TIME=$(awk -F: '/^time:/ {print $2}' "$f" | sed 's/[[:space:]]*$//')
        BODY=$(awk '/^\#\#\# Content$/{flag=1} flag' "$f" | tail -n +2)

        # ---- Store in index & memory -------------------------------
        add_to_memory "$MSG_ID" "$TITLE" "$TAGS" "$DATE" "$TIME" "$BODY"

        # ---- Prune old active logs (keep only 7‑day window) ----------
        FILE_AGE_DAYS=$(( ( $(date +%s) - $(stat -c %Y "$f") ) / 86400 ))
        if [ "$FILE_AGE_DAYS" -gt 7 ]; then
            # Move to archive instead of delete to keep safety copy
            mv "$f" "${f}.archive"
        fi
    done

    # Update state file so next iteration only sees newer files
    echo "$NOW" > "$STATE_FILE"

    # Optional: attempt to archive any daily file older than 30 days
    # (run once per loop; cheap)
    DAILY_FILE="${MEMORY_ROOT}/$(date -d '30 days ago' +%Y-%m-%d)-logs.md"
    if [[ -f "$DAILY_FILE" ]]; then
        archive_daily_log "$DAILY_FILE"
    fi

    # Sleep 5 seconds before next poll
    sleep 5
done