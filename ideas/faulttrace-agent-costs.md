---
summary: "\"FaultTrace Agent Stack — API Cost Estimate\""
read_when: ["["idea", "faulttrace", "agent", "pricing"]"]
---
# FaultTrace Agent Stack — API Cost Estimate

**Based on Claude 4.6 pricing (Opus $15/$75, Sonnet $3/$15 per 1M tokens)**

## Assumptions

| Metric | Value | Rationale |
|--------|-------|-----------|
| Avg L5X file size | 25 KB | Medium-sized PLC program (~500 rungs) |
| Input tokens per 1KB | ~250 | Text: 1 char ≈ 0.25 tokens |
| Avg input tokens per file | 6,250 | 25 KB × 250 |
| Agent overhead (context) | +2,000 | System prompts, memory, previous turns |
| Total per analysis | ~8,250 tokens | conservative |

## Cost Scenarios

### 1. MVP Implementation (1 agent skill: Test Generator)

**Usage estimate:** 100 analyses/day for 30 days = 3,000 analyses

| Model | Input | Output | Total tokens/mo | Cost/mo |
|-------|-------|--------|-----------------|---------|
| Opus (complex logic) | 8,250 | 4,000 | 36,750,000 | $551 (input) + $300 (output) = **$851** |
| Sonnet (standard) | 8,250 | 4,000 | 36,750,000 | $110 + $60 = **$170** |
| Haiku (simple) | 8,250 | 4,000 | 36,750,000 | $29 + $16 = **$45** |

**Recommended MVP model:** Sonnet — balance of quality and cost.

### 2. Production (4 premium skills)

3,000 analyses/mo across 4 skills (avg 750 analyses/skill)

| Skill | Complexity | Model | Mo. cost |
|-------|------------|-------|----------|
| Test Generator | Standard | Sonnet | $42 |
| Auto-Fixer | Complex | Opus | $212 |
| Compliance Checker | Standard | Sonnet | $42 |
| Runtime Simulator | Complex | Opus | $212 |
| **Total** | | | **$508/mo** |

### 3. Pay-Per-Use Pricing Model

Price per credit-enhanced analysis:

| Model | Cost/analysis | Sell for | Margin |
|-------|---------------|----------|--------|
| Haiku | $0.045 | $0.10 | 55% |
| Sonnet | $0.17 | $0.35 | 51% |
| Opus | $0.85 | $1.50 | 43% |

**Example:** 1,000 users doing 3 analyses/mo (50% Sonnet, 50% Opus)
- Cost: (1,500 × $0.17) + (1,500 × $0.85) = $1,530
- Revenue: (1,500 × $0.35) + (1,500 × $1.50) = $2,775
- **Net: $1,245/mo**

### 4. Enterprise (All-in subscription)

Assume 10 enterprise customers @ $299/mo each = $2,990 revenue

Estimate usage: 10 companies × 100 analysts × 10 analyses/mo = 10,000 analyses

If 70% Sonnet, 30% Opus:
- Cost: (7,000 × $0.17) + (3,000 × $0.85) = $1,190 + $2,550 = **$3,740**

**Result: Loss of $750/mo** unless we:
- Negotiate volume discounts from OpenRouter
- Use Haiku for simpler analyses
- Cache results (re-run only on code changes)

## Optimization Strategies

1. **Cache analysis results** — identical inputs → free retrieval
2. **Tiered model routing**:
   - Compile errors only → Haiku
   - Code quality → Sonnet
   - Architecture suggestions → Opus
3. **Batch processing** — nightly re-runs on changed files only
4. **Prompt optimization** — shrink system prompts by 30% → direct cost savings

## Bottom Line

- MVP: ~$170/mo (Sonnet only, 3k analyses)
- 4-skill production: ~$500/mo
- Need ~1,200 paying users at $0.35/analysis to break even if mix is mostly Opus

Recommend starting with **Sonnet-only MVP** to validate demand before introducing Opus-heavy features.

---
*Created: 2026-03-27*
*Prices: Claude 4.6 via OpenRouter*
*Exchange rate: 1 token = 1 input or output token*
