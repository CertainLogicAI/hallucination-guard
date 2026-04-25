#!/usr/bin/env python3
"""Test Spec: Brain Integration Dry Run
Author: Customer (CertainLogic Internal)
Purpose: Verify Hallucination Guard SDK works end-to-end in a real coding workflow
"""
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hguard_client import HGuardClient

client = HGuardClient()
results = []

# === Task 1: Validate a correct fact ===
r1 = client.validate(
    "What is Python default recursion depth?",
    "Python default maximum recursion depth is 1000."
)
results.append({"task": "correct_fact", "result": r1})
print("[1] Correct fact:", f"valid={r1['valid']}, conf={r1['confidence']}")

# === Task 2: Validate correct code ===
r2 = client.validate(
    "Write a palindrome checker in Python",
    "def is_palindrome(s): return s == s[::-1]"
)
results.append({"task": "correct_code", "result": r2})
print("[2] Correct code:", f"valid={r2['valid']}, conf={r2['confidence']}")

# === Task 3: Validate a speculative (should pass, no fact match) ===
r3 = client.validate(
    "What if JavaScript had static typing?",
    "If JavaScript used static typing, many runtime errors would be caught at compile time."
)
results.append({"task": "speculative", "result": r3})
print("[3] Speculative:", f"valid={r3['valid']}, conf={r3['confidence']}")

# === Task 4: Validate a hedge (should invalidate) ===
r4 = client.validate(
    "What is the default Docker network driver?",
    "I think the default Docker network driver is bridge, maybe."
)
results.append({"task": "hedge", "result": r4})
print("[4] Hedge:", f"valid={r4['valid']}, conf={r4['confidence']}, flags={r4['flags']}")

# === Task 5: Validate a wrong number (currently passes -- known limitation) ===
r5 = client.validate(
    "What is Python default recursion depth?",
    "Python default maximum recursion depth is 500."
)
results.append({"task": "wrong_number", "result": r5})
print("[5] Wrong number:", f"valid={r5['valid']}, conf={r5['confidence']}, flags={r5['flags']}")

# === Session Metrics ===
metrics = {
    "test_run": "brain_integration_dry_run",
    "tests_run": len(results),
    "tests_passed": sum(1 for r in results if r["result"]["valid"]),
    "tests_failed": sum(1 for r in results if not r["result"]["valid"]),
    "flags_triggered": sum(len(r["result"]["flags"]) for r in results),
    "details": results
}

log_dir = Path(__file__).parent / "brain_logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "test_run_metrics.json"
with open(log_file, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\nMetrics saved to: {log_file}")
print(f"Total tests: {metrics['tests_run']}, Passed: {metrics['tests_passed']}, Failed: {metrics['tests_failed']}")
print(f"Flags triggered across all tests: {metrics['flags_triggered']}")
