---
summary: "\"Decoupled Architecture — Revised Build & Cost Estimates\""
read_when: ["["idea", "agent", "pricing"]"]
---
# Decoupled Architecture — Revised Build & Cost Estimates

**FaultTrace API + OpenClaw Agent Skills (separate products)**

---

## Revised Architecture (Static-Only)

```
┌─────────────────┐     ┌─────────────────┐
│   Engineer      │     │  FaultTrace API │
│   (user)        │────▶│   (static)      │
│                 │     │   • Analyzer    │
│ Upload L5X      │     │   • I/O Mapper  │
│ via web/CLI     │     │   • Report Gen  │
│                 │     │   • JSON export │
└─────────────────┘     └─────────────────┘
```

**Key change:** FaultTrace provides static analysis reports only. No AI agents, no OpenRouter costs.

---

## Build Effort (Static-Only)

### 1. FaultTrace API Layer (1-2 weeks)
- **Output:** REST/GraphQL endpoint that accepts L5X, returns JSON report
- **Already have:** Static analysis engine, I/O mapping, rule checks
- **Need to add:** Serialize results to structured JSON (not HTML/PDF)
- **Work:** 3-5 days
- **Optional:** Add rate limiting, auth tokens for API access

### 2. Web UI (1 week)
- Drag-drop file upload interface
- Display JSON report in pretty format
- Basic account management
- Work: 3-5 days

### 3. Billing/Payments (1-2 weeks)
- Stripe integration for subscription tiers
- Metering API calls per user (if usage-based pricing)
- Work: 3-5 days

### 4. Testing & Scaling (1 week)
- Load test: 100 concurrent analyses
- CSV/JSON export validation
- Fault injection: handle malformed L5X gracefully

**Total build time:** **3-4 weeks**

---

## Cash Costs (Solo Build)

| Item | Cost |
|------|------|
| API development (time) | $0 (your time) |
| Web UI | $0 |
| Testing & polish | $0 |
| **Development cash** | **$0** |
| VPS (FaultTrace API hosting) | $50/mo × 2 = $100 |
| Stripe fees (if billing) | ~$50 setup |
| **Total cash outlay** | **~$150** |

**Opportunity cost:** 4 weeks × 40 hrs/week = 160 hours. At $100/hr = $16k.

---

## Static-Only Operating Costs

### Infrastructure (per month)

| Scale | Analyses/mo | VPS tier | Cost/mo | CPU (est.) |
|-------|-------------|----------|---------|------------|
| Conservative | 2,500 | 4 vCPU, 16GB | $100 | 10% |
| Moderate | 12,000 | 4 vCPU, 16GB | $100 | 40% |
| Aggressive | 40,000 | 8 vCPU, 32GB | $200 | 80% (consider autoscale) |

**Bandwidth:** Negligible (L5X files ~25KB each → 1 GB/mo even at 40k analyses)

**Total:** $100–$200/mo depending on scale

---

## Revenue Model (Static-Only)

- **FaultTrace Pro:** $49/mo (includes API access)
- **Enterprise:** $99/mo (multi-seat, priority support)
- **Usage-based add-on:** $0.05/analysis beyond 10 included

**Break-even:**
- Conservative: 3 Pro subscribers ($147) vs $100 hosting → profitable
- Moderate: 3 Pro subscribers still covers costs; scale is mostly profit
- Aggressive: 2 Enterprise ($198) vs $200 hosting → breakeven; add usage fees for profit

---

## Pricing Tiers

| Tier | Price | Includes |
|------|-------|----------|
| Hobbyist | $9/mo | 5 analyses/mo, community support |
| Pro | $49/mo | 100 analyses/mo, email support |
| Team | $99/mo | 500 analyses/mo, 3 seats |
| Enterprise | Custom | Unlimited, SLA, on-prem options |

**At scale (40k analyses/mo):**
- 200 Pro users @ $49 = $9,800 revenue - $200 hosting = **$9,600 profit**
- Or 33 Enterprise @ $299 = $9,867 - $200 = **$9,667 profit**

Static-only margins are *excellent* because no AI token costs.

---

## Build Timeline (Static-Only: 3-4 weeks)

| Week | Tasks |
|------|-------|
| 1 | FaultTrace API: JSON endpoint + auth |
| 2 | Web UI: file upload + report display |
| 3 | Billing (Stripe) + usage metering |
| 4 | Testing, docs, launch prep |

---

## Key Advantages of Static-Only API

1. **Faster revenue:** 4 weeks to MVP vs 8 weeks with agents
2. **Zero token costs:** Only hosting, highly predictable
3. **Simpler support:** No AI hallucinations to manage
4. **Easier to sell:** Clear value proposition (better linter with API)
5. **Later AI optional:** Add agent layer once revenue stream exists

---

## One‑Time Build Cost (Recap)

- **Solo cash:** $150 (2 months VPS + Stripe setup)
- **Solo time:** 4 weeks = 160 hours
- **Total first-year cash outlay:** $150 + $100 (VPS ongoing) = **$250**

---

## Recommendation

Build the FaultTrace API *now* as a static-only service. It's 4 weeks to revenue, no AI token costs, and excellent margins.

If you later want AI features, add OpenClaw agent skills that consume this API. That becomes a separate product with its own pricing.

**Next step:** Build `POST /api/v1/analyze` that accepts L5X and returns structured JSON. That's the critical path.

---
*Created: 2026-03-27*
*Architecture: Decoupled, Static-Only (no AI)*
*Build: 3-4 weeks, cash ~$150 solo*
