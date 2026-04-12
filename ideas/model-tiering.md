---
summary: "\"Model Tiering Strategy\""
read_when: ["["idea"]"]
---
# Model Tiering Strategy

## Current Assignment
| Task | Model | Cost (per 1M tokens in/out) | Rationale |
|------|-------|-----------------------------|-----------|
| Main session (Anton chat) | Opus 4.6 | $15 / $75 | Complex reasoning, strategy, code generation |
| Daily self-eval cron | Haiku 4.5 | $0.80 / $4 | Simple checklist, read files, brief report |
| Weekly memory audit cron | Sonnet 4.6 | $3 / $15 | Needs judgment to curate memories |
| FaultTrace AI backend (future) | TBD — test MiMo/GPT-5.4 Nano via OpenRouter | $0.20-1 / $1.25-3 | Rule engine handles 75%, AI only for novel queries |

## Cost Comparison (estimated daily)
| Before (all Opus) | After (tiered) |
|--------------------|----------------|
| Main: ~$2-5/day | Main: ~$2-5/day (unchanged) |
| Daily eval: ~$0.50 | Daily eval: ~$0.03 (Haiku) |
| Weekly audit: ~$0.50/wk | Weekly audit: ~$0.10/wk (Sonnet) |
| **Total: ~$3-6/day** | **Total: ~$2-5/day** |

## Future Crons (when added)
| Task | Recommended Model |
|------|-------------------|
| Blog post generation | Sonnet |
| Tweet drafts | Haiku |
| X monitoring | Haiku |
| Skills backlog tasks | Sonnet |
| Simple reminders | Haiku |

## Rules
- Opus: only main session + tasks requiring complex multi-step reasoning
- Sonnet: content generation, memory curation, anything needing quality writing
- Haiku: monitoring, simple checks, reminders, data extraction
