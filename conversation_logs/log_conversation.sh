#!/bin/bash
# Simple logger script for conversation logs
# Usage: ./log_conversation.sh <message_id> "<sender>" "<title>" "<tags>" "<content>"

set -e

MESSAGE_ID=$1
SENDER=$2
TITLE=$3
TAGS=$4
CONTENT=$5

# Default fields
SENDER_ID="1381429689"
USERNAME="ForCryptoClearly"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

LOGFILE="/data/.openclaw/workspace/conversation_logs/${MESSAGE_ID}.md"

cat <<EOF > "${LOGFILE}"
---
message_id: ${MESSAGE_ID}
sender_id: ${SENDER_ID}
sender: ${SENDER}
username: ${USERNAME}
title: ${TITLE}
tags: ${TAGS}
date: ${DATE}
time: ${TIME}
---
## Content

${CONTENT}
EOF

echo "Log entry created for ${MESSAGE_ID}"