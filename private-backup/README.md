# PRIVATE-BACKUP

**Status:** SENSITIVE — CONTAINS CERTAINLOGIC PROPRIETARY DATA

**Contents:**
- `facts_db_backup_YYYY-MM-DD_HHMMSS.json` — Verified facts database snapshots
- `answer_cache_backup_YYYY-MM-DD_HHMMSS.json` — Query/response cache snapshots

**Policy:**
- NEVER commit cache files to public repositories (they may contain customer data)
- This directory is for disaster recovery only ( recreate main DB if corrupted )
- Backups taken after major data migrations

**To restore from backup:**
```bash
cp private-backup/facts_db_backup_*.json facts_db.json
# Restart Brain API
bash start-brain.sh
```

**Last backup:** 2026-05-05 13:45 UTC
- Facts: 443 entries
- Cache queries: 319 entries
