# API Reference

## MCP Server Tools

CertainLogic's MCP server exposes the following tools for AI agent integration:

---

### `brain_api_query`

Check a factual claim against the CertainLogic knowledge base.

**Parameters:**

```json
{
  "query": "string, required — the factual question to check",
  "agent_id": "string, optional — identifies the calling agent for metrics"
}
```

**Response:**

```json
{
  "answer": "string — the verified answer, or uncertainty explanation",
  "confident": "boolean — true if answer is verified, false if uncertain",
  "method": "string — how the answer was resolved: cache | facts | llm | uncertain"
}
```

**Example:**

```python
brain_api_query(query="Did Acme AI raise $50M in March 2026?")

→ {
    "answer": "Yes. Acme AI raised $50M Series B led by Sequoia Capital in March 2026.",
    "confident": true,
    "method": "facts"
  }
```

**Cost:** Free tier cache hits = $0. Facts DB hits = $0. LLM calls ~$0.0001 per query.

**Latency:**
- Cache hit: ~10ms
- Facts DB hit: ~50ms
- LLM: ~2-5s

---

### `batch_query`

Validate multiple facts in a single call.

**Parameters:**

```json
{
  "queries": "array of strings, required — list of factual questions",
  "api_key": "string, optional — Brain API key"
}
```

**Response:**

```json
{
  "results": [
    {
      "query": "string — original query",
      "answer": "string — verified answer",
      "confident": "boolean",
      "method": "string"
    }
  ],
  "total": "integer — total queries processed",
  "confident": "integer — count of confident answers",
  "uncertain": "integer — count of uncertain answers",
  "errors": "integer — count of errors"
}
```

**Example:**

```python
batch_query(
    queries=[
        "Python 3.12 release date",
        "PEP 8 author",
        "Django default port"
    ]
)

→ {
    "results": [
      {"query": "Python 3.12 release date", "answer": "October 2, 2023", "confident": true, "method": "facts"},
      {"query": "PEP 8 author", "answer": "Guido van Rossum, Barry Warsaw, Nick Coghlan", "confident": true, "method": "facts"},
      {"query": "Django default port", "answer": "8000", "confident": true, "method": "cache"}
    ],
    "total": 3,
    "confident": 3,
    "uncertain": 0,
    "errors": 0
  }
```

---

### `verify_fact_guard`

Validate a claim against source text using the hallucination detector.

**Parameters:**

```json
{
  "claim": "string, required — the claim to verify",
  "source_text": "string, required — the text to validate against",
  "strictness": "number, optional — 0.7 (coder) | 0.8 (agent) | 0.9 (enterprise)",
  "api_key": "string, optional — Brain API key"
}
```

**Response:**

```json
{
  "valid": "boolean | null — true if supported, false if contradicted, null if unclear",
  "confidence": "number — 0.0 to 1.0 confidence score",
  "reason": "string — explanation of the decision",
  "method": "string — filter (deterministic) | llm | uncertain"
}
```

**Example:**

```python
verify_fact_guard(
    claim="Acme AI has 200 employees",
    source_text="Acme AI reported 200 employees in their March 2026 SEC filing.",
    strictness=0.9
)

→ {
    "valid": true,
    "confidence": 0.99,
    "reason": "Explicitly stated in source text",
    "method": "filter"
  }
```

---

### `health_check`

Check if the Brain API is available and responsive.

**Parameters:** None

**Response:**

```json
{
  "status": "string — ok | degraded | down",
  "components": "dict — subsystem status (db, cache, llm, etc.)",
  "latency_ms": "integer — response time in milliseconds"
}
```

**Example:**

```python
health_check()

→ {
    "status": "ok",
    "components": {
      "db": "ok",
      "cache": "ok",
      "llm": "ok"
    },
    "latency_ms": 42
  }
```

---

## HTTP API (Direct)

If MCP is not available, call the Brain API directly:

### Authentication

```
X-API-Key: your_api_key
```

### Endpoints

#### POST `/query`

```bash
curl -X POST https://api.certainlogic.ai/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"query": "Did Acme AI raise $50M?", "agent_id": "mcp"}'
```

#### POST `/batch`

```bash
curl -X POST https://api.certainlogic.ai/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"queries": ["Q1", "Q2", "Q3"]}'
```

#### POST `/validate`

```bash
curl -X POST https://api.certainlogic.ai/validate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{
    "query": "Claim to verify",
    "text": "Source text to validate against",
    "strictness": 0.8
  }'
```

