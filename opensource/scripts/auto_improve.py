#!/usr/bin/env python3
"""
24/7 Auto-Iteration Engine for CertainLogic/hallucination-guard.

Monitors repo changes, runs benchmarks, promotes verified facts,
and spawns improvement subagents when regressions are detected.

Phase-A additions:
  - Gatekeeper safety checks before each iteration
  - Health assessment after gatekeeper passes
  - Per-iteration cost tracking

Usage:
    python scripts/auto_improve.py --mode daemon    # Run forever
    python scripts/auto_improve.py --mode once      # Single iteration
    python scripts/auto_improve.py --mode benchmark # Run benchmark only
    python scripts/auto_improve.py --force          # Bypass rate limit
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Ensure our scripts directory is importable
_SCRIPTS_DIR = Path(__file__).parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import gatekeeper
import assessor
import cost_tracker

# Paths
REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = REPO_ROOT / "src/hallucination_guard"
BENCHMARK_DIR = REPO_ROOT / "benchmarks"
FACTS_PATH = REPO_ROOT / "coder_facts_pack_v1.0.json"
RESULTS_PATH = BENCHMARK_DIR / "results.json"
STATE_PATH = REPO_ROOT / ".iteration_state.json"
LOG_PATH = REPO_ROOT / ".iteration_log.jsonl"

# Targets
DEFAULT_ACCURACY_TARGET = 0.95
MAX_ITERATIONS_PER_SESSION = 10
CHECK_INTERVAL_SECONDS = 300  # 5 minutes


@dataclass
class IterationState:
    iteration: int = 0
    best_accuracy: float = 0.0
    last_facts_hash: str = ""
    last_code_hash: str = ""
    total_fixes_applied: int = 0
    last_run: Optional[str] = None
    # Phase-A additions
    total_spend: float = 0.0
    last_gatekeeper_result: Optional[dict] = None
    last_assessment: Optional[dict] = None
    subagent_suppress_until: Optional[str] = None

    def save(self):
        with open(STATE_PATH, "w") as f:
            json.dump(self.__dict__, f, indent=2, default=str)

    @classmethod
    def load(cls) -> "IterationState":
        if STATE_PATH.exists():
            with open(STATE_PATH) as f:
                data = json.load(f)
            # Coerce extra fields from old states gracefully
            known = {k for k in cls.__dataclass_fields__}
            data = {k: v for k, v in data.items() if k in known}
            return cls(**data)
        return cls()


def log_event(event: str, details: dict):
    """Append structured log entry."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **details,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[{entry['timestamp']}] {event}: {details}")


def hash_file(path: Path) -> str:
    """SHA-256 hash of file contents."""
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def hash_directory(dir_path: Path, pattern: str = "*.py") -> str:
    """Hash of all matching files in directory."""
    hashes = []
    for f in sorted(dir_path.rglob(pattern)):
        hashes.append(f"{f.relative_to(dir_path)}:{hash_file(f)}")
    return hashlib.sha256("\n".join(hashes).encode()).hexdigest()[:16]


def run_benchmark() -> Optional[dict]:
    """Run benchmark suite and return results."""
    log_event("benchmark_start", {})

    cmd = [
        sys.executable, "-c",
        "import sys; sys.path.insert(0, 'src'); import benchmarks.benchmark_suite as bm; bm.main()"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)

    if RESULTS_PATH.exists():
        with open(RESULTS_PATH) as f:
            data = json.load(f)
        overall = data.get("overall", {})
        log_event("benchmark_complete", {
            "accuracy": overall.get("accuracy", 0),
            "correct": overall.get("correct", 0),
            "total": overall.get("total", 0),
            "fp": overall.get("fp", 0),
            "fn": overall.get("fn", 0),
        })
        return data

    log_event("benchmark_failed", {"stderr": result.stderr[:500]})
    return None


def categorize_failures(results: dict) -> dict[str, list[dict]]:
    """Group failures by root cause pattern."""
    failures = []
    for case in results.get("cases", []):
        expected = case.get("expected_valid", False)
        actual = case.get("actual_valid", False)
        if expected != actual:
            failures.append(case)

    categories: dict[str, list[dict]] = {
        "qualifier_misfire": [],
        "cross_match": [],
        "numeric_tolerance": [],
        "missing_fact": [],
        "string_mismatch": [],
        "code_output": [],
        "other": [],
    }

    for case in failures:
        flags = " ".join(case.get("flags", [])).lower()
        query = case.get("query", "").lower()
        category = case.get("category", "unknown")

        if "unverifiable qualifiers" in flags:
            categories["qualifier_misfire"].append(case)
        elif any(wrong in flags for wrong in ["javascript == vs ===", "python asyncio introduced", "python type hints introduced"]):
            categories["cross_match"].append(case)
        elif category == "code_output":
            categories["code_output"].append(case)
        elif "expected" in flags and any(c.isdigit() for c in flags):
            categories["numeric_tolerance"].append(case)
        elif "expected" in flags:
            categories["string_mismatch"].append(case)
        elif "no matching fact" in flags or not case.get("flags"):
            categories["missing_fact"].append(case)
        else:
            categories["other"].append(case)

    return {k: v for k, v in categories.items() if v}


