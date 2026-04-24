#!/usr/bin/env python3
"""
fix_designer.py — read failure_patterns.json from stdin, output fix proposals.

Usage:
    cat failure_patterns.json | python3 scripts/fix_designer.py
"""

import json
import re
import sys
from pathlib import Path


def read_detector_content() -> str:
    """Read the current hallucination_detector.py source."""
    detector_path = Path(__file__).parent.parent / "src" / "hallucination_guard" / "hallucination_detector.py"
    if not detector_path.exists():
        return ""
    return detector_path.read_text()


def find_safe_qualifiers_section(content: str) -> tuple[str | None, list[str]]:
    """Find the _SAFE_QUALIFIERS list in the detector and return surrounding text + existing entries."""
    # Look for _SAFE_QUALIFIERS = [
    match = re.search(
        r"(_SAFE_QUALIFIERS\s*=\s*\[)(.*?)(\])",
        content,
        re.DOTALL,
    )
    if not match:
        return None, []
    block = match.group(2)
    # Extract existing patterns (quoted strings / raw strings)
    existing = re.findall(r'r?"(.*?)(?<!\\)"', block)
    return match.group(0), existing


def generate_uncertainty_hedge_fix(cases: list[dict]) -> dict | None:
    """Generate an auto-fix for uncertainty_hedge pattern by adding missing hedge phrases to _SAFE_QUALIFIERS."""
    detector_content = read_detector_content()
    if not detector_content:
        return None

    _, existing = find_safe_qualifiers_section(detector_content)
    existing_lower = [e.lower() for e in existing]

    # Known hedge expressions that should be treated as safe qualifiers
    # We add phrases found in responses that triggered uncertainty_hedge failures
    candidates = []
    for case in cases:
        response = case.get("response", "").lower()
        for phrase in ["i'm not sure", "i think", "maybe", "probably"]:
            if phrase in response and phrase not in existing_lower:
                if phrase not in candidates:
                    candidates.append(phrase)

    if not candidates:
        return None

    # Build new entries
    new_entries = [f'    r"\\b{c}\\b",' for c in candidates]
    new_text_block = "\n".join(new_entries)

    # Find the exact list block to patch
    list_block_match = re.search(
        r"(_SAFE_QUALIFIERS\s*=\s*\[)(.*?)(\])",
        detector_content,
        re.DOTALL,
    )
    if not list_block_match:
        return None

    old_text = list_block_match.group(0)
    # Insert new entries before the closing bracket
    lines = old_text.rsplit("]", 1)
    if len(lines) != 2:
        return None
    prefix = lines[0]
    closing = "]" + lines[1][1:]  # keep any trailing content if present
    # If prefix ends with whitespace but no trailing comma on last item, handle carefully
    new_text = prefix.rstrip() + "\n" + new_text_block + "\n" + closing

    test_queries = [c["query"] for c in cases[:3]]

    return {
        "type": "auto",
        "target_file": "src/hallucination_guard/hallucination_detector.py",
        "description": f"Add {len(candidates)} missing hedge phrase(s) to _SAFE_QUALIFIERS: {candidates}",
        "old_text": old_text,
        "new_text": new_text,
        "test_queries": test_queries,
        "estimated_impact": len(cases),
    }


def generate_numeric_tolerance_fix(cases: list[dict]) -> dict | None:
    """Generate a subagent fix proposal for numeric_tolerance failures."""
    if not cases:
        return None
    return {
        "type": "subagent",
        "description": "Review and improve numeric tolerance rules in hallucination_detector._check_factual_consistency",
        "reasoning": (
            f"Found {len(cases)} numeric tolerance failure(s). "
            "The current numeric comparison logic (exact match for identifiers <100, 1%% relative tolerance otherwise) "
            "may be too strict or too loose for certain fact domains. "
            "A subagent should audit tolerance thresholds and propose tighter heuristics."
        ),
        "estimated_cost_usd": round(0.05 * len(cases), 2),
    }


def generate_missing_fact_fixes(cases: list[dict]) -> list[dict]:
    """Generate fact_proposal entries for missing_fact failures."""
    proposals = []
    for case in cases:
        query = case.get("query", "")
        if not query:
            continue
        key = re.sub(r"[^\w\s]", "", query).lower().strip()[:80]
        proposals.append({
            "type": "fact_proposal",
            "key": key,
            "query": query,
            "auto_approve": False,
            "confidence": 0.5,
        })
    return proposals


def main():
    data = json.load(sys.stdin)
    patterns = data.get("patterns", {})

    auto_fixes = []
    subagent_fixes = []
    fact_proposals = []

    for pattern_name, info in patterns.items():
        cases = info.get("cases", [])
        if pattern_name == "uncertainty_hedge":
            fix = generate_uncertainty_hedge_fix(cases)
            if fix:
                auto_fixes.append(fix)
        elif pattern_name == "numeric_tolerance":
            fix = generate_numeric_tolerance_fix(cases)
            if fix:
                subagent_fixes.append(fix)
        elif pattern_name == "missing_fact":
            fact_proposals.extend(generate_missing_fact_fixes(cases))

    output = {
        "auto_fixes": auto_fixes,
        "subagent_fixes": subagent_fixes,
        "fact_proposals": fact_proposals,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
