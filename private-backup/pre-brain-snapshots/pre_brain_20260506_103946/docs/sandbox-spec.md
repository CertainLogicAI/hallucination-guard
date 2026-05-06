# CertainGuard Sandbox — Technical Specification

## Overview
Isolated environment for testing ClawHub skills before installation. Runs skill in a tmpfs jail with no network access, monitors behavior, generates security report.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        HOST SYSTEM                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              CertainGuard Controller                  │   │
│  │  (Python CLI: `certainguard install <skill-slug>`)   │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                     │
│         ┌─────────────▼──────────────┐                    │
│         │    Linux Namespaces        │                    │
│         │    ┌──────────────────┐    │                    │
│         │    │   tmpfs (50MB)   │    │                    │
│         │    │   ┌───────────┐  │    │                    │
│         │    │   │ Skill Dir │  │    │                    │
│         │    │   │ + sandbox │  │    │                    │
│         │    │   └───────────┘  │    │                    │
│         │    │   Network: DROP  │    │                    │
│         │    │   Time: 5min max │    │                    │
│         │    └──────────────────┘    │                    │
│         └────────────────────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Sandbox Controller (`sandbox.py`)
Creates and manages isolated environment.

**Methods:**
```python
class Sandbox:
    def create(self, size_mb=50, timeout_sec=300) -> str
    def install_skill(self, slug: str, sandbox_id: str) -> bool
    def run_scan(self, sandbox_id: str) -> SecurityReport
    def destroy(self, sandbox_id: str) -> bool
    def get_logs(self, sandbox_id: str) -> list[str]
```

**Isolation techniques:**
- `unshare --mount --net --pid --ipc --uts` (Linux namespaces)
- `mount -t tmpfs -o size=50M tmpfs /sandbox/<id>` (tmpfs)
- `iptables -A OUTPUT -j DROP` (network isolation)
- `timeout 300` (process timeout)
- `setrlimit(RLIMIT_AS, 100 * 1024 * 1024)` (memory limit)

### 2. Security Scanner (`scanner.py`)
Analyzes everything the skill did in the sandbox.

**Detection categories:**
| Category | Patterns | Severity |
|----------|----------|----------|
| Prompt injection | `ignore previous`, `you are now`, `system override` | CRITICAL |
| Code execution | `exec(`, `eval(`, `__import__`, `subprocess` | CRITICAL |
| Network access | Any outbound connection attempt | HIGH |
| File system | Access outside skill dir, rm -rf, chmod | HIGH |
| Secret leakage | `api_key`, `token`, `password`, `secret` (entropy > 4.5) | CRITICAL |
| Privilege escalation | `sudo`, `chmod +s`, `setuid` | CRITICAL |
| Obfuscation | Base64 encoded strings, hex encoding | MEDIUM |
| Suspicious imports | `socket`, `urllib`, `requests`, `paramiko` | MEDIUM |

**Scoring:**
- CRITICAL = 10 points
- HIGH = 5 points  
- MEDIUM = 2 points
- LOW = 1 point
- Total > 20 = BLOCK
- Total > 10 = WARNING
- Total ≤ 10 = PASS

### 3. Report Generator (`reporter.py`)
Generates human-readable security report.

**Output format:**
```json
{
  "skill": "certainlogicai/agentpathfinder",
  "version": "1.2.7",
  "timestamp": "2026-04-28T13:00:00Z",
  "verdict": "PASS|WARNING|BLOCK",
  "score": 3,
  "findings": [
    {
      "severity": "MEDIUM",
      "category": "suspicious_imports",
      "file": "scripts/hguard_client.py",
      "line": 12,
      "description": "Imports urllib.request (network capability)",
      "evidence": "from urllib.request import Request, urlopen"
    }
  ],
  "sandbox_logs": [
    "[13:00:01] Process started: python3 setup.py",
    "[13:00:02] File created: /skill/scripts/hguard_client.py",
    "[13:00:03] No network activity detected"
  ],
  "recommendation": "Install approved — score 3/10, only medium finding is expected urllib import for API client"
}
```

### 4. CLI Interface (`__main__.py`)
```bash
# Install a skill (with sandbox + scan)
certainguard install certainlogicai/agentpathfinder

# Scan without installing
certainguard scan certainlogicai/agentpathfinder

# View last report
certainguard report

# Set policy (auto-approve if score < 5)
certainguard policy --auto-approve 5
```

## Implementation Details

### File Structure
```
certainguard/
├── __init__.py
├── __main__.py          # CLI entry point
├── sandbox.py           # Namespace/tmpfs management
├── scanner.py           # Pattern detection + scoring
├── reporter.py          # Report generation (JSON + text)
├── policy.py            # User policy configuration
├── utils.py             # Helpers (entropy calc, file walking)
└── patterns/
    ├── __init__.py
    ├── injection.py     # Prompt injection patterns
    ├── execution.py     # Code execution patterns
    ├── network.py       # Network-related imports
    ├── secrets.py       # Secret detection regex
    └── obfuscation.py   # Encoding/obfuscation patterns
```

### Sandbox Creation Script
```bash
#!/bin/bash
# create-sandbox.sh — Run with sudo

SANDBOX_ID="$1"
SIZE_MB="${2:-50}"
TIMEOUT="${3:-300}"

# Create tmpfs
mkdir -p /tmp/cg-sandbox/$SANDBOX_ID
mount -t tmpfs -o size=${SIZE_MB}M,mode=1777 tmpfs /tmp/cg-sandbox/$SANDBOX_ID

# Drop network (create network namespace)
ip netns add cg-$SANDBOX_ID
ip netns exec cg-$SANDBOX_ID iptables -P OUTPUT DROP

# Run skill install in namespace
timeout $TIMEOUT ip netns exec cg-$SANDBOX_ID \
  unshare --mount --pid --fork --ipc --uts \
  chroot /tmp/cg-sandbox/$SANDBOX_ID /bin/bash -c "$4"

# Cleanup
ip netns del cg-$SANDBOX_ID 2>/dev/null
umount /tmp/cg-sandbox/$SANDBOX_ID
rm -rf /tmp/cg-sandbox/$SANDBOX_ID
```

### Python Fallback (no sudo)
If namespaces unavailable, use:
- Virtualenv isolation
- `socket` monkey-patch to block network
- `os` monkey-patch to track file access
- Thread-level timeout

## Testing

1. **Test with known-bad skill:** Create test skill with `exec()`, `rm -rf`, hardcoded API key → verify BLOCK
2. **Test with clean skill:** Our own AgentPathfinder → verify PASS
3. **Test with edge case:** Skill using urllib (like TRE) → verify WARNING with correct context
4. **Mock namespace failures:** Ensure Python fallback works

## Integration Points

1. **ClawHub:** Hook into `clawhub install` command
2. **AgentPathfinder:** Run as build step in auto_build pipeline
3. **CI/CD:** GitHub Action that runs certainguard on PR

## Deliverables

1. ✅ Working Python package with CLI
2. ✅ Sandbox creation (namespace or fallback)
3. ✅ Security scanner with 30+ checks
4. ✅ Report generator (JSON + human-readable)
5. ✅ Integration tests with good/bad skills
6. ✅ SKILL.md for ClawHub publication
7. ✅ Published on ClawHub
