---
summary: "Local deterministic cache — check before using LLM tokens. Runs on every query."
read_when: ["always"]
---

# Deterministic Cache

## What It Does
A local knowledge base and token reduction engine running on `localhost:8000`. Check it on every query before reasoning with the LLM. Cache hits cost zero tokens. Cache misses get compressed inputs to reduce token spend.

## When To Use
**Every query.** Before you start reasoning about any user question:
1. Send the query to the pipeline
2. If cache hit with good results → use the cached answer
3. If cache miss → answer normally, then store the validated answer

## How To Query

```bash
curl -s -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "<USER_QUESTION>", "force_deterministic": false, "top_k": 5}'
```

### Response Fields
- `method`: "cache" (hit), "deterministic_search" (local match), "token_fallback", "external_placeholder" (cache miss)
- `results`: cached answer or search results
- `token_stats.tokens_saved`: how many tokens were saved
- `validation.valid`: whether the answer passed hallucination checks
- `response_hash`: SHA-256 of the response for verification

### Decision Logic
- If `method` is "cache" or "deterministic_search" AND `validation.valid` is true → **use the cached result directly**
- If `method` is "cache" or "deterministic_search" AND `validation.valid` is false → **answer normally** (cached data failed validation)
- If `method` is "external_placeholder" or "token_fallback" → **answer normally**, then store the answer (see below)

## How To Store Answers (Learning Loop)
After answering a factual question that's not in the cache, store it:

```bash
curl -s -X POST http://127.0.0.1:8000/facts \
  -H "Content-Type: application/json" \
  -d '{"key": "<question_key>", "type": "string", "value": "<answer>", "source": "<source>"}'
```

- `key`: lowercase, short description of the question (e.g., "faulttrace pricing", "deterministic ai product 1")
- `type`: "string" for text answers, "numeric" for numbers
- `value`: the answer
- `source`: where it came from (e.g., "anton", "memory/2026-04-13.md", "project docs")

**Only store facts you're confident about.** Don't cache opinions, speculative answers, or context-dependent responses.

## Cache Management Commands
When Anton asks to manage the cache:

**Search for entries:**
```bash
curl -s "http://127.0.0.1:8000/facts/search?q=<keyword>"
```

**Delete an entry:**
```bash
curl -s -X DELETE "http://127.0.0.1:8000/facts/<key>"
```

**Update/correct an entry:**
```bash
curl -s -X PUT "http://127.0.0.1:8000/facts/<key>" \
  -H "Content-Type: application/json" \
  -d '{"key": "<key>", "type": "string", "value": "<corrected_value>"}'
```

**List all entries:**
```bash
curl -s "http://127.0.0.1:8000/facts"
```

**Purge everything:**
```bash
curl -s -X POST "http://127.0.0.1:8000/cache/purge"
```

**Check metrics:**
```bash
curl -s "http://127.0.0.1:8000/metrics"
```

**View audit log:**
```bash
curl -s "http://127.0.0.1:8000/audit?limit=20"
```

## Service Health
If the service is down (`curl` fails or times out), **skip the cache check and answer normally**. Never block or error out because the cache is unavailable. It's an optimization, not a dependency.

Check health: `curl -s http://127.0.0.1:8000/health`

## What NOT To Cache
- Opinions or subjective answers
- Time-sensitive information (unless tagged with expiry context)
- Conversation-specific context ("what did I just say")
- Anything Anton asks you NOT to cache
- Speculative or uncertain answers
