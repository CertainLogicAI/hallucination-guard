# Backup Automation Documentation

## Overview
This folder contains the **local backup automation** for all conversation logs. The system works without cron, using a **systemd service and timer** that run inside the container.

## Files
| File | Purpose |
|------|---------|
| `sync_daemon.sh` | Continuously watches `conversation_logs/` for new `.md` files, copies them to `backup_local/`, and performs daily compression when the timer fires. |
| `backup-daemon.service` *(in this folder)* | Systemd service that starts `sync_daemon.sh` on boot and ensures it restarts on failure. |
| `backup-timer.timer` | Triggers daily compression at 02:00 UTC. |
| `README.md` *(this file)* | Documentation for the backup automation. |

## How It Works
1. **File detection** – `sync_daemon.sh` uses `inotifywait` to react instantly to new log files.
2. **Mirroring** – Each new log is copied to `backup_local/` preserving the original filename.
3. **Daily compression** – The systemd timer runs at 02:00 UTC, calling `sync_daemon.sh` which compresses the previous day's logs into a `YYYY‑MM‑DD.tar.gz` file.
4. **Retention** – Files older than 7 days are automatically removed from the daily folder (adjustable in the script).

## Managing the Service
```bash
# Reload systemd after any changes
sudo systemctl daemon-reload

# Enable/start the daemon (runs on boot)
sudo systemctl enable backup-daemon.service
sudo systemctl start backup-daemon.service

# Enable/start the timer (runs daily at 02:00)
sudo systemctl enable backup-timer.timer
sudo systemctl start backup-timer.timer
```

## Verifying Operation
- **Service status**: `systemctl status backup-daemon.service`
- **Timer status**: `systemctl list‑timers --all | grep backup-timer`
- **Log output**: `journalctl -u backup-daemon.service -f`

## Troubleshooting
- If the daemon stops, check `journalctl -u backup-daemon.service` for error messages.
- Ensure the script has execute permission: `chmod +x sync_daemon.sh`.
- Verify that `inotify-tools` is installed (`apt-get install inotify-tools`).

---
*This documentation lives in the `backup_local/` directory so it’s version‑controlled alongside the automation scripts.*