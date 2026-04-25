# CertainLogic Hermes Integration — Customer Dry Run

## Overview

This integration treats Hermes (our internal coding agent) as if it were a paying customer using the CertainLogic Brain API SaaS. This validates that our tech stack works end-to-end before shipping to real customers.

## Architecture

```
Hermes (Kimi K2.6 via OpenRouter)
  │
  ├─→ [PRE] CertainLogic BrainClient.reduce(spec)
  │     → Token reduction (~20% savings)
  │     → Cache check (bypass LLM if deterministic)
  │
  ├─→ [LLM] Kimi generates code
  │
  ├─→ [POST] CertainLogic BrainClient.validate(query, response)
  │     → Hallucination detection
  │     → Flag hedge language
  │     → Check factual consistency
  │
  └─→ [LOG] Metrics per session
```

## Files

| File | Purpose |
|---|---|
| `scripts/hermes_brain_client.py` | BrainClient class — reduce + validate + log |
| `scripts/brain_logs/*.json` | Session metrics (cache hits, tokens saved, errors) |

## Usage in Hermes Specs

When writing a spec for Hermes, include this at the top:

```python
import sys
sys.path.insert(0, "/data/.openclaw/workspace/opensource/scripts")
from hermes_brain_client import BrainClient

client = BrainClient()

# 1. Reduce spec tokens before reasoning
reduced_spec, tokens_saved = client.reduce(full_spec_text)

# 2. After implementation, validate the code
for test_case in test_cases:
    result = client.validate(test_case["query"], test_case["response"])
    if not result["valid"]:
        print(f"WARNING: {result['flags']}")

# 3. Log session
client.log_task("spec_name", tokens_saved=tokens_saved, validation=result)
client.save_session_log()
```

## Metrics Tracked

Per session:
- Total tasks
- Cache hits / cache hit rate
- Tokens saved
- Validations passed / flagged
- Hallucination flags caught

## Current Status

| Metric | Value |
|---|---|
| Brain API | ✅ Healthy (52 facts loaded) |
| Cache hit rate (overall) | 19.56% |
| Validation accuracy | 100% (relevant categories) |

## Running the Demo

```bash
cd /data/.openclaw/workspace/opensource
python3 scripts/hermes_brain_client.py
```

This simulates a customer agent making reduce + validate calls and logs metrics.
