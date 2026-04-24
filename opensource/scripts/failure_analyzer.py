#!/usr/bin/env python3
"""
failure_analyzer.py — read benchmark results, classify failures into patterns.

Usage:
    python3 scripts/failure_analyzer.py benchmarks/results.json
"""

import json
import re
import sys
from pathlib import Path

# Pattern detection heuristics
UNCERTAINTY_HEDGE_PATTERNS = [
    r"\bi'm not sure\b",
    r"\bi think\b",
    r"\bit depends\b",
    r"\bprobably\b",
    r"\bmaybe\b",
    r"\bgenerally\b",
    r"\bin most cases\b",
]

FAILURE_REASON_KEYS = {
    "numeric_tolerance": ["tolerance", "range"],
    "unit_mismatch": ["unit"],
    "exact_match_failure": ["exact_match"],
    "qualifier_misfire": ["qualifier"],
}


def classify_failure(case: dict) -> str:
    """Classify a single failing case into a pattern."""
    response = (case.get("response_snippet") or "").lower()
    flags_text = " ".join(case.get("flags", [])).lower()
    notes_text = (case.get("notes") or "").lower()
    failure_reason = f"{flags_text} {notes_text}".strip()

    # 1. uncertainty_hedge: response contains hedge phrases
    for pattern in UNCERTAINTY_HEDGE_PATTERNS:
        if re.search(pattern, response, re.IGNORECASE):
            return "uncertainty_hedge"

    # 2-5. Check failure_reason keywords
    for pattern_name, keywords in FAILURE_REASON_KEYS.items():
        if any(kw in failure_reason for kw in keywords):
            return pattern_name

    # 6. missing_fact: no matched fact found in DB
    if "no matching fact" in failure_reason:
        return "missing_fact"

    # 7. other
    return "other"


def extract_failure_reason(case: dict) -> str:
    """Build a human-readable failure_reason string."""
    flags = case.get("flags", [])
    notes = case.get("notes", "")
    parts = []
    if flags:
        parts.extend(flags)
    if notes:
        parts.append(notes)
    return " | ".join(parts) if parts else "Unknown failure"


def main():
    if len(sys.argv) < 2:
        print("Usage: failure_analyzer.py <benchmark_results.json>", file=sys.stderr)
        sys.exit(1)

    results_path = Path(sys.argv[1])
    with open(results_path, "r") as f:
        data = json.load(f)

    failures = [c for c in data.get("cases", []) if c.get("correct") is False]
    total_failures = len(failures)

    patterns: dict[str, dict] = {}
    for case in failures:
        pattern_name = classify_failure(case)
        if pattern_name not in patterns:
            patterns[pattern_name] = {
                "count": 0,
                "cases": [],
                "suggested_strategy": "",
                "confidence": 0.0,
            }
        patterns[pattern_name]["count"] += 1
        patterns[pattern_name]["cases"].append({
            "query": case.get("query", ""),
            "response": case.get("response_snippet", ""),
            "failure_reason": extract_failure_reason(case),
        })

    # Assign suggested_strategy and confidence per pattern
    strategies = {
        "uncertainty_hedge": {
            "strategy": "Add missing hedge phrases to _SAFE_QUALIFIERS in hallucination_detector.py",
            "confidence": 0.95,
        },
        "numeric_tolerance": {
            "strategy": "Review numeric tolerance rules in fact-matching logic",
            "confidence": 0.85,
        },
        "unit_mismatch": {
            "strategy": "Improve unit validation in unit_validator.py",
            "confidence": 0.85,
        },
        "exact_match_failure": {
            "strategy": "Tune exact_match_required logic in _check_factual_consistency",
            "confidence": 0.80,
        },
        "qualifier_misfire": {
            "strategy": "Refine qualifier detection heuristics in hallucination_detector.py",
            "confidence": 0.75,
        },
        "missing_fact": {
            "strategy": "Add missing facts to facts_db or propose new fact entries",
            "confidence": 0.90,
        },
        "other": {
            "strategy": "Manual review required - no clear automated fix identified",
            "confidence": 0.50,
        },
    }

    for name, info in patterns.items():
        s = strategies.get(name, strategies["other"])
        info["suggested_strategy"] = s["strategy"]
        info["confidence"] = s["confidence"]

    # Build fix_priorities list (sorted by impact, then ease)
    fix_priorities = []
    for name, info in patterns.items():
        auto_fixable = name in ("uncertainty_hedge", "missing_fact")
        ease = "easy" if name == "uncertainty_hedge" else ("medium" if name == "missing_fact" else "hard")
        fix_priorities.append({
            "pattern": name,
            "impact": info["count"],
            "ease": ease,
            "auto_fixable": auto_fixable,
        })

    fix_priorities.sort(key=lambda x: (-x["impact"], x["ease"]))

    output = {
        "total_failures": total_failures,
        "patterns": patterns,
        "fix_priorities": fix_priorities,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
