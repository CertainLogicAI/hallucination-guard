# Skill Vetter Plus

One command to know if a ClawHub skill is safe to install.

## What This Is

A security scanner for OpenClaw skills. Checks code, claims, and dependencies before you install.

## What It Does vs. What It Doesn't

| ✅ What It Does | ❌ What It Does NOT |
|-----------------|---------------------|
| Scans skill code for dangerous patterns (eval, unrestricted shell) | Run the skill to observe runtime behavior |
| Flags false marketing claims ("100%", "eliminates") | Guarantee a skill is safe — we miss things too |
| Checks for external data calls to unknown domains | Deep vulnerability analysis (CVE database, etc.) |
| Verifies dependency pinning | Judge whether a skill is useful for your use case |
| Gives you a "CertainLogic Certified" badge if it passes | Protect you from skills we haven't seen |

## What You Get (Free Forever)

| Feature | What It Means |
|---------|-------------|
| **One-command scan** | `vetter scan <skill-id>` — instant PASS/FAIL/WARN |
| **5 safety checks** | Code safety, claim honesty, network calls, file system, dependencies |
| **Context-aware** | Skips quoted examples and "does NOT" sections — fewer false positives |
| **Offline** | Works on local skill folders, no network needed |
| **Open source** | Read the code, trust the process |

## Honest Limitations

| Limitation | What That Means |
|------------|-----------------|
| Static analysis only | We read the code, we don't run it. Smart malicious code can hide. |
| Regex-based detection | False positives happen. False negatives happen. |
| Marketing claims only | We catch "100% accurate" but not "world-class" (subjective but suspicious). |
| No deep security audit | No CVE database lookup, no fuzzing, no runtime analysis. |
| Certifies against OUR standards | Passing our scan means you passed our checks. That's all. |

## Quick Start

### One-line install (curl | bash)
```bash
curl -sSL https://raw.githubusercontent.com/certainlogic/skill-vetter-plus/main/install.sh | bash
```

### Single file drop-in
Download `scripts/vetter.py` and run:
```bash
python3 vetter.py scan <skill-folder>
```

### ClawHub install
```bash
clawhub install certainlogic.skill-vetter-plus
```

## Usage

### Free tier
```bash
$ vetter scan some-skill
✅ PASS — Looks clean

$ vetter scan sketchy-skill
⚠️  WARN — Some concerns
   Run --pro for details
```

### Pro tier
```bash
$ vetter scan some-skill --pro
✅ CERTIFIED — CertainLogic Certified
Cert ID: daec54267bfc5958

Badge (paste into README):
[![CertainLogic Certified](https://img.shields.io/badge/CertainLogic-Certified-blue)]
```

### Batch scan
```bash
$ for skill in skills/*; do vetter scan "$skill"; done
```

## When to Use This

**Good for:**
- Before installing any ClawHub skill you haven't reviewed
- When someone sends you a skill and you want a quick sanity check
- Auditing your existing installed skills
- Adding a badge to your own skill's README (if you pass)

**Not for:**
- Replacing manual code review for critical security decisions
- Catching zero-day exploits in skill code
- Judging whether a skill actually does what it claims (just whether its claims are honest)
- Production security audits without additional tooling

## Honest Note

Skill Vetter Plus catches the obvious problems so you don't have to. It's not a substitute for reading code yourself — but it's a lot faster.

If you find a skill that passes our scan but is malicious, tell us. We fix the scanner.

---

*Built by [CertainLogic](https://certainlogic.ai) — honest tools for honest builders.*
*Free on [ClawHub](https://clawhub.ai/certainlogicai). Pro upgrades at [certainlogic.ai/shop](https://certainlogic.ai/shop).*
*Questions? [X @CertainLogicAI](https://x.com/CertainLogicAI)*
