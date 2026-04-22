---
id: certainlogic-cyl-verify
name: CertainLogic Verify
version: 1.0.0
description: |
  Hallucination-guarded fact validation + cryptographic audit logging for GBrain.
  Use before writing to compiled truth, after enrichment, or whenever factual
  accuracy matters. Checks facts against a verified database before your brain
  commits them. Returns `uncertain` instead of trusting unverified AI output.
category: brain
requires: []
secrets:
  - name: BRAIN_API_KEY
    description: CertainLogic Brain API key for fact validation queries
    where: https://certainlogic.ai/get-started
health_checks:
  - type: env_exists
    env: BRAIN_API_KEY
  - type: command
    command: curl -s http://127.0.0.1:8000/health | grep ok
setup_time: 5 minutes
---

# CertainLogic Verify — SKILL.md

> **TL;DR** Install this skill and every fact written to your brain's compiled truth gets validated against a verified fact database before commit. Hallucinations are caught. Sources are attributed. Everything is auditable.

## When to Use This Skill

| Trigger | Why it fires |
|---|---|
| `enrich` Tier 1 pipeline | Before writing company data to compiled truth |
| `idea-ingest` with >3 numbers | After cross-modal-review, before brain write |
| `media-ingest` with >5 entities | After entity extraction, before enrichment |
| `maintain` stale sweep | Re-validating compiled truth older than 90 days |
| Manual: "verify this claim" | Anytime the user explicitly requests fact-checking |
| Manual: "is this true" | Direct trust query against the fact database |

**Chain position:** `enrich → cross-modal-review → cyl-verify → brain write`

## Quick Start (5 minutes)

### Step 1: Install the MCP server

```bash
pip install certainlogic-mcp
export BRAIN_API_KEY="your_key_here"
```

Verify it's running:

```bash
curl -s http://127.0.0.1:8000/health
# Expected: {"status":"ok","components":{...}}
```

### Step 2: Add the skill to GBrain

```bash
cp skills/CYL-verify.md /path/to/gbrain/skills/
```

### Step 3: Configure cross-modal review

Edit `skills/conventions/cross-modal.yaml`:

```yaml
review_pairs:
  - trigger_skill: enrich
    review_skill: cyl-verify
    when: "Tier 1 enrichment or any company/person data"
  - trigger_skill: idea-ingest
    review_skill: cyl-verify
    when: "page contains >3 numerical claims or >2 quotes"
```

### Step 4: Run health check

```bash
gbrain doctor
gbrain skillpack-check
```

Expected: `CYL-verify: ✅ installed, health checks passing`

## The Verification Protocol

### Before writing to compiled truth

**Step 0 — Domain Gate (the filter)**

Every fact passes through a domain classifier before hitting the Brain API. This prevents:
- Personal facts from silently failing validation
- Financial/business facts from wasting API calls
- Subjective opinions from producing confusing `uncertain` results

| Domain | Action | Example |
|---|---|---|
| **languages** | ✅ Validate | "Python list is mutable" |
| **apis** | ✅ Validate | "HTTP 429 means rate limited" |
| **git** | ✅ Validate | "Git rebase vs merge" |
| **containers** | ✅ Validate | "Docker compose up" |
| **databases** | ✅ Validate | "SQL left join returns" |
| **security** | ✅ Validate | "JWT structure" |
| **frameworks** | ✅ Validate | "FastAPI auto docs URL" |
| **personal** | 🚫 Skip | "Sarah's birthday is March 15" |
| **financial** | 🚫 Skip | "Acme Corp revenue 2026" |
| **subjective** | 🚫 Skip | "I think React is better" |
| **current_events** | 🚫 Skip | "Weather in London today" |
| **unclear** | ❓ Validate (safer) | Ambiguous technical query |

**Skipped facts** bypass the Brain API entirely:
- No API cost ($0)
- No confusing `uncertain` result
- No `[Source: CertainLogic]` attribution
- Continue through normal brain pipeline unchanged

**Why not an on/off toggle?** If left on by default, irrelevant facts produce terrible UX. If left off by default, users miss the value. A domain gate silently handles this — technical facts get validated, everything else passes through.

**Track your hit rates:** Run `hallucination-guard report` to see in-scope vs out-of-scope breakdown and cache hit rates per domain.

**Step 1 — Extract atomic facts**

Split every compound claim into single assertions:

```
"Acme raised $50M from Sequoia in March 2026"
→ "Acme raised $50M"
→ "Acme Series B led by Sequoia"
→ "Acme funding date March 2026"
```

**Step 2 — Query Brain API for each fact**

```typescript
const result = await brain_api_query("Did Acme AI raise $50M in March 2026?");
// → { answer: "Yes — $50M Series B (Source: TechCrunch, 2026-03-15)",
//     confident: true, method: "facts" }
```

