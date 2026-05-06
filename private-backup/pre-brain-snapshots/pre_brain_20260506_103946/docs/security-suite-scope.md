# CertainGuard — AI Agent Security Suite

**Mission:** The first comprehensive security layer for AI agent deployments. Not just scanning — protecting.

**Positioning:** Business-grade security available to everyone. Think "CrowdStrike for AI agents" meets "npm audit for skills."

---

## The Problem

AI agents are becoming autonomous. They:
- Execute shell commands unsupervised
- Install packages from unknown sources  
- Handle API keys and credentials
- Run continuously without human oversight
- Connect to external services (Slack, email, databases)

**Current state:** Zero security tooling exists for AI agent deployments. Developers ship agents the same way they shipped web apps in 2005 — blind trust, no scanning, no validation.

**Attack surfaces:**
1. Malicious skills (backdoored ClawHub packages)
2. Prompt injection ("ignore all previous instructions")
3. Secret leakage (API keys in logs, configs, memory)
4. Dependency poisoning (typosquatting, compromised packages)
5. Privilege escalation (agents with sudo, file system access)
6. Data exfiltration (agents uploading company data)

---

## Components

### Module 1: SkillGuard — ClawHub/Skill Marketplace Scanner
**What it does:** Evaluates every skill before installation.

| Check | Severity | Implementation |
|-------|----------|----------------|
| VirusTotal API scan | CRITICAL | File hash check |
| Prompt injection patterns | CRITICAL | Regex + heuristics |
| Hardcoded secrets | CRITICAL | Entropy analysis + keyword matching |
| Network calls (curl/wget/fetch) | HIGH | Static analysis |
| File system operations | HIGH | rm -rf, chmod, sudo detection |
| Code execution (exec/eval) | CRITICAL | AST parsing |
| Pipe-to-shell installs | HIGH | Pattern matching |
| Dependency audit | MEDIUM | Check for known malicious packages |
| License validation | LOW | OSI-approved check |
| Supply chain verification | MEDIUM | Owner reputation, update recency |

**Output:** Security score (A-F), detailed report, install/block recommendation.

---

### Module 2: AgentGuard — Runtime Security Monitoring
**What it does:** Watches your running agents for suspicious behavior.

| Detection | Method | Response |
|-----------|--------|----------|
| Unexpected network calls | Network trace monitoring | Alert + kill agent |
| File system access outside workspace | Syscall monitoring | Alert + block |
| Credential access attempts | Hook on os.environ, keyring | Alert + mask |
| Privilege escalation | sudo/su detection | Immediate kill |
| Prompt injection attempts | Input sanitization check | Block + log |
| Excessive token usage (DoS) | Rate limiting | Throttle + alert |

**Output:** Real-time security dashboard, incident reports, automatic containment.

---

### Module 3: SecretGuard — Credential & Config Scanner
**What it does:** Finds secrets before they leak.

| Source | Method |
|--------|--------|
| Environment variables | Scan for KEY=, TOKEN=, SECRET= patterns |
| Config files | YAML/JSON/TOML secret detection |
| Code files | Entropy analysis for API keys, regex for common patterns |
| Memory dumps | Prevent secrets in swap/logs |
| Git history | Scan commits for accidentally committed secrets |
| Agent memory files | Ensure no credentials in agent memory |

**Integrations:** GitHub Secret Scanning, AWS Secrets Manager, HashiCorp Vault.

---

### Module 4: DependencyGuard — Supply Chain Security
**What it does:** Verifies every dependency your agents use.

| Check | Data Source |
|-------|-------------|
| Known CVEs | NVD (National Vulnerability Database) |
| Typosquatting detection | Levenshtein distance from popular packages |
| Package reputation | Download counts, maintainer activity, stars |
| Integrity verification | SHA-256 hash check against registry |
| License compliance | SPDX license detection |
| Transitive dependency audit | Full tree scan |

**Output:** Dependency health report, upgrade recommendations, vulnerability alerts.

---

### Module 5: PolicyGuard — Security Policy Enforcement
**What it does:** Enforces security rules across all agents.

```yaml
# Example policy file
global:
  max_file_size: 10MB
  allowed_network_hosts:
    - api.openai.com
    - github.com
  blocked_commands:
    - rm -rf /
    - sudo
  secret_rotation_days: 90
  
agents:
  production:
    sandbox: required
    network: restricted
    file_access: read-only
    
  development:
    sandbox: optional
    network: unrestricted
    file_access: read-write
```

**Features:**
- Policy-as-code (YAML)
- Per-agent policy assignment
- Automatic policy enforcement
- Violation logging and alerting
- Compliance reporting (SOC2, ISO 27001 mappings)

---

### Module 6: AuditGuard — Compliance & Forensics
**What it does:** Complete audit trail for security events.

