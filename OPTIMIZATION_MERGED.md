# OpenClaw Optimization Plan — Merged with Current Work
# Generated: 2026-05-03
# Status: Integration in progress

## ALREADY DONE ✅ (Don't Repeat)

| Plan Item | What We Have | Status |
|-----------|-------------|--------|
| Purpose doc | SOUL.md + USER.md + MEMORY.md + IDENTITY.md | ✅ Exists but scattered |
| Source of truth | SKILLS_REGISTRY.md | ✅ Created today |
| Decision log | docs/anton-todo.md + MEMORY.md | ✅ Exists |
| Security audit | claim-verification-policy.md | ✅ Exists (needs enforcement) |
| Daily memory | Daily cron + summarize_memory.py | ✅ Created today |
| Agent Pathfinder | certainlogic-pathfinder skill | ✅ Built, tested, pending Anton verify |
| Process docs | PROCESS.md v2.0 | ✅ Excellent, needs enforcement |
| Git audit | GIT_CLEANUP_REPORT.md | ✅ Created today |

## OVERLAP — MERGE THESE

**Plan Phase 1.1: PURPOSE.md**  
→ We have SOUL.md (Alex identity), USER.md (Anton profile), MEMORY.md (company history), IDENTITY.md (name/emoji).  
→ **Action:** Merge into single CERTAINLOGIC-PURPOSE.md instead of scattered files.

**Plan Phase 1.2: Source of truth**  
→ We have SKILLS_REGISTRY.md (products), docs/anton-todo.md (tasks), MEMORY.md (company context).  
→ **Action:** Already covered. Just ensure SKILLS_REGISTRY.md stays updated.

**Plan Phase 1.3: Security audit**  
→ We ran full audit today. ClawHub search confirms 3 published skills under certainlogic namespace.  
→ **Action:** Already done. Need to act on findings.

## GAPS — NEW WORK NEEDED

### Phase 2: Coding-Heavy Workflow (This Week)

**4. Dedicated Coder sub-agent**  
→ **Status:** NOT BUILT  
→ **Priority:** HIGH  
→ **What:** Create agent that ONLY handles coding tasks, has Pathfinder + Hallucination Guard mandatory  
→ **Files needed:** `agents/coder/SOUL.md`, agent config  
→ **Blocked by:** Need to confirm if Hallucination Guard is ready (was retired in April)

**5. Coding gates in main orchestrator**  
→ **Status:** NOT BUILT  
→ **Priority:** HIGH  
→ **What:** Main agent (me) must propose code solution before any non-coding task  
→ **Files needed:** Update AGENTS.md with routing rules  
→ **Blocked by:** Anton needs to approve the gate language

**6. Memory hygiene rules**  
→ **Status:** PARTIAL (cron exists, no pruning rules)  
→ **Priority:** MEDIUM  
→ **What:** Daily logs = raw. MEMORY.md = only verified facts. Weekly prune.  
→ **Files needed:** Update AGENTS.md or MEMORY.md with hygiene rules  
→ **Blocked by:** Need to define "live primitive or decision" criteria

**7. Integrate own tools**  
→ **Status:** PARTIAL (Pathfinder works, Hallucination Guard retired)  
→ **Priority:** HIGH  
→ **What:** Pathfinder must run on every task output. Hallucination Guard on all code gen.  
→ **Blocked by:** Hallucination Guard was retired (April 24). Is it being rebuilt?

### Phase 3: Monitoring & Scaling (Next 2-4 Weeks)

**8. Dashboard + weekly review**  
→ **Status:** NOT BUILT  
→ **Priority:** MEDIUM  
→ **What:** Coder sub-agent generates weekly performance report (coding % vs business %, audit integrity)  
→ **Blocked by:** Phase 2 completion

**9. Model routing**  
→ **Status:** NOT BUILT  
→ **Priority:** LOW (current model works)  
→ **What:** Coder → coding model (Claude Code/Codex), Orchestrator → lighter model  
→ **Blocked by:** Need model budget decisions from Anton

**10. Verifiable hand-off protocol**  
→ **Status:** PARTIAL (claim verification policy exists, not enforced)  
→ **Priority:** HIGH  
→ **What:** Every non-coding task ends with: "Signed receipt via Pathfinder + proposed code next step"  
→ **Blocked by:** Need Anton to enforce, not just document

## MERGED PRIORITY LIST (This Week)

1. **Cleanup git repo** (GIT_CLEANUP_REPORT.md) — Anton approves, Alex executes  
   → TODAY

2. **Verify published skills** (AUDIT_PLAN.md) — Anton on clean machine  
   → TONIGHT after work

3. **Create CERTAINLOGIC-PURPOSE.md** — Merge SOUL.md + USER.md + IDENTITY.md + Company Brain thesis  
   → Alex drafts, Anton approves  
   → TOMORROW

4. **Build Coder sub-agent** — New agent profile, coding-only, mandatory Pathfinder  
   → Alex builds  
   → After git cleanup

5. **Update AGENTS.md with coding gates** — "Propose code solution first" rule  
   → Alex drafts, Anton approves  
   → After Coder sub-agent

6. **Hallucination Guard status** — Is it being rebuilt or replaced?  
   → Anton decides  
   → BEFORE Phase 2 completion

7. **Memory hygiene rules** — Define pruning criteria, add to AGENTS.md  
   → Alex drafts  
   → After coding gates

8. **Weekly review automation** — Dashboard report generation  
   → Future, after core infra solid

## QUESTIONS FOR ANTON

1. **Hallucination Guard** — Retired April 24. Is it being rebuilt, or should we remove references from the plan?

2. **Coder sub-agent scope** — Should it handle ALL coding (Pathfinder, dashboard, tools) or only certain types?

3. **Model routing** — Want to stick with current Kimi K2.6 default, or split by task type? (Costs vs quality tradeoff)

4. **Non-coding business tasks** — What percentage of your daily work is non-coding? (If <20%, maybe we don't need heavy separation)

## CURRENT STATUS

- Path 1: Git cleanup + skill audit → Anton action needed
- Path 2: Optimization plan → New work, needs Anton decisions on scope
- Path 3: Both in parallel → Do audit tonight, start optimization tomorrow

## RECOMMENDATION

**Do the audit tonight (Path 1)**, then start Phase 2 of optimization plan tomorrow. Don't try to build everything at once — the plan explicitly says "piecemeal > complete."

Ready to proceed with whichever Anton chooses.
