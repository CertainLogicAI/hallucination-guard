#!/bin/bash
# Daily backup: local + Backblaze B2 upload
set -euo pipefail

BACKUP_DIR="/data/.openclaw/backups"
DATE=$(date +%Y-%m-%d)
BACKUP_FILE="${BACKUP_DIR}/workspace-${DATE}.tar.gz"
B2_BUCKET="OpenclawBackup1"
B2_KEY_ID="005b66eb9a17c000000000001"
B2_APP_KEY="K005VpdspLyYbPdLivcHXtW9I+dmM1E"

mkdir -p "$BACKUP_DIR"

# Remove local backups older than 7 days
find "$BACKUP_DIR" -name "workspace-*.tar.gz" -mtime +7 -delete 2>/dev/null || true

# Create compressed backup
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
echo "Local backup: ${BACKUP_FILE} (${SIZE})"

# Authorize with B2
AUTH=$(curl -s -u "${B2_KEY_ID}:${B2_APP_KEY}" https://api.backblazeb2.com/b2api/v2/b2_authorize_account)
API_URL=$(echo "$AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['apiUrl'])")
AUTH_TOKEN=$(echo "$AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['authorizationToken'])")

# Get upload URL
BUCKET_ID=$(curl -s -H "Authorization: ${AUTH_TOKEN}" "${API_URL}/b2api/v2/b2_list_buckets" \
  -d "{\"accountId\":\"b66eb9a17c00\",\"bucketName\":\"${B2_BUCKET}\"}" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['buckets'][0]['bucketId'])")

UPLOAD_INFO=$(curl -s -H "Authorization: ${AUTH_TOKEN}" "${API_URL}/b2api/v2/b2_get_upload_url" \
  -d "{\"bucketId\":\"${BUCKET_ID}\"}")
UPLOAD_URL=$(echo "$UPLOAD_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['uploadUrl'])")
UPLOAD_TOKEN=$(echo "$UPLOAD_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['authorizationToken'])")

# Calculate SHA1
SHA1=$(sha1sum "$BACKUP_FILE" | cut -d' ' -f1)

# Upload
RESULT=$(curl -s \
  -H "Authorization: ${UPLOAD_TOKEN}" \
  -H "X-Bz-File-Name: openclaw/daily/workspace-${DATE}.tar.gz" \
  -H "Content-Type: application/gzip" \
  -H "X-Bz-Content-Sha1: ${SHA1}" \
  --data-binary "@${BACKUP_FILE}" \
  "$UPLOAD_URL")

UPLOADED_NAME=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('fileName','FAILED'))" 2>/dev/null || echo "FAILED")

if [ "$UPLOADED_NAME" = "FAILED" ]; then
  echo "ERROR: B2 upload failed"
  echo "$RESULT"
  exit 1
else
  echo "B2 upload: ${UPLOADED_NAME} (${SIZE})"
  echo "Backup complete."
fi
