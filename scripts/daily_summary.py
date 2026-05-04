#!/usr/bin/env python3
"""Daily summary — collect memory, health, and project status."""

import glob
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

WORKSPACE = "/data/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
LOGS_DIR = os.path.join(WORKSPACE, "logs")


def today_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


def get_memory_files(date_str):
    pattern = os.path.join(MEMORY_DIR, f"{date_str}*.md")
    files = glob.glob(pattern)
    # Exclude archive/backups
    files = [f for f in files if not f.endswith(".bak") and not f.endswith(".gz")]
    return sorted(files)


def summarize_memory(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    bullets = []
    headings = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            headings.append(stripped)
        elif stripped.startswith(("- ", "* ", "• ")):
            bullets.append(stripped)

    # Truncate if massive
    if len(bullets) > 30:
        bullets = bullets[:30] + [f"... ({len(bullets) - 30} more bullets)"]

    return {
        "filename": os.path.basename(path),
        "headings": headings,
        "bullets": bullets,
        "line_count": len(lines),
    }


def git_status():
    out = run_cmd(f"cd {WORKSPACE} && git status --short")
    if not out:
        return "Clean"
    lines = out.splitlines()
    return f"{len(lines)} modified/untracked"


def recent_commits(n=3):
    out = run_cmd(f"cd {WORKSPACE} && git log --oneline -{n}")
    return out.splitlines() if out else []


def system_health_brief():
    # Run the existing health script and capture JSON
    health_json = os.path.join(LOGS_DIR, "system_health_latest.json")
    # Refresh it
    run_cmd(f"cd {WORKSPACE} && python3 scripts/system_health.py >/dev/null 2>&1")
    if os.path.exists(health_json):
        import json
        with open(health_json, "r") as f:
            data = json.load(f)
        disk = data.get("disk", {})
        mem = data.get("memory", {})
        cpu = data.get("cpu", {})
        return {
            "disk_used_pct": disk.get("percent_used", "?"),
            "mem_used_pct": mem.get("percent_used", "?"),
            "cpu_load": cpu.get("1m", "?"),
            "uptime": data.get("uptime", {}).get("uptime", "?"),
        }
    return {}


def active_sessions():
    # Look for any indicator files or running processes
    state_dir = os.path.join(WORKSPACE, "state")
    if os.path.isdir(state_dir):
        files = [f for f in os.listdir(state_dir) if not f.startswith(".")]
        return files
    return []


def main():
    date_str = today_iso()
    mem_files = get_memory_files(date_str)

    print(f"# Daily Summary — {date_str}")
    print(f"Generated: {datetime.now(timezone.utc).isoformat()} UTC")
    print()

    # --- Memory ---
    print("## Memory Files")
    if not mem_files:
        print("No memory files found for today.")
    else:
        for mf in mem_files:
            info = summarize_memory(mf)
            print(f"\n### {info['filename']} ({info['line_count']} lines)")
            if info["headings"]:
                for h in info["headings"]:
                    print(f"  {h}")
            if info["bullets"]:
                for b in info["bullets"]:
                    # Truncate very long bullets
                    if len(b) > 200:
                        b = b[:197] + "..."
                    print(f"  {b}")
    print()

    # --- Git ---
    print("## Git Status")
    print(f"  Working tree: {git_status()}")
    commits = recent_commits()
    if commits:
        print("  Recent commits:")
        for c in commits:
            print(f"    {c}")
    print()

    # --- Health ---
    print("## System Health")
    health = system_health_brief()
    if health:
        print(f"  Disk used: {health.get('disk_used_pct')}%")
        print(f"  Memory used: {health.get('mem_used_pct')}%")
        print(f"  CPU load (1m): {health.get('cpu_load')}")
        print(f"  Uptime: {health.get('uptime')}")
    else:
        print("  Health data unavailable.")
    print()

    # --- State ---
    active = active_sessions()
    if active:
        print("## Active State Files")
        for a in active:
            print(f"  {a}")
        print()

    # --- Footer ---
    print("---")
    print("End of summary.")

    # Write to logs for persistence
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_path = os.path.join(LOGS_DIR, f"daily_summary_{date_str}.md")
    # We already printed to stdout; also write if we want file persistence
    # Re-run logic to write file (or capture stdout — simpler to just write)
    # For now, stdout is enough for cron capture.


if __name__ == "__main__":
    main()
