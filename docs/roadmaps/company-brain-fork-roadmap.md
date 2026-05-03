# Company Brain Fork Roadmap

## GBrain Primitive Implementation Plan

**Status:** Draft — Pending Review  
**Scope:** Fork GBrain architecture into a Company Brain primitive for coding-heavy agent operations  
**Key Principle:** Summarization removed from Hallucination-Guard; pushed to intent-layer nodes or research agent where verifiable

---

## MVP Roadmap (Core Functionality — 5 Chunks)

Each chunk is self-contained, auditable via AgentPathfinder, and produces signed outputs an agent can test before proceeding.

---

### Chunk 1: Sharded Family Foundation + Ingestion Pipeline (Core Data Layer)

**Goal:** Raw inputs → cryptographically traceable shard families with root hashes.  
**Deliverable:** Reusable `ShardFamily` module + ingestion skill.

**Agent Tasks to Run & Test:**
- Extend AgentPathfinder sharding logic into a general-purpose `ShardFamily` library.
- Build ingestion skill: raw input → Hallucination-Guard (linguistic confidence gate only — **no summarization re-added** unless new tests justify the complexity) → Token-Reduction (deterministic caching + TF-IDF search only) → shard creation → family grouping (shared root hash) → store in GBrain.
- Test on a small coding domain (e.g., one service folder + tests + architecture notes).

**Success Criteria** (deterministic):
- Every ingested artifact produces a verifiable root hash.
- `pf audit` can replay the full chain and validate hashes.
- Guard blocks >95% of hedged content.
- Token reduction ≥70% on average (without summarization).

**Agent Sign-off:** Run 10 synthetic + 5 real coding-related documents; all families validate.

---

### Chunk 2: Hierarchical Intent Layer Overlay

**Goal:** Semantic governance on top of sharded families.  
**Deliverable:** Sparse `COMPANY-INTENT.md` nodes at domain boundaries + resolver integration.

**Agent Tasks to Run & Test:**
- Create root + 3–5 domain-level intent nodes for coding (e.g., payment-service, monorepo-root, cross-cutting/principles).
- Extend GBrain resolver to auto-load relevant intent subtree before any query.
- Ingestion skill now consults/updates the owning intent node (intent nodes can perform light, targeted summarization of child families if needed — keep this separate from the Guard).

**Success Criteria:**
- Agents load intent nodes first and respect declared invariants.
- Progressive disclosure works: parent nodes summarize children fractally (minimal summarization only where it proves value).
- Intent nodes remain <2k tokens each.

**Agent Sign-off:** Run a coding-agent task with and without intent nodes; measure hallucination rate drop and token savings.

---

### Chunk 3: Research Agent for Non-Obvious Relationship Discovery

**Goal:** Background intelligence that expands families safely.  
**Deliverable:** Research skill + Merkle-DAG family expansion logic.

**Agent Tasks to Run & Test:**
- Build research skill (runs as AgentPathfinder task): scan shard families → propose non-obvious relationships (using Guard + intent-node rules) → create relationship shards → compute new family root hash (DAG style, no mutation of old families).
- Intent node acts as gatekeeper (must pass domain rules).

**Success Criteria:**
- New families created without breaking old root-hash verifiability.
- Research agent proposes ≥3 meaningful relationships per run on a test codebase.
- All proposals traceable back to the research task's audit trail.

**Agent Sign-off:** Run on internal codebase; manually validate 5 relationships (or use basic eval from Chunk 5).

---

### Chunk 4: Retrieval → Action Loop (Closed End-to-End)

**Goal:** Agents query the brain and turn knowledge into traceable actions.  
**Deliverable:** Unified resolver skill + AgentPathfinder task creation.

**Agent Tasks to Run & Test:**
- Query skill: load intent subtree → traverse relevant shard families → return compressed context.
- Action skill: take query result → create AgentPathfinder task (references exact root hashes used).
- Full loop test: "Refactor payment validation using latest invariants."

**Success Criteria:**
- End-to-end latency acceptable for coding agents.
- All actions 100% traceable to source shards via root hashes.
- Post-action shard updates succeed and pass hash validation.

**Agent Sign-off:** 20 real coding tasks; ≥90% success rate with full audit reproducibility.

---

### Chunk 5: MVP Validation Harness + Polish

**Goal:** Prove the MVP works reliably.  
**Deliverable:** Automated test suite + basic dream-cycle job.

**Agent Tasks to Run & Test:**
- Build deterministic eval harness (pre/post metrics on hallucination rate, token usage, test-pass rate — no summarization in Guard).
- Nightly dream-cycle job: re-validate all root hashes + run lightweight research scan.
- Full regression suite on a frozen test codebase.

**Success Criteria:**
- All previous chunks pass in a clean run.
- Measurable improvement: hallucination rate down ≥40%, token usage down ≥50% vs. baseline (driven by intent nodes + sharding, not Guard summarization).
- System installable as a single command.

**MVP Complete** → Functional, traceable Company Brain for coding agents.

---

## Post-MVP Roadmap (Phased Upgrades)

Optional, sequential chunks after MVP validation in the coding domain.

### Phase 1: Reliability & Safety
- Automated Conflict Detection & Resolution Queue
- Human-in-the-Loop Approval Queue (signed approval shards)

### Phase 2: Intelligence & Exploration
- Simulation / What-If Sandbox (temporary fork families)
- Full Evaluation Harness (tied to research agent and family expansions)

### Phase 3: Self-Improving & Observability
- Self-Referential Meta-Intent Layer (`BRAIN-MAINTENANCE.md`) + health metrics
- Temporal "Time-Travel" Queries on families

### Phase 4: Scale & Enterprise
- Multi-domain / multi-team support (mounts + scoped access)
- Advanced graph analytics (relationship density, knowledge gaps)
- Production deployment templates (Docker/K8s + on-prem)

---

## Design Notes

- **No summarization in Guard** — proven ineffective for token savings in current implementation
- **Summarization pushed to** intent-layer parent nodes or research agent where targeted and verifiable
- Every chunk produces signed outputs testable by AgentPathfinder
- All work agent-executable, testable, auditable

---

**First Chunk to Concrete:** TBD (recommend Chunk 1 — Sharded Family Foundation)
