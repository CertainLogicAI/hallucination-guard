#!/usr/bin/env python3
"""
24/7 Auto-Iteration Engine — Simplified Entry Point.

Phase D cleanup: All phase logic has been extracted into dedicated modules:
  - gatekeeper.py     (Phase 0)
  - assessor.py       (Phase 1)
  - iteration_orchestrator.py (Phases 2–8, full pipeline wiring)
  - custodian.py      (Phase 7: git custody)
  - reporter.py       (Phase 8: human-readable reporting)

This file now only:
  1. Parses CLI arguments
  2. Loads config (from file or defaults)
  3. Dispatches to iteration_orchestrator.run_full_iteration()
  4. Handles daemon mode (sleep + loop)

Backward-compatibility:
  --mode daemon/once/benchmark    preserved
  --force                         preserved
  --dry-run                       preserved
  --target                          preserved
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from iteration_orchestrator import run_full_iteration

REPO_ROOT = Path(__file__).parent.parent
STATE_PATH = REPO_ROOT / ".iteration_state.json"
LOG_PATH = REPO_ROOT / ".iteration_log.jsonl"

DEFAULT_ACCURACY_TARGET = 0.95
DEFAULT_MAX_ITERATIONS = 12
CHECK_INTERVAL_SECONDS = 300  # 5 minutes


def _log_event(event: str, details: dict):
    """Append structured log entry."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **details,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[{entry['timestamp']}] {event}: {details}")


def _load_config(args) -> dict:
    """Build config dict from CLI args and optional config file."""
    config_path = REPO_ROOT / ".improve_config.json"
    config = {}
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            pass

    # CLI overrides
    config["target_accuracy"] = args.target
    config["max_iterations_per_day"] = config.get("max_iterations_per_day", DEFAULT_MAX_ITERATIONS)
    config["auto_commit"] = config.get("auto_commit", True)
    config["dry_run"] = args.dry_run
    return config


def _should_trigger_iteration() -> tuple[bool, str]:
    """Check if facts or code changed since last run."""
    import hashlib

    def _hash_file(path: Path) -> str:
        if not path.exists():
            return ""
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]

    def _hash_directory(dir_path: Path, pattern: str = "*.py") -> str:
        hashes = []
        for f in sorted(dir_path.rglob(pattern)):
            hashes.append(f"{f.relative_to(dir_path)}:{_hash_file(f)}")
        return hashlib.sha256("\n".join(hashes).encode()).hexdigest()[:16]

    facts_path = REPO_ROOT / "coder_facts_pack_v1.0.json"
    src_dir = REPO_ROOT / "src" / "hallucination_guard"

    state = {}
    if STATE_PATH.exists():
        with open(STATE_PATH, "r") as f:
            state = json.load(f)

    current_facts_hash = _hash_file(facts_path)
    current_code_hash = _hash_directory(src_dir)

    if current_facts_hash != state.get("last_facts_hash", ""):
        return True, f"facts changed"

    if current_code_hash != state.get("last_code_hash", ""):
        return True, f"code changed"

    return False, "no changes detected"


def daemon_mode(config: dict, force: bool = False, dry_run: bool = False):
    """Run continuous iteration loop."""
    target = config.get("target_accuracy", DEFAULT_ACCURACY_TARGET)
    max_iterations = config.get("max_iterations_per_day", DEFAULT_MAX_ITERATIONS)

    print("Starting 24/7 Auto-Iteration Engine...")
    print(f"Check interval: {CHECK_INTERVAL_SECONDS}s")
    print(f"Accuracy target: {target:.0%}")
    print(f"Max iterations/session: {max_iterations}")
    print(f"Log: {LOG_PATH}")
    print(f"State: {STATE_PATH}")
    if dry_run:
        print("[DRY RUN] No file changes will be applied.")
    print("\nPress Ctrl+C to stop.\n")

    iteration_count = 0
    try:
        while True:
            should_run, reason = _should_trigger_iteration()
            if should_run:
                _log_event("iteration_triggered", {"reason": reason})
                result = run_full_iteration(config, force=force, dry_run=dry_run)
                iteration_count += 1

                if result.get("aborted_at"):
                    _log_event("iteration_aborted", {
                        "phase": result["aborted_at"],
                        "summary": result.get("summary", {}),
                    })

                if iteration_count >= max_iterations:
                    _log_event("session_limit_reached", {
                        "iterations": iteration_count,
                        "best_accuracy": result.get("summary", {}).get("best_accuracy", 0.0),
                    })
                    print(f"\nReached max iterations ({max_iterations}). Restart to continue.")
                    break
            else:
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {reason}, sleeping...")

            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopping daemon...")
        _log_event("daemon_stopped", {"iterations": iteration_count})


def main():
    parser = argparse.ArgumentParser(description="24/7 Auto-Iteration Engine")
    parser.add_argument(
        "--mode",
        choices=["daemon", "once", "benchmark"],
        default="once",
        help="Run mode: daemon (continuous), once (single), benchmark (benchmark only)",
    )
    parser.add_argument(
        "--target", type=float, default=DEFAULT_ACCURACY_TARGET,
        help=f"Target accuracy (default: {DEFAULT_ACCURACY_TARGET})",
    )
    parser.add_argument("--force", action="store_true", help="Bypass gatekeeper rate limit")
    parser.add_argument("--dry-run", action="store_true", help="Run all phases but do not apply file changes")
    args = parser.parse_args()

    config = _load_config(args)

    if args.mode == "daemon":
        daemon_mode(config, force=args.force, dry_run=args.dry_run)
    elif args.mode == "once":
        result = run_full_iteration(config, force=args.force, dry_run=args.dry_run)
        summary = result.get("summary", {})
        if result.get("aborted_at"):
            print(f"Iteration aborted at: {result['aborted_at']}")
            sys.exit(1)
        print(f"\nDone. Accuracy: {summary.get('accuracy', 0):.1%}")
    elif args.mode == "benchmark":
        # Benchmark-only mode: run a single benchmark and print results
        import subprocess
        cmd = [
            sys.executable, "-c",
            "import sys; sys.path.insert(0, 'src'); sys.path.insert(0, '.'); "
            "import benchmarks.benchmark_suite as bm; bm.main()",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
        results_path = REPO_ROOT / "benchmarks" / "results.json"
        if results_path.exists():
            with open(results_path) as f:
                data = json.load(f)
            overall = data.get("overall", {})
            print(f"Accuracy: {overall.get('accuracy', 0):.1%}")
            print(f"Correct: {overall.get('correct', 0)}/{overall.get('total', 0)}")
        else:
            print("Benchmark failed to produce results")
            print(result.stderr[:500])


if __name__ == "__main__":
    main()
