#!/usr/bin/env python3
"""HALLUCINATION-GUARD BENCHMARK — Realistic assessment"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from hallucination_guard.hallucination_detector import HallucinationDetector


def run():
    detector = HallucinationDetector()
    with open(Path(__file__).parent / "test_cases.json") as f:
        cases = json.load(f)

    results = {}
    for case in cases:
        result = detector.validate(case["query"], case["response"])
        actual = result.get("valid", False) and not result.get("flagged", False)
        case["passed"] = (actual == case["expected_valid"])
        case["actual_valid"] = actual
        case["confidence"] = result.get("confidence", 0.0)
        case["flags"] = result.get("flags", [])

    for cat in ["known_facts_correct", "known_facts_hallucination", "pricing_cost", "date_version", "definitional", "speculative", "code_output", "edge_cases"]:
        cat_cases = [c for c in cases if c["category"] == cat]
        passed = sum(1 for c in cat_cases if c["passed"])
        results[cat] = {"total": len(cat_cases), "passed": passed, "rate": passed / len(cat_cases) * 100 if cat_cases else 0}

    # What the detector actually does
    relevant = ["known_facts_correct", "speculative", "code_output", "edge_cases"]
    rel_cases = [c for c in cases if c["category"] in relevant]
    rel_passed = sum(1 for c in rel_cases if c["passed"])

    # What it doesn't do
    contradiction = [c for c in cases if c["category"] == "known_facts_hallucination"]
    contra_passed = sum(1 for c in contradiction if c["passed"])

    print("=" * 70)
    print("  HALLUCINATION-GUARD BENCHMARK")
    print("=" * 70)
    print(f"\n  Total cases: {len(cases)}")
    print()
    for cat, name in [
        ("code_output", "Code Output (core use case)"),
        ("known_facts_correct", "Known Facts Correct"),
        ("speculative", "Speculative (no fact match)"),
        ("edge_cases", "Edge Cases"),
        ("pricing_cost", "Pricing/Cost (no facts loaded)"),
        ("date_version", "Date/Version (no facts loaded)"),
        ("definitional", "Definitional (no facts loaded)"),
        ("known_facts_hallucination", "Known Facts Hallucination (contradiction detection)"),
    ]:
        r = results[cat]
        marker = "  " if cat in ["code_output", "known_facts_correct", "speculative"] else "  "
        print(f"  {name:55} {r['passed']:>3}/{r['total']:<3}  ({r['rate']:>5.1f}%)")

    print()
    print(f"  RELEVANT CATEGORIES (what it does): {rel_passed}/{len(rel_cases)} = {rel_passed/len(rel_cases)*100:.1f}%")
    print(f"  CONTRADICTION DETECTION (not implemented): {contra_passed}/{len(contradiction)} = {contra_passed/len(contradiction)*100:.1f}%")
    print()

    # Save results
    output = {
        "total": len(cases),
        "relevant_score": f"{rel_passed}/{len(rel_cases)}",
        "relevant_rate": round(rel_passed/len(rel_cases)*100, 1),
        "contradiction_score": f"{contra_passed}/{len(contradiction)}",
        "contradiction_rate": round(contra_passed/len(contradiction)*100, 1) if contradiction else 0,
        "categories": {k: {"total": v["total"], "passed": v["passed"], "rate": round(v["rate"], 1)} for k, v in results.items()}
    }
    with open(Path(__file__).parent / "results.json", "w") as f:
        json.dump(output, f, indent=2)

    return output


if __name__ == "__main__":
    run()
