# CertainLogic Quality Rules — Effective 2026-04-29

## Rule 1: No "Done" Without Audit

A project is NOT done until:
1. Scope/spec sheet is compared line-by-line against delivered code
2. README is compared line-by-line against delivered code
3. Every CLI command in docs has been run and verified
4. Security self-scan passed on own code
5. Anton has reviewed the audit report

**Violations:** The install-sandbox was reported "done" without checking if it matched the scope doc (sandbox vs scanner). AgentPathfinder was reported "clean" without checking what files were actually in the package.

---

## Rule 2: Honest Naming

**If the scope says X, the code must be X.**

| Scope Says | Code Must Be | If Not Possible |
|-----------|-------------|----------------|
| Sandbox | Runtime isolation (namespaces, tmpfs, network block) | Rename scope to "scanner" BEFORE building |
| Dashboard | Live HTML UI | Don't call CLI output a dashboard |
| Pro feature | Paywalled/license-checked | Don't include in free package |
| Free forever | No payment required | Don't hardcode Stripe integration |

**Violations:** Called a temp directory a "sandbox." Called a static report a "dashboard."

---

## Rule 3: README Last, Not First

**Order:**
1. Write scope/spec
2. Build code that matches scope
3. Test everything
4. Write README based on what ACTUALLY works
5. Audit README against code
6. Publish

**Violations:** README for install-sandbox claimed tmpfs/namespaces before code existed. README for AgentPathfinder said "Upgrade for dashboard" while including dashboard code.

---

## Rule 4: Publish Checklist (Mandatory)

Every ClawHub publish requires:

- [ ] All scope items implemented and tested
- [ ] README claims verified against code (trace every sentence to a function)
- [ ] Every CLI command tested in clean environment
- [ ] Install from scratch works (`pip install -e .` or `clawhub install`)
- [ ] Security self-scan passed (run scanner on own code)
- [ ] SKILL.md YAML validates (`python -c "import yaml; yaml.safe_load(...)")`
- [ ] No localhost/127.0.0.1 in code or config (security flag)
- [ ] No hardcoded secrets or API keys
- [ ] Version bumped (no silent updates)
- [ ] Git tagged with version (`git tag v1.0.0`)
- [ ] Anton reviews and approves audit report

---

## Rule 5: Clean Install Test

Before publish, verify in fresh environment:

```bash
# Create isolated test
python3 -m venv /tmp/test-install
source /tmp/test-install/bin/activate
pip install -e .

# Test every CLI command
skill-name --help
skill-name init
skill-name run
# ... etc

# Verify what's actually installed
find /tmp/test-install/lib -name "*.py" | grep -v __pycache__ | sort
```

**Why:** Would have caught Pro dashboard in free package immediately.

---

## Rule 6: Scope Change = Rename, Not Lie

If scope exceeds effort/bandwidth:
1. Rename the feature to match what you'll actually build
2. Update scope doc
3. Get Anton approval on reduced scope
4. Build honest version

**Never:** Keep the impressive name, deliver less, and hope nobody notices.

**Violations:** "Sandbox" scope → "scanner" delivery with "sandbox" name kept.

---

## Rule 7: Third-Party Audit After Clean Install

Before considering anything "done":
1. Install from scratch (Rule 5)
2. Hand it to someone else (or fresh eyes) to test
3. They try to break it without reading docs
4. Fix everything they find confusing or broken

**Violations:** install-sandbox `install` command would have crashed immediately if anyone ran it.

---

## Rule 8: No Publish Without Sign-Off

**Chain:**
1. Alex builds
2. Alex audits (Rule 4 checklist)
3. Alex writes audit report
4. Anton reviews audit report
5. Anton approves (or sends back)
6. Publish

**No shortcuts. No "trust me, it works."** Show the audit report.

---

## Rule 9: Version Discipline

- Every code change = version bump (even README fixes)
- Git tag matches ClawHub version exactly
- No "I'll fix it later" — if it's broken, fix before next version
- Deprecated skills get final version with deprecation notice, then deletion

**Violations:** Multiple silent fixes to AgentPathfinder and TRE without version bumps.

---

## Rule 10: Honest Retrospectives

When something goes wrong:
1. Write it down (like this file)
2. Identify the exact rule that would have prevented it
3. Add that rule
4. Enforce it on the next project

**Not:** "Oops, won't happen again." → Write the rule so it literally can't.

---

## Current Status

**All CertainLogic skills delisted from ClawHub (2026-04-29).**

Nothing gets republished until:
1. Code matches scope exactly
2. Audit report is complete
3. Anton approves

**Violations of these rules = immediate work stoppage + written explanation.**

Signed: Alex
Date: 2026-04-29 03:57 EDT
