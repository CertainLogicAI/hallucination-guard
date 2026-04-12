#!/bin/bash
# cleanup_logs.sh - Clean up old logs and archives

# Configuration
LOG_DIR="/data/.openclaw/workspace/conversation_logs"
BACKUP_DIR="/data/.openclaw/workspace/backup_local"
ARCHIVE_DIR="$BACKUP_DIR/archive"

# Cleanup old logs (older than 7 days)
echo "Cleaning up old logs..."
find "$LOG_DIR" -name "*.md" -mtime +7 -exec rm -f {} \;
echo "Old logs cleaned up."

# Cleanup old archives (older than 30 days)
echo "Cleaning up old archives..."
find "$ARCHIVE_DIR" -name "*.tar.gz" -mtime +30 -exec rm -f {} \;
echo "Old archives cleaned up."

# Cleanup old daily backups (older than 7 days)
echo "Cleaning up old daily backups..."
find "$BACKUP_DIR" -name "*.md" -mtime +7 -exec rm -f {} \;
echo "Old daily backups cleaned up."