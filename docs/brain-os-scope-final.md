# Scope & Spec: CertainLogic Brain OS — Final Synthesis

**Version:** Stage 3 (Opus 4.6 synthesis of Kimi K2.6 base + Qwen3 Coder critique)
**Date:** 2026-05-07
**Status:** FINAL — ready for Anton review

---

## Stage 3 Synthesis Notes

This document merges two perspectives:
- **Kimi K2.6 (Stage 1):** Comprehensive, optimistic, builds everything
- **Qwen3 Coder (Stage 2):** Skeptical, production-focused, cuts bloat

**Opus synthesis principles applied:**
- **Order corrected:** Production hardening FIRST, then migration
- **Scope reduced:** Cache deferred (443 facts = fast enough), metrics cut from 8 to 4
- **Security deepened:** Added supply chain, data poisoning, log leakage, ReDoS, process exhaustion
- **Architecture simplified:** Python wrapper calls CLI directly with intent-aware flags; TypeScript stays internal
- **Timeline extended:** 3 weeks → 5 weeks (allows for Anton review at each gate)
- **Math Prompts separated:** Phase 5, not in this scope
- **Acceptance criteria hardened:** Exact numbers, exact inputs, exact outputs

---

## Executive Summary

The CertainLogic Brain OS is a deterministic middleware layer providing agent skills with structured, auditable, local-first knowledge retrieval. Phase 1–3 (grounding, alignment, routing) are complete. This spec covers Phase 4: taking the brain from "working proof-of-concept" to "production-hardened infrastructure."

**Core thesis:** Agent queries should hit a local deterministic brain before ever calling an LLM. The brain is a fast optimization (<100ms, zero API cost), not a hard dependency. When it doesn't know, agents fall back to what they would have done before the brain existed.

**Total timeline:** 5 weeks (2026-05-07 → 2026-06-11)

---

## Architecture (Simplified)

```
Skill Code
    ↓
brain_wrapper.Brain()  ← Python, calls CLI with intent-aware flags
    ↓
gbrain_cli()           ← subprocess: bun run src/cli.ts query "..." --detail <X> --limit N
    ↓
GBrain CLI             ← TypeScript, runs on PGLite (local SQLite)
    ↓
Intent classifier      ← certainlogic-intent.ts (regex patterns, auto-detected)
Source boost map       ← certainlogic-boosts.ts (merged into resolveBoostMap)
Hybrid search          ← hybrid.ts (RRF ranking, detail-aware)
    ↓
Structured result      ← {answer, sources, confidence, intent}
```

**Key simplification (Qwen insight):** The Python wrapper doesn't need the TypeScript router layer. It detects intent locally (regex in Python), then calls gbrain CLI with the right `--detail` flag. The TypeScript router exists for future gbrain-native extensions, not for Python skills.

---

## In Scope

### Phase 4A: Production Layer Hardening (Week 1)

Harden `deterministic_brain.py` and `brain_wrapper.py` BEFORE any skill migration.

