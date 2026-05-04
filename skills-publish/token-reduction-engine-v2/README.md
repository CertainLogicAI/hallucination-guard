# Token Reduction Engine v1.2.0

> ⚠️ **DRAFT — Pending personal review and explicit approval by Anton before publication.** Per CertainLogic Claim Verification Policy v1.0 (April 29, 2026).

> Persistent answer cache for AI agents. Fast answers, cheap queries, honest limitations.

## Benefits

| 🏆 What you get | How it helps |
|-----------------|-------------|
| **Speed** | Repeated queries return in ~100ms (vs 1–4s LLM round-trip) |
| **Cost** | Zero API spend for cache-hit queries — save tokens, save money |
| **Consistency** | Same question → same answer, every time — no "lucky roll" variance |
| **Quality gate** | Uncertain answers ("maybe", "I think") are shown but NOT cached — prevents garbage accumulation |
| **Persistence** | Survives server restarts — no warm-up, no cold cache |
| **Self-contained** | Zero external dependencies — works offline, no API keys |

## What This Does NOT

| ❌ Myth | ✅ Reality |
|---------|-----------|
| "Eliminates hallucinations" | Only catches hedging language. Confident falsehoods pass through. |
| "Verifies facts" | It is a cache, not a fact-checker. "Toronto is Canada's capital" (confidently) would be cached. |
| "Validates answers with Brain API" | Standalone — no external validation. The Guard is local only. |
| "Works for all LLM responses" | Only catches specific uncertainty patterns. Novel hedging slips through. |
| "Permanent knowledge base" | 1-hour expiry. Old entries auto-delete. |
| "Thread-safe" | Untested with concurrent writes. Single-process use recommended. |

## Quick Start

```bash
# Install via ClawHub (when published)
clawhub install token-reduction-engine

# Or drop in the single file
curl -L https://github.com/CertainLogicAI/token-reduction-engine/raw/main/scripts/tre_client.py \
  -o tre_client.py && chmod +x tre_client.py

# Cache an answer
./tre_client.py cache "What is Python?" "Python is a programming language."

# Same question again — instant return
./tre_client.py get "What is Python?"
# → {"cached": true, "answer": "Python is a programming language.", "tokens": 6}

# Check metrics
./tre_client.py metrics
# → {"cache_hits": 1, "cache_misses": 0, "cache_hit_rate_percent": 100.0, ...}
```

## What This Is (And Isn't)

### ✅ It IS
- A **performance cache** — makes repeated queries fast
- A **cost reducer** — no API spend on cache hits
- A **basic quality guard** — rejects hedging/uncertain language from cache
- A **persistent store** — survives process restarts

### ❌ It is NOT
- A **fact checker** — "Canada's capital is Toronto" (confidently) would be cached as-is
- A **hallucination eliminator** — only catches specific hedging patterns
- A **verified answer database** — cached answers have NOT been fact-checked
- A **Brain API** — no external validation, no curated facts

### ⚠️ Honest Limitations

| Limitation | Detail |
|------------|--------|
| **Linguistic gate only** | Catches "maybe", "I think", "not sure". Confident falsehoods pass through. |
| **Pattern-based** | Novel hedging not in our pattern list (e.g., "I'm 60% certain") slips through. |
| **1-hour expiry** | Old entries auto-delete. Not a permanent knowledge base. |
| **Not thread-safe** | Untested with concurrent writes. Single-process use recommended. |
| **Plain JSON on disk** | Cache file is unencrypted JSON. Sensitive data not recommended. |
| **Best-effort persistence** | Disk full = silently drops writes. Check `get_metrics()` for persisted status. |

## Architecture

```
User asks a question
    ↓
Hash query (SHA-256)
    ↓
Cache HIT?
    ├─ YES → return instantly (~100ms)
    └─ NO → generate answer (LLM / facts / whatever)
              ↓
        Hallucination Guard checks for uncertainty
              ↓
        Uncertainty detected?
            ├─ YES → show answer, DON'T cache, warn user
            └─ NO → cache answer, save to disk, return
```

Guard patterns: `maybe`, `I think`, `not sure`, `could be`, `might be`, `probably`, `I guess`, etc.

## Python API

```python
from tre_client import cache_answer, get_cached_answer, get_metrics, clear_cache

# Store (if Guard passes)
result = cache_answer("prompt", "response")
# → {"cached": True, "flagged": False, "reason": "Guard passed"}

# Retrieve
cached = get_cached_answer("prompt")
# → ("response", token_count) or None

# Metrics
print(get_metrics())
# → {"cache_hits": 5, "cache_misses": 3, "cache_hit_rate_percent": 62.5, ...}
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `tre_client cache <query> <answer>` | Store answer in cache (Guard-checked) |
| `tre_client get <query>` | Retrieve cached answer |
| `tre_client metrics` | Show hit rate, cache size, flagged count |
| `tre_client clear` | Wipe cache (RAM + disk) |

## Configuration

Edit constants at top of `tre_client.py`:

```python
CACHE_SIZE_LIMIT    = 1000    # Max entries before LRU eviction
CACHE_TTL_SECONDS   = 3600    # 1 hour — auto-expiry
TOKEN_ESTIMATE_RATIO = 0.75   # Words-to-tokens multiplier
```

## Related Products

| Product | What It Does | Use When |
|---------|-------------|----------|
| **TRE (this tool)** | Cache + basic guard | You need speed and consistency |
| **CertainLogic Brain API** | Fact-checking against curated DB | You need verified correct answers |
| **AgentPathfinder** | Signed task audit trails | You need to prove what agents did |
| **Hallucination Guard** | Deeper validation (numeric, factual) | You need stronger quality gates |

## License

MIT-0 — use freely, no attribution required.

---

*CertainLogic builds honest AI infrastructure. We tell you exactly what our tools do, what they don't do, and where the sharp edges are. No overselling.*
