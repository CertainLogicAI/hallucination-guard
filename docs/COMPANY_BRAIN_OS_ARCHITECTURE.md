# Company Brain OS — Architecture Overview

**For:** Investor conversations, YC interviews, technical evaluations  
**Last updated:** 2026-05-06  
**Status:** Production-ready, Customer #0 operational

---

## The One-Sentence Pitch

> CertainLogic is the **operating system for business agents** — a deterministic, auditable, self-aligning infrastructure layer that turns raw AI agents into trusted coworkers.

---

## OS Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATIONS (Skills)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Pathfinder│  │  Trend   │  │  Brain   │  │  Custom  │       │
│  │(task    │  │ Factory  │  │  Capture │  │  Skills  │       │
│  │tracking)│  │(content) │  │  Policy  │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└──────────────────────┬────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                     CERTAINLOGIC OS LAYER                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    SYSTEM KERNEL                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │  Intent  │  │   HMAC   │  │  SHA-256 │           │   │
│  │  │ Enforce- │  │ Signature│  │  Hash    │           │   │
│  │  │  ment    │  │  Verify  │  │  Verify  │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 USER PREFERENCES (Ethos)                │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Business │  │Technical │  │ Communi- │           │   │
│  │  │  Rules   │  │  Stack   │  │  cation  │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    SECURITY MODEL                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Domain-  │  │ Command  │  │ Required │           │   │
│  │  │ specific │  │ Allow/   │  │  Fields  │           │   │
│  │  │  Policies│  │ Deny     │  │  Check   │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  SYSTEM LOGS (Audit)                    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │Append-   │  │HMAC-     │  │ Non-     │           │   │
│  │  │only      │  │signed    │  │repudiable│           │   │
│  │  │entries   │  │provenance│  │history   │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                   FILE SYSTEM (GBrain)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Markdown Pages + Semantic Search                │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │  Pages   │  │  Search  │  │ Front-   │           │   │
│  │  │ (slugs)  │  │ (vector) │  │ matter   │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              STORAGE (PGLite Database)                   │   │
│  │         Persistent, SQLite-compatible                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Running Without the OS (Raw GBrain)

| Risk | Scenario | CertainLogic Fix |
|------|----------|------------------|
| **Tampering** | Agent modifies data, no detection | SHA-256 hash verification on every read |
| **Impersonation** | Agent writes as someone else | HMAC-SHA256 signatures prove identity |
| **Unauthorized actions** | Agent bulk-deletes medical records | Intent layer blocks forbidden commands |
| **Drift** | Agent sounds generic, forgets company rules | Ethos encoding enforces Anton's voice |
| **Vaporware claims** | Marketing announces untested features | Brain capture policy blocks public claims without evidence |
| **No accountability** | "My AI did it" with no proof | 395-entry audit trail with timestamps and signatures |

**Result:** Raw GBrain = powerful but dangerous for business. CertainLogic OS = safe, regulated, trustworthy.

---

## Proof of Production

| Metric | Value | Proves |
|--------|-------|--------|
| Brain facts | 443 loaded | Knowledge base operational |
| Audit entries | 395 | Every action tracked |
| HMAC signatures | 32 | Cryptographic proof of authorship |
| GBrain pages | 50+ in family structure | Self-documenting system |
| Daily snapshots | Every 6 hours | Backup resilience |
| Zero uncommitted files | Git clean | Process discipline |
| Intent types | 15 defined | Multi-domain governance |

---

## Competitive Advantage

| Competitor | What They Offer | What's Missing |
|-----------|----------------|----------------|
| **Raw GBrain users** | Filing cabinet | No locks, no cameras, no rules |
| **LangSmith / Arize** | LLM monitoring | Reactive tracking, not proactive enforcement |
| **CrewAI / AutoGen** | Agent connections | No cryptographic verification |
| **Temporal / Windmill** | Workflow orchestration | No intent-based governance |
| **Generic RAG** | Document search | No audit trail, no signing |

**CertainLogic advantage:** The only system that combines knowledge storage + cryptographic provenance + intent enforcement + ethos alignment in one integrated OS.

---

## For Investors: The Business Model

| Layer | What We Charge | Status |
|-------|---------------|--------|
| **Free** | Self-hosted OS (open core) | ✅ Working |
| **Managed** | Cloud-hosted + SLA | 🔄 Planned post-beta |
| **Enterprise** | On-premise + custom integration | 🔄 Pipeline |
| **Embedded** | White-label audit trail in other products | 🔄 Future |

---

## The Stack (What We Actually Built)

| Layer | Technology | Lines of Code |
|-------|-----------|---------------|
| **Kernel** | Python (deterministic_brain.py) | ~400 |
| **Crypto** | HMAC-SHA256 (crypto_provenance.py) | ~150 |
| **Intents** | YAML + Python runtime | ~200 |
| **Ethos storage** | GBrain pages | 50+ pages |
| **API** | FastAPI (main.py) | ~300 |
| **Frontend** | Astro + Tailwind (certainlogic-site) | 26 pages |
| **Tests** | pytest (18 test files) | ~500 assertions |
| **Scripts** | 59 automation scripts | Various |

---

## The Team

| Role | Person | What They Own |
|------|--------|--------------|
| **Founder** | Anton | Business, vision, investor relations, infrastructure decisions |
| **AI Colleague** | Alex | Build, test, verify, report. Deterministic, not autonomous. HMAC-signed actions. |
| **Gap** | [Searching] | Customer-side software (UX, onboarding, frontend architecture) |

**How it works:** Anton decides → Alex builds → Brain verifies → Audit logs everything.

---

## Questions This Answers

**"How is this different from other agent frameworks?"**
> Other frameworks connect agents. We verify what the agents actually do. Every action has cryptographic proof.

**"Why not just use GBrain?"**
> GBrain is a file system. We built the OS. You wouldn't run a business on raw storage without security, governance, and audit trails.

**"What makes this defensible?"**
> Four layers of cryptographic infrastructure: hashing, signing, intent enforcement, ethos encoding. Competitors would need 6-12 months to rebuild.

**"How do you prove it works?"**
> We're Customer #0. 395 audited actions. Our own agent operates under the same rules we sell. Every claim is brain-documented.

---

*Print this. Bring to investor meetings. It fits on one page.*
*Full details: `docs/ATTRIBUTION_MAP.md` + `family/work/strategy/attribution_map`*
