#!/usr/bin/env python3
"""
Agent Self-Improvement Loop — daily orchestrator.
Runs system health, memory GC, product health, daily summary, and agent learning.
Produces a unified JSON report.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

WORKSPACE = "/data/.openclaw/workspace"
LOGS_DIR = os.path.join(WORKSPACE, "logs")


def run_subprocess(script_name, args=None, timeout=120):
    """Run a Python script under scripts/ and return result dict."""
    script_path = os.path.join(WORKSPACE, "scripts", script_name)
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=WORKSPACE,
            timeout=timeout,
        )
        return {
            "ok": result.returncode == 0,
            "rc": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "rc": -1, "stdout": "", "stderr": "TIMEOUT"}
    except Exception as e:
        return {"ok": False, "rc": -2, "stdout": "", "stderr": str(e)}


def log(message):
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[agent-self-improve] {message}")
    return f"[{ts}] {message}"


def main():
    now = datetime.now(timezone.utc).isoformat()
    overall_pass = True
    results = {}

    # 1. system_health
    log("Starting system_health.py")
    res = run_subprocess("system_health.py", timeout=60)
    results["system_health"] = {
        "ok": res["ok"],
        "rc": res["rc"],
        "stdout_last_500": res["stdout"][-500:] if res["stdout"] else "",
        "stderr_last_500": res["stderr"][-500:] if res["stderr"] else "",
    }
    if not res["ok"]:
        overall_pass = False
        log("system_health: FAIL")
    else:
        log("system_health: OK")

    # 2. memory_gc
    log("Starting memory_gc.py")
    res = run_subprocess("memory_gc.py", timeout=120)
    results["memory_gc"] = {
        "ok": res["ok"],
        "rc": res["rc"],
        "stdout_last_500": res["stdout"][-500:] if res["stdout"] else "",
        "stderr_last_500": res["stderr"][-500:] if res["stderr"] else "",
    }
    if res["ok"]:
        # Parse JSON from stdout tail
        try:
            data_lines = [l for l in res["stdout"].strip().splitlines() if l.strip().startswith("{") or l.strip().startswith('"')]
            parsed = json.loads(res["stdout"].strip().split("\n")[-1])
            results["memory_gc"]["data"] = parsed
        except Exception:
            results["memory_gc"]["data"] = {}
    else:
        overall_pass = False
        log("memory_gc: FAIL")

    # 3. product_health
    log("Starting product_health.py")
    res = run_subprocess("product_health.py", timeout=60)
    results["product_health"] = {
        "ok": res["ok"],
        "rc": res["rc"],
        "stdout_last_500": res["stdout"][-500:] if res["stdout"] else "",
        "stderr_last_500": res["stderr"][-500:] if res["stderr"] else "",
    }
    if not res["ok"]:
        overall_pass = False
        log("product_health: FAIL")
    else:
        log("product_health: OK")

    # 4. daily_summary
    log("Starting daily_summary.py")
    res = run_subprocess("daily_summary.py", timeout=60)
    results["daily_summary"] = {
        "ok": res["ok"],
        "rc": res["rc"],
        "stdout_last_500": res["stdout"][-500:] if res["stdout"] else "",
        "stderr_last_500": res["stderr"][-500:] if res["stderr"] else "",
    }
    if not res["ok"]:
        overall_pass = False
        log("daily_summary: FAIL")
    else:
        log("daily_summary: OK")

    # 5. agent_learning (agent_learn.py)
    log("Starting agent_learn.py --all --limit 20")
    res = run_subprocess("agent_learn.py", args=["--all", "--limit", "20"], timeout=60)
    results["agent_learning"] = {
        "ok": res["ok"],
        "rc": res["rc"],
        "stdout_last_1000": res["stdout"][-1000:] if res["stdout"] else "",
        "stderr_last_500": res["stderr"][-500:] if res["stderr"] else "",
    }
    if not res["ok"]:
        overall_pass = False
        log("agent_learning: FAIL")
    else:
        log("agent_learning: OK")

    # Write unified report
    report = {
        "timestamp": now,
        "overall_pass": overall_pass,
        "results": results,
    }

    os.makedirs(LOGS_DIR, exist_ok=True)
    report_path = os.path.join(LOGS_DIR, "agent_self_improve_latest.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n=== Agent Self-Improvement Run ===")
    print(f"Timestamp: {now}")
    print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")
    for name, res in results.items():
        icon = "✓" if res.get("ok") else "✗"
        print(f"  {icon} {name}: rc={res.get('rc')}")
    print(f"\nReport written to: {report_path}")

    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
