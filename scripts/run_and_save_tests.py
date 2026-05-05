#!/usr/bin/env python3
"""
Benchmark/Test Result Preservation System
Never lose test results again.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
RESULTS_DIR = WORKSPACE / "test-results"
LATEST_LINK = RESULTS_DIR / "latest"

def get_git_info():
    """Get current commit hash and branch."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=WORKSPACE, timeout=5
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=WORKSPACE, timeout=5
        ).stdout.strip()
        return {"commit": commit, "branch": branch}
    except Exception:
        return {"commit": "unknown", "branch": "unknown"}

def run_tests(test_path: str = "tests/"):
    """Run pytest and capture output."""
    print(f"Running tests: {test_path}")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
        capture_output=True, text=True, cwd=WORKSPACE, timeout=120
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

def save_results(test_name: str, result: dict):
    """Save test results with metadata."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    run_dir = RESULTS_DIR / f"{timestamp}-{test_name}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Test output
    (run_dir / "test_output.txt").write_text(result["stdout"])
    if result.get("stderr"):
        (run_dir / "test_stderr.txt").write_text(result["stderr"])

    # Metadata
    git_info = get_git_info()
    metadata = {
        "timestamp": timestamp,
        "test_name": test_name,
        "git": git_info,
        "python_version": sys.version,
        "workspace": str(WORKSPACE),
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, default=str))

    # Summary
    summary = parse_summary(result["stdout"])
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    # Update latest symlink
    if LATEST_LINK.exists() or LATEST_LINK.is_symlink():
        LATEST_LINK.unlink()
    LATEST_LINK.symlink_to(run_dir.name)

    print(f"Saved to: {run_dir}")
    print(f"Summary: {summary['passed']} passed, {summary['failed']} failed, {summary['time']}")
    return run_dir

def parse_summary(stdout: str):
    """Parse pytest summary line."""
    lines = stdout.strip().split("\n")
    summary = {"passed": 0, "failed": 0, "error": 0, "skipped": 0, "time": "unknown"}
    for line in lines:
        if "passed" in line and ("failed" in line or "error" in line or " in" in line):
        # e.g., "26 passed in 0.07s" OR "26 passed, 2 failed in 0.12s"
            import re
            m = re.search(r'(\d+) passed', line)
            if m:
                summary["passed"] = int(m.group(1))
            m = re.search(r'(\d+) failed', line)
            if m:
                summary["failed"] = int(m.group(1))
            m = re.search(r'in ([\d.]+s)', line)
            if m:
                summary["time"] = m.group(1)
        if "FAILED" in line:
            summary["failed"] += 1
    return summary

def commit_results(run_dir: Path):
    """Auto-commit test results to git."""
    try:
        subprocess.run(["git", "add", str(run_dir), str(LATEST_LINK)],
                      capture_output=True, cwd=WORKSPACE, timeout=10)
        commit_result = subprocess.run(
            ["git", "commit", "-m", f"test-results: {run_dir.name}"],
            capture_output=True, cwd=WORKSPACE, timeout=10
        )
        if commit_result.returncode == 0:
            print("Committed to git")
            return True
        else:
            print("Nothing to commit (may already be tracked)")
            return False
    except Exception as e:
        print(f"Git commit failed: {e}")
        return False

def main():
    test_path = sys.argv[1] if len(sys.argv) > 1 else "tests/"
    test_name = Path(test_path).stem

    result = run_tests(test_path)
    run_dir = save_results(test_name, result)
    commit_results(run_dir)

    if result["returncode"] != 0:
        print("\n⚠️ Tests failed — see test_output.txt for details")
        sys.exit(1)
    else:
        print("\n✅ All tests passed and saved")

if __name__ == "__main__":
    main()
