---
summary: "Market Research Pro"
read_when: ["[]"]
---



# Market Research Pro

Turn fuzzy ideas into decision-ready evidence. Research markets, size opportunities, validate demand, and map competitors before committing resources.

## Quick Reference

| Need | Resource |
|------|----------|
| Size a market (TAM/SAM/SOM) | `scripts/tam-calculator.sh` |
| Analyze a competitor | `scripts/battle-card.sh <name>` |
| Interview potential customers | `references/customer-discovery.md` |
| Research pricing strategy | `references/pricing-research.md` |
| Decide whether to enter a market | `references/market-entry-scorecard.md` |
| Find evidence of demand | `references/signal-tracker.md` |
| Run a SWOT analysis | `scripts/swot-generator.sh <business-name>` |
| Quick-scan a competitor website | `scripts/competitor-scraper.sh <url>` |

## Research Process

### 1. Define the Question
Before researching, write one sentence: "We need to know ___ so we can decide ___."

Bad: "Research the AI market"
Good: "We need to know if OpenClaw skill creators will pay $15-25 for premium tools so we can decide whether to build a paid catalog."

### 2. Gather Signals
Use `references/signal-tracker.md`. Find evidence across:
- **Behavioral** (strongest): people paying, hiring, building workarounds
- **Stated** (medium): people discussing pain, requesting features
- **Inferred** (weakest): search trends, funding activity, content volume

**Rule:** Don't enter without 3+ pieces of B-grade or higher evidence.

### 3. Size the Opportunity
Run the TAM calculator:
```bash
bash scripts/tam-calculator.sh workspace/artifacts/market-sizing.md
```
Cross-check top-down and bottom-up approaches. If they're >2x apart, revisit assumptions.

### 4. Map Competitors
Generate battle cards for each competitor:
```bash
bash scripts/battle-card.sh "CompetitorName" workspace/artifacts/battlecard-competitor.md
```

Research sources:
- Company websites (homepage H1, pricing, about)
- G2, Capterra, TrustRadius (reviews reveal weaknesses)
- LinkedIn (size, recent hires signal priorities)
- Crunchbase (funding, investors)
- Reddit, Twitter (real user opinions)
- Job postings (what they're hiring signals strategy)

### 5. Validate with Customers
Use `references/customer-discovery.md` for interview scripts.
- 5 interviews reveals ~80% of issues
- 12-15 for robust patterns
- Stop when you hear the same answers 3x (saturation)

**The Mom Test:** Talk about their life, not your idea. Past behavior > future promises.

### 6. Research Pricing
Use `references/pricing-research.md` for frameworks:
- **Van Westendorp** — find acceptable price range from 4 questions
- **Gabor-Granger** — test specific price points to maximize revenue
- **Competitive analysis** — map price vs value positioning

### 7. Make the Call
Score the opportunity with `references/market-entry-scorecard.md`:
- 6 dimensions × 1-5 scale
- 25-30 = enter now, 19-24 = cautious, 13-18 = defer, <13 = skip

## Evidence Rules
- **Cite sources.** No claims without evidence.
- **Grade evidence.** A (behavioral) > B (stated) > C (inferred) > D (anecdotal).
- **Date everything.** Markets move. Note when info was verified.
- **Say "I don't know."** Gaps are honest. Guesses dressed as research are dangerous.
