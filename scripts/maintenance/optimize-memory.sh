#!/bin/bash
# Compress old memory files (>7 days)
find /data/.openclaw/workspace/memory -name "*.md.gz" -mtime +7 -exec gzip -k {} \;
# Clean up stale temp files
rm -f /data/.openclaw/workspace/scripts/temp-*.js
