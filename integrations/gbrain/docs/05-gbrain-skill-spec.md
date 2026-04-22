# GBrain Skill Specification

## Conformance to GBrain Standard

This skill conforms to:
- **GBrain skill format v1.0.0** (frontmatter + markdown body)
- **GBrain manifest schema** (name, path, description)
- **GBrain cross-modal review protocol** (review_pairs, trigger conditions)
- **GBrain citation convention** (`[Source: ...]` inline attribution)
- **GBrain backlinking convention** (bidirectional cross-links)

## Skill Structure

### Frontmatter

```yaml
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
  - brain_api_query
  - verify_fact
  - log_audit_entry
  - get_page
  - put_page
mutating: true
---
```

**Schema compliance:**
- `name`: lowercase, hyphens, max 30 chars ✅ `cyl-verify`
- `version`: semver ✅ `1.0.0`
- `description`: max 500 chars, multiline YAML string ✅
- `triggers`: array of strings ✅ 7 triggers
- `tools`: array of strings, listed in manifest ✅
- `mutating`: boolean ✅ `true` (writes audit log)

### Skill Body

The skill body follows gbrain conventions:
- **Contract section**: What this skill guarantees
- **Philosophy section**: Why this matters
- **Protocol sections**: Step-by-step execution
- **Integration points**: Where it fits in other skills
- **Anti-Patterns**: What NOT to do
- **Credits**: Attribution and links

## Integration with Other GBrain Skills

### Before: signal-detector

**Change:** No direct impact. Signal detector still fires on every message.
CYL-verify hooks in AFTER signal detection, during enrichment.

### Before: brain-ops

**Change:** Brain-ops still does brain-first lookups. CYL-verify adds a
second lookup layer: facts get validated before being written.

### During: enrich

**Change:** Major. The `enrich` skill gains a validation gate before writing
compiled truth.

```diff
# In enrich/SKILL.md, compiled truth section:

## Compiled Truth (State Section)
- Every fact must have an inline citation
+ Every fact must have an inline citation AND pass CYL-verify

- Write the most comprehensive, up-to-date version of truth
+ Write the most comprehensive, up-to-date, VALIDATED version of truth

- If uncertain, write "Unknown" or omit
+ If uncertain, write to timeline as UNVERIFIED; do NOT write to compiled truth
```

### After: cross-modal-review

**Change:** Cross-modal-review checks quality. CYL-verify checks truth.
They run sequentially, not in parallel, to avoid double-writing.

```
idea-ingest → cross-modal-review (quality) → cyl-verify (truth) → brain write
                    ↓                           ↓
               style issues                factual errors
               grammar                    hallucinations
               structure                  contradictions
```

### During: maintain

**Change:** The `maintain` skill gains a periodic re-validation sweep.

```diff
# In maintain/SKILL.md:

## Stale Content Check
- Find pages not updated in 90 days
- Check for outdated information
+ For compiled truth older than 90 days:
+   - cyl_verify(fact)
+   - If result changed: update page, log audit
```

### During: query

**Change:** Optional. The `query` skill can double-check before responding.

```
user asks → query skill searches brain → finds compiled truth
              → optional: cyl_verify(fact)
              → respond with confidence level and validation source
```

## Trigger Resolution

When does CYL-verify fire?

### Automatic Triggers

| Condition | Skill | Action |
|---|---|---|
| `enrich` triggered with Tier 1 | enrich | CYL-verify runs before compiled truth write |
| `idea-ingest` produces page with >3 numbers | idea-ingest | CYL-verify runs after cross-modal-review |
| `media-ingest` enrichment updates >5 entities | media-ingest | CYL-verify runs after entity extraction |
|`maintain` finds compiled truth >90 days old | maintain | CYL-verify runs during stale content sweep |

### Manual Triggers

User can explicitly request verification:

```
User: "Verify that claim about Acme AI"
Agent: → cyl-verify: "Acme AI claim"
     → brain_api_query or Guard
     → Return result with confidence and source
```

## Back-Linking

When CYL-verify validates a fact, it creates an audit log entry. This is NOT a
brain page backlink (different system), but the principle is similar:

```
Every mention of a fact in compiled truth → links to audit log entry
Every audit log entry → references the brain page it validated
```

Format:

