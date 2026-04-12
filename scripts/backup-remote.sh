#!/bin/bash

# Configure rclone (run once)
rclone config

# Sync to remote storage
rclone copy /data/.openclaw/workspace openclaw-backup:backups/openclaw/ --progress
