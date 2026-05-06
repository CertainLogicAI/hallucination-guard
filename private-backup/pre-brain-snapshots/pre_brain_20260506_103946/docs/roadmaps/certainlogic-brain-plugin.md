# CertainLogic Brain — Execution-Layer Plugin Roadmap

**Research Date:** 2026-05-03  
**Status:** Research Complete — Ready for Implementation Review  
**Scope:** Unified OpenClaw plugin combining hallucination-guard, Token Reduction Engine, and Agent Pathfinder

---

## Overview

Converged on a single, unified **execution-layer plugin** called **CertainLogic Brain** (or `certainlogic-brain`). Combines three proven pieces into one lightweight, local-first OpenClaw plugin:

- **hallucination-guard** — output confidence + gating
- **Token Reduction Engine** — smart caching
- **Agent Pathfinder** — cryptographic audit trails down to every tool input/output + real-world effect verification

The plugin covers the **entire execution pipeline** automatically via OpenClaw's runtime hooks (pre-LLM, before/after tool calls, post-LLM, etc.). Creates a tamper-evident trail for every query.

The **knowledge layer** (heavily adapted from Garry Tan's open-source GBrain) will sit on top later for structured memory, fact grounding, and regulated-industry compliance.

**Execution plugin is built first** as the reliable foundation.

---

## MVP: 9 Coding Chunks

Each chunk independently testable. Build and test one at a time.

---

### Chunk 1: Plugin Skeleton & Hook Registration (1–2 hours)

**Goal**: Create a working plugin that registers itself and logs basic events.

**What to code**:
- New directory: `certainlogic-brain/`
- `plugin.json` (manifest with name, version, hooks)
- `index.ts` (or JS) that registers hooks: `message_received`, `before_tool_call`, `after_tool_call`, `llm_output`, etc.
- Simple console log on each hook for now.

**Verification test**:
1. Install with `clawhub install ./certainlogic-brain` (or symlink).
2. Run any query to your agent.
3. Check logs: You should see "CertainLogic Brain: message received", "before tool call", etc.
4. Confirm plugin appears in `openclaw plugins list`.

**Success criteria**: Plugin loads cleanly and fires hooks on every query. No errors.

---

### Chunk 2: Per-Query Trail Initialization (2–3 hours)

**Goal**: Automatically start a cryptographic trail for every new query.

**What to code**:
- In `message_received` hook: Generate unique trail ID + root HMAC hash (query + timestamp).
- Store trail metadata in `~/.certainlogic/brain/trails/{id}.jsonl`.
- Add config flag in `plugin.json` for "enforce on all queries".

**Verification test**:
1. Send a simple query ("What time is it?").
2. Run `claw brain trails list` (stub CLI you'll add later) or manually check the folder.
3. Confirm a new `{id}.jsonl` file exists with root hash and original query.
4. Repeat with 2–3 queries → each gets its own trail.

**Success criteria**: Every query creates an independent, tamper-evident trail file.

---

### Chunk 3: Tool-Level I/O Capture & Crypto Chaining (3–4 hours)

**Goal**: Record every tool call (input + output) and chain the hashes.

**What to code**:
- In `before_tool_call`: Record tool name + sanitized input → update chain hash.
- In `after_tool_call`: Record output + final hash → append to trail file.
- Lightweight real-world check for common tools (e.g., "file exists?" for write tools).

**Verification test**:
1. Send a query that triggers 2+ tools (e.g., "List files in my workspace and read one").
2. Check the trail file: Should show sequential entries with inputs, outputs, and chained hashes.
3. Manually re-hash the chain (simple script) and confirm it matches the final hash.

**Success criteria**: Trail contains exact tool I/O sequence and remains tamper-evident.

---

### Chunk 4: Integrate Hallucination-Guard into Post-LLM Hook (2–3 hours)

**Goal**: Gate LLM outputs with existing guard logic.

**What to code**:
- Reuse hallucination-guard code in `llm_output` hook.
- On low confidence: Redact, retry (once), or flag in trail.
- Log confidence score to the trail.

**Verification test**:
1. Send queries known to cause hedging/hallucinations.
2. Check trail + final response: Low-confidence outputs are flagged or redacted.
3. Confirm high-confidence responses pass through unchanged.

**Success criteria**: Guard runs automatically and affects output only when needed; trail records the score.

---

### Chunk 5: Add Token Reduction Engine (Caching) (3–4 hours)

**Goal**: Cache repeat queries/results and skip LLM when possible.

**What to code**:
- In pre-LLM hook: Semantic hash of query → check cache.
- On hit: Serve cached result + attach cached trail reference.
- On miss (and guard passes): Store result + trail hash in cache.
- Use existing Token Reduction logic (local storage).

**Verification test**:
1. Send identical query twice.
2. Second time should show "0 new LLM tokens used (cache hit)" in response/trail.
3. Change query slightly → cache miss, then repeat exact query again (hit).

**Success criteria**: Caching works, reduces tokens, and links to correct trail.

---

### Chunk 6: Unify All Three Pieces + Config (2 hours)

**Goal**: One plugin that orchestrates everything.

**What to code**:
- Single config file (`brain-config.json`) with toggles for guard, cache, trails.
- Ensure hooks run in correct order: init trail → cache check → LLM (if needed) → guard → tools → finalize trail.
- Add graceful fallback if any piece is disabled.

**Verification test**:
1. Toggle features on/off via config.
2. Run mixed queries (some cached, some with tools, some guarded).
3. Confirm full trail includes guard scores + cache status + tool I/O.

**Success criteria**: All three components work together seamlessly in one plugin.

---

### Chunk 7: Reporting, Summary, & CLI Verify Command (3 hours)

**Goal**: User-friendly output and verification.

**What to code**:
- Post-response hook: Append clean `#CompanyBrain Trail #abc123` summary.
- Implement `claw brain verify <id>` CLI: Re-computes hashes and confirms real-world effects.

**Verification test**:
1. After any query, look for the summary in chat.
2. Run `claw brain verify <id>` → should say "All 4 tool calls verified ✓ Chain intact".
3. Tamper with trail file manually → verify command should detect and report failure.

**Success criteria**: Users see clear, verifiable summaries; CLI proves integrity.

---

### Chunk 8: Packaging, Testing Suite & ClawHub Readiness (2–3 hours)

**Goal**: Make it shippable.

**What to code**:
- Add unit tests for each hook (mock OpenClaw runtime).
- `llms.txt` + README for agent discoverability.
- Package for `clawhub publish`.

**Verification test**:
1. Uninstall/reinstall cleanly.
2. Run full test suite (your agent can generate 10 varied queries).
3. Confirm install works on a fresh OpenClaw instance.

**Success criteria**: Plugin installs via ClawHub and passes end-to-end tests.

---

### Chunk 9: GBrain Adapter Stub (Prep for Knowledge Layer) (1–2 hours)

**Goal**: Light interface for future integration.

**What to code**:
- Simple functions: `gbrain.query(context)`, `gbrain.writeOutcome(trailSummary)`.
- Stub that logs calls (real adapter comes when knowledge layer is ready).

**Verification test**:
1. Enable stub.
2. Run query → logs show "Would query GBrain for X" and "Would write outcome Y".
3. Confirm no breakage.

**Success criteria**: Hooks exist; ready for full GBrain integration later.

---

## Real OpenClaw Plugin System

**Manifest:** `openclaw.plugin.json` (not `plugin.json`)  
**Entry points:** `index.js`, `register.runtime.js`, `setup-api.js`  
**Format:** Node.js module with OpenClaw-specific hooks  
**Install:** `openclaw plugins install ./path --link`  
**Verify:** `openclaw plugins list` and `openclaw plugins doctor`

> ⚠️ **Note:** The research roadmap below uses generic hook names (`message_received`, `before_tool_call`, etc.). Actual OpenClaw hook names may differ. We need to inspect the runtime API (`runtime-api.js` in stock plugins) to determine exact hook surface.

### Quick Discovery Commands

```bash
# List all available hooks in your OpenClaw instance
openclaw plugins inspect <plugin-id> --full

# Read a stock plugin's runtime API for hook patterns
cat /usr/local/lib/node_modules/openclaw/dist/extensions/acpx/runtime-api.js | head -100

# Check what hooks are available
openclaw plugins list --verbose | grep hooks
```

```
User Query → CertainLogic Brain Plugin
├── message_received hook
│   └── Init trail (HMAC root hash)
├── pre-LLM hook
│   └── Check cache (Token Reduction Engine)
│       ├── HIT → Return cached result + trail ref
│       └── MISS → Proceed to LLM
├── llm_output hook
│   └── Hallucination Guard
│       ├── LOW confidence → Flag/redact/retry
│       └── HIGH confidence → Pass through
├── before_tool_call hook
│   └── Record tool + input → update chain hash
├── after_tool_call hook
│   └── Record output + final hash → append trail
└── post-response hook
    └── Append #CompanyBrain Trail #<id> summary
```

**Trail Storage**: `~/.certainlogic/brain/trails/{id}.jsonl`  
**Cache Storage**: `~/.certainlogic/brain/cache/`  
**Config**: `~/.certainlogic/brain/brain-config.json`

---

## Design Principles

- **Local-first** — No external API calls.
- **Deterministic** — HMAC-SHA256 trails, no AI-in-the-loop for verification.
- **Composable** — Each chunk independently testable and usable.
- **Transparent** — Every action logged, every hash verifiable.
- **Graceful degradation** — Any piece can be disabled without breaking the pipeline.

---

## Timeline Estimate

- **2–4 days** of focused agent work
- **Test one chunk per session**
- **Final deliverable**: Production-ready execution primitive after Chunk 8

---

## Next Step

Review this roadmap. Once approved, start **Chunk 1** in a fresh workspace with the official OpenClaw plugin template.