**4A.1: Timeout Enforcement**
- Every brain query has a hard timeout. Default: 2s for search, 5s for page get.
- Implementation: `concurrent.futures.ThreadPoolExecutor` in Python wrapper (cross-platform, doesn't use `signal`)
- File: `brain_wrapper.py` (modified)

**4A.2: Retry Logic**
- Exponential backoff for transient failures (gbrain CLI timeout, file lock)
- Max retries: 3. Base delay: 100ms. Backoff factor: 2.
- Only retries on TRANSIENT errors (timeout, file lock). Does NOT retry on PERMANENT errors (bad slug, no matches).
- File: `brain_wrapper.py` (modified)

**4A.3: Circuit Breaker**
- If brain query fails 5 times consecutively, stop querying for 10 minutes.
- Return {"brain_unavailable": true} to callers.
- Recovers automatically after timeout.
- File: `src/core/circuit_breaker.py`

**4A.4: Error Classification**
- Transient: `subprocess.TimeoutExpired`, `FileNotFoundError` (gbrain CLI missing), file lock (`sqlite3.DatabaseError` with "database is locked")
- Permanent: `ValueError` (bad slug format), empty result set, `KeyError` (expected field missing)
- File: `src/core/error_classifier.py`

**4A.5: Process Pool (Anti Fork-Bomb)**
- Every `bun run src/cli.ts` spawns a process. If a skill calls brain in a tight loop, we exhaust file descriptors.
- Fix: Use a process pool with max 4 concurrent gbrain CLI calls. Queue additional requests.
- File: `src/core/cli_pool.py`

**4A.6: Simplified Intent Detection**
- Python wrapper does keyword-based intent detection (not TypeScript regex).
- Maps intent to `--detail` flag:
  - strategy/product/data → `--detail high`
  - operations/general → `--detail medium`
- Fallback to `--detail medium` if no keyword match.
- File: `brain_wrapper.py` (modified)

**Deliverables (4A):**
- `brain_wrapper.py` — updated with timeout, retry, circuit breaker, process pool, intent detection
- `src/core/circuit_breaker.py`
- `src/core/error_classifier.py`
- `src/core/cli_pool.py`
- `test/test_production_layer.py` — unit tests for all 6 components

**Acceptance criteria (4A):**
| Test | Input | Expected Output | Pass/Fail |
|---|---|---|---|
| Timeout | Brain query with 5s sleep injected | Returns in <3s with timeout error | |
| Retry | Brain CLI fails with timeout on 1st/2nd call | Succeeds on 3rd call | |
| Circuit breaker | 5 consecutive failures | 6th call returns "brain unavailable" immediately | |
| Circuit recovery | Wait 10 min after breaker trip | 7th call retries normally | |
| Error classification | ValueError("bad slug") | Classified as PERMANENT, no retry | |
| Error classification | subprocess.TimeoutExpired | Classified as TRANSIENT, retry with backoff | |
| Process pool | 10 concurrent brain queries | Only 4 gbrain processes at any time, rest queued | |
| Intent detection | "what is our moat strategy" | Detects strategy, passes `--detail high` | |
| Intent detection | "random unrelated query" | No match, passes `--detail medium` | |

---

### Phase 4B: Security Hardening (Week 1)

**4B.1: Input Validation**
- Slug whitelist: `[a-zA-Z0-9_/-]+`. Reject `..`, `~`, absolute paths, null bytes.
- Query length limit: 2000 characters. Reject longer.
- Reject SQL-like patterns in queries (`; -- DROP`, `UNION SELECT`, etc.)
- File: `src/core/input_validator.py`

**4B.2: Write Access Control**
- Currently: ANY code can `brain.put_page` if it has CLI access.
- Fix: Separate read path (fast, no auth) from write path (requires explicit allowlist).
- Allowlist: `deterministic_brain.py` and specific admin scripts.
- File: `src/core/write_guard.py`

**4B.3: Audit Log Redaction**
- Audit logs (`audit.jsonl`) contain query text. Queries may contain sensitive keywords.
- Redact any query matching regex: `(api[_-]?key|token|secret|password|credential)[\s:=]+\S+`
- Replace match with `[REDACTED_CREDENTIAL]`.
- File: `src/core/log_redactor.py`

**4B.4: ReDoS Audit**
- Scan all 80 regexes in `certainlogic-intent.ts` for catastrophic backtracking.
- Test each pattern against: `a`*1000, `(`*`500, and crafted payloads.
- Any pattern that takes >50ms = flag for rewrite.
- File: `test/test_regex_safety.py`

**4B.5: Supply Chain Pin**
- `company-brain/` is a fork. Pin the exact commit hash in `docs/brain-version.md`.
- Document divergence points (which files were modified, what was added).
- Before pulling upstream changes: test in isolated session.
- File: `docs/brain-version.md`

**4B.6: Content Sanitization**
- Strip `<script>`, `javascript:`, and `data:` URIs from brain content before returning to skills.
- Markdown is preserved. HTML tags are stripped or escaped.
- File: `src/core/content_sanitizer.py`

**Deliverables (4B):**
- `src/core/input_validator.py`
- `src/core/write_guard.py`
- `src/core/log_redactor.py`
- `src/core/content_sanitizer.py`
- `test/test_regex_safety.py`
- `test/test_security.py`
- `docs/brain-version.md`

**Acceptance criteria (4B):**
| Test | Input | Expected Output | Pass/Fail |
|---|---|---|---|
| Slug validation | `../../etc/passwd` | Rejected with clear error | |
| Slug validation | `concepts/moat` | Accepted | |
| Query length | 2001 chars | Rejected with "query too long" | |
| SQL injection | `"'; DROP TABLE pages; --"` | Rejected with "invalid characters" | |
| Write guard | Script not in allowlist calls `put_page` | Blocked with "write access denied" | |
| Log redaction | Query: `api_key=sk-abc123` | Logged as: `api_key=[REDACTED_CREDENTIAL]` | |
| ReDoS test | Pattern `/\b(a+)+\b/` on input `a`*1000 | Completes in <50ms (or pattern is flagged) | |
| Content sanitize | Content with `<script>alert(1)</script>` | Returns with `<script>` stripped | |
| Content sanitize | Content with `**bold**` markdown | Returns unchanged | |

---

### Phase 4C: Observability (Week 2)

**Cut from Stage 1:** `brain_query_total`, `brain_intent_distribution`, `brain_confidence_avg` (vanity metrics, no decision driver).

**Kept:**
| Metric | Type | Decision driver |
|---|---|---|
| brain_latency_ms_p95 | Histogram p95 | Detect performance regression |
| brain_hit_rate | Gauge | Adoption: are skills using brain? |
| brain_fallback_rate | Gauge | Data quality: is brain useful? |
| brain_error_rate | Gauge | Reliability: is brain stable? |

**Storage:**
- Local: `logs/brain-metrics-YYYY-MM-DD.jsonl` (one line per query)
- Daily rollup: `logs/brain-metrics-daily-YYYY-MM-DD.json` (aggregates)
- Retention: 30 days for raw, 90 days for daily.

**Dashboard:**
- Script: `scripts/brain_metrics.py --today` — prints summary to terminal
- Optional: HTML dashboard at `company-brain-data/dashboard.html` (static file, no server needed)

**Deliverables (4C):**
- `src/core/metrics.py` — lightweight metric recording (~10 lines per query)
- `scripts/brain_metrics.py --today` — daily summary
- `scripts/brain_metrics.py --tail N` — last N queries
- `test/test_metrics.py`

**Acceptance criteria (4C):**
| Test | Input | Expected Output | Pass/Fail |
|---|---|---|---|
| Metric recording | 100 brain queries | 100 lines in `brain-metrics-*.jsonl` | |
| Daily rollup | Run `--today` after 100 queries | Single JSON with p95, hit rate, fallback rate, error rate | |
| No perf impact | Brain query with metrics enabled | Latency increase <1ms compared to without metrics | |

---

### Phase 4D: Pilot Skill Migration (Week 2)

Migrate ONE skill first. Validate the hardened layer before bulk migration.

**Pilot skill: `content-engine`** (X post generation)
- Why: Highest impact, most queries are strategy/branding questions (natural brain fit)
- Complexity: Medium (needs brand voice from brain, but also creative generation)

**Migration pattern:**
```python
from brain_wrapper import Brain

def generate_post(slot, topic=None):
    brain = Brain()
    
    # Query brand voice / strategy
    if topic:
        strategy = brain.strategy(f"brand voice for {topic}")
        positioning = brain.product(topic)
    else:
        strategy = brain.strategy("brand voice default")
    
    # If brain has nothing, fall back to legacy (LLM prompt without brain context)
    # If brain has results, include them in the LLM prompt
    legacy_prompt = build_legacy_prompt(slot, topic)
    
    if strategy.get("confidence", 0) > 0.2:
        enhanced_prompt = f"""
Company positioning (from verified knowledge base):
{strategy['answer']}

{legacy_prompt}
"""
        return call_llm(enhanced_prompt)
    
    return call_llm(legacy_prompt)
```

**Key principle:** The brain ENHANCES the prompt, it doesn't REPLACE the LLM. If brain returns nothing, the skill works exactly as before.

**Deliverables (4D):**
- Updated `marketing/content_engine.py` with brain integration
- `test/content_engine_brain_test.py` — test brain-enhanced vs legacy path
- Migration log: `docs/skill-migration/content-engine.md`

**Acceptance criteria (4D):**
| Test | Input | Expected Output | Pass/Fail |
|---|---|---|---|
| Brain-enhanced path | Query with strong brain match | More on-brand post than legacy | |
| Legacy fallback | Query with no brain match | Same output as before migration | |
| Brain unavailable | Circuit breaker open | Falls back to legacy, no error | |
| Latency | Brain-enhanced path | Total latency < legacy + 200ms | |

---

### Phase 4E: Bulk Skill Migration (Weeks 3–4)

Migrate remaining 9 skills, validated one at a time.

| Priority | Skill | Brain Usage | Complexity |
|---|---|---|---|
| 1 | `content-engine` | `brain.strategy()` brand voice | Done (Phase 4D) |
| 2 | `x-api` (v1 slots) | `brain.strategy()` messaging | Low |
| 3 | `x-api` (v2 trending) | `brain.product()` positioning | Low |
| 4 | `market-research-pro` | `brain.search()` + `brain.metrics()` | Medium |
| 5 | `certainlogic-pathfinder` | `brain.query()` audit trails | Medium |
| 6 | `seo-audit-pro` | `brain.search()` SEO knowledge | Low |
| 7 | `cold-outreach-pro` | `brain.strategy()` positioning | Low |
| 8 | `skill-vetter-plus` | `brain.strategy()` security rules | Low |
| 9 | `skill-oracle` | `brain.search()` skill docs | Low |
| 10 | `skill-guard` | `brain.search()` bad patterns | Low |

**Deliverables (4E):**
- Updated SKILL.md for each of 10 skills
- `brain_integration.py` shim per skill (import guard)
- `test/skill_migration_test.py` — smoke test for each skill
- `docs/skill-migration/INDEX.md` — status tracker

**Acceptance criteria (4E):**
- All 10 skills import `brain_wrapper.Brain()` without error
- All 10 skills fall back to legacy behavior when brain unavailable
- No skill regression (all existing tests pass)

---

### Phase 4F: Cache Layer (Week 4)

**Purpose:** Required for external dataset validation (Wikipedia, etc.). Facts can grow 10–100x quickly; PGLite LIKE queries on 10K–100K rows degrade without cache.

**Cache layers:**

1. **Intent Classification Cache** — `query_text → intent` mapping.
   - Storage: In-memory dict, max 1000 entries, LRU eviction
   - TTL: 1 hour (patterns don't change often)
   - File: `src/core/intent_cache.py`

2. **Query Result Cache** — `query_text + detail_level + limit → results`.
   - Storage: SQLite on disk (`company-brain-data/query_cache.db`)
   - TTL: 5 minutes (content changes with ingestion)
   - Invalidation: On `brain.put_page`, `brain.ingest` — clear all cache
   - File: `src/core/query_cache.py`

**Deliverables (4F):**
- `src/core/intent_cache.py`
- `src/core/query_cache.py`
- Updated `brain_wrapper.py` with cache integration
- `test/test_cache.py`

**Acceptance criteria (4F):**
| Test | Input | Expected Output | Pass/Fail |
|---|---|---|---|
| Intent cache hit | Query "moat" twice | Second query returns cached intent in <1ms | |
| Intent cache miss | New query "never seen before" | Runs regex classification, stores in cache | |
| Query cache hit | Same query + detail + limit twice | Second query returns cached results in <5ms | |
| Cache invalidation | Ingest new page, then query | Returns fresh results (not stale cache) | |
| Cache performance | 1000 unique queries | Intent cache hit rate >50% | |

---

### Phase 4G: Testing (Week 5)

**Three tiers:**

**G.1: Unit tests (Python)**
- `test/test_intent_detection.py` — 50 queries per category
- `test/test_source_boosts.py` — Verify correct slug→boost mapping
- `test/test_input_validation.py` — Injection attempts
- `test/test_security.py` — All security mitigations
- `test/test_cache.py` — Cache hit/miss/invalidation

**G.2: Integration tests**
- `test/test_brain_end_to_end.py` — Full query → result pipeline
- `test/test_fallback.py` — Brain empty → legacy path

**G.3: Benchmark**
- `test/test_brain_benchmark.py` — 200 queries, old path vs new path
- Measure: latency (target: <100ms with cache), cost ($0 brain vs LLM cost), accuracy (brain answers relevant?)
- Target: brain path <100ms avg (with cache), hit rate >50%, cost reduction >30%

**Deliverables (4G):**
- `test/` directory with all test files
- `scripts/run_tests.sh` — runs all tiers with report
- `test/BENCHMARK_RESULTS.md` — baseline vs brain-enhanced comparison

**Acceptance criteria (4G):**
| Tier | Target | Pass/Fail |
|---|---|---|
| Unit tests | ≥90% pass rate | |
| Integration tests | 100% pass rate | |
| Benchmark | <100ms avg latency, >50% hit rate, >30% cost reduction | |

---

### Phase 4H: Deployment & Rollback (Week 5)

**4G.1: Feature Flag**
- Environment variable: `BRAIN_DETERMINISTIC_LAYER=enabled|disabled`
- Default: `enabled` (once tested)
- When `disabled`: `Brain()` returns empty results, skills use legacy path

**4G.2: Deployment Script**
- `scripts/brain-deploy.sh` — commits, runs tests, enables flag
- `scripts/brain-rollback.sh` — reverts last commit, disables flag

**4G.3: Version Pinning**
- `docs/brain-version.md` — exact gbrain commit hash, divergence documentation

**Deliverables (4G):**
- `scripts/brain-deploy.sh`
- `scripts/brain-rollback.sh`
- `docs/brain-deployment.md`
- `docs/brain-version.md`

**Acceptance criteria (4G):**
| Test | Input | Expected Output | Pass/Fail |
|---|---|---|---|
| Deploy | Run `brain-deploy.sh` | Commits, tests pass, flag enabled | |
| Rollback | Run `brain-rollback.sh` | Reverts, tests pass, flag disabled | |
| Feature flag off | `BRAIN_DETERMINISTIC_LAYER=disabled` | All skills use legacy path, no brain queries | |
| Feature flag on | `BRAIN_DETERMINISTIC_LAYER=enabled` | Skills query brain normally | |

---

### Phase 4I: LLM Fallback (Week 5)

When brain returns nothing useful, skills fall back to what they would have done before brain existed.

**No complex prompt templates.** Just:
```python
if confidence < 0.2:
    return legacy_llm_answer(query)
```

**One addition:** Include a `brain_sourced` boolean in responses so the agent (and user) knows where the answer came from.

**Deliverables (4H):**
- Updated `brain_wrapper.py` — `brain_sourced` field in all responses
- Updated each skill — append `brain_sourced` to output metadata

---

## Out of Scope (Phase 5)

1. **Cache layers** — In scope for Phase 4D (Week 4). Required for external dataset validation (Wikipedia, etc.) where facts can grow 10–100x quickly.
2. **Multi-brain support** — Single brain instance only.
3. **Distributed brain** — Single node only.
4. **Real-time sync** — Batch ingestion, not streaming.
5. **Natural language ingestion** — Manual or scripted ingestion only.
6. **Mobile app** — Web-only.
7. **Third-party API** — Internal use only.
8. **Vector DB migration** — PGLite only.
9. **Mathematical prompt decomposition** — Separate project (2026-05-04 insight). Enables the 2% hallucination target, but not in Brain OS scope.

---

## Milestones (5-Week Timeline)

| Week | Milestone | Deliverables | Acceptance Criteria |
|---|---|---|---|
| **W1** | Production Hardening + Security | circuit_breaker.py, error_classifier.py, cli_pool.py, updated brain_wrapper.py, input_validator.py, write_guard.py, log_redactor.py, content_sanitizer.py, regex guard | All AC tables pass |
| **W2** | Observability + Pilot Migration | metrics.py, brain_metrics.py, content_engine.py migrated | 4 metrics recording, pilot skill works with brain |
| **W3** | Bulk Migration (Skills 2–6) | 5 skills migrated | All skills import Brain(), no regressions |
| **W4** | Cache Layer + Bulk (Skills 7–10) + Testing | intent_cache.py, query_cache.py, invalidation logic, 4 skills migrated, all tests, benchmark | Cache hit rate >50%, benchmark targets hit |
| **W5** | Deployment + Fallback | deploy.sh, rollback.sh, feature flags, brain_sourced field | One-command deploy/rollback, flag works |

---

## Dependencies

| Dependency | Risk Level | Mitigation |
|---|---|---|
| gbrain CLI stability | Medium | Pin version. Monitor PGLite. `bun run` works; `bun build` broken. |
| Anton review bandwidth | High (bottleneck) | Weekly review checkpoint. Anton can approve/reject per-milestone. |
| Brain data quality | High | Confidence threshold (0.2). Fallback to legacy. Periodic curation (not in this scope). |
| Model availability for fallback | Low | OpenRouter fallback: 24 free models configured. |
| Subagent data destruction | Medium | Never touch `test/`, `benchmark/` dirs with subagents. Write-protect. |

---

## Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Brain queries too slow | Skills revert to legacy, Brain OS unused | Low | PGLite on 443 rows is fast. Timeout ensures bounded latency. |
| Brain data stale/wrong | Agent gives wrong answers confidently | High | Confidence threshold + fallback. `brain_sourced` flag shows user where answer came from. |
| Feature flag fails off | Can't disable broken layer | Low | Test flag in CI. Rollback script as backup. |
| gbrain CLI breaks | All brain queries fail | Medium | Pin version. Isolated session testing before upgrade. |
| Subagent destroys data (repeat of Hermes) | Test suite lost | Medium | `test/` and `benchmark/` directories write-protected at filesystem level. |
| Anton unavailable for review | Milestones stall | Medium | Each milestone has a "default proceed after 48h if no rejection" rule. |

---

## Key Decisions Needed (From Anton)

1. **Confidence threshold:** Currently 0.2. Is this right? Higher = more fallbacks but fewer false confidences.
2. **Metrics retention:** Keep raw logs for 30 days, daily rollups for 90 days. OK?
3. **Pilot skill:** Content engine (X post generation). Good choice, or prefer something else?
4. **Write allowlist:** Who can write to the brain? Just `deterministic_brain.py` + admin scripts, or broader?
5. **Default timeline:** 5 weeks. Can you commit to weekly review checkpoints? Or extend to 6 weeks?
6. **Math Prompts relation:** Confirm they're separate (Phase 5), not in this scope.
