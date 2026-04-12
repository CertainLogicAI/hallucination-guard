#!/bin/bash
# Log capture script
# Accepts arguments: msg_id sender title tags content
# It writes a markdown file in conversation_logs/
# The script writes a markdown file with a header and the content.

# Hallucination guard – reject empty/whitespace generated_text
if [ -z "$(echo "$5" | tr -d '[:space:]')" ]; then
    echo "ERROR: Generated text is empty or whitespace – aborting logging." >&2
    exit 1
fi

# Variables
msg_id="$1"
sender="$2"
title="$3"
tags="$4"
content="$5"

# Default variables
PID=$PPID
SENDER_ID="1381429689"
USERNAME="ForCryptoClearly"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

LOGFILE="/data/.openclaw/workspace/conversation_logs/${msg_id}.md"

cat <<EOF > "${LOGFILE}"
---
message_id: ${msg_id}
sender_id: ${SENDER_ID}
sender: ${sender}
username: ${USERNAME}
title: ${title}
tags: ${tags}
date: ${DATE}
time: ${TIME}
---
## Content

${content}
EOF

echo "Log entry created for ${msg_id}"