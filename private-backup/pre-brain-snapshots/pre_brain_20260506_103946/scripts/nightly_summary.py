#!/usr/bin/env python3
"""Nightly session summarizer — aggregate today’s activity into a single memory file."""

import glob
import os
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
    health_json = os.path.join(LOGS_DIR, "system_health_latest.json")
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
    state_dir = os.path.join(WORKSPACE, "state")
    if os.path.isdir(state_dir):
        files = [f for f in os.listdir(state_dir) if not f.startswith(".")]
        return files
    return []


def main():
    date_str = today_iso()
    mem_files = get_memory_files(date_str)

    # Build summary lines
    lines = []
    lines.append(f"# Nightly Summary — {date_str}")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()} UTC")
    lines.append("")

    # --- Memory ---
    lines.append("## Memory Files")
    if not mem_files:
        lines.append("No memory files found for today.")
    else:
        for mf in mem_files:
            info = summarize_memory(mf)
            lines.append(f"")
            lines.append(f"### {info['filename']} ({info['line_count']} lines)")
            if info["headings"]:
                for h in info["headings"]:
                    lines.append(f"  {h}")
            if info["bullets"]:
                for b in info["bullets"]:
                    if len(b) > 200:
                        b = b[:197] + "..."
                    lines.append(f"  {b}")
    lines.append("")

    # --- Git ---
    lines.append("## Git Status")
    lines.append(f"  Working tree: {git_status()}")
    commits = recent_commits()
    if commits:
        lines.append("  Recent commits:")
        for c in commits:
            lines.append(f"    {c}")
    lines.append("")

    # --- Health ---
    lines.append("## System Health")
    health = system_health_brief()
    if health:
        lines.append(f"  Disk used: {health.get('disk_used_pct')}%")
        lines.append(f"  Memory used: {health.get('mem_used_pct')}%")
        lines.append(f"  CPU load (1m): {health.get('cpu_load')}")
        lines.append(f"  Uptime: {health.get('uptime')}")
    else:
        lines.append("  Health data unavailable.")
    lines.append("")

    # --- State ---
    active = active_sessions()
    if active:
        lines.append("## Active State Files")
        for a in active:
            lines.append(f"  {a}")
        lines.append("")

    lines.append("---")
    lines.append("End of summary.")

    summary_text = "\n".join(lines)

    # Write to today's memory file
    memory_path = os.path.join(MEMORY_DIR, f"{date_str}.md")
    with open(memory_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(summary_text)
    print(f"\n[INFO] Summary written to {memory_path}")


if __name__ == "__main__":
    main()
