# Requirements Audit Log

**Project:** P1 — Build single `requirements.txt`
**Started:** 2026-05-04 14:25 UTC
**Status:** ✅ COMPLETE

## Step 1: Discover all dependencies

**Method:** Scanned all .py files in workspace (excluded archive/, skills-publish/, .build_data/, node_modules/)
**Command used:** `grep -rh "^import\|^from" --include="*.py" . | sort | uniq | filter stdlib`

## Step 2: Results

**Third-party packages found:**

| Package | Used By | Purpose |
|---------|---------|---------|
| `fastapi` | main.py | Brain API server |
| `pydantic` | main.py, api/main.py, archive/ | API models, data validation |
| `uvicorn` | main.py (indirect), start scripts | ASGI server |
| `requests` | scripts/agent_learn.py, scripts/seed_internal_cache.py, token_reduction_engine.py | HTTP calls |
| `pytest` | skills/*/tests/ | Testing |

**Everything else is stdlib.** No numpy, pandas, ML libs, or heavy deps cluttering the workspace.

## Step 3: Generated requirements.txt

```
fastapi>=0.104.0
pydantic>=2.0.0
uvicorn[standard]>=0.24.0
requests>=2.31.0
pytest>=7.4.0
```

## Verification

Want to test in fresh venv? Run:
```bash
python3 -m venv /tmp/test-venv
source /tmp/test-venv/bin/activate
pip install -r requirements.txt
python3 -c "from main import app; print('✓ Brain API imports OK')"
```

## Notes

- `yaml` usage in `archive/` only — not in core workspace
- `typer` in retired skills only — not in core workspace
- Node deps (package.json: gray-matter, openai, redis, yaml) are for OpenClaw internals, not Python workspace
- Skills have `setup.py` with no deps (install_requires=[])
