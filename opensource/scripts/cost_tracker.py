#!/usr/bin/env python3
"""
Per-Iteration Spend Tracker — snapshots Brain API cost before/after each iteration.

Logs to .iteration_log.jsonl as event type `iteration_cost`.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LOG_PATH = REPO_ROOT / ".iteration_log.jsonl"
STATE_PATH = REPO_ROOT / ".iteration_state.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_metrics() -> dict:
    try:
        result = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:8000/metrics"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return {}


def snapshot() -> dict:
    """Return current cost snapshot from Brain API."""
    m = fetch_metrics()
    return {
        "timestamp": now_iso(),
        "today_cost": m.get("openrouter", {}).get("today_cost_usd", 0.0),
        "total_cost": m.get("openrouter", {}).get("total_cost_usd", 0.0),
        "total_calls": m.get("openrouter", {}).get("total", 0),
        "today_calls": m.get("openrouter", {}).get("today", 0),
        "cache_hit_rate": m.get("rates", {}).get("cache_hit_rate_pct", 0.0),
    }


def log_event(event: str, details: dict):
    entry = {
        "timestamp": now_iso(),
        "event": event,
        **details,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[{entry['timestamp']}] {event}: {details}")


def log_iteration_cost(before: dict, after: dict, iteration: int):
    """Calculate delta and append an iteration_cost event."""
    iteration_spend = round((after.get("today_cost") or 0.0) - (before.get("today_cost") or 0.0), 4)
    iteration_calls = (after.get("today_calls") or 0) - (before.get("today_calls") or 0)
    cache_hit_rate = after.get("cache_hit_rate", 0.0)

    details = {
        "iteration": iteration,
        "iteration_spend": iteration_spend,
        "iteration_calls": iteration_calls,
        "cache_hit_rate": cache_hit_rate,
        "before": before,
        "after": after,
    }
    log_event("iteration_cost", details)

    # Update total_spend in state
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            data = json.load(f)
    else:
        data = {}
    data["total_spend"] = round((data.get("total_spend") or 0.0) + iteration_spend, 4)
    with open(STATE_PATH, "w") as f:
        json.dump(data, f, indent=2)

    return details


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", action="store_true", help="Print pre-iteration snapshot JSON")
    parser.add_argument("--after", action="store_true", help="Print post-iteration snapshot JSON")
    parser.add_argument("--iteration", type=int, default=0)
    parser.add_argument("--compare", help="Path to JSON file containing 'before' snapshot")
    args = parser.parse_args()

    if args.before:
        snap = snapshot()
        print(json.dumps(snap))
        return

    if args.after:
        if not args.compare:
            print("error: --after requires --compare <before.json>", file=sys.stderr)
            sys.exit(1)
        with open(args.compare) as f:
            before = json.load(f)
        after = snapshot()
        result = log_iteration_cost(before, after, args.iteration)
        print(json.dumps(result))
        return

    # Default: just print current snapshot
    print(json.dumps(snapshot()))


if __name__ == "__main__":
    main()
