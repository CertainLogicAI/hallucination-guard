# Architecture Guide

## Design Philosophy

> GBrain captures everything. CertainLogic tells you what's true.

GBrain is a **comprehensive** knowledge graph — it ingests, connects, and surfaces information. CertainLogic is a **discriminating** validation layer — it checks facts before they harden into truth.

They are not competitors. They are complementary layers in a complete knowledge system.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER                                       │
│          (asks question, shares article, mentions entity)         │
└─────────────────────────────┬─────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     GBRAIN SKILLS                                 │
│                                                                   │
│  signal-detector → brain-ops → ingest → enrich → query            │
│                                                                   │
└─────────────────────────────┬─────────────────────────────────────┘
                              │ enrichment content (raw facts)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CYL-VERIFY LAYER                                │
│                       (this integration)                          │
│                                                                   │
│  Step 1: Extract atomic facts from enrichment content             │
│  Step 2: brain_api_query — check against pre-verified facts       │
│  Step 3: Guard — hallucination detector for uncertain facts       │
│  Step 4: Decision — pass | uncertain | reject                      │
│  Step 5: Audit log — append-only, tamper-evident                  │
│                                                                   │
└─────────────────────────────┬─────────────────────────────────────┘
                              │ validated / uncertain / rejected
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GBRAIN WRITE                                 │
│                                                                   │
│  ✓ Confident  → compiled truth (State section)                    │
│  ✗ Uncertain  → timeline only (flagged UNVERIFIED)                │
│  ✗ Rejected   → not written (logged for audit)                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## The Verification Pipeline

### 1. Fact Extraction

Before any external API call or brain write, the enrichment content is decomposed into atomic claims:

**Input:**
```
"Acme AI raised $50M Series B from Sequoia Capital and a16z in March 2026,
led by partner Sarah Chen. The company was founded in 2022 by former
Google researchers and claims 10x performance over GPT-4 on coding tasks."
```

**Extracted facts:**
| # | Claim | Category |
|---|---|---|
| 1 | Acme AI raised $50M | Financial |
| 2 | Acme AI funding round = Series B | Financial |
| 3 | Acme AI investors include Sequoia | Financial |
| 4 | Acme AI investors include a16z | Financial |
| 5 | Acme AI funding led by Sarah Chen | Person |
| 6 | Acme AI founded in 2022 | Company |
| 7 | Acme AI founded by former Google researchers | Company |
| 8 | Acme AI claims 10x performance over GPT-4 | Performance |
| 9 | Acme AI's advantage is in coding tasks | Performance |

### 2. Brain API Query

Each claim is checked against CertainLogic's pre-verified fact database:

```python
result = brain_api_query("Did Acme AI raise $50M?")
# → { "answer": "Yes — Acme AI raised $50M Series B",
#     "confident": true,
#     "method": "facts" }

result = brain_api_query("Does Acme AI claim 10x performance over GPT-4?")
# → { "answer": "Acme AI claims 10x improvement on coding benchmarks",
#     "confident": true,
#     "method": "facts" }
```

**Method types:**
- `facts` — matched in pre-verified database (fastest)
- `cache` — semantic cache hit
- `llm` — LLM checked against source text (slower, costs tokens)
- `uncertain` — no data available

### 3. Hallucination Guard

If the Brain API returns `uncertain`, the Guard runs a deeper check:

```python
guard_result = verify_fact(
    claim="The company claims 10x performance over GPT-4",
    source_text="Acme AI blog post, 2026-03-15"
)
# → { "valid": true/false,
#     "confidence": 0.92,
#     "reason": "Explicitly stated in source" }
```

Guard uses LLM → assertion filter → cache → LLM fallback pipeline.
The filter catches ~40% of hallucinations before they reach the LLM.

### 4. Decision

| Brain API | Guard | Decision | Action |
|---|---|---|---|
| `confident: true` | — | ✅ Pass | Write to compiled truth |
| `uncertain` | `valid: true` | ⚠️ Conditional pass | Write to compiled truth with [Source: Guard validated, low confidence] |
| `uncertain` | `valid: false` | ❌ Rejected | Write to timeline as UNVERIFIED |
| `uncertain` | `valid: null` | ❌ Uncertain | Do not write to compiled truth |

### 5. Audit Logging

Every decision is logged with:

```json
{
  "task_id": "uuid-of-enrichment-job",
  "entity": "Acme AI",
  "fact_hash": "sha256-of-claim-text",
  "claim": "Acme AI raised $50M",
  "result": "validated",
  "method": "facts",
  "brain_api_confidence": 0.98,
  "guard_result": null,
  "source": "TechCrunch, 2026-03-15",
  "timestamp": "2026-04-21T20:07:00Z",
  "agent_id": "gbrain-enrich-v1"
}
```

The log is append-only. Entries can be verified independently by checking the fact hash against the stored claim.

## Data Flow: End-to-End Example

```
1. User shares tweet: "Acme AI just raised $50M from Sequoia"

2. GBrain signal-detector fires
   → Detects: company "Acme AI", person/company "Sequoia", financial event

3. Brain-ops checks existing pages
   → Acme AI page exists? No
   → Create new page via enrich

4. CYL-verify intercepts
   → Extract facts: [Acme raised $50M], [investor: Sequoia]
   → brain_api_query("Did Acme AI raise $50M from Sequoia?")
   → Result: confident=true, method=facts, source=TechCrunch

5. GBrain writes compiled truth
   → State: "Acme AI raised $50M Series B from Sequoia [Source: CertainLogic validated, TechCrunch 2026-03-15]"
   → Timeline: 2026-03-15 | Raised $50M Series B from Sequoia

6. Audit log
   → task_id=..., entity="Acme AI", fact_hash=..., result="validated", method="facts"

7. Backlinks
   → Sequoia page updated: "2026-03-15 | Invested in Acme AI [link]"
```

## Integration Points

### Point 1: Enrich Skill (Primary)

Hooks into `enrich/SKILL.md` before the compiled truth write.

```diff
# In enrich pipeline, before writing to compiled truth:

  facts = extract_atomic_claims(enrichment_content)
  for fact in facts:
+     validation = cyl_verify(fact)
+     if validation.confident:
          write_to_compiled_truth(fact, source=validation.source)
+     else:
+         write_to_timeline(fact, status="UNVERIFIED")
+         log_audit(fact, result="uncertain")
```

### Point 2: Cross-Modal Review (Secondary)

Runs after the existing `cross-modal-review` quality gate.

```
idea-ingest → quality check (cross-modal-review)
                    ↓
            truth check (cyl-verify)
                    ↓
            brain write (enrich or direct)
```

### Point 3: Maintain Skill (Periodic)

Monthly re-validation of compiled truth older than 90 days.

```
maintain skill: sweep compiled truth
  → for each fact older than 90 days:
    → cyl_verify(fact)
    → if result changed: update page, log audit
```

### Point 4: Query Skill (Outbound)

When answering user queries, check CertainLogic before synthesizing.

```
user asks: "Does Acme AI have 10x performance?"
  → query skill searches brain
  → finds claim in compiled truth
  → cyl_verify double-checks before responding
  → responds with confidence level and source
```

## Performance Characteristics

| Metric | GBrain alone | With CYL-verify |
|---|---|---|
| Enrichment latency | ~2-5s | +50-500ms per fact checked |
| Fact accuracy | ~85% (estimated) | ~99% for covered domains |
| Token cost per enrich | ~5K-15K | +0-500 (cache hits are free) |
| Brain storage growth | Raw | Same (unverified facts go to timeline) |
| Audit trail | None | SHA-256 hashed, append-only |

## Security Model

**Fact hash privacy:**
- Brain API sees the query text (necessary for matching)
- GBrain only sees the validation result (not the query)
- Audit log stores SHA-256 hashes, not query text
- CertainLogic does not retain query text after validation

**API key security:**
- Key stored in environment variable or `.env` file
- GBrain agent never sees the key in context
- Key is passed via MCP server config (not LLM tool input)

## Next: Enhanced Audit Integrity (v2.0)

Future versions will explore cryptographic enforcement mechanisms to make audit logs provably tamper-evident, complementing the current append-only logging system.

---

*Architecture version 1.0 | Last updated 2026-04-21*
