# Business in a Box — Strategy

## Core Thesis

The CertainLogic configuration/methodology is the core asset. Products (Pathfinder, Brain API, FaultTrace) are proof points — demonstrations that the system works. The real product is the **reproducible, deterministic, infrastructure-as-code system** that makes any AI agent safe to operate in production.

> *"Process/configuration itself is most valuable asset. 0→YC in 2 months validates the system."* — May 4, 2026

---

## What "Business in a Box" Means

A turnkey Company Brain deployment that any business can:
1. **Install** — `curl | sh` or Docker container
2. **Populate** — Feed it their documentation, SOPs, preferences, rules
3. **Verify** — Tamper-evident audit trail from day one
4. **Extend** — Add agents, skills, workflows without losing determinism

The buyer gets:
- Deterministic AI layer (GBrain + CertainLogic shim)
- Pre-loaded ethos templates (adaptable to any business)
- Hook system for any agent framework (OpenClaw, Hermes, LangChain, CrewAI)
- Audit trail for every agent decision
- 60-90% LLM cost reduction via cache

---

## Competitive Position

| Competitor | What They Sell | What We Sell |
|-----------|---------------|--------------|
| LangSmith / Arize | LLM monitoring (reactive) | Deterministic execution (proactive) |
| Temporal / Windmill | Workflow orchestration | Verified context layer |
| CrewAI / AutoGen | Agent frameworks | Agent **governance** |
| Generic RAG | Document search | Structured, signed, auditable facts |

Our moat: **We don't just deploy agents. We deploy agents that have provenance.**

---

## Deployment Models

### 1. Self-Hosted (Free)
- Open-source Company Brain core
- Docker compose, local PGLite
- Community support, ClawHub skills

### 2. Managed (Subscription)
- Cloud-hosted Brain API
- Automatic backups, SLAs
- Pro dashboard, team collaboration

### 3. Enterprise (White-glove)
- On-premise deployment
- Custom integrations (ERP, CRM)
- Dedicated support

### 4. Embedded (B2B2C)
- CertainLogic Brain inside other products
- White-labeled audit trail
- Per-seat licensing

---

## Reproducibility

The entire system is reproducible via:

1. **Setup scripts** — `install.sh` clones, configures, starts everything
2. **Declarative config** — JSON/YAML for model routing, auth, caching
3. **Infrastructure as code** — Terraform/ansible for cloud deploy
4. **Digestible container** — Docker image with pre-loaded facts

This means:
- YC demo is a live instance
- Beta users get identical environment
- Enterprise gets air-gapped reproduction
- Hackathon = offline mode with cached facts

---

## Marketing Angle

### For Investors
> "We're not selling AI tools. We're selling deterministic AI infrastructure. Anyone can use LLMs. We're building the layer that makes LLMs safe for critical operations."

### For Developers
> "Install CertainLogic Brain. Define your rules. Watch your agents stop hallucinating."

### For Business Owners
> "Your AI agent now follows your SOPs, your security rules, and your tone. And you can prove it."

---

## Status

| Component | Done | Next |
|-----------|------|------|
| Core deterministic brain | ✅ 27 tests pass | Packaging for install |
| HMAC provenance | ✅ Bolt-on to GBrain | Enterprise key management |
| Intent layer | ✅ 4 ethos domains | Expand to industry templates |
| Beta signup system | ✅ Built, not deployed | Cloudflare deploy |
| Auto-installer | ✅ `company-brain/install.sh` | Test on clean machine |
| Docker container | ❌ Not started | High priority |
| Cloud deploy (managed) | ❌ Not started | Post-beta |
| White-label integration | ❌ Not started | Enterprise pipeline |

---

## Key Decisions

1. **Trade secret over patent** — Business in a Box methodology is trade secret, not patent
2. **Open core, closed enterprise** — Deterministic layer OSS, enterprise features paid
3. **Config as product** — Don't sell features, sell the *system* that generates features

---

## YC Positioning

**What we tell YC:**
We built a deterministic AI layer on top of Garry Tan's GBrain. We encode company knowledge as cryptographically-signed facts. Agents read these facts before acting, producing auditable, verifiable output. We shipped the hackathon weapon (instant scaffold generation), the beta infrastructure (reusable signup system), and the investor pitch — all using our own Company Brain. The configuration that does this is the product. The products are just proof.

---

*This document captures the Business in a Box strategy from discussions May 4–6, 2026.*
*If revised, update this file and commit.*
