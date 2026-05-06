# Trend Factory Enhancement Notes

Extracted from external feedback, 2026-05-06.

## Recommended Free Models (OpenRouter)

| Role | Model | Reason |
|------|-------|--------|
| Coding (primary) | Qwen3 Coder 480B | Agentic, tool-calling, free |
| Coding (fallback) | Poolside Laguna M.1 | Code specialist |
| Research (primary) | DeepSeek R1 (free) | Reasoning |
| Long context | Owl Alpha | 1M+ context |
| General | NVIDIA Nemotron 3 Super | Speed |

## Trend Source Upgrades

| Source | Cost | Note |
|--------|------|------|
| Apify X Trends Scraper | ~$1/1k results | Real-time, structured JSON |
| MCP servers (OpenTweet/Xpoz) | Free tier 100k/mo | AI-native query |
| Official X API v1.1 | Free limits | Basic trends |
| RSS (TLDR AI, Ben's Bites, HN) | Free | Always-on, zero cost |
| NewsData.io / Firecrawl | Free tier | Structured JSON articles |

## "Watch Live" Dashboard Concept
- Public URL showing agent thoughts, tool calls, generated code, test results
- Hash-verified session logs exportable as case studies
- Viral hook: "Watch the Company Brain agent work in real time"
- Every run ends with beta invite CTA

## Immediate Actions
- [ ] Update trend factory model list with recommended free models
- [ ] Add RSS ingestion to trend sources (lower cost than API scraping)
- [ ] Document "watch live" architecture for later build
- [ ] Test Qwen3 Coder 480B vs our current qwen3-coder:free

## Anti-Noise Filter
- Same sender as earlier message with ~80% duplicate content
- Hyperbolic claims already filtered out
- Tactical recommendations only captured above
