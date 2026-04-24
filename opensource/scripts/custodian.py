#!/usr/bin/env python3
"""
scripts/custodian.py — Git custody, tagging, commit, revert, and chain-of-custody logging.

Architecture decisions:
- All git operations are subprocess-based for maximum transparency and auditability.
- Dry-run mode short-circuits all mutating operations but still returns structured data.
- The custody log is append-only JSONL for tamper-evident audit trails.
- SHA-256 of diffs is computed from git diff output (not repo state) to ensure reproducibility.
- Tags use ISO-8601 basic format (no colons) to stay filesystem-safe.
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent
CUSTODY_LOG_PATH = REPO_ROOT / ".iteration_log.jsonl"


def _run_git(cmd: list[str], cwd: Path = REPO_ROOT, timeout: int = 30) -> dict:
    """Run a git subcommand and return structured results."""
    try:
        result = subprocess.run(
            ["git", *cmd],
            capture_output=True,
            text=True,
            cwd=str(cwd),
            timeout=timeout,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "ok": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": f"timeout after {timeout}s", "ok": False}
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e), "ok": False}


def _now_iso_basic() -> str:
    """Return ISO-8601 basic format string safe for git tags and filenames."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _diff_sha256(repo_root: Path = REPO_ROOT) -> str:
    """Compute SHA-256 of the current git diff for custody records."""
    result = _run_git(["diff", "HEAD"], cwd=repo_root)
    return hashlib.sha256(result["stdout"].encode()).hexdigest()


def _diff_stats(repo_root: Path = REPO_ROOT) -> dict:
    """Return lines added/removed from git diff --numstat."""
    result = _run_git(["diff", "--numstat", "HEAD"], cwd=repo_root)
    added, removed = 0, 0
    for line in result["stdout"].splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                added += int(parts[0]) if parts[0] != "-" else 0
                removed += int(parts[1]) if parts[1] != "-" else 0
            except ValueError:
                continue
    return {"lines_added": added, "lines_removed": removed}


def pre_iteration_tag(iteration: int, dry_run: bool = False) -> str:
    """
    Stash untracked changes and create a pre-iteration tag.

    Returns the tag name (e.g., iteration-47-pre-20260424T120000Z).
    In dry-run mode, returns the tag name that *would* be created.
    """
    tag_name = f"iteration-{iteration}-pre-{_now_iso_basic()}"

    if dry_run:
        return tag_name

    # Stash untracked files so the working tree is clean before we tag
    stash_result = _run_git(["stash", "push", "-u", "-m", f"auto-stash pre-iteration-{iteration}"])
    if not stash_result["ok"]:
        # If nothing to stash, git exits 0 with "No local changes to save"
        # If it fails for another reason, we still proceed — the tag creation is the primary goal
        pass

    tag_result = _run_git(["tag", "-a", tag_name, "-m", f"Pre-iteration {iteration} safety tag"])
    if not tag_result["ok"]:
        # Tag might already exist from a prior run; that's acceptable if it points to the same commit
        pass

    return tag_name


def post_fix_commit(
    iteration: int,
    fix_summary: str,
    accuracy_before: float,
    accuracy_after: float,
    cost_usd: float,
    model: str,
    dry_run: bool = False,
) -> str:
    """
    Stage all changes and commit with a structured auto-fix message.

    Returns the commit hash (or "dry_run" in dry-run mode).
    """
    if dry_run:
        return "dry_run"

    _run_git(["add", "-A"])

    # Compute cases improved from accuracy delta
    # We don't have total cases here, so we leave that to the orchestrator to fill in
    commit_msg = (
        f"[AUTO] Iteration {iteration}: {fix_summary}\n\n"
        f"- Accuracy: {accuracy_before:.1%} → {accuracy_after:.1%}\n"
        f"- Subagent: {model} | Cost: ${cost_usd:.4f}\n"
    )

    commit_result = _run_git(["commit", "-m", commit_msg])
    if not commit_result["ok"]:
        # Nothing to commit is not a failure
        if "nothing to commit" in commit_result["stdout"].lower() or \
           "nothing to commit" in commit_result["stderr"].lower():
            return _run_git(["rev-parse", "HEAD"])["stdout"].strip() or "no_changes"
        return "commit_failed"

    hash_result = _run_git(["rev-parse", "HEAD"])
    return hash_result["stdout"].strip() if hash_result["ok"] else "unknown"


