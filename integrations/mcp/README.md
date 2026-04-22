# CertainLogic MCP Server

Verified fact lookup for AI agents via the Brain API. Eliminates hallucinations on covered domains.

**PyPI version** | **Python 3.10+** | **License MIT**

## What It Does

AI agents hallucinate on factual questions. CertainLogic provides a pre-verified fact database + hallucination guard that returns:

- **Verified answer** — when the fact is in our database
- **Honest `uncertain`** — when we don't know (instead of guessing)
- **Hallucination detection** — when given a claim + source text

The MCP server wraps this as tools your agent can call automatically.

## Quick Start

### 1. Install

```bash
pip install certainlogic-mcp
# or: uv add certainlogic-mcp
```

### 2. Set Your API Key

```bash
export BRAIN_API_KEY=your_key_here
# Free tier: 100 queries/day at https://certainlogic.ai/signup
```

### 3. Add to Claude Code

```bash
claude mcp add certainlogic-brain -- certainlogic-mcp
```

Or manually, add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "certainlogic-brain": {
      "command": "certainlogic-mcp",
      "env": {
        "BRAIN_API_KEY": "your_key_here"
      }
    }
  }
}
```

### 4. Test

Ask Claude Code:

> "What's the default timeout for Python's requests library?"

Claude will call `brain_api_query` and return:

> "The default timeout is `None` — requests will hang indefinitely unless you specify a timeout."

## Tools

| Tool | Purpose | Returns |
|---|---|---|
| `brain_api_query` | Single fact lookup | answer + confident + method |
| `batch_query` | Validate multiple facts at once | aggregated results with counts |
| `verify_fact_guard` | Hallucination detection against source text | valid/invalid/unclear |
| `health_check` | Check Brain API availability | ok / degraded / down |

## Response Methods

| Method | Meaning | Speed | Cost |
|---|---|---|---|
| `cache` | Semantic cache hit | < 50ms | $0 |
| `facts` | Pre-verified fact database | < 100ms | $0 |
| `llm` | LLM validated the answer | 2-5s | ~$0.0001 |
| `uncertain` | No data, not guessing | 50-100ms | $0 |

## Configuration

| Environment Variable | Description | Default |
|---|---|---|
| `BRAIN_API_KEY` | Brain API key (required) | — |
| `BRAIN_API_ENDPOINT` | Query endpoint | `https://api.certainlogic.ai/query` |
| `BRAIN_VALIDATE_ENDPOINT` | Guard endpoint | `https://api.certainlogic.ai/validate` |
| `BRAIN_HEALTH_ENDPOINT` | Health endpoint | `https://api.certainlogic.ai/health` |
| `BRAIN_API_TIMEOUT` | Request timeout (seconds) | `10` |
| `BRAIN_API_MAX_RETRIES` | Max retries on server errors | `3` |
| `MCP_LOG_LEVEL` | Logging level | `INFO` |

## Telemetry

Each invocation logs a hashed query identifier (SHA-256, first 8 hex chars) with method and latency:

```
[BRAIN_API] ts=1713456789.123 query_hash=a1b2c3d4 method=facts latency_ms=42
```

**No PII or query content is logged.** Only hash, method, and timing are recorded.

## Documentation

- [Installation Guide](docs/installation.md)
- [Architecture](docs/architecture.md)
- [Usage Examples](docs/usage.md)
- [API Reference](docs/api-reference.md)

## Developing

```bash
git clone https://github.com/CertainLogicAI/certainlogic-mcp.git
cd certainlogic-mcp
pip install -e ".[dev]"
pytest tests/ -v
```

## Links

- [CertainLogic](https://certainlogic.ai)
- [GitHub Repository](https://github.com/CertainLogicAI/certainlogic-mcp)
- [Issues](https://github.com/CertainLogicAI/certainlogic-mcp/issues)
