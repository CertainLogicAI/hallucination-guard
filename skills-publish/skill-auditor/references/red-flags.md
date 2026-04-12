---
summary: "\"Red Flags Reference\""
read_when: ["[]"]
---
# Red Flags Reference

Quick reference for security and quality red flags during skill audits.

## Security Red Flags (reject or deep review)

### Critical — Do Not Install
- **Prompt injection patterns** — "ignore previous instructions", "you are now", "forget your instructions"
- **Obfuscated code** — base64 encoding, eval(), exec(), fromCharCode in scripts
- **Data exfiltration** — scripts sending local files or data to external URLs
- **Hidden credentials** — hardcoded API keys, tokens, or passwords in source

### Serious — Deep Manual Review Required
- **VirusTotal flagged** — ClawHub flagged the skill as suspicious during install
- **Pipe-to-shell installs** — `curl | sh`, `wget | bash` patterns
- **Auto-token fetching** — skill automatically requests/stores tokens from third-party APIs without explicit user consent
- **Excessive network calls** — scripts that phone home to unknown servers
- **Cryptocurrency wallet addresses** — donation links embedded in skill logic (not docs)

### Moderate — Note and Monitor
- **Broad exec permissions** — `allowed-tools: Bash(*)` without scoping
- **Third-party platform lock-in** — all functionality routed through one external service
- **Stale dependencies** — npm packages with known vulnerabilities
- **No license specified** — unclear usage rights

## Quality Red Flags (skip or deprioritize)

### Structure Issues
- **No YAML frontmatter** — skill won't trigger properly in OpenClaw
- **Missing description** — agent can't determine when to use the skill
- **SKILL.md > 500 lines** — bloats context window, should be split
- **Unnecessary files** — README.md, CHANGELOG.md, REVIEW.md (per AgentSkill spec)
- **"When to Use" in body** — duplicates frontmatter description, wastes tokens

### Content Issues
- **Marketing wrapper** — impressive description but just points to external repos/services
- **JSON config wishlist** — lists 30+ capabilities with zero implementation
- **Generic advice** — nothing you couldn't get from asking any LLM directly
- **Stale content** — references outdated APIs, deprecated tools, old versions
- **Non-English without translation** — limits usability unless you read the language

### Dependency Issues
- **Requires paid external service** — no free tier or trial available
- **Platform lock-in** — all actions go through one company's API
- **Heavy binary dependencies** — requires installing large toolchains
- **Undocumented requirements** — needs tools/accounts not listed in frontmatter