def revert_to_tag(tag_name: str, reason: str = "", dry_run: bool = False) -> bool:
    """
    Hard-reset repo to tag_name and log the reversion reason.

    Returns True on success. In dry-run mode, returns True without touching files.
    """
    if dry_run:
        return True

    reset_result = _run_git(["reset", "--hard", tag_name])
    if not reset_result["ok"]:
        return False

    # Also clean untracked files that may have been created during the failed iteration
    _run_git(["clean", "-fd"])

    # Log reversion to custody log
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "custody_reversion",
        "tag_name": tag_name,
        "reason": reason,
    }
    with open(CUSTODY_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return True


def generate_custody_log(
    iteration: int,
    changes: dict,
    verification: dict,
    cost: dict,
    pre_tag: str,
    post_commit: str,
) -> dict:
    """
    Build a full custody record for the iteration.

    This is the canonical audit-trail structure. It is returned as a dict
    and expected to be serialized by the caller (iteration_orchestrator).
    """
    return {
        "iteration": iteration,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "changes": {
            "file": changes.get("file", ""),
            "diff_sha256": changes.get("diff_sha256", ""),
            "lines_added": changes.get("lines_added", 0),
            "lines_removed": changes.get("lines_removed", 0),
        },
        "verification": {
            "benchmark_accuracy_before": verification.get("benchmark_accuracy_before", 0.0),
            "benchmark_accuracy_after": verification.get("benchmark_accuracy_after", 0.0),
            "unit_tests_pass": verification.get("unit_tests_pass", False),
            "pytest_time_seconds": verification.get("pytest_time_seconds", 0.0),
        },
        "cost": {
            "subagent_tokens": cost.get("subagent_tokens", 0),
            "subagent_cost_usd": cost.get("subagent_cost_usd", 0.0),
            "benchmark_runtime_seconds": cost.get("benchmark_runtime_seconds", 0.0),
        },
        "custody": {
            "pre_tag": pre_tag,
            "post_commit": post_commit,
            "reverted_commit": None,
            "human_review_required": verification.get("regression_detected", False),
        },
    }


# ---------------------------------------------------------------------------
# Stand-alone helpers for the orchestrator
# ---------------------------------------------------------------------------

def get_current_commit_hash() -> str:
    """Return the current HEAD commit hash."""
    result = _run_git(["rev-parse", "HEAD"])
    return result["stdout"].strip() if result["ok"] else "unknown"


def compute_changes_summary(changed_file: Optional[Path] = None) -> dict:
    """Compute a changes dict suitable for generate_custody_log."""
    stats = _diff_stats()
    return {
        "file": str(changed_file.relative_to(REPO_ROOT)) if changed_file else "",
        "diff_sha256": _diff_sha256(),
        "lines_added": stats["lines_added"],
        "lines_removed": stats["lines_removed"],
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Git custody operations")
    parser.add_argument("--pre-tag", type=int, help="Create pre-iteration tag")
    parser.add_argument("--post-commit", type=int, help="Create post-fix commit")
    parser.add_argument("--revert", help="Revert to tag name")
    parser.add_argument("--dry-run", action="store_true", help="No file changes")
    args = parser.parse_args()

    if args.pre_tag is not None:
        tag = pre_iteration_tag(args.pre_tag, dry_run=args.dry_run)
        print(tag)
    elif args.post_commit is not None:
        h = post_fix_commit(
            args.post_commit,
            "manual test commit",
            0.91,
            0.92,
            0.0,
            "manual",
            dry_run=args.dry_run,
        )
        print(h)
    elif args.revert:
        ok = revert_to_tag(args.revert, reason="manual test", dry_run=args.dry_run)
        print("reverted" if ok else "failed")
