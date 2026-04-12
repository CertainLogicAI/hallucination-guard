### REFERENCE: openclaw ###
# OpenClaw Agents — Framework Overview

OpenClaw is an **agent orchestration platform** that lets you build AI-powered skills that automate tasks across tools and APIs. Agents are autonomous workers that can use tools, make decisions, and execute multi-step workflows.

## Key Concepts

- **Agent** — An autonomous entity with an goal, a set of tools, and a reasoning loop (plan → act → observe)
- **Skill** — A reusable capability (e.g., web scraper, SEO auditor, cold outreach writer) packaged as an agent
- **Tool** — A function the agent can call (HTTP request, database query, file operation, external API)
- **Runtime** — The execution environment (local subprocess, ACP harness, cloud sandbox)

## Architecture

```
User → OpenClaw Gateway → Agent (skill) → Tools → External APIs
                             ↑
                      Memory (context)
```

Agents maintain conversation state, can use tools, and handle errors autonomously.

## Development Model

- Skills are **self-contained** directories with `SKILL.md` (metadata) and optional `code/` or `references/`
- Published to **ClawHub** (marketplace) or run locally
- Support multiple runtimes: Node.js, Python, subprocesses
- Built-in **cron scheduler** for periodic tasks

## Use Cases

- Automated research and reporting
- Content generation at scale
- Data pipeline orchestration
- Multi-channel outreach campaigns
- System monitoring and alerting

## Relationship to FaultTrace

OpenClaw agents can **consume** the FaultTrace API to add AI layers on top of static analysis: generate tests from findings, suggest fixes, create compliance reports.

---
*Canonical reference. Do not edit without updating dependents.*
### END REFERENCE ###
