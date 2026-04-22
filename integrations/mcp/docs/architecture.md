# MCP Server Architecture

## Design Goals

1. **Zero hallucination risk** on factual queries
2. **Sub-millisecond cache hits** after first call
3. **Honest uncertainty** — returns `uncertain` instead of guessing
4. **Privacy-first** — query text hashed, no PII logged
5. **Standard MCP transport** — stdio by default, works with Claude Code, Cursor, Windsurf

## System Flow

```
User asks Claude Code a factual question
         ↓
Claude Code decides to call brain_api_query
         ↓
FastMCP server receives tool call
         ↓
Resolve API key (param → env → .env)
         ↓
Compute SHA-256 query hash (first 8 chars)
         ↓
POST to Brain API with X-API-Key header
         ↓
Brain API: Query → Token Reduction → Routing → Search/Facts/LLM → Validation
         ↓
Return BrainAPIResult { answer, confident, method }
         ↓
Log telemetry: hash + method + latency (NO query text)
         ↓
Return result to Claude Code
         ↓
Claude Code uses verified answer or flags uncertainty
```

## Component Breakdown

### FastMCP Server

- **Transport:** stdio (default for Claude Code compatibility)
- **Entry point:** `certainlogic-mcp` console script
- **Package:** `mcp[cli]` + `httpx` + `pydantic`
- **Model:** FastMCP from `mcp.server.fastmcp`

### Brain API Call

Uses `httpx.AsyncClient` for non-blocking HTTP:

```python
async with httpx.AsyncClient(timeout=BRAIN_API_TIMEOUT) as client:
    response = await client.post(
        BRAIN_API_ENDPOINT,
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        json={"query": query, "agent_id": "mcp"}
    )
```

### Error Handling

| Exception | Response | Action |
|---|---|---|
| `TimeoutException` | `method="error"`, suggest retry | Log timeout |
| `HTTPStatusError` (401) | `method="error"`, bad key | Check API key |
| `HTTPStatusError` (429) | `method="error"`, rate limited | Retry with backoff |
| `Generic Exception` | `method="error"`, details | Log stack trace |

### API Key Resolution Order

1. `api_key` parameter (from tool call)
2. `BRAIN_API_KEY` environment variable
3. `.env` file (loaded via `python-dotenv`)

**Security note:** Passing `api_key` as a parameter exposes it to the LLM.
Prefer environment variable configuration.

### Telemetry Logging

```
[BRAIN_API] ts=1713456789.123 query_hash=a1b2c3d4 method=facts latency_ms=42
```

**Logged:**
- `ts`: Unix timestamp
- `query_hash`: SHA-256(query), first 8 hex chars
- `method`: cache | facts | llm | uncertain | error
- `latency_ms`: End-to-end call time

**Never logged:**
- Query text
- Full query hash (only first 8 chars)
- API key
- User identity

## Response Methods

| Method | Meaning | Confidence | Speed | Cost |
|---|---|---|---|---|
| `cache` | Semantic cache hit (L2) | High | < 50ms | $0 |
| `facts` | Facts DB hit | Very high | < 100ms | $0 |
| `llm` | LLM found and validated answer | Medium | 2-5s | ~$0.0001 |
| `uncertain` | No data, not guessing | — | 50-100ms | $0 |
| `error` | Network/API failure | — | — | — |

## Performance Characteristics

| Operation | P50 | P99 |
|---|---|---|
| First query (cold) | 500ms | 5s |
| Cache hit | 10ms | 50ms |
| Facts DB hit | 50ms | 200ms |
| Error response | 10ms | 100ms |

## Extension Points

Future additions to the MCP server:

- `batch_query`: validate multiple facts in one call
- `audit_log`: retrieve verification history
- `warm_cache`: pre-populate cache with facts
- `subscribe`: push notifications for fact updates
- `guard`: direct hallucination detector access

## Security Model

```
User/Claude Code        FastMCP Server        Brain API
       │                      │                    │
       │  tool call           │                    │
       │─────────────────────>│                    │
       │                      │  HTTPS POST        │
       │                      │───────────────────>│
       │                      │                    │
       │                      │  encrypted         │
       │                      │  in transit        │
       │                      │                    │
       │  result              │                    │
       │<─────────────────────│                    │
```

- TLS 1.3 for all Brain API calls
- API key in headers, not URL or body
- Query text sent to Brain API but not retained by MCP server
- No local storage of queries or responses
