# CertainLogic Foundation — Open Source Manifest

**Date:** 2026-05-07 (LOCKED IN)
**Status:** ACTIVE
**Business model:** Open core → community trust → paid verification/co-pilot
**Product name:** CertainLogic Foundation (or "Base OS")
**License:** MIT
**Target communities:** gbrain, gstack (100K+ stars collectively)

## What Was Decided

Anton: "Lock it in. We give a basic intent layer to the gbrain community along with a plugin for our TRE and AgentPathfinder all set to bolt on easy. This forms the CertainLogic Foundation or base OS."

**Verdict:** The CertainLogic Foundation is now the official open source product. It includes the intent layer framework, TRE plugin, and AgentPathfinder tracking layer — all bolted onto gbrain. Proprietary layers (co-pilot agent, crypto verification) remain paid.

## What's in the Foundation (Open Source)

### 1. Intent Layer
- Generic intent classification framework (regex-based, extensible)
- Source boost framework (prefix-based multipliers)
- Python wrapper around gbrain CLI with production hardening
- Placeholder configs for community customization

### 2. TRE Plugin (Token Reduction Engine)
- Query intent caching
- Result caching with invalidation
- Model routing (cheap ↔ expensive by complexity)
- Token savings tracker

### 3. AgentPathfinder (Tracking Layer)
- Structured query logging (JSONL)
- Daily analytics: hit rate, latency, intent distribution
- Self-hosted (logs stay local)
- No crypto signing — structured plaintext tracking only

## What's NOT in Foundation (Proprietary)

- CertainLogic-specific intent values (our 80 regexes)
- CertainLogic-specific boost multipliers (our priorities)
- Cryptographic signing / chain of custody (Verification tier)
- Co-pilot agent personality (Premium tier)

## Three-Tier Model

| Tier | Name | What's Included | Price |
|---|---|---|---|
| 1 | Foundation | Intent framework, TRE, AgentPathfinder tracking | FREE (MIT) |
| 2 | Verification | Foundation + crypto signing + compliance exports | PAID |
| 3 | Co-Pilot | Verification + tuned agent personality + deep integration | PER-SEAT |

## Philosophy

"Open source is distribution, not charity."

The Foundation clears the path. The moat is the co-pilot agent.

## Launch

- **v1.0 target:** After Phase 4 completion (Week 5, ~2026-06-11)
- **Distribution:** PyPI (`pip install certainlogic-foundation`)
- **Community:** GitHub repo under CertainLogicAI org
- **Integration:** One `pip install`, two config lines, bolted onto existing gbrain

## Why This Works

1. **gbrain users need this.** gbrain is a great core but lacks intent awareness, query routing, and agent observability.
2. **Install is trivial.** `pip install` + config. Zero friction.
3. **Upgrade path is clear.** Start tracking (free) → need compliance (paid) → want intelligence (premium).
4. **Moat is protected.** The co-pilot agent (personality, contradiction, self-critique) is the product. Can't be replicated in a weekend.

## Commit Rule

