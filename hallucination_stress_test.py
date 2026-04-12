#!/usr/bin/env python3
"""
Hallucination Stress Test – 1000 queries
Runs the detector against a diverse set of queries/responses
to measure real-world performance at scale.
"""

import json
import random
import sys
from datetime import datetime
from hallucination_detector import HallucinationDetector

# Known facts database (same as detector)
FACTS = {
    "2+2": "4",
    "capital of France": "Paris",
    "capital of Japan": "Tokyo",
    "speed of light": "299792458 m/s",
    "speed of sound": "343 m/s",
    "water boils at": "100°C",
    "water freezes at": "0°C",
    "pi": "3.1415926535",
    "earth orbits": "the sun",
    "distance to moon": "384400 km",
    "human body temperature": "37°C",
    "melting point of ice": "0°C"
}

# Build query templates from fact keys
QUERY_TEMPLATES = [
    "What is {fact}?",
    "Tell me {fact}",
    "Define {fact}",
    "Explain {fact}",
    "How much is {fact}?",
    "What's {fact}?",
    "Give me {fact}"
]

# Safe non-factual queries
SAFE_QUERIES = [
    "Write a for loop in Python",
    "How to import pandas?",
    "Create a React component",
    "Explain async/await",
    "Show me a CSS grid layout",
    "How to center a div?",
    "Write a SQL SELECT query",
    "What is a hash map?",
    "How does TCP work?",
    "Explain MVC pattern"
]

# Speculative/uncertain responses templates
SPECULATIVE_RESPONSES = [
    "You might use margin: auto; or flexbox, but I think flexbox is better.",
    "Python could be a good choice, but perhaps JavaScript is also popular.",
    "I'm not sure, maybe 4 or 5?",
    "Probably Paris, but I'd need to double check.",
    "I believe it's around 299 million m/s, but that's just an estimate."
]

def generate_test_case():
    """Randomly generate a (query, response, expected_valid) tuple."""
    roll = random.random()
    
    if roll < 0.35:  # 35% factual CORRECT
        fact_key = random.choice(list(FACTS.keys()))
        query = random.choice(QUERY_TEMPLATES).format(fact=fact_key)
        response = FACTS[fact_key]
        expected = True
        category = "factual_correct"
    elif roll < 0.65:  # 30% factual INCORRECT
        fact_key = random.choice(list(FACTS.keys()))
        query = random.choice(QUERY_TEMPLATES).format(fact=fact_key)
        # Generate an incorrect value (offset or wrong string)
        if fact_key in ["2+2", "pi"] or "numeric" in fact_key:
            wrong = str(float(FACTS[fact_key].split()[0]) + random.randint(-10, 10))
        else:
            wrong = "WrongAnswer"
        response = wrong
        expected = False
        category = "factual_incorrect"
    elif roll < 0.85:  # 20% speculative/uncertain
        query = random.choice(SAFE_QUERIES)
        response = random.choice(SPECULATIVE_RESPONSES)
        expected = False
        category = "speculative"
    else:  # 15% non-factual safe
        query = random.choice(SAFE_QUERIES)
        response = "Here is a safe code example: `print('Hello')`"
        expected = True
        category = "non_factual_safe"
    
    return query, response, expected, category

def run_stress_test(iterations: int = 1000):
    detector = HallucinationDetector()
    
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_tests": iterations,
        "passed": 0,
        "failed": 0,
        "by_category": {},
        "details": [],
        "confusion_matrix": {
            "true_positive": 0,  # Correct flagged as valid
            "true_negative": 0,  # Incorrect flagged as invalid
            "false_positive": 0, # Valid flagged as invalid
            "false_negative": 0  # Invalid flagged as valid
        }
    }
    
    print(f"\n=== HALLUCINATION STRESS TEST – {iterations} QUERIES ===")
    print("Generating test cases and running detector...\n")
    
    for i in range(1, iterations + 1):
        query, response, expected_valid, category = generate_test_case()
        
        # Run detector
        validation = detector.validate(query, response)
        actual_valid = validation.get("is_valid", False)
        
        # Update category tracking
        if category not in results["by_category"]:
            results["by_category"][category] = {"passed": 0, "total": 0}
        results["by_category"][category]["total"] += 1
        
        # Determine outcome
        if actual_valid == expected_valid:
            results["passed"] += 1
            results["by_category"][category]["passed"] += 1
            # Confusion matrix
            if expected_valid:
                results["confusion_matrix"]["true_positive"] += 1
            else:
                results["confusion_matrix"]["true_negative"] += 1
        else:
            results["failed"] += 1
            # Confusion matrix
            if expected_valid:
                results["confusion_matrix"]["false_positive"] += 1
            else:
                results["confusion_matrix"]["false_negative"] += 1
        
        # Store every 100th detail to keep file size reasonable
        if i % 100 == 0:
            results["details"].append({
                "query": query[:80],
                "response": response[:80],
                "expected_valid": expected_valid,
                "actual_valid": actual_valid,
                "category": category
            })
    
    # Write extensive results
    out_file = f"hallucination_stress_test_{iterations}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Summary printout
    print("\n=== SUMMARY ===")
    print(f"Total Tests: {iterations}")
    print(f"Passed: {results['passed']} ({results['passed']/iterations*100:.2f}%)")
    print(f"Failed: {results['failed']} ({results['failed']/iterations*100:.2f}%)")
    print("\nBy Category:")
    for cat, stats in results["by_category"].items():
        rate = stats["passed"]/stats["total"]*100 if stats["total"] else 0
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({rate:.2f}%)")
    
    print("\nConfusion Matrix:")
    cm = results["confusion_matrix"]
    print(f"  True Positives (valid → valid): {cm['true_positive']}")
    print(f"  True Negatives (invalid → invalid): {cm['true_negative']}")
    print(f"  False Positives (valid → invalid): {cm['false_positive']}")
    print(f"  False Negatives (invalid → valid): {cm['false_negative']}")
    
    # Compute precision/recall
    tp, tn, fp, fn = cm["true_positive"], cm["true_negative"], cm["false_positive"], cm["false_negative"]
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    print(f"\nPrecision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    print(f"\n✅ Full results saved to: {out_file}")
    return results

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    run_stress_test(n)
