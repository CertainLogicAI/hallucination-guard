---
summary: "Cold Outreach Pro"
read_when: ["[]"]
---



# Cold Outreach Pro

Battle-tested cold outreach system from Hormozi's $100M Leads, Cleverly, Hypergen, and SalesHandy analysis of 100K+ campaigns.

## Quick Reference

| Need | Resource |
|------|----------|
| Build your Ideal Customer Profile | `scripts/icp-builder.sh` |
| Industry-specific templates (SaaS, agency, freelance, local, ecom, B2B) | `references/industry-templates.md` |
| A/B test subject lines, openings, CTAs | `references/ab-testing.md` |
| Handle prospect objections (price, timing, competition, trust) | `references/objection-handling.md` |
| Score and prioritize leads before outreach | `references/lead-scoring.md` |
| Generate a 5-touch outreach sequence | `scripts/sequence-generator.sh <name> <industry> <pain>` |
| Track your outreach pipeline | `scripts/follow-up-tracker.sh init` |
| Add prospects to pipeline | `scripts/follow-up-tracker.sh add <name> <email>` |
| Check overdue follow-ups | `scripts/follow-up-tracker.sh due` |

## ICP First

Before writing a single word, build your Ideal Customer Profile:
```bash
bash scripts/icp-builder.sh workspace/artifacts/my-icp.md
```
Fill in the template. If you can't describe their daily frustration in one sentence, your ICP isn't sharp enough.

## Why Most Cold Outreach Fails

- **Ego-centric opener** — "We're the leading..." Nobody cares about you yet.
- **Generic spray** — 1,000 identical emails → 2.1% reply. 50 targeted → 5.8%.
- **Hard sell in email #1** — pricing/demos before establishing value = dead.
- **Wall of text** — over 125 words loses 50%+ of readers. Ideal: 50-100 words.
- **No follow-up** — most conversions require 2+ touches.

## Core Psychology

- **3-Second Rule** — first line must prove you researched THEM
- **Reciprocity** — give value before asking (Hormozi's lead magnet principle)
- **Pattern interrupt** — specificity is the antidote to spam
- **Loss aversion** — "You're losing X" hits harder than "You could gain X"

## Hormozi's 4 Steps

1. **Build the list (ICP-first)** — who, what pain, what signal, where to find
2. **Personalize to trigger** — beyond {FirstName}. Reference their news, site, gaps.
3. **Lead with value** — insight, quick win, or social proof. Free stuff must be good enough to charge for.
4. **Automate the sequence** — 3-5 touches, 3-5 days apart, each adds NEW value

## Copywriting Frameworks

**PAS (Problem → Agitate → Solve)** — for prospects who KNOW they have a problem
```
[Problem] Noticed [Business] doesn't have [X].
[Agitate] Most [type] lose [impact] monthly because of this.
[Solve] We built [solution] for [similar biz] → [result in timeframe].
Worth 10 minutes?
```

**BAB (Before → After → Bridge)** — for prospects who don't realize the problem
```
[Before] Right now, [Business] is [current state].
[After] Imagine [desired state].
[Bridge] We help [type] get there. [Similar biz] switched in [timeframe].
Quick look?
```

**AIDA (Attention → Interest → Desire → Action)** — when you need a hook
```
[Attention] [Surprising stat about their business]
[Interest] We found that [insight].
[Desire] [Similar biz] used this for [result].
[Action] Can I share the playbook? 2 min read.
```

**One-Liner** — for execs, follow-ups, SMS
```
[Observation] + [Result for similar company] + [Soft ask]
```

## Sequence Blueprint

| Touch | Day | Channel | Purpose |
|-------|-----|---------|---------|
| 1 | 0 | Email | Problem-aware opener (PAS/BAB) |
| 2 | 3 | LinkedIn | Connect + engage their content |
| 3 | 5 | Email | Share insight or case study |
| 4 | 10 | SMS/Email | Brief personal touch (one-liner) |
| 5 | 14 | Email | Breakup — close the loop gracefully |

## Metrics

| Metric | Bad | Good | Great |
|--------|-----|------|-------|
| Open rate | <30% | 50-65% | 65%+ |
| Reply rate | <2% | 5-8% | 8%+ |
| Meeting booked | <0.5% | 1-2% | 2%+ |

**Diagnose:** Low opens → subject line. Opens no replies → message/CTA. Replies no meetings → offer/timing.

## Deliverability

- SPF, DKIM, DMARC configured on sending domain
- Send from secondary domain (protect primary)
- Warm up 2+ weeks (start 5/day, increase 5/day)
- Under 50 emails/day per mailbox
- No spam triggers ("free", "guarantee", "act now")
- Plain text or minimal HTML
- Unsubscribe link (CAN-SPAM / GDPR)
- Bounce rate under 3%
