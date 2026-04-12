# Conversation Logging System

## Overview
This directory contains automated logs of all chat interactions. Each conversation is saved as a Markdown file with a structured header and content.

## File Format
All log files follow this structure:

```markdown
---
message_id: <unique_id>
sender_id: <user_id>
sender: <sender_label>
username: <username>
title: <conversation_title>
tags: <comma_separated_tags>
date: <YYYY-MM-DD>
time: <HH:MM:SS>
---
## Content

<conversation_content>
```

## Logging Script
The script `/data/.openclaw/workspace/conversation_logs/log_conversation.sh` is used to create new log entries.

### Usage
```bash
./log_conversation.sh <message_id> "<sender>" "<title>" "<tags>" "<content>"
```

### Example
```bash
./log_conversation.sh 9025 "Alex" "Test Log" "test,logging" "This is a test log entry to verify the logging system works correctly."
```

## Configuration
- **Default sender**: Alex
- **Default username**: ForCryptoClearly
- **Default sender_id**: 1381429689

## Best Practices
- Use unique message IDs for each log entry
- Keep tags comma-separated and without spaces
- Ensure content is UTF-8 encoded
- Verify log creation with `ls -la *.md` after running the script

## Error Handling
The script will fail with a descriptive error if:
- Required arguments are missing
- File permissions are insufficient
- Path resolution fails

After creating a log, the console will display: `Log entry created for <message_id>`