# Brain OS Multi-LLM Scope & Spec — Stage 1 Kickoff

## Project: CertainLogic Brain OS — Deterministic Layer + Skill Migration

### Already Built (Phase 1–3 Complete)

**Phase 1 — Moat Thesis Grounding**
- `company-brain/concepts/certainlogic-moat-thesis.md` — Core strategic principles
- `company-brain/concepts/certainlogic-strategic-principles.md` — Operative rules

**Phase 2 — Search Alignment**
- `src/core/search/certainlogic-boosts.ts` — Source-type boost map (concepts: 1.8×, projects: 1.5×)
- Merged into `resolveBoostMap()` in `source-boost.ts`

**Phase 3 — Skills Routing**
- `src/core/search/certainlogic-intent.ts` — 80 regexes, 4 intent categories (strategy/product/data/operations)
- `src/core/search/certainlogic-router.ts` — TypeScript router with fallback chain
- `certainlogic_router.py` — Python bridge for skills
- `brain_wrapper.py` — Drop-in `Brain()` class: `brain.query()`, `brain.strategy()`, `brain.product()`, `brain.metrics()`, `brain.ops()`
- `intent.ts` modified — `autoDetectDetail()` checks CL patterns after base

**Current Architecture**
```
Query Text
    ↓
Intent Classifier (certainlogic-intent.ts) — 80 regexes
    ↓
Routing Decision (certainlogic-router.ts)
    ↓
Brain Search with Source Boosts (merged into hybrid.ts)
    ↓
Structured Result (brain_wrapper.py)
```

**Production Status**
- GBrain CLI: `bun run src/cli.ts` works (bun build fails on Node.js builtins)
- Brain API: localhost:8000, 443 facts loaded
- Git: clean, all committed
- No uncommitted files

### What Needs Scoping (Phase 4 + Production Hardening)

1. **Skill-by-Skill Migration** — Which skills use brain-first queries? How? Fallback chain?
2. **Production Deterministic Layer** — Error handling, timeouts, retries, circuit breakers
3. **Observability** — Metrics: brain hit rate, confidence distribution, fallback rate, latency
4. **Cache Strategy** — Intent classification caching, query result caching, facts sync
5. **Security Hardening** — Input validation, injection prevention, credential isolation
6. **Deployment Model** — How brain code deploys alongside main workspace
7. **Testing Strategy** — Unit tests for intent patterns, integration tests for routing, benchmark for accuracy
8. **LLM Integration** — When brain returns nothing, how does fallback to LLM work? Prompt structure?

### Constraints
- Deterministic > accurate > comprehensive (always prefer known facts over synthesis)
- Sub-100ms brain queries (local, no API calls)
- Git-tracked: all brain code committed, no secrets in repo
- Audit trail: every query logged via deterministic_brain.py audit system
- No submodule (company-brain is fork in workspace repo)

### Request

Generate a comprehensive scope and spec document covering all 8 areas above. Be explicit about:
- What's in scope vs out of scope
- Milestones / phases
- Deliverables (files, scripts, config changes)
- Acceptance criteria for each milestone
- Dependencies and risks

Write your output as a structured Markdown document suitable for feeding to the next LLM review stage.
