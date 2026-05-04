# CertainLogic Asset System

**Purpose:** Modular business by design — products serve immediate revenue while building toward Company Brain. This system captures every scoped project, infrastructure component, message insight, and decomposed product part so assets compound instead of scattering.

**Date:** 2026-05-04  
**Status:** v1.0 — implementing now  

---

## Asset Categories

### 1. SCOPED & VIABLE (Retired Projects)
Projects we scoped, validated, but passed on due to timing/strategy. These are fully documented, ready to revive.

| Project | Summary | Why Passed | Revival Trigger | Docs |
|---------|---------|------------|-----------------|------|
| **MCP Server** | Model Context Protocol server for agent tool calling | Market timing / integration complexity | Agent-first marketing demand, OpenClaw MCP adoption | memory/2026-04-18.md |
| **Personal Knowledge Base** | Deterministic cache skill for personal data | Scope shifted to CertainLogic Brain (superset) | Anton personal use need, enterprise KB demand | docs/project-scope-personal-knowledge-base.md |
| **Cryptographic Agent Identity** | Shard-selection identity verification for agents | Hermes benchmark destruction + complexity | Identity becomes industry requirement | docs/ideas/shard-selection-identity.md |
| **Rotating Puzzle Key** | Physical-hardware cryptographic puzzle | Hardware integration not viable yet | Hardware wallet demand, threat model shift | docs/ideas/rotating-puzzle-key.md |
| **EPlan Lite** | Simplified electrical planning tool | Focus on FaultTrace core competency | Customer demand for electrical planning | ideas/eplan-lite.md |
| **Agent Architecture Upgradeable** | Modular agent stack architecture | Built into Pathfinder + ongoing work | New framework demand, research interest | ideas/agent-architecture-upgradeable.md |
| **Decoupled Agent Architecture** | Cost-optimized decoupled agent design | Cost analysis showed partial viability | Scale economics change, cost reduction tech | ideas/decoupled-agent-architecture-costs.md |
| **Model Tiering Strategy** | Multi-model routing optimization | Implemented as part of TRE and routing | New models, pricing changes | ideas/model-tiering.md |
| **LLM Optimization Infrastructure** | Infrastructure for optimizing LLM costs | Partially implemented, not productized | Enterprise demand for LLM cost optimization | ideas/llm-optimization-infrastructure.md |
| **Hallucination Guard** | Deterministic factual validation layer for LLM outputs | Retired April 24 after Hermes destruction; feature not product | Integrate into Brain API as capability; revisit if factual errors spike | `hallucination_detector.py` runtime module |
| **CertainLogic Validator** | AI output verification and quality scoring | Not built as standalone; concept validated | Enterprise/regulated AI validation demand; could be premium feature | Concept only — docs from audits |

**Rule:** When reviving, check original scope against current reality. Update before building. Never rebuild from scratch when scoped docs exist.

---

### 2. PRODUCT DECOMPOSITION (Standalone Parts)
Current products decomposed into potential standalone offerings.

#### FaultTrace
| Component | Standalone Value | Status | Notes |
|-----------|-----------------|--------|-------|
| **L5X Parser** | General Rockwell PLC file parser | ✅ In product, not standalone | Could be OSS library — high developer demand |
| **Schematic Generator** | Auto-generate electrical schematics from logic | ✅ In product | Industry-specific, hard to generalize |
| **Rule Engine** | Pattern-matching safety rule checker | ✅ In product | Could be standalone safety validation tool |
| **Trace Engine** | Signal tracing through ladder logic | ✅ In product | Core differentiator |
| **Audit Engine** | Comprehensive audit report generator | ✅ In product | Could service other industries |
| **Test Generator** | Auto-generate test cases from L5X | ✅ In product | Could serve QA workflows outside PLCs |

