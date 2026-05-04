# Onboarding Wizard v2.1.0 — Scope: Freemium Shift
**Approved 2026-05-02 09:03 EDT**

## Problem We’re Solving
Copycats will clone our wizard within 60 days. The only defense is making the free version so good that clones look like cheap knockoffs.

## Big Change: Free Tier Gets Everything

### Free (Previously Limited)
- [x] Environment scan
- [x] All profiles (developer, business, etc.)
- [x] Markdown report generation
- [x] Links to skills

### Free (NEW — Previously Pro-only)
- [ ] **One-command setup scripts** — shell scripts that install your recommended stack
- [ ] **Post-install verification** — checks that installed skills actually load and run
- [ ] **Weekly checkups** — re-scans environment, suggests updates, flags issues
- [ ] **Team onboarding** — export setup scripts for your team's agents

### Pro ($29) — Loses feature lock, gains service
- [ ] Priority support (24h response SLA)
- [ ] Early access to new features
- [ ] Custom industry templates (healthcare, legal, finance)
- [ ] One-on-one onboarding call (15 min)

**Pro is not an unlock. It’s a relationship. Free is the product.**

## Messaging Changes

### README.md
- Remove "Free vs Pro" comparison table that makes free look incomplete
- Add: "CertainLogic free products are built to the same standard as paid products. Upgrade when you want deeper support, not when you need basic features."
- Add competitive differentiation section: "Why not fork this? Clones ship code. We ship code + documentation + edge-case handling + active maintenance."

### SKILL.md
- Same structure, new tier table
- Add: "If you can find a free OpenClaw onboarding skill with better documentation or more thorough error handling, install it. We’ll wait."
- Remove urgency language ("limited time," "early access")

### Code Changes Required

| File | Change | Effort |
|------|--------|--------|
| `README.md` | Rewrite tier section, add anti-copycat copy | 15 min |
| `SKILL.md` | Same, add "why this is free" explanation | 15 min |
| `scripts/onboarding_wizard.py` | Remove Pro-check logic, enable all features for all users | 10 min |
| `skill.json` | Remove "free vs pro" feature gating references | 5 min |
| `tests/` | Add tests for verification scripts (previously Pro-only) | 20 min |

## Test Plan
1. Old behavior: Pro features blocked → verify now unblocked
2. Report generation includes setup scripts → verify scripts are valid shell
3. Post-install verification runs without error → verify on clean environment
4. Weekly checkup mode runs as scheduled → verify via test flag

## Anti-Copycat Strategy
- **Documentation depth** — clones copy code, not the 2,000 words explaining edge cases
- **Error messages** — every failure path has a helpful message; knockoffs ship `print("error")`
- **Active maintenance** — weekly checkups that actually catch drift in skill versions
- **Integration depth** — verification scripts that test actual skill behavior, not just file existence

## Files to Modify
- `/data/.openclaw/workspace/skills-publish/certainlogic-onboarding-wizard/README.md`
- `/data/.openclaw/workspace/skills-publish/certainlogic-onboarding-wizard/SKILL.md`
- `/data/.openclaw/workspace/skills-publish/certainlogic-onboarding-wizard/scripts/onboarding_wizard.py`
- `/data/.openclaw/workspace/skills-publish/certainlogic-onboarding-wizard/skill.json`

## Not Changed
- GitHub repo URL
- ClawHub listing (will republish as v2.1.0)
- Core scan/detection logic (still works the same, just enabled for all)

## Risk
- **Revenue impact:** $0 immediate (Pro was converting ~0% anyway; free quality drives paid upsell on OTHER skills)
- **Support load:** Slightly higher (free users get full verification scripts → more questions)
- **Mitigation:** Verification scripts are self-serve; support questions are actually sales conversations

## Time Estimate
- Code changes: 30 minutes
- Testing: 20 minutes
- Documentation: 30 minutes
- Total: ~90 minutes

## Approval Required
Anton must approve this scope before execution. Two things:
1. Confirm the freemium shift matches intent
2. Confirm "Pro = support relationship, not feature unlock" positioning

---
*Scope built 2026-05-02 09:30 EDT. Awaiting approval.*
