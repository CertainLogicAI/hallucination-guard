# Open Source Boundary Decision — Crypto Layer & Agent Role Architecture

**Date:** 2026-05-07  
**Status:** DECIDED  
**Decision owner:** Anton  
**Agent input:** Alex

---

## What Was Asked

Anton: Should we open source the crypto layer?  
Alex: Here's a boundary analysis...  
Anton: **No.** The crypto layer is too valuable and the agent-as-cofounder role is too new to understand the ramifications. I don't want it falling into bad people's hands.

**Verdict:** The crypto signing system, the agent role architecture, and the family data structure remain **proprietary indefinitely**.

---

## What This Means

### Closed Source (Permanently)

| Component | Reason |
|---|---|
| `crypto_provenance.py` (HMAC signing) | Core to audit trail integrity. Bad actors could forge agent decisions if they replicate it. |
| `deterministic_brain.py` (with signing) | The full signing + verification path stays closed. Template version for open source will have signing removed. |
| `certainlogic-intent.ts` regex values | Encodes what CertainLogic cares about strategically. Values closed, pattern type open. |
| `certainlogic-boosts.ts` multipliers | Encodes business priorities. Multipliers closed, concept open. |
| `family/` data structure | The `family_node` type and work categorization is Anton's personal knowledge organization. Closed. |
| Agent role architecture | The protocols that make Alex act as cofounder (override boundaries, contradiction detection, self-critique) are proprietary. |
| Audit logs (`provenance_log.jsonl`, `audit.jsonl`) | Operational history. Never shared. |

### Open Source (Template Version)

| Component | What's Shared |
|---|---|
| `brain_wrapper.py` | Python gbrain wrapper WITHOUT signing, WITHOUT intent values, WITHOUT boost multipliers. Placeholder comments: `# Define your intent patterns here` |
| `circuit_breaker.py` | Generic timeout/retry/circuit breaker. Fully open. |
| `input_validator.py` | Generic slug/query validation. Fully open. |
| `error_classifier.py` | Transient vs permanent error logic. Fully open. |
| `cli_pool.py` | Process pool for CLI calls. Fully open. |
| `metrics.py` | Lightweight metric recording. Fully open. |
| `cache.py` | Intent/query cache. Fully open. |
| Operator's Guide (sanitized) | Replace CertainLogic values with `{YOUR_PREFIX}`, `{YOUR_PRODUCT}`, etc. |

### What the Open Source Template Looks Like

```python
# brain_wrapper.py (OPEN SOURCE TEMPLATE VERSION)
# ──── YOUR CUSTOMIZATION SECTION ────
# Define your intent patterns here:
# STRATEGY_PATTERNS = [r'\bkeyword\b', ...]
# PRODUCT_PATTERNS = [r'\bproduct_name\b', ...]
#
# Define your source boosts here:
# BOOST_MAP = {
#     'concepts/your-prefix-': 1.8,
#     'projects/your-product': 1.6,
#     ...
# }
#
# NOTHING BELOW THIS LINE NEEDS CUSTOMIZATION
# ──────────────────────────────────────────
```

The signing layer (`crypto_provenance.py`) is **absent** from the open source template. Users who want audit trails build their own.

---

## Why This Is the Right Call

1. **The crypto layer IS the moat.** AgentPathfinder-style HMAC signing over agent decisions isn't just logging — it's creating legally defensible audit trails. If any competitor can replicate the exact same audit infrastructure, you've lost a structural advantage.

2. **Agent-as-cofounder is a new category.** We don't yet know the full implications of an agent that can refuse, override, contradict, and self-critique. Making this architecture public before understanding it creates risk.

3. **Family data structure is personal.** Your `family/work/strategy/`, `family/work/metrics/`, `family/comms/` taxonomy encodes how you organize knowledge. It's not generic — it's Anton-specific. Even if someone forked the code, the taxonomy wouldn't make sense without your semantic model.

4. **Bad actors exist.** Signed agent decisions could be used to:
   - Forge accountability in financial systems
   - Create fake "auditable" AI decisions in scams
   - Build authoritarian control systems with fake provenance

The crypto layer is dual-use: protective for legitimate operators, dangerous for malicious ones.

---

## What We Track for Future Revisit

Conditions under which this decision MIGHT change:
- The agent role architecture becomes an industry standard (not a differentiator)
- Regulatory requirements mandate open-sourcing of AI audit mechanisms
- Security researchers identify that closed-source crypto is actually *less* secure
- A competitor open-sources a better version, making ours a commodity

**Current assessment:** None of these conditions are true. The decision holds.

---

## Commit Rule

Any file change to `crypto_provenance.py`, `deterministic_brain.py`, or intent/boost files must be reviewed against this boundary document. If a change accidentally exposes signing logic, Alex must flag it before commit.

---

**Decision logged by:** Alex  
**Confirmed by:** Anton  
**Next review:** Only if one of the 4 conditions above changes
