# CertainLogic Skills Registry
# SINGLE SOURCE OF TRUTH for all ClawHub and local skill listings
# Updated: 2026-05-03
# Last audit: 2026-05-03

## Published on ClawHub (live)

| Slug | Display Name | Status | Has Code | Has Tests | Issue |
|------|-------------|--------|----------|-----------|-------|
| certainlogic-onboarding-wizard | Certainlogic Onboarding Wizard | ✅ Visible | ? | ? | **Tool** — verify manually |
| certainlogic-smart-router | CertainLogic Smart Router | ⚠️ Quality held | ✅ | ✅ 14 passed | **Tool** — verify manually |
| skill-oracle | Skill Oracle | ✅ Visible | ❌ No code | ❌ | **Documentation** — MD-only by design |
| pa-pack | Pa Pack | ✅ Visible | ❌ No code | ❌ | **Documentation** — recommendations pack |
| skill-vetter-plus | Skill Vetter Plus | 🔴 Suspicious | ✅ | ❌ | **Tool** — verify manually (false positive?) |
| certainlogic-context-tokenreducer | CertainLogic Context Manager | ✅ Visible | ? | ? | **Tool** — verify manually |

### Action Items (Published)
- **skill-oracle**: UNPUBLISH or implement code
- **pa-pack**: UNPUBLISH or implement code
- **skill-vetter-plus**: Contact ClawHub about false positive flag
- **certainlogic-smart-router**: Investigate why quality-held
- **certainlogic-onboarding-wizard**: Pull local copy, verify it works
- **certainlogic-context-tokenreducer**: Pull local copy, verify it works

## Local Only (not published)

| Slug | Display Name | Has Code | Has Tests | Status |
|------|-------------|----------|-----------|--------|
| certainlogic-pathfinder | AgentPathfinder | ✅ 15 files | ✅ 17 passed | **Ready to publish** (pending install UX final check) |

## Premium Products (roadmap — do not publish yet)

| Slug | Display Name | Has Code | Notes |
|------|-------------|----------|-------|-------|
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
