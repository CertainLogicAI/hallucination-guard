# Structured Self-Critique Protocol

**Version:** 1.0  
**Date:** 2026-05-07  
**Status:** Active — replaces multi-LLM refinement pipeline  
**Rationale:** Single-session structured critique gets 90% of multi-LLM benefit with zero infrastructure risk.

---

## When to Apply

Mandatory before delivering:
- Scope & spec documents
- Architecture designs
- Process/protocol definitions
- SKILL.md updates (complex ones)

Optional but recommended:
- Code refactoring plans
- Deployment runbooks
- Content strategies

**Rule:** No scope doc ships without explicit critique section.

---

## The 5 Challenge Perspectives

For every deliverable, challenge it from these 5 angles. Write the critique as if you're someone else — don't go easy on yourself.

### 1. Production Skeptic

*"This will break in production. How?"*

**Questions:**
- What happens under load? (100x current traffic)
- What happens when dependencies fail?
- What happens after 30 days of continuous operation?
- Where are the single points of failure?
- What monitoring will tell us it's broken before users notice?

**Action:** If you can't answer, the spec is incomplete. Add failure modes and mitigations.

---

### 2. Scope Minimizer

*"90% of this work is unnecessary. Prove me wrong."*

**Questions:**
- What is the smallest change that provides 80% of the value?
- Which features are "nice to have" vs "must have"?
- What can be deferred to Phase 5 without blocking Phase 4?
- Is this solving a real problem or an imagined one?
- Are we optimizing for a scale we haven't reached yet?

**Action:** Cut ruthlessly. Defer anything not on the critical path.

---

### 3. Security Auditor

*"I'm going to attack this. Where are the gaps?"*

**Questions:**
- What happens if malicious content enters the system?
- Where are injection points? (input validation gaps)
- What data leaks in logs, errors, or responses?
- Who has write access? What can they destroy?
- What supply chain risks exist?
- Is there a path to credential exposure?

**Action:** If a threat can't be mitigated, flag it as accepted risk with justification.

---

### 4. Timeline Realist

*"This will take 3x what you estimated. Why?"*

**Questions:**
- What's the longest pole? (critical path item)
- Where is Anton's review needed? How long does that usually take?
- What's the unknown-unknown we haven't discovered yet?
- What other projects compete for the same resources?
- What breaks if we're 2 weeks late?

**Action:** Add buffer. Define "default proceed" rules for when review is delayed.

---

### 5. Dependency Checker

*"This assumes 5 things that aren't true yet."*

**Questions:**
- What tools, configs, or accounts need to exist before this works?
- What knowledge does the user need? Do they have it?
- What other projects does this depend on? Are they done?
- What external services? Are they reliable?
- What version pinning is needed?

**Action:** List every dependency explicitly. Flag any that are unverified.

---

## Critique Format

Append this section to every deliverable:

```markdown
---

## Self-Critique

### Production Skeptic
[What breaks? What did I add to handle it?]

### Scope Minimizer  
[What did I cut? What was deferred?]

### Security Auditor
[What threats did I miss initially? What mitigations were added?]

### Timeline Realist
[What buffer did I add? Where are the review gates?]

### Dependency Checker
[What does this depend on? Which are verified vs assumed?]

### Final Decisions
[What changed as a result of this critique?]
```

---

## Example: Brain OS Scope (Applied)

**Applied to the Brain OS scope document:**

### Production Skeptic
- *What breaks:* 10 concurrent brain queries fork-bomb the system. → **Added cli_pool.py**
- *What breaks:* gbrain CLI times out, skill hangs forever. → **Added 2s timeout + retry**
- *What breaks:* Circuit breaker never recovers. → **Added auto-recovery after 10 min**

### Scope Minimizer
- *Cut:* 3 cache layers for 443 facts. Already sub-100ms. → **Deferred to Phase 5**
- *Cut:* 4 vanity metrics with no decision driver. → **Cut to 4 actionable metrics**
- *Cut:* Complex LLM prompt template engine. → **Simplified to boolean flag**

### Security Auditor
- *Threat missed:* Data poisoning via brain writes. → **Added write_guard.py**
- *Threat missed:* Logs leak credentials from queries. → **Added log_redactor.py**
- *Threat missed:* ReDoS in intent regexes. → **Added ReDoS audit test**
- *Threat missed:* Supply chain risk from gbrain fork. → **Added version pinning doc**

### Timeline Realist
- *Buffer added:* 3 weeks → 5 weeks (allows weekly Anton checkpoints)
- *Review gates:* Each milestone has 48h default-proceed rule
- *Long pole:* Skill migration requires Anton verification per skill

### Dependency Checker
- *Verified:* gbrain CLI works (`bun run src/cli.ts`)
- *Verified:* PGLite with 443 facts is fast
- *Assumed:* Anton will review weekly (flagged as assumption)
- *Assumed:* Brain data quality is good enough for 50% hit rate (flagged as assumption, benchmark will verify)

### Final Decisions
- Reordered: Hardening before migration
- Cut complexity by ~40%
- Added 5 security mitigations not in original scope
- Extended timeline by 40% for review gates

---

## Integration with Evolution Reporter

Every Evolution Report must include:
- What was critiqued this session
- What changed as a result
- What was cut/deferred

This creates a paper trail of scope discipline.

---

## Commit Message Convention

When delivering a critiqued document:
```
feat(scope): [description]

Self-critique applied:
- Production: [key fix]
- Scope: [what was cut]
- Security: [mitigation added]
- Timeline: [buffer/reorder]
- Dependencies: [verified/flagged]
```

---

**Protocol owner:** Alex  
**Replaces:** Multi-LLM refinement pipeline (too much infrastructure risk)  
**Review cycle:** After every major deliverable
