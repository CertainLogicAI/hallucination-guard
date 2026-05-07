# CertainLogic Foundation — Open Source Manifest

**Date:** 2026-05-07  
**Status:** LOCKED IN  
**Product name:** CertainLogic Foundation (or "Base OS")  
**License:** MIT  
**Target communities:** gbrain, gstack

---

## What Is CertainLogic Foundation?

A bolt-on deterministic layer for gbrain users. It adds three primitives that gbrain doesn't include out of the box:

1. **Intent Layer** — Classify queries into business-relevant categories, route to appropriate brain search with source boosting
2. **TRE Plugin** — Token Reduction Engine (caching + routing layer for agent queries)
3. **AgentPathfinder** — Structured tracking layer for agent decisions (query logging, metrics, basic analytics)

**It's not replacing gbrain.** It's extending gbrain. One `pip install`, two config lines, and any gbrain user gets deterministic query routing + decision tracking.

---

## What's Included (Open Source)

### 1. Intent Layer (Base)

```python
from certainlogic_foundation import Brain

brain = Brain()
result = brain.query("what is our moat strategy")
# Returns: answer, sources, confidence, intent, detailed routing metadata
```

**Includes:**
- Generic intent classification framework (regex-based, extensible)
- Source boost framework (prefix-based multipliers)
- Python wrapper around gbrain CLI
- Production hardening: timeout, retry, circuit breaker, error classification, CLI process pool
- Placeholder configs: fill in your own intent patterns and boost values

**What you customize:**
- Your intent regexes (what does YOUR business care about?)
- Your boost multipliers (what content types are most valuable to YOU?)
- Your slug prefixes (how do YOU organize knowledge?)

### 2. TRE Plugin (Token Reduction Engine)

```python
from certainlogic_foundation.tre import TokenReductionEngine

tre = TokenReductionEngine()
result = tre.process(user_query)
# Checks local cache first, routes to appropriate model, logs token savings
```

**Includes:**
- Query intent caching (avoid re-classifying common queries)
- Result caching with automatic invalidation
- Model routing (cheap model for simple queries, expensive model for complex)
- Token savings tracker (how many tokens did you save this month?)

**What you customize:**
- Cache TTLs
- Model routing rules
- Cost thresholds

### 3. AgentPathfinder (Tracking Layer)

```python
from certainlogic_foundation.pathfinder import AgentPathfinder

pf = AgentPathfinder()
pf.log_decision(agent_action="query", query="moat", result=brain_result)
# Logs: timestamp, action, intent, confidence, latency
```

**Includes:**
- Structured query logging (JSONL, one entry per agent action)
- Daily analytics: hit rate, latency, intent distribution, token savings
- Exportable metrics (CSV, JSON)
- Self-hosted: all logs stay on YOUR machine

**What you DON'T get (upgrade to Verification Tier):**
- No cryptographic signing
- No tamper-evident audit trail
- No chain of custody
- No compliance exports

---

## What's NOT Included (CertainLogic Proprietary)

| Component | Where It Lives | Why Closed |
|---|---|---|
| **CertainLogic-specific intent values** | Our private config | Encodes our strategic priorities |
| **CertainLogic boost multipliers** | Our private config | Encodes our business priorities |
| **Cryptographic signing** | `crypto_provenance.py` (closed) | Regulatory verification — paid tier |
| **Chain of custody** | `provenance_log.jsonl` (closed) | Audit trail integrity — paid tier |
| **Co-pilot agent** | CertainLogic Agent product | The proprietary agent personality |

---

## The Three-Tier Model

### Foundation (Free, MIT License)
> *"Every agent needs a brain. This is the foundation."*

- Intent classification framework
- Source boost framework
- TRE caching/routing
- AgentPathfinder structured tracking
- Basic analytics

**Best for:** Solo devs, startups, small teams, anyone using gbrain who wants deterministic agent infrastructure.

### Verification (Paid, Commercial License)
> *"If regulators demand proof, this is the proof."*

- Everything in Foundation
- **PLUS:** HMAC-signed audit trails
- **PLUS:** Tamper-evident provenance logs
- **PLUS:** Chain of custody verification
- **PLUS:** Compliance exports (SOC2, HIPAA, FDA-ready)

