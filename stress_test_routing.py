#!/usr/bin/env python3
"""
Stress Test for Hybrid AI Router
Tests 25 varied queries to verify routing accuracy
"""
import json
import sys
sys.path.insert(0, '/data/.openclaw/workspace')
from hybrid_ai_router import HybridAIRouter

# Test queries across different categories
test_cases = [
    # COMPLIANCE / INDUSTRIAL (should route deterministic)
    ("How do I fix PLC communication errors in Ladder Logic?", {"expected": "deterministic"}),
    ("What is the IEC 61508 standard for safety-critical systems?", {"expected": "deterministic"}),
    ("Generate an audit trail for all L5X file modifications in Q3.", {"expected": "deterministic"}),
    ("Verify compliance with ISO 13849 for this safety circuit.", {"expected": "deterministic"}),
    ("How to validate FAULTTRACE PLC code against HIPAA requirements?", {"expected": "deterministic"}),
    
    # CREATIVE / EXPLORATORY (should route external)
    ("Write a catchy tagline for a new productivity app.", {"expected": "external"}),
    ("Brainstorm 5 marketing campaign ideas for a pet food brand.", {"expected": "external"}),
    ("Help me plan a surprise birthday party for 30 people.", {"expected": "external"}),
    ("What would happen if dinosaurs had smartphones?", {"expected": "external"}),
    ("Suggest creative names for a coffee shop chain.", {"expected": "external"}),
    
    # PII / SENSITIVE (should route deterministic)
    ("Summarize patient medical records for John Doe born 1985.", {"expected": "deterministic"}),
    ("Analyze bank transaction history for account ending in 4892.", {"expected": "deterministic"}),
    ("Redact personal identifiable information from this employee database.", {"expected": "deterministic"}),
    ("How to handle sensitive customer data under GDPR?", {"expected": "deterministic"}),
    
    # FINANCIAL / LEGAL (should route deterministic)
    ("Draft an NDA for our proprietary PLC analysis algorithm.", {"expected": "external"}),  # mixed
    ("Summarize SOX compliance requirements for internal controls.", {"expected": "deterministic"}),
    ("Calculate tax implications of a $5M equipment purchase.", {"expected": "external"}),  # mixed
    ("Extract legal precedents from our corporate litigation database.", {"expected": "deterministic"}),
    
    # AMBIGUOUS / MIX (edge cases)
    ("Tell me about AI", {"expected": "external"}),
    ("What is deterministic search?", {"expected": "deterministic"}),
    ("Help me understand my code", {"expected": "external"}),
    ("Fix this Python bug", {"expected": "external"}),
    ("Run verification on my workspace", {"expected": "deterministic"}),
    ("Write an email to my boss", {"expected": "external"}),
    ("How does caching work?", {"expected": "external"}),
]

router = HybridAIRouter("/data/.openclaw/workspace")
results = []

print("=" * 80)
print("HYBRID AI ROUTER STRESS TEST")
print(f"Testing {len(test_cases)} queries")
print("=" * 80)

correct = 0
for i, (query, meta) in enumerate(test_cases):
    result = router.process_query(query)
    
    expected = meta['expected']
    actual = result['ai_type']
    match = expected == actual
    if match:
        correct += 1
    
    status = "✅" if match else "❌"
    
    results.append({
        "query": query,
        "expected": expected,
        "actual": actual,
        "confidence": round(result['confidence'], 3),
        "reasoning": result['reasoning'],
        "match": match
    })
    
    print(f"\n{status} Query {i+1}: {query[:50]}...'")
    print(f"   Expected: {expected} | Actual: {actual} | Conf: {result['confidence']:.1%}")
    print(f"   Reasoning: {result['reasoning']}")

print("\n" + "=" * 80)
print("STRESS TEST RESULTS")
print(f"✅ Correct: {correct}/{len(test_cases)} ({correct/len(test_cases)*100:.0f}%)")
print("=" * 80)

# Detailed breakdown
by_type = {}
for r in results:
    key = r['expected']
    if key not in by_type:
        by_type[key] = {"total": 0, "correct": 0}
    by_type[key]["total"] += 1
    if r["match"]:
        by_type[key]["correct"] += 1

print("\nBreakdown by category:")
for cat, stats in by_type.items():
    accuracy = stats['correct'] / stats['total'] * 100
    print(f"  {cat}: {stats['correct']}/{stats['total']} correct ({accuracy:.0f}%)")

print("\nMis-categorized queries:")
for r in results:
    if not r["match"]:
        print(f"  ❌ Expected: {r['expected']} | Got: {r['actual']} | Confidence: {r['confidence']:.1%}")
        print(f"     Query: {r['query'][:70]}...")
        print(f"     Reasoning: {r['reasoning']}")
