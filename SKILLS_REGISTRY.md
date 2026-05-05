# CertainLogic Skills Registry
# SINGLE SOURCE OF TRUTH for all ClawHub and local skill listings
# Updated: 2026-05-05
# Last audit: 2026-05-05 (Anton verified pa-pack + pathfinder delisted)

## Published on ClawHub (need verification)

| Slug | Display Name | Status | Has Code | Has Tests | Issue |
|------|-------------|--------|----------|-----------|-------|
| certainlogic-onboarding-wizard | Certainlogic Onboarding Wizard | ⚠️ Unknown | ? | ? | **Tool** — verify manually |
| skill-oracle | Skill Oracle | ⚠️ Unknown | ❌ No code | ❌ | **Documentation** — MD-only by design |
| skill-vetter-plus | Skill Vetter Plus | ⚠️ Unknown | ✅ | ❌ | **Tool** — verify manually (false positive?) |
| certainlogic-context-tokenreducer | CertainLogic Context Manager | ⚠️ Unknown | ? | ? | **Tool** — verify manually |

## Retired / Delisted from ClawHub

| Slug | Display Name | Delisted | Reason |
|------|-------------|----------|--------|
| pa-pack | PA Pack | 2026-05-04 | Documentation-only, not a product |
| certainlogic-smart-router | Smart Router | 2026-05-04 | Absorbed into Hybrid Router |
| certainlogic-pathfinder | AgentPathfinder | 2026-05-05 | Code is internal component, not standalone skill |

## Premium Products (roadmap — do not publish yet)

| Slug | Display Name | Has Code | Notes |
|------|-------------|----------|-------|
| skill-auditor | Skill Auditor | ❌ No | Not built yet |
| cold-outreach-pro | Cold Outreach Pro | ❌ No | Not built yet |
| market-research-pro | Market Research Pro | ❌ No | Not built yet |
| seo-audit-pro | SEO Audit Pro | ❌ No | Not built yet |
| ai-visibility-pro | AI Visibility Pro | ❌ No | Not built yet |
| x-monitor-pro | X Monitor Pro | ❌ No | Not built yet |

## Rules
1. **Never publish without code + tests**
2. **Update this file immediately** on every publish/unpublish
3. **Verify locally** before publishing
4. **Audit published skills monthly**

## Commands to Use
```bash
# List published skills
clawhub list

# Check skill locally
cd /data/.openclaw/workspace/skills/<slug>
ls -la
python3 -m pytest tests/ -v

# Publish
clawhub publish . --slug <slug> --version <version>

# Unpublish
clawhub skill unpublish <slug>
```

## Action Items
- **certainlogic-onboarding-wizard**: Pull local copy, verify it works
- **certainlogic-context-tokenreducer**: Pull local copy, verify it works
- **skill-oracle**: Decide: implement code or keep as internal doc
- **skill-vetter-plus**: Contact ClawHub about false positive flag OR verify manually
