# CertainLogic Claim Verification Policy
## Effective: April 29, 2026
## Version: 1.0

---

## Principle

**No claim about any CertainLogic product may be published without Anton's personal verification that the claim is accurate.** Not "I trust Alex." Not "the agent said it works." Anton installs, uses, and confirms every claim.

---

## What Requires Verification

Any public-facing statement about what a product does, including:

- SKILL.md "capabilities" sections
- README feature lists
- Blog posts and case studies
- X/Twitter posts and replies
- Website copy (services, product pages, about)
- Benchmark results and methodology claims
- Pricing/feature comparison tables
- Customer testimonials promoted by CertainLogic

---

## The Verification Process

### For Every Product Listing (SKILL/README)

| Step | Who | Required Proof |
|------|-----|----------------|
| 1. Build | Alex | Code in repo, tests passing |
| 2. Document features | Alex | Draft README, SKILL.md |
| 3. **Install from public source** | Anton | `clawhub install [product]` or `pip install git+...` |
| 4. **Test each claimed feature** | Anton | Run the exact commands the README shows. Verify output matches claims. |
| 5. Verify no false implications | Anton | Read every sentence. Does it imply something that isn't implemented? |
| 6. **Explicit publish approval** | Anton | Say "approved" — no silent consent, no assumed yes |

**Minimum hold time:** 24 hours between draft and approval.

### For Benchmarks

| Step | Who | Required Proof |
|------|-----|----------------|
| 1. Define methodology first | Both | Written before any test runs |
| 2. Run live | Alex | Actual API calls, actual outputs |
| 3. Disclose ALL results | Alex | Including unfavorable ones |
| 4. Verify reproducibility | Anton | Re-run a subset, confirm same results |
| 5. Define scoring explicitly | Both | Epistemic vs standard. No ambiguous "pass rates." |
| 6. **Explicit publish approval** | Anton | Must understand and agree with every claimed number |

### For Blog Posts / Social Media

| Step | Who | Required Proof |
|------|-----|----------------|
| 1. Draft | Alex | Fact-check every statistic, every quote |
| 2. Verify product claims match verified listing | Alex | If blog says "works in main chat," check if SKILL.md says same |
| 3. Anton review | Anton | Read entire post before scheduling/publishing |
| 4. **Explicit publish approval** | Anton | No auto-tweeting, no scheduled posts without check |

---

## What Alex Cannot Do Without Explicit Approval

- Publish or update SKILL.md files
- Publish or update GitHub READMEs for public repos
- Post on X/Twitter or any social media about products
- Publish benchmark results
- Submit products to ClawHub or any marketplace
- Write blog posts (can draft, cannot publish)
- Respond to product reviews or testimonials with claims
- Make any statement on Anton's behalf about product capabilities

**If in doubt, ask.
If Anton is unavailable, wait.
No urgent claim is worth a false one.**

---

## Corrections Process

If a false or misleading claim is discovered:

1. **Stop spreading immediately** — remove listing, unpublish post, whatever it takes
2. **Assess scope** — how many places was it published?
3. **Draft correction** — honest, specific, no excuse-making
4. **Anton approves correction** — exactly what he wants to say
5. **Publish correction in all channels where false claim appeared**
6. **Update ALL docs** — not just one, everywhere the claim existed
7. **Wait 7 days before relisting** — time buffer to catch follow-on issues

---

## Language Red Flags

The following require extra scrutiny. If they appear in a draft, flag for Anton:

- "100%" anything — almost certainly overstated
- "eliminates" — implies complete removal, rarely true
- "guarantees" — legal-level claim, needs proof
- "proves" / "proof" — stronger than "records" or "signs"
- "verified" — does it mean "I checked" or "the system checked automatically"?
- "cryptographic proof" — does it verify truth or just authorship?
- "AI reliability" — vague, hard to define, easy to overclaim
- "deterministic" — only if ZERO probabilistic components exist
- Cost savings percentages — must be from live data, disclosed methodology
- Any claim that sounds like a promise a customer could sue over

---

## Scope of Review for Anton

As product owner, Anton must personally confirm:

- [ ] He has installed the product from the public repository
- [ ] He has run the main advertised features
- [ ] The output matches the documented behavior
- [ ] No feature is described as working that he hasn't seen work
- [ ] No marketing implication goes beyond what he personally observed
- [ ] He understands every technical claim and agrees it's accurate
- [ ] He is willing to defend each claim if challenged

**If any checkbox is no, the product does not ship.**

---

## Why This Exists

On April 29, 2026, we discovered that AgentPathfinder was marketed as "100% verified task completion" and "cryptographic proof" when the system actually only records and signs agent claims. The agent can still falsely claim completion. The claim was wrong. The damage was limited because we caught it early, but it should never have shipped.

Root causes:
- Alex built and documented without Anton running the product
- Claims were written without verifying the mechanism
- Marketing language outpaced implementation
- No explicit approval checkpoint existed

This policy prevents recurrence.

---

## Enforcement

This policy is enforced by:
- Alex refusing to publish without explicit Anton approval
- Anton withholding approval until personal verification is complete
- No exceptions for "quick fixes" or "minor updates"
- 24-hour minimum hold on all publish decisions

---

*Policy written April 29, 2026. Applies to all CertainLogic products, posts, and publications going forward. Anton is the final authority on all claims.*