```markdown
# Acme AI

## Compiled Truth
Acme AI raised $50M Series B led by Sequoia Capital.
[Source: CertainLogic validated, TechCrunch 2026-03-15]
[Audit: a1b2c3d4-e5f6-7890-abcd-ef1234567890]
```

The `[Audit: ...]` link is not a gbrain native backlink. It's an external
reference to the CertainLogic audit system.

## Citation Convention

CYL-verify extends the gbrain citation standard:

### GBrain Native Citations

| Type | Format |
|---|---|
| User statement | `[Source: User, context, YYYY-MM-DD]` |
| Meeting | `[Source: Meeting "title", YYYY-MM-DD]` |
| Email | `[Source: email from name re: subject, YYYY-MM-DD]` |
| Web | `[Source: publication, URL, YYYY-MM-DD]` |
| Social | `[Source: X/@handle, YYYY-MM-DD](URL)` |

### CYL-verify Extended Citations

| Type | Format |
|---|---|
| CertainLogic facts DB | `[Source: CertainLogic validated, source_name]` |
| CertainLogic Guard | `[Source: CertainLogic Guard validated, confidence: 0.92]` |
| CertainLogic uncertain | `[Source: UNVERIFIED — CertainLogic uncertain]` |
| Audit log | `[Audit: audit_id]` |

## Notability Gate

CYL-verify does NOT override the gbrain notability gate. It operates on facts
that have already passed notability. If a fact is not notable enough for a
brain page, CYL-verify doesn't check it.

## Error Handling

### If CertainLogic API is unavailable

```python
try:
    result = brain_api_query(claim)
except BrainAPIError:
    # Log error
    log_error("CertainLogic API unavailable during enrich")
    # Continue WITHOUT verification
    # Write to compiled truth with [Source: unverified — API down]
```

**Never block brain operations because validation is unavailable.**

### If API key is missing

```python
if not os.getenv("BRAIN_API_KEY"):
    log_warning("BRAIN_API_KEY not set — skipping CertainLogic verification")
    # Continue without validation
```

**Skill degrades gracefully without API key.**

### If rate limited

```python
if response.status_code == 429:
    # Exponential backoff
    time.sleep(2 ** attempt)
    retry
```

**Retry 3 times, then continue without validation.**

## Skill Testing

### Unit Tests

```typescript
// In gbrain's test suite
describe("CYL-verify", () => {
  it("validates a true fact", async () => {
    const result = await cylVerify("Acme AI raised $50M");
    expect(result.confident).toBe(true);
    expect(result.method).toBe("facts");
  });

  it("flags an uncertain fact", async () => {
    const result = await cylVerify("Acme AI will IPO in 2027");
    expect(result.confident).toBe(false);
    expect(result.method).toBe("uncertain");
  });

  it("rejects a false fact", async () => {
    const result = await cylVerify("Acme AI was founded by Elon Musk");
    expect(result.confident).toBe(false);
  });

  it("logs audit entry", async () => {
    const audit = await logAuditEntry({ task_id: "test", ... });
    expect(audit.status).toBe("ok");
  });
});
```

### Integration Tests

```typescript
describe("Enrich + CYL-verify", () => {
  it("writes validated facts to compiled truth", async () => {
    const page = await enrich("Acme AI");
    const truth = page.compiledTruth;
    expect(truth).toContain("[Source: CertainLogic validated");
  });

  it("writes uncertain facts to timeline", async () => {
    const page = await enrich("Mystery Startup");
    const timeline = page.timeline;
    expect(timeline).toContain("[UNVERIFIED");
  });
});
```

## Skill Performance

| Metric | Target |
|---|---|
| Fact extraction time | < 100ms per claim |
| Brain API call time | < 500ms per fact |
| Guard check time | < 100ms per fact (filter) |
| Audit log write time | < 50ms per entry |
| Total overhead per enrichment | < 1s for 3-5 facts |
| Memory footprint | < 10MB (MCP server) |

## Skill Maintenance

### Monthly

- Review audit log for patterns (common uncertain claims)
- Update CertainLogic facts DB with new validated facts
- Check for API changes (version bumps)

### Quarterly

- Run benchmark: validation accuracy vs. manual fact-checking
- Review false positive/negative rates
- Adjust strictness thresholds if needed

### Annually

- Full skill rewrite if gbrain v2 changes conventions
- Evaluate new CertainLogic features (crypto audit chain, etc.)

---

*Skill specification v1.0.0 | Conforms to gbrain skill standard v1.0.0*
