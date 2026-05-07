# CertainLogic Brain OS — Operator's Guide

**Version:** 1.0  
**Date:** 2026-05-07  
**Status:** Production  
**Scope:** Human operator reference for running, querying, and maintaining the Brain OS

---

## Table of Contents

1. [What Is the Brain OS?](#what-is-the-brain-os)
2. [Architecture at a Glance](#architecture-at-a-glance)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [Using the Brain](#using-the-brain)
6. [Intent Routing](#intent-routing)
7. [Source Boosts](#source-boosts)
8. [Skill Integration](#skill-integration)
9. [Production Status](#production-status)
10. [Emergency Procedures](#emergency-procedures)
11. [Troubleshooting](#troubleshooting)
12. [Roadmap](#roadmap)

---

## What Is the Brain OS?

The CertainLogic Brain OS is a **deterministic knowledge layer** that sits between agent skills and large language models. It stores business facts, strategic principles, product knowledge, and operational context in a structured, searchable, auditable format.

**Why it exists:**
- **Reduce hallucination:** Known facts come from the brain, not synthesized by an LLM
- **Reduce latency:** Local PGLite database queries in <100ms, no API calls
- **Reduce cost:** Zero LLM tokens for questions the brain can answer
- **Increase auditability:** Every query is logged; every answer is sourced

**What it is NOT:**
- Not a general-purpose LLM (it doesn't generate creative text)
- Not a chatbot (it returns structured facts, not conversational responses)
- Not a database (it doesn't support arbitrary SQL)

**The core promise:** If the brain knows the answer, you'll get a fast, cited, deterministic result. If it doesn't, the skill falls back to its normal behavior.

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────┐
│                     Agent Skills                         │
│  (content-engine, x-api, pathfinder, market-research)   │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────▼──────────────┐
         │   brain_wrapper.Brain()    │
         │   (Python drop-in class)   │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │  certainlogic_router.py    │
         │  (intent classification)   │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │     gbrain CLI             │
         │  bun run src/cli.ts        │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │     PGLite Database        │
         │  (~/.gbrain/default.db)    │
         │  443 facts, 149 pages      │
         └────────────────────────────┘
```

**Key files and their roles:**

| File | Role | Language |
|---|---|---|
| `company-brain/brain_wrapper.py` | Primary interface: `Brain()` class | Python |
| `company-brain/certainlogic_router.py` | Intent classification, query routing | Python |
| `company-brain/deterministic_brain.py` | Low-level gbrain wrapper with audit trails | Python |
| `company-brain/src/core/search/intent.ts` | Intent regex patterns (80 patterns, 4 categories) | TypeScript |
| `company-brain/src/core/search/certainlogic-boosts.ts` | Source-type boost map | TypeScript |
| `company-brain/src/core/search/certainlogic-intent.ts` | CL-specific intent patterns | TypeScript |
| `company-brain/src/core/search/certainlogic-router.ts` | TypeScript router (internal use) | TypeScript |
| `company-brain/src/cli.ts` | GBrain CLI entry point | TypeScript |

---

## Quick Start

### 1. Check Brain Health

```bash
# HTTP API health check
curl -s http://127.0.0.1:8000/health
# Expected: {"status":"ok","facts_db":"443 facts loaded"}

# CLI health check
cd /data/.openclaw/workspace/company-brain && bun run src/cli.ts stats
# Expected: Pages: 149
```

### 2. Query the Brain

**Via CLI:**
```bash
cd /data/.openclaw/workspace/company-brain
bun run src/cli.ts query "what is our moat strategy" --limit 3
```

**Via Python:**
```python
import sys
sys.path.insert(0, '/data/.openclaw/workspace/company-brain')
from brain_wrapper import Brain

brain = Brain()
result = brain.query("what is our moat strategy")

print(result["answer"])       # Top result excerpt
print(result["sources"])      # List of {slug, title, score}
print(result["confidence"])   # Relevance score (0-1)
print(result["intent"])       # Detected intent: strategy/product/data/operations
```

**Via HTTP API:**
```bash
curl -s http://127.0.0.1:8000/query?q=moat&limit=3
```

### 3. List All Pages

```bash
cd /data/.openclaw/workspace/company-brain
bun run src/cli.ts list | head -20
```

### 4. Get a Specific Page

```bash
cd /data/.openclaw/workspace/company-brain
bun run src/cli.ts get concepts/certainlogic-moat-thesis
```

### 5. Semantic Search

```bash
cd /data/.openclaw/workspace/company-brain
bun run src/cli.ts search "data flywheel" --limit 5
```

---

## Core Concepts

### Facts vs. Pages

- **Facts** are atomic knowledge units (loaded into the Facts DB via HTTP API)
- **Pages** are structured markdown documents in the GBrain database
- Facts are used by the HTTP API; pages are used by the CLI and Python wrapper
- In practice, most queries hit pages. Facts are for the token reduction engine.

### Slugs

Every page has a unique slug (path-like identifier):
- `concepts/certainlogic-moat-thesis` — Strategic concepts
- `projects/faulttrace` — Product pages
- `family/work/strategy/x_posting_gap` — Operational strategy
- `family/work/metrics/backup_confirmation_2026-05-07` — Metrics and evidence

Slugs are hierarchical. The first segment determines the source type and boost level.

### Confidence Scores

Search results include a relevance score (0.0 to 1.0+):
- **>0.3** — Strong match, likely useful
- **0.1–0.3** — Moderate match, contextually relevant
- **<0.1** — Weak match, probably not useful

The default confidence threshold for skills is **0.2**. Below this, skills fall back to LLM.

---

## Using the Brain

### Query Types

The brain supports three query modes:

| Mode | Command | Use Case |
|---|---|---|
| **Exact query** | `bun run src/cli.ts query "text"` | Natural language question |
| **Semantic search** | `bun run src/cli.ts search "text"` | Find related content |
| **Page get** | `bun run src/cli.ts get <slug>` | Retrieve specific page |

**Query** uses hybrid search (full-text + semantic + source boosts). **Search** is pure semantic similarity. **Get** is direct slug lookup.

### Detail Levels

Queries automatically select a detail level based on intent classification:

| Detail | Behavior | When Used |
|---|---|---|
| `low` | Compiled truth only (no timeline) | Entity queries ("who is X?") |
| `medium` | Compiled truth + context | Operations, general queries |
| `high` | Everything (timeline, context, depth) | Strategy, product, data queries |

You can override: `bun run src/cli.ts query "moat" --detail high`

### Python Wrapper

The canonical way for skills to use the brain:

```python
from brain_wrapper import Brain

brain = Brain()

# Auto-detects intent, returns structured result
result = brain.query("what is our moat strategy")

# Shorthand for known categories
result = brain.strategy("data flywheel")      # Forces strategy intent
result = brain.product("L5X parsing")          # Forces product intent
result = brain.metrics("cache hit rate")       # Forces data intent
result = brain.ops("roadmap")                  # Forces operations intent

# Response shape
{
    "query": "what is our moat strategy",
    "intent": "strategy",
    "answer": "Our moat is a data flywheel...",
    "sources": [
        {"slug": "concepts/certainlogic-moat-thesis", "title": "CertainLogic Moat Thesis", "score": 0.34}
    ],
    "confidence": 0.34,
    "brain_query": {...}  # Raw gbrain result
}
```

**Key rule:** The brain wrapper always returns a result. If the brain is unavailable, empty, or below confidence threshold, the result will have `confidence: 0` and empty `sources`. Skills must check `confidence > 0.2` before using brain results.

### Writing to the Brain

**⚠️ Requires write access. Currently restricted to `deterministic_brain.py` and admin scripts.**

```python
from deterministic_brain import DeterministicBrain

brain = DeterministicBrain(domain="default")
result = brain.command("brain.put_page", {
    "slug": "family/work/strategy/new_decision",
    "content": "# New Strategic Decision\n\nWe decided to...",
    "source": "default"
})
```

Every write is:
- HMAC-signed for audit trail
- SHA-256 hashed for integrity verification
- Logged to `audit.jsonl`

---

## Intent Routing

### How It Works

When you query the brain, your text is classified into one of five intents:

| Intent | Detects | Example Queries | Boost Prefix | Detail |
|---|---|---|---|---|
| **strategy** | moat, strategy, competitive advantage, data flywheel, trade secret, patent, month 6 | "what is our moat", "how do we compete" | `concepts/certainlogic-` | high |
| **product** | FaultTrace, Brain API, deterministic AI, L5X, PLC | "how does faulttrace work" | `projects/` | high |
| **data** | benchmark, metrics, accuracy, cache hit, alignment score | "what is our benchmark accuracy" | `family/work/metrics/` | high |
| **operations** | funding, pricing, YC, hackathon, team, roadmap | "when is our next hackathon" | `family/work/` | medium |
| **general** | Everything else | "hello", "what time is it" | `family/work/` | medium |

### Intent Patterns

The classifier uses 80 regular expressions across 4 categories. Key patterns:

```
Strategy:  \bmoat\b, \bstrategy\b, \bdata flywheel\b, \btrade secret\b, \bmonth[- ]?6\b
Product:   \bfaulttrace\b, \bbrain\s+api\b, \bL5X\b, \bplc\b, \bschematic\b
Data:      \bbenchmark\b, \bmetrics?\b, \bcache\s+hit\b, \bhallucination\b
Operations: \bfunding\b, \bpricing\b, \bYC\b, \bhackathon\b, \broadmap\b
```

**Important:** Intent classification is **heuristic**, not AI-based. It's fast (<1ms) but can misclassify ambiguous queries. If a query has multiple intents, the first matching pattern wins.

### Fallback Chain

If no intent matches, the query defaults to `general` with medium detail and the `family/work/` boost prefix.

---

## Source Boosts

### How Results Are Ranked

Every search result gets multiplied by a source-type boost factor. This encodes the Moat Thesis: curated strategy content ranks highest, product pages rank highly, personal noise ranks lowest.

| Slug Prefix | Boost | Rationale |
|---|---|---|
| `concepts/certainlogic-` | 1.8× | Moat thesis — curated, opinionated, highest value |
| `concepts/deterministic-ai` | 1.7× | Core technology strategy |
| `projects/faulttrace` | 1.6× | Product pages — data flywheel |
| `projects/brain-api` | 1.6× | Product pages — data flywheel |
| `family/work/strategy/` | 1.5× | High-signal operational context |
| `family/work/evidence/` | 1.4× | Evidence and proof points |
| `family/work/metrics/` | 1.3× | Quantified data |
| `family/work/reports/` | 1.3× | Structured reports |
| `family/comms/` | 1.1× | Communications content |
| `yc/`, `civic/` | 1.0× | Neutral — not our moat but relevant |
| `family/personal/` | 0.6× | Demoted — personal noise |
| `family/home/` | 0.6× | Demoted — personal noise |

**Effect:** A page about FaultTrace (`projects/faulttrace`) with a raw score of 0.20 will outrank a personal blog post (`family/personal/`) with a raw score of 0.30.

### Boost Bypass

Detail level `high` bypasses source boosts entirely (for temporal/event queries where chronology matters more than source type).

---

## Skill Integration

### Migration Pattern

Skills should default to brain-first queries:

```python
from brain_wrapper import Brain

def handle_request(inputs):
    brain = Brain()
    brain_result = brain.query(inputs["user_query"])
    
    if brain_result["confidence"] > 0.2:
        return {
            "answer": brain_result["answer"],
            "sources": brain_result["sources"],
            "brain_first": True,
        }
    
    return fallback_to_llm(inputs)
```

**Migration priorities (complete by Week 5):**

| Skill | Brain Usage | Complexity | Status |
|---|---|---|---|
| content-engine | `brain.strategy()` brand voice | Medium | Planned Week 2 |
| x-api (v1 slots) | `brain.strategy()` messaging | Low | Planned Week 3 |
| x-api (v2 trending) | `brain.product()` positioning | Low | Planned Week 3 |
| market-research-pro | `brain.search()` + `brain.metrics()` | Medium | Planned Week 3 |
| certainlogic-pathfinder | `brain.query()` audit trails | Medium | Planned Week 4 |
| seo-audit-pro | `brain.search()` SEO knowledge | Low | Planned Week 4 |
| cold-outreach-pro | `brain.strategy()` positioning | Low | Planned Week 4 |
| skill-vetter-plus | `brain.strategy()` security rules | Low | Planned Week 4 |
| skill-oracle | `brain.search()` skill docs | Low | Planned Week 4 |
| skill-guard | `brain.search()` bad patterns | Low | Planned Week 4 |

### Graceful Degradation

Every skill must work without the brain. If `Brain()` fails to import, if the brain database is missing, or if all queries return empty results, the skill must fall back to its pre-brain behavior.

**Migration requirement:** Add an `import_guard`:

```python
try:
    from brain_wrapper import Brain
    brain_available = True
except ImportError:
    brain_available = False

def handle_request(inputs):
    if brain_available:
        brain = Brain()
        result = brain.query(inputs["user_query"])
        if result["confidence"] > 0.2:
            return {"answer": result["answer"], "brain_first": True}
    
    return legacy_handler(inputs)
```

---

## Production Status

### What's Live Now

| Component | Status | Details |
|---|---|---|
| Brain API (HTTP) | ✅ UP | localhost:8000, 443 facts |
| GBrain CLI | ✅ Working | `bun run src/cli.ts` |
| Source boosts | ✅ Active | 12 prefix rules in `resolveBoostMap()` |
| Intent classifier | ✅ Active | 80 regexes, auto-detected |
| Python wrapper | ✅ Importable | `brain_wrapper.Brain()` |
| Audit trail | ✅ Logging | `audit.jsonl` append-only |
| Review gate (X posting) | ✅ Active | `post_review.py` blocks unapproved slots |
| Emergency kill switch | ✅ Ready | `scripts/x-kill.sh` |
| Chat command spec | ✅ Defined | Not yet wired to live handler |
| Emergency override | ✅ Defined | Recognized in conversation, not system-enforced |

### Health Monitoring

Check brain health in two ways:

```bash
# 1. HTTP health endpoint
curl -s http://127.0.0.1:8000/health
# Expected: {"status":"ok","facts_db":"443 facts loaded"}

# 2. CLI stats
cd /data/.openclaw/workspace/company-brain && bun run src/cli.ts stats
# Expected: Pages: 149

# 3. Git status (should always be clean)
cd /data/.openclaw/workspace && git status --short
# Expected: (no output)
```

**Alert if:**
- `status` ≠ `ok`
- `facts_db` drops by >5 from last check
- Git has uncommitted files

### Known Limitations

1. **GBrain `bun build` is broken** — TypeScript files can't be bundled (Node.js builtin errors). Use `bun run` instead.
2. **Coding query tracker is broken** — 4 days zero queries, cron timeouts. Not blocking Brain OS operation.
3. **Blog publish URLs are broken** — Shows `"PUBLISHED"` placeholder instead of real URLs.
4. **Telegram is not paired** — Bot exists but no chat ID. Dashboard-only notifications.
5. **Math Prompts architecture is not implemented** — Still a concept (2026-05-04).

---

## Emergency Procedures

### Kill Switch (Stop All X Posting)

```bash
# Emergency stop — one command
./scripts/x-kill.sh "reason for stop"

# What it does:
# - Removes all X-posting crons
# - Clears scheduled content files
# - Locks review gate
# - Logs to memory/ and logs/
# - Requires Anton approval to re-enable
```

### Brain API Down

```bash
# Check if process is running
pgrep -f "brain" || echo "Brain API is down"

# Restart
bash /data/.openclaw/workspace/start-brain.sh

# Verify
curl -s http://127.0.0.1:8000/health
```

### Emergency Override (Override My Refusal)

If I refuse to do something and delay is dangerous:

1. **Explicit declaration:** `This is an emergency. Override refusal [X]. Reason: [one sentence]`
2. **Command prefix:** `!EMERGENCY <command>`
3. **Crisis description:** Describe the active crisis ("site is down," "data disappearing")

I will acknowledge, log, execute — but **never** override these 8 red lines:
1. No exfiltration of private data
2. No deletion of backups
3. No credential rotation without replacement keys
4. No permanent destruction of the only copy
5. No group chat messages without recipient consent
6. No committing secrets to git
7. No disabling audit/logging
8. No executing untrusted code

### Full System Lockdown

If everything is compromised:

```bash
# 1. Kill all crons
cd /data/.openclaw/workspace && openclaw cron list | awk '{print $1}' | xargs -I{} openclaw cron remove {}

# 2. Stop brain API
pkill -f "brain"

# 3. Lock review gate
echo '{"emergency_lock": true}' > /data/.openclaw/workspace/marketing/content_output/approved_slots.json

# 4. Verify
curl -s http://127.0.0.1:8000/health || echo "System locked down"
```

---

## Troubleshooting

### Problem: Brain query returns empty results

**Check:**
1. Is the brain API up? `curl http://127.0.0.1:8000/health`
2. Is the query in the right format? Try simpler keywords.
3. Is the page actually in the brain? `bun run src/cli.ts list | grep <keyword>`
4. Is the intent misclassified? Try a more specific query ("moat" vs "strategy").

**Solution:** If confidence < 0.2, skills should fall back to LLM. This is expected behavior for unknown queries.

### Problem: GBrain CLI fails with "gbrain not found"

**Cause:** Missing dependencies or wrong working directory.

```bash
cd /data/.openclaw/workspace/company-brain
bun install  # If node_modules missing
bun run src/cli.ts query "test"
```

### Problem: Intent classification is wrong

**Example:** "Our pricing model" gets classified as `strategy` instead of `operations`.

**Check:** `grep -n "pricing" src/core/search/certainlogic-intent.ts`

**Fix:** Add or adjust regex patterns. Currently `pricing` is in `OPERATIONS_PATTERNS`. If it's matching `strategy` first, reorder the patterns or make the regex more specific.

**File:** `company-brain/src/core/search/certainlogic-intent.ts`

### Problem: Source boost not applying

**Check:** `grep -n "your-prefix" src/core/search/source-boost.ts`

**Verify:** The boost map is merged in `resolveBoostMap()`. Check that your prefix is in `CERTAINLOGIC_SOURCE_BOOSTS`.

**Test:** Run a query and check if results from the boosted prefix rank higher than unboosted results with similar raw scores.

### Problem: Python wrapper import fails

```bash
# Test import
python3 -c "import sys; sys.path.insert(0, '/data/.openclaw/workspace/company-brain'); from brain_wrapper import Brain; print('OK')"

# If fails, check:
# 1. File exists: ls /data/.openclaw/workspace/company-brain/brain_wrapper.py
# 2. Python path includes company-brain
# 3. No syntax errors in wrapper
```

### Problem: Performance degradation (>100ms per query)

**Check:**
```bash
# Time a query
time bun run src/cli.ts query "moat" --limit 5

# Check brain size
ls -lh ~/.gbrain/default.db

# Check for concurrent queries (process exhaustion)
ps aux | grep "gbrain" | wc -l
```

**Solutions:**
- If database is large (>10MB): Cache layer not yet deployed (Phase 4F)
- If many concurrent gbrain processes: Limit concurrent queries in skill code
- If intermittent: Check for file locks via `lsof ~/.gbrain/default.db`

---

## Roadmap

### Phase 4: Production Hardening (In Progress)

| Week | Milestone | Status |
|---|---|---|
| W1 | Production Layer Hardening + Security | Planned |
| W2 | Observability + Pilot Migration | Planned |
| W3 | Bulk Migration (Skills 2–6) | Planned |
| W4 | Cache Layer + Bulk (Skills 7–10) + Testing | Planned |
| W5 | Deployment + Fallback | Planned |

### Phase 5: Math Prompts & Scale (Concept)

- Mathematical prompt decomposition (2% hallucination target)
- Wikipedia-scale validation (100K+ facts)
- Brain-Mirror read-only instance (at 10K facts)
- Compliance audit package (enterprise offering)

### Phase 6: Ecosystem (Vision)

- Third-party API access
- Multi-brain support
- Real-time sync
- Deterministic AI Brain patent/trade secret strategy

---

## Quick Reference Card

```
# Health check
curl -s http://127.0.0.1:8000/health

# Query brain
bun run src/cli.ts query "question" --limit 3

# Search
bun run src/cli.ts search "topic" --limit 5

# Get page
bun run src/cli.ts get concepts/certainlogic-moat-thesis

# List all
bun run src/cli.ts list

# Python wrapper
python3 -c "from brain_wrapper import Brain; b=Brain(); print(b.query('moat'))"

# Kill switch
./scripts/x-kill.sh "reason"

# Emergency override
!EMERGENCY <command>
```

---

## For Other Users

If you're reading this as a potential operator of a Brain OS instance:

1. **This is a fork of Garry Tan's gbrain.** The CertainLogic modifications are in `src/core/search/certainlogic-*.ts` and the Python wrapper layer.
2. **It's deterministic by design.** No randomness in search ranking (same query = same results).
3. **It's auditable.** Every query, every write, every override is logged.
4. **It's local.** Zero API dependencies for queries (PGLite SQLite database).
5. **It's opinionated.** Source boosts encode business priorities, not neutral information retrieval.

To replicate: Fork gbrain, add your own `certainlogic-boosts.ts` and `certainlogic-intent.ts`, deploy `brain_wrapper.py`. The architecture is generalizable to any company that has structured knowledge to protect.

---

**Document owner:** Alex  
**Review cycle:** After each Phase 4 milestone  
**Questions:** Ping Anton or Alex
