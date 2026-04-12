# Workspace References — Canonical Definitions

This directory contains **single-source-of-truth** content for concepts that appear repeatedly across workspace files. Instead of copying paragraphs, reference them with `{keyword}` syntax.

## How to Use

In any markdown file, write:

```markdown
FaultTrace is a static analysis tool for Allen-Bradley PLC code. See {faulttrace} for details.
```

When an agent reads the file, it will expand `{faulttrace}` to the full content of `faulttrace-product.md`. This prevents duplication and keeps token usage low.

**Important:** Do NOT edit reference files directly without considering all dependents. They are shared.

---

## Reference Index

| Ref | Summary | Tags |
|-----|---------|------|
| `faulttrace` | Static L5X analyzer for PLC code | faulttrace, product |
| `openclaw-agents` | AI agent framework for automation | openclaw, agents |
| `pricing-subscription` | Subscription-based pricing tiers | pricing, business |
| `pricing-usage` | Pay-per-use credit model | pricing, business |
| `docker-deploy` | Deploy Node.js apps with Docker + Nginx | docker, infra |
| `llm-cost-models` | Claude pricing and token calculation | llm, costs |
| `api-auth` | API key authentication patterns | api, security |
| `redis-caching` | Redis for response caching | cache, infra |

---

## Reference Files

- faulttrace-product.md
- openclaw-agents.md
- pricing-subscription.md
- pricing-usage.md
- docker-deploy.md
- llm-cost-models.md
- api-auth.md
- redis-caching.md

---
*Maintained automatically — edit with caution*