**Best for:** Regulated industries (healthcare, finance, insurance, legal) that must prove agent decision integrity to auditors.

### Co-Pilot (Premium, Per-Seat Subscription)
> *"This agent doesn't just track decisions. It thinks."*

- Everything in Verification
- **PLUS:** Tuned agent personality (override handling, contradiction detection, self-critique)
- **PLUS:** Business-specific intent tuning
- **PLUS:** Custom knowledge base integration
- **PLUS:** Deep workflow integration

**Best for:** Enterprises who want an agent that acts as a senior team member, not a yes-man.

---

## Installation

```bash
# Install from PyPI
pip install certainlogic-foundation

# Or install from source
git clone https://github.com/CertainLogicAI/foundation.git
cd foundation && pip install -e .
```

### Quick Start

```python
from certainlogic_foundation import Brain
from certainlogic_foundation.tre import TokenReductionEngine
from certainlogic_foundation.pathfinder import AgentPathfinder

# 1. Initialize brain
brain = Brain()

# 2. Initialize TRE (caches queries, routes by complexity)
tre = TokenReductionEngine()

# 3. Initialize tracker (logs all agent actions)
pf = AgentPathfinder()

# 4. Use it
user_query = "what is our moat strategy"
result = brain.query(user_query)

# 5. Log it
pf.log_decision(
    agent_action="brain_query",
    query=user_query,
    intent=result.intent,
    confidence=result.confidence,
    sources=[s.slug for s in result.sources],
)

# 6. Check daily stats
print(pf.get_daily_stats())
# {'queries': 1, 'hit_rate': 0.85, 'avg_latency_ms': 45, 'top_intents': {'strategy': 1}}
```

### Configuration

```python
# config.py — YOUR business customization
certainlogic_foundation.configure({
    "intent_patterns": {
        "strategy": [r'\bmoat\b', r'\bstrategy\b', ...],
        "product": [r'\byour_product\b', ...],
    },
    "boost_map": {
        "concepts/your-prefix": 1.8,
        "projects/your-product": 1.6,
        "personal/": 0.6,
    },
    "gbrain_path": "/path/to/your/gbrain",
    "cache_dir": "~/.certainlogic-foundation/cache",
})
```

---

## Philosophy

**Open source isn't charity. It's distribution.**

The CertainLogic Foundation exists because:
1. Every agent needs deterministic routing and basic tracking
2. gbrain provides a great core, but lacks intent-awareness and observability
3. If we solve the foundation problem for free, we earn trust
4. If they trust us, they'll consider us when they need the premium layers

**We're not giving away the moat. We're clearing the path to it.**

The moat is the co-pilot agent — the tuned personality, the contradiction detection, the self-critique, the business-specific knowledge. That's what takes months to build and can't be replicated in a weekend.

The foundation is the on-ramp. Free to use, easy to adopt, harder to outcompete.

---

## Contributing

We welcome contributions to the CertainLogic Foundation. Priority areas:
- Additional intent classification patterns (industry-specific)
- New source boost strategies (content-type prioritization)
- TRE optimizations (cheaper routing, bigger caches)
- AgentPathfinder exporters (Datadog, Splunk, Grafana)
- Documentation and tutorials

**Not accepting:**
- CertainLogic-specific config values (kept in private repo)
- Cryptographic signing code (proprietary, Verification tier only)
- Co-pilot agent logic (proprietary, Premium tier only)

---

## Roadmap

**v1.0 (Phase 4 complete — Week 5)**
- Core intent layer
- TRE caching and routing
- AgentPathfinder tracking
- Production hardening
- Operator's guide

**v1.1**
- Multi-source gbrain support
- Advanced cache invalidation strategies
- Community-contributed intent pattern packs

**v1.2**
- Integration with gstack
- Code-aware query routing
- Benchmarking suite

---

## License

MIT License — permissive, community-friendly, YC-aligned.

The CertainLogic Foundation is free to use, modify, and distribute. CertainLogic proprietary products (Verification tier, Co-pilot agent, CertainLogic-specific tuning) are available separately under commercial license.

---

**Maintained by:** CertainLogic  
**Website:** certainlogic.ai  
**Community:** [GBrain Discord / gstack channel]
