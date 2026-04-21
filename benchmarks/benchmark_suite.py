#!/usr/bin/env python3
"""
Hallucination-Guard Benchmark Suite
=====================================
Comprehensive benchmark for the HallucinationDetector across 8 categories.

Usage:
    python3 benchmarks/benchmark_suite.py
    python3 benchmarks/benchmark_suite.py --test-cases benchmarks/test_cases.json
    python3 benchmarks/benchmark_suite.py --output benchmarks/results.json

Results are saved to benchmarks/results.json by default.
"""

import sys
import json
import time
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ── Path setup ──────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from hallucination_guard.hallucination_detector import HallucinationDetector

FACTS_DB_PATH = REPO_ROOT / "coder_facts_pack_v1.0.json"
TEST_CASES_PATH = Path(__file__).parent / "test_cases.json"
RESULTS_PATH = Path(__file__).parent / "results.json"


# ── Helpers ──────────────────────────────────────────────────────────────────

def load_test_cases(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_valid_result(result: dict) -> bool:
    """Normalize detector output to boolean: True = valid, False = invalid/flagged."""
    v = result.get("valid")
    if v is True:
        return True
    if v is False or v == "flagged":
        return False
    # Fallback: use confidence threshold
    return result.get("confidence", 0.0) >= 0.7


def run_benchmark(test_cases: list[dict], detector: HallucinationDetector) -> dict:
    """Run all test cases and collect per-case + per-category results."""
    case_results = []
    start_time = time.perf_counter()

    for i, tc in enumerate(test_cases):
        query = tc["query"]
        response = tc["response"]
        expected_valid = tc["expected_valid"]
        category = tc["category"]

        t0 = time.perf_counter()
        try:
            result = detector.validate(query, response)
        except Exception as e:
            result = {
                "valid": False,
                "confidence": 0.0,
                "severity": "high",
                "flags": [f"Exception during validation: {e}"],
                "checks": {},
            }
        elapsed_ms = (time.perf_counter() - t0) * 1000

        actual_valid = is_valid_result(result)
        correct = (actual_valid == expected_valid)

        case_results.append({
            "index": i,
            "category": category,
            "query": query[:120],
            "response_snippet": response[:100],
            "expected_valid": expected_valid,
            "actual_valid": actual_valid,
            "raw_valid": result.get("valid"),
            "confidence": result.get("confidence"),
            "severity": result.get("severity"),
            "flags": result.get("flags", []),
            "correct": correct,
            "elapsed_ms": round(elapsed_ms, 3),
            "notes": tc.get("notes", ""),
        })

    total_ms = (time.perf_counter() - start_time) * 1000

    # ── Per-category metrics ──────────────────────────────────────────────────
    categories = defaultdict(list)
    for r in case_results:
        categories[r["category"]].append(r)

    category_stats = {}
    for cat, items in sorted(categories.items()):
        tp = sum(1 for r in items if not r["expected_valid"] and not r["actual_valid"])  # correctly flagged
        fp = sum(1 for r in items if r["expected_valid"] and not r["actual_valid"])       # false positives
        fn = sum(1 for r in items if not r["expected_valid"] and r["actual_valid"])        # missed hallucinations
        tn = sum(1 for r in items if r["expected_valid"] and r["actual_valid"])            # correctly passed

        total = len(items)
        accuracy = (tp + tn) / total if total > 0 else 0.0

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        category_stats[cat] = {
            "total": total,
            "correct": tp + tn,
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "avg_confidence": round(
                sum(r["confidence"] for r in items if r["confidence"] is not None) / total, 4
            ) if total > 0 else 0.0,
            "avg_elapsed_ms": round(sum(r["elapsed_ms"] for r in items) / total, 3),
        }

    # ── Overall metrics ───────────────────────────────────────────────────────
    total = len(case_results)
    tp_all = sum(1 for r in case_results if not r["expected_valid"] and not r["actual_valid"])
    fp_all = sum(1 for r in case_results if r["expected_valid"] and not r["actual_valid"])
    fn_all = sum(1 for r in case_results if not r["expected_valid"] and r["actual_valid"])
    tn_all = sum(1 for r in case_results if r["expected_valid"] and r["actual_valid"])

    overall_accuracy = (tp_all + tn_all) / total if total > 0 else 0.0
    overall_precision = tp_all / (tp_all + fp_all) if (tp_all + fp_all) > 0 else 0.0
    overall_recall = tp_all / (tp_all + fn_all) if (tp_all + fn_all) > 0 else 0.0
    overall_f1 = (2 * overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0

    overall_stats = {
        "total": total,
        "correct": tp_all + tn_all,
        "accuracy": round(overall_accuracy, 4),
        "precision": round(overall_precision, 4),
        "recall": round(overall_recall, 4),
        "f1": round(overall_f1, 4),
        "tp": tp_all, "fp": fp_all, "fn": fn_all, "tn": tn_all,
        "total_elapsed_ms": round(total_ms, 3),
        "avg_elapsed_ms": round(total_ms / total, 3) if total > 0 else 0.0,
    }

    return {
        "run_timestamp": datetime.utcnow().isoformat() + "Z",
        "facts_db": str(FACTS_DB_PATH),
        "overall": overall_stats,
        "categories": category_stats,
        "cases": case_results,
    }


# ── Printing ──────────────────────────────────────────────────────────────────

CAT_LABELS = {
    "known_facts_correct":       "Known Facts — Correct Answer",
    "known_facts_hallucination": "Known Facts — Hallucination",
    "pricing_queries":           "Pricing / Cost Queries",
    "date_version_queries":      "Date / Version Queries",
    "definitional_queries":      "Definitional Queries (no fact)",
    "speculative_hedged":        "Speculative / Hedged Queries",
    "code_output":               "Code Output Validation",
    "edge_cases":                "Edge Cases",
}


def print_summary(results: dict):
    o = results["overall"]
    cats = results["categories"]

    print()
    print("=" * 76)
    print("  HALLUCINATION-GUARD BENCHMARK RESULTS")
    print("=" * 76)
    print(f"  Facts DB : {results['facts_db']}")
    print(f"  Run at   : {results['run_timestamp']}")
    print(f"  Total    : {o['total']} test cases  |  {o['total_elapsed_ms']:.1f} ms total  |  {o['avg_elapsed_ms']:.2f} ms/case")
    print()

    # Overall row
    print(f"  {'OVERALL':40s}  {'Acc':>6}  {'Prec':>6}  {'Rec':>6}  {'F1':>6}  {'Corr':>5}/{o['total']}")
    print(f"  {'-'*40}  {'------':>6}  {'------':>6}  {'------':>6}  {'------':>6}  {'------':>5}")
    print(f"  {'ALL CATEGORIES':40s}  {o['accuracy']:>6.1%}  {o['precision']:>6.1%}  {o['recall']:>6.1%}  {o['f1']:>6.1%}  {o['correct']:>5}/{o['total']}")
    print()

    # Per-category
    print(f"  {'Category':40s}  {'Acc':>6}  {'Prec':>6}  {'Rec':>6}  {'F1':>6}  {'N':>4}")
    print(f"  {'-'*40}  {'------':>6}  {'------':>6}  {'------':>6}  {'------':>6}  {'----':>4}")
    for cat, label in CAT_LABELS.items():
        if cat not in cats:
            continue
        s = cats[cat]
        print(f"  {label:40s}  {s['accuracy']:>6.1%}  {s['precision']:>6.1%}  {s['recall']:>6.1%}  {s['f1']:>6.1%}  {s['total']:>4}")
    print()

    # Confusion matrix
    print(f"  Confusion Matrix (overall):")
    print(f"    TP (correctly flagged)   : {o['tp']:>4}")
    print(f"    TN (correctly passed)    : {o['tn']:>4}")
    print(f"    FP (false positives)     : {o['fp']:>4}  (valid responses incorrectly flagged)")
    print(f"    FN (missed hallucination): {o['fn']:>4}  (hallucinations that slipped through)")
    print()
    print("=" * 76)

    # Failures summary
    failures = [c for c in results["cases"] if not c["correct"]]
    if failures:
        print(f"\n  FAILURES ({len(failures)} total):")
        print(f"  {'-'*72}")
        for f in failures[:10]:
            exp = "valid" if f["expected_valid"] else "INVALID"
            got = "valid" if f["actual_valid"] else "INVALID"
            print(f"  [{f['category'][:20]}] Q: {f['query'][:50]!r}")
            print(f"    Expected={exp}, Got={got}, Conf={f['confidence']:.3f}")
            if f["flags"]:
                print(f"    Flags: {f['flags'][0][:80]}")
        if len(failures) > 10:
            print(f"  ... and {len(failures) - 10} more failures (see results.json)")
    print("=" * 76)
    print()


# ── CLI entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Hallucination-Guard Benchmark Suite")
    parser.add_argument("--test-cases", default=str(TEST_CASES_PATH), help="Path to test_cases.json")
    parser.add_argument("--facts-db", default=str(FACTS_DB_PATH), help="Path to facts DB JSON")
    parser.add_argument("--output", default=str(RESULTS_PATH), help="Output path for results.json")
    parser.add_argument("--threshold", type=float, default=0.7, help="Confidence threshold (default: 0.7)")
    parser.add_argument("--category", default=None, help="Run only a specific category")
    args = parser.parse_args()

    print(f"Loading facts DB from: {args.facts_db}")
    detector = HallucinationDetector(
        confidence_threshold=args.threshold,
        facts_db_path=args.facts_db,
    )
    n_facts = len(detector.facts_db)
    print(f"Facts loaded: {n_facts}")

    print(f"Loading test cases from: {args.test_cases}")
    test_cases = load_test_cases(Path(args.test_cases))
    if args.category:
        test_cases = [tc for tc in test_cases if tc["category"] == args.category]
        print(f"Filtered to category '{args.category}': {len(test_cases)} cases")
    else:
        print(f"Test cases loaded: {len(test_cases)}")

    print("Running benchmark...\n")
    results = run_benchmark(test_cases, detector)

    print_summary(results)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_path}")

    # Exit code: 0 if accuracy >= 70%, else 1
    acc = results["overall"]["accuracy"]
    sys.exit(0 if acc >= 0.70 else 1)


if __name__ == "__main__":
    main()
