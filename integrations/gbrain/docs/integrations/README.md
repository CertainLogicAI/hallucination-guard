# GBrain Integration Recipe — CertainLogic Verify

**Self-installing recipe for adding hallucination-guarded fact validation to GBrain.**

## What This Does (30 seconds)

Every time GBrain writes to compiled truth, this skill checks the facts against CertainLogic's verified database first. Hallucinations are caught. Sources are attributed. Everything is auditable.

```
Before: Brain writes whatever the LLM claims
After:  Brain writes only validated facts with audit trails
```

## Prerequisites

- GBrain v1.0.0+ installed and running
- `pip` available in your environment
- A CertainLogic Brain API key (free tier: https://certainlogic.ai/get-started)

## Install (5 minutes, copy-paste)

### Step 1: Install the MCP server

```bash
pip install certainlogic-mcp
export BRAIN_API_KEY="your_key_here"
```

Verify it works:

```bash
curl -s http://127.0.0.1:8000/health
# Expected: {"status":"ok","components":{...}}
```

### Step 2: Copy the skill

```bash
# From this repo
cp skills/CYL-verify.md /path/to/gbrain/skills/

# Or download directly
curl -L https://raw.githubusercontent.com/CertainLogicAI/hallucination-guard/main/integrations/gbrain/skills/CYL-verify.md \
  -o /path/to/gbrain/skills/CYL-verify.md
```

### Step 3: Configure cross-modal review

Add to `/path/to/gbrain/skills/conventions/cross-modal.yaml`:

```yaml
review_pairs:
  - trigger_skill: enrich
    review_skill: certainlogic-cyl-verify
    when: "Tier 1 enrichment or any company/person data"
  - trigger_skill: idea-ingest
    review_skill: certainlogic-cyl-verify
    when: "page contains >3 numerical claims or >2 quotes"
```

### Step 4: Verify

```bash
cd /path/to/gbrain
gbrain doctor
gbrain skillpack-check
# Expected: certainlogic-cyl-verify: ✅ installed, health checks passing
```

### Step 5: Test

Trigger an enrichment on a company. Check compiled truth — you should see `[Source: CertainLogic validated, ...]`.

## What You Get

| Feature | Status |
|---|---|
| Fact validation (verified developer facts database) | ✅ |
| Pre-warmed cache (zero cold start) | ✅ |
| Cryptographic audit logging | ✅ |
| Graceful degradation (no blocking on API failure) | ✅ |
| Cross-modal review integration | ✅ |
| MCP server for Claude/Cursor/any agent | ✅ |
| 36 integration tests | ✅ |

## How It Works

```
Enrich triggered
    ↓
Extract atomic facts from content
    ↓
Query CertainLogic Brain API for each fact
    ↓
+ Confident → Write to compiled truth [Source: CertainLogic validated, ...]
- Uncertain → Write to timeline [UNVERIFIED claim: ...]
    ↓
Log audit entry (append-only, SHA-256)
    ↓
Done
```

## Files in This Integration

| File | Purpose |
|---|---|
| `skills/CYL-verify.md` | The skill definition (frontmatter + protocol) |
| `CHANGELOG.md` | Version history |
| `migrations/v1.0.0.md` | Migration from pre-v1.0.0 |
| `RESOLVER.md` | Dispatcher trigger mapping |
| `docs/05-gbrain-skill-spec.md` | Full conformance specification |
| `README.md` | Integration overview |

## Health Checks

Run these anytime:

```bash
gbrain doctor                    # Overall system health
gbrain skillpack-check          # Skill conformance
gbrain integrations             # Show all integration recipes
curl http://127.0.0.1:8000/health  # Brain API status
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `BRAIN_API_KEY not set` | Export your key or the skill degrades gracefully |
| `Brain API returns 404` | MCP server not running. Start with `certainlogic-mcp` |
| `Skill not showing in gbrain` | Check `skills/CYL-verify.md` is in the right directory |
| `Compiled truth no [Source: ...]` | Cross-modal review may not be configured. Check `cross-modal.yaml` |
| `Audit log empty` | Check `~/.certainlogic/` directory exists and is writable |

## Upgrade

To update to the latest version:

```bash
cd /path/to/gbrain
gbrain update certainlogic-cyl-verify
```

Or manually:

```bash
curl -L https://raw.githubusercontent.com/CertainLogicAI/hallucination-guard/main/integrations/gbrain/skills/CYL-verify.md \
  -o /path/to/gbrain/skills/CYL-verify.md
```

See [CHANGELOG.md](CHANGELOG.md) and [migrations/](migrations/) for version-specific upgrade steps.

## Uninstall

```bash
rm /path/to/gbrain/skills/CYL-verify.md
# Remove review_pairs from cross-modal.yaml
```

Your audit log remains at `~/.certainlogic/` if you want to keep it.

## Support

- Issues: https://github.com/CertainLogicAI/hallucination-guard/issues
- Email: ops@certainlogic.ai
- CertainLogic site: https://certainlogic.ai
- GBrain repo: https://github.com/garrytan/gbrain

## License

CertainLogic integration: MIT (the code)
Data products (fact packs): Subject to [EULA](EULA.md) — single-user/org license, no redistribution

---

*Recipe v1.0.0 | Maintained by CertainLogic | Compatible with GBrain v1.0.0+*
