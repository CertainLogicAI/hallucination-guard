# Project Scope: Personal Knowledge Base (Deterministic Cache Skill)

## Overview
Deploy the deterministic AI brain as a local service and wire it into OpenClaw as a skill. Every query runs through the full pipeline: input summarization → cache check → Opus (if needed) → validate → cache. Saves tokens on every single interaction — cache hits cost nothing, cache misses cost less via compression.

## Key Requirements
- **Runs on ALL queries** — not selective, every query hits the pipeline
- **Input summarization** — compress queries before they reach Opus (saves tokens on every cache miss)
- **Cache management** — ability to remove, correct, search, and purge entries
- **Graceful fallback** — if service is down, normal Opus flow continues

## Problem
- Every query costs Opus tokens, even repeat questions
- Project knowledge is scattered across memory files — expensive to re-read
- No persistent, searchable knowledge base outside of conversation history

## Solution
Local FastAPI service + OpenClaw skill that checks cache on every query, serves from cache when possible, and learns from every new answer.

## Deliverables

### Phase 1: Service & Skill (Day 1)
| # | Task | Effort | Priority |
|---|------|--------|----------|
| 1 | Start deterministic brain as background service (systemd or Docker) | 30 min | P0 |
| 2 | Write OpenClaw skill (`deterministic-cache/SKILL.md`) | 1 hr | P0 |
| 3 | Skill logic: check cache on ALL queries → return hit or proceed normally | 30 min | P0 |
| 4 | Seed cache with project facts (products, pricing, decisions, specs) | 1 hr | P0 |
| 5 | Test end-to-end: ask cached question, verify no Opus reasoning | 30 min | P0 |

**Phase 1 total: ~3.5 hours**

### Phase 2: Learning Loop + Management (Day 2)
| # | Task | Effort | Priority |
|---|------|--------|----------|
| 6 | Auto-store: after answering any query, POST result to cache | 1 hr | P1 |
| 7 | Confidence threshold: only cache answers validated by hallucination detector | 30 min | P1 |
| 8 | Bulk import: script to ingest memory/*.md files into facts cache | 1 hr | P1 |
| 9 | Cache management API endpoints: | 1.5 hr | P1 |
|   | - `DELETE /facts/{key}` — remove entry | | |
|   | - `PUT /facts/{key}` — correct entry | | |
|   | - `GET /facts/search?q=` — find by keyword | | |
|   | - `POST /cache/purge` — wipe all | | |
| 10 | Telegram cache commands: "cache delete/list/search/purge" | 1 hr | P1 |

**Phase 2 total: ~5 hours**

### Phase 3: Optimization (Week 1)
| # | Task | Effort | Priority |
|---|------|--------|----------|
| 11 | Fuzzy matching: similar queries hit same cache entry (not just exact match) | 2 hr | P2 |
| 12 | Category tagging: tag entries by domain (FaultTrace, pricing, technical) | 1 hr | P2 |
| 13 | Cache persistence: dump to disk on shutdown, reload on start | 1 hr | P2 |
| 14 | Metrics tracking: tokens saved per day/week, cache growth rate | 1 hr | P2 |
| 15 | Cache status dashboard endpoint (hit rate, size, last queries) | 30 min | P2 |

**Phase 3 total: ~5.5 hours**

## Architecture

```
User Query → OpenClaw (Alex)
                ↓
        Skill: send to pipeline (ALL queries)
                ↓
    curl localhost:8000/query
                ↓
    1. Token reduction (compress input)
                ↓
    2. Cache lookup (compressed query)
                ↓
        Cache hit?           
        ↓ yes              ↓ no
    Return cached      3. Compressed query → Opus
    answer               (fewer input tokens)
    (zero tokens)              ↓
                      4. Validate response
                            ↓
                      5. Cache validated answer
                         (free next time)
```

**Savings on every query type:**
- Cache hit → zero Opus tokens
- Cache miss → reduced input tokens via summarization
- Repeat query → zero tokens forever after first ask

## Cache Management

### API Endpoints
- `POST /query` — query the cache (existing)
- `POST /facts` — add/update entry (existing)
- `GET /facts` — list all entries (existing)
- `GET /facts/search?q=keyword` — search entries (new)
- `DELETE /facts/{key}` — remove specific entry (new)
- `PUT /facts/{key}` — correct specific entry (new)
- `POST /cache/purge` — wipe everything (new)
- `GET /audit` — audit trail (existing)

### Telegram Commands
- "cache list [keyword]" — search/list entries
- "cache delete [key]" — remove bad entry
- "cache correct [key] [new value]" — fix an entry
- "cache purge" — wipe all (with confirmation)
- "cache status" — hit rate, size, health

## Tech Stack
- **Service:** FastAPI (Python) — already built, tested, working
- **Cache:** In-memory LRU with JSON persistence — already built
- **Hallucination filter:** Already built and tested
- **Skill:** SKILL.md + curl wrapper
- **Hosting:** Same VPS, port 8000, localhost only

## Success Metrics
- Cache hit rate >30% after 2 weeks
- Measurable input token reduction on cache misses (target: 20-40% compression)
- Measurable total token savings (cache hits + compression combined)
- Zero hallucination slip-through on cached answers
- Sub-100ms response time on cache hits
- Anton can manage cache from Telegram without touching CLI

## Risks
| Risk | Mitigation |
|------|------------|
| Stale cache answers | TTL expiry + manual management + Telegram commands |
| Wrong answers cached | Hallucination detector validates before caching |
| Service goes down | Skill falls back to normal Opus — no degradation |
| Cache grows too large | LRU eviction at 1000 entries, expandable |
| Bad info persists | Search + delete via API and Telegram |

## Cost
- $0 infrastructure (runs on existing VPS)
- ~14 hours total across 3 phases
- Phase 1 is functional standalone

## Status: SCOPED — Ready to build on Anton's go
