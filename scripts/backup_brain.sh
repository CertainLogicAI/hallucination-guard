#!/usr/bin/env bash
# Brain Data Backup — Pre-Brain Safety Net
# Run manually before any risky brain operations or daily via cron

set -euo pipefail

WORKSPACE="/data/.openclaw/workspace"
DATA_DIR="$WORKSPACE/company-brain-data"
BACKUP_DIR="$WORKSPACE/private-backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "=== Brain Data Backup ==="
echo "Timestamp: $TIMESTAMP"
echo "Source: $DATA_DIR"
echo "Destination: $BACKUP_DIR"
echo

# 1. Verify source exists
if [[ ! -d "$DATA_DIR" ]]; then
    echo "ERROR: $DATA_DIR not found"
    exit 1
fi

# 2. Create backup directory
mkdir -p "$BACKUP_DIR"

# 3. Copy all brain data files
echo "[1/5] Copying brain data files..."
cp -v "$DATA_DIR/audit.jsonl" "$BACKUP_DIR/audit_backup_$TIMESTAMP.jsonl"
cp -v "$DATA_DIR/page_hashes.jsonl" "$BACKUP_DIR/page_hashes_backup_$TIMESTAMP.jsonl"
cp -v "$DATA_DIR/provenance_log.jsonl" "$BACKUP_DIR/provenance_backup_$TIMESTAMP.jsonl"

# 4. Copy intent directory (with structure)
echo "[2/5] Copying intent definitions..."
cp -rv "$DATA_DIR/intent" "$BACKUP_DIR/intent_backup_$TIMESTAMP"

# 5. Compress for efficiency
echo "[3/5] Compressing backup..."
tar -czf "$BACKUP_DIR/brain_full_$TIMESTAMP.tar.gz" \
    -C "$DATA_DIR" \
    audit.jsonl page_hashes.jsonl provenance_log.jsonl intent/

# 6. Copy critical files uncompressed for quick access
echo "[4/5] Quick-access copies..."
cp -v "$DATA_DIR/audit.jsonl" "$BACKUP_DIR/audit_latest.jsonl"

# 7. Calculate checksums
echo "[5/5] Calculating checksums..."
cd "$BACKUP_DIR"
sha256sum brain_full_$TIMESTAMP.tar.gz > brain_full_$TIMESTAMP.sha256
cat brain_full_$TIMESTAMP.sha256

echo
echo "=== Backup Complete ==="
echo "Files:"
ls -lh "$BACKUP_DIR/"*"$TIMESTAMP"* 2>/dev/null || true
echo
echo "Total backup size:"
du -sh "$BACKUP_DIR/brain_full_$TIMESTAMP.tar.gz"
echo
echo "Verify integrity:"
echo "  sha256sum -c $BACKUP_DIR/brain_full_$TIMESTAMP.sha256"
echo

# Cleanup old backups (keep last 14)
echo "Cleaning up backups older than 14 days..."
find "$BACKUP_DIR" -name "brain_full_*.tar.gz" -mtime +14 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.sha256" -mtime +14 -delete 2>/dev/null || true
echo "Done."
