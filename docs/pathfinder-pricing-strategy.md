# AgentPathfinder Pricing Strategy — Recommendation

**Date:** 2026-04-25
**Competitive analysis complete.**

---

## Competitive Landscape

| Competitor | Category | Free Tier | Entry Paid | What They Do | What's Missing |
|------------|----------|-----------|------------|--------------|----------------|
| **Temporal** | Workflow Orchestration | $1K credits | $100/mo Essentials | Deterministic workflows, visibility, retries | No cryptographic sharding |
| **Orkes Conductor** | Workflow Orchestration | Dev Playground | Enterprise custom | Managed Conductor (Confluent backed) | No sharding, no agent auth |
| **CrewAI AMP** | Agent Orchestration | 50 execs/mo | $0.50/execution | Multi-agent workflows, studio | No audit integrity, no shard vault |
| **Arize AX** | AI Observability | 25K spans/mo | $50/mo Pro | LLM tracing, evals, hallucination scores | Not orchestration — just monitoring |
| **LangSmith** | AI Observability | Limited traces | $39/mo+ | LangChain tracing, testing | No task decomposition or security |

**Key insight:** Nobody offers cryptographic task sharding. Temporal is deterministic but plaintext. CrewAI is agentic but no audit integrity. Arize watches but doesn't protect.

---

## Recommended Pricing Tiers

### Free — "Pathfinder Core"
**$0 / forever**

- ✅ Full sharding engine (local vault)
- ✅ CLI with visual confirmations (emojis)
- ✅ Task creation, execution, reconstruction
- ✅ Basic audit trail (local JSONL)
- ✅ Agent registration (up to 2 agents)
- ✅ 29-test core suite included

**Positioning:** "See the product work. Get value immediately."

---

### Pro — "Pathfinder Dashboard"
**$29 / month**

Everything in Free, plus:
- 🖥️ **Unified web dashboard** (tasks + brain stats)
- 📊 CSV/JSON report exports
- 🔑 Multi-agent coordination (up to 10 agents)
- 📈 90-day audit retention
- 📧 Email support
- 🔄 Basic webhook notifications (task start/complete)

**Positioning:** "Track everything. Prove it happened."

**Comp anchors:** Arize AX Pro ($50/mo, 50K spans). We're $29/mo for deterministic task security + observability. Temporal Essentials ($100/mo) has no sharding. Cheaper, more defensible.

**Target:** Solo builders, indie hackers, small dev teams who need audit-proof agent workflows.

---

### Business — "Pathfinder Teams"
**$79 / month**

Everything in Pro, plus:
- 👥 Unlimited agents
- ☁️ Remote vault (S3, B2, MinIO compatible)
- 🔗 Advanced webhooks (per-step, Slack/Teams)
- 🏢 Team access controls
- 🧪 API rate limits per team member
- 💬 Priority support (Discord, 24-hr response)
- 📋 Advanced audit search (filter by date, agent, task)

**Positioning:** "Scale secure agent workflows across your team."

**Comp anchors:** Temporal Business ($500/mo). We're 6× cheaper with better security primitives. CrewAI Enterprise (custom, likely $500+). We have audit integrity they don't.

**Target:** Agencies, SaaS teams, compliance-conscious startups.

---

### Enterprise — "Pathfinder Vault"
**$299+ / month (custom)**

Everything in Business, plus:
- 🏢 On-prem / air-gapped deployment
- 🔒 Custom vault backends (HashiCorp Vault, AWS KMS, Azure Key Vault)
- 🛡️ SSO/SAML (Okta, MS Entra)
- 📜 SOC 2 / HIPAA / FedRAMP documentation
- ⚡ Dedicated onboarding engineer
- 🎯 Custom feature development (quarterly)
- 📞 24/7 phone escalation

**Positioning:** "Bank-grade cryptographic orchestration for regulated industries."

**Comp anchors:** Temporal Enterprise (custom, starts at $2K+/mo with support). Orkes Enterprise (custom). We're priced aggressively for the unique value of cryptographic sharding + full audit integrity.

**Target:** Healthcare, fintech, government, anyone handling PII or audit-sensitive automation.

---

## Pricing Psychology

| Principle | How we apply it |
|-----------|----------------|
| **Anchor high, sell Pro** | Enterprise at $299 makes $79 look cheap, $29 look free |
| **Free proves value** | Emojis + CLI = immediate visual confirmation = "it works" |
| **Dashboard = upgrade hook** | Free shows tasks work → user wants to track 50 agents → upgrade |
| **Security creates urgency** | "Your agent workflows are plain text. We shard them cryptographically." |
| **Per-agent is pain** | Unlimited agents in Business instead of per-seat pricing = easier upsell |

---

## Revenue Projections (Conservative)

| Tier | Price | Est. Users (mo 12) | MRR |
|------|-------|-------------------|-----|
| Free | $0 | 500+ (lead gen) | — |
| Pro | $29 | 40 | $1,160 |
| Business | $79 | 12 | $948 |
| Enterprise | $299+ | 2 | $598+ |
| **Total MRR mo 12** | | | **$2,706+** |

Conservative because you're solo and focus is build, not sales. If you add a landing page + Stripe checkout + X/email funnel, Pro could hit 200+ users.

---

## What to Ship First

1. **Free + Pro ($29)** — this is the funnel
2. **Stripe checkout** — 2 hours to wire
3. **Landing page** — CertainLogic.ai/Pathfinder
4. **Business ($79)** — launch after you have 20 Pro users (proves demand)
5. **Enterprise ($299)** — sales-led, don't build features until customer commits

---

## Bottom Line

**Recommended:**
- Skill: **Free** (emoji confirmations, CLI, local vault)
- Dashboard + Reports: **$29/mo Pro**
- Teams + Remote vault: **$79/mo Business**
- Regulated/air-gapped: **$299+/mo Enterprise**

This undercuts Temporal by 3-6× while delivering a capability they don't have (cryptographic sharding). It validates at $29 — low enough to impulse buy, high enough to respect.
