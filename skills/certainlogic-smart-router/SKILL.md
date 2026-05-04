# CertainLogic Smart Router

**Route queries to the right model tier. Save money without thinking about it.**

v1.0.0

**Built and dogfooded by CertainLogicAI** — Keyword routing. Not AI. Not magic. Just cheaper.

---

## What It Actually Does
A **deterministic keyword + regex router** that classifies your query and recommends the best LLM tier:

- **cheap** — Simple lookups, greetings, short answers
- **default** — Standard tasks, explanations, drafting
- **powerful** — Complex reasoning, architecture, strategy

It supports built-in profiles (coding, research, marketing, general) and custom profiles via JSON.

## What It Does NOT Do
| Claimed Feature | Reality |
|----------------------------------|---------|
| AI-powered or learned routing | NO — Pure keyword + regex matching (deterministic) |
| Automatic LLM API calls | NO — Returns recommendation only. You call the model. |
| Built-in caching (v1) | NO — Caching layer planned for v1.1 |
| Guaranteed perfect routing | NO — Simple heuristics. Edge cases may misroute. |
| Multi-provider auto-selection | NO — Works with any models (you map tiers to models) |

## How to Use
### Standalone CLI
```bash
python3 scripts/smart_router.py "Write a Python function to parse JSON"
```

### In Your Agent (example)
```python
from smart_router import SmartRouter

router = SmartRouter()
result = router.route("Design a distributed system")

if result["model_tier"] == "cheap":
    model = "anthropic/claude-haiku-4-5"
elif result["model_tier"] == "default":
    model = "anthropic/claude-sonnet-4-6"
else:
    model = "anthropic/claude-opus-4-6"

# Then call your LLM with the chosen model
```

### Override Flags
- `--cheap` — Force cheap tier
- `--powerful` — Force powerful tier
- `--config my_profiles.json` — Use custom profiles

## Honest Limitations
- Static keyword lists (update config for new domains)
- English only (patterns tuned for English)
- Returns recommendation only (no API calls)
- Simple heuristics — will misroute edge cases (override flags exist)
- No built-in usage analytics or dynamic learning in v1

## Free vs Pro
**Free (this skill)**
- 4 built-in profiles
- Custom config support
- Override flags
- Full source code on GitHub

**Pro ($29 one-time)**
- Dynamic feedback loop (track what actually worked)
- Usage analytics + monthly savings report
- Auto-optimization using our benchmarks
- Fallback chains and team profiles
- Priority support

## Example Savings
Scenario: 100 queries/day (estimates)

| Without Router | With Router |
|-------------------------|---------------------------------|
| 100 × Opus | 60 × Haiku + 30 × Sonnet + 10 × Opus |
| ~$150/day | ~$120/day |
| | **Savings: ~20%** |

**Note:** Actual savings depend on your query mix. Test with our benchmarks.

## Recommended Next Steps (CertainLogic Stack)
- **Skill Vetter Plus** — Scan before installing anything new
- **Token Reduction Engine** — Keep sessions lean and cheap
- **AgentPathfinder** — Verifiable task tracking
- **Skill Oracle** — Honest skill recommendations

All work great together.

## Open Source Core
- Full source: https://github.com/CertainLogicAI/certainlogic-smart-router
- Related benchmarks: https://github.com/CertainLogicAI/hallucination-benchmark

## Links
- GitHub: https://github.com/CertainLogicAI/certainlogic-smart-router
- ClawHub: https://clawhub.ai/certainlogicai/certainlogic-smart-router

---

*Built by CertainLogicAI. We dogfood every skill we publish and fix issues transparently.*

### Version
latest v1.0.0

### Runtime Requirements
Python 3.10+, zero external dependencies
