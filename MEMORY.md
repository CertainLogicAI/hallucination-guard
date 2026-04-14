# MEMORY.md

## Identity
- I'm Alex. Trusted colleague. Brutal clarity, accuracy over speed, no shortcuts.
- Anton: Controls engineer, marketing degree, sales/crypto/real estate background. CST. @CertainLogicAI on X.

## Products
1. **Deterministic AI Brain** — Two tiers: (1) Agent/SMB: LLM→filter→cache. (2) Regulated: facts-only DB, zero-LLM capable. Patent drafted, NOT filed. Keep as trade secret for now.
2. **FaultTrace** — L5X parser + writer + schematic generator. 29/29 tests passed. 2 beta testers. faulttrace.ai
3. **Skills** — 6 premium at $19. Moving to CertainLogic.ai shop.

## Infrastructure
- Brain API: localhost:8000. Watchdog cron every 5min (Haiku). 52 facts loaded.
- Backups: Daily 3AM EDT → Backblaze B2 (OpenclawBackup1/openclaw/daily/)
- Model: Sonnet default. Haiku for cron. Opus on demand.
- OpenRouter fallback: configured, 24 free models. Key in auth-profiles.json.
- Telegram: polling mode, @CertainLogicAI account paired.

## Business
- Brand: CertainLogic.ai (all). FaultTrace.ai (product). Blenderism retired.
- Funnel: Free skills (ClawHub) → Blog → Shop → Consulting ($2-10K builds) → Retainers ($200-500/mo)
- Site: Astro v6 + Tailwind v4 + Cloudflare Pages. Navy #0F1724, Electric Blue #2563EB.
  - Phase 1A done: foundation, homepage, header, footer
  - Phase 1B done: blog + 5 posts written and building
  - Needs: GitHub repo + Cloudflare Pages (Anton) + Stripe account (Anton)
- Socials: @CertainLogicAI on X (rebranded from @ForCryptoClearly). LinkedIn/YouTube TBD.
- X content calendar: 2 weeks (42 posts + 2 threads) drafted. Awaiting Anton review.

## Anton's Todo
See docs/anton-todo.md for full list. Key items:
- Stripe account, GitHub repo, Cloudflare Pages connect
- X API keys, OpenRouter key ✅
- Claim LinkedIn/YouTube as CertainLogic
- FaultTrace pricing decision
- IP attorney consult before month 6

## Key Decisions
- No patent filing yet — trade secret protection, consult attorney before month 6
- FaultTrace is parallel Track B — strongest PMF, ship it
- Free OpenRouter models for cache-building; validate before caching
- Spawn subagents for heavy build tasks to control token burn
- Start fresh sessions daily
