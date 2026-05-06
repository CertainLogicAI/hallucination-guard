#!/usr/bin/env python3
"""Process Dashboard - Single view of ALL CertainLogic system health."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def run_cmd(cmd, shell=False):
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else f"ERROR: {result.stderr.strip()[:100]}"
    except Exception as e:
        return f"ERROR: {str(e)[:100]}"

def check_brain_api():
    try:
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:8000/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            comps = data.get("components", {})
            return {
                "status": "UP",
                "facts_db": comps.get("facts_db", "unknown"),
                "components": {k: v for k, v in comps.items() if k != "facts_db"}
            }
    except Exception as e:
        return {"status": "DOWN", "error": str(e)[:100]}

def check_git_status():
    output = run_cmd("git -C /data/.openclaw/workspace status --short | wc -l", shell=True)
    try:
        count = int(output)
        return {"count": count, "alert": count > 20}
    except:
        return {"count": -1, "alert": True, "error": output}

def check_archive_size():
    output = run_cmd("du -sm /data/.openclaw/workspace/archive/ 2>/dev/null | awk '{print $1}'", shell=True)
    try:
        mb = int(output)
        return {"mb": mb, "alert": mb > 500, "size_str": f"{mb}MB"}
    except:
        return {"mb": 0, "alert": False, "size_str": "unknown"}

def check_coding_tracker():
    try:
        today = datetime.now(timezone.utc).date().isoformat()
        report_file = Path(f"/data/.openclaw/workspace/logs/daily_reports/coding_queries_{today}.json")
        if report_file.exists():
            with open(report_file) as f:
                data = json.load(f)
            return {
                "total": data.get("total_queries", 0),
                "coding": data.get("coding_queries", 0),
                "hit_rate": data.get("coding_hit_rate_percent", 0),
                "tokens_saved": data.get("total_tokens_saved", 0)
            }
        return {"total": 0, "coding": 0, "hit_rate": 0, "tokens_saved": 0}
    except Exception as e:
        return {"error": str(e)[:100]}

def check_memory_files():
    output = run_cmd("ls /data/.openclaw/workspace/memory/*.md 2>/dev/null | wc -l", shell=True)
    try:
        return {"count": int(output)}
    except:
        return {"count": 0}

def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    print("=" * 70)
    print(f"  CertainLogic Process Dashboard  |  {now}")
    print("=" * 70)
    
    # Brain API
    print("\n[BRAIN API]")
    brain = check_brain_api()
    if brain["status"] == "UP":
        print(f"  Status:     UP")
        print(f"  Facts DB:   {brain['facts_db']}")
        ok_comps = [k for k, v in brain.get("components", {}).items() if v == "ok"]
        print(f"  Components: {', '.join(ok_comps) if ok_comps else 'checking...'}")
    else:
        print(f"  Status:     DOWN - {brain.get('error', 'unknown')}")
        print(f"  Fix:        bash start-brain.sh")
    
    # Git
    print("\n[GIT STATUS]")
    git = check_git_status()
    status_icon = "ALERT" if git.get("alert") else "OK"
    print(f"  Uncommitted: {git['count']} files ({status_icon})")
    if git.get("alert"):
        print(f"  Action:      Commit or archive files")
    
    # Archive
    print("\n[ARCHIVE]")
    archive = check_archive_size()
    status_icon = "ALERT" if archive["alert"] else "OK"
    print(f"  Size:        {archive['size_str']} ({status_icon})")
    
    # Coding Tracker
    print("\n[CODING TRACKER]")
    tracker = check_coding_tracker()
    if "error" not in tracker:
        print(f"  Today:       {tracker['total']} queries ({tracker['coding']} coding)")
        print(f"  Hit Rate:    {tracker['hit_rate']}%")
        print(f"  Tokens Saved: {tracker['tokens_saved']}")
        if tracker['hit_rate'] < 50 and tracker['coding'] > 0:
            print(f"  Note:        Cache warming - expected low hit rate")
    else:
        print(f"  Status:      ERROR - {tracker['error']}")
    
    # Memory
    print("\n[MEMORY FILES]")
    memory = check_memory_files()
    print(f"  Count:       {memory['count']} files")
    
    # Crons
    print("\n[CRONS]")
    print(f"  Status:      Run 'cron list' for details")
    print(f"  Note:        Check consecutiveErrors column")
    
    # Summary
    print("\n" + "=" * 70)
    print("  Check complete.")
    print("  See docs/PROCESS_LOG.md for active priorities.")
    print("=" * 70)
    
    # JSON mode
    if "--json" in sys.argv:
        report = {
            "timestamp": now,
            "brain_api": brain,
            "git": git,
            "archive": archive,
            "coding_tracker": tracker,
            "memory": memory
        }
        print("\n--- JSON ---")
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