#### Pathfinder (AgentPathfinder)
| Component | Standalone Value | Status | Notes |
|-----------|-----------------|--------|-------|
| **Task Engine** | Generic task queue/callback system | ✅ Published | Could be generalized beyond skill dev |
| **Dashboard** | Agent activity visualization | ✅ In product | Generic enough for any agent framework |
| **Tool Audit** | Automated security audit for tools | ✅ In product | Industry-agnostic security scanner |
| **Issuing Layer** | Token/credential issuance | ✅ In product | Broader identity/credential use |
| **New Facts System** | Dynamic fact injection | ✅ In product | Could serve any knowledge system |

#### Brain API (CertainLogic Brain)
| Component | Standalone Value | Status | Notes |
|-----------|-----------------|--------|-------|
| **Token Reduction Engine** | Query optimization/token savings | ✅ In product | SaaS potential: any LLM app |
| **Hybrid Router** | Deterministic + LLM routing | ✅ In product | Core differentiator, don't separate |
| **Hallucination Detector** | Fact-based validation | ✅ In product | Could serve as middleware for any LLM |
| **Memory Search** | Semantic fact retrieval | ✅ In product | Standalone vector search capability |
| **Cache Manager** | LRU cache with TTL | ✅ In product | Generic caching layer |

#### Smart Router
| Component | Standalone Value | Status | Notes |
|-----------|-----------------|--------|-------|
| **Keyword Router** | Simple intent-based routing | ❌ Retired | Too simple — absorbed into Hybrid Router |
| **Productivity Middleware** | Task routing layer | ❌ Retired | Replaced by Pathfinder |

---

### 3. CUSTOM INFRASTRUCTURE (Documented Resources)
Built for CertainLogic, reusable elsewhere.

| Infrastructure | Description | Reuse Potential | Location |
|----------------|-------------|-----------------|----------|
| **Token Reduction Engine** | Reduces LLM tokens via caching/routing | Any LLM-based product | `token_reduction_engine.py` |
| **Brain API** | Deterministic + hybrid AI layer | Core platform, licensed | `main.py` |
| **Cache Builder** | Automated fact extraction + seeding | Any knowledge system | `cache_builder.py` |
| **Coding Query Tracker** | Query categorization + hit rate analytics | Any caching system | `scripts/coding_query_tracker.py` |
| **Memory GC** | Automated archival of old memory files | Any long-running agent | `scripts/memory_gc.py` |
| **Daily/Nightly Summarizers** | Automated log summarization | Any chat-based system | `scripts/daily_summary.py`, `scripts/nightly_summary.py` |
| **Metrics Snapshot** | Cache performance tracking | Any caching system | `scripts/metrics_snapshot.py` |
| **Backup-to-B2** | Backblaze B2 backup automation | Any project needing backups | `scripts/backup-to-b2.sh` |
| **Prepublish Audit** | Skill publish validation | Any ClawHub publisher | `scripts/prepublish_audit.py` |
| **Product/System Health** | Automated health checks | Any service-based product | `scripts/product_health.py`, `scripts/system_health.py` |
| **Agent Learn** | Automated embedding generation | Any agent system | `scripts/agent_learn.py` |
| **Harvest → Extract → Promote** | Fact pipeline from cache to facts DB | Any knowledge system | `scripts/harvest_cache.py`, `scripts/extract_facts.py`, `scripts/promote_facts.py` |
| **Cron Monitoring** | 20+ cron jobs across all functions | Any scheduled task system | Gateway cron system |
| **Gateway Health** | Multi-model failover, rate limiting, cost tracking | Any multi-model system | OpenClaw Gateway |

---

### 4. MESSAGE LOG INSIGHTS (Product & Process Gold)
Extracted from conversation logs — ideas, decisions, improvements that surfaced during chats.

