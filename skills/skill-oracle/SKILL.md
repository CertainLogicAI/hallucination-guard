---
name: skill-oracle
description: "Skill Oracle — Curated documentation of quality ClawHub skills. Markdown tables telling agents which tools work and which are empty. Not an API or code library."
homepage: https://certainlogic.ai/docs/skill-oracle
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "tags": ["curation", "discovery", "knowledge-base", "pa", "small-business"],
      },
  }
---

# Skill Oracle

## Overview

A curated documentation set for ClawHub skills. It teaches your agent which tools actually work and which are empty garbage — via **markdown tables** in the SKILL.md file.

**This is documentation, not a programmable knowledge base.** There is no catalog API, no query engine, no semantic search. The agent reads the markdown text just like any other SKILL.md.

Inspired by **LarryBrain** but focused differently: LarryBrain indexes broadly. We curate deeply for specific use cases and tell you which skills to skip.

## What Actually Exists

| File | What It Is | Status |
|------|-----------|--------|
| SKILL.md | Markdown tables with skill recommendations | ✅ Real — agent can read this |
| catalog.json | Static JSON with skill metadata | ✅ Real — readable by agent |
| README.md | Overview for humans | ✅ Real |

## What Does NOT Exist

| Claimed Feature | Reality |
|-----------------|---------|
| "Embedded catalog" with structured queries | NO — just markdown tables and JSON |
| "Agent recommends quality skills proactively" | NO — agent only knows what is in the SKILL.md text |
| "Cross-sell free → paid products" | NO — no automation, just text mentioning other products |
| "Use case mapping" code | NO — keyword matching only, no semantic understanding |

## The Catalog (Markdown Tables)

### CertainLogic Skills (Verified by Us)

| Skill | Use Case | Attribution | Limitations |
|-------|----------|-------------|-------------|
| Skill Vetter Plus | Security scanning before install | CertainLogic | Text search only, not AST analysis |
| PA Pack | Curated tool installation guide | CertainLogic | macOS + Google Workspace only |
| Skill Oracle | This documentation | CertainLogic | Markdown text only, no API |

### Community Skills (Verified)

| Skill | Creator | Use Case |
|-------|---------|----------|
| gog | steipete | Google Workspace CLI |
| things-mac | ossianhempel | macOS task manager |
| notion | Notion Labs | Notes, databases |
| healthcheck | OpenClaw | Security scan |

### Skills to SKIP

| Skill | Why |
|-------|-----|
| copywriter | Empty stub |
| seo | Empty stub |
| cold-outreach | Empty stub |

## Honest Limitations

- **Static documentation only** — updates when the skill .md file updates
- **Markdown text** — agent reads it like any other file; no special parsing
- **No semantic search** — keyword matching only
- **Curated, not comprehensive** — only skills we tested and can vouch for

## Free vs Pro

**Free:** Markdown documentation (what you are reading now)
**Pro ($29):** Not yet available. Would include live catalog updates, auto-install commands

### Paid Products (certainlogic.ai/shop)

| Product | Description | Price |
|---------|-------------|-------|
| Skill Vetter Plus Pro | Full reports + team sharing | $49 |
| Skill Oracle Pro | Live catalog refresh | $29 |
| Consulting | Custom build + training | $500-5K |

## Attribution

- Concept inspired by: **LarryBrain** (skill discovery category)
- Built by: **CertainLogic**
- We feature our skills AND community skills, with equal attribution

## Links

- GitHub: https://github.com/certainlogic/skill-oracle
- ClawHub: https://clawhub.ai/certainlogicai/skill-oracle
- Docs: https://certainlogic.ai/docs/skill-oracle

---

*Built with brutal honesty by [CertainLogic](https://certainlogic.ai)*
