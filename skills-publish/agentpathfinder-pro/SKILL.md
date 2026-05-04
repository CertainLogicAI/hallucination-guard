---
summary: "AgentPathfinder Pro — dashboard and multi-agent upgrades"
read_when: ["installing", "upgrading", "dashboard"]
name: AgentPathfinder Pro
description: "Dashboard and multi-agent upgrades for AgentPathfinder. Includes static HTML reports, live Flask dashboard, and subagent delegation views. Requires AgentPathfinder Free installed first."
version: 1.0.0
author: CertainLogic
license: Commercial
platforms: [linux, macos]
---

# AgentPathfinder Pro

Dashboard and multi-agent upgrades for AgentPathfinder.

## Requirements

- AgentPathfinder Free installed
- Python 3.10+
- Flask (for live dashboard)

## Install

```bash
clawhub install agentpathfinder-pro
```

## Features

### Static HTML Dashboard
```bash
python3 dashboard_static.py --output report.html
```

### Live Dashboard
```bash
python3 pro_dashboard.py --port 8080
```

### Multi-Agent Subagent View
```bash
python3 pro_dashboard_v2.py --port 8080 --mode subagent
```

## License

Commercial license required. Contact beta@certainlogic.ai for early access.