#### GET `/health`

```bash
curl https://api.certainlogic.ai/health
→ {"status": "ok", "components": {...}}
```

#### GET `/metrics`

```bash
curl https://api.certainlogic.ai/metrics \
  -H "X-API-Key: YOUR_KEY"
```

Returns:
```json
{
  "token_engine": {
    "total_queries": 1154,
    "cache_hits": 616,
    "cache_hit_rate_percent": 47.42
  },
  "openrouter": {
    "total": 2474,
    "today": 52,
    "total_cost_usd": 2.28
  },
  "rates": {
    "cache_hit_rate_pct": 23.73,
    "validation_pass_rate_pct": 85.36
  }
}
```

---

## Error Codes

### `brain_api_query` / `batch_query` Errors

| Code | HTTP | Meaning | Action |
|---|---|---|---|
| `VALIDATED` | 200 | Fact confirmed | Use answer |
| `UNCERTAIN` | 200 | No data available | Flag for review or use LLM |
| `error` | 401 | Invalid API key | Check `BRAIN_API_KEY` env var |
| `error` | 429 | Rate limited | Wait, retry, or upgrade plan |
| `error` | 503 | Brain API unavailable | Check `/health`, retry later |

### `verify_fact_guard` Errors

| Code | Meaning | Action |
|---|---|---|
| `filter: true` | Claim supported by source | Use claim |
| `filter: false` | Claim contradicted by source | Reject claim |
| `llm: true` | LLM confirms claim | Use with caution |
| `llm: false` | LLM rejects claim | Reject claim |
| `uncertain` | Unclear from source | Flag for review |

---

## Rate Limits

| Tier | Queries/Day | Cost |
|---|---|---|
| Free | 100 | $0 |
| Coder Pack | Unlimited | $69 one-time |
| Agent | Unlimited + priority | $499/yr |
| Enterprise | Unlimited + SLA | $2,499/yr |

Cache hits don't count against quota.

**Burst limits:**
- Free: 10 requests/second
- Paid: 100 requests/second

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `BRAIN_API_KEY` | Yes | — | Your CertainLogic API key |
| `BRAIN_API_ENDPOINT` | No | `https://api.certainlogic.ai/query` | Query endpoint |
| `BRAIN_VALIDATE_ENDPOINT` | No | `https://api.certainlogic.ai/validate` | Guard endpoint |
| `BRAIN_HEALTH_ENDPOINT` | No | `https://api.certainlogic.ai/health` | Health endpoint |
| `BRAIN_API_TIMEOUT` | No | `10` | Request timeout (seconds) |
| `BRAIN_API_MAX_RETRIES` | No | `3` | Max retries on 5xx/network errors |
| `BRAIN_API_RETRY_BASE_DELAY` | No | `1.0` | Base delay for exponential backoff |
| `BRAIN_API_RETRY_MAX_JITTER` | No | `0.5` | Max jitter added to retry delay |
| `MCP_LOG_LEVEL` | No | `INFO` | MCP server logging level |

---

## Response Methods Explained

| Method | Meaning | Confidence | Speed | Cost | Use When |
|---|---|---|---|---|---|
| `cache` | Semantic cache hit (L2) | High | < 50ms | $0 | Repeated queries |
| `facts` | Facts DB hit | Very high | < 100ms | $0 | Single fact lookup |
| `llm` | LLM found and validated answer | Medium | 2-5s | ~$0.0001 | Uncovered domain |
| `uncertain` | No data, not guessing | — | 50-100ms | $0 | Gap in knowledge base |
| `error` | Network/API failure | — | — | — | Retry or degrade |

---

## Response Time Targets

| Metric | Target | P99 |
|---|---|---|
| Cache hit | < 50ms | < 100ms |
| Facts DB hit | < 100ms | < 200ms |
| LLM call | < 3s | < 10s |
| Guard (filter) | < 50ms | < 100ms |
| Guard (LLM) | < 3s | < 8s |
| Health check | < 200ms | < 500ms |
| Retry overhead | +1-4s | +8s |

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 0.1.0 | 2026-04-21 | Initial release: single query, batch query, Guard, health check |
| 0.2.0 | Planned | Streaming responses, subscription push |
| 1.0.0 | Planned | Cryptographic audit chain, AgentPathfinder integration |

---

*API version 0.1.0 | Base URL: https://api.certainlogic.ai*
