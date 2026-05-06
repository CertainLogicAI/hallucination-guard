# GBrain Integration — Deterministic Company Brain (Chunk 0)

**Date:** 2026-05-05  
**Status:** Repository cloned, architecture mapped, deterministic layer designed  
**Repo:** `company-brain/` (GBrain v0.27.0 fork)  

---

## What We Have

- Full GBrain codebase (62MB, TypeScript, Bun-based)
- 34 skills (Markdown workflows)
- Operations API (~41 operations in `src/core/operations.ts`)
- PGLite engine (embedded Postgres via WASM, zero-config)
- Hybrid search: keyword + vector embeddings + graph ranking
- Brain-first lookup protocol + back-linking (Iron Law)

## What We Add (CertainLogic Deterministic Layer)

### Layer 1: Hash Verification on Every Write
- Every page write computes SHA-256 of content + frontmatter
- Hash stored in `_meta.sha256` and separate `page_hashes` table
- Verification: any read can confirm content hasn't changed
- Audit trail: who/what/when for every mutation

### Layer 2: Intent Node Overlay
- `COMPANY-INTENT.md` files at domain boundaries
- Agents load intent first, then query brain
- Intent declares: allowed operations, forbidden operations, data boundaries
- Prevents agents from operating outside their scope

### Layer 3: Structured Command Interface
- Replace free-form agent prompts with JSON-RPC commands
- Commands validated against schema before execution
- No open-ended "ingest this" — only structured `ingest_article`, `ingest_meeting`, etc.
- Every command HMAC-signed by AgentPathfinder

### Layer 4: Shard Families
- Related pages grouped into "families" with shared root hash
- Family merge = deterministic hash computation
- Family split = Merkle-DAG style (old hash preserved, new branch created)
- Enables time-travel queries: "show me family X as of date Y"

---

## Current GBrain Architecture

```
┌─────────────────────────────────────────┐
│           Agent / CLI / MCP             │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│      src/core/operations.ts             │
│  (41 operations, contract-first)        │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│      src/core/engine.ts                 │
│  (BrainEngine: query, search, crud)     │
└───────┬───────────────┬─────────────────┘
        │               │
   ┌────▼────┐    ┌─────▼─────┐
   │ PGLite  │    │ Postgres  │
   │ (local) │    │ (remote)  │
   └─────────┘    └───────────┘
```

## CertainLogic Overlay (After Integration)

```
┌─────────────────────────────────────────┐
│      AgentPathfinder (HMAC signed)      │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   Structured Command Validator          │
│  (JSON-RPC schema, bounds checking)     │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   Intent Layer (COMPANY-INTENT.md)      │
│  (scope, boundaries, allowed ops)       │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   Deterministic Hash Layer              │
│  (SHA-256 per page, family root hash)   │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         GBrain Core (v0.27)             │
│  ( unchanged — just the engine)         │
└─────────────────────────────────────────┘
```

---

## Files to Read

1. `company-brain/AGENTS.md` — how agents operate GBrain
2. `company-brain/skills/RESOLVER.md` — which skill for which task
3. `company-brain/skills/brain-ops/SKILL.md` — core read/write cycle
4. `company-brain/src/core/operations.ts` — API contract (41 ops)
5. `company-brain/docs/architecture/brains-and-sources.md` — two-axis model

---

## Next Steps

1. **Build deterministic hash wrapper** around `put_page` operation
2. **Create first intent node** for coding domain
3. **Write structured command schema** for brain operations
4. **Integrate with AgentPathfinder** for HMAC-signed commands
5. **Test end-to-end**: command → intent check → hash → write → verify

## Status

✅ Repo cloned and mapped  
⬜ Deterministic hash layer  
⬜ Intent nodes  
⬜ Structured commands  
⬜ AgentPathfinder integration  
