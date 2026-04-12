#!/usr/bin/env python3
"""
Full Stress Test for Hybrid AI Router
Tests 30 queries across 6 categories
Reports accuracy, confidence distribution, and failure analysis
"""
import json
import sys
import time

sys.path.insert(0, '/data/.openclaw/workspace')
from hybrid_ai_router import HybridAIRouter

# Test cases with expected routing
test_cases = [
    # === INDUSTRIAL / PLC (should route deterministic) ===
    ("How do I fix PLC communication errors in Ladder Logic?", {"expected": "deterministic", "category": "industrial_plc"}),
    ("What is the IEC 61508 standard for safety-critical systems?", {"expected": "deterministic", "category": "industrial_plc"}),
    ("Verify compliance with ISO 13849 for this safety circuit.", {"expected": "deterministic", "category": "industrial_plc"}),
    ("Analyze this L5X file for race conditions.", {"expected": "deterministic", "category": "industrial_plc"}),
    ("How does FAULTTRACE validate PLC tag references?", {"expected": "deterministic", "category": "industrial_plc"}),

    # === COMPLIANCE / AUDIT (should route deterministic) ===
    ("Generate an audit trail for all system modifications in Q3.", {"expected": "deterministic", "category": "compliance_audit"}),
    ("What are the SOX compliance requirements for internal controls?", {"expected": "deterministic", "category": "compliance_audit"}),
    ("Document all verification steps for ISO 27001 certification.", {"expected": "deterministic", "category": "compliance_audit"}),
    ("Extract legal precedents from our corporate database.", {"expected": "deterministic", "category": "compliance_audit"}),
    ("Validate GDPR data retention policy implementation.", {"expected": "deterministic", "category": "compliance_audit"}),

    # === PII / SENSITIVE DATA (should route deterministic) ===
    ("Summarize patient medical records for John Doe born 1985.", {"expected": "deterministic", "category": "pii_sensitive"}),
    ("Redact personal identifiable information from employee database.", {"expected": "deterministic", "category": "pii_sensitive"}),
    ("Analyze bank transaction history for account ending 4892.", {"expected": "deterministic", "category": "pii_sensitive"}),
    ("How to handle sensitive customer data under HIPAA?", {"expected": "deterministic", "category": "pii_sensitive"}),
    ("Remove SSNs from this HR compliance report.", {"expected": "deterministic", "category": "pii_sensitive"}),

    # === CREATIVE / BRAINSTORMING (should route external) ===
    ("Write a catchy tagline for a new productivity app.", {"expected": "external", "category": "creative"}),
    ("Brainstorm 5 marketing campaign ideas for a pet food brand.", {"expected": "external", "category": "creative"}),
    ("Help me plan a surprise birthday party for 30 people.", {"expected": "external", "category": "creative"}),
    ("Suggest creative names for a new coffee shop chain.", {"expected": "external", "category": "creative"}),
    ("What would happen if AI could dream?", {"expected": "external", "category": "creative"}),

    # === TECHNICAL DEBUGGING (should route external) ===
    ("Fix this Python bug in my Flask API.", {"expected": "external", "category": "technical_debug"}),
    ("Help me understand my React component state issue.", {"expected": "external", "category": "technical_debug"}),
    ("Explain how caching works in database systems.", {"expected": "external", "category": "technical_debug"}),
    ("Write a script to automate email sending.", {"expected": "external", "category": "technical_debug"}),
    ("Debug this Docker compose networking problem.", {"expected": "external", "category": "technical_debug"}),

    # === AMBIGUOUS / MIXED (edge cases) ===
    ("Tell me about AI", {"expected": "external", "category": "ambiguous"}),
    ("What is deterministic search?", {"expected": "deterministic", "category": "ambiguous"}),
    ("Help me understand my code", {"expected": "external", "category": "ambiguous"}),
    ("Run verification on my workspace", {"expected": "deterministic", "category": "ambiguous"}),
    ("How does caching work?", {"expected": "external", "category": "ambiguous"}),
    ("Explain blockchain to a 10-year-old", {"expected": "external", "category": "ambiguous"}),
    ("What's the difference between SHA-256 and SHA-512?", {"expected": "deterministic", "category": "ambiguous"}),
    ("Write an email to my boss about being late", {"expected": "external", "category": "ambiguous"}),
]

