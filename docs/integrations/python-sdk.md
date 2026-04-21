# Python SDK

Use CertainLogic Verifier directly in Python without running the HTTP service.

## Installation

```bash
pip install hallucination-guard
```

## Hallucination Detection

```python
from hallucination_guard.hallucination_detector import HallucinationDetector

detector = HallucinationDetector(facts_db_path="./facts_db.json")

# Validate a response
result = detector.validate(
    query="What is the speed of light?",
    response="The speed of light is approximately 300,000 km/s"
)

print(result["valid"])       # True
print(result["confidence"])  # 1.0
print(result["flags"])       # []
```

## Token Reduction

```python
from hallucination_guard.token_reduction_engine import TokenReductionEngine

engine = TokenReductionEngine(cache_db_path="./cache.db")

result = engine.reduce(
    query="Explain quantum entanglement in simple terms",
    semantic=True
)

if result["cache_hit"]:
    print("Answered from cache — 0 tokens!")
    print(result["cached_response"])
else:
    print(f"Reduced to {result['token_count']} tokens")
```

## Semantic Cache

```python
from hallucination_guard.semantic_cache import SemanticCache

cache = SemanticCache()

# Store a response
cache.store("What is Python?", "Python is a programming language...")

# Retrieve similar queries
result = cache.search("Tell me about Python", threshold=0.85)
if result:
    print(f"Cache hit (similarity: {result['score']:.2f})")
```

## Intent Classification

```python
from hallucination_guard.intent_classifier import classify_intent

intent = classify_intent("What is the price of GPT-5?")
print(intent["category"])   # "pricing"
print(intent["confidence"]) # 0.95
```
