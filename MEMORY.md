# MEMORY.md

- Added a daily self-evaluation process to regularly review performance and update habits.

## 2026-04-13 — Major Session

### Identity & Setup
- I'm Alex. Trusted colleague. Brutal clarity, accuracy over speed, no shortcuts, always acknowledge messages immediately.
- Anton: Controls engineer, marketing degree, sales experience, crypto, rental real estate business. CST timezone. @ForCryptoClearly on Telegram.
- Old instance restored from Backblaze B2 backup (233MB). Telegram fixed (polling mode, full token restored).

### Products (3 active)
1. **Deterministic AI Brain** — Two products: (1) Agent/SMB: LLM→filter→cache, >2% hallucination OK, token savings. (2) Regulated: known-facts DB, zero-LLM capable, <2% hallucination target. Patent drafted but NOT filed. CertainLogic.ai is the brand.
2. **FaultTrace** — Industrial PLC analyzer. L5X parser + writer + schematic generator. 29/29 test files passed. 2 beta testers. Pricing TBD ($99-499/mo discussed). faulttrace.ai domain.
3. **Skills marketplace** — 6 premium skills at $19 each. Moving to CertainLogic.ai shop.

### Infrastructure Built
- Deterministic brain API running on localhost:8000 (FastAPI, 48 facts, full pipeline)
- Skill: deterministic-cache/SKILL.md (checks cache on every query)
- Brain API watchdog cron (every 5 min, Haiku)
- Daily Backblaze B2 backup cron (3AM EDT, Haiku)
- Default model: Sonnet 4.6. Cron jobs: Haiku. Manual /model opus for heavy work.
- Auth permissions: 600. Git committed.

### Business Strategy
- Brand: CertainLogic.ai (everything). FaultTrace.ai (product). Blenderism retired.
- Funnel: Free skills (ClawHub) → Blog → Premium skills shop → Consulting → Custom builds ($2-10K) → Retainers ($200-500/mo)
- FaultTrace runs as parallel Track B — strongest PMF, ship it.
- Skip patent for now — no filing, keep as trade secret, consult attorney before month 6.
- Content: business owners, not devs. Problems + money, not tech.
- Socials: X (Twitter) + LinkedIn priority. YouTube claim now.

### CertainLogic.ai Site (in progress)
- Stack: Astro v6 + Tailwind v4 + Cloudflare Pages + Stripe + Resend
- Colors: Navy #0F1724, Electric Blue #2563EB, White/off-white background
- Phase 1A done: foundation, design system, homepage, header, footer
- Phase 1B done: blog infrastructure + 5 launch posts written and building clean
- Needs: GitHub repo (Anton) + Cloudflare Pages connection (Anton) + Stripe account (Anton)

### Anton's Todo
- X API tokens (developer.twitter.com)
- OpenRouter API key (notes)
- Stripe account setup
- GitHub repo + push site code
- Cloudflare Pages connection
- Claim @certainlogic on X, LinkedIn, YouTube
- FaultTrace pricing decision
- IP attorney consult (not urgent, before month 6)
# Curated long-term memory
#
# This file stores distilled memories, decisions, lessons learned, and other
# curated context.  Add significant events, insights, and context here.
# 
# Initialized on 2026-04-12.