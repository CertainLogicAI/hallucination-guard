# CertainLogic + GBrain Integration

**Validated facts for your self-evolving brain.**

## The Pitch

Gbrain captures everything. CertainLogic tells you what's true.

This integration adds deterministic hallucination detection + cryptographic audit logging to gbrain's enrichment pipeline. Every fact written to compiled truth passes through CertainLogic's Guard before your brain commits it.

## Status

| Component | Status | Tests |
|---|---|---|
| Skill definition | ✅ Complete | Unit + integration |
| MCP server | ✅ Ready | 10/10 passing |
| Integration tests | ✅ 36/36 passing | End-to-end pipeline |
| Audit logging | ✅ SQLite schema + tests | Append-only |
| Documentation | ✅ Complete | 5 docs |
| Crypto audit chain | 🔄 Planned v2.0 | AgentPathfinder integration |

## Quick Start

### 1. Install the MCP server

```bash
pip install certainlogic-mcp
export BRAIN_API_KEY=your_key_here
```

### 2. Configure Your Agent

```json
{
  "mcpServers": {
    "gbrain": { "command": "gbrain", "args": ["serve"] },
    "certainlogic": { "command": "certainlogic-mcp" }
  }
}
```

### 3. Add the Skill

```bash
cp skills/CYL-verify.md /path/to/gbrain/skills/
```

### 4. Configure Cross-Modal Review

Edit `gbrain/skills/conventions/cross-modal.yaml`:

```yaml
review_pairs:
  - trigger_skill: enrich
    review_skill: cyl-verify
    when: "Tier 1 enrichment or any company/person data"
  - trigger_skill: idea-ingest
    review_skill: cyl-verify
    when: "page contains >3 numerical claims or >2 quotes"
```

## Running Tests

```bash
cd opensource/gbrain-integration
pytest tests/test_integration.py -v
```

**Expected: 36 passed**

## What's Included

| File | Purpose |
|---|---|
| `skills/CYL-verify.md` | GBrain skill spec (frontmatter + full body) |
| `docs/01-installation.md` | Step-by-step setup |
| `docs/02-architecture.md` | Pipeline design, security model |
| `docs/03-usage.md` | 7 real-world examples |
| `docs/04-api-reference.md` | MCP tools, HTTP endpoints, rate limits |
| `docs/05-gbrain-skill-spec.md` | GBrain conformance, trigger resolution |
| `tests/test_integration.py` | 36 end-to-end tests |
| `CONTRIBUTING.md` | PR process, CoC |

## Architecture

```
Inbound signal
    ↓
GBrain enrich / idea-ingest
    ↓
Brain-first lookup (existing pages)
    ↓
CYL-verify:
  1. Extract atomic facts
  2. brain_api_query (pre-verified facts DB)
  3. Guard (hallucination detector)
  4. Decision: validated | uncertain | rejected
  5. Audit log (SHA-256 hashed, append-only)
    ↓
Write: compiled truth (✓) or timeline (✗)
```

## When to Use

- **Enriching** person/company pages with external data
- **Ingesting** articles with numerical claims
- **Fact-checking** user quotes before brain write
- **Due diligence** before investor meetings
- **Maintenance** monthly re-validation sweep

## Cost

- **Free tier**: 3,000 queries/month — enough for most personal brains
- **Paid tier**: From $69 one-time (Coder Pack)
- Each enrichment: 3-5 fact checks = negligible cost
- Cache hits: free, ~50ms

## Security

- API key in env var only — never in LLM context
- Query text hashed (SHA-256) for telemetry
- Audit log: append-only, no PII
- CertainLogic does not retain query text after validation

## Credits

- **Integration**: CertainLogic (https://certainlogic.ai)
- **GBrain**: Garry Tan (https://github.com/garrytan/gbrain)
- **GStack**: Garry Tan (https://github.com/garrytan/gstack)
- **License**: MIT

## Integration for GStack Users

Same integration works for gstack. The MCP server adds `brain_api_query` to Claude Code's tool set, so every gstack-powered agent gets CertainLogic validation alongside the 23 gstack tools.

---

*CertainLogic is the "validated data guys" for the gbrain/gstack community.*
