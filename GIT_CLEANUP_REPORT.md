# Git Cleanup Report
## Generated: 2026-05-03
## Status: 146 files need attention

---

## Executive Summary

**Tracked (modified/deleted):** 17 files  
**Untracked:** 127 files  
**Total:** 146 files

**Risk Assessment:**
- 🔴 **High risk:** Generated files (pycache), old backups, duplicates
- 🟡 **Medium risk:** Uncommitted docs, scripts, configs
- 🟢 **Low risk:** Skills directories (already tracked in .clawhub)

---

## Category 1: Generated Files (DELETE IMMEDIATELY)

These should never be in git — add to .gitignore if not already there.

| File | Action | Why |
|------|--------|-----|
| `tests/__pycache__/` | **DELETE** | Compiled Python cache |
| `opensource/src/hallucination_guard/__pycache__/` | **DELETE** | Compiled Python cache |
| `opensource/scripts/__pycache__/` | **DELETE** | Compiled Python cache |
| `opensource/benchmarks/__pycache__/` | **DELETE** | Compiled Python cache |
| `__pycache__/` (4 files) | **DELETE** | Compiled Python cache |

**Script to clean:**
```bash
find /data/.openclaw/workspace -type d -name "__pycache__" -exec rm -rf {} +
```

---

## Category 2: Old Backups & Duplicates (ARCHIVE OR DELETE)

| File | Action | Why |
|------|--------|-----|
| `agentpathfinder.old-april25/` | **DELETE** | Old conflicting package, moved aside |
| `facts_db_backup_85.json` | **ARCHIVE** | Old backup, date in filename |
| `archive/facts_trivia_2026-04-30.json` | **KEEP in archive/** | Already in archive directory |
| `faulttrace-l5x/` | **VERIFY** | Is this old or current? |
| `gbrain/` | **VERIFY** | Is this old or current? |
| `agentpathfinder_dashboard.html` | **DELETE** | Generated file, recreate on demand |

---

## Category 3: Documentation Files (COMMIT)

34 files in `docs/` — all documentation and planning. Should be committed.

**Key docs to commit:**
- `docs/claim-verification-policy.md` ✅ Critical
- `docs/audit_report_2026-04-29.md` ✅ Audit trail
- `docs/audit_yc_readiness.md` ✅ YC prep
- `docs/agentpathfinder-*` (5 files) ✅ Product specs
- `docs/yc-application-summer-2026.md` ✅ YC application

**Maybe archive:**
- `docs/ideas/` — brainstorms, may be outdated
- `docs/btc-trading-scope.md` — off-topic?
- `docs/restaurant-inventory-assessment.md` — off-topic?

---

## Category 4: Scripts (COMMIT)

12 files in `scripts/` — utility scripts. Most should be committed.

**Should commit:**
- `scripts/prepublish_audit.py` ✅ Quality gate
- `scripts/summarize_memory.py` ✅ Daily cron
- `scripts/product_health.py` ✅ Monitoring
- `scripts/system_health.py` ✅ Monitoring

**Maybe delete (obsolete):**
- `scripts/agent_self_improve.py` ❓ Uses retired auto-improve cron
- `scripts/agent_learn.py` ❓ May be old
- `scripts/auto_build.py` ❓ May conflict with PROCESS.md v2.0

---

## Category 5: Skills Directories (VERIFY)

These are the actual skill code. Most are in `.openclaw/skills/` but some copies are in workspace.

**Check for duplicates:**
- `skills/` vs `skills-publish/` — which is source of truth?
- `skills-publish/` contains 18 files including published and retired skills

**Recommended action:**
- `skills-publish/` should be **archived** once we have SKILLS_REGISTRY.md
- Keep `skills/` as current development directory
- Retired skills (hallucination-guard-v2, install_sandbox) should move to `archive/`

---

## Category 6: Data & Generated Files (ADD TO GITIGNORE)

| File | Action |
|------|--------|
| `pathfinder_data/` | **ADD to .gitignore** — runtime data |
| `cache.db` | **ADD to .gitignore** — SQLite cache |
| `cache_data/` | **ADD to .gitignore** — cache directory |
| `demo_data/` | **ADD to .gitignore** — demo artifacts |
| `content_output/` | **ADD to .gitignore** — generated content |
| `.build_data/` | **ADD to .gitignore** — build artifacts |
| `curl` | **DELETE** — accidental file? |
| `>/` | **DELETE** — accidental file? |

---

## Category 7: Open Source Archive (MOVE TO archive/)

11 files in `opensource/` — old benchmark code and retired project artifacts.

**Recommended:** Move to `archive/opensource-retired/`

---

## Category 8: Configuration Files (COMMIT)

| File | Action |
|------|--------|
| `SKILLS_REGISTRY.md` | **COMMIT** ✅ New canonical registry |
| `QUALITY_RULES.md` | **COMMIT** ✅ Quality standards |
| `AUDIT_PLAN.md` | **COMMIT** ✅ Audit protocol |
| `KEY_REGISTRY.json` | **VERIFY** — what keys are these? |
| `brain_inventory.json` | **COMMIT** ✅ Brain config |
| `coding_cache_seed.json` | **COMMIT** ✅ Cache seed data |
| `cache_builder.py` | **COMMIT** ✅ Cache builder |
| `brain_proxy.py` | **COMMIT** ✅ Proxy config |

---

## Category 9: Retired/Killed Projects (MOVE TO archive/)

| File | Action |
|------|--------|
| `hallucination-benchmark/` | **ARCHIVE** — retired project |
| `llm-benchmarks/` | **ARCHIVE** — old benchmarks |
| `marketplace-domination/` | **ARCHIVE** — old strategy doc |
| `onboarding-guides/` | **ARCHIVE** — superseded by onboarding-wizard |
| `paywall/` | **ARCHIVE** — old pricing experiments |
| `products/` | **ARCHIVE** — old product specs |

---

## Recommended .gitignore Additions

```gitignore
# Generated files
__pycache__/
*.pyc
*.pyo

# Runtime data
pathfinder_data/
cache.db
cache_data/
demo_data/
content_output/
.build_data/
logs/*.json

# Generated dashboards
agentpathfinder_dashboard.html

# OS files
.DS_Store
```

---

## Cleanup Script (Suggested)

```bash
#!/bin/bash
# Run from /data/.openclaw/workspace

# 1. Delete generated files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 2. Delete accidental files
rm -f curl
rm -f ">"

# 3. Move retired projects to archive
mkdir -p archive/retired-skills archive/retired-projects
mv skills-publish/hallucination-guard-v2/ archive/retired-skills/ 2>/dev/null
mv skills-publish/install_sandbox/ archive/retired-skills/ 2>/dev/null
mv hallucination-benchmark/ archive/retired-projects/ 2>/dev/null
mv llm-benchmarks/ archive/retired-projects/ 2>/dev/null
mv marketplace-domination/ archive/retired-projects/ 2>/dev/null
mv paywall/ archive/retired-projects/ 2>/dev/null

# 4. Delete old backups
rm -rf agentpathfinder.old-april25/

# 5. Clean generated files
rm -f agentpathfinder_dashboard.html

# 6. Update .gitignore
cat >> .gitignore << 'EOF'
__pycache__/
*.pyc
pathfinder_data/
cache.db
cache_data/
.build_data/
EOF

echo "Cleanup complete. Run 'git status' to verify."
```

---

## Decision Log (NEEDS ANTON APPROVAL)

| Decision | Default Action | Need Anton to Confirm |
|----------|--------------|---------------------|
| Delete `agentpathfinder.old-april25/` | ✅ Yes | Confirm no data needed |
| Keep `docs/btc-trading-scope.md` | ❌ No | Confirm if still relevant |
| Keep `docs/restaurant-inventory-assessment.md` | ❌ No | Confirm if still relevant |
| Archive `opensource/` | ✅ Yes | Confirm old benchmark code not needed |
| Archive `skills-publish/` | ✅ Yes | Confirm SKILLS_REGISTRY.md is new source of truth |
| Delete `scripts/agent_self_improve.py` | ✅ Yes | Confirm auto-improve is retired |
| Delete `scripts/auto_build.py` | ✅ Yes | Confirm old build script |
| Keep `gbrain/` | ❓ Unknown | What is this? |
| Keep `faulttrace-l5x/` | ❓ Unknown | Is this current FaultTrace code? |

---

## After Cleanup: Expected State

**Before:** 146 files  
**After (estimated):** ~40-50 files

**What remains:**
- docs/ (minus off-topic files)
- scripts/ (minus obsolete)
- skills/ (current dev)
- Archive directories (retired projects)
- Clean .gitignore
- Committed configs

---

## Next Steps

1. **Anton approves** cleanup decisions above
2. **Run cleanup script** (or do manually)
3. **Verify** `git status` shows only wanted files
4. **Commit** with message: `git commit -m "chore: cleanup generated files, archive retired projects, add .gitignore"`
5. **Future:** All new generated files go to .gitignore automatically
