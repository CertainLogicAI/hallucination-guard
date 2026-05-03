# HEARTBEAT.md

## Checks

### Critical (run every check)
- **Brain API**: `curl -s http://127.0.0.1:8000/health` → if down, run `bash /data/.openclaw/workspace/start-brain.sh`
  - Expected: `{"status":"ok","facts_db":"N facts loaded"}`
  - Alert if: `status` != `ok` or `facts_db` drops by >5 from last check
- **Skills Registry**: Verify SKILLS_REGISTRY.md matches `clawhub list` output
  - Alert if: mismatched or new unpublished skills detected
- **Git Health**: Check for uncommitted files via `git status --short`
  - Alert if: >20 uncommitted files (indicates cleanup needed)
- **Brain Facts Trend**: Log facts_db count
  - Alert if: count decreases (knowledge loss) or stuck for >3 days

### Daily (run once per day)
- **Skill Install Check**: Verify published skills install cleanly
  - `clawhub install certainlogic-pathfinder --dry-run` (if supported)
  - Alert if: install fails or version mismatch
- **Registry Sync**: Compare `clawhub list` vs SKILLS_REGISTRY.md
  - Alert if: discrepancies found
- **Coding Query Tracker**: Generate daily coding cache hit rate report
  - Run: `python3 scripts/coding_query_tracker.py --today`
  - Check: `logs/daily_reports/coding_queries_YYYY-MM-DD.json`
  - Alert if: coding hit rate <50% or zero coding queries logged

### Weekly (run on Sundays)
- **Archive Cleanup**: Check `archive/` size
  - Alert if: >500MB (old projects accumulating)
- **Decision Log Review**: Ensure docs/anton-todo.md has no stale items >14 days

## Quiet hours
- 11PM–8AM CST: stay quiet unless urgent
