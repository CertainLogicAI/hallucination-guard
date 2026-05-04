# CertainLogic Repo Conventions

**Purpose:** Prevent the git disorganization and duplicate files situation from ever recurring.
**Status:** Enforced from 2026-05-04 forward.

---

## Rules

### 1. Generated Files Never Tracked
**What:** `__pycache__/`, `*.pyc`, `*.pyo`, `cache.db`, `*.log`, `workspace-cache.json`  
**How:** Already in `.gitignore`. Never `git add` them.  
**Enforcement:** HEARTBEAT alert if >20 uncommitted files.

### 2. Single Source of Truth for Skills
**What:** `SKILLS_REGISTRY.md` is the ONLY canonical list.  
**Rules:**
- `skills/` = current development directory
- `skills-publish/` = ephemeral publish staging ONLY
- Never commit the same skill to both locations
- After publishing, delete from `skills-publish/` (not commit)
- Before any skill work, check `SKILLS_REGISTRY.md`

### 3. Retired Projects → Archive Immediately
**What:** When a project is dead/killed/obsoleted:  
**How:**
```bash
mv ./dead-project/ archive/retired-projects/    # or
mv ./dead-skill/ archive/retired-skills/
```
**When:** Within 24 hours of retirement decision.  
**Never leave old code in root directory.**

### 4. Submodules Stay in Their Own Repos
**What:** `patent_filings/`, `certainlogic-site/`  
**How:** `.gitignore` them in main repo. Work inside them, commit there, never commit to main repo.

### 5. Commit Before EOD
**Rule:** End of every workday (even if partial), commit changes:  
```bash
git add <relevant files>
git commit -m "<action>: <what was done today>"
```
**Why:** Prevents 157-file accumulation. Small commits are fine.

### 6. No Duplicate Module Copies
**What:** One copy of any module. Period.  
**Enforcement:** If Brain API uses its own internal `hallucination_detector.py`, the workspace MUST NOT have a second copy. If it exists → archive or delete immediately.

---

## Daily Checks (Automated)

Already active:
- **Git health** → HEARTBEAT checks daily. Alert if >20 uncommitted.
- **Skills registry sync** → Cron adds to nightly summary.
- **Coding query tracker** → Daily hit rate report.

---

## Violation Log

| Date | Violation | Fix |
|------|-----------|-----|
| 2026-05-03 | `hallucination_detector.py` duplicate (workspace + Brain internal) | Archived workspace copy |
| | `skills/` vs `skills-publish/` duplicates | Archived `skills-publish/` |
| | `agentpathfinder.old-april25/` conflicting package moved aside, not deleted | Archived |
| | 157 uncommitted files | Aggressive cleanup session |

---

## How to Propose Changes

Edit this file (CONVENTIONS.md) via pull request / Anton approval.
