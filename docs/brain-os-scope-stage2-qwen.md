# Stage 2 Review: Brain OS Scope — Qwen3 Coder Architectural Critique

**Reviewer:** Qwen3 Coder perspective (senior software architect, anti-bloat, production-hardening focus)
**Input:** Stage 1 (Kimi K2.6 base scope, 395 lines)
**Status:** Critique complete. Recommendations below folded into Stage 3 synthesis.

---

## Stage 2 Review Notes: What Changed and Why

### 1. Priority Inversion: Skill Migration Before Hardening Is Dangerous

**Stage 1 order:** 4A Skill Migration → 4B Production Hardening → ...

**Problem:** Migrating 10 skills to a layer that isn't production-hardened means 10 potential failure points. If the brain times out, circuit breaker misbehaves, or slugs aren't validated, skills break in production.

**Right order:** Harden the layer FIRST (4B Production Layer), THEN migrate one skill as a pilot (4A-Pilot), validate, then migrate the rest (4A-Bulk).

### 2. Cache Is Overkill for 443 Facts

**Stage 1:** Three cache layers (intent, query, facts), invalidation logic, LRU eviction.

**Reality check:** 443 facts in PGLite. A full text search with LIKE queries on 443 rows takes <5ms on modern hardware. Intent regex matching on a 200-char string takes microseconds. The brain is ALREADY sub-100ms without any cache.

**What cache actually costs:**
- Invalidation complexity (when facts change, caches must clear)
- Memory overhead (1000-entry dict × ~200 bytes ≈ 200KB, trivial but still complexity)
- Testing burden (stale reads, race conditions during ingest)
- Bug surface area

**Verdict:** Defer cache to Phase 5. If the brain grows beyond 10,000 facts, revisit. Right now, cache is premature optimization disguised as architecture.

### 3. Too Many Metrics = Noise

**Stage 1:** 8 metrics including `brain_intent_distribution`, `brain_confidence_avg`, `brain_error_rate`.

**Actionable question:** What decision does each metric drive?

