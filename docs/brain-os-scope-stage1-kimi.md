# Scope & Spec: CertainLogic Brain OS — Deterministic Layer + Skill Migration

**Version:** Stage 1 (Kimi K2.6 base scope)
**Date:** 2026-05-07
**Status:** Draft — pending multi-LLM review

---

## Executive Summary

The CertainLogic Brain OS is a deterministic middleware layer sitting atop Garry Tan's gbrain, providing agent skills with structured, auditable, local-first knowledge retrieval. Phase 1–3 are complete (moat thesis grounding, search alignment, intent routing). This scope covers Phase 4 (skill migration) and production hardening.

**Core thesis:** Agent queries should hit a local, deterministic brain before ever calling an LLM. This reduces hallucination (facts over synthesis), latency (sub-100ms), and cost (zero API tokens for known questions).

---

## In Scope

### Phase 4A: Skill-by-Skill Migration
Migrate all CertainLogic skills to use `brain_wrapper.Brain()` for queries before falling back to LLM or external tools.

**Target skills:**
| Skill | Current Query Pattern | Brain Usage |
|---|---|---|
| `certainlogic-pathfinder` | Audit trail lookups | `brain.query()` for page history |
| `skill-vetter-plus` | Security scan references | `brain.strategy()` for security rules |
| `skill-oracle` | Skill documentation | `brain.search()` for skill specs |
| `skill-guard` | ClawHub skill checks | `brain.search()` for known bad patterns |
| `x-api` (v1 slots) | Content generation | `brain.strategy()` for brand voice alignment |
| `x-api` (v2 trending) | Trending topic selection | `brain.query()` for product positioning |
| `content-engine` | Post generation | `brain.strategy()` for messaging principles |
| `market-research-pro` | Research synthesis | `brain.search()` + `brain.metrics()` |
| `seo-audit-pro` | SEO analysis | `brain.search()` for SEO knowledge |
| `cold-outreach-pro` | Outreach copy | `brain.strategy()` for positioning |

**Migration pattern per skill:**
```python
def handle_request(inputs):
    # 1. Brain-first query
    brain = Brain()
    result = brain.query(inputs["user_query"])
    
    if result["confidence"] > 0.2:
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "brain_first": True,
        }
    
    # 2. Fallback to LLM with brain context
    return fallback_to_llm(inputs, brain_context=result["sources"])
```

**Deliverables:**
- Updated `SKILL.md` for each target skill with brain-first pattern
- `brain_integration.py` shim per skill (import guard for brain availability)
- Test: each skill can operate without brain (graceful degradation)

**Acceptance criteria:**
- All 10 skills import `brain_wrapper.Brain()` without error
- Each skill falls back to legacy behavior when brain unavailable
- No skill broken by brain integration (backward compatibility)

---

### Phase 4B: Production Deterministic Layer

Harden `deterministic_brain.py` and `brain_wrapper.py` for production use.

**Components:**

1. **Circuit Breaker** — If brain query fails N times consecutively, stop querying for M minutes. Return "brain temporarily unavailable" to callers.
   - Config: `BRAIN_CIRCUIT_FAILURES=5`, `BRAIN_CIRCUIT_TIMEOUT_MINUTES=10`
   - File: `src/core/circuit_breaker.py`

2. **Timeout Enforcement** — Every brain query has a hard timeout. Default: 2s for search, 5s for page get.
   - Config: `BRAIN_SEARCH_TIMEOUT_MS=2000`, `BRAIN_GET_TIMEOUT_MS=5000`
   - Implementation: `signal.alarm()` or `concurrent.futures.ThreadPoolExecutor` in Python wrapper

3. **Retry Logic** — Exponential backoff for transient failures (gbrain CLI timeout, file lock).
   - Max retries: 3, Base delay: 100ms, Backoff factor: 2

4. **Error Classification** — Distinguish permanent errors (bad slug, no matching pages) from transient (CLI timeout, file lock).
   - Permanent → return empty result
   - Transient → retry

**Deliverables:**
- `src/core/circuit_breaker.py`
- `src/core/error_classifier.py`
- Updated `brain_wrapper.py` with timeout + retry + circuit breaker
- `docs/brain-production-config.md` — environment variable reference

