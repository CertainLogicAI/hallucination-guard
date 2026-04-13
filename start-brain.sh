#!/bin/bash
# Start the Deterministic AI Brain service
# Run from workspace root

cd /data/.openclaw/workspace
PID_FILE="/tmp/brain-api.pid"
LOG_FILE="/data/.openclaw/workspace/logs/brain-api.log"

# Kill existing if running
if [ -f "$PID_FILE" ]; then
    kill $(cat "$PID_FILE") 2>/dev/null
    sleep 1
fi

# Start
PATH="/data/.local/bin:$PATH"
nohup uvicorn main:app --host 127.0.0.1 --port 8000 >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

# Wait and verify
sleep 2
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    FACTS=$(curl -s http://127.0.0.1:8000/facts | python3 -c 'import sys,json; print(json.load(sys.stdin)["count"])')
    echo "Brain API running (PID $(cat $PID_FILE), $FACTS facts loaded)"
else
    echo "ERROR: Brain API failed to start. Check $LOG_FILE"
    exit 1
fi