All Foundation code must:
1. Be generic (no CertainLogic-specific values)
2. Include placeholder configs (clearly marked for customization)
3. Be documented (operator's guide entry)
4. Have tests (unit + integration)
5. Be MIT licensed

CertainLogic-specific configs live in a separate private repo, never committed to Foundation.

---

**Decision locked by:** Alex  
**Confirmed by:** Anton  
**Next step:** Build Foundation v1.0 after Phase 4 (Week 5)


---

## Business Model

Anton's go-to-market strategy for CertainLogic:
1. Open source Brain OS upgrades to gbrain/gstack community (100K+ stars collectively)
2. Community adoption — gbrain users get deterministic, auditable agent infrastructure
3. Funnel to paid products:
   - Coding agent middleware (cache warmers, optimization)
   - Data products (pre-built knowledge bases, benchmark datasets)
   - Co-pilot agent (specialized, non-yes-man agent with intent awareness, override handling, and self-critique)
4. Revenue model: Per-seat for the co-pilot agent

This reframes the moat: The crypto layer is not the product — the CO-PILOT AGENT is. The crypto layer is trust infrastructure that makes the paid product credible and defensible.

---

## What Goes Open (Brain OS Template Repository)

| Component | What's Shared | Why |
|---|---|---|
| **Crypto signing mechanism** | The algorithm, RFC, and reference implementation. HMAC signing pattern for agent decisions. How to verify on read. | Trust infrastructure. Community adopts it, CertainLogic is the authoritative source. |
| **brain_wrapper.py template** | Full Python gbrain wrapper with placeholders for intent patterns and boost values. Includes timeout, retry, circuit breaker, error classification. | Community gets a working brain integration out of the box. |
| **Production hardening** | Circuit breaker, input validator, error classifier, CLI pool, metrics, cache layer. All generic. | Operational best practices that anyone can adopt. |
| **Intent classification pattern** | The REGEX-BASED CLASSIFICATION MECHANISM (not the values). Document: "Detect intent from query text using regex patterns, route to appropriate brain search." | Community customizes for their own needs. |
| **Source boost pattern** | The PREFIX-BASED BOOST MECHANISM (not the values). Document: "Higher multipliers for higher-value content types." | Community sets their own priorities. |
| **Sanitized operator's guide** | Full guide with {YOUR_PREFIX}, {YOUR_PRODUCT}, {YOUR_COMPANY} placeholders. | Community gets operational docs. |
| **Integration examples** | How to plug brain queries into agent skills (enhance prompts, fallback logic). | Reduces time-to-value for gbrain developers. |
| **deterministic_brain.py (stripped)** | The structured command schema, hash verification, read path. Signing key derivation and provenance logging removed. | Community gets deterministic brain reads. Audit trail is their responsibility (or they buy from us). |

---

## What Stays Closed (CertainLogic Proprietary)

| Component | Why Closed |
|---|---|
| **CertainLogic-specific intent values** | The 80 regexes encoding our strategic concerns (month-6, trade secret, data flywheel, FaultTrace). Replaceable by community with their own values. Not competitive advantage. |
| **CertainLogic-specific boost multipliers** | The 1.8x, 1.6x, 0.6x values encoding our priorities. Again, template is open; our specific business priorities are private. Not competitive advantage. |
| **The CO-PILOT AGENT** | The tuned, trained, specialized agent that overrides, contradicts, self-critiques, and acts as cofounder. This is the PRODUCT. This is what customers pay per-seat for. |
| **Signing KEY** | The algorithm is open. The master key (CERTAINLOGIC_MASTER_KEY) and derived keys are private. Anyone can implement signing. Only CertainLogic has our specific audit trail. |
| **Provenance logs** | provenance_log.jsonl — the actual signed history of every agent decision. Trade secret. Not shareable. |
| **Audit logs** | audit.jsonl — operational history. Not shareable. |
| **Brain data (443 facts)** | The actual knowledge. Personal and business data. Never shared. |
| **Family taxonomy** | The family/work/strategy/, family/comms/ knowledge organization is Anton-specific. Template is open; our specific content is private. |
| **Agent training/coaching layer** | The protocols, boundaries, and personality that make the agent a cofounder instead of a yes-man. This is the intellectual property. |

---

## Tier Model (Anton's Vision)

### Free Tier: AgentPathfinder-Style Tracking
- Structured logging of every agent query
- Intent classification (what the agent was trying to do)
- Confidence scores (how sure the brain was)
- Basic analytics: hit rate, latency, intent distribution
- Self-hosted: logs stay on your machine
- **No verification: trust but no proof**

### Paid Tier: Regulatory Verification
- Cryptographic chain of custody (HMAC-signed audit trails)
- Tamper-evident provenance logs
- Third-party verifiable decision history
- Compliance exports (SOC2, HIPAA, FDA)
- **For regulated industries that MUST prove chain of custody**

### Premium Tier: Co-Pilot Agent
- Tuned agent personality (override handling, contradiction, self-critique)
- Business-specific intent patterns
- Custom knowledge base and boost tuning
- Deep integration with customer workflows
- Per-seat pricing


---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Large player forks crypto, adds marketing | Brain OS upgrades become commodity | Medium | Move fast. Build community trust now. Co-pilot agent is the moat, not the crypto. |
| Bad actors use open crypto to forge accountability | Reputational damage if "CertainLogic style signing" used in scams | Medium | Public docs emphasize: "This signs but does not verify truth." Truth requires human review + verified knowledge base. |
| Community adopts template but never converts to paid | High support load, low revenue | High | Tagline: "Free brain. Premium mind." The template is functional but basic. Co-pilot is the value. |
| Anton's specific intent/boost values leak in public commits | Strategic priorities exposed | Low | Git pre-commit hook checks for proprietary patterns. CI blocks commits containing CL-specific values. |
| Premature open source — product not ready for community | Bad first impression | Medium | Launch with v1.0 template only after Phase 4 complete (hardened, tested, benchmarked). |

---

## Licensing

Open source template: MIT License (permissive, community-friendly, YC-aligned)
- Maximum adoption, no friction for gbrain devs
- Allows commercial fork with no attribution requirement
- Because premium co-pilot agent is completely separate, MIT does not cannibalize revenue

CertainLogic proprietary: Standard commercial license (TBD)
- Per-seat pricing for co-pilot agent
- Enterprise add-ons (data products, custom training)

---

## Evolution from Original Decision

Original decision: Crypto stays closed indefinitely (2026-05-07 10:47 AM)
Revised decision: Crypto mechanism goes open, key/logs stay closed, co-pilot agent is the product (2026-05-07 11:44 AM)

What changed: Business model clarified — distribution via open source, revenue via premium co-pilot agent.

---

## Commit Rule

All commits to open source template must pass:
1. Git pre-commit hook: No CL-specific intent/boost values in files marked for open source
2. CI check: Assert no CERTAINLOGIC_MASTER_KEY references in template files
3. Code review: Verify crypto_provenance.py is either stripped (template) or private (prod)

---

## Launch Checklist

- [ ] Phase 4 complete (hardened, tested, benchmarked)
- [ ] Template repository created with MIT license
- [ ] All CL-specific values scrubbed from template
- [ ] Signing key derivation removed from deterministic_brain.py (template version)
- [ ] Operator's guide sanitized with placeholders
- [ ] README with clear link to paid co-pilot agent
- [ ] Blog post announcing integration with gbrain
- [ ] Social media posts to gbrain/gstack community
- [ ] ClawHub skill published demonstrating template usage

---

**Decision logged by:** Alex
**Confirmed by:** Anton
**Next review:** After Phase 4 completion or before open source launch
