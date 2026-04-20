#!/usr/bin/env python3
"""
Demo script for CertainLogic Verifier.
Shows hallucination detection and token reduction in action.
"""

import json
import subprocess
import time
import sys

API_BASE = "http://localhost:8000"

def run_curl(data, endpoint="/validate"):
    """Make a POST request to the API."""
    cmd = [
        "curl", "-s", "-X", "POST", f"{API_BASE}{endpoint}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ curl failed: {result.stderr}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"❌ JSON decode error: {result.stdout[:200]}")
        return None

def print_step(title):
    """Print a step header."""
    print("\n" + "=" * 60)
    print(f"📌 {title}")
    print("=" * 60)

def demo_hallucination_detection():
    """Demo catching a price hallucination."""
    print_step("1. Catching a Price Hallucination")
    print("Query: What is the price of OpenAI GPT‑5?")
    print("Response: Its around $200 per month.\n")
    
    result = run_curl({
        "query": "What is the price of OpenAI GPT‑5?",
        "response": "Its around $200 per month."
    })
    
    if result:
        print("✅ Detector result:")
        print(f"   Valid: {result['valid']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Severity: {result['severity']}")
        if result.get('flags'):
            for flag in result['flags']:
                print(f"   ⚠️  {flag}")
        print("\n💡 The hallucination is flagged for human review!")

def demo_fact_verification():
    """Demo verifying a known fact."""
    print_step("2. Verifying a Known Fact")
    print("Query: What year was Python created?")
    print("Response: Python was created in 1991 by Guido van Rossum.\n")
    
    result = run_curl({
        "query": "What year was Python created?",
        "response": "Python was created in 1991 by Guido van Rossum."
    })
    
    if result:
        print("✅ Detector result:")
        print(f"   Valid: {result['valid']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Message: {result['checks']['factual_consistency']['message']}")
        print("\n💡 Correct facts pass with high confidence.")

def demo_token_reduction():
    """Demo token reduction via caching."""
    print_step("3. Token Reduction via Semantic Caching")
    print("Query: Explain quantum entanglement in simple terms...")
    print("(First call goes to LLM, second hits cache)\n")
    
    # First request
    result1 = run_curl({
        "query": "Explain quantum entanglement in simple terms",
        "semantic": True
    }, endpoint="/reduce")
    
    if result1:
        print(f"First request:")
        print(f"   Cache hit: {result1.get('cache_hit', False)}")
        print(f"   Reduced query length: {result1.get('reduced_length', 'N/A')}")
        print(f"   Original tokens: {result1.get('original_tokens', 'N/A')}")
        print(f"   Reduced tokens: {result1.get('reduced_tokens', 'N/A')}")
        
        # Simulate second request (same query)
        time.sleep(0.5)
        result2 = run_curl({
            "query": "Explain quantum entanglement in simple terms",
            "semantic": True
        }, endpoint="/reduce")
        
        if result2:
            print(f"\nSecond request (same query):")
            print(f"   Cache hit: {result2.get('cache_hit', False)}")
            print(f"   Reduced query length: {result2.get('reduced_length', 'N/A')}")
            if result2.get('cache_hit'):
                print("\n💡 Cache hit → zero tokens sent to LLM (100% savings)!")

def demo_uncertainty_penalty():
    """Demo penalty for uncertain language in factual responses."""
    print_step("4. Penalizing Uncertain Language")
    print("Query: What is the capital of France?")
    print("Response: I think it might be Paris, but I'm not sure.\n")
    
    result = run_curl({
        "query": "What is the capital of France?",
        "response": "I think it might be Paris, but I'm not sure."
    })
    
    if result:
        print("✅ Detector result:")
        print(f"   Valid: {result['valid']}")
        print(f"   Confidence: {result['confidence']}")
        issues = result['checks']['uncertainty']['issues']
        print(f"   Uncertainty phrases: {issues}")
        print("\n💡 Responses with 'I think', 'might be', 'not sure' get penalized.")

def main():
    print("🚀 CertainLogic Verifier – Live Demo")
    print("Make sure the service is running: uvicorn main:app --host 0.0.0.0 --port 8000")
    print()
    
    try:
        # Quick health check
        subprocess.run(["curl", "-s", f"{API_BASE}/health"], 
                      capture_output=True, check=True)
    except:
        print("❌ API not reachable. Start the service first.")
        print("   cd hallucination-guard && uvicorn main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    demo_hallucination_detection()
    demo_fact_verification()
    demo_uncertainty_penalty()
    demo_token_reduction()
    
    print_step("Demo Complete")
    print("✅ Hallucination detection ✓")
    print("✅ Fact verification ✓")  
    print("✅ Uncertainty penalty ✓")
    print("✅ Token reduction via caching ✓")
    print("\n🎯 Core use cases covered: blocking price hallucinations, verifying facts,")
    print("   penalizing uncertain language, and reducing token costs via caching.")

if __name__ == "__main__":
    main()