print("=" * 90)
print("HYBRID AI ROUTER - FULL STRESS TEST REPORT")
print(f"Test Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
print(f"Total Queries: {len(test_cases)}")
print("=" * 90)

router = HybridAIRouter("/data/.openclaw/workspace")
results = []
correct = 0
start_time = time.time()

for i, (query, meta) in enumerate(test_cases):
    result = router.process_query(query)
    
    expected = meta['expected']
    category = meta['category']
    actual = result['ai_type']
    match = expected == actual
    if match:
        correct += 1
    
    results.append({
        "query": query,
        "expected": expected,
        "actual": actual,
        "confidence": round(result['confidence'], 3),
        "reasoning": result['reasoning'],
        "match": match,
        "category": category
    })

elapsed = time.time() - start_time

# Print individual results (condensed)
print("\n" + "=" * 90)
print("INDIVIDUAL RESULTS")
print("=" * 90)

for r in results:
    status = "✅" if r["match"] else "❌"
    print(f"{status} [{r['category']:15}] {r['expected']:14} -> {r['actual']:14} | {r['confidence']:.1%} | {r['reasoning'][:60]}")
    print(f"   Q: {r['query'][:85]}")

# Overall stats
print("\n" + "=" * 90)
print("OVERALL PERFORMANCE")
print("=" * 90)
accuracy = correct / len(test_cases) * 100
print(f"Overall Accuracy: {correct}/{len(test_cases)} ({accuracy:.0f}%)")
print(f"Processing Time:  {elapsed:.2f}s ({len(test_cases)/elapsed:.1f} queries/sec)")

# Confidence distribution
confidences = [r['confidence'] for r in results]
correct_confs = [r['confidence'] for r in results if r['match']]
incorrect_confs = [r['confidence'] for r in results if not r['match']]
print(f"Average Confidence: {sum(confidences)/len(confidences):.1%}")
print(f"Correct Avg Conf:   {sum(correct_confs)/len(correct_confs):.1%}" if correct_confs else "Correct Avg Conf:   N/A")
print(f"Incorrect Avg Conf: {sum(incorrect_confs)/len(incorrect_confs):.1%}" if incorrect_confs else "Incorrect Avg Conf: N/A")

# Category breakdown
by_category = {}
for r in results:
    cat = r['category']
    if cat not in by_category:
        by_category[cat] = {"total": 0, "correct": 0}
    by_category[cat]["total"] += 1
    if r["match"]:
        by_category[cat]["correct"] += 1

print("\n" + "=" * 90)
print("CATEGORY BREAKDOWN")
print("=" * 90)
for cat, stats in by_category.items():
    acc = stats['correct'] / stats['total'] * 100
    print(f"  {cat:15}: {stats['correct']}/{stats['total']} correct ({acc:.0f}%)")

# Mis-categorized analysis
print("\n" + "=" * 90)
print("MIS-CATEGORIZED QUERIES ANALYSIS")
print("=" * 90)
for r in results:
    if not r["match"]:
        print(f"\n  ❌ Category: {r['category']}")
        print(f"     Query:    {r['query']}")
        print(f"     Expected: {r['expected']} | Got: {r['actual']} | Conf: {r['confidence']:.1%}")
        print(f"     Why:      {r['reasoning']}")

# Recommendations
print("\n" + "=" * 90)
print("RECOMMENDATIONS")
print("=" * 90)

if accuracy < 60:
    print("⚠️  Accuracy is below 60%. The router needs tuning before production deployment.")
    print("   Primary issues:")
    for cat, stats in by_category.items():
        if stats['correct'] / stats['total'] < 0.5:
            print(f"   - {cat}: {stats['correct']}/{stats['total']} ({stats['correct']/stats['total']*100:.0f}%)")
elif accuracy < 80:
    print("✅ Accuracy is acceptable (60-80%). Minor tuning recommended.")
else:
    print("🎯 Excellent accuracy (>80%). Ready for production with monitoring.")

print("\n" + "=" * 90)
