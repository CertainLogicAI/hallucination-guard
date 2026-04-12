# MEMORY System Documentation

## Overview
This document outlines the memory system architecture, implementation details, and operational procedures for the OpenClaw memory management system.

## Core Components
1. **Memory Files**
   - `MEMORY.md`: Central long-term memory repository
   - Daily notes: `memory/YYYY-MM-DD.md` (ephemeral records)

2. **Atomic Write Mechanism**
   - `write_atomic.sh`: Ensures safe file updates via temporary files
   - Git integration: Automatic version control with signed commits

3. **Integrity System**
   - `integrity_scan.sh`: Verifies file integrity via SHA-256 hashes
   - Backup verification: `rclone` sync (if configured) or local dummy fallback

4. **Automation**
   - Nightly heartbeat: `nightly_heartbeat.sh` with retry logic
   - Cron job: Scheduled at 02:00 UTC

## Workflow
1. All changes go through `write_atomic.sh`
2. Every modification is git-committed
3. Integrity check runs automatically
4. Backup sync attempted nightly

## Security
- All files stored in `/data/.openclaw/workspace`
- Git repository maintains audit trail
- Optional GPG signing for commit verification

## Maintenance
- Weekly: Review `MEMORY.md` for orphaned entries
- Monthly: Verify backup integrity via `integrity_scan.sh`
- Quarterly: Audit git history and remove stale backups

## Troubleshooting
- Check logs: `/data/.openclaw/workspace/logs/heartbeat_integrity.log`
- Run: `./integrity_scan.sh --full` for manual checks