| Metric | Action if high? | Action if low? | Decision relevance |
|---|---|---|---|
| brain_query_total | None (counter) | None (counter) | ❌ Vanity — total queries doesn't change behavior |
| brain_latency_ms | Investigate slow queries | None | ✅ Yes — detects performance regression |
| brain_hit_rate | Keep doing what works | Re-evaluate threshold or data quality | ✅ Yes — core adoption metric |
| brain_confidence_avg | Check for overconfidence | Check for underconfidence | ⚠️ Depends on ground truth (we don't have labeled data) |
| brain_fallback_rate | Data quality problem | Success (brain answers most) | ✅ Yes — inverse of hit rate |
| brain_intent_distribution | Verify routing loads are balanced | None | ⚠️ Interesting but not actionable |
| brain_error_rate | Investigate root cause | None | ✅ Yes — reliability metric |

**Recommendation:** Cut to 4 metrics: latency, hit rate, fallback rate, error rate. The others are dashboard fillers.

### 4. Security: Missing the Real Threats

**Stage 1 threats:** Prompt injection, path traversal, credential exposure, regex DoS.

**Missing threats:**
1. **Supply chain** — gbrain is a fork. If Garry's repo introduces a breaking change, our fork stays behind. Pin the fork version. Document divergence points.
2. **Data poisoning** — Anyone who can `brain.put_page` can introduce false facts. Stage 1 has NO write access control. If a compromised subagent writes bad facts, all queries return poison.
3. **Log leakage** — Audit logs contain full query text. If queries contain sensitive keywords ("X API key", "Stripe test"), logs leak them.
4. **ReDoS in intent patterns** — 80 regexes written by Kimi may contain catastrophic backtracking. `(a+)+` patterns hidden in seemingly innocent regexes.
5. **File descriptor exhaustion** — Every `bun run src/cli.ts` spawns a new process. If a skill calls brain in a loop, we fork-bomb.

### 5. LLM Fallback Design Is Too Complex

**Stage 1:** Two prompt templates, LLM orchestration, brain context injection.

**Simpler approach:** The fallback IS "just call the LLM with the user's original query." The brain is an optimization layer, not a requirement. If brain doesn't know, agent should do what it would have done BEFORE brain existed.

**Don't:** Build a complex prompt template system.
**Do:** `if brain_result.confidence < 0.2: return legacy_llm_answer(query)`

**The only addition:** Flag in the response whether the answer came from brain or LLM. That's one boolean field, not a template engine.

### 6. Relation to "Mathematically Perfect Prompts" (2026-05-04)

The Brain OS and the 2% hallucination strategy are **complementary but distinct:**

| Brain OS | Math Prompts |
|---|---|
| **What:** Structured facts + intent routing | **What:** Prompt decomposition + bounded choice sets |
| **When:** Agent needs company-specific knowledge | **When:** Agent needs to make any decision |
| **How:** Local search + source ranking | **How:** Structural prompt optimization |
| **Goal:** Reduce hallucination on facts | **Goal:** Reduce hallucination on reasoning |
| **Status:** 80% built | **Status:** Concept only |

**Integration point:** Brain OS provides the "ground truth facts" that make mathematical prompts effective. If the prompt says "Choose from [A, B, C] based on company strategy," Brain OS supplies the strategy document. Without Brain OS, the prompt has no ground truth to ground choices in.

**Recommendation:** Keep them separate in scope. Brain OS = Phase 4. Math Prompts = Phase 5 (separate project). Don't let scope creep merge them.

### 7. Timeline Is Too Aggressive

**Stage 1:** 3 weeks for 8 milestones.

**Realistic pacing:** Each milestone requires Anton review for at least some components. Anton's bandwidth is the real constraint.

| Milestone | Realistic Days | Stage 1 Days |
|---|---|---|
| Production Hardening | 5 | 7 |
| Pilot Skill Migration | 3 | 7 |
| Bulk Skill Migration | 7 | 7 |
| Observability | 2 | 7 |
| Cache | 0 (deferred) | 7 |
| Security | 3 | 7 |
| Deployment | 2 | 7 |
| Testing | 5 | 7 |
| LLM Fallback | 2 | 7 |
| **Total** | **≈4 weeks** | **3 weeks** |

### 8. Missing Acceptance Criteria

Many Stage 1 criteria are vague:
- "Timeout <3s" → What's the baseline? What's the worst case? How many 9s?
- "Circuit breaker works" → Define "works." 5 failures trigger? Recovery after 10 min?
- "All 4 mitigations tested" → How? Manually? Unit tests? Fuzzing?

**Need:** Concrete test cases with inputs and expected outputs.

### 9. Architecture Simplification

**Current wrapper hierarchy:**
```
skill → brain_wrapper.Brain() → certainlogic_router.py → certainlogic-router.ts → gbrain CLI
```

**Problem:** 4 layers for a query that ultimately runs `bun run src/cli.ts query "..."`.

**Simpler hierarchy:**
```
skill → Brain() → gbrain_cli() → bun run src/cli.ts
```

The TypeScript router and intent classifier are useful for brain-native code, but the Python wrapper should just:
1. Detect intent (regex in Python)
2. Call gbrain with appropriate `--detail` and `--limit`
3. Return parsed results

The TypeScript files are for gbrain internal features (custom search, CLI extensions), not for the Python skill bridge.

**Verdict:** Keep TS files for gbrain internals. Simplify Python wrapper to call CLI directly with intent-aware flags.

---

## Consolidated Recommendations for Stage 3

1. **Reorder:** Production Hardening → Pilot Migration → Metrics → Security → Bulk Migration → Testing → Deployment → LLM Fallback
2. **Cut:** Cache (deferred to Phase 5), intent_distribution metric, query_template engine
3. **Add:** Supply chain pinning, write-access control, log redaction, ReDoS audit, process pool for CLI calls
4. **Fix:** Acceptance criteria must be measurable (exact numbers, exact inputs, exact expected outputs)
5. **Simplify:** Python wrapper calls gbrain CLI directly; TypeScript router stays internal
6. **Separate:** Math Prompts strategy = Phase 5, not in this scope
7. **Extend:** 3 weeks → 4 weeks

---

**Next:** Fold these recommendations into Stage 3 (Opus 4.6 synthesis) for final merged scope.
