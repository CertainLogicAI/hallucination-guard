---
summary: "Hallucination Guard"
read_when: ["installing", "configuring", "troubleshooting"]
---

# Hallucination Guard

Deterministic AI validation middleware. Catches hallucinations before they reach users. Zero LLM calls required for fact-based queries. Typical results: 20% token savings, 95%+ accuracy on facts.

## Quick Reference

| Need | Command |
|------|---------|
| Validate a response | `hguard validate "query" "response"` |
| Batch validate | `hguard batch <input.json> <output.json>` |
| Check status | `hguard status` |

## Installation

### 1. Install the skill

```bash
clawhub install hallucination-guard
```

### 2. Verify Brain API (included)

```bash
hguard status
```

Should show:
```
Brain API: OK (52 facts loaded)
Validation accuracy: 100% (relevant categories)
```

### 3. Use in your agent

Import and call from any Python script:

```python
import sys
sys.path.insert(0, "/usr/local/lib/node_modules/openclaw/skills/hallucination-guard/scripts")
from hguard_client import HGuardClient

client = HGuardClient()

# Validate any AI-generated text
result = client.validate("What is Docker?", "Docker is a containerization platform.")
print(result["valid"])   # True
print(result["confidence"])  # 1.0

# Check for hallucinations
bad_result = client.validate(
    "What is Python recursion depth?",
    "Python recursion depth is 500."
)
print(bad_result["valid"])      # False
print(bad_result["flags"])      # ["Factual mismatch: ..."]
```

## Agent Integration

Add to your agent's system prompt:

```
You are integrated with the CertainLogic Hallucination Guard.
When making factual claims in your responses, call validate() on the claim.
If validation flags the response, revise before shipping.
```

Or add to agent config:

```json
{
  "preProcess": "hguard validate",
  "postProcess": "hguard validate"
}
```

## CLI Reference

### validate
```bash
hguard validate "query text" "response text"
```

### batch
```bash
hguard batch input.json output.json
```

Input format:
```json
[
  {"query": "What is 2+2?", "response": "4"},
  {"query": "What is 2+2?", "response": "5"}
]
```

## Metrics

Track your agent's performance:

```python
metrics = client.get_session_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']}%")
print(f"Tokens saved: {metrics['tokens_saved']}")
print(f"Hallucinations caught: {metrics['flags_caught']}")
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Brain API not found" | Start the brain: `python3 scripts/start_brain.py` |
| "No facts loaded" | Load facts: `hguard load-facts facts.json` |
| Validation too strict | Adjust threshold: `client.set_threshold(0.5)` |
| False positives on hypotheticals | Add hedges to query |

## Uninstall

```bash
clawhub uninstall hallucination-guard
```

## License
MIT-0 (Free, no attribution required)