**Acceptance criteria:**
- Brain query timeout works (simulated slow query returns in <3s)
- Circuit breaker trips after 5 failures and recovers after timeout
- Retry logic handles transient CLI failures
- All errors classified correctly (no false positives)

---

### Phase 4C: Observability

Track brain performance without adding latency.

**Metrics to collect:**
| Metric | Type | Where |
|---|---|---|
| brain_query_total | Counter | Every query |
| brain_query_latency_ms | Histogram | Every query |
| brain_hit_rate | Gauge | Hits / total |
| brain_confidence_avg | Gauge | Average of top result scores |
| brain_fallback_rate | Gauge | Fallbacks / total |
| brain_intent_distribution | Counter | Per-intent (strategy/product/data/operations/general) |
| brain_error_rate | Gauge | Errors / total |

**Storage:**
- Local: `logs/brain-metrics-YYYY-MM-DD.jsonl`
- Daily rollup: `logs/brain-metrics-daily.json`

**Dashboard:**
- Simple HTML dashboard served from brain API (`/metrics` endpoint)
- Or: `bun run src/cli.ts metrics --today`

**Deliverables:**
- `src/core/metrics.py` / `src/core/metrics.ts`
- `docs/brain-metrics.md` — metric definitions + interpretation guide
- Script: `scripts/brain_metrics_report.py --today`

**Acceptance criteria:**
- All 8 metrics recorded for every query
- Metrics file rotates daily, doesn't grow unbounded
- Daily report generated automatically (cron)
- Report: hit rate >70%, fallback rate <30%, error rate <5%

---

### Phase 4D: Cache Strategy

Reduce redundant work by caching intent classification and frequently-queried content.

**Cache layers:**

