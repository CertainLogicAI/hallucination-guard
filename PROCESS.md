# CertainLogic Build Process

**Status:** Locked v2.0  
**Effective Date:** 2026-05-02  
**Purpose:** Prevent the regression patterns that destroyed previous products. Preserve what Onboarding Wizard proved works.

---

## Non-Negotiable Rules

1. **No code obfuscation, ever.** Encoding data to dodge scanners is banned. If a scanner flags honest code, we document why and request manual review. We don't hide things.
2. **No publish without approval.** Process lock: Audit → Scope → Approval Gate → Execute.
3. **No feature claims without evidence.** If we say it does something, there's a test proving it.
4. **No "v1.0" until it works end-to-end.** Version numbers reflect reality, not aspirations.

---

## Phase 1: Design (Before Any Code)

### 1.1 Requirements Definition
- [ ] **Single-sentence purpose:** Explain what this does in one line a non-technical person understands
- [ ] **Scope boundary:** Explicitly list what it does NOT do (prevents scope creep)
- [ ] **Target user:** Define who installs this and what they know
- [ ] **Success criteria:** How do we know it's working? (Specific, measurable)

### 1.2 Honest Limitations Document
- [ ] List 3+ things this cannot do
- [ ] List failure modes (what breaks it)
- [ ] List dishonest marketing angles competitors might use vs. our actual capability

### 1.3 Architecture Decision
- [ ] Simplest possible solution that meets requirements
- [ ] Document why more complex approaches were rejected
- [ ] Identify external dependencies and their risk level

**Gate:** Requirements + Limitations + Architecture documented in `/docs/<project>-design.md`

---

## Phase 2: Construction

### 2.1 Test-First Development
- [ ] Write tests before implementation (where possible)
- [ ] Every public function has at least one test
- [ ] Edge cases: empty input, malformed input, oversized input
- [ ] Error cases: what happens when dependencies fail?

### 2.2 Implementation
- [ ] Single responsibility: each module does one thing
- [ ] No magic: explicit over implicit, verbose over clever
- [ ] Input validation: sanitize at boundaries
- [ ] Fail gracefully: never crash the host system

### 2.3 Self-Review Checklist
- [ ] Can I explain every line to a junior developer?
- [ ] Are there any strings that could trigger security scanners? (Document them, don't hide them)
- [ ] Is this deterministic for the same inputs?
- [ ] Would this work if run by a different user on a different machine?

---

## Phase 3: Documentation

### 3.1 README.md (User-Facing)
- [ ] One-line description at the top
- [ ] Quick start: install + run in 60 seconds
- [ ] Honest feature table with checks and X's
- [ ] Limitations section BEFORE the feature list
- [ ] No jargon without definition

### 3.2 SKILL.md (Agent-Facing)
- [ ] What the agent can do with this tool
- [ ] Exact command examples with expected output
- [ ] Error handling: what to tell the user when it fails
- [ ] Integration patterns: how this connects to other tools

### 3.3 Architecture Notes (Internal)
- [ ] Why specific technical decisions were made
- [ ] Known technical debt (tradeoffs accepted)
- [ ] Security considerations documented

---

## Phase 4: Quality Verification

### 4.1 Automated Testing
- [ ] All tests pass
- [ ] No warnings or deprecations
- [ ] Test coverage > 70% for core logic

### 4.2 Manual Testing
- [ ] Install on clean environment (no existing dependencies)
- [ ] Run with realistic inputs
- [ ] Run with adversarial/malformed inputs
- [ ] Verify graceful degradation when a dependency is missing

### 4.3 Security Review
- [ ] No hardcoded credentials
- [ ] No eval/exec/system calls on untrusted data
- [ ] File operations restricted to expected directories
- [ ] Network requests are explicit and documented

---

## Phase 5: Pre-Publication Audit

### 5.1 Run Prepublish Audit Tool
```bash
python3 scripts/prepublish_audit.py <project-dir>
```

### 5.2 Manual Verification
- [ ] Read every file in the release directory
- [ ] Check for accidentally committed files (logs, configs, credentials)
- [ ] Verify version numbers match across all files
- [ ] Confirm no `__pycache__` or build artifacts
- [ ] Verify skill.json matches actual capabilities

### 5.3 Honesty Check
- [ ] Does README use words like "guarantee," "eliminate," "always," "100%"?
- [ ] Are limitations visible in the first 30 seconds of reading?
- [ ] Would a user be surprised by something it CAN'T do?
- [ ] Are benchmark numbers sourced and reproducible?

**Gate:** Audit report documented. Zero unresolved issues.

---

## Phase 6: Approval & Publication

### 6.1 Scope Presentation
Present to Anton:
1. What changed since last version
2. What tests prove it works
3. What the limitations are
4. What could go wrong

### 6.2 Approval Gate
Anton must explicitly approve with one of:
- "Approved for GitHub only" → push to repo, NOT to ClawHub
- "Approved for GitHub + ClawHub" → push to both
- "Needs changes" → back to construction phase

**No publish without explicit approval statement.** "Looks good" or "ok" is NOT approval.

### 6.3 Publication
- [ ] GitHub: commit with descriptive message, push to main
- [ ] ClawHub: only after GitHub approval, use exact version from skill.json
- [ ] Post-publish: verify it installs cleanly, runs correctly

---

## Post-Publication

### Monitoring
- [ ] Check dashboard status within 24 hours
- [ ] Respond to any quality holds with transparency, not obfuscation
- [ ] Collect real user feedback (not just download counts)

### Iteration
- [ ] One bug fix = patch version bump
- [ ] One feature addition = minor version bump
- [ ] Breaking change = major version bump, new approval required

---

## What Destroyed Previous Products (Anti-Pattern Log)

| Failure | Root Cause | Prevention |
|---------|-----------|------------|
| Hallucination Guard "98% detection" | Benchmark fabricated by agent | Tests run separately, results reviewed by human |
| Vetter Plus false claims | Built features before designing them | Requirements doc before code |
| GBrain naming confusion | No documentation of what it actually was | Architecture decisions documented |
| Context Manager scope creep | No explicit "does NOT do" list | Phase 1.2 mandatory |
| Install-sandbox "sandbox" claim | Marketing wrote features, not engineers | Honest limitations before feature list |
| Base64 encoding scandal | Scanner dodge instead of explaining | Rule #1: no obfuscation |
| Benchmark withdrawal overreach | Panic response without process | Approval gate prevents knee-jerk changes |

---

## Onboarding Wizard Success Factors

What went right:
1. **Defined scope early:** "Scans environment, generates checklist, does NOT install"
2. **Honest about limitations:** Clear what it detects vs. what it guesses
3. **Tested thoroughly:** 17 unit tests, manual install verification
4. **Clean architecture:** Separate detection from recommendation from reporting
5. **Transparent docs:** Explained WHY it recommends each skill
6. **No false urgency:** Published when ready, not when pressured
7. **User feedback loop:** Actually iterated based on Anton's testing

---

## Version History

- **v1.0:** Initial process after credibility crisis (2026-05-01)
- **v2.0:** Locked after Onboarding Wizard proved the model works (2026-05-02)

---

*This process is not bureaucracy. It's the pattern that prevents the destruction of our credibility. Violate it only with written justification approved by Anton.*
