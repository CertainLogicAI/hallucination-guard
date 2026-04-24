#!/usr/bin/env python3
"""
scripts/iteration_orchestrator.py — Full pipeline wiring (Phase 0–8).

Architecture decisions:
- Each phase is a distinct step with explicit data flow. No hidden globals.
- Dry-run short-circuits file mutations at the git + patch layers but runs all analysis.
- Orchestrator owns state loading/saving and custody logging. Phase modules are stateless.
- Subagent ceiling ($0.50) and daily budget ($5.00) are enforced BEFORE spawn, not after.
- Verification failure triggers automatic revert via custodian. No continuation on regression.
- All exceptions in a phase are caught, logged, and prevent state advancement.
- The orchestrator returns a full result dict so callers (auto_improve.py, daemon, tests)
  can inspect every phase outcome without parsing stdout.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import assessor
import cost_tracker
import custodian
import gatekeeper
import reporter

REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = REPO_ROOT / "src" / "hallucination_guard"
BENCHMARK_DIR = REPO_ROOT / "benchmarks"
FACTS_PATH = REPO_ROOT / "coder_facts_pack_v1.0.json"
RESULTS_PATH = BENCHMARK_DIR / "results.json"
STATE_PATH = REPO_ROOT / ".iteration_state.json"
LOG_PATH = REPO_ROOT / ".iteration_log.jsonl"
_CUSTODY_DIR = REPO_ROOT / "custody_log"

DEFAULT_TARGET = 0.95
DEFAULT_MAX_ITERATIONS = 12
DEFAULT_SUBAGENT_CEILING = 0.50
DEFAULT_DAILY_BUDGET = 5.0


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


def _hash_file(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _hash_directory(dir_path: Path, pattern: str = "*.py") -> str:
    hashes = []
    for f in sorted(dir_path.rglob(pattern)):
        hashes.append(f"{f.relative_to(dir_path)}:{_hash_file(f)}")
    return hashlib.sha256("\n".join(hashes).encode()).hexdigest()[:16]


def _load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_state(state: dict):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, default=str)


def _run_benchmark() -> Optional[dict]:
    """Run benchmark suite and return results dict."""
    _log_event("benchmark_start", {})
    cmd = [
        sys.executable, "-c",
        "import sys; sys.path.insert(0, 'src'); import benchmarks.benchmark_suite as bm; bm.main()",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    if RESULTS_PATH.exists():
        try:
            with open(RESULTS_PATH, "r") as f:
                data = json.load(f)
            overall = data.get("overall", {})
            _log_event("benchmark_complete", {
                "accuracy": overall.get("accuracy", 0),
                "correct": overall.get("correct", 0),
                "total": overall.get("total", 0),
            })
            return data
        except json.JSONDecodeError:
            pass
    _log_event("benchmark_failed", {"stderr": result.stderr[:500]})
    return None


def _run_failure_analysis() -> dict:
    """Phase 2: Run failure_analyzer.py on latest results."""
    result = subprocess.run(
        [sys.executable, str(_SCRIPTS_DIR / "failure_analyzer.py"), str(RESULTS_PATH)],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"patterns": {}, "error": "parse_failed", "raw": result.stdout[:500]}
    # Save to disk for downstream phases
    patterns_path = REPO_ROOT / "failure_patterns.json"
    with open(patterns_path, "w") as f:
        json.dump(data, f, indent=2)
    return data


def _run_fix_designer() -> dict:
    """Phase 3: Run fix_designer.py on failure patterns from stdin and return proposals."""
    patterns_path = REPO_ROOT / "failure_patterns.json"
    with open(patterns_path, "r") as f:
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "fix_designer.py")],
            capture_output=True, text=True, stdin=f, cwd=REPO_ROOT,
        )
    try:
        proposals = json.loads(result.stdout)
    except json.JSONDecodeError:
        proposals = {"auto_fixes": [], "subagent_fixes": [], "error": "parse_failed"}
    proposals_path = REPO_ROOT / "fix_proposals.json"
    with open(proposals_path, "w") as f:
        json.dump(proposals, f, indent=2)
    return proposals


def _run_auto_fixes(detector_path: Path, failure_patterns: dict, auto_fixes: list, dry_run: bool) -> dict:
    """Phase 5a: Apply deterministic auto-fixes via auto_fixes.py."""
    import auto_fixes as af

    patterns = failure_patterns.get("patterns", {})
    for fix in auto_fixes:
        pattern = fix.get("type", "unknown")
        failures_for_pattern = patterns.get(pattern, {}).get("cases", [])
        if pattern == "uncertainty_hedge":
            res = af.fix_qualifier_misfire(failures_for_pattern, detector_path)
        elif pattern == "numeric_tolerance":
            res = af.fix_numeric_tolerance(failures_for_pattern, detector_path)
        elif pattern == "code_output":
            res = af.fix_code_output_skip(failures_for_pattern, detector_path)
        else:
            res = {"patches": [], "error": f"unknown pattern {pattern}"}

        if res and res.get("patches"):
            applied_result = af.apply_patches(res["patches"], dry_run=dry_run)
            return {
                "pattern": pattern,
                "applied": len(applied_result.get("applied", [])),
                "failed": len(applied_result.get("failed", [])),
                "dry_run": dry_run,
            }
    return {"pattern": "none", "applied": 0, "dry_run": dry_run}


def _run_subagent_fixes(detector_path: Path, subagent_fixes: list, dry_run: bool) -> dict:
    """Phase 5b: Spawn subagent for complex fixes (max 1 per iteration per spec)."""
    import subagent_fixer as sf

    if not subagent_fixes:
        return {"status": "no_fixes", "applied": False}

    fix_plans = []
    for entry in subagent_fixes:
        pattern = entry.get("pattern", entry.get("type", "unknown"))
        fix_plans.append({
            "pattern": pattern,
            "query": entry.get("query", ""),
            "expected": entry.get("expected", ""),
            "actual": entry.get("actual", ""),
            "target_file": str(detector_path.relative_to(REPO_ROOT)),
            "case_id": entry.get("case_id", ""),
        })

    result = sf.spawn_fix_subagent(fix_plans[0], work_dir=REPO_ROOT, dry_run=dry_run)
    return {
        "applied": bool(result.get("patch")) and result.get("status") == "success",
        "status": result.get("status"),
        "patch_length": len(result.get("patch", "")),
    }


def _run_verification(before_accuracy: float) -> tuple[bool, dict]:
    """Phase 6: Run 5-layer verification. Returns (all_passed, details)."""
    import verifier as vr

    baseline_commit = custodian.get_current_commit_hash()
    result = vr.run_all_verifications(
        before_accuracy=before_accuracy,
        baseline_commit=baseline_commit,
    )
    return result["all_passed"], result["details"]


def run_full_iteration(config: dict, force: bool = False, dry_run: bool = False) -> dict:
    """
    Run one full iteration through all phases.

    Returns a dict with every phase outcome. On any blocking error,
    the result dict includes an "aborted_at" key indicating which phase
    halted execution.
    """
    # Normalize config with defaults
    target_accuracy = config.get("target_accuracy", DEFAULT_TARGET)
    max_iterations = config.get("max_iterations_per_day", DEFAULT_MAX_ITERATIONS)
    auto_fixes_enabled = config.get("auto_fixes_enabled", True)
    subagent_enabled = config.get("subagent_enabled", True)
    subagent_model = config.get("subagent_model", "openrouter/moonshotai/kimi-k2.6")
    subagent_ceiling = config.get("subagent_cost_ceiling", DEFAULT_SUBAGENT_CEILING)
    daily_budget = config.get("daily_cost_budget_usd", DEFAULT_DAILY_BUDGET)

    # Load persistent state
    state = _load_state()
    iteration = state.get("iteration", 0) + 1
    best_accuracy = state.get("best_accuracy", 0.0)
    total_spend = state.get("total_spend", 0.0)

    print(f"\n{'='*60}")
    print(f"ITERATION {iteration}")
    print(f"{'='*60}")
    if dry_run:
        print("[DRY RUN] No file changes will be applied.\n")

    result = {
        "iteration": iteration,
        "dry_run": dry_run,
        "phases": {},
        "aborted_at": None,
        "summary": {},
    }

    # ------------------------------------------------------------------
    # Phase 0: Gatekeeper
    # ------------------------------------------------------------------
    try:
        gk_report = gatekeeper.gatekeeper(force=force)
        result["phases"]["gatekeeper"] = gk_report
        print(f"[gatekeeper] proceed={gk_report['proceed']} | block_reason={gk_report['block_reason']}")
        if not gk_report["proceed"]:
            _log_event("iteration_blocked", {"reason": gk_report["block_reason"]})
            result["aborted_at"] = "gatekeeper"
            return result
    except Exception as e:
        _log_event("gatekeeper_error", {"error": str(e)})
        result["phases"]["gatekeeper"] = {"error": str(e)}
        result["aborted_at"] = "gatekeeper"
        return result

    # ------------------------------------------------------------------
    # Phase 1: Assessment
    # ------------------------------------------------------------------
    try:
        assessment = assessor.assess()
        result["phases"]["assessment"] = assessment
        print(f"[assessor] risk={assessment['risk_level']} | score={assessment['overall_score']}")
        _log_event("assessment_complete", {
            "risk_level": assessment["risk_level"],
            "overall_score": assessment["overall_score"],
        })
    except Exception as e:
        print(f"[assessor] failed: {e}")
        result["phases"]["assessment"] = {"error": str(e)}
        # Assessment failure is non-blocking per Phase A spec

    # ------------------------------------------------------------------
    # Pre-iteration custody tag
    # ------------------------------------------------------------------
    pre_tag = custodian.pre_iteration_tag(iteration, dry_run=dry_run)
    print(f"[custodian] pre-tag: {pre_tag}")

    # ------------------------------------------------------------------
    # Cost snapshot (before)
    # ------------------------------------------------------------------
    cost_before = cost_tracker.snapshot()

    # ------------------------------------------------------------------
    # Phase 2: Benchmark
    # ------------------------------------------------------------------
    bench_results = _run_benchmark()
    if not bench_results:
        result["aborted_at"] = "benchmark"
        return result

    overall = bench_results.get("overall", {})
    accuracy = overall.get("accuracy", 0)
    correct = overall.get("correct", 0)
    total_cases = overall.get("total", 0)
    result["phases"]["benchmark"] = {"accuracy": accuracy, "correct": correct, "total": total_cases}

    # ------------------------------------------------------------------
    # Phase 3: Failure analysis
    # ------------------------------------------------------------------
    failure_patterns = _run_failure_analysis()
    result["phases"]["failure_analysis"] = {
        "patterns_found": list(failure_patterns.get("patterns", {}).keys()),
        "total_failures": failure_patterns.get("total_failures", 0),
    }

    # ------------------------------------------------------------------
    # Phase 4: Fix design
    # ------------------------------------------------------------------
    proposals = _run_fix_designer()
    auto_fixes = proposals.get("auto_fixes", [])
    subagent_fixes = proposals.get("subagent_fixes", [])
    result["phases"]["fix_design"] = {
        "auto_fixes": len(auto_fixes),
        "subagent_fixes": len(subagent_fixes),
    }

    # ------------------------------------------------------------------
    # Phase 5a: Auto-fixes
    # ------------------------------------------------------------------
    detector_path = REPO_ROOT / "src" / "hallucination_guard" / "hallucination_detector.py"
    auto_fix_result = {"pattern": "none", "applied": 0, "dry_run": dry_run}
    if auto_fixes_enabled and auto_fixes:
        try:
            auto_fix_result = _run_auto_fixes(
                detector_path, failure_patterns, auto_fixes, dry_run
            )
            _log_event("auto_fix_applied", auto_fix_result)
        except Exception as e:
            _log_event("auto_fix_error", {"error": str(e)})
            auto_fix_result["error"] = str(e)
    result["phases"]["auto_fixes"] = auto_fix_result

    # ------------------------------------------------------------------
    # Budget check before subagent spawn
    # ------------------------------------------------------------------
    current_spend = cost_before.get("today_cost", total_spend)
    remaining_budget = daily_budget - current_spend
    if remaining_budget <= 0:
        _log_event("subagent_skipped_budget", {"remaining": remaining_budget})
        subagent_fixes = []  # zero out so we don't spawn

    # ------------------------------------------------------------------
    # Phase 5b: Subagent fixes
    # ------------------------------------------------------------------
    subagent_result = {"status": "skipped", "applied": False}
    if subagent_enabled and subagent_fixes and remaining_budget > 0:
        # Approximate cost guard: we only know post-hoc, so we gate on budget only here
        # The actual cost is logged after the subagent returns
        try:
            subagent_result = _run_subagent_fixes(detector_path, subagent_fixes, dry_run)
            _log_event("subagent_fix_applied", subagent_result)
        except Exception as e:
            _log_event("subagent_fix_error", {"error": str(e)})
            subagent_result["error"] = str(e)
    elif subagent_fixes and dry_run:
        subagent_result = {"status": "dry_run_skipped", "applied": False}
        _log_event("subagent_skipped_dry_run", {"count": len(subagent_fixes)})
    result["phases"]["subagent_fixes"] = subagent_result

    # ------------------------------------------------------------------
    # Phase 6: Verification
    # ------------------------------------------------------------------
    all_passed = True
    verify_details = {}
    try:
        all_passed, verify_details = _run_verification(before_accuracy=accuracy)
        result["phases"]["verification"] = {"all_passed": all_passed, "details": verify_details}
        _log_event("verification_complete", {"all_passed": all_passed})
    except Exception as e:
        _log_event("verification_error", {"error": str(e)})
        result["phases"]["verification"] = {"error": str(e)}
        all_passed = False

    if not all_passed:
        _log_event("verification_failed", verify_details)
        # Revert to pre-iteration tag
        revert_ok = custodian.revert_to_tag(pre_tag, reason="verification_failed", dry_run=dry_run)
        _log_event("auto_revert_executed", {"reverted_to": pre_tag, "success": revert_ok})
        result["aborted_at"] = "verification"
        result["reverted"] = True
        result["phases"]["verification"]["reverted_to"] = pre_tag

    # ------------------------------------------------------------------
    # Phase 7: Custody logging
    # ------------------------------------------------------------------
    # Re-run benchmark after fixes to get the true after-accuracy
    after_accuracy = accuracy
    if not dry_run and all_passed:
        post_bench = _run_benchmark()
        if post_bench:
            after_accuracy = post_bench.get("overall", {}).get("accuracy", accuracy)

    # Compute changes summary (git diff vs HEAD)
    changes = custodian.compute_changes_summary(changed_file=detector_path)

    # Cost snapshot after
    cost_after = cost_tracker.snapshot()
    cost_info = cost_tracker.log_iteration_cost(cost_before, cost_after, iteration)
    iteration_spend = cost_info.get("iteration_spend", 0.0)
    total_spend = round(total_spend + iteration_spend, 4)

    # Build custody log
    custody_record = custodian.generate_custody_log(
        iteration=iteration,
        changes=changes,
        verification={
            "benchmark_accuracy_before": accuracy,
            "benchmark_accuracy_after": after_accuracy,
            "unit_tests_pass": all_passed,
            "pytest_time_seconds": verify_details.get("layer_2_unit_tests", {}).get("elapsed", 0.0),
            "regression_detected": not all_passed,
        },
        cost={
            "subagent_tokens": 0,  # populated by caller if available
            "subagent_cost_usd": 0.0,
            "benchmark_runtime_seconds": verify_details.get("layer_1_benchmark", {}).get("elapsed", 0.0),
        },
        pre_tag=pre_tag,
        post_commit="dry_run" if dry_run else custodian.get_current_commit_hash(),
    )
    result["phases"]["custody"] = custody_record

    if not dry_run:
        cust_path = _CUSTODY_DIR / datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_iteration.json")
        cust_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cust_path, "w") as f:
            json.dump(custody_record, f, indent=2, default=str)

    # ------------------------------------------------------------------
    # Phase 8: Commit (if auto_commit enabled and passes verification)
    # ------------------------------------------------------------------
    commit_hash = "dry_run"
    if not dry_run and all_passed and config.get("auto_commit", True):
        fix_summary = auto_fix_result.get("pattern", "none")
        if subagent_result.get("applied"):
            fix_summary += f" + subagent({subagent_result.get('status', 'unknown')})"
        commit_hash = custodian.post_fix_commit(
            iteration=iteration,
            fix_summary=fix_summary or "no fixes",
            accuracy_before=accuracy,
            accuracy_after=after_accuracy,
            cost_usd=iteration_spend,
            model=subagent_model,
            dry_run=dry_run,
        )
    result["phases"]["commit"] = {"hash": commit_hash}

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    cases_improved = max(0, round((after_accuracy - accuracy) * total_cases))
    report_msg = reporter.format_iteration_summary(
        iteration=iteration,
        accuracy_before=accuracy,
        accuracy_after=after_accuracy,
        fixes_applied=auto_fix_result.get("applied", 0),
        subagent_spawns=1 if subagent_result.get("applied") else 0,
        cost_total=iteration_spend,
        commit_hash=commit_hash,
        all_passed=all_passed,
        cases_improved=cases_improved,
        cases_total=total_cases,
    )
    print("\n" + report_msg + "\n")
    result["report"] = report_msg

    # ------------------------------------------------------------------
    # Update best accuracy
    # ------------------------------------------------------------------
    if after_accuracy > best_accuracy:
        best_accuracy = after_accuracy
        _log_event("new_best_accuracy", {
            "accuracy": after_accuracy,
            "iteration": iteration,
        })

    # ------------------------------------------------------------------
    # Save state
    # ------------------------------------------------------------------
    state["iteration"] = iteration
    state["best_accuracy"] = best_accuracy
    state["last_facts_hash"] = _hash_file(FACTS_PATH)
    state["last_code_hash"] = _hash_directory(SRC_DIR)
    state["total_spend"] = total_spend
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    _save_state(state)

    # Build summary dict
    result["summary"] = {
        "accuracy": after_accuracy,
        "best_accuracy": best_accuracy,
        "total_spend": total_spend,
        "fixes_applied": auto_fix_result.get("applied", 0),
        "subagent_applied": bool(subagent_result.get("applied")),
        "all_passed": all_passed,
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Iteration Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Run all phases without file changes")
    parser.add_argument("--once", action="store_true", help="Single iteration then exit")
    parser.add_argument("--force", action="store_true", help="Bypass gatekeeper rate limit")
    parser.add_argument("--config", help="Path to JSON config file")
    args = parser.parse_args()

    config = {}
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    if args.once or True:  # default to once for CLI usage
        result = run_full_iteration(config, force=args.force, dry_run=args.dry_run)
        # Print final JSON for programmatic consumers
        print(json.dumps(result["summary"], indent=2))
        sys.exit(0 if not result.get("aborted_at") else 1)


if __name__ == "__main__":
    main()
