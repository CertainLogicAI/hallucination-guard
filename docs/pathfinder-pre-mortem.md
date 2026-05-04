# AgentPathfinder v2 — Pre-Mortem: What Will Go Wrong

**Date:** 2026-04-25
**Status:** Published to ClawHub. Time for brutal honesty.

---

## The Suspicion Is Right

Yes, it was too easy. Here's everything that will break, confuse, or embarrass us in the first 48 hours.

---

## 🔴 HIGH RISK — Will Break Immediately

### 1. `clawhub install agentpathfinder` Probably Doesn't Work

**Problem:** The skill package imports from `agentpathfinder` (the core Python package), but ClawHub installs the skill into its own isolated directory. The import resolution in `pathfinder_client.py` tries relative paths like `../../agentpathfinder`, which won't exist in a user's ClawHub install.

**What happens:** User runs `clawhub install agentpathfinder`, then `pf create test step1` → 💥 `ImportError: cannot find agentpathfinder`

**Fix needed:** Either vendor the core into the skill package, or publish `agentpathfinder` as a pip package.

**Likelihood:** 90% of fresh installs fail.

### 2. No Dependency Management

**Problem:** No `requirements.txt`, `setup.py`, or `pyproject.toml`. The dashboard needs Flask. The client needs nothing (stdlib), but users have no way to know that.

**What happens:** User tries `pf dashboard` → 💥 `ModuleNotFoundError: No module named 'flask'`

**Fix needed:** Add `requirements.txt` and `setup.py`.

### 3. `pf run` Is Simulation — Users Will Be Confused

**Problem:** `pf run` marks all steps complete without running real code. A user will:
1. Create a task with steps named "deploy", "test", "notify"
2. Run `pf run`
3. Think their deployment actually happened
4. Be very confused/angry when nothing deployed

**Fix needed:** Clear warning in CLI: "SIMULATION MODE — no real code executed. Use Python SDK for production."

### 4. No Tests for the Skill Package

**Problem:** Core has 29 tests. The CLI/client has 0. The static dashboard generator has 0.

**What happens:** Someone uses a task name with Unicode characters. Or a step name with quotes. Or 1000 steps. Something breaks.

**Fix needed:** Add pytest suite for CLI edge cases.

---

## 🟡 MEDIUM RISK — Will Confuse or Annoy Users

### 5. Windows Compatibility = Broken

**Problem:** `task_engine.py` uses `fcntl` for file locking. `fcntl` is Unix-only. Windows users get immediate `ImportError`.

**What happens:** 💥 `ModuleNotFoundError: No module named 'fcntl'` on every Windows machine.

**Fix needed:** Add Windows-compatible locking (portalocker or threading.RLock fallback).

### 6. Committed `__pycache__` to GitHub

**Problem:** I committed `.pyc` files to the repo. This is sloppy and bloats the package.

**Fix needed:** `.gitignore`, then `git rm --cached` the pycache directories.

### 7. No Task Cleanup — Data Directory Grows Forever

**Problem:** Every task creates files in `pathfinder_data/`. No cleanup mechanism. After 1000 tasks, the directory is a mess.

**What happens:** Users complain about disk usage. Or worse, they manually delete files and corrupt active tasks.

**Fix needed:** Add `pf tasks list` and `pf task delete <id>` commands. Auto-archive completed tasks after 30 days.

### 8. Dashboard Static Generator Untested Edge Cases

**Problem:** The static HTML dashboard generator was written quickly. What happens with:
- Zero tasks?
- Tasks with 0 steps?
- Step names with `<script>` tags (XSS)?
- Very long step names?
- Tasks missing audit files?

**Likelihood:** At least one of these breaks the HTML.

---

## 🟢 LOW RISK — Embarrassing But Not Fatal

### 9. Version Number Mismatch

Repo says `1.0.0`. ClawHub says `1.0.0-beta.1`. Confusing.

### 10. No README in Repo About SDK Usage

The repo README only shows CLI. Python SDK is buried in SKILL.md. Developers won't find it.

### 11. Skill Description Doesn't Mention "Free Forever"

Our biggest differentiator (no usage limits) isn't in the ClawHub listing. Competitors will add caps; we should shout about not having them.

### 12. No Error Handling for Missing Task IDs

`pf status fake-id-123` → ugly Python traceback instead of clean error message.

### 13. The Name "AgentPathfinder"

I didn't check if this is already trademarked or used by another project. If someone else claims it, we rebrand.

### 14. `dashboard.py` vs `dashboard_static.py` Confusion

Two dashboard scripts. Users will run the wrong one. The Flask one needs pip install. The static one generates HTML. Which is which?

---

## The Real Risk: We Ship, It Breaks, Users Leave Forever

**First impressions are everything.** If someone's first experience is:
1. `clawhub install agentpathfinder` → works
2. `pf create test a b c` → 💥 ImportError
3. They uninstall and never come back

That's catastrophic. One bad first impression = lost customer forever.

---

## Fix Priority (Before Anyone Installs)

| Priority | Fix | Time |
|----------|-----|------|
| **P0** | Test `clawhub install` in a fresh environment | 30 min |
| **P0** | Vendor core into skill OR publish pip package | 1-2 hours |
| **P0** | Add `.gitignore` + remove pycache | 15 min |
| **P1** | Add `requirements.txt` + `setup.py` | 30 min |
| **P1** | Add simulation warning to `pf run` | 15 min |
| **P1** | Add `pf task delete` command | 30 min |
| **P1** | Clean error messages for missing tasks | 30 min |
| **P2** | Windows compatibility (fcntl fallback) | 1-2 hours |
| **P2** | XSS protection in dashboard | 30 min |
| **P3** | Add skill package tests | 1-2 hours |

---

## Recommendation

**Don't promote this yet.** Fix P0 and P1 items first. Test a clean install on a fresh machine (or VM). Then announce.

**Better to ship late and working than on time and broken.**
