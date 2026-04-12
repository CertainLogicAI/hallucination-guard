#!/bin/bash
# Cache cleanup script
CACHE_FILE="/data/.openclaw/workspace/workspace-cache.json"
BACKUP_DIR="/data/.openclaw/workspace/backups/cache"

# Create backup of current cache
mkdir -p "$BACKUP_DIR"
cp "$CACHE_FILE" "$BACKUP_DIR/cache-$(date +%Y%m%d-%H%M%S).json"

# Get current size
CURRENT_SIZE=$(wc -c < "$CACHE_FILE")
MAX_SIZE=$((50 * 1024 * 1024))  # 50MB

if [ "$CURRENT_SIZE" -gt "$MAX_SIZE" ]; then
    echo "Cache size $CURRENT_SIZE exceeds limit $MAX_SIZE"
    echo "Running cleanup..."
    
    # Remove entries older than 30 days
    python3 -c "
import json
import time
from datetime import datetime, timedelta

with open('$CACHE_FILE', 'r') as f:
    cache = json.load(f)

cutoff = time.time() - (30 * 24 * 60 * 60)
new_cache = {k: v for k, v in cache.items() 
            if v.get('timestamp', 0) > cutoff}

with open('$CACHE_FILE', 'w') as f:
    json.dump(new_cache, f, indent=2)

print(f'Reduced cache from {len(cache)} to {len(new_cache)} entries')
"
    
    echo "Cache cleanup completed"
else
    echo "Cache size OK: $CURRENT_SIZE bytes"
fi