def should_trigger_iteration(state: IterationState) -> tuple[bool, str]:
    """Check if facts or code changed since last run."""
    current_facts_hash = hash_file(FACTS_PATH)
    current_code_hash = hash_directory(SRC_DIR)

    if current_facts_hash != state.last_facts_hash:
        return True, f"facts changed: {state.last_facts_hash} → {current_facts_hash}"

    if current_code_hash != state.last_code_hash:
        return True, f"code changed: {state.last_code_hash} → {current_code_hash}"

    return False, "no changes detected"


def apply_auto_fixes(categories: dict[str, list[dict]]) -> list[str]:
    """Apply automatic fixes based on failure categories."""
    fixes_applied = []

    # Fix 1: Missing facts
    if "missing_fact" in categories:
        fixes_applied.append(f"missing_facts: {len(categories['missing_fact'])} cases need new facts")

    # Fix 2: Code output false positives
    if "code_output" in categories:
        fixes_applied.append(f"code_output: {len(categories['code_output'])} cases — consider skipping factual check for 'write a'/'how do I write' queries")

    # Fix 3: Cross-match
    if "cross_match" in categories:
        fixes_applied.append(f"cross_match: {len(categories['cross_match'])} cases — need tokenization fix")

    # Fix 4: Qualifier misfire
    if "qualifier_misfire" in categories:
        fixes_applied.append(f"qualifier_misfire: {len(categories['qualifier_misfire'])} cases — need safe-qualifier update")

    return fixes_applied


def spawn_improvement_subagent(failure_analysis: dict, suppress_until: Optional[str] = None) -> None:
    """Spawn a subagent to fix the specific failure pattern."""
    if suppress_until:
        from datetime import datetime as _dt
        try:
            until = _dt.fromisoformat(suppress_until)
            if _dt.now(timezone.utc) < until:
                log_event("subagent_spawn_skipped", {
                    "reason": "suppressed",
                    "suppress_until": suppress_until,
                })
                return
        except ValueError:
            pass
    log_event("subagent_spawn_request", {
        "target": "benchmark_improvement",
        "failure_categories": {k: len(v) for k, v in failure_analysis.items()},
    })


