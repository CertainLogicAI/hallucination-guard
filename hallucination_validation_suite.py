#!/usr/bin/env python3
"""
Comprehensive Hallucination Validation Suite
Tests the hallucination detector against known good/bad outputs
"""

import json
import sys
from datetime import datetime
from hallucination_detector import HallucinationDetector

def generate_test_cases():
    """Generate a robust set of test cases: factual, speculative, contradictory"""
    return [
        # ✅ Factually CORRECT (should pass)
        {
            "query": "What is 2+2?",
            "response": "4",
            "expected_valid": True,
            "category": "factual_correct"
        },
        {
            "query": "What is the capital of France?",
            "response": "Paris",
            "expected_valid": True,
            "category": "factual_correct"
        },
        {
            "query": "What is the speed of light?",
            "response": "299,792,458 meters per second",
            "expected_valid": True,
            "category": "factual_correct"
        },
        {
            "query": "At what temperature does water freeze?",
            "response": "0 degrees Celsius",
            "expected_valid": True,
            "category": "factual_correct"
        },
        # ❌ Factually INCORRECT (should fail)
        {
            "query": "What is 2+2?",
            "response": "5",
            "expected_valid": False,
            "category": "factual_incorrect"
        },
        {
            "query": "What is the capital of France?",
            "response": "London",
            "expected_valid": False,
            "category": "factual_incorrect"
        },
        {
            "query": "What is the speed of light?",
            "response": "150,000 m/s",
            "expected_valid": False,
            "category": "factual_incorrect"
        },
        # ⚠️ Speculative language (should fail)
        {
            "query": "How do I center a div?",
            "response": "You might use margin: auto; or flexbox, but I think flexbox is better.",
            "expected_valid": False,
            "category": "speculative"
        },
        {
            "query": "What is the best programming language?",
            "response": "Python could be a good choice, but perhaps JavaScript is also popular.",
            "expected_valid": False,
            "category": "speculative"
        },
        # ❓ Vague/Uncertain (should fail)
        {
            "query": "What is 2+2?",
            "response": "I'm not sure, maybe 4 or 5?",
            "expected_valid": False,
            "category": "uncertain"
        },
        # ✅ Non-factual but safe (no ground truth, no speculation)
        {
            "query": "Write a for loop in Python",
            "response": "for i in range(10): print(i)",
            "expected_valid": True,
            "category": "non_factual_safe"
        },
        {
            "query": "How do I import pandas?",
            "response": "import pandas as pd",
            "expected_valid": True,
            "category": "non_factual_safe"
        }
    ]

def run_validation_suite():
    detector = HallucinationDetector()
    test_cases = generate_test_cases()
    
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_tests": len(test_cases),
        "passed": 0,
        "failed": 0,
        "by_category": {},
        "details": []
    }
    
    print(f"\n=== HALLUCINATION VALIDATION SUITE ===")
    print(f"Running {len(test_cases)} test cases...\n")
    
    for i, case in enumerate(test_cases, 1):
        query = case["query"]
        response = case["response"]
        expected = case["expected_valid"]
        category = case["category"]
        
        # Run detector
        validation = detector.validate(query, response)
        actual = validation if isinstance(validation, bool) else validation.get("is_valid", False)
        
        # Track by category
        if category not in results["by_category"]:
            results["by_category"][category] = {"passed": 0, "total": 0}
        results["by_category"][category]["total"] += 1
        
        # Determine pass/fail
        test_passed = (actual == expected)
        if test_passed:
            results["passed"] += 1
            results["by_category"][category]["passed"] += 1
        else:
            results["failed"] += 1
        
        # Store details
        results["details"].append({
            "test_number": i,
            "query": query,
            "response": response,
            "expected_valid": expected,
            "actual_valid": actual,
            "category": category,
            "passed": test_passed
        })
        
        # Print live update
        status = "✅" if test_passed else "❌"
        print(f"{status} Test {i}: {category} | Expected: {expected} | Got: {actual}")
    
    # Write results to file
    output_file = "hallucination_validation_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print("\n=== SUMMARY ===")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']} ({results['passed']/results['total_tests']*100:.1f}%)")
    print(f"Failed: {results['failed']} ({results['failed']/results['total_tests']*100:.1f}%)")
    print("\nBy Category:")
    for cat, stats in results["by_category"].items():
        rate = stats["passed"]/stats["total"]*100 if stats["total"] > 0 else 0
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
    
    print(f"\n✅ Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    run_validation_suite()
