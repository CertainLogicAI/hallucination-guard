#!/usr/bin/env python3
"""System health check script."""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone


def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


def disk_usage():
    total, used, free = shutil.disk_usage("/")
    return {
        "total_gb": round(total / (1024**3), 2),
        "used_gb": round(used / (1024**3), 2),
        "free_gb": round(free / (1024**3), 2),
        "percent_used": round(used * 100 / total, 1)
    }


def memory_usage():
    try:
        mem = run_cmd("free -m | awk 'NR==2{print $2,$3,$7}'")
        total, used, avail = map(float, mem.split())
        return {
            "total_mb": round(total, 0),
            "used_mb": round(used, 0),
            "available_mb": round(avail, 0),
            "percent_used": round(used * 100 / total, 1)
        }
    except Exception as e:
        return {"error": str(e)}


def cpu_info():
    try:
        load = os.getloadavg()
        cores = max(1.0, float(run_cmd("nproc")))
        return {
            "1m": round(load[0], 2),
            "5m": round(load[1], 2),
            "15m": round(load[2], 2),
            "cores": int(cores),
            "usage_estimate_percent": round((load[0] / cores) * 100, 1)
        }
    except Exception as e:
        return {"error": str(e)}


def uptime_info():
    uptime = run_cmd("uptime -p")
    return {"uptime": uptime}


def check_services(services):
    results = {}
    for svc in services:
        try:
            out = run_cmd(f"systemctl is-active {svc}", timeout=10)
            results[svc] = "active" if out == "active" else f"inactive ({out})"
        except Exception as e:
            results[svc] = f"error: {e}"
    return results


def docker_info():
    running = run_cmd("docker ps -q | wc -l")
    total = run_cmd("docker ps -aq | wc -l")
    return {
        "containers_running": int(running) if running.isdigit() else running,
        "containers_total": int(total) if total.isdigit() else total
    }


def top_processes():
    top = run_cmd("ps aux --sort=-%mem | head -6 | tail -5")
    lines = []
    for line in top.split("\n"):
        parts = line.split(None, 10)
        if len(parts) >= 11:
            lines.append(parts[10])
    return lines


def check_openclaw_logs():
    log_path = "/data/.openclaw/workspace/logs"
    if not os.path.isdir(log_path):
        return {"log_dir_exists": False}
    recent_errors = run_cmd(f"grep -ri --exclude='system_health_latest.json' -E -A2 'error|fatal|panic' {log_path} 2>/dev/null | tail -30 || true")
    return {
        "log_dir_exists": True,
        "recent_errors": recent_errors.split("\n") if recent_errors else []
    }


def main():
    now = datetime.now(timezone.utc).isoformat()
    result = {
        "timestamp": now,
        "hostname": run_cmd("hostname"),
        "disk": disk_usage(),
        "memory": memory_usage(),
        "cpu": cpu_info(),
        "uptime": uptime_info(),
        "docker": docker_info(),
        "top_processes": top_processes(),
        "openclaw_logs": check_openclaw_logs()
    }

    # Print human-readable summary
    print(f"=== System Health Check ===")
    print(f"Timestamp: {now}")
    print(f"Hostname:  {result['hostname']}")
    print(f"Uptime:    {result['uptime']['uptime']}")
    print()
    d = result["disk"]
    print(f"Disk Usage:  {d['used_gb']} / {d['total_gb']} GB  ({d['percent_used']}% used)")
    m = result["memory"]
    if "error" not in m:
        print(f"Memory:      {m['used_mb']} / {m['total_mb']} MB  ({m['percent_used']}% used)")
    c = result["cpu"]
    if "error" not in c:
        print(f"CPU Load:    {c['1m']} ({c['usage_estimate_percent']}% est. on {c['cores']} cores)")
    print(f"Docker:      {result['docker']['containers_running']} running / {result['docker']['containers_total']} total")
    print()
    if result["openclaw_logs"]["log_dir_exists"]:
        errors = result["openclaw_logs"]["recent_errors"]
        if errors:
            print(f"Recent log errors/warnings ({len(errors)} lines):")
            for e in errors:
                print(f"  {e}")
        else:
            print("No recent errors/warnings in logs.")
    else:
        print("Log directory not found.")
    print()
    print("=== Top Processes by Memory ===")
    for p in result["top_processes"]:
        print(f"  {p}")

    # Also write JSON output for easy parsing
    json_path = "/data/.openclaw/workspace/logs/system_health_latest.json"
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nJSON result written to: {json_path}")


if __name__ == "__main__":
    main()
