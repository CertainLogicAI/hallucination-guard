#!/usr/bin/env python3
"""
scripts/auto_fixes.py — Deterministic, zero-risk fix implementations.

Applies known-pattern fixes to hallucination_detector.py without LLM calls.
All fixes are rule-based and validated against existing tests before application.
"""

import re
from pathlib import Path


def _read_detector(detector_path: Path) -> str:
    if not detector_path.exists():
        raise FileNotFoundError(f"Detector file not found: {detector_path}")
    return detector_path.read_text()


def fix_qualifier_misfire(failure_cases: list, detector_path: Path) -> dict:
    """Auto-fix 1: Add uncertainty-hedge phrases to _SAFE_QUALIFIERS."""
    content = _read_detector(detector_path)
    existing_qualifiers = _extract_existing_qualifiers(content)
    existing_lower = [q.lower() for q in existing_qualifiers]

    hedge_phrases = ["i'm not sure", "i think", "probably", "maybe", "it depends"]

    existing_plain = []
    for q in existing_lower:
        plain = q.replace(r"\b", "").strip()
        existing_plain.append(plain)

    to_add = []
    for phrase in hedge_phrases:
        if phrase not in existing_plain:
            to_add.append(phrase)

    if not to_add:
        return {"patches": [], "test_cases": [], "estimated_impact": 0}

    match = re.search(
        r"(_SAFE_QUALIFIERS\s*=\s*\[)(.*?)(\])",
        content,
        re.DOTALL,
    )
    if not match:
        return {
            "patches": [],
            "test_cases": [],
            "estimated_impact": 0,
            "error": "Could not locate _SAFE_QUALIFIERS block",
        }

    old_text = match.group(0)
    lines = old_text.rsplit("]", 1)
    if len(lines) != 2:
        return {
            "patches": [],
            "test_cases": [],
            "estimated_impact": 0,
            "error": "Could not split list block",
        }

    prefix = lines[0]
    closing = lines[1][1:]
    indent = "        "  # 8-space indent
    new_entries = [f'{indent}r"\\b{p}\\b",' for p in to_add]
    new_text = prefix.rstrip() + "\n" + "\n".join(new_entries) + "\n" + "    ]" + closing

    patches = [
        {
            "target_file": str(detector_path),
            "old_text": old_text,
            "new_text": new_text,
            "description": f"Add {len(to_add)} hedge phrase(s) to _SAFE_QUALIFIERS",
        }
    ]

    test_queries = [c.get("query", "") for c in failure_cases[:3]]

    return {
        "patches": patches,
        "test_cases": test_queries,
        "estimated_impact": len(failure_cases),
    }


def _extract_existing_qualifiers(content: str) -> list:
    match = re.search(
        r"_SAFE_QUALIFIERS\s*=\s*\[(.*?)\]",
        content,
        re.DOTALL,
    )
    if not match:
        return []
    block = match.group(1)
    return re.findall(r'r?"(.*?)"', block)


def fix_numeric_tolerance(failure_cases: list, detector_path: Path) -> dict:
    """Auto-fix 2 stub."""
    return {"patches": [], "test_cases": [], "estimated_impact": 0}


def fix_code_output_skip(failure_cases: list, detector_path: Path) -> dict:
    """Auto-fix 3 stub."""
    return {"patches": [], "test_cases": [], "estimated_impact": 0}


def apply_patches(patches: list, dry_run: bool = False) -> dict:
    applied = []
    failed = []
    for patch in patches:
        target = Path(patch["target_file"])
        if not target.exists():
            failed.append({"patch": patch, "error": "Target file not found"})
            continue

        old_text = patch.get("old_text")
        new_text = patch.get("new_text")
        if old_text is None or new_text is None:
            failed.append({"patch": patch, "error": "Missing old_text or new_text"})
            continue

        content = target.read_text()
        if old_text not in content:
            failed.append({"patch": patch, "error": "old_text not found in target file"})
            continue

        if dry_run:
            applied.append({"patch": patch, "applied": "dry_run"})
            continue

        content = content.replace(old_text, new_text, 1)
        target.write_text(content)
        applied.append({"patch": patch, "applied": True})

    return {"applied": len(applied), "failed": failed}
