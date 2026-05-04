---
summary: "Skill Vetter Plus"
read_when: ["Before installing any ClawHub skill", "When auditing skills for security", "Adding certification to your own skill"]
---

# Skill Vetter Plus

Quick security and honesty scan for ClawHub/OpenClaw skills.

## Quick Reference

| Need | Command |
|------|---------|
| Quick scan | `python3 scripts/vetter.py scan <skill-folder>` |
| Full report with badge | `python3 scripts/vetter.py scan <skill-folder> --pro` |
| Batch scan all skills | `for s in skills/*; do vetter scan "$s"; done` |
| Verify a cert ID | `python3 scripts/badge_generator.py verify <cert-id>` |

## How It Works

1. **Code Safety** — Checks for `eval()`, unrestricted `subprocess.run()`, `os.system()`
2. **Claim Honesty** — Flags "100%", "eliminates", "guaranteed" in READMEs
3. **Network Calls** — Lists external domains the skill contacts
4. **File System** — Warns about reading outside workspace
5. **Dependencies** — Checks if requirements are pinned

False positive reduction:
- Skips `❌` (does-NOT) table cells
- Skips quoted phrases in tables
- Whitelists `capture_output`, `timeout=`, `check=` as safe subprocess patterns
- Whitelists `localhost`, `127.0.0.1`

## Output

**Free tier:** `PASS` / `WARN` / `FAIL`
**Pro tier:** Full report with CertainLogic Certified badge

## Building Starter Packs

```bash
python3 scripts/build_starter_pack.py my-pack skill1/ skill2/ skill3/
```

Scans each skill, includes only certified ones, generates combined README + install script.

## Rules
- Always scan before installing unfamiliar skills
- Free tier shows result only — no details
- Pro tier unlocks: full findings, badge generation, cert registry
- No claim is perfect — static analysis has limits
