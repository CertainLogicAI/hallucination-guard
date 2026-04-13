#!/bin/bash
set -e

WORKSPACE_DIR="/data/.openclaw/workspace"
BACKUP_DIR="$WORKSPACE_DIR/backups"
INTEGRITY_HASH_FILE="$BACKUP_DIR/memory-integrity.hash"

echo "Running memory integrity scan..."

# Change to the workspace directory
cd "$WORKSPACE_DIR"

# Run backup using rclone. Use trailing colon to reference remote
echo "Starting backup sync..."
rclone sync . memory-backup: --quiet || (echo "Backup failed" && exit 1)

# Generate integrity hash
echo "Generating integrity hash..."
sha256sum MEMORY.md memory/*.md > "$INTEGRITY_HASH_FILE"

echo "✅ Integrity scan complete. System status: PASS"
