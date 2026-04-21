# API Endpoints

All endpoints accept and return JSON. The service runs on port 8000 by default.

## `POST /validate`

Validate an AI-generated response against the facts database.

**Request:**

```json
{
  "query": "What is 2+2?",
  "response": "4"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | ✅ | Original user query (1–2000 chars) |
| `response` | string | ✅ | AI-generated response to validate (1–10000 chars) |

**Response:**

```json
{
  "query": "What is 2+2?",
  "valid": true,
  "flagged": false,
  "confidence": 1.0,
  "severity": "none",
  "flags": [],
  "checks": {
    "factual_consistency": {"passed": true, "message": "...", "score": 1.0},
    "uncertainty": {"passed": true, "issues": [], "score": 1.0},
    "internal_consistency": {"passed": true, "issues": [], "score": 1.0},
    "specificity": {"passed": true, "message": "...", "score": 1.0}
  }
}
```

---

## `POST /reduce`

Reduce token count via caching and deterministic lookup.

**Request:**

```json
{
  "query": "Explain quantum theory in detail",
  "semantic": true
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | — | Query to reduce (1–5000 chars) |
| `force_deterministic` | bool | `false` | Skip LLM, use deterministic fallback only |
| `semantic` | bool | `true` | Try semantic cache on exact-hash miss |

---

## `POST /search`

Search verified facts via TF-IDF over the memory index.

**Request:**

```json
{
  "query": "Python best practices",
  "top_k": 5
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | — | Search query (1–500 chars) |
| `top_k` | int | `5` | Max results |

---

## `POST /route`

Classify a query and route to the appropriate handler.

**Request:**

```json
{
  "query": "What is the price of GPT-5?"
}
```

**Response includes:** `brain_handler`, `openclaw_model`, `compressed` query, `token_count`, full `intent` classification.

---

## `GET /health`

Health check. Returns component status.

```json
{
  "status": "ok",
  "components": {
    "token_engine": "ok",
    "memory_search": "ok",
    "hallucination_detector": "ok",
    "facts_db": "175 facts loaded"
  }
}
```

---

## `GET /metrics`

Returns cache hit rates, token savings, cost tracking, and query volumes. Requires API key header: `X-API-Key`.

---

## `DELETE /cache`

Purge the token-reduction cache.

```json
{"cleared": true}
```
