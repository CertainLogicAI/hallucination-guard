# Anton's To-Do List (Updated 2026-05-03)

## In Progress (Alex working today 2026-05-03)
- [x] **Audit plan prepared** — AUDIT_PLAN.md ready for Anton's clean machine testing
- [x] **SKILLS_REGISTRY corrected** — Skill Oracle & PA Pack reclassified as documentation
- [x] **Git cleanup report** — GIT_CLEANUP_REPORT.md created, awaits Anton approval
- [x] **Smart Router delist** — ClawHub CLI has no unpublish, need web UI or support
- [x] **PA Pack delist** — ClawHub CLI has no unpublish, need web UI or support
- [ ] **Investigate smart-router quality hold** — code is clean, likely auto-hold for simple tools
- [ ] **Investigate skill-vetter-plus suspicious flag** — ClawHub security scanner false positive analysis
- [ ] **Pathfinder final polish** — docs, install script, ready for Anton verification
- [ ] **HEARTBEAT.md expansion** — add skill/flag/install checks

## Delist Queued (Pending Anton Action)
- [ ] **certainlogic-smart-router** — quality held, needs proper trial before relist
- [ ] **pa-pack** — removed per Anton decision
- Note: ClawHub CLI has no `unpublish` command. Must use web UI or contact support.

## AgentPathfinder (Near Ready — Needs Anton's Clean Machine Test)
- [x] **Fix conflicting old package** — moved /data/.openclaw/workspace/agentpathfinder to .old-april25
- [x] **Verify clean install** — tested in fresh venv, pip install -e . works
- [x] **CLI works** — `pf create/status/audit` verified
- [x] **17 tests pass** — in clean environment
- [ ] **Customer install test on fresh machine** — YOU need to verify this (tonight)
- [ ] **Dashboard UX** — works when you copy HTML to your machine and open in browser
- [ ] **Get approval before publish** — per claim-verification policy

## Premium Products (Roadmap — Do NOT Publish Yet)
- [ ] **skill-auditor** — empty, needs full implementation
- [ ] **cold-outreach-pro** — empty, needs full implementation
- [ ] **market-research-pro** — empty, needs full implementation
- [ ] **seo-audit-pro** — empty, needs full implementation
- [ ] **ai-visibility-pro** — empty, needs full implementation
- [ ] **x-monitor-pro** — empty, needs full implementation

## Infrastructure
- [x] **Daily memory cron** — created, runs every 24 hours
- [ ] **Fix onboarding-wizard & context-manager** — not on this machine, need to locate

## Credentials Still Needed
- [ ] **X API tokens** — all 4 values
- [ ] **Stripe account** — for certainlogic.ai shop
- [ ] **GitHub repo + Cloudflare Pages** — for site launch

## No Longer Relevant (archived)
- ~~Relist hallucination-guard~~ — killed, not viable
- ~~Relist certainlogic-verifier~~ — killed, not viable