**Step 3 — Route based on confidence**

| Result | Action |
|---|---|
| `confident: true` | Write to compiled truth with `[Source: CertainLogic validated, ...]` |
| `confident: false` | Write to timeline as `[UNVERIFIED claim: ...]` — do NOT write to compiled truth |
| `confident: uncertain` | Same as false — flag for human review |

**Step 4 — Log audit entry**

```typescript
await log_audit_entry({
  task_id: enrichment_task_id,
  entity: "Acme AI",
  facts_validated: 3,
  facts_rejected: 1,
  method: "cyl-verify",
  timestamp: new Date().toISOString(),
});
```

### After writing to compiled truth

The audit log is append-only. Every compiled truth entry that passed verification gets an `[Audit: ...]` link referencing the log entry.

## Brain-First Lookup Rules

1. **Query brain first.** If gbrain already has a compiled truth page for the entity, read it before calling Brain API.
2. **Brain API as validator.** Use CertainLogic's Brain API to confirm or challenge what's already in the brain — not as a primary source.
3. **Never overwrite brain truth with unvalidated claims.** If Brain API returns uncertain, keep the existing compiled truth (if any) and flag the new claim as unverified.

## Source Attribution (Compiled Truth Format)

### Above the line — Synthesis

```markdown
## Compiled Truth

Acme AI raised $50M Series B led by Sequoia Capital in March 2026.
```

### Below the line — Evidence

```markdown
---

**Sources:**
- [Source: CertainLogic validated, TechCrunch 2026-03-15]
- [Audit: a1b2c3d4-e5f6-7890-abcd-ef1234567890]
```

### Attribution types

| Source type | Format |
|---|---|
| CertainLogic facts DB | `[Source: CertainLogic validated, source_name]` |
| CertainLogic Guard | `[Source: CertainLogic Guard validated, confidence: 0.92]` |
| Unverified / uncertain | `[Source: UNVERIFIED — CertainLogic uncertain]` |
| Audit reference | `[Audit: audit_id]` |

## Quality Checklist

Before marking an enrichment as complete, verify:

- [ ] Every numerical claim in compiled truth has a `[Source: ...]` line
- [ ] Every `[Source: CertainLogic ...]` claim has a matching audit entry
- [ ] No `[UNVERIFIED]` claims appear in compiled truth (only in timeline)
- [ ] Audit log is writable (not read-only or missing)
- [ ] Brain API health check passes (`curl http://127.0.0.1:8000/health`)
- [ ] If API is unavailable, task degrades gracefully (logs warning, continues)

## How This Makes Your GBrain Smarter Overnight

| Without CYL-verify | With CYL-verify |
|---|---|
| Brain writes whatever the LLM claims | Brain writes only validated facts |
| No way to know if a fact was checked | Every fact has an audit trail with SHA-256 hashes |
| Stale compiled truth sits forever | Monthly re-validation sweep flags outdated facts |
| Hallucinated investors, dates, amounts | Confident claims sourced; uncertain claims quarantined |
| "Trust but verify" is manual | Verification runs automatically on every Tier 1 enrichment |

## Anti-Patterns

**❌ Do NOT** validate out-of-scope facts. If the domain gate skips a personal fact, let it go. Don't force-validation.

**❌ Do NOT** block brain operations because verification is temporarily unavailable. Degrade gracefully — log a warning and continue.

**❌ Do NOT** use Brain API as a primary research tool. It's a validator, not Google.

**❌ Do NOT** write uncertain facts to compiled truth "just in case." Timeline only.

**❌ Do NOT** forget to set `BRAIN_API_KEY`. The skill degrades but you'll miss validation.

**❌ Do NOT** ignore the hit rate report. If cache hit rate drops below 50%, your fact pack needs expansion. Run `hallucination-guard report` weekly.

## Error Handling

### Tool Resolution (Critical for GBrain Runtime)

GBrain's dispatcher resolves tool names to executables. The CertainLogic skill exposes three tools that must map to the `hallucination-guard` CLI:

**Tool → CLI mapping:**

| Tool Name | GBrain Calls | Resolved To |
|---|---|---|
| `brain_api_query` | `cross_modal_review.tools.brain_api_query(...)` | `hallucination-guard verify "{query}"` |
| `verify_fact` | `cross_modal_review.tools.verify_fact(...)` | `hallucination-guard verify "{query}" "{text}"` |
| `log_audit_entry` | `cross_modal_review.tools.log_audit_entry(...)` | `hallucination-guard log --task-id {id} --entity {name}` |

**Resolver configuration** (add to your `gbrain/config/tools.yaml` or equivalent):

