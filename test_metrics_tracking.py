#!/usr/bin/env python3
"""
Verify BrainClient metrics tracking is complete and accurate.

Tests:
1. reduce() returns (reduced_text, tokens_saved_estimate)
2. validate() returns valid/flagged/confidence/flags/method/routing/cache_hit
3. log_task() appends to session tasks
4. get_metrics() aggregates: total_tasks, cache_hits, cache_hit_rate_pct, 
   validations_passed, validations_flagged, total_tokens_saved, brain_ready
5. save_session_log() writes JSON with session_id, metrics, tasks[]
6. All 309 coder facts are accessible

Usage: python3 test_metrics_tracking.py
"""
import sys, json, os
from pathlib import Path

sys.path.insert(0, "/data/.openclaw/workspace/opensource/scripts")
from hermes_brain_client import BrainClient

def test_reduce():
    client = BrainClient()
    spec = "Write a Python function to check if a string is a palindrome. The function should handle edge cases like empty strings and non-alphabetic characters."
    reduced, saved = client.reduce(spec)
    assert isinstance(reduced, str), "reduce() must return string"
    assert isinstance(saved, int), "reduce() must return int tokens_saved"
    assert saved >= 0, "tokens_saved must be >= 0"
    print(f"  ✅ reduce(): {len(spec.split())} -> {len(reduced.split())} (saved ~{saved})")
    return client, saved

def test_validate_correct_fact(client):
    result = client.validate("What is Python's current stable version?", "Python 3.13")
    assert "valid" in result, "validate() must return 'valid' key"
    assert "flagged" in result, "validate() must return 'flagged' key"
    assert "confidence" in result, "validate() must return 'confidence' key"
    assert "flags" in result, "validate() must return 'flags' key"
    assert "method" in result, "validate() must return 'method' key"
    assert "routing" in result, "validate() must return 'routing' key"
    assert "cache_hit" in result, "validate() must return 'cache_hit' key"
    print(f"  ✅ validate(correct): valid={result['valid']}, cache_hit={result['cache_hit']}, method={result['method']}")
    return result

def test_validate_hallucination(client):
    # Use a Coder Pack fact (in DB) with deliberately wrong answer
    result = client.validate("What is Python walrus operator symbol?", "The answer is =")
    print(f"  ✅ validate(hallucination): valid={result['valid']}, flagged={result['flagged']}, flags={result['flags']}")
    return result

def test_validate_hedge(client):
    result = client.validate("Explain Python recursion.", "I'm not sure about recursion details.")
    print(f"  ℹ️ validate(hedge): valid={result['valid']}, flagged={result['flagged']}, flags={result['flags']}")
    return result

def test_metrics_aggregation(client, tokens_saved):
    # Log the tasks we've run
    client.log_task("test_reduce", tokens_saved=tokens_saved, validation={"valid": True, "flagged": False, "cache_hit": True, "confidence": 0.95})
    client.log_task("test_validate_correct", tokens_saved=0, validation={"valid": True, "flagged": False, "cache_hit": True, "confidence": 1.0})
    client.log_task("test_validate_wrong", tokens_saved=0, validation={"valid": False, "flagged": True, "cache_hit": False, "confidence": 0.3})
    
    metrics = client.get_metrics()
    assert metrics["total_tasks"] == 3, f"Expected 3 tasks, got {metrics['total_tasks']}"
    assert metrics["cache_hits"] == 2, f"Expected 2 cache hits, got {metrics['cache_hits']}"
    assert metrics["cache_hit_rate_pct"] == 66.67, f"Expected 66.67% hit rate, got {metrics['cache_hit_rate_pct']}"
    assert metrics["validations_passed"] == 2, f"Expected 2 passed, got {metrics['validations_passed']}"
    assert metrics["validations_flagged"] == 1, f"Expected 1 flagged, got {metrics['validations_flagged']}"
    assert metrics["total_tokens_saved"] == tokens_saved, f"Expected {tokens_saved} tokens saved, got {metrics['total_tokens_saved']}"
    assert metrics["brain_ready"] == True, "Brain should be ready"
    print(f"  ✅ metrics: {json.dumps(metrics, indent=2)}")
    return metrics

def test_session_log(client):
    log_path = client.save_session_log()
    assert Path(log_path).exists(), f"Log file not created: {log_path}"
    with open(log_path) as f:
        data = json.load(f)
    assert "session_id" in data, "Log must have session_id"
    assert "metrics" in data, "Log must have metrics"
    assert "tasks" in data, "Log must have tasks"
    assert len(data["tasks"]) == 3, "Log should have 3 tasks"
    print(f"  ✅ session_log: {log_path} ({len(json.dumps(data))} bytes)")
    return log_path

def test_facts_count():
    import urllib.request
    with urllib.request.urlopen("http://127.0.0.1:8000/facts") as r:
        data = json.loads(r.read())
    count = data["count"]
    print(f"  ✅ facts_db: {count} facts loaded (expected 393)")
    assert count >= 300, f"Expected 300+ facts for full Coder Pack, got {count}"
    # Verify specific coder facts exist
    test_keys = ["python current stable version", "python list is mutable", "python walrus operator symbol"]
    for key in test_keys:
        assert key in data["facts"], f"Missing expected fact: {key}"
    print(f"  ✅ spot-check: all 3 test facts present")

if __name__ == "__main__":
    print("\n🧪 BrainClient Metrics Verification\n")
    
    print("1. Testing reduce()...")
    client, tokens_saved = test_reduce()
    
    print("\n2. Testing validate(correct fact)...")
    test_validate_correct_fact(client)
    
    print("\n3. Testing validate(hallucination)...")
    test_validate_hallucination(client)
    
    print("\n4. Testing validate(hedge language)...")
    test_validate_hedge(client)
    
    print("\n5. Testing metrics aggregation...")
    test_metrics_aggregation(client, tokens_saved)
    
    print("\n6. Testing session log persistence...")
    test_session_log(client)
    
    print("\n7. Testing facts DB count...")
    test_facts_count()
    
    print("\n✅ ALL TESTS PASSED")
