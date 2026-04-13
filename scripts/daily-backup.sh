#!/bin/bash
# Daily backup of workspace to /data/.openclaw/backups/
# Excludes node_modules, __pycache__, and scraper data
set -euo pipefail

BACKUP_DIR="/data/.openclaw/backups"
DATE=$(date +%Y-%m-%d)
BACKUP_FILE="${BACKUP_DIR}/workspace-${DATE}.tar.gz"

mkdir -p "$BACKUP_DIR"

# Remove backups older than 7 days
find "$BACKUP_DIR" -name "workspace-*.tar.gz" -mtime +7 -delete 2>/dev/null || true

# Create compressed backup excluding large/rebuilable dirs
cd /data/.openclaw/workspace
tar czf "$BACKUP_FILE" \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='projects/plc-analyzer/scraper/data' \
  --exclude='projects/plc-analyzer/app/landing/node_modules' \
  --exclude='projects/plc-analyzer/app/app' \
  --exclude='*.tar.gz' \
  --exclude='.git/objects/pack' \
  . 2>/dev/null

SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup complete: ${BACKUP_FILE} (${SIZE})"