| Feature | Description |
|---------|-------------|
| Cryptographic audit trail | HMAC-SHA256 signed events (AgentPathfinder integration) |
| Tamper-evident logs | Blockchain-style chaining |
| Compliance reports | SOC2, ISO 27001, GDPR mappings |
| Incident response | Automated playbook triggers |
| Forensic timeline | Reconstruct exactly what happened |
| Export | PDF, JSON, SIEM integration |

---

## Architecture

```
┌─────────────────────────────────────────┐
│           CertainGuard CLI              │
│     (clawhub install certainguard)      │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
┌───▼────┐         ┌─────▼──────┐
│Local   │         │ Cloud API  │
│Scanner │         │ (optional) │
└───┬────┘         └─────┬──────┘
    │                    │
    └────────┬───────────┘
             │
    ┌────────▼────────┐
    │  AgentPathfinder │
    │  Audit Trail     │
    └─────────────────┘
```

**Deployment modes:**
1. **Local (Free):** Runs on developer machine, all modules except cloud threat intel
2. **Team (Pro):** Shared dashboard, team policies, Slack/email alerts
3. **Enterprise:** On-prem deployment, SIEM integration, custom policies, compliance reports

---

## Revenue Model

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | SkillGuard (basic), SecretGuard (local files), DependencyGuard (top-level only) |
| **Pro** | $29/mo/agent | All modules, team dashboard, cloud threat intel, API access |
| **Enterprise** | Custom | On-prem, SIEM, custom policies, compliance reports, priority support |

**Alternative pricing:** Per-scan (API credits) for CI/CD integration.

---

## MVP Scope (Week 1)

**Goal:** Ship something useful immediately.

1. **SkillGuard Basic** — Security scan any ClawHub skill
   - File hash check (VirusTotal API)
   - Regex pattern matching (prompt injection, exec/eval, secrets)
   - Score + report
   - CLI: `certainguard scan <skill-slug>`

2. **SecretGuard Basic** — Scan workspace for secrets
   - grep-based + entropy analysis
   - Config file scanning
   - Report: found secrets with file locations

3. **Integration** — Hook into AgentPathfinder auto-build
   - Every build triggers security scan
   - Block build on CRITICAL findings
   - Report in build output

**Deliverable:** ClawHub skill + standalone CLI. Free tier fully functional.

---

## Competitive Landscape

| Product | What They Do | Gap CertainGuard Fills |
|---------|-------------|------------------------|
| Snyk | Dependency CVEs | No agent/skill awareness |
| GitGuardian | Secret detection | No runtime agent monitoring |
| CrowdStrike | Endpoint security | No AI agent-specific detection |
| Socket.dev | Supply chain | No skill marketplace scanning |
| **CertainGuard** | **AI agent security** | **Purpose-built for autonomous agents** |

**Differentiator:** We understand AI agents. We know they install skills, execute code, and run unsupervised. Generic security tools don't account for this attack surface.

---

## Technical Stack

| Component | Tech |
|-----------|------|
| CLI | Python (typer/click) |
| Skill scanner | AST parsing + regex + entropy analysis |
| Runtime monitor | eBPF (Linux) / Endpoint Security API (macOS) |
| Secret detection | truffleHog-style entropy + regex patterns |
| Dependency audit | OSV API + NVD feed |
| Dashboard | FastAPI + htmx (lightweight) |
| Audit trail | AgentPathfinder integration (HMAC-SHA256) |
| Reports | WeasyPrint (PDF) + JSON export |

---

## Success Metrics

| Metric | Target (Month 1) | Target (Month 3) |
|--------|------------------|------------------|
| Skills scanned | 100 | 1,000 |
| Secrets found | 50 | 500 |
| CVEs detected | 20 | 200 |
| Active installs | 50 | 500 |
| Enterprise demos | 2 | 10 |

---

## Risks

| Risk | Mitigation |
|------|------------|
| False positives overwhelm users | Tuning + severity levels + user feedback loop |
| VirusTotal API limits | Caching + tiered access |
| Runtime monitoring is OS-specific | Start with Linux (eBPF), expand later |
| Enterprise sales cycle is long | Lead with free/pro, upsell organically |

---

## Next Steps

1. **Day 1:** Build SkillGuard MVP (scan + score + report)
2. **Day 2:** Build SecretGuard MVP (scan workspace)
3. **Day 3:** Integrate with AgentPathfinder auto-build
4. **Day 4:** ClawHub skill packaging + publishing
5. **Day 5:** X announcement, blog post, influencer outreach

**6 weeks to Pro tier.** Enterprise follows after 3 paying customers.

---

*CertainGuard: Because trusting your AI agent without verification is gambling with your data.*