| Date | Insight | Source | Action |
|------|---------|--------|--------|
| 2026-04-25 | Agent identity verification via shard selection — viable but not prioritized | Hermes Phase 1 discussion | Saved as `docs/ideas/shard-selection-identity.md` |
| 2026-04-25 | AgentPathfinder should have upgradeable architecture — built into P1 | P1 scoping | Now in Pathfinder core |
| 2026-04-26 | Decoupled architecture costs viable at scale — revisit when economics change | Cost analysis | Saved in `ideas/` |
| 2026-04-30 | Claim verification policy needed before any marketing claims | Audit discussion | Implemented as `docs/claim-verification-policy.md` |
| 2026-05-01 | No "sandbox" claims until actually built — honest limitations outperform false claims | Audit gate | Enforced as business rule |
| 2026-05-01 | Audit → Scope → Approval → Execution workflow prevents rework | Process improvement | Documented in `AGENTS.md` |
| 2026-05-02 | Scope documents need approval gates — prevents wasted builds | Onboarding Wizard project | Standardized in process |
| 2026-05-03 | "Knowledge is the new oil" — Company Brain as refinery, execution as commodity | Strategic insight | To be captured in `CERTAINLOGIC-PURPOSE.md` |
| 2026-05-03 | Piecemeal > complete — ship one improvement, audit, then next | Optimization discussion | Core philosophy |
| 2026-05-04 | Agent-first marketing — target OpenClaw agents as primary audience | Research analysis | Captured in `docs/research/agent-first-marketing.md` |
| 2026-05-04 | TRE robustness: `try/except ImportError` + graceful fallback | Hallucination detector incident | Pattern to apply elsewhere |
| 2026-05-04 | `hallucination_detector.py` is runtime dependency (not duplicate) | Root cause analysis | Added to `CONVENTIONS.md` as rule |

**Extraction process:** Batch-review conversation logs monthly. Tag insights with #product, #process, #insight. Add to this table. Delete raw logs after extraction to save space.

---

## Asset Compounding System

### How We Compound
1. **Every scoped project gets a document** — even if passed. Docs live in `docs/ideas/` or `ideas/`.
2. **Every product gets decomposed** — annual review: which parts could stand alone?
3. **Every insight gets extracted** — from message logs, memory files, discussions. Tagged and searchable.
4. **Infrastructure gets documented** — what we built, where it lives, how to reuse it.
5. **Quarterly asset audit** — review all four categories. Identify revivals, spin-offs, or kills.

### Tracking
- **This file (`ASSET_SYSTEM.md`)** = master catalog
- **`SKILLS_REGISTRY.md`** = published products
- **`docs/roadmaps/`** = long-term product direction
- **`ideas/`** = scoped/viable projects
- **`docs/research/`** = market insights
- **`memory/`** = daily decisions and insights
- **`docs/CONVENTIONS.md`** = process rules (prevents asset loss)

### Integration Points
- **ClawHub skills** → products → revenue → fund Company Brain
- **Company Brain** → deterministic AI layer → product differentiation
- **Plugin system** → agent-first marketing distribution
- **Documentation** → compound knowledge → faster future builds

---

## Next Actions

| Priority | Action | Owner |
|----------|--------|-------|
| High | Create `CERTAINLOGIC-PURPOSE.md` merging SOUL.md + USER.md + Company Brain thesis | Anton + Alex |
| High | Build `/llms.txt` for `certainlogic.ai` (agent-first marketing) | Alex |
| Medium | Decompose FaultTrace — which components get standalone docs/repos? | Anton decides |
| Medium | Extract message logs (Apr 18-May 4) into structured insights | Alex |
| Medium | Document Brain API as reusable infrastructure (OpenAPI spec) | Alex |
| Low | Quarterly asset audit — schedule first for July 2026 | Anton |
| Low | Revive MCP Server if agent tooling demand spikes | Future |

---

## Rules

1. **Never lose a scoped project.** If we pass, save scope + reason + revival trigger.
2. **Decompose annually.** Every product is a bundle of components. Some deserve to breathe on their own.
3. **Extract insights monthly.** Message logs contain gold. Mine them before deleting.
4. **Document infrastructure.** What we built for ourselves often serves others.
5. **Quarterly audit.** Review all assets. Revive, spin off, or kill. Compounding only works if you revisit.

---

*This system ensures CertainLogic's modular design pays compound interest instead of scattering value into the void.*
