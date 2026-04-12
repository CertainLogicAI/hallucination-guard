#!/bin/bash
# log-backup-wrapper.sh
# Runs both the FastAPI server and the log daemon in the same process tree.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO] $1${NC}"
}
error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}
warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" >&2
}

# Directory setup
LOGS_DIR="/data/.openclaw/workspace/conversation_logs"
BACKUP_DIR="/data/.openclaw/workspace/backup_local"
ARCHIVE_DIR="$BACKUP_DIR/archive"

# Ensure directories exist
mkdir -p "$LOGS_DIR" "$BACKUP_DIR" "$ARCHIVE_DIR"

# Function to start the FastAPI server
start_api() {
    log "Starting FastAPI server on port 8000..."
    # Run in background so we can also run the daemon
    nohup uvicorn api/main.py --host 0.0.0.0 --port 8000 > api.log 2>&1 &
    API_PID=$!
    log "FastAPI server started with PID $API_PID"
    sleep 2  # Give it a moment to bind to port
}

# Function to start the log daemon
start_daemon() {
    log "Starting log daemon..."
    # Run in background
    nohup ./sync_daemon.sh > sync.log 2>&1 &
    DAEMON_PID=$!
    log "Log daemon started with PID $DAEMON_PID"
}

# Function to check if processes are running
check_processes() {
    API_RUNNING=false
    DAEMON_RUNNING=false
    
    # Check API (any uvicorn process)
    if pgrep -f "uvicorn" > /dev/null 2>&1; then
        API_RUNNING=true
    fi
    
    # Check daemon
    if pgrep -f "sync_daemon.sh" > /dev/null 2>&1; then
        DAEMON_RUNNING=true
    fi
    
    # Return non-zero if any not running
    return $(( !API_RUNNING || !DAEMON_RUNNING ))
}

# Function to print status
print_status() {
    API_RUNNING=false
    DAEMON_RUNNING=false
    
    if pgrep -f "uvicorn" > /dev/null 2>&1; then
        API_RUNNING=true
    fi
    if pgrep -f "sync_daemon.sh" > /dev/null 2>&1; then
        DAEMON_RUNNING=true
    fi
    
    echo "=== System Status ==="
    echo "API running: $API_RUNNING"
    echo "Daemon running: $DAEMON_RUNNING"
    echo "Logs directory: $LOGS_DIR"
    echo "Backup directory: $BACKUP_DIR"
    echo "Archive directory: $ARCHIVE_DIR"
    echo "===================="
}

# Main execution
log "Starting Log Backup System..."

# Start both services
start_api
start_daemon

# Wait a moment for processes to start
sleep 3

# Print initial status
print_status

# Keep the script running (watchdog loop)
while true; do
    # Check if either process died
    if ! pgrep -f "uvicorn" > /dev/null 2>&1 || ! pgrep -f "sync_daemon.sh" > /dev/null 2>&1; then
        log "One of the processes died. Restarting..."
        # Kill any orphaned processes
        pkill -f uvicorn 2>/dev/null || true
        pkill -f sync_daemon.sh 2>/dev/null || true
        
        # Restart both
        start_api
        start_daemon
        
        # Print status after restart
        print_status
    fi
    
    # Sleep before next health check
    sleep 30
done

log "Log Backup System exited."