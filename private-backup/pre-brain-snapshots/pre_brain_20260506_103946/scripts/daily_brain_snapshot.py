#!/usr/bin/env python3
"""
Daily Brain Data Snapshot
Snapchots facts_db.json and answer_cache.json to private-backup/ with rotation.
Runs automatically via cron every day.
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
PRIVATE_BACKUP = WORKSPACE / "private-backup"
FACTS_DB = WORKSPACE / "facts_db.json"
ANSWER_CACHE = WORKSPACE / "cache_data" / "answer_cache.json"

def run_cmd(cmd, cwd=None):
    """Run shell command silently."""
    subprocess.run(cmd, shell=True, cwd=cwd or WORKSPACE,
                  capture_output=True, timeout=30)

def snapshot():
    """Create timestamped backup of brain data."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    PRIVATE_BACKUP.mkdir(exist_ok=True)
    
    # Snapshot facts
    if FACTS_DB.exists():
        dest = PRIVATE_BACKUP / f"facts_db_snapshot_{ts}.json"
        shutil.copy(FACTS_DB, dest)
        with open(FACTS_DB) as f:
            facts = json.load(f)
        fact_count = len(facts.get("facts", {}))
    else:
        fact_count = 0
    
    # Snapshot cache
    cache_count = 0
    if ANSWER_CACHE.exists():
        dest = PRIVATE_BACKUP / f"answer_cache_snapshot_{ts}.json"
        shutil.copy(ANSWER_CACHE, dest)
        with open(ANSWER_CACHE) as f:
            cache = json.load(f)
        cache_count = len(cache.get("entries", []))
    
    # Rotate: keep last 7 snapshots of each
    rotate_backups("facts_db_snapshot_", 7)
    rotate_backups("answer_cache_snapshot_", 7)
    
    # Git commit
    run_cmd("git add private-backup/")
    run_cmd(f'git commit -m "Daily brain snapshot: {fact_count} facts, {cache_count} queries ({ts})"')
    run_cmd("git push")
    
    print(f"[SNAPSHOT] {fact_count} facts, {cache_count} queries | {ts}")
    return fact_count, cache_count

def rotate_backups(prefix, keep):
    """Delete old backups beyond retention count."""
    files = sorted(PRIVATE_BACKUP.glob(f"{prefix}*.json"), key=lambda p: p.stat().st_mtime)
    for old in files[:-keep]:
        old.unlink()

def main():
    try:
        snapshot()
    except Exception as e:
        print(f"[SNAPSHOT ERROR] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
