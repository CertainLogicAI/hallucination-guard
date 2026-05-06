# CertainLogic Published Skills — Full Audit Report
**Date:** 2026-04-29 03:40 EDT
**Auditor:** Alex (self-audit)
**Scope:** All CertainLogic skills published on ClawHub

---

## 1. the-install-sandbox (CRITICAL)

**Published version:** 0.1.0
**ClawHub slug:** installsandbox

### skill.json claims:
> "Sandbox and scan ClawHub skills before installation. Isolated tmpfs environment + 30+ security checks. Block malicious skills before they touch your system."

### Tags: "sandbox", "isolated", "malware-detection"

### ACTUAL CODE:
- `Sandbox.create()` → `tempfile.mkdtemp()` (plain temp directory)
- No tmpfs mount
- No Linux namespaces (`unshare`)
- No network blocking (iptables)
- No resource limits (cgroups)
- `sandbox.install_skill()` → **METHOD DOES NOT EXIST** (crashes CLI)
- `install` CLI command → references non-existent method

### SEVERITY: CRITICAL
**Claimed:** Runtime sandbox with isolation
**Actual:** Static regex scanner that copies files to /tmp

### IMPACT:
- Users trust "sandbox" protection they don't have
- Security assessment explicitly flagged this as dangerous misrepresentation
- 37 downloads with false security claims

**STATUS:** Fixed in local repo (commit e7d3f46), NOT pushed to ClawHub
**ACTION NEEDED:** Republish v1.0.1 with honest description, or unpublish entirely

---

## 2. AgentPathfinder Free (HIGH)

**Published version:** 1.2.7
**ClawHub slug:** certainlogicai/agentpathfinder-agent-task-tracker-free

### SKILL.md claims:
> "Free forever, unlimited tasks, no usage caps. Upgrade when you want a dashboard, multi-agent views, or exportable audit files."

### ACTUAL CODE (v1.2.7 on ClawHub):
- `scripts/dashboard_static.py` → INCLUDED (should be Pro-only)
- `scripts/pro_dashboard.py` → INCLUDED (should be Pro-only)
- `scripts/pro_dashboard_v2.py` → INCLUDED (should be Pro-only)
- `pf dashboard` command → documented in SKILL.md table

### SEVERITY: HIGH
**Claimed:** Free = CLI only, Pro = dashboard
**Actual:** Free included all dashboard code for ~8 days

### IMPACT:
- ~200 users got Pro features for free
- No upgrade path — they already have it
- Devalued Pro offering before it launched

**STATUS:** Fixed locally (dashboard scripts moved to agentpathfinder-pro/), NOT republished
**ACTION NEEDED:** Republish clean v1.2.8

---

## 3. Token Reduction Engine (MEDIUM)

**Published version:** 1.0.1
**ClawHub slug:** token-reduction-engine

### SKILL.md claims:
> "Deterministic AI validation middleware"

### ACTUAL CODE (v1.0.1 on ClawHub):
- `hguard_client.py` line 35:
  ```python
  self.api_url = (api_url or BRAIN_API or "http://localhost:8000").rstrip("/")
  ```
- Hardcoded localhost fallback in published version
- Scanner flags this as suspicious (malware indicator)

### SEVERITY: MEDIUM
**Claimed:** Clean deterministic validation
**Actual:** Hardcoded localhost endpoint (security flag)

**STATUS:** Fixed locally (constructor raises ValueError if no endpoint), CANNOT republish (ClawHub CLI parser bug)
**ACTION NEEDED:** Manual ClawHub web UI upload

---

## 4. Hallucination Guard (MEDIUM)

**Published version:** Unknown (redirects to TRE)

### STATUS:
- ClawHub slug redirects to TRE
- Effectively deprecated
- No active users (redirection in place)

---

## 5. Other Skills (PRE-PUBLISH)

These exist in workspace but NOT published on ClawHub:
- ai-visibility-pro
- cold-outreach-pro
- market-research-pro
- seo-audit-pro
- x-monitor-pro
- skill-auditor
- skill-auditor-free

**STATUS:** Safe — never published, never exposed

---

## Audit Summary

| Skill | Published | Critical Issue | Status |
|-------|-----------|----------------|--------|
| the-install-sandbox | ✅ | FALSE "sandbox" claims | Fixed local, not pushed |
| AgentPathfinder Free | ✅ | Gave away Pro dashboard | Fixed local, not pushed |
| Token Reduction Engine | ✅ | Hardcoded localhost | Fixed local, can't push |
| Hallucination Guard | ✅ (redirect) | Deprecated | Low risk |
| agentpathfinder-pro | ❌ | N/A | Never published |
| Other Pro skills | ❌ | N/A | Never published |

---

## Pattern Analysis

**Root cause of every issue:**
1. **Never test published code** — install_locally, run every command, read every README line
2. **README written before code** — spec promises features not yet built
3. **No verification gate** — publish first, fix later attitude
4. **skill.json not audited** — metadata claims never checked against actual code

**2-level failure you identified:**
- **Level 1 (Delivery):** Scoped a sandbox, delivered a scanner (wrong architecture)
- **Level 2 (Honesty):** Called the scanner a "sandbox" anyway (misrepresentation)

**What should have happened:**
1. Build tmpfs + namespaces sandbox → test → then call it a sandbox
2. If effort exceeds scope → rename to "security scanner" before any publish
3. Never claim features in README that don't exist in code

---

## Immediate Actions Required

1. **Unpublish or republish** the-install-sandbox with honest description
2. **Republish** AgentPathfinder Free v1.2.8 (clean, no dashboard)
3. **Manually upload** TRE v1.0.2 via ClawHub web UI (CLI broken)
4. **No new features** until all published work is verified clean
5. **Verify gate:** Every publish gets installed from scratch, every CLI command run, every README claim checked against code

---

Signed: Alex
Date: 2026-04-29 03:40 EDT
