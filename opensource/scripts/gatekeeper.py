#!/usr/bin/env python3
"""
Safety Gate — runs before any iteration starts.

Checks:
  - cost_budget_check: today's OpenRouter cost > $5 → block
  - git_clean_check: uncommitted changes and auto-stash fails → block
  - consecutive_failure_check: ≥3 subagent spawns in last 24h with no accuracy improvement → suppress spawns for 4h
  - rate_limit_check: last run was under 1 hour ago → block unless --force

Output: gatekeeper_report.json
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LOG_PATH = REPO_ROOT / ".iteration_log.jsonl"
REPORT_PATH = REPO_ROOT / "gatekeeper_report.json"
STATE_PATH = REPO_ROOT / ".iteration_state.json"

MAX_DAILY_COST = 5.00
SUBAGENT_SUPPRESS_HOURS = 4
MIN_INTERVAL_MINUTES = 60


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_last_iter_time() -> datetime | None:
    if not LOG_PATH.exists():
        return None
    last = None
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("event") in ("benchmark_start", "iteration_triggered"):
                    last = entry.get("timestamp")
            except json.JSONDecodeError:
                continue
    if last is None and STATE_PATH.exists():
        with open(STATE_PATH) as f:
            data = json.load(f)
        last = data.get("last_run")
    if last:
        try:
            return datetime.fromisoformat(last)
        except ValueError:
            return datetime.strptime(last, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
    return None


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


def cost_budget_check(metrics: dict) -> dict:
    today_cost = metrics.get("openrouter", {}).get("today_cost_usd", 0.0)
    if today_cost is None:
        today_cost = 0.0
    passed = today_cost <= MAX_DAILY_COST
    return {
        "passed": passed,
        "current_spend": round(today_cost, 2),
        "budget": MAX_DAILY_COST,
    }


def git_clean_check() -> dict:
    try:
        diff = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=10
        )
        has_changes = bool(diff.stdout.strip())
        if not has_changes:
            return {"passed": True, "stashed": False, "message": "working tree clean"}
        stash = subprocess.run(
            ["git", "stash", "push", "-m", f"auto-stash @ {now_iso()}"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=10
        )
        if stash.returncode == 0:
            return {"passed": True, "stashed": True, "message": stash.stdout.strip()}
        else:
            return {"passed": False, "stashed": False, "message": stash.stderr.strip()}
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"passed": False, "stashed": False, "message": str(e)}


def consecutive_failure_check() -> dict:
    if not LOG_PATH.exists():
        return {"passed": True, "recent_subagents": 0, "message": "no log"}
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_subagents = 0
    recent_best = None
    last_best = None
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts_str = entry.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str)
            except (ValueError, TypeError):
                continue
            if ts < cutoff:
                if entry.get("event") == "new_best_accuracy":
                    last_best = entry.get("accuracy")
                continue
            if entry.get("event") == "subagent_spawn_request":
                recent_subagents += 1
            elif entry.get("event") == "new_best_accuracy":
                recent_best = entry.get("accuracy")
    improved = False
    if recent_best is not None:
        if last_best is None or recent_best > last_best:
            improved = True
    suppress_until = None
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            data = json.load(f)
        s = data.get("subagent_suppress_until")
        if s:
            try:
                suppress_until = datetime.fromisoformat(s)
            except ValueError:
                pass
    now = datetime.now(timezone.utc)
    if suppress_until and now < suppress_until:
        return {
            "passed": False,
            "recent_subagents": recent_subagents,
            "suppress_until": suppress_until.isoformat(),
            "message": f"subagent suppression active until {suppress_until.isoformat()}",
        }
    if recent_subagents >= 3 and not improved:
        new_suppress = now + timedelta(hours=SUBAGENT_SUPPRESS_HOURS)
        if STATE_PATH.exists():
            with open(STATE_PATH) as f:
                data = json.load(f)
        else:
            data = {}
        data["subagent_suppress_until"] = new_suppress.isoformat()
        with open(STATE_PATH, "w") as f:
            json.dump(data, f, indent=2)
        return {
            "passed": False,
            "recent_subagents": recent_subagents,
            "suppress_until": new_suppress.isoformat(),
            "message": f">=3 subagent spawns with no accuracy improvement — suppressing for {SUBAGENT_SUPPRESS_HOURS}h",
        }
    return {
        "passed": True,
        "recent_subagents": recent_subagents,
        "message": "no failure spiral detected",
    }


def rate_limit_check(force: bool = False) -> dict:
    last = read_last_iter_time()
    if last is None:
        return {"passed": True, "minutes_since_last": None, "message": "no prior run"}
    delta = datetime.now(timezone.utc) - last
    minutes = int(delta.total_seconds() / 60)
    if force:
        return {"passed": True, "minutes_since_last": minutes, "message": "force flag set"}
    if minutes < MIN_INTERVAL_MINUTES:
        return {
            "passed": False,
            "minutes_since_last": minutes,
            "message": f"last run was {minutes} min ago (min {MIN_INTERVAL_MINUTES} min)",
        }
    return {"passed": True, "minutes_since_last": minutes, "message": "rate limit clear"}


def gatekeeper(force: bool = False) -> dict:
    metrics = fetch_metrics()
    ck1 = cost_budget_check(metrics)
    ck2 = git_clean_check()
    ck3 = consecutive_failure_check()
    ck4 = rate_limit_check(force=force)
    all_passed = ck1["passed"] and ck2["passed"] and ck3["passed"] and ck4["passed"]
    block_reason = ""
    if not ck1["passed"]:
        block_reason = f"budget exceeded: ${ck1['current_spend']} / ${ck1['budget']}"
    elif not ck2["passed"]:
        block_reason = f"git dirty and stash failed: {ck2['message']}"
    elif not ck3["passed"]:
        block_reason = ck3["message"]
    elif not ck4["passed"]:
        block_reason = ck4["message"]
    report = {
        "timestamp": now_iso(),
        "proceed": all_passed,
        "block_reason": block_reason,
        "checks": {
            "cost_budget": ck1,
            "git_clean": ck2,
            "consecutive_failures": ck3,
            "rate_limit": ck4,
        },
    }
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Bypass rate limit")
    args = parser.parse_args()
    report = gatekeeper(force=args.force)
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["proceed"] else 1)


if __name__ == "__main__":
    main()
