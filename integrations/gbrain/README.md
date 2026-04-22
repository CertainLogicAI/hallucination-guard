# CertainLogic + GBrain Integration

**Validated facts for your self-evolving brain.**

## The Pitch

GBrain captures everything. CertainLogic tells you what's true.

This integration adds deterministic hallucination detection + cryptographic audit logging to gbrain's enrichment pipeline. Every fact written to compiled truth passes through CertainLogic's Guard before your brain commits it.

## Status

| Component | Status | Tests |
|---|---|---|
| SKILL.md (GBrain v1.0.0 format) | ✅ Complete | Schema validated |
| Skill definition | ✅ Complete | Unit + integration |
| MCP server | ✅ Ready | 10/10 passing |
| Integration tests | ✅ 36/36 passing | End-to-end pipeline |
| Audit logging | ✅ SQLite schema + tests | Append-only |
| CHANGELOG.md | ✅ Complete | Version history |
| Migrations | ✅ v1.0.0 guide | Upgrade path documented |
| RESOLVER.md | ✅ Complete | Dispatcher trigger mapping |
| Integration recipe | ✅ Self-installing | 5-minute setup |
| Documentation | ✅ Complete | 6 docs |
| Crypto audit chain | 🔄 Planned v2.0 | AgentPathfinder integration |

## Quick Start (5 minutes)

**Self-installing recipe — copy, paste, done:**

[→ integration recipe](docs/integrations/README.md)

Or the one-liner version:

```bash
pip install certainlogic-mcp && \
cp skills/CYL-verify.md /path/to/gbrain/skills/ && \
gbrain doctor && gbrain skillpack-check
```

## What's in the Box

| File | Purpose |
|---|---|
| `skills/CYL-verify.md` | **The skill** — frontmatter + protocol for GBrain agents |
| `CHANGELOG.md` | Version history (Keep a Changelog format) |
| `migrations/v1.0.0.md` | Upgrade guide from pre-v1.0.0 skill |
| `RESOLVER.md` | Dispatcher trigger mapping and chain position |
| `docs/integrations/README.md` | Self-installing recipe for new users |
| `docs/05-gbrain-skill-spec.md` | Full conformance specification |

## How It Works

```
[Enrich triggered]
    ↓
[Extract atomic facts]
    ↓
[CertainLogic Brain API — validate each fact]
    ↓
  ✅ Confident    → Write compiled truth [Source: CertainLogic validated, ...]
  ❌ Uncertain    → Write timeline [UNVERIFIED claim: ...]
    ↓
[Log audit entry — append-only, SHA-256]
    ↓
[Done]
```

### Chain Position

```
Enrich → Cross-Modal Review → CertainLogic Verify → Brain Write
         (quality check)      (truth check)         (commit)
```

## Performance

| Metric | Target | Typical |
|---|---|---|
| Fact extraction | < 100ms | 45ms |
| Brain API query | < 500ms | 120ms (cache hit) |
| Total overhead (3-5 facts) | < 1s | ~350ms |
| Memory footprint | < 10MB | 6MB |

## Verified Facts Database

333 verified developer facts covering:
- Python (core, advanced, async, testing)
- HTTP / APIs (all status codes, methods, headers)
- Git (branching, rebasing, GitHub Actions)
- Docker (compose, layers, networking)
- SQL (joins, transactions, optimization)
- JavaScript / TypeScript (ES6+, TypeScript strict mode)
- Security (JWT, OAuth, OWASP, TLS 1.3)
- Frameworks (FastAPI, Flask, Django, React, Next.js)
- Cloud (AWS, GCP, Azure basics)

**Free tier:** 100 essential facts. **Paid tier:** All 333 + pre-warmed cache.

## Upgrade Path

See [CHANGELOG.md](CHANGELOG.md) for version history and [migrations/](migrations/) for step-by-step upgrade guides.

### Planned (v2.0.0)

- XOR audit fragments (tamper-evident verification)
- Real-time brain sync (push validated facts immediately)
- Federation (multiple GBrain instances sharing validation state)

## Credits

- **CertainLogic**: https://certainlogic.ai — deterministic AI validation
- **GBrain**: https://github.com/garrytan/gbrain — self-evolving second brain
- Maintained openly at https://github.com/CertainLogicAI/hallucination-guard

## License

Integration code: MIT
Data products: Subject to [EULA](../EULA.md)
