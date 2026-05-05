# GBrain Exploration Report

**Date:** 2026-05-05  
**Repository:** https://github.com/garrytan/gbrain  
**Version:** v0.27.0  
**Size:** 82MB  
**Production scale:** 17,888 pages, 4,383 people, 723 companies (Garry's instance)

---

## What It Is

GBrain is a **long-term persistent memory system for AI agents** — exactly the knowledge layer Anton needs. Built by Garry Tan (YC President/CEO) for his own production OpenClaw and Hermes deployments.

**Core loop:**
1. Agent sees something (meeting, email, tweet, idea)
2. Signal detector extracts entities/concepts
3. Brain-ops searches existing knowledge
4. Creates/updates Markdown pages with typed links (works_at, invested_in, attended)
5. Overnight "dream cycle" consolidates, deduplicates, fixes citations

---

## Architecture

| Component | What It Does | CertainLogic Parallel |
|-----------|-------------|----------------------|
| **Storage** | PGLite (embedded Postgres via WASM) or Postgres + pgvector | Our `facts_db.json` + `memory/` |
| **Search** | Hybrid: keyword + vector embeddings + graph ranking + backlinks | Brain API `memory_search` |
| **Graph** | Zero-LLM typed links between entities | Intent layer + shard families |
| **Skills** | 34 Markdown workflow files agents follow | Our `skills/` + `SKILL.md` pattern |
| **Integration** | MCP (Model Context Protocol) — plugs into Claude, OpenClaw, etc. | Our `main.py` Brain API |
| **Cron** | 21 autonomous jobs running overnight | Our heartbeat + cron system |

**Two axes (key concept):**
- **Brain** = database (which DB: host, mounts, team brains)
- **Source** = repo within that DB (wiki, gstack, openclaw)
- Queries route on both axes — prevents cross-contamination

---

## Key Strengths

1. **Production-tested** — Garry runs his entire YC operation on this. Not theoretical.
2. **Benchmarked** — P@5 49.1%, R@5 97.9% on 240-page corpus. Graph layer carries +31.4 points over vector-only.
3. **Agent-native design** — 30-min agent-led install, agent reads skills, agent operates it.
4. **Skills are code** — 34 Markdown skills = determinism. Not prompt engineering.
5. **Eval system** — `gbrain eval export` + `gbrain eval replay` for regression testing.

---

## Integration Path for CertainLogic (5 chunks)

**Chunk 0 (today):** Fork/extend GBrain codebase into `company-brain/` workspace
**Chunk 1:** Add deterministic layer — hash verification on every page write, sharded families with root hashes
**Chunk 2:** Overlay intent layer — `COMPANY-INTENT.md` nodes at domain boundaries, resolver integration
**Chunk 3:** Wire AgentPathfinder — every brain-ops call HMAC-signed, every action auditable
**Chunk 4:** Business adaptation — skills for business workflows (not personal knowledge), compliance exports, enterprise auth

---

## Files Anton Should Read

1. `README.md` — vision + install
2. `AGENTS.md` — how agents operate it
3. `skills/RESOLVER.md` — dispatch table (which skill for which task)
4. `docs/architecture/brains-and-sources.md` — two-axis mental model
5. `CLAUDE.md` — architecture for contributors

---

## Verdict

**This is the foundation.** Not a competitor — the starting point. YC President open-sourced his production brain. We extend it with determinism, audit trails, and business logic. That's the CertainLogic upgrade.

**Status:** Ready to fork. Recommend cloning into `workspace/company-brain/` as subdirectory or submodule. Keep upstream sync for improvements.
