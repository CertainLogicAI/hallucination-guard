# Anton's Decision Checklist — B1-B6

**Created:** 2026-05-04  
**Purpose:** Clear action items for Anton to unblock CertainLogic process recovery  
**Status:** ☐ OPEN — awaiting decisions  

---

## B1 — Skill Audit on Clean Machine
**What:** Test Pathfinder install on personal machine (not workspace server)  
**Why:** Verify published skill installs cleanly for real users  
**Document:** `AUDIT_PLAN.md` (already written, 4.6KB)  

### Steps
☐ Read `AUDIT_PLAN.md` in repo root (takes 2 min)  
☐ Open personal machine (not workspace server)  
☐ Run commands from AUDIT_PLAN.md Step-by-Step  
☐ Record results: PASS / FAIL / PARTIAL  
☐ Report back to Alex with findings  

**Expected time:** 10-15 minutes  
**Do this:** Tonight after work  

---

## B2 — Delist smart-router from ClawHub
**What:** Remove `certainlogic-smart-router` from ClawHub marketplace  
**Why:** Quality hold since April 24, not a viable product  

### Steps
☐ Open browser → navigate to clawhub.ai  
☐ Log into ClawHub account (@blenderism / CertainLogic)  
☐ Go to "My Skills" or "Published Skills"  
☐ Find `certainlogic-smart-router`  
☐ Click "Delist" or "Unpublish" or "Remove"  
☐ Confirm delisting  
☐ Screenshot confirmation, save to `docs/`  
☐ Tell Alex "smart-router delisted"  

**Alternative if no web UI option:**  
☐ Email clawhub support: support@clawhub.ai  
☐ Subject: "Delist request: certainlogic-smart-router"  
☐ Body: "Please delist certainlogic-smart-router from account [your account]. Quality hold since April 24, product retired."  

**Do this:** Within 48 hours  

---

## B3 — Delist pa-pack from ClawHub
**What:** Remove `pa-pack` from ClawHub marketplace  
**Why:** Not a functional product — just documentation of external tools  

### Steps
☐ Same process as B2  
☐ Find `pa-pack` instead of `smart-router`  
☐ Confirm delisting  
☐ Tell Alex "pa-pack delisted"  

**Do this:** Same session as B2  

---

## B4 — Hallucination Guard Decision
**What:** Decide fate of Hallucination Guard (deterministic factual validation layer)  
**Context:** Retired April 24 after Hermes benchmark destruction. Currently TRE uses graceful fallback (`try/except ImportError`) when module missing.  

### Options
☐ **A. REBUILD** — Rewrite Hallucination Guard with lessons learned (schema-based validation, better regex, smaller scope). Effort: 1-2 days.  
☐ **B. REPLACE** — Use external hallucination detection (e.g., grounding APIs, RAG verification). Effort: 1 day integration.  
☐ **C. REMOVE** — Accept that TRE's graceful fallback + hybrid routing is sufficient. No dedicated hallucination layer. Effort: 0. Already done.  

### Decision needed
☐ Pick A, B, or C  
☐ If A or B: prioritize in Phase 2 (next week)  
☐ If C: close this item, remove from future roadmaps  

**Recommendation from Alex:** Option C for now. TRE's `try/except` works. Brain API handles factual consistency via facts_db. Revisit only if factual errors spike.  

**Do this:** Reply with "A", "B", or "C"  

---

## B5 — Model Routing Strategy
**What:** Decide default model and task-based routing  
**Context:** Currently Kimi K2.6 default. Options exist for free/cheaper models.  

### Options
☐ **A. SINGLE MODEL** — Keep Kimi K2.6 as default for everything. Simple, predictable.  
☐ **B. SPLIT BY TASK** — Route by query type:  
  - Coding queries → Kimi K2.6 (strong reasoning)  
  - Simple/factual → Haiku 4.5 or Ling-2.6-Flash (fast, cheap)  
  - Complex reasoning → Opus 4.6 (best quality, expensive)  
  - TRE routing already decides internal/external — extend for model selection  
☐ **C. COST-OPTIMIZED** — Use free models where possible,付费 only for complex. Risk: quality inconsistency.  

### Decision needed
☐ Pick A, B, or C  
☐ If B or C: Alex updates routing logic in TRE + Brain API  

**Recommendation from Alex:** Option B with conservative thresholds. Start with Kimi default, add Haiku for simple queries, measure quality.  

**Do this:** Reply with "A", "B", or "C"  

---

## B6 — Merge cleanup_complete → main
**What:** Merge 48 commits from `cleanup_complete` branch to `main` (or `master`)  
**Context:** 157 files cleaned down to ~0. 39 commits on branch. Anton wanted to wait until after audit.  

### Prerequisites
☐ B1 complete (audit passes) OR Anton accepts risk  
☐ Review last 5 commits: `git log --oneline -5 cleanup_complete`  

### Steps
☐ Review commit history (`git log --oneline cleanup_complete`)  
☐ Verify no sensitive files in history  
☐ Alex runs: `git checkout main && git merge cleanup_complete`  
☐ Fix any merge conflicts (unlikely — main was untouched)  
☐ Push to origin  
☐ Verify: `git status` clean on main  

### Decision needed
☐ **APPROVE MERGE** — Alex merges now (or after B1)  
☐ **WAIT** — Keep `cleanup_complete` as working branch until after audit  
☐ **NEVER MERGE** — Keep branches separate (not recommended)  

**Do this:** Reply with "MERGE", "WAIT", or "NEVER"  

---

## Quick Reference — How to Complete This Checklist

1. Reply to Alex with decisions: "B4: C, B5: B, B6: WAIT" etc.
2. For B1: Run audit tonight, report back tomorrow morning.
3. For B2+B3: Log into clawhub.ai when convenient (5 min task).
4. Alex updates `PROCESS_LOG.md` moving items from Blocked → Completed.
5. Once B1-B6 done, Phase 1 (P1-P4) execution begins.

---

## Decision Summary (Fill in and send to Alex)

| Item | Decision | Notes |
|------|----------|-------|
| B1 — Clean machine audit | ☐ Will do tonight / ☐ Skip | |
| B2 — Delist smart-router | ☐ Doing now / ☐ Skip | |
| B3 — Delist pa-pack | ☐ Doing now / ☐ Skip | |
| B4 — Hallucination Guard | ☐ A / ☐ B / ☐ C | |
| B5 — Model Routing | ☐ A / ☐ B / ☐ C | |
| B6 — Merge branch | ☐ MERGE / ☐ WAIT / ☐ NEVER | |
