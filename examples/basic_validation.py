#!/usr/bin/env python3
"""
Basic example: validate an AI response against your facts database.

Usage:
    python examples/basic_validation.py
"""

import json
import tempfile
from pathlib import Path

from hallucination_guard import HallucinationDetector

# Initialize detector with default facts
detector = HallucinationDetector()

# --- Example 1: Known fact (correct answer) ---
result = detector.validate("What is 2+2?", "4")
print("=== Known fact (correct) ===")
print(f"  Valid: {result['valid']}")
print(f"  Confidence: {result['confidence']}")
print(f"  Flags: {result['flags']}")
print()

# --- Example 2: Known fact (wrong answer → hallucination) ---
result = detector.validate("What is 2+2?", "5")
print("=== Known fact (hallucination) ===")
print(f"  Valid: {result['valid']}")
print(f"  Confidence: {result['confidence']}")
print(f"  Flags: {result['flags']}")
print()

# --- Example 3: Unknown query ---
result = detector.validate(
    "What is the airspeed of an unladen swallow?", "About 11 m/s"
)
print("=== Unknown query ===")
print(f"  Valid: {result['valid']}")
print(f"  Confidence: {result['confidence']}")
print(f"  Severity: {result['severity']}")
print()

# --- Example 4: Custom facts database ---
custom_facts = {
    "facts": {
        "company founded": {"type": "numeric", "value": "2026"},
        "ceo name": {"type": "string", "value": "jane doe"},
        "product price": {
            "type": "numeric",
            "value": "49.99",
            "unit": "usd",
            "tolerance": 0.01,
        },
    }
}

with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    json.dump(custom_facts, f)
    custom_path = f.name

detector = HallucinationDetector(facts_db_path=custom_path)
result = detector.validate("When was the company founded?", "2026")
print("=== Custom facts DB ===")
print(f"  Valid: {result['valid']}")
print(f"  Confidence: {result['confidence']}")

Path(custom_path).unlink()
