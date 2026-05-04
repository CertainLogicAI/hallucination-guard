---
name: pa-pack
description: "Personal Assistant Pack — Curated toolkit for Google Workspace business owners. Includes installation guides for 5 real tools (gog, things-mac, notion, healthcheck, vetter). Does NOT include automated workflows — it teaches your agent which tools exist and how to install them."
homepage: https://certainlogic.ai/docs/pa-pack
metadata:
  {
    "openclaw":
      {
        "emoji": "📋",
        "tags": ["productivity", "pa", "assistant", "google-workspace", "curation"],
      },
  }
---

# Personal Assistant Pack

## Overview

A curated toolkit for personal assistants supporting Google Workspace business owners. This is a **knowledge pack** — it teaches your agent which tools exist and how to set them up. It does NOT contain working automation.

## What Actually Exists

| Component | What It Is | Status |
|-----------|-----------|--------|
| PA_GUIDE.md | Written documentation of recommended daily workflow | ✅ Real |
| README.md | Installation instructions for each tool | ✅ Real |
| scripts/pa-cli.py | Stub — lists components but each command prints "not implemented" | ⚠️ Not functional |

## What the Agent Can Do

With this pack installed, your agent knows:
- Which 5 tools form the daily workflow (gog, things-mac, notion, healthcheck, vetter)
- What each tool does (Gmail triage, task management, knowledge base, security)
- How to install each tool and what prerequisites are needed
- Who built each tool (attribution)

## What the Agent CANNOT Do

| Claimed Feature | Reality |
|-----------------|---------|
| Automated email triage | NO — agent knows the tools exist but cannot run them |
| Context-aware drafting | NO — pa-cli.py is a stub, no real drafting code |
| Calendar conflict detection | NO — no calendar integration code |
| Deadline tracking | NO — no follow-up automation |

## Prerequisites

- macOS (for Things 3)
- Things 3 app (paid, ~$50)
- Google Workspace account
- Notion account + API key

## Honest Limitations

- **Knowledge only** — teaches tools, does not implement workflows
- **macOS + Google Workspace** — no Outlook/Exchange support
- **Manual setup** — each tool must be installed and configured separately
- **Things 3 is paid** — $50 for the task manager

## Free vs Pro

**Free:** Knowledge pack with installation instructions and workflow guide
**Pro ($49):** Not yet available. Would include working automations, custom workflows, priority support

## Attribution

This pack curates tools by **steipete** (gog), **ossianhempel** (things-mac), **Notion Labs** (notion), **OpenClaw** (healthcheck), and **CertainLogic** (vetter).

## Links

- GitHub: https://github.com/certainlogic/pa-pack
- ClawHub: https://clawhub.ai/certainlogicai/pa-pack
- Docs: https://certainlogic.ai/docs/pa-pack

---

*Built with brutal honesty by [CertainLogic](https://certainlogic.ai)*
