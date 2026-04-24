#!/usr/bin/env python3
"""
Full Project Health Assessment — runs after gatekeeper passes.

Checks:
  - Code changes: git diff --stat HEAD (lines changed since last run)
  - Build health: python -m py_compile src/hallucination_guard/*.py
  - Brain API status: cache hit rate, cost trend, facts loaded
  - External API health: HTTP probe to OpenRouter

Output: assessment_report.json with health scores and risk_level
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import urllib.request
except ImportError:
    urllib = None

REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = REPO_ROOT / "src/hallucination_guard"
REPORT_PATH = REPO_ROOT / "assessment_report.json"
METRICS_URL = "http://127.0.0.1:8000/metrics"
OPENROUTER_PING_URL = "https://openrouter.ai/api/v1/models"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_code_changes() -> dict:
    """Check how many lines changed since last commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=10
        )
        stdout = result.stdout.strip()
        if not stdout:
            return {"score": 100, "lines_changed": 0, "files_changed": 0, "message": "no uncommitted changes"}
        # Parse " file changed" summary
        total_line = [l for l in stdout.split("\n") if "file" in l and "changed" in l]
        if total_line:
            parts = total_line[-1].split(",")
            insertions = sum(int(p.strip().split()[0]) for p in parts if "insertion" in p)
            deletions = sum(int(p.strip().split()[0]) for p in parts if "deletion" in p)
            files = int(parts[0].split()[0])
            lines = insertions + deletions
        else:
            lines = stdout.count("\n")
            files = lines
        # Score: 0-50 lines = 100, 200 = 80, 500 = 60, 1000 = 40
        if lines <= 50:
            score = 100
        elif lines <= 200:
            score = 90
        elif lines <= 500:
            score = 75
        elif lines <= 1000:
            score = 60
        else:
            score = 40
        return {"score": score, "lines_changed": lines, "files_changed": files, "message": stdout[:200]}
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"score": 50, "lines_changed": None, "files_changed": None, "message": str(e)}


def check_build_health() -> dict:
    """Syntax-check all src/hallucination_guard/*.py files."""
    py_files = sorted(SRC_DIR.glob("*.py"))
    if not py_files:
        return {"score": 0, "files_checked": 0, "errors": 0, "message": "no .py files found"}
    errors = []
    for pf in py_files:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(pf)],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            errors.append({"file": pf.name, "error": result.stderr.strip()[:200]})
    score = 100 if not errors else max(0, 100 - len(errors) * 20)
    return {
        "score": score,
        "files_checked": len(py_files),
        "errors": errors,
        "failed_count": len(errors),
        "message": "all clean" if not errors else f"{len(errors)} file(s) failed syntax check",
    }


def check_brain_api() -> dict:
    """Probe Brain API and extract cache hit rate, cost trend, facts."""
    try:
        if urllib is None:
            raise ImportError("urllib unavailable")
        req = urllib.request.Request(METRICS_URL, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"score": 50, "cache_hit_rate": None, "today_cost": None, "facts_loaded": None, "message": str(e)}

    rates = data.get("rates", {})
    cache_rate = rates.get("cache_hit_rate_pct", 0.0)
    openrouter = data.get("openrouter", {})
    today_cost = openrouter.get("today_cost_usd", 0.0)
    total_queries = openrouter.get("total", 0)
    embedding_idx = data.get("embedding_index_size", 0)

    # Score: cache hit rate drives this
    if cache_rate >= 50:
        score = 95
    elif cache_rate >= 30:
        score = 80
    elif cache_rate >= 15:
        score = 65
    else:
        score = 45

    # Penalize if cost is high
    if today_cost and today_cost > 3.0:
        score = max(0, score - 20)
    elif today_cost and today_cost > 1.5:
        score = max(0, score - 10)

    return {
        "score": score,
        "cache_hit_rate": cache_rate,
        "today_cost": today_cost,
        "total_queries": total_queries,
        "facts_loaded": embedding_idx,
        "message": f"cache {cache_rate}%, cost ${today_cost}, facts {embedding_idx}",
    }


def check_external_api() -> dict:
    """Quick HTTP probe to OpenRouter to confirm external connectivity."""
    try:
        if urllib is None:
            raise ImportError("urllib unavailable")
        req = urllib.request.Request(OPENROUTER_PING_URL, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            if status == 200:
                return {"score": 100, "status": status, "message": "OpenRouter reachable"}
            elif status <= 299:
                return {"score": 90, "status": status, "message": f"OpenRouter status {status}"}
            else:
                return {"score": 50, "status": status, "message": f"OpenRouter status {status}"}
    except Exception as e:
        return {"score": 30, "status": None, "message": str(e)[:200]}


def assess() -> dict:
    code = check_code_changes()
    build = check_build_health()
    brain = check_brain_api()
    ext = check_external_api()

    scores = [code["score"], build["score"], brain["score"], ext["score"]]
    avg = sum(scores) / len(scores)

    if avg >= 85:
        risk = "low"
    elif avg >= 60:
        risk = "medium"
    else:
        risk = "high"

    report = {
        "timestamp": now_iso(),
        "risk_level": risk,
        "overall_score": round(avg, 1),
        "dimensions": {
            "code_changes": code,
            "build_health": build,
            "brain_api": brain,
            "external_api": ext,
        },
    }
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    return report


def main():
    report = assess()
    print(json.dumps(report, indent=2))
    # Exit 0 on low/medium risk, 1 on high risk (but don't block iteration, just warn)
    sys.exit(0)


if __name__ == "__main__":
    main()