1. **Intent Classification Cache** — `query_text → intent` mapping. Tiny (strings), high hit rate on repeated questions.
   - Storage: In-memory dict, max 1000 entries, LRU eviction
   - TTL: 1 hour (intents don't change often, but new patterns can be added)
   - File: `src/core/intent_cache.py`

2. **Query Result Cache** — `query_text + detail_level + limit → results`.
   - Storage: SQLite or JSON on disk (brain data is small, 443 facts)
   - TTL: 5 minutes (content changes as brain ingests)
   - Invalidation: On `brain.put_page`, `brain.ingest`
   - File: `src/core/query_cache.py`

3. **Facts DB Sync** — Keep hot facts in memory for sub-10ms access.
   - Load `facts_db` into dict at startup
   - Reload on file modification time change
   - File: `src/core/facts_cache.py`

**Deliverables:**
- `src/core/intent_cache.py`
- `src/core/query_cache.py`
- `src/core/facts_cache.py`
- Updated `brain_wrapper.py` with cache integration

**Acceptance criteria:**
- Intent cache hit rate >60% on repeated queries
- Query cache hit rate >30% on repeated queries
- Cache invalidation works (new page ingestion clears cache)
- No cache stale reads (reads after write show updated data)

---

### Phase 4E: Security Hardening

Prevent injection and data leakage in the brain query pipeline.

**Threats:**
1. **Prompt injection via brain content** — Malicious markdown in brain pages could leak into prompts.
2. **Path traversal in slug** — `../../etc/passwd` passed as slug.
3. **Credential exposure in error messages** — CLI errors might contain file paths or credentials.
4. **Input injection in regex patterns** — Crafted query could DoS the intent classifier.

**Mitigations:**
1. **Content sanitization** — Strip HTML/script from brain content before returning. Markdown is fine, but no inline scripts.
   - File: `src/core/content_sanitizer.py`

2. **Slug validation** — Whitelist allowed characters: `[a-zA-Z0-9_/-]`. Reject `..`, `~`, absolute paths.
   - File: `src/core/slug_validator.py`

3. **Error message redaction** — Any error containing `SECRET_`, `API_`, `TOKEN_`, `KEY_` is replaced with `[REDACTED]`.
   - File: `src/core/error_redactor.py`

4. **Regex timeout** — Intent patterns have a max execution time (50ms). Slow patterns killed.
   - File: `src/core/regex_guard.py`

**Deliverables:**
- `src/core/content_sanitizer.py`
- `src/core/slug_validator.py`
- `src/core/error_redactor.py`
- `src/core/regex_guard.py`
- `docs/brain-security.md` — threat model + mitigations

**Acceptance criteria:**
- Path traversal attempt returns sanitized error (no file system access)
- Content with `<script>` tags is stripped before returning
- Error messages never contain credential keywords
- Regex timeout prevents DoS (test with `r'^(a+)+$'` on `a`*1000)

---

### Phase 4F: Deployment Model

How brain code updates deploy alongside the main workspace.

**Current state:**
- `company-brain/` is in workspace repo (not submodule)
- `src/core/search/certainlogic-*.ts` files are ignored by `.gitignore` wildcard but force-added
- `bun run src/cli.ts` works; `bun build` fails

**Deployment needs:**
1. **Hot reload** — Brain code changes should be testable without restart
   - Since `bun run` interprets TypeScript on the fly, file edits are immediate
   - Python wrapper reloads module on import

2. **Rollback** — If brain update breaks queries, revert in one command
   - Git-based: `git revert <commit>`
   - Feature flags: `BRAIN_DETERMINISTIC_LAYER=enabled|disabled`

3. **Staging** — Test brain changes before they affect production
   - Isolated session approach: spawn subagent with modified brain code
   - Or: second gbrain data dir (`~/.gbrain-staging/`)

**Deliverables:**
- `scripts/brain-deploy.sh` — commit, test, enable
- `scripts/brain-rollback.sh` — revert + verify
- Environment flag: `BRAIN_DETERMINISTIC_LAYER=enabled|disabled`
- `docs/brain-deployment.md`

**Acceptance criteria:**
- `brain-deploy.sh` commits changes, runs tests, enables flag
- `brain-rollback.sh` reverts in <30s
- Feature flag works (disabled → brain returns empty, skills use legacy path)

---

### Phase 4G: Testing Strategy

Three-tier testing: unit, integration, benchmark.

**Unit tests:**
- Intent classification: 50 test queries per category (strategy/product/data/operations/general)
  - File: `test/intent_classification_test.py`
- Source boost correctness: Verify correct prefix matching
  - File: `test/source_boost_test.py`
- Router: Verify correct action selection per intent
  - File: `test/router_test.py`

**Integration tests:**
- Brain wrapper end-to-end: `Brain().query("moat")` returns expected results
  - File: `test/brain_integration_test.py`
- Fallback chain: brain empty → fallback to LLM mock
  - File: `test/fallback_test.py`

**Benchmark:**
- Run 200 queries through old path (direct to LLM) vs new path (brain-first)
  - Measure: latency, cost, accuracy
  - Target: brain path <100ms, 70%+ hit rate, 50%+ cost reduction
  - File: `test/brain_benchmark.py`

**Deliverables:**
- `test/` directory with all test files
- `scripts/run_tests.sh` — runs all tiers
- `docs/brain-testing.md` — test plan + interpretation

**Acceptance criteria:**
- Unit tests: >90% pass rate
- Integration tests: all green
- Benchmark: brain path <100ms avg, hit rate >70%

---

### Phase 4H: LLM Integration (Fallback Path)

When brain returns nothing useful, how does the agent fall back to LLM?

**Current gap:** Fallback is unimplemented. The router has `fallbacks: []` placeholder.

**Design:**

```typescript
export type FallbackStrategy = {
  primary: ToolAction;     // brain.query
  fallbacks: ToolAction[]; // [brain.search, web.fetch, llm.synthesize]
  llm_prompt_template: string; // How to format brain results + user query for LLM
};
```

**LLM prompt template (when brain has partial results):**
```
You are answering based on company knowledge. Here are relevant facts:
<BRAIN_RESULTS>

User question: <USER_QUERY>

Guidelines:
- If the facts fully answer the question, answer directly.
- If the facts partially answer, synthesize with your knowledge but flag uncertainties.
- If the facts don't answer, say "I don't have that information on file."
- Never contradict the facts provided.
```

**LLM prompt template (when brain has NO results):**
```
User question: <USER_QUERY>

Guidelines:
- This query was not found in our knowledge base.
- Answer based on your training data but flag any uncertainty.
- If this involves company-specific details, recommend documenting the answer.
```

**Deliverables:**
- `src/core/llm_fallback.ts` — prompt templates + fallback orchestration
- `src/core/prompt_templates/` — directory of prompt templates per intent
- Updated `certainlogic-router.ts` with functional fallback chain

**Acceptance criteria:**
- Fallback triggers when brain confidence < 0.2
- LLM receives brain context (top sources) in prompt
- LLM never contradicts brain facts
- Response flags when information comes from LLM vs brain

---

## Out of Scope (Phase 5)

1. **Multi-brain support** — Querying multiple gbrain instances
2. **Distributed brain** — Brain across multiple machines/nodes
3. **Real-time sync** — WebSocket-based brain update streaming
4. **Natural language ingestion** — Auto-extract facts from emails/meetings
5. **Mobile app** — Brain access from mobile devices
6. **Third-party API** — Exposing brain as REST API to external customers
7. **Vector DB migration** — Moving from PGLite to Pinecone/Weaviate
8. **Mathematical prompt decomposition** — Your 2% hallucination architecture (separate project)

---

## Milestones

| Phase | Milestone | Deliverables | Target Date | Acceptance Criteria |
|---|---|---|---|---|
| 4A | Skill Migration Complete | Updated SKILL.md × 10, brain_integration.py × 10 | 2026-05-14 | All skills import Brain(), no regressions |
| 4B | Production Layer Hardened | circuit_breaker.py, error_classifier.py, updated wrapper | 2026-05-14 | Timeout <3s, circuit breaker works, retry handles transient |
| 4C | Observability Live | metrics.py, daily report, dashboard | 2026-05-14 | All 8 metrics recorded, report auto-generates |
| 4D | Cache Deployed | intent/query/facts cache, invalidation logic | 2026-05-21 | Intent cache 60%+ hit, query cache 30%+ hit |
| 4E | Security Hardened | sanitizer, validator, redactor, regex guard | 2026-05-21 | All 4 mitigations tested, no injection paths |
| 4F | Deployment Model | deploy/rollback scripts, feature flags | 2026-05-21 | One-command deploy/rollback, flag works |
| 4G | Tests Green | Unit + integration + benchmark | 2026-05-28 | 90%+ unit pass, all integration green, benchmark targets hit |
| 4H | LLM Fallback | Fallback chain, prompt templates, LLM integration | 2026-05-28 | Fallback triggers correctly, LLM uses brain context, flagged |

**Total estimated timeline:** 3 weeks (2026-05-07 → 2026-05-28)

---

## Dependencies

| Dependency | Risk Level | Mitigation |
|---|---|---|
| gbrain CLI stability | Medium | Currently works (`bun run`), but `bun build` broken. Monitor PGLite issues. |
| Model availability for fallback | Low | OpenRouter fallback configured with 24 free models. |
| Brain data quality | High | 443 facts but many are noisy/ outdated. Needs periodic curation. |
| Anton review bandwidth | Medium | Skills migration requires Anton to verify each SKILL.md update. |
| OpenClaw gateway config | Medium | Chat commands and override protocol need gateway-level wiring. |

---

## Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Brain queries too slow (>100ms) | Skills won't use brain, revert to LLM | Medium | Cache + circuit breaker. Monitor metrics. |
| Brain data stale/wrong | Agent gives wrong answers confidently | High | Confidence threshold (0.2), fallback to LLM, periodic curation |
| Feature flag fails off | Deterministic layer can't be disabled | Low | Test flag in CI. Manual kill switch as backup. |
| gbrain CLI breaking change | All brain queries fail | Medium | Pin gbrain version. Test in isolated session before upgrade. |
| Subagent destroys data again | Benchmark/test data lost | Medium | Never let subagents touch `test/`, `benchmark/`, or `archive/` dirs. |

---

## Key Decisions Needed

1. **Confidence threshold:** Currently 0.2. Is this right? Too low = false confidence. Too high = too many fallbacks.
2. **Cache persistence:** In-memory only, or disk-backed? Disk has invalidation complexity.
3. **Metrics retention:** How long to keep daily metrics? 30 days? 90 days? Forever?
4. **Fallback LLM model:** Which model for LLM fallback? Kimi K2.6 (fast), Opus 4.6 (accurate), or Qwen3 Coder (cheap)?
5. **Brain data curation:** Who curates facts? Cron job? Anton manual review? Agent suggestion?
