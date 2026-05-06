#!/usr/bin/env python3
"""Daily metrics snapshot — single-line summary for cron delivery."""

import json
import os
import shutil
import subprocess
from datetime import datetime, date, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
LOGS_DIR = WORKSPACE / "logs"
PRODUCTS_DIR = WORKSPACE / "products"


def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except Exception as e:
        return ""


def disk():
    total, used, free = shutil.disk_usage("/")
    return {
        "total_gb": round(total / (1024**3), 2),
        "used_gb": round(used / (1024**3), 2),
        "free_gb": round(free / (1024**3), 2),
        "pct": round(used * 100 / total, 1)
    }


def mem():
    try:
        out = run_cmd("free -m | awk 'NR==2{print $2,$3,$7}'")
        total, used, avail = map(float, out.split())
        return {
            "total_mb": round(total, 0),
            "used_mb": round(used, 0),
            "pct": round(used * 100 / total, 1)
        }
    except Exception:
        return {"pct": None}


def cpu():
    try:
        load = os.getloadavg()
        cores = max(1.0, float(run_cmd("nproc") or 1))
        return {
            "1m": round(load[0], 2),
            "cores": int(cores),
            "pct": round((load[0] / cores) * 100, 1)
        }
    except Exception:
        return {"pct": None}


def docker():
    running = run_cmd("docker ps -q 2>/dev/null | wc -l")
    total = run_cmd("docker ps -aq 2>/dev/null | wc -l")
    return {
        "running": int(running) if str(running).isdigit() else 0,
        "total": int(total) if str(total).isdigit() else 0
    }


def git_stats():
    unstaged = run_cmd(f"cd {WORKSPACE} && git status --short | wc -l")
    last_commit = run_cmd(f"cd {WORKSPACE} && git log -1 --format=%h")
    return {"unstaged": int(unstaged) if str(unstaged).isdigit() else 0, "last_commit": last_commit or "none"}


def product_health():
    if not PRODUCTS_DIR.exists():
        return {"products": 0, "pass": 0, "fail": 0}
    products = [d for d in PRODUCTS_DIR.iterdir() if d.is_dir()]
    passed = 0
    failed = 0
    for p in products:
        inv = p / "inventory.json"
        if inv.exists():
            try:
                data = json.loads(inv.read_text())
                if data.get("status") == "active":
                    passed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        else:
            failed += 1
    return {"products": len(products), "pass": passed, "fail": failed}


def coding_queries(target_date: date = None):
    target_date = target_date or date.today()
    target_str = target_date.isoformat()
    log_file = LOGS_DIR / "coding_queries.jsonl"
    coding = 0
    hits = 0
    total_queries = 0
    tokens_saved = 0
    if log_file.exists():
        with open(log_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("date") != target_str:
                    continue
                total_queries += 1
                if entry.get("is_coding"):
                    coding += 1
                    if entry.get("cache_hit"):
                        hits += 1
                tokens_saved += entry.get("tokens_saved", 0)
    hit_rate = round(hits / coding * 100, 1) if coding > 0 else 0.0
    return {
        "total": total_queries,
        "coding": coding,
        "hits": hits,
        "hit_rate": hit_rate,
        "tokens_saved": tokens_saved
    }


def main():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    d = disk()
    m = mem()
    c = cpu()
    dc = docker()
    g = git_stats()
    ph = product_health()
    cq = coding_queries()

    # Build compact summary line
    parts = [
        f"[{ts}]",
        f"disk={d['pct']}% ({d['free_gb']}GB free)",
        f"mem={m['pct']}%",
        f"cpu={c['pct']}% ({c['1m']} load, {c['cores']} cores)",
        f"docker={dc['running']}/{dc['total']}",
        f"git={g['unstaged']} unstaged last={g['last_commit']}",
        f"products={ph['products']} (pass={ph['pass']} fail={ph['fail']})",
        f"queries={cq['total']} coding={cq['coding']} hit_rate={cq['hit_rate']}% tokens_saved={cq['tokens_saved']}",
    ]

    line = " | ".join(parts)
    print(line)

    # Persist JSON for downstream dashboards
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "disk": d,
        "memory": m,
        "cpu": c,
        "docker": dc,
        "git": g,
        "products": ph,
        "coding_queries": cq
    }

    LOGS_DIR.mkdir(exist_ok=True)
    json_path = LOGS_DIR / "metrics_snapshot_latest.json"
    with open(json_path, "w") as f:
        json.dump(snapshot, f, indent=2)


if __name__ == "__main__":
    main()
