# Skill Packager (Internal Tool)

> Automates the CertainLogic skill packaging process. Validates, audits, standardizes, and generates submission-ready packages for any marketplace.

**Status:** Internal use only. Not for public ClawHub listing.

---

## What This Is

A checklist-driven automation tool that makes sure our skills meet marketplace requirements AND follow CertainLogic's honesty standards before publication.

**Like a pre-flight checklist for pilots** — it catches problems before takeoff, not after.

---

## What You Get

| Feature | What It Means |
|---------|-------------|
| ✅ **Rule validation** | Checks structure against ClawHub/SkillsMP/LobeHub requirements before submission |
| 🔍 **Jargon detector** | Scans README for words normies don't understand and flags them |
| 📋 **Benefits templates** | Generates plain-language benefits tables for your skill type |
| 🔧 **Install script generator** | Auto-creates `install.sh` for one-line `curl \| bash` installs |
| 📄 **Install docs checker** | Verifies README explains how users install your skill |
| ✔️ **Pre-flight checklist** | Anton-verification checklist for every publish |

---

## What It Does NOT

| It Does NOT | Why That Matters |
|-------------|------------------|
| ❌ Publish for you | Anton must still explicitly approve before any publish |
| ❌ Write your README | It flags problems; you still write the content |
| ❌ Verify features work | It checks files exist, not that code runs correctly |
| ❌ Replace human judgment | Final call is always Anton's |

---

## Requirements

- Python 3.10+
- Zero external dependencies (stdlib only)

---

## Install

```bash
# Internal only — clone from our repo
git clone https://github.com/CertainLogicAI/skill-packager.git
cd skill-packager
```

---

## Usage

### Full packaging run

```bash
python3 scripts/package_skill.py \
  /path/to/skill-source \
  /path/to/output \
  --marketplace clawhub \
  --skill-type task_tracking
```

### What happens

1. **Fetch rules** — loads ClawHub requirements (required files, fields, semver)
2. **Validate structure** — checks skill.json, README.md, SAFETY.md exist and aren't empty
3. **Audit language** — scans for jargon (HMAC, cryptographic, deterministic, etc.)
4. **Check install docs** — verifies README has clear install instructions (one-line, pip, or ClawHub)
5. **Generate benefits template** — creates plain-language table for your skill type
6. **Generate install script** — auto-creates `install.sh` for one-line `curl | bash` installs
7. **Build package** — copies files to output folder + checklist

### Output

```
output/
├── skill.json              # copied from source
├── README.md               # copied from source
├── SAFETY.md               # copied from source
├── scripts/                # copied from source
├── install.sh              # generated — one-line curl | bash script
├── BENEFITS_TEMPLATE.md    # generated — paste into README
└── PUBLISH_CHECKLIST.md    # generated — Anton must complete
```

---

## Install Script Generation (Auto)

If your skill doesn't have an `install.sh`, the packager creates one:

```bash
# Auto-generated install.sh lets users do:
curl -fsSL https://raw.githubusercontent.com/CertainLogicAI/your-skill/main/install.sh | bash
```

The script:
- Auto-detects your main script from `skill.json` entrypoint
- Handles `scripts/*.py` or package structure
- Downloads to appropriate PATH directory
- Warns user if PATH needs updating

**Manual step:** Update the `SCRIPT_URL` in generated `install.sh` with your actual GitHub repo URL.

---

## Skill Types & Templates

| Type | Use For | Example Products |
|------|---------|------------------|
| `task_tracking` | Agents that record steps | AgentPathfinder |
| `cache` | Performance/cost optimization | Token Reduction Engine |
| `security` | Scanning/verification tools | Hallucination Guard |
| `generic` | Everything else | — |

---

## Jargon Detection

The tool flags these words and suggests replacements:

| Flagged Word | Suggested Replacement |
|--------------|----------------------|
| HMAC-SHA256 | "signed" or "proof of who said what" |
| cryptographic | "secure" or "tamper-proof" |
| deterministic | "consistent" or explain without the word |
| crash recovery | "resume where you left off" |
| tamper-evident | "tamper-proof" or "shows if edited" |
| idempotency | "safe to run twice" |
| zero-dependency | "works offline" |

---

## Pre-flight Checklist (Example)

Every package generates this checklist for Anton:

```markdown
## Before You Publish

- [ ] Anton has personally installed and tested the product
- [ ] Every claimed feature has been verified by Anton
- [ ] No jargon in README (no HMAC, cryptographic, deterministic, etc.)
- [ ] Benefits table is clear and simple
- [ ] 'What It Does NOT' table is present and honest
- [ ] No '100%', 'eliminates', 'guarantees', 'proves' language
- [ ] Version follows semver (X.Y.Z)
- [ ] skill.json is valid JSON
- [ ] All required files present
- [ ] install.sh generated and URL verified

## After Publish

- [ ] Test install from marketplace (not dev environment)
- [ ] Verify listed features work from clean install
- [ ] Monitor for issues for 48 hours
```

---

## Why This Exists

On April 29, 2026, we published AgentPathfinder with language that overstated its capabilities ("100% verified", "cryptographic proof"). It should never have shipped. This tool prevents that by enforcing honesty standards BEFORE publication, not after.

**Rule enforced:** No claim gets published until Anton personally verifies it.

---

## License

MIT-0 — internal use only.
