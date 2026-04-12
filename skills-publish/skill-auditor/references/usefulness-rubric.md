---
summary: "\"Usefulness Rubric\""
read_when: ["[]"]
---
# Usefulness Rubric

Score each dimension 1-5. Total determines tier.

## Dimensions

### Substance (1-5)
Does it contain real frameworks, workflows, or tools — or just vague advice?

| Score | Criteria |
|-------|----------|
| 1 | Empty or placeholder content, no actionable information |
| 2 | Generic advice easily found anywhere, no unique value |
| 3 | Decent frameworks but surface-level, missing depth |
| 4 | Strong workflows with specific steps, examples, or templates |
| 5 | Battle-tested frameworks, reference files, scripts, production-ready |

### Structure (1-5)
Is it well-organized with progressive disclosure?

| Score | Criteria |
|-------|----------|
| 1 | One messy blob, no sections, no frontmatter |
| 2 | Basic sections but poor organization, missing frontmatter fields |
| 3 | Decent organization, has frontmatter, but SKILL.md is bloated (>300 lines) |
| 4 | Clean SKILL.md with reference files, good progressive disclosure |
| 5 | Lean SKILL.md (<150 lines) with well-organized references, scripts, and/or assets |

### Actionability (1-5)
Can you use it immediately, or does it need heavy setup?

| Score | Criteria |
|-------|----------|
| 1 | Requires external services with no free tier, complex setup |
| 2 | Needs significant configuration or missing dependencies |
| 3 | Works after minor setup (env vars, one install) |
| 4 | Works immediately with standard OpenClaw tools |
| 5 | Zero setup, instantly useful, self-contained |

### Fit (1-5)
Does it align with your goals and fill a gap in your toolkit?

| Score | Criteria |
|-------|----------|
| 1 | Completely irrelevant to current needs |
| 2 | Tangentially related but not useful now |
| 3 | Could be useful eventually |
| 4 | Directly relevant, fills a clear gap |
| 5 | Critical need, nothing else covers this |

### Maintenance (1-5)
Is the skill actively maintained and trustworthy?

| Score | Criteria |
|-------|----------|
| 1 | No updates in 6+ months, unknown owner |
| 2 | Rarely updated, minimal community presence |
| 3 | Updated within last 3 months |
| 4 | Actively maintained, known author, good license |
| 5 | Frequently updated, strong reputation, MIT-0 or similar |

## Tier Calculation

| Total Score | Tier | Action |
|-------------|------|--------|
| 20-25 | **Tier 1 — Install** | High quality, immediately useful |
| 14-19 | **Tier 2 — Worth having** | Solid but less critical |
| 8-13 | **Tier 3 — Skip** | Low quality or not relevant |
| 5-7 | **Reject** | Waste of context window |

## Quick Decision Overrides

Regardless of score, **skip** if:
- VirusTotal flagged
- Locked into a third-party platform with no escape
- Auto-fetches tokens/credentials from unknown APIs
- Pipe-to-shell install (`curl | sh`)
- Obvious marketing wrapper with no real content

Regardless of score, **install** if:
- Fills a critical gap with no alternative
- Clean security scan + strong substance
