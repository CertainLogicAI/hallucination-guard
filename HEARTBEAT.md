# HEARTBEAT.md - Nightly Memory Integrity Check

## Periodic Checks
- **Brain API**: Verify `curl -s http://127.0.0.1:8000/health` returns OK. If down, run `bash /data/.openclaw/workspace/start-brain.sh` to restart.

## Scheduled Tasks
- **02:00 UTC**: Run nightly memory integrity check with retries
  - Executes: `/data/.openclaw/workspace/nightly_heartbeat.sh`
  - Max 3 attempts with 30s delays between retries
  - Logs to: `/data/.openclaw/workspace/logs/heartbeat_integrity.log`
  - Runs automatically during heartbeat poll at 02:00 UTC

## Current Status
- Nightly script: ✅ Created and executable
- Retry logic: ✅ Implemented (max 3 attempts, 30s delays)
- Log directory: ✅ Created
- Heartbeat integration: ✅ Scheduled for 02:00 UTC

## Check Instructions
If you suspect the nightly check failed, inspect the log:
```bash
cat /data/.openclaw/workspace/logs/heartbeat_integrity.log
```