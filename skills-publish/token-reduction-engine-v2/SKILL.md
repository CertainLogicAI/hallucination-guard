# Token Reduction Engine v1.2.0

Persistent answer cache for AI agents. Second identical query returns in ~100ms instead of 1–4 seconds. No API tokens spent on cached queries.

---

## What This Does

1. **Answers a question once, reuses it forever** (well, until expiry)
2. **Automatically detects and rejects uncertain answers** — "maybe", "I think", "not sure"
3. **Saves cache to disk** — survives server restarts
4. **Fast metrics** — see hit rate, flagged count, cache size

---

## Benefits

| Benefit | What It Means |
|---------|--------------|
| **Speed** | Repeated queries return in ~100ms (vs 1–4s LLM round-trip) |
| **Cost** | Zero API spend for cache-hit queries |
| **Consistency** | Same question → same answer, every time |
| **Quality gate** | Uncertain answers are shown but NOT cached — prevents garbage accumulation |
| **Persistence** | Survives process restart; no warm-up needed |
| **Self-contained** | No external API dependencies, no Brain API required |

---

## Limitations (Read This)

### What It Does NOT Do

| Myth | Reality |
|------|---------|
| "Eliminates hallucinations" | ❌ No — only catches hedging language ("maybe", "I think"). Confident falsehoods pass through. |
| "Verifies facts" | ❌ No — it is a cache, not a fact-checker. "Canada's capital is Toronto" (confidently) would be cached. |
| "Validates answers with the Brain API" | ❌ No — this is standalone. No external API calls. The Guard is a local linguistic check only. |
| "Works for all LLM responses" | ⚠️ Only catches specific uncertainty patterns. Novel hedging not in pattern list slips through. |
| "Permanent knowledge base" | ⚠️ 1-hour TTL by default. Old entries expire automatically. Use Facts DB for permanent storage. |
| "Thread-safe" | ⚠️ Not tested with concurrent writes. Single-process use recommended. |

### Architecture Notes

- **Cache stores hashed queries, not the original** — uses SHA-256 for lookup
- **LRU eviction at 1000 entries** — oldest entries deleted silently
- **Disk writes are best-effort** — disk full = silently drops persistence
- **No encryption at rest** — cache file is plain JSON

---

## Requirements

- Python 3.10+
- Zero external dependencies (stdlib only)

---

## Install

```bash
# ClawHub (when published)
clawhub install token-reduction-engine

# Manual
wget https://raw.githubusercontent.com/CertainLogicAI/token-reduction-engine/main/scripts/tre_client.py
chmod +x tre_client.py
```

---

## Usage

### As a Python module

```python
from tre_client import cache_answer, get_cached_answer, get_metrics

# 1. Cache a clean answer
result = cache_answer("What is Python?", "Python is a programming language.")
print(result["cached"])     # True

# 2. Same query again — instant return
cached = get_cached_answer("What is Python?")
print(cached[0])            # "Python is a programming language."

# 3. Uncertain answer — NOT cached
result = cache_answer("What is 2+2?", "I think maybe 4?")
print(result["cached"])     # False
print(result["flagged"])    # True
print(result["warning"])    # Response contains hedging language!

# 4. Check metrics
print(get_metrics())
```

### CLI

```bash
tre_client cache "What is Python?" "Python is a programming language."
tre_client get "What is Python?"
tre_client metrics
tre_client clear
```

---

## How It Works

```
User asks a question
    ↓
Hash the query (SHA-256)
    ↓
Check cache → HIT?
    ├─ YES → return cached answer (~100ms)
    └─ NO → generate answer via LLM/facts/whatever
              ↓
        Run Hallucination Guard on answer
              ↓
        Contains uncertainty?
            ├─ YES → show answer, DON'T cache
            └─ NO → cache answer, persist to disk
```

---

## Configuration

Edit constants at top of `tre_client.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `CACHE_SIZE_LIMIT` | 1000 | Max entries before LRU eviction |
| `CACHE_TTL_SECONDS` | 3600 | 1 hour — entries expire after this |
| `TOKEN_ESTIMATE_RATIO` | 0.75 | Words-to-tokens estimate (rough) |

---

## What We're Honest About

This tool is a **performance optimization with a basic quality gate**. It makes repeated queries fast and consistent. It does NOT make answers correct — that's a separate, harder problem (see our Brain API and Facts DB for that).

If you need:
- **Verified correct answers** → CertainLogic Brain API (separate product)
- **Tamper-evident audit trails** → AgentPathfinder (separate product)
- **Just speed + consistency** → this tool

---

## License

MIT-0 (no attribution required)
