#!/bin/bash

# Create encrypted backup
gpg --batch --yes --passphrase "YOUR_STRONG_PASSPHRASE" -c /data/.openclaw/workspace/backup-full-$(date +%Y-%m-%d).tar.gz

# Sync to remote
rclone copy /data/.openclaw/workspace/openclaw-backup.gpg openclaw-backup:backups/openclaw/
