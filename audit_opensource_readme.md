## 🚨 CRITICAL FINDINGS — Open Source README Audit
**Repo:** `CertainLogicAI/hallucination-guard` (our "first open source product")
**File:** `/data/.openclaw/workspace/opensource/README.md`
**Audited:** 2026-05-02 ~10:35 EDT

---

### FALSE OR WITHDRAWN CLAIMS STILL PRESENT

| Line | Claim | Status | Truth |
|------|-------|--------|-------|
| Tagline | "Kill AI hallucinations deterministically" | ❌ FALSE | Only deterministic when fact EXACTLY matches DB. Unknown queries still use LLM. |
| Tagline | "85-98% token savings" | ❌ WITHDRAWN | Real: ~38% cache hit rate on measured workloads. 85-98% was old fabricated marketing. |
| Why This Exists | "Deterministic verification – rule-based fact-checking" | ⚠️ MISLEADING | Deterministic ONLY for cached/matched facts. Not deterministic for novel queries. |
| Benchmarks | "83.9% hallucination detection accuracy" | ❌ WITHDRAWN | Benchmark withdrawn April 2026. This number unverified. |
| Benchmarks | "100% recall on pricing queries" | ❌ WITHDRAWN | Part of withdrawn benchmark suite. |
| Benchmarks | "<1% hallucination rate (rule-based)" | ❌ UNVERIFIED | Never measured. Made up for comparison table. |
| Comparison | "5-15% (LLM judges can hallucinate)" | ❌ UNSOURCED | No source for competitor hallucination rates. |
| Compliance | "HIPAA/GDPR/SOC2/FedRAMP patterns" | ⚠️ ASPIRATIONAL | Designed with compliance in mind, but ZERO certifications. Not "ready." |
| Compliance | "Regulatory-ready" | ⚠️ MISLEADING | Implies certification exists. It does not. |
| Products | "$39 Coder Pack, $199 Industrial Pack" | ❌ NOT FOR SALE | No shop exists at shopclawmart.com to actually buy these. |
| Products | "sales@certainlogic.ai" | ❌ UNVERIFIED | Email may not exist or be monitored. |
| Integration | LangChain integration examples | ❌ UNVERIFIED | `examples/langchain_integration.py` referenced but existence not confirmed. |
| Branding | "CertainLogic Verifier" | ⚠️ CONFUSING | Repo is `hallucination-guard` but README calls it "Verifier" — two brands for one product. |

---

### WHAT'S ACTUALLY TRUE

- FastAPI service with /validate, /reduce, /search, /route endpoints
- Uses facts DB (JSON) for verification
- Has semantic caching layer
- MIT licensed
- Self-hostable
- 84 facts currently loaded

### WHAT'S MISLEADING ABOUT ARCHITECTURE

The README describes a **full brain API service** (/route, /search, /reduce, /validate) but the actual `hallucination-guard` package on PyPI is just the **linguistic guard** (hedge word detection). The brain API is a SEPARATE product.

The README conflates two things:
1. `hallucination-guard` pip package = linguistic scanner only
2. Brain API = full service with caching, routing, facts DB

This is like describing a car and calling it a bicycle.

---

### SCOPE TO FIX

**Option A: Minimal** — Strip all false claims, keep structure
- Remove benchmark numbers
- Remove "deterministic" blanket claim
- Add "not certified" qualifier to compliance section
- Remove fact pack pricing (until shop exists)
- Fix branding to "Hallucination Guard" consistently
- ~30 minutes

**Option B: Honest Rewrite** — Rewrite entire README to match actual v2.0 product
- Describe what the guard ACTUALLY does (linguistic pattern detection + optional facts DB lookup)
- Honest limitations section
- Remove all comparison tables with unsourced competitor claims
- Remove roadmap items that are aspirational
- Add "What this is NOT" section
- ~60 minutes

**Option C: Full Correction** — Split README to match actual product architecture
- `hallucination-guard` = standalone linguistic guard (what's on PyPI)
- `brain-api` = full service (what runs on localhost:8000)
- Separate docs, separate claims
- ~90 minutes

---

### RECOMMENDATION

**Option B + partial C.** Rewrite the README to be honest about what Hallucination Guard v2.0 actually is (linguistic gate + optional facts lookup), remove all fabricated numbers, and clarify that the full brain API is a separate product.

This is our most visible open-source repo. Every false claim on this page destroys credibility with developers who actually read code.

**Your call on scope. All three are scoped above.**
