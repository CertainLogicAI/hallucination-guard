# LLM Cost Models — Token Budgeting

Current OpenRouter pricing (Claude 4.6):

| Model | Input /1M tokens | Output /1M tokens |
|-------|------------------|-------------------|
| Haiku | $0.80 | $4.00 |
| Sonnet | $3.00 | $15.00 |
| Opus | $15.00 | $75.00 |

## Token Estimation

- 1 token ≈ 4 characters (English)
- 1KB ≈ 250 tokens
- System prompt: 50–2,000 tokens (keep it lean)
- Output cap: set `max_tokens` to control costs

## Cost Calculation

```
Total cost = (input_tokens / 1M) × input_rate + (output_tokens / 1M) × output_rate
```

Example: 5,000 input + 1,000 output using Sonnet:
- Input: 0.005M × $3 = $0.015
- Output: 0.001M × $15 = $0.015
- **Total: $0.03** per request

## Optimization Targets

- Cache identical requests (80% hit rate = 80% cost reduction)
- Compress inputs (semantic摘要 saves 70–90%)
- Route simple tasks to Haiku, complex to Opus
- Set hard output limits (JSON mode prevents rambling)
- Batch multiple items in one prompt when possible

## Budget Planning

At 10k requests/month:
- 5k tokens avg per request (input+output) = 50M tokens
- Mixed model average $0.20/M tokens = **$10,000/mo**

Reduce to 1.25k tokens avg → 12.5M tokens → **$2,500/mo** → **75% savings**.

---
*Canonical reference. Do not edit without updating dependents.*
