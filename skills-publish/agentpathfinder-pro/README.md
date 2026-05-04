# AgentPathfinder Pro

Dashboard upgrades for AgentPathfinder.

## What's Included

| Feature | Free | Pro |
|---------|------|-----|
| Task tracking | ✅ | ✅ |
| Audit trail | ✅ | ✅ |
| CLI export | ✅ | ✅ |
| Static HTML dashboard | ❌ | ✅ |
| Live dashboard (Flask) | ❌ | ✅ |
| Multi-agent views | ❌ | ✅ |
| Subagent delegation | ❌ | ✅ |

## Install

```bash
# Install free version first
clawhub install agentpathfinder-agent-task-tracker-free

# Then install Pro upgrade (coming soon)
clawhub install agentpathfinder-pro
```

## Usage

### Static HTML Dashboard
```bash
python3 dashboard_static.py --output report.html
# Open report.html in your browser
```

### Live Dashboard
```bash
python3 pro_dashboard.py --port 8080
# Open http://localhost:8080
```

### Multi-Agent Subagent View
```bash
python3 pro_dashboard_v2.py --port 8080 --mode subagent
```

## License

Pro features require a license key. Contact beta@certainlogic.ai for early access.
