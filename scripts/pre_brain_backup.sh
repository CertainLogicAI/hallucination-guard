#!/usr/bin/env bash
# Pre-Brain Backup — Complete workspace snapshot before brain operations
# This is the "nuclear option" backup — everything before the brain touches it

set -euo pipefail

WORKSPACE="/data/.openclaw/workspace"
BACKUP_BASE="$WORKSPACE/private-backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PRE_BRAIN_DIR="$BACKUP_BASE/pre-brain-snapshots"

echo "=== PRE-BRAIN BACKUP ==="
echo "Timestamp: $TIMESTAMP"
echo "Workspace: $WORKSPACE"
echo "Backup: $PRE_BRAIN_DIR"
echo

mkdir -p "$PRE_BRAIN_DIR"

# What to backup (everything except noise)
BACKUP_NAME="pre_brain_$TIMESTAMP"
BACKUP_PATH="$PRE_BRAIN_DIR/$BACKUP_NAME"

mkdir -p "$BACKUP_PATH"

echo "[1/6] Backing up docs/..."
cp -r "$WORKSPACE/docs" "$BACKUP_PATH/"

echo "[2/6] Backing up scripts/..."
cp -r "$WORKSPACE/scripts" "$BACKUP_PATH/"

echo "[3/6] Backing up memory/..."
cp -r "$WORKSPACE/memory" "$BACKUP_PATH/"

echo "[4/6] Backing up config files..."
cp "$WORKSPACE/.env" "$BACKUP_PATH/" 2>/dev/null || true
cp "$WORKSPACE/requirements.txt" "$BACKUP_PATH/" 2>/dev/null || true
cp "$WORKSPACE/HEARTBEAT.md" "$BACKUP_PATH/" 2>/dev/null || true
cp "$WORKSPACE/SOUL.md" "$BACKUP_PATH/" 2>/dev/null || true
cp "$WORKSPACE/USER.md" "$BACKUP_PATH/" 2>/dev/null || true
cp "$WORKSPACE/IDENTITY.md" "$BACKUP_PATH/" 2>/dev/null || true
cp "$WORKSPACE/MEMORY.md" "$BACKUP_PATH/" 2>/dev/null || true
cp "$WORKSPACE/AGENTS.md" "$BACKUP_PATH/" 2>/dev/null || true
cp "$WORKSPACE/TOOLS.md" "$BACKUP_PATH/" 2>/dev/null || true

echo "[5/6] Backing up company-brain source (not data)..."
cp -r "$WORKSPACE/company-brain" "$BACKUP_PATH/" 2>/dev/null || true
rm -rf "$BACKUP_PATH/company-brain/node_modules" 2>/dev/null || true

echo "[6/6] Creating compressed archive..."
cd "$PRE_BRAIN_DIR"
tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME/"

# Checksum
sha256sum "$BACKUP_NAME.tar.gz" > "$BACKUP_NAME.sha256"

# Size
SIZE=$(du -sh "$BACKUP_NAME.tar.gz" | cut -f1)

echo
echo "=== PRE-BRAIN BACKUP COMPLETE ==="
echo "Archive: $PRE_BRAIN_DIR/$BACKUP_NAME.tar.gz"
echo "Size: $SIZE"
echo "Verify: sha256sum -c $PRE_BRAIN_DIR/$BACKUP_NAME.sha256"
echo
echo "To restore:"
echo "  cd /tmp && tar -xzf $PRE_BRAIN_DIR/$BACKUP_NAME.tar.gz"
echo
echo "Contents:"
ls -lh "$BACKUP_PATH" | head -20

# Keep only last 10 pre-brain snapshots
echo
echo "Cleanup: Keeping last 10 snapshots..."
cd "$PRE_BRAIN_DIR"
ls -t *.tar.gz 2>/dev/null | tail -n +11 | xargs -I {} rm -f {} {}.sha256 2>/dev/null || true
echo "Done."
