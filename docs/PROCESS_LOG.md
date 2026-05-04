# Process Recovery & Solid Footing — Active Log

**Initiated:** 2026-05-04  
**Goal:** Get CertainLogic to organized, efficient state before resuming product builds.  
**Status:** In progress — this file is the single source of truth for process recovery.  

---

## System State Check (Last Verified: 2026-05-04 12:55 UTC)

| Component | Status | Detail |
|-----------|--------|--------|
| Brain API | ✅ Healthy | 84 facts, all components ok |
| Git branch | `cleanup_complete` | 48 commits, do NOT merge yet |
| Uncommitted files | ✅ Good | 2 files (submodules, under threshold) |
| Crons | ✅ Fixed | 6 failing crons fixed (delivery mode → none) |
| Coding tracker | ✅ Active | 2 queries logged today (new) |
| Hallucination detector | ✅ Fixed | Restored as runtime dep, committed |
| Telegram | ❌ Not paired | Agent can't send messages |
| ClawHub | ✅ Connected | Pathfinder published |

---

## Completed Today (2026-05-04)

- [x] HEARTBEAT checks (3x) — all healthy
- [x] Fixed 5 broken crons (metrics-snapshot, nightly-summary, coding-tracker, cache-builder, cache-harvest)
- [x] Fixed hallucination_detector.py ImportError (critical — was archived as "duplicate," actually runtime dep)
- [x] Added hallucination_detector.py back to .gitignore → removed (now tracked as runtime dep)
- [x] Created CONVENTIONS.md (repo hygiene rules, prevents future disorganization)
- [x] Created IMPROVEMENTS.md (12 gaps identified, prioritized)
- [x] Created ASSET_SYSTEM.md (modular compounding framework)
- [x] Created agent-first marketing research (docs/research/)
- [x] Git committed: 4 commits (conventions, improvement scan, critical fix, asset system)

---

## Open Items (Categorized)

### Blocked — Waiting on Anton

| # | Item | Why Blocked | What Anton Needs to Do |
|---|------|-------------|------------------------|
| B1 | Skill audit on clean machine | Only Anton has personal machine access | Run AUDIT_PLAN.md tonight after work, report back |
| B2 | Delist smart-router from ClawHub | ✅ DONE | `clawhub delete certainlogic-smart-router --yes` — Success |
| B3 | Delist pa-pack from ClawHub | ✅ DONE | `clawhub delete pa-pack --yes` — Success |
| B4 | Hallucination Guard | ✅ DECIDED | Log as asset in ASSET_SYSTEM.md. Don't sell standalone. Integrate into Brain API. |
| B5 | Model routing | ✅ DECIDED | Kimi (coding/arch), Grok (marketing/biz), Free (crons/lower tier) |
| B6 | Merge branch | ✅ DECIDED | WAIT until after B1 clean machine audit |

### Process — Do Next (Before Building Products)

| # | Item | Priority | Why Critical | Effort |
|---|------|----------|--------------|--------|
| P1 | Build single `requirements.txt` | HIGH | Fresh venv would fail — prevents "works on my machine" | 15 min |
| P2 | Write unit tests for critical scripts | HIGH | 16 scripts, 1 test. Cron failures go silent until someone notices. | 2-3 hrs |
| P3 | Create `ONBOARDING.md` | MEDIUM | No one (including Anton in 3 months) knows how repo works. Chaos multiplies. | 1 hr |
| P4 | Rename `master` → `main` | MEDIUM | Standard practice, prevents confusion. Low risk with current branch structure. | 5 min |
| P5 | Document Brain API OpenAPI spec | MEDIUM | Agent-first marketing requires this. Also helps any external integration. | 1-2 hrs |
| P6 | Build `/llms.txt` for certainlogic.ai | MEDIUM | Quick win for agent-first marketing. | 30 min |
| P7 | Process dashboard (health overview) | MEDIUM | Single command shows all system health. Prevents silent failures. | 2 hrs |
| P8 | Backup restore test | LOW | Verifies B2 backups actually work. Do monthly. | 30 min |
| P9 | Add linting standards (ruff/black) | LOW | Readability + style consistency. | 30 min |
| P10 | CI/CD pipeline (GitHub Actions) | LOW | Only matters when repo is public. Can wait. | 2 hrs |

### Product — After Process Complete

