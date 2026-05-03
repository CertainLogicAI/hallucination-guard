# CertainLogic Quality Lockdown — Audit Plan
# Prepared: 2026-05-03
# Owner: Anton
# Goal: Verify every published skill installs and runs on a clean machine

## Published Skills — Corrected Classification

| # | Slug | Type | Status | Action |
|---|------|------|--------|--------|
| 1 | certainlogic-onboarding-wizard | **Tool** | ✅ Visible | VERIFY — not on local machine yet |
| 2 | certainlogic-smart-router | **Tool** | ⚠️ Quality held | VERIFY — has code + tests |
| 3 | skill-oracle | **Documentation** | ✅ Visible | RECLASSIFY — MD-only by design |
| 4 | pa-pack | **Documentation** | ✅ Visible | RECLASSIFY — recommendations pack |
| 5 | skill-vetter-plus | **Tool** | 🔴 Suspicious | VERIFY — flagged by ClawHub scanner |
| 6 | certainlogic-context-tokenreducer | **Tool** | ✅ Visible | VERIFY — not on local machine yet |

## Verification Protocol (Per Claim-Verification Policy)

For each TOOL skill, do ALL of these:
1. **Install fresh** — `clawhub install <slug>` on clean machine
2. **Run main features** — execute exact commands from README/SKILL.md
3. **Verify output** — output must match documented behavior
4. **Check limits** — confirm what it does NOT do (matches docs)
5. **Document** — pass/fail, gaps found, in this file

## Clean Machine Setup

### Step 0: Prepare Machine (Tonight)
```bash
# Ensure clawhub CLI is installed
clawhub --version

# Clear any previous installs of our skills
clawhub uninstall certainlogic-onboarding-wizard 2>/dev/null
clawhub uninstall certainlogic-smart-router 2>/dev/null
clawhub uninstall skill-vetter-plus 2>/dev/null
clawhub uninstall certainlogic-context-tokenreducer 2>/dev/null

# Create audit directory
mkdir -p ~/certainlogic-audit
cd ~/certainlogic-audit
```

### Step 1: Skill #1 — Onboarding Wizard
```bash
clawhub install certainlogic-onboarding-wizard
cd ~/.openclaw/skills/certainlogic-onboarding-wizard
ls -la  # Check files exist
cat SKILL.md | head -20  # Read what it claims
# Run whatever command SKILL.md says is the main feature
# Document result below
```

**Expected:** ?
**Actual:** ?
**Pass/Fail:** ?
**Notes:**

---

### Step 2: Skill #2 — Smart Router
```bash
clawhub install certainlogic-smart-router
cd ~/.openclaw/skills/certainlogic-smart-router
ls -la
cat SKILL.md | head -20
# Main feature test:
python3 -m pytest tests/ -v
# Additional manual test per SKILL.md
```

**Expected:** Tests pass, routing works
**Actual:** ?
**Pass/Fail:** ?
**Notes:**

---

### Step 3: Skill #5 — Skill Vetter Plus
```bash
clawhub install skill-vetter-plus
cd ~/.openclaw/skills/skill-vetter-plus
ls -la
cat SKILL.md | head -20
# Main feature test:
python3 scripts/vetter.py /path/to/skill --json
# Document if it flags false positives
```

**Expected:** Scans skills, reports real issues, minimal false positives
**Actual:** ?
**Pass/Fail:** ?
**Why Suspicious:** ? (document ClawHub's reasoning)
**Notes:**

---

### Step 4: Skill #6 — Context Token Reducer
```bash
clawhub install certainlogic-context-tokenreducer
cd ~/.openclaw/skills/certainlogic-context-tokenreducer
ls -la
cat SKILL.md | head -20
# Main feature test: ?
```

**Expected:** ?
**Actual:** ?
**Pass/Fail:** ?
**Notes:**

---

## Documentation Skills (No Code Expected)

### Skill #3 — Skill Oracle
- Type: Markdown documentation
- Purpose: Curated skill recommendations
- Verify: `clawhub install` → `cat SKILL.md` → content is useful
- **No tool execution needed**

### Skill #4 — PA Pack
- Type: Markdown documentation
- Purpose: Toolkit recommendations for business owners
- Verify: `clawhub install` → `cat SKILL.md` → content is useful
- **No tool execution needed**

---

## Pass Criteria Summary

| Skill | To Pass |
|-------|---------|
| Onboarding Wizard | Installs, main feature runs, output matches docs |
| Smart Router | Installs, all tests pass, manual feature works |
| Skill Vetter Plus | Installs, scans correctly, flags are reasonable |
| Context Token Reducer | Installs, main feature works |
| Skill Oracle | MD-only, content is useful/accurate |
| PA Pack | MD-only, content is useful/accurate |

## After Audit — Decision Matrix

| Result | Action |
|--------|--------|
| Tool passes all checks | Update SKILLS_REGISTRY.md, keep published |
| Tool fails but fixable | Fix within 48 hrs, re-verify, then publish |
| Tool fails and unfixable | Unpublish immediately |
| Doc skill outdated | Update content, keep published |
| Doc skill useless | Unpublish |

---

## Notes Area

(Add your findings below as you test)

### 2026-05-03 Evening Session


### 2026-05-04 Evening Session


### 2026-05-05 Evening Session


