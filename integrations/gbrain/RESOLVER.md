# Resolver — certainlogic-cyl-verify

Maps triggers, commands, and chain positions for the CertainLogic Verify skill within the GBrain dispatcher.

## Skill Identity

| Field | Value |
|---|---|
| `id` | `certainlogic-cyl-verify` |
| `name` | CertainLogic Verify |
| `version` | 1.0.0 |
| `category` | brain |
| `priority` | `after=cross-modal-review, before=brain-write` |

## Trigger Resolution

### Automatic Triggers (Dispatcher)

| Trigger Source | Condition | Handler | Priority |
|---|---|---|---|
| `enrich` | `tier == 1` | `certainlogic-cyl-verify` | `after:enrich, before:brain-write` |
| `enrich` | `entity_type in ["company","person","product"]` | `certainlogic-cyl-verify` | `after:enrich, before:brain-write` |
| `idea-ingest` | `page.numbers > 3 or page.quotes > 2` | `certainlogic-cyl-verify` | `after:cross-modal-review, before:brain-write` |
| `media-ingest` | `entities_updated > 5` | `certainlogic-cyl-verify` | `after:entity-extraction, before:brain-write` |
| `maintain` | `compiled_truth.age > 90 days` | `certainlogic-cyl-verify` | `during:maintain-sweep` |

### Manual Triggers (User Intent)

| User Input Pattern | Handler |
|---|---|
| `verify (?:this )?claim` | `certainlogic-cyl-verify` |
| `is this true` | `certainlogic-cyl-verify` |
| `check (?:before writing|before brain)` | `certainlogic-cyl-verify` |
| `certainlogic` | `certainlogic-cyl-verify` |
| `guard (?:this|fact)` | `certainlogic-cyl-verify` |
| `audit (?:this )?fact` | `certainlogic-cyl-verify` |

### Explicit Tool Calls

When an agent explicitly calls these tools, the dispatcher routes to `certainlogic-cyl-verify`:

| Tool | Handler |
|---|---|
| `brain_api_query` | `certainlogic-cyl-verify` |
| `verify_fact` | `certainlogic-cyl-verify` |
| `log_audit_entry` | `certainlogic-cyl-verify` |

## Chain Position

```
[User Input]
    ↓
[Signal Detection]
    ↓
[Intent Classification]
    ↓
[Enrich / Ingest / Maintain]
    ↓
[Cross-Modal Review] ← quality check (style, grammar, structure)
    ↓
[CertainLogic Verify] ← THIS SKILL ← truth check (facts, sources, hallucinations)
    ↓
[Brain Write] ← only if validation passes or degrades gracefully
    ↓
[Response Generation]
```

**Critical:** CYL-verify always runs AFTER cross-modal-review and BEFORE brain-write. Never in parallel — prevents double-writing and race conditions.

## Conflict Resolution

| Scenario | Rule |
|---|---|
| CYL-verify and enrich both triggered | enrich runs first, CYL-verify validates output |
| CYL-verify and cross-modal-review both triggered | cross-modal-review first, CYL-verify second |
| CYL-verify wants to reject, enrich wants to write | CYL-verify wins — writes to timeline, not compiled truth |
| CYL-verify unavailable (API down) | Dispatcher skips CYL-verify, logs warning, continues chain |
| Multiple review skills claim the same trigger | Priority order: cross-modal-review → cyl-verify → any custom |

## Fallback Rules

1. **No API key:** Skill inactive. Dispatcher logs warning. Chain continues without validation.
2. **API timeout:** Retry 3x with exponential backoff. If still failing, log error and continue.
3. **Rate limited (429):** Wait for Retry-After header. If no header, backoff 2^attempt seconds.
4. **Unknown trigger:** If dispatcher cannot map trigger to handler, assume manual intent and route to cyl-verify if the message contains validation keywords.

## Health Check Integration

The dispatcher runs these before activating the skill:

```yaml
health_checks:
  - type: env_exists
    env: BRAIN_API_KEY
    severity: warning  # skill degrades, doesn't block
  - type: command
    command: curl -s http://127.0.0.1:8000/health | grep ok
    severity: warning  # skill degrades if API down
```

If health checks fail, the dispatcher still routes triggers to `certainlogic-cyl-verify` but the skill body skips validation and logs warnings.

## Version Pinning

| Dispatcher Version | Skill Version | Compatibility |
|---|---|---|
| gbrain v1.0.0+ | cyl-verify v1.0.0 | ✅ Fully compatible |
| gbrain v0.9.x | cyl-verify v1.0.0 | ⚠️ Cross-modal review may need manual config |
| gbrain v0.8.x | cyl-verify v1.0.0 | ❌ Frontmatter not supported. Use pre-v1.0.0 skill. |

---

*Resolver v1.0.0 | If triggers don't fire correctly, check `gbrain doctor` and `gbrain skillpack-check`*
