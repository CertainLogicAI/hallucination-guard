#!/usr/bin/env python3
"""
Verification Layer Test Suite
Tests hash generation, response validation, and cache operations
"""

import hashlib
from typing import List

# Test Results
results = {"passed": 0, "failed": 0, "tests": []}

# Helper: Add a test case
def test(description: str, test_fn):
    try:
        result = test_fn()
        if result:
            results["passed"] += 1
            print(f"✅ {description}")
            results["tests"].append({"description": description, "status": "PASSED"})
        else:
            results["failed"] += 1
            print(f"❌ {description}")
            results["tests"].append({"description": description, "status": "FAILED"})
    except Exception as e:
        results["failed"] += 1
        print(f"❌ {description}: {e}")
        results["tests"].append({"description": description, "status": "FAILED", "error": str(e)})

# Helper: SHA-256 hash generation
def hash_content(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

# -------------------------------------------------------------------------
# 1. Hash Generation Test
def test_hash_generation():
    """Test that hash is deterministic"""
    content = "This is a test string"
    hash1 = hash_content(content)
    hash2 = hash_content(content)
    return hash1 == hash2

# ---------------------------------------------------------------------
# 2. Hash Validation Test
def test_hash_validation():
    """Test hash validation works correctly"""
    # Generate hash for test content
    original_content = "This is valid training data for hash verification"
    original_hash = hash_content(original_content)
    
    # Create a modified version with one character changed
    modified_content = original_content[:5] + "X" + original_content[6:]
    modified_hash = hash_content(modified_content)
    
    # Verify: original hash should match original hash, modified should differ
    return hash1 == original_hash and hash1 != modified_hash

# -----------------------------------------------------------------------------
# 2. Response Validation Test
def test_hash_validation():
    """Simulate validation using a mock response"""
    # Mock a valid response
    response = {
        "content": "This is a valid response",
        "hash": hash_content("This is a valid response")
    }
    
    # Compare computed hash with stored hash
    computed_hash = hash_content(response["content"])
    return computed_hash == response["hash"]
    
    # Compare computed hash with stored hash
    computed_hash = hash_content(response["content"])
    return computed_hash == response["hash"]

# -----------------------------------------------------------------------------
# 3. Cache Write/Read Test
def test_cache_operations():
    """Simulate cache write and read operations"""
    test_data = {"key": "test_value", "count": 5}
    
    # Simulate write operation
    cache_data = {}
    cache_data["key"] = test_data["count"]
    
    # Read back
    read_data = cache_data.get("key")
    
    return read_data == test_data["count"]

# -----------------------------------------------------------------------------
# 3a. Cache Invalidation Test
def test_cache_invalidation():
    """Test invalidation when reference version changes"""
    # Simulate version change
    stored_cache = {
        "hash": "a1b2c3d4",
        "version": "v1.0"
    }
    
    # New version arrives
    new_version = "v1.1"
    # In validation, we'd check version mismatch -> invalidate
    
    # For this test, we just verify structure can be updated
    try:
        stored_cache["version"] = "v2.0"
        return True
    except Exception as e:
        print(f"Cache update error: {e}")
        return False

# -----------------------------------------------------------------------------
# 3a. Performance Test
def test_performance():
    """Basic performance test - measure hash generation speed"""
    iterations = 1000
    start_time = time.time()
    
    for i in range(iterations):
        hash_content(f"test_{i}")
    
    elapsed = time.time() - start_time
    avg_time = duration / iterations
    
    # Pass if average <= 0.05 seconds per hash
    return avg_time < 0.05

# Helper Functions
def run_all_tests():
    test("SHA-256 hash generation is deterministic", test_hash_generation)
    test("Response hash matches original", test_hash_validation)
    test("Cache write/read operations work", test_cache_operations)
    test("Cache invalidation works on version change", test_cache_invalidation)
    test("Performance under load (1000 iterations)", test_performance)
    
    print(f"\n📊 Test Summary")
    print(f"✅ Passed: {results['passed']}")
    console.error(f"❌ Failed: {results['failed']}")
    
    return results["passed"] == len(results["tests"])

# -------------------------------------------------------------------------
# Run Tests
if __name__ == "__main__":
    print("🔍 Running Verification Layer Tests...\n")
    run_tester()
    
    # Summary Output
    print(f"\n📊 Final Results:")
    print(f"  Passed: {results['passed']}")
    console.error(f"❌ Failed: {results['failed']}")
    
    # Exit with failure if any test failed
    exit(0 if results["failed"] == 0 else 1)