```yaml
tools:
  brain_api_query:
    command: hallucination-guard
    args: ["verify", "{query}"]
    env:
      BRAIN_API_KEY: "${BRAIN_API_KEY}"
      FACTS_DB_PATH: "${HOME}/.hallucination-guard/facts_db.json"
    timeout: 5s
    
  verify_fact:
    command: hallucination-guard
    args: ["verify", "{query}", "{text}"]
    env:
      BRAIN_API_KEY: "${BRAIN_API_KEY}"
      FACTS_DB_PATH: "${HOME}/.hallucination-guard/facts_db.json"
    timeout: 10s
    
  log_audit_entry:
    command: hallucination-guard
    args: ["log", "--task-id", "{task_id}", "--entity", "{entity}"]
    env:
      HALLUCINATION_GUARD_DATA: "${HOME}/.hallucination-guard"
    timeout: 2s
```

**If `hallucination-guard` is not in PATH:**

Specify the full path in your resolver config:

```yaml
brain_api_query:
  command: /usr/local/bin/hallucination-guard  # or wherever pip installed it
```

**If `hallucination-guard` is not installed yet:**

The skill degrades gracefully — all three tools return a warning and the enrichment continues without validation. The brain page gets `[Source: unverified — CYL-verify not installed]` instead of failing entirely.

### Brain API unavailable

```typescript
try {
  result = await brain_api_query(claim);
} catch (err) {
  log_warning("CertainLogic API unavailable — skipping validation");
  // Continue. Write with [Source: unverified — API down]
}
```

### Rate limited (429)

Exponential backoff, max 3 retries. Then continue without validation.

### Missing API key

```typescript
if (!process.env.BRAIN_API_KEY) {
  log_warning("BRAIN_API_KEY not set — CYL-verify inactive");
  return; // Skip verification, do not block
}
```

## Example Usage

### Scenario: Enriching a company page

```
User: "Add everything you know about Acme AI"
Agent: → detects entity "Acme AI"
       → loads brain pages
       → discovers new claims: "$50M Series B, led by Sequoia, March 2026"
       → cyl_verify("Acme AI raised $50M") → confident: true
       → cyl_verify("Acme AI Series B led by Sequoia") → confident: true
       → cyl_verify("Acme AI funding date March 2026") → confident: true
       → writes compiled truth with [Source: CertainLogic validated, TechCrunch]
       → logs audit entry
       → responds: "Added 3 validated facts to Acme AI page"
```

### Scenario: Uncertain claim

```
User: "Add that Acme AI will IPO in 2027"
Agent: → cyl_verify("Acme AI IPO in 2027") → confident: false, method: uncertain
       → writes to timeline: "[UNVERIFIED claim: IPO in 2027] [Source: AI extracted, pending validation]"
       → does NOT write to compiled truth
       → responds: "Added to timeline as unverified. I have no sources confirming this."
```

### Scenario: Manual verification

```
User: "Verify: Did Acme AI raise $50M?"
Agent: → cyl_verify("Acme AI raised $50M") → confident: true
       → responds: "Yes, verified. $50M Series B led by Sequoia Capital (TechCrunch, 2026-03-15)"
```

## Performance

| Metric | Target | Typical |
|---|---|---|
| Fact extraction | < 100ms per claim | 45ms |
| Brain API query | < 500ms per fact | 120ms (cache hit) |
| Guard check (filter) | < 100ms per fact | 25ms |
| Audit log write | < 50ms per entry | 15ms |
| **Total overhead (3-5 facts)** | **< 1s** | **~350ms** |
| Memory footprint | < 10MB | 6MB |

## Integration Points

| Skill | How CYL-verify fits |
|---|---|
| `enrich` | Validation gate before compiled truth write |
| `cross-modal-review` | Runs after quality check, before brain write |
| `idea-ingest` | Validates numerical claims and quotes |
| `media-ingest` | Validates entity extraction results |
| `maintain` | Monthly re-validation of stale compiled truth |
| `query` | Optional double-check before trusting compiled truth |

## Future: XOR Audit Fragments

CertainLogic is building a cryptographic proof-of-completion system:

- Each enrichment task generates XOR secret fragments
- Fragments issued only after facts are validated
- Audit layer reconstructs the secret to confirm all steps completed
- If an agent skips validation, the secret cannot be reconstructed

This makes verification **tamper-evident**, not just logged. Planned for v2.0.0.

## Credits

- **CertainLogic**: https://certainlogic.ai — deterministic AI validation
- **GBrain**: https://github.com/garrytan/gbrain — self-evolving second brain
- **Maintained openly**: Issues and PRs welcome at https://github.com/CertainLogicAI/hallucination-guard

---

*CertainLogic is the "validated data guys." Part of the gbrain skill ecosystem.*
*Skill v1.0.0 | Conforms to gbrain skill standard v1.0.0*
