# CertainLogic Workspace — New Developer Onboarding

**Last Updated:** 2026-05-04  
**Assumes:** You have Python 3.10+, git, and basic CLI knowledge.  
**Questions?** Ask Alex (Anton's AI colleague) or ping Anton directly.

---

## Quick Start (5 minutes)

```bash
# 1. Clone and enter
git clone <repo-url> certainlogic
cd certainlogic

# 2. Install Python deps
pip install -r requirements.txt

# 3. Verify Brain API
curl -s http://127.0.0.1:8000/health
# Expected: {"status":"ok","facts_db":"N facts loaded"}

# 4. Run tests
pytest tests/ -v
```

---

## Repo Structure

```
.
├── main.py                  # Brain API (deterministic + LLM hybrid)
├── token_reduction_engine.py # Query optimizer + cache router
├── cache_manager.py         # LRU cache with TTL
├── cache_builder.py         # Automated fact extraction
├── requirements.txt         # Python deps (5 packages only)
│
├── config/
│   └── model_routing.json   # Tiered model selection (Kimi/Grok/Free)
│
├── scripts/                 # Infrastructure automation
│   ├── coding_query_tracker.py    # Daily cache hit rate logging
│   ├── daily_summary.py           # Chat log summarizer
│   ├── nightly_summary.py         # Nightly session summary
│   ├── metrics_snapshot.py        # Cache performance tracker
│   ├── agent_learn.py             # Auto-embed for agents
│   ├── memory_gc.py               # Archive old memory files
│   ├── product_health.py          # Product health checks
│   ├── system_health.py           # System health checks
│   └── backup-to-b2.sh            # Backblaze backup
│
├── skills/                  # Development directory (in-progress skills)
│   └── certainlogic-pathfinder/   # AgentPathfinder (published on ClawHub)
│
├── docs/                    # Documentation
│   ├── CONVENTIONS.md       # Repo hygiene rules
│   ├── ASSET_SYSTEM.md      # Modular business compounding
│   ├── ANTON_DECISIONS.md   # Decision log (B1-B6)
│   ├── PROCESS_LOG.md       # Process recovery tracker
│   ├── IMPROVEMENTS.md      # Known gaps and priorities
│   └── research/            # Market research
│
├── memory/                  # Daily decision logs
├── archive/                 # Retired projects (251MB)
├── logs/                    # Daily reports, cache logs
├── tests/                   # Unit tests
└── conversation_logs/       # Raw chat logs (to be extracted monthly)
```

---

## Key Conventions (Must Follow)

1. **Generated files** → `.gitignore` forever (`__pycache__/`, `*.pyc`, `*.log`)
2. **Skills** → `SKILLS_REGISTRY.md` is single source of truth
3. **Retired projects** → Move to `archive/` within 24h, never leave in root
4. **Submodules** → `certainlogic-site/`, `patent_filings/` are tracked in their own repos
5. **Commit before EOD** — even partial progress. Prevents 157-file messes.
6. **Verify imports** before archiving `.py` files — `main.py` imports are runtime deps
7. **Test your code** — `pytest tests/ -v` before committing
8. **Update `PROCESS_LOG.md`** when process items complete

---

## How to Run Tests

```bash
# All tests
pytest tests/ -v

# Single test file
pytest tests/test_coding_query_tracker.py -v

# With coverage (install: pip install pytest-cov)
pytest tests/ --cov=scripts --cov-report=term-missing
```

---

## How to Write a New Script

1. Create file in `scripts/` (lowercase, underscores)
2. Add to `tests/test_<name>.py` (required)
3. Test in fresh venv: 
   ```bash
   python3 -m venv /tmp/test-venv
   source /tmp/test-venv/bin/activate
   pip install -r requirements.txt
   python3 scripts/your_script.py --help
   ```
4. Add to `PROCESS_LOG.md` if it's scheduled work

---

## How to Add a New Skill

1. Read `docs/CONVENTIONS.md` Rule #2
2. Create directory: `skills/your-skill-name/`
3. Required files:
   - `skill.json` — metadata and manifest
   - `SKILL.md` — instructions for agents
   - `setup.py` — install config (can be empty `install_requires=[]`)
   - `your_module/__init__.py` — package init
4. Tests: `tests/test_<module>.py`
5. Update `SKILLS_REGISTRY.md`
6. Publish: `clawhub publish skills/your-skill-name/`
7. Verify: `clawhub install your-skill-name`

---

## How to Deploy

**Brain API:**
```bash
# Start (already running as daemon)
bash start-brain.sh

# Or manual
uvicorn main:app --host 127.0.0.1 --port 8000
```

**Cron Jobs:**
- Managed via OpenClaw Gateway (`cron list`)
- 25 jobs scheduled (some isolated, some main session)
- See `cron list` for status and errors

**Backups:**
- Daily at 3 AM: `scripts/backup-to-b2.sh`
- Verify: `du -sh archive/` should be <500MB

---

## Daily Workflow (For Anton + Alex)

**Morning:**
1. Check heartbeat: `curl -s http://127.0.0.1:8000/health`
2. Review PROCESS_LOG.md for priorities
3. Run coding tracker: `python3 scripts/coding_query_tracker.py --today`

**End of Day:**
1. `git status` — should be <20 files
2. `git add <files>` + `git commit -m "<action>: <what>"`
3. Update `memory/YYYY-MM-DD.md` with decisions
4. Check `PROCESS_LOG.md` — anything to advance?

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ImportError` for workspace module | Check if file got archived. See CONVENTIONS.md Rule #6 |
| Brain API down | Run `bash start-brain.sh` |
| Cron failures | `cron list` → check consecutiveErrors. Update delivery mode if Telegram unpaired |
| Git mess (>20 files) | Check `docs/CONVENTIONS.md`, commit or archive |
| Cache hit rate low | Expected. Cache is still warming (only 2 queries today) |
| Model errors in cron | Check `config/model_routing.json` for fallback chains |

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `curl -s http://127.0.0.1:8000/health` | Check Brain API |
| `python3 scripts/coding_query_tracker.py --today` | Daily cache report |
| `pytest tests/ -v` | Run all tests |
| `clawhub list` | List installed skills |
| `clawhub publish skills/<name>/` | Publish skill |
| `cron list` | View cron jobs |
| `git log --oneline -10` | Recent commits |
| `du -sh archive/` | Archive size check |

---

*This file is living documentation. Update it when structure changes. — Alex, 2026-05-04*
