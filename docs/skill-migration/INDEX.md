# Skill Migration Index

**Status:** In Progress (Phase 4E, 2026-05-07)

## Migration Pattern

Each skill gets a `brain_integration.py` shim that optionally imports `Brain()`.
If brain unavailable, skill runs exactly as before (zero breaking changes).

```python
# In skill's main file
from .brain_integration import get_brain_context

context = get_brain_context()
if context:
    prompt = f"{context}\n\n{legacy_prompt}"
else:
    prompt = legacy_prompt
```

## Skill Status

| # | Skill | Complexity | Brain Use | Status | Commit |
|---|-------|-----------|-----------|--------|--------|
| 1 | `content-engine` | Pilot (done) | strategy() | ✅ Migrated | `4100b85` |
| 2 | `x-api` v1 slots | Low | strategy() messaging | ⏳ Shim ready | — |
| 3 | `x-api` v2 trending | Low | product() positioning | ⏳ Shim ready | — |
| 4 | `market-research-pro` | Medium | search() + metrics() | ⏳ Shim ready | — |
| 5 | `certainlogic-pathfinder` | Medium | query() audit trails | ⏳ Shim ready | — |
| 6 | `seo-audit-pro` | Low | search() SEO knowledge | ⏳ Shim ready | — |
| 7 | `cold-outreach-pro` | Low | strategy() positioning | ⏳ Shim ready | — |
| 8 | `skill-vetter-plus` | Low | strategy() security rules | ⏳ Shim ready | — |
| 9 | `skill-oracle` | Low | search() skill docs | ⏳ Shim ready | — |
| 10 | `skill-guard` | Low | search() bad patterns | ⏳ Shim ready | — |

## Acceptance Criteria (4E)

- [x] All 10 skills can import `brain_wrapper.Brain()` without error
- [ ] All 10 skills fall back to legacy behavior when brain unavailable
- [ ] No skill regression (all existing tests pass)
- [ ] INDEX.md tracked in git

## Integration Guide Per Skill

### Low Complexity (1-line integration)
Replace prompt building with brain-enhanced prompt:
```python
context = get_brain_context_for_skill()
if context:
    prompt = f"Company context:\n{context}\n\n{original_prompt}"
```

### Medium Complexity (3-5 line integration)
Merge brain results with skill output:
```python
brain_data = get_brain_data()
if brain_data.get("confidence", 0) > 0.2:
    result["brain_context"] = brain_data
    result["sources"] = brain_data.get("sources", [])
```

## Rollout Plan

1. **Phase 4E (now):** Shims written, all skills can import Brain()
2. **Phase 4F (Week 4):** Integrate shims into skill runtime (requires skill-specific testing)
3. **Phase 4G (Week 4):** Run full regression test suite
