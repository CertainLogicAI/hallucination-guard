# Agent-Action Tracker

## Overview

An append-only logging system that tracks all agent actions, verifies task completion via validators, and stores immutable records in SQLite for auditability and debugging.

## Components

### 1. Core Tracker (`action_tracker.py`)
- `@track_action` decorator that wraps any agent method
- Logs: agent_name, method, start_ts, end_ts, input_json, output_json, output_hash, status, error
- Custom validators determine success/failure per method
- SQLite backend (`agent_actions.db`)

### 2. Validators
- `nonempty_str` - verifies non-empty string output
- `exact_hash_match` - compares output hash to expected
- Custom validator support via lambda functions

### 3. Audit API (`/actions`)
- Read-only endpoint to query logs
- Filters: agent, status (SUCCESS/FAILED/ERROR), since, limit
- Returns immutable records

## Database Schema

```sql
CREATE TABLE actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT,
    method TEXT,
    start_ts TEXT,
    end_ts TEXT,
    input_json TEXT,
    output_json TEXT,
    output_hash TEXT,
    status TEXT,
    error TEXT
);
```

## Integration

```python
from action_tracker import track_action

@track_action(agent_name="DeterministicEngine", validator=nonempty_str)
def run_query(self, query: str) -> str:
    # method implementation
    return answer
```

## Usage Examples

### Query Logs
```bash
curl "http://localhost:8000/actions?agent=DeterministicEngine&status=FAILED"
```

### Add Validator
```python
@track_action(agent_name="MyAgent", validator=lambda r: r.startswith("OK"))
def my_method(self):
    return "OK"
```

## Status Values

- **SUCCESS** - validator returned True
- **FAILED** - validator returned False
- **ERROR** - exception raised during execution

## Future Extensions

- Alerting on FAILED/ERROR entries
- Grafana dashboard
- Versioned validators
- Distributed storage (PostgreSQL/ClickHouse)
- Web UI for log browsing

## Files

- `/data/.openclaw/workspace/action_tracker.py` - Core tracker module
- `/data/.openclaw/workspace/agent_actions.db` - SQLite database
- `/data/.openclaw/workspace/api.py` - Audit endpoint

## Created

- Date: 2026-04-08
- Context: MVP upgrade scoping for Deterministic AI Brain