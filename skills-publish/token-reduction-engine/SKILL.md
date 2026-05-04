---
name: token-reduction-engine
description: "Deterministic AI validation middleware. Zero LLM calls for facts. Requires Brain API endpoint configuration."
---

# Token Reduction Engine

Deterministic validation without LLM calls. Catches hallucinations before they reach users.

## Requirements

- Brain API endpoint (user-configured)
- Python 3.10+

## Install

```bash
pip install requests  # optional, urllib fallback available
```

## Configuration

**Required:** Set Brain API endpoint before use.

```bash
export CERTAINLOGIC_API="http://your-brain-api.com"
```

Or pass directly:

```python
from scripts.hguard_client import HGuardClient
client = HGuardClient(api_url="http://your-brain-api.com")
```

**No default endpoint. No hardcoded URLs.** The client requires explicit configuration.

## Usage

```python
from scripts.hguard_client import HGuardClient

# Must configure endpoint first
client = HGuardClient(api_url="http://your-brain-api.com")

# Validate a response
result = client.validate("What is 2+2?", "5")
print(result["valid"])   # False
print(result["flags"])   # ["Factual mismatch"]
```

## CLI

```bash
# Validate a single response
python3 scripts/hguard_client.py validate "What is 2+2?" "5"

# Check Brain API health
python3 scripts/hguard_client.py status
```

## Error Handling

| Error | Fix |
|-------|-----|
| "Brain API URL required" | Set `CERTAINLOGIC_API` env var or pass `api_url=...` |
| "HTTP 404" | Check endpoint URL is correct |
| "Connection refused" | Brain API server not running |