| # | Item | Depends On |
|------|------|------------|
| Prod1 | Agent-first marketing implementation (llms.txt, plugins, registries) | P6, P5 |
| Prod2 | FaultTrace standalone components evaluation | Prod discussion with Anton |
| Prod3 | Pathfinder standalone components (dashboard, tool audit) | Prod discussion |
| Prod4 | Brain API SaaS packaging (TRE as standalone) | P1, P5 |
| Prod5 | Company Brain Plugin (Chunk 1) | P1, P2, P5 |
| Prod6 | Revive MCP Server if demand | Asset system audit |

---

## Recommended Priority Order

**Phase 1: Solid Footing (This Week)**
1. ☐ Alex updates ASSET_SYSTEM.md to log Hallucination Guard + Validator as assets — DECIDED B4
2. ☐ Alex adds model routing config: Kimi (coding/arch), Grok (marketing/biz), Free (crons) — DECIDED B5
3. ☐ Alex builds P1 `requirements.txt` (15 min)
4. ☐ Alex writes P2 unit tests — start with `coding_query_tracker.py` (2-3 hrs)
5. ☐ Alex creates P3 `ONBOARDING.md` (1 hr)
6. ☐ Alex renames branch P4 `master` → `main` (5 min)
7. ☐ Anton runs B1 clean machine audit tonight

**Phase 2: Infrastructure Docs (Next Week)**
6. ☐ Alex builds P5 OpenAPI spec for Brain API (1-2 hrs)
7. ☐ Alex builds P6 `/llms.txt` (30 min)
8. ☐ Alex builds P7 process dashboard (2 hrs)
9. ☐ Alex runs P8 backup restore test (30 min)

**Phase 3: Polish (Following Week)**
10. ☐ Alex adds P9 linting standards (30 min)
11. ☐ Alex sets up P10 CI/CD (2 hrs)

**Phase 4: Build Products (After Phase 3)**
12. ☐ Implement agent-first marketing (Prod1)
13. ☐ Evaluate component decomposition (Prod2, Prod3)
14. ☐ Begin Company Brain Plugin Chunk 1 (Prod5)

---

## Active Rules (From CONVENTIONS.md)

1. Generated files → `.gitignore` forever
2. Single source of truth for skills (`SKILLS_REGISTRY.md`)
3. Retired projects → `archive/` within 24h
4. Submodules stay in their own repos
5. Commit before EOD (even partial progress)
6. Verify imports before archiving `.py` files
7. Track all assets in `ASSET_SYSTEM.md`
8. Daily memory summaries required

---

## Log of Process Recovery Decisions

| Timestamp | Decision | Made By | Rationale |
|-----------|----------|---------|-----------|
| 2026-05-04 07:40 UTC | Keep `cleanup_complete` as working branch, don't merge until after audit | Anton (approved) | Safety — verify nothing breaks first |
| 2026-05-04 07:49 UTC | Create CONVENTIONS.md to prevent future git disorganization | Alex (implemented) | 157-file incident must not repeat |
| 2026-05-04 08:02 UTC | Fix hallcination_detector.py as critical runtime dependency | Alex (confirmed by Anton) | main.py imports directly — no fallback |
| 2026-05-04 08:08 UTC | Create IMPROVEMENTS.md — systematic gap list | Alex | Need visibility into what's broken |
| 2026-05-04 08:38 UTC | Fix 6 crons by setting delivery mode to `none` | Alex | Silent failures were hiding real problems |
| 2026-05-04 08:50 UTC | Create ASSET_SYSTEM.md — modular compounding framework | Alex (clarified as plan, not built) | Anton needs clarity before building |
| 2026-05-04 10:09 UTC | B4: Don't sell Guard/Validator standalone, log as asset, integrate into Brain API | Anton | These are features not products |
| 2026-05-04 10:09 UTC | B5: Tiered model routing — Kimi (coding/arch), Grok (marketing/biz), Free (crons) | Anton | Right tool for right job |
| 2026-05-04 10:09 UTC | B6: WAIT on merge cleanup_complete → main | Anton | Wait until after B1 audit passes |
| 2026-05-04 10:09 UTC | B2+B3: Delisted smart-router and pa-pack via clawhub CLI | Alex | Dashboard had no option, CLI worked |

---

## Next Action Required

**Anton:** Decide on B1-B6 (audit + delist + decisions) so we know what to execute.

**Alex:** Standing by. Can proceed with P1-P4 while Anton decides on blockers.

---

**How to update this file:**
- Check off completed items: change `☐` → `✅`
- Add new blocked items under "Blocked — Waiting on Anton"
- Add new process items under "Process — Do Next"
- Log decisions in "Log of Process Recovery Decisions"
- Commit after each update: `git add docs/PROCESS_LOG.md && git commit -m "process: update PROCESS_LOG — [what changed]"`
