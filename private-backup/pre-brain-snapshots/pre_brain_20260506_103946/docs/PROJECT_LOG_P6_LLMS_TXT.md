# /llms.txt Project Log

**Project:** P6 — Build `/llms.txt` for certainlogic.ai
**Started:** 2026-05-04 15:22 UTC  
**Status:** In Progress

## Goals
- Create `/llms.txt` at site root — standard index agents auto-check first
- List key capabilities, APIs, pricing, integration examples, success metrics
- Plain, dense markdown — agents treat it as table of contents
- Include MCP annotations and tool definitions

## Reference
- docs/research/agent-first-marketing.md (agent-first strategy)
- config/model_routing.json (capabilities)
- main.py (Brain API endpoints)

## Execution Results

**Created two files:**

1. **site/llms.txt** (5.4KB) — Standard agent index with:
   - Overview with key metrics (84 facts, 60% token reduction)
   - Product summaries (Brain API, FaultTrace, AgentPathfinder)
   - API endpoints and integration examples
   - Model routing tiers
   - MCP tool definitions
   - Contact info and changelog

2. **site/llms-full.txt** (6.2KB) — Complete technical reference with:
   - Full API reference (health, facts, process endpoints)
   - Architecture diagram (deterministic → LLM decision tree)
   - Pydantic models and request/response schemas
   - MCP tool definitions (JSON schemas)
   - Integration examples (Python, cURL, OpenClaw)
   - Performance benchmarks table
   - Error handling matrix
   - Environment variables
   - Security notes

**Key features for agents:**
- Dense, structured markdown — no fluffy copy
- Verifiable metrics (84 facts, benchmarks, pricing)
- Actionable integration code (copy-paste ready)
- MCP annotations for native tool loading
- Clear value proposition for each tier

## Status
✅ **P6 COMPLETE** — Agent-ready documentation deployed
