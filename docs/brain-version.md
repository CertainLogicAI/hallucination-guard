# Brain Version Pin — Supply Chain Security

**Date:** 2026-05-07
**gbrain fork commit:** (to be determined — needs git log)
**Divergence documented:** Yes (below)

---

## Origin

The CertainLogic Brain OS is built on a fork of Garry Tan's gbrain:
- Original: https://github.com/garrytan/gbrain (or equivalent)
- Fork date: Approximately 2026-04
- Fork method: Copied into workspace (not git submodule)

---

## Divergence Points

The following files are **CertainLogic-specific additions** not present in upstream gbrain:

### Intent & Search Layer
| File | Added | Purpose |
|---|---|---|
| `src/core/search/certainlogic-boosts.ts` | 2026-05-07 | Source-type boost map for CL priorities |
| `src/core/search/certainlogic-intent.ts` | 2026-05-07 | 80 regex patterns for intent classification |
| `src/core/search/certainlogic-router.ts` | 2026-05-07 | TypeScript router with fallback chain |

### Production Hardening (Phase 4)
| File | Added | Purpose |
|---|---|---|
| `src/core/circuit_breaker.py` | 2026-05-07 | Circuit breaker for query resilience |
| `src/core/error_classifier.py` | 2026-05-07 | Transient vs permanent error classification |
| `src/core/cli_pool.py` | 2026-05-07 | Process pool (anti fork-bomb) |
| `src/core/input_validator.py` | 2026-05-07 | Input validation (security) |
| `src/core/write_guard.py` | 2026-05-07 | Write access control |
| `src/core/log_redactor.py` | 2026-05-07 | Credential redaction in logs |
| `src/core/content_sanitizer.py` | 2026-05-07 | Content sanitization (security) |
| `src/core/metrics.py` | 2026-05-07 | Query metrics and analytics |

### Python Integration Layer
| File | Added | Purpose |
|---|---|---|
| `brain_wrapper.py` | 2026-05-07 | Drop-in Brain() class for skills |
| `certainlogic_router.py` | 2026-05-07 | Python intent router bridge |
| `deterministic_brain.py` | Earlier | Deterministic brain with HMAC signing |
| `crypto_provenance.py` | Earlier | HMAC signing/verification layer |

### Modified Files (Present in gbrain, but changed)
| File | Change | Reason |
|---|---|---|
| `src/core/search/intent.ts` | Modified | autoDetectDetail() checks CL patterns after base |
| `src/core/search/source-boost.ts` | Modified | resolveBoostMap() merges CL boosts |

### Concepts & Knowledge
| File | Added | Purpose |
|---|---|---|
| `concepts/certainlogic-moat-thesis.md` | 2026-05-07 | Strategic thesis (Phase 1) |
| `concepts/certainlogic-strategic-principles.md` | 2026-05-07 | Operative rules (Phase 1) |
| `concepts/brain-os-operators-guide.md` | 2026-05-07 | Ingested into brain |

---

## Version Pin Procedure

### Before pulling upstream changes:

1. **Check upstream changelog** — Review commits since last sync
2. **Test in isolated session** — Spawn subagent with updated gbrain code
3. **Run regression tests** — Verify all CL additions still work
4. **Commit pin update** — Record new upstream commit hash here

### After pulling upstream:

1. **Check for conflicts** — CL-modified files may need manual merge
2. **Verify builds** — `bun run src/cli.ts` must still work
3. **Run test suite** — All tests must pass before committing

---

## Current Status

| Component | Status |
|---|---|
| Upstream sync | Not performed since fork |
| CL modifications | Stable (Phase 4A complete) |
| Known issues | `bun build` fails (Node.js builtins). Use `bun run`. |
| PGLite stability | Working with 443 facts. Monitor for breaking changes in PGLite updates. |

---

## Upgrade Policy

- **Minor upstream fixes:** Apply after 48h review window
- **Major upstream changes:** Test in isolated session before applying
- **Breaking upstream API changes:** Evaluate cost of migration vs. maintaining fork
- **Security patches from upstream:** Apply immediately after verification

---

## Contact

If upstream gbrain introduces breaking changes:
1. Check this document for divergence points
2. Evaluate impact on CL additions
3. Spawn subagent to test compatibility
4. Update this document with new divergence points

**Maintained by:** Alex
**Review cycle:** Monthly, or after any upstream sync
