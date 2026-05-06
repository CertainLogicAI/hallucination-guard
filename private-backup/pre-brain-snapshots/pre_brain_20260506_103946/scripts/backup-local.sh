#!/bin/bash

# Create timestamped backup
BACKUP_DIR="/data/backups/openclaw-$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

# Copy critical files
rsync -av --delete /data/.openclaw/workspace/ "$BACKUP_DIR/" 2>/dev/null

# Compress the backup
tar czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

# Clean up old backups (keep last 7 days)
find /data/backups -maxdepth 1 -type d -name "openclaw-*" -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR"