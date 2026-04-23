---
name: cyl-verify
version: 1.0.0
description: |
  CertainLogic integration for gbrain. Hallucination-guarded fact validation
  + cryptographic audit logging. Use when enriching, ingesting, or reviewing
  brain content where factual accuracy matters.
triggers:
  - "verify fact"
  - "validate claim"
  - "check before writing brain"
  - "certainlogic"
  - "guard"
  - "audit fact"
  - "is this true"
tools:
  - web_search
  - brain_api_query  # CertainLogic Brain API tool
  - verify_fact      # Guard validator
  - log_audit_entry  # Audit chain
  - get_page
  - put_page
mutating: true
---

# CertainLogic Verify

## What This Is

An optional validation layer for gbrain that:
1. **Checks facts** against Brain API's hallucination detector before writing to brain
2. **Audits every enrich decision** with a cryptographic log (tamper-evident)
3. **Returns `uncertain`** instead of trusting unverified AI-extracted facts

Use this when factual accuracy matters: company data, financials, legal claims, regulatory info, technical facts, quotations.

## Philosophy

> gbrain captures everything. CertainLogic tells you what's true.
>
> gbrain is *comprehensive*. CertainLogic is *discriminating*.
> They work better together than either alone.

## When to Activate

- Any **Tier 1 enrich** (full pipeline) involving company data
- Any **brain write** with numerical claims, dates, or quotes
- Any **enrich** where source authority is uncertain
- Any fact that contradicts existing brain knowledge
- Before writing to compiled truth (State section)

## How to Register

### Step 1: Install the MCP server

```bash
pip install certainlogic-mcp
export BRAIN_API_KEY=your_key_here
```

Add to your agent's MCP config:

```json
{
  "mcpServers": {
    "gbrain": { "command": "gbrain", "args": ["serve"] },
    "certainlogic": { "command": "certainlogic-mcp" }
  }
}
```

### Step 2: Configure as cross-modal reviewer

In your `skills/conventions/cross-modal.yaml`, add:

```yaml
review_pairs:
  - trigger_skill: enrich
    review_skill: cyl-verify
    when: "Tier 1 enrichment or any company/person data"
  - trigger_skill: idea-ingest
    review_skill: cyl-verify
    when: "page contains >3 numerical claims or >2 quotes"
```

## The Verification Protocol

### Before writing to compiled truth:

**Step 1:** Extract atomic facts from the content
- Each claim gets ONE fact check
- Split: "Acme raised $50M from Sequoia in March 2026"
  → "Acme raised $50M"
  → "Acme funding from Sequoia"
  → "Acme funding date March 2026"

**Step 2:** Call Brain API / Guard for each fact

```
brain_api_query("Did Acme AI raise $50M in March 2026?")
→ { "answer": "Yes — Acme AI raised $50M Series B (Source: TechCrunch, 2026-03-15)",
    "confident": true,
    "method": "facts" }
```

```
brain_api_query("Who invested in Acme AI's Series B?")
→ { "answer": "Sequoia Capital and Andreessen Horowitz co-led",
    "confident": true,
    "method": "facts" }
```

**Step 3:** If `confident: true` → write to brain with `[Source: CertainLogic validated]`

**Step 4:** If `confident: false` → flag as UNVERIFIED, do NOT write to compiled truth
  - Write to timeline: `[UNVERIFIED claim: ...] [Source: AI extracted, pending validation]`
  - Log audit: claim unverified, reason: no source match in fact DB

### After writing to brain:

**Step 5:** Log audit entry

```
log_audit_entry(
  task_id=enrichment_task_id,
  entity="Acme AI",
  facts_validated=3,
  facts_rejected=1,
  method="cyl-verify",
  timestamp=ISO8601
)
```

## Audit Chain — Cryptographic Proof

Every verification decision is logged with:
- **Task ID**: UUID of the enrichment job
- **Entity**: Person/company name
- **Fact hash**: SHA-256 of the claim text
- **Result**: `validated` | `rejected` | `uncertain`
- **Method**: `facts` (cache hit) | `llm` ( LLM-checked ) | `uncertain` (no data)
- **Timestamp**: ISO 8601

The log is append-only. Entries can be verified independently.

## Integration Points

### 1. Enrich skill (before write)

Override the default `enrich` flow:

```diff
  1. Detect entities
  2. Load brain pages
  3. Identify new information
+ 4. CYL-verify: validate each claim
+    - Pass → write compiled truth
+    - Fail → write to timeline as UNVERIFIED
  5. Write it back
```

### 2. Cross-modal review (after write)

After `cross-modal-review` checks quality, `cyl-verify` checks truth:

```
Idea ingest → cross-modal-review (style) → cyl-verify (truth) → brain write
```

### 3. Maintain skill (periodic audit)

Monthly: sweep compiled truth for facts older than 90 days, re-verify.

```
Skill: maintain + cyl-verify
Trigger: monthly cron
Action: Re-validate compiled truth entries, flag stale facts
```

## What You Get

| Without CYL-verify | With CYL-verify |
|---|---|
| "Acme raised $50M" (maybe true?) | "Acme raised $50M" [Source: CertainLogic validated, TechCrunch 2026-03-15] |
| Hallucinated investors | Verified investor list or flagged unverified |
| Stale compiled truth | Periodic re-validation with audit trail |
| No proof claims were checked | Cryptographic log of every verification |

## Cost

Brain API is **free tier**: 3,000 queries/month.
Paid tier: $69 one-time (Coder Pack), $499-$2,499/year (Agent/Enterprise).

Each enrichment typically triggers 3-5 fact checks = negligible cost.

## Credits

- **CertainLogic**: https://certainlogic.ai — deterministic AI validation
- **GBrain**: https://github.com/garrytan/gbrain — self-evolving second brain
- This integration is maintained openly. Issues/PRs welcome.

---

*Part of the gbrain skill ecosystem. CertainLogic is the "validated data guys."*