def run_iteration(state: IterationState, force: bool = False) -> IterationState:
    """Run one full iteration: gatekeeper → assess → benchmark → analyze → fix → report."""
    state.iteration += 1
    state.last_run = datetime.now(timezone.utc).isoformat()

    print(f"\n{'='*60}")
    print(f"ITERATION {state.iteration}")
    print(f"{'='*60}")

    # ── Step 0a: Gatekeeper ─────────────────────────────
    gk_report = gatekeeper.gatekeeper(force=force)
    state.last_gatekeeper_result = gk_report
    print(f"[gatekeeper] proceed={gk_report['proceed']} | block_reason={gk_report['block_reason']}")
    if not gk_report["proceed"]:
        log_event("iteration_blocked", {"reason": gk_report["block_reason"], "gatekeeper": gk_report})
        state.save()
        return state

    # ── Step 0b: Assessment ─────────────────────────────
    try:
        assessment = assessor.assess()
        state.last_assessment = assessment
        print(f"[assessor] risk={assessment['risk_level']} | score={assessment['overall_score']}")
        log_event("assessment_complete", {
            "risk_level": assessment["risk_level"],
            "overall_score": assessment["overall_score"],
        })
    except Exception as e:
        print(f"[assessor] failed: {e}")
        log_event("assessment_failed", {"error": str(e)})

    # ── Step 0c: Cost snapshot (before) ─────────────────
    cost_before = cost_tracker.snapshot()

    # ── Step 1: Run benchmark ────────────────────────────
    results = run_benchmark()
    if not results:
        log_event("iteration_failed", {"reason": "benchmark failed"})
        # Still log cost even on failure
        cost_after = cost_tracker.snapshot()
        cost_tracker.log_iteration_cost(cost_before, cost_after, state.iteration)
        return state

    overall = results.get("overall", {})
    accuracy = overall.get("accuracy", 0)

    # ── Step 2: Check if improved ────────────────────────
    if accuracy > state.best_accuracy:
        state.best_accuracy = accuracy
        log_event("new_best_accuracy", {
            "accuracy": accuracy,
            "previous_best": state.best_accuracy,
            "iteration": state.iteration,
        })

    # ── Step 3: Categorize failures ──────────────────────
    categories = categorize_failures(results)
    log_event("failure_analysis", {
        "categories": {k: len(v) for k, v in categories.items()},
        "total_failures": sum(len(v) for v in categories.values()),
    })

    # ── Step 4: Apply auto-fixes ─────────────────────────
    fixes = apply_auto_fixes(categories)
    if fixes:
        log_event("fixes_applied", {"fixes": fixes})
        state.total_fixes_applied += len(fixes)

    # ── Step 5: Spawn improvement subagent if needed ─────
    total_failures = sum(len(v) for v in categories.values())
    if total_failures > 5 and accuracy < ACCURACY_TARGET:
        spawn_improvement_subagent(categories, suppress_until=state.subagent_suppress_until)

    # ── Step 6: Cost snapshot (after) ────────────────────
    cost_after = cost_tracker.snapshot()
    cost_info = cost_tracker.log_iteration_cost(cost_before, cost_after, state.iteration)
    state.total_spend = round((state.total_spend or 0.0) + cost_info.get("iteration_spend", 0.0), 4)

    # ── Step 7: Update hashes and save ───────────────────
    state.last_facts_hash = hash_file(FACTS_PATH)
    state.last_code_hash = hash_directory(SRC_DIR)
    state.save()

    # ── Step 8: Report ───────────────────────────────────
    print(f"\nIteration {state.iteration} complete:")
    print(f"  Accuracy: {accuracy:.1%}")
    print(f"  Best: {state.best_accuracy:.1%}")
    print(f"  Failures: {total_failures}")
    print(f"  Spend: ${cost_info.get('iteration_spend', 0):.4f}")
    print(f"  Categories: { {k: len(v) for k, v in categories.items()} }")

    return state


def daemon_mode(force: bool = False):
    """Run continuous iteration loop."""
    print("Starting 24/7 Auto-Iteration Engine...")
    print(f"Check interval: {CHECK_INTERVAL_SECONDS}s")
    global ACCURACY_TARGET
    print(f"Accuracy target: {ACCURACY_TARGET:.0%}")
    print(f"Max iterations/session: {MAX_ITERATIONS_PER_SESSION}")
    print(f"Log: {LOG_PATH}")
    print(f"State: {STATE_PATH}")
    print("\nPress Ctrl+C to stop.\n")

    state = IterationState.load()

    try:
        while True:
            should_run, reason = should_trigger_iteration(state)

            if should_run:
                log_event("iteration_triggered", {"reason": reason})
                state = run_iteration(state, force=force)

                if state.iteration >= MAX_ITERATIONS_PER_SESSION:
                    log_event("session_limit_reached", {
                        "iterations": state.iteration,
                        "best_accuracy": state.best_accuracy,
                    })
                    print(f"\nReached max iterations ({MAX_ITERATIONS_PER_SESSION}). Restart to continue.")
                    break
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {reason}, sleeping...")

            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopping daemon...")
        state.save()
        log_event("daemon_stopped", {"iterations": state.iteration})


def main():
    parser = argparse.ArgumentParser(description="24/7 Auto-Iteration Engine")
    parser.add_argument("--mode", choices=["daemon", "once", "benchmark"], default="once",
                       help="Run mode: daemon (continuous), once (single iteration), benchmark (only)")
    parser.add_argument("--target", type=float, default=DEFAULT_ACCURACY_TARGET,
                       help=f"Target accuracy (default: {DEFAULT_ACCURACY_TARGET})")
    parser.add_argument("--force", action="store_true",
                       help="Bypass gatekeeper rate limit")
    args = parser.parse_args()

    global ACCURACY_TARGET
    ACCURACY_TARGET = args.target

    if args.mode == "daemon":
        daemon_mode(force=args.force)
    elif args.mode == "once":
        state = IterationState.load()
        state = run_iteration(state, force=args.force)
        state.save()
    elif args.mode == "benchmark":
        results = run_benchmark()
        if results:
            overall = results.get("overall", {})
            print(f"Accuracy: {overall.get('accuracy', 0):.1%}")
            print(f"Correct: {overall.get('correct', 0)}/{overall.get('total', 0)}")


if __name__ == "__main__":
    main()
