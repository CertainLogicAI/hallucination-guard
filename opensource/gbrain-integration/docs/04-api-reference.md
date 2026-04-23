# API Reference

## MCP Server Tools

CertainLogic's MCP server exposes the following tools for gbrain integration:

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

```
brain_api_query(query="Did Acme AI raise $50M in March 2026?")

→ {
    "answer": "Yes. Acme AI raised $50M Series B led by Sequoia Capital in March 2026.",
    "confident": true,
    "method": "facts"
  }
```

**Cost:** Free tier cache hits = $0. Facts DB hits = $0. LLM calls ~$0.0001 per query.

**Latency:**
- Cache hit: ~50ms
- Facts DB hit: ~100ms
- LLM: ~2-5s

---

### `verify_fact` (Guard)

Validate a claim against source text using the hallucination detector.

**Parameters:**

```json
{
  "claim": "string, required — the claim to verify",
  "source_text": "string, required — the text to validate against",
  "strictness": "number, optional — 0.7 (coder) | 0.8 (agent) | 0.9 (enterprise)"
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

```
verify_fact(
  claim="Acme AI has 200 employees",
  source_text="Acme AI reported 200 employees in their March 2026 SEC filing.")

→ {
    "valid": true,
    "confidence": 0.99,
    "reason": "Explicitly stated in source text",
    "method": "filter"
  }
```

---

### `log_audit_entry`

Log a verification decision to the audit chain.

**Parameters:**

```json
{
  "task_id": "string — UUID of the enrichment task",
  "entity": "string — person/company name",
  "claim": "string — the claim text",
  "result": "string — validated | uncertain | rejected",
  "method": "string — cache | facts | llm | filter | uncertain",
  "source": "string, optional — verification source",
  "corrected_fact": "string, optional — if claim was rejected, what the correct fact is"
}
```

**Response:**

```json
{
  "status": "ok",
  "audit_id": "uuid",
  "timestamp": "2026-04-21T20:07:00Z",
  "fact_hash": "sha256-hash-of-claim"
}
```

**Example:**

```
log_audit_entry(
  task_id="550e8400-e29b-41d4-a716-446655440000",
  entity="Acme AI",
  claim="Raised $50M",
  result="validated",
  method="facts",
  source="TechCrunch, 2026-03-15")

→ {
    "status": "ok",
    "audit_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-04-21T20:07:00Z",
    "fact_hash": "3a8f7d..."
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
  -d '{"query": "Did Acme AI raise $50M?", "agent_id": "gbrain"}'
```

#### POST `/validate`

```bash
curl -X POST https://api.certainlogic.ai/validate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"query": "Acme AI has 200 employees", "text": "source text here"}'
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

### `brain_api_query` Errors

| Code | HTTP | Meaning | Action |
|---|---|---|---|
| `VALIDATED` | 200 | Fact confirmed | Write to compiled truth |
| `UNCERTAIN` | 200 | No data available | Write to timeline as UNVERIFIED |
| `error` | 401 | Invalid API key | Check `BRAIN_API_KEY` env var |
| `error` | 429 | Rate limited | Wait, retry, or upgrade plan |
| `error` | 503 | Brain API unavailable | Check `/health`, retry later |

### `verify_fact` (Guard) Errors

| Code | Meaning | Action |
|---|---|---|
| `filter: true` | Claim supported by source | Write to compiled truth |
| `filter: false` | Claim contradicted by source | Reject, log audit |
| `llm: true` | LLM confirms claim | Write with [Guard validated] tag |
| `llm: false` | LLM rejects claim | Reject, log audit |
| `uncertain` | Unclear from source | Write to timeline as UNVERIFIED |

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
| `BRAIN_API_ENDPOINT` | No | `https://api.certainlogic.ai/query` | API endpoint |
| `BRAIN_API_TIMEOUT` | No | `10` | Request timeout in seconds |
| `MCP_LOG_LEVEL` | No | `INFO` | MCP server logging level |

---

## Fact Database Schema

CertainLogic stores facts in this format:

```json
{
  "acme ai funding amount": {
    "type": "string",
    "value": "$50M Series B",
    "verified": true,
    "aliases": [
      "acme ai raised amount",
      "how much did acme ai raise",
      "acme ai series b size"
    ],
    "category": "business",
    "source_url": "https://techcrunch.com/2026/03/15/acme-ai-50m/"
  }
}
```

**Fields:**
- `key`: lowercase, kebab-case, 3-8 words
- `type`: `string` | `number` | `boolean` | `list`
- `value`: the factual answer
- `verified`: boolean — has this been checked?
- `aliases`: alternative phrasings that match this fact
- `category`: `business` | `technology` | `science` | `regulation` | `people` | etc.
- `source_url`: provenance link

---

## Response Time Targets

| Metric | Target | P99 |
|---|---|---|
| Cache hit | < 100ms | < 200ms |
| Facts DB hit | < 200ms | < 500ms |
| LLM call | < 3s | < 10s |
| Guard (filter) | < 50ms | < 100ms |
| Guard (LLM) | < 3s | < 8s |

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-04-21 | Initial integration: MCP server, fact validation, audit logging |
| 1.1.0 | Planned | Periodic re-validation in maintain skill |
| 2.0.0 | Planned | Enhanced cryptographic audit integrity |

---

*API version 1.0.0 | Base URL: https://api.certainlogic.ai*
