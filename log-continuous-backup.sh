#!/bin/bash
# log-continuous-backup.sh
# Contains container restart resilience logic

# Configuration
LOGS_DIR="/data/.openclaw/workspace/conversation_logs"
BACKUP_DIR="/data/.openclaw/workspace/backup_local"
ARCHIVE_DIR="$BACKUP_DIR/archive"
SYNC_DAEMON="sync_daemon.sh"

# PID files
API_PID="$BACKUP_DIR/api.pid"
DAEMON_PID="$BACKUP_DIR/daemon.pid"

# Colors
INFO="\033[0;32m[INFO] \033[0m"
ERROR="\033[0;31m[ERROR] \033[0m"
WARN="\033[0;33m[WARN] \033[0m"

# Initialize directories
mkdir -p "$BACKUP_DIR" "$BACKUP_DIR/archive"

# Start API with PID handling
start_api() {
  echo -e "$INFO Starting FastAPI server..."
  uvicorn api/main.py --host 0.0.0.0 --port 8000 > /data/.openclaw/workspace/api.log 2>&1 &
  echo $! > "$API_PID"
}

# Start sync daemon
start_daemon() {
  echo -e "$INFO Starting log monitor..."
  (cd "$LOGS_DIR" && ./$SYNC_DAEMON) > /data/.openclaw/workspace/sync.log 2>&1 &
  echo $! > "$DAEMON_PID"
}

# Check if processes are running
is_running() {
  pid="$1"
  if ! ps -p "$pid" > /dev/null 2>&1; then
    echo 0
  else
    echo 1
  fi
}

# Cleanup orphaned processes
clean_orphans() {
  if [ -f "$API_PID" ]; then
    pkill -f 'uvicorn' 2>/dev/null
    rm -f "$API_PID"
  fi
  if [ -f "$DAEMON_PID" ]; then
    pkill -f 'sync_daemon.sh' 2>/dev/null
    rm -f "$DAEMON_PID"
  fi
}

# Main loop
while true; do
  # Clean up orphans first
  clean_orphans

  # Start services if not running
  if [ $(is_running $(cat "$API_PID" 2>/dev/null)) -eq 0 ]; then
    start_api
  fi
  
  if [ $(is_running $(cat "$DAEMON_PID" 2>/dev/null)) -eq 0 ]; then
    start_daemon
  fi

  # Give processes time to start
  if [ $(is_running $(cat "$API_PID" 2>/dev/null)) -eq 1 ]; then
    sleep 1  # Wait for API to bind
  fi

  # Health check
  if ! curl --output /dev/null --silent --head --fail http://localhost:8000/health; then
    echo -e "$ERROR Health check failed - killing processes"
    clean_orphans
    continue
  fi

  # Final status
  echo -e "$INFO System healthy"
  echo "API: $(cat "$API_PID" || echo 'N/A')"
  echo "Daemon: $(cat "$DAEMON_PID" || echo 'N/A')"
  echo "------------------"
  
  sleep 2  # Small delay between successful heartbeat checks
done

# Fallback - in case container restarts or processes complete
while kill $(ps -orscargs= -p $PPID); do
  sleep 1
done
exit 0