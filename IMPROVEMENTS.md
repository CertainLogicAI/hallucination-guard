# Internal Improvements Needed

**Date:** 2026-05-04  
**Status:** Draft — pending Anton priority review  

---

## Critical (Fix This Week)

### 1. No 'main' Branch — Only 'master'
**Problem:** Remote has `master`, local has `cleanup_complete`. Standard is `main`.  
**Fix:** `git branch -m master main` + `git push origin main` + update default branch  
**Risk:** Low. Just git workflow standardization.

### 2. Scripts Have Zero Unit Tests
**Problem:** 16 scripts, only 1 has any test coverage.  
**Impact:** When cron jobs break (like `metrics-snapshot-daily` with 9 consecutive errors), we don't catch issues before deployment.  
**Fix:** Add basic unit tests for:
- `coding_query_tracker.py` (test filtering logic, hit rate calculation)
- `summarize_memory.py` (test summarization pipeline)
- `cache_builder.py` (test fact extraction)
**Priority:** Medium — affects reliability.

### 3. Cron Jobs Failing Silently
**Evidence:**
- `metrics-snapshot-daily`: 9 consecutive errors, `model_not_found`, Telegram 404
- `cache-harvest-weekly`: 2 consecutive errors, same Telegram issue  
**Fix:** Either fix Telegram delivery or switch delivery to `mode: "none"` until paired.
**Priority:** High — failed jobs = missing data.

### 4. Secrets Exposure Risk
**Files referencing keys/tokens:** `audit_yc_readiness.md`, `fallback_logger.py`, old archived logs  
**Fix:** Run `git-filter-repo` or `BFG` to scrub history if any real secrets exist. Verify first with `git secret` scan.
**Priority:** High if real secrets found, Low if only references.

---

## Important (Fix This Month)

### 5. No Dependency Management
**Problem:** No consolidated `requirements.txt` for scripts.  
`token_reduction_engine.py` imports `hallucination_detector` — but that was archived.  
**Fix:** Create root `requirements.txt`, test imports in fresh venv.
**Impact:** Prevents "works on my machine" failures.

### 6. No CI/CD Pipeline
**Problem:** No automated testing before commit.  
**Fix:** GitHub Actions workflow (when repo is public):
```yaml
# .github/workflows/test.yml
- python -m pytest skills/*/tests/
- python scripts/test_all.py  # if we add one
```
**Impact:** Catches broken code before merge.

### 7. No Code Linting Standards
**Problem:** Mix of formatting styles. Some scripts use 2-space indent, some 4.  
**Fix:** Add `ruff` or `black` config. One command: `ruff check .`
**Impact:** Readability + prevents style arguments.

### 8. Backup Verification Missing
**Problem:** Daily B2 backup cron runs, but we never test restore.  
**Fix:** Monthly "restore test" — pull latest backup to `/tmp/restore-test/` and verify files match.
**Impact:** Ensures backups actually work.

---

## Nice to Have (Q2 2026)

### 9. Centralized Logging
**Problem:** Logs scattered: `logs/brain-api.log`, `audit_log.jsonl`, cron logs, script output files.  
**Fix:** Single structured logging format (JSONL) with rotation.
**Impact:** Easier debugging, especially for cron failures.

### 10. Script Health Dashboard
**Problem:** We check cron status manually.  
**Fix:** Simple JSON status file updated by each script run:
```json
{
  "script": "coding_query_tracker",
  "last_run": "2026-05-04T07:00:00Z",
  "status": "ok",
  "errors": []
}
```
**Impact:** One view of all system health.

### 11. Document `ONBOARDING.md`
**Problem:** New developer (or Anton in 3 months) has no idea how repo works.  
**Fix:** Single file explaining:
- Where things live (`skills/`, `scripts/`, `docs/`)
- How to run tests
- How to add a new skill
- How to deploy
**Impact:** Faster onboarding, fewer "where is X?" questions.

### 12. Skill Dependency Graph
**Problem:** `skills-publish/` had duplicates. Skills depend on each other (pathfinder uses agentpathfinder).  
**Fix:** `SKILLS_REGISTRY.md` includes "Depends on" column. Prevents circular deps.
**Impact:** Easier refactoring.

---

## Antons: What order do you want these in?

My recommendation:
1. **Today:** Fix cron job delivery (stop silent failures)
2. **This week:** Add `main` branch, fix `requirements.txt`, test imports
3. **Next week:** Add unit tests for critical scripts (query tracker, cache builder)
4. **This month:** CI/CD pipeline when repo is public
5. **Ongoing:** Linting + logging improvements as we touch files
