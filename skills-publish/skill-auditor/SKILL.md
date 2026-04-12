---
summary: "Skill Auditor"
read_when: ["[]"]
---



# Skill Auditor

Evaluate ClawHub skills for security, quality, and usefulness before installation. Prevents installing malicious, bloated, or redundant skills.

## Quick Reference

| Need | Resource |
|------|----------|
| Automated security scan | `scripts/security-scan.sh <skill-dir>` |
| Scoring framework | `references/usefulness-rubric.md` |
| Known red flags | `references/red-flags.md` |

## Process (9 Steps)

### 1. Search
```bash
clawhub search "<query>"
clawhub inspect <slug>
```
Search multiple categories for broad sweeps. Check `inspect` for license, update date, owner.

### 2. Install to Temp
Never install directly to workspace. Always audit first.
```bash
mkdir -p /tmp/skill-audit
clawhub install <slug> --dir /tmp/skill-audit --force
```
Note VirusTotal flags — `--force` is required for flagged skills. Flag this to the user immediately.

### 3. Security Audit
Run the automated scanner:
```bash
bash scripts/security-scan.sh /tmp/skill-audit/<slug>
```
Review results. For any CRITICAL findings, reject. For WARNINGS, read the flagged files manually. See `references/red-flags.md` for the full checklist.

### 4. Usefulness Audit
Score using the rubric in `references/usefulness-rubric.md`. Rate each dimension (Substance, Structure, Actionability, Fit, Maintenance) 1-5. Total determines tier:
- **20-25** → Tier 1 (Install)
- **14-19** → Tier 2 (Worth having)
- **8-13** → Tier 3 (Skip)

### 5. Redundancy Check
Compare against installed skills:
```bash
ls skills/
grep -c -i "<topic>" skills/*/SKILL.md
```
**Keep both** when skills complement (strategy vs execution). **Drop the weaker** when one is a strict subset.

### 6. Report
Present to user: security verdict, usefulness tier, comparison to similar skills, install/skip recommendation. One report per batch.

### 7. Install
Only after user approval:
```bash
clawhub install <slug> --force
```

### 8. Post-Install Optimization
- Delete clutter: `README.md`, `REVIEW.md`, `CHANGELOG.md`, `skill.json`
- Fix missing YAML frontmatter (`name:` + `description:`)
- Split SKILL.md if >300 lines → move sections to `references/`
- Remove duplicate "When to Use" body sections

### 9. Cleanup
```bash
rm -rf /tmp/skill-audit
```
Update memory with what was installed and why.

## Rules
- **Always security audit first** — no exceptions
- **Always get user approval** before installing to workspace
- **One report per batch** — don't make the user approve one at a time
- **VirusTotal flags require extra scrutiny** — read every file manually
- **Prefer free (MIT-0)** unless user specifically wants paid
