# CertainLogic Coder Pack — Technical Requirements

## Server Requirements

### Minimal (Free Tier — 100 facts)
- **RAM**: 128 MB (facts DB in memory + LRU cache)
- **Disk**: 10 MB (Python package + facts file)
- **CPU**: Any x86_64 or ARM64 (no GPU required)
- **Python**: 3.11+
- **Network**: Optional (works completely offline after install)

### Recommended (Paid Tier — 333 facts + semantic cache)
- **RAM**: 512 MB (full facts DB + sentence-transformers model)
- **Disk**: 250 MB (includes `all-MiniLM-L6-v2` embedding model)
- **CPU**: 2 cores (for parallel lookups)
- **Python**: 3.12+ (free-threaded mode supported)
- **Network**: Only for updates ($9.99/mo optional)

### Production (Enterprise)
- **RAM**: 1 GB (multiple concurrent queries)
- **Disk**: 500 MB (audit logs + pre-warmed cache)
- **CPU**: 4 cores
- **Network**: Internal LAN access (self-hosted, air-gapped supported)

## What Runs Where

| Component | Runs On | Required? | Port |
|---|---|---|---|
| `hallucination-guard` CLI | Local machine | ✅ Yes (core) | — |
| Facts DB (JSON) | Local filesystem | ✅ Yes (core) | — |
| SQLite cache | Local filesystem | ✅ Yes (auto-created) | — |
| Brain API server | Optional local server | ❌ No (optional) | 8000 |
| Semantic cache model | Optional, in-process | ❌ No (optional) | — |
| MCP server | Optional, local | ❌ No (optional) | configurable |
| Audit log | Local filesystem | ✅ Yes (auto-created) | — |

**Key insight:** You only need the CLI and facts file. Everything else is optional enhancement.

## Install Paths

### Path A: Standalone CLI (no server)

```bash
pip install hallucination-guard
hallucination-guard install          # 100 facts
hallucination-guard status           # Check install
hallucination-guard report           # View hit rates
```

**No server. No API key. No network after install.**

### Path B: Full Brain API (local server)

```bash
pip install hallucination-guard[semantic_cache]
export BRAIN_API_KEY="your_key"
uvicorn hallucination_guard.__main__:app --host 0.0.0.0 --port 8000
```

**Server required only if:**
- You want HTTP API access from other machines
- You want semantic cache (sentence embeddings)
- You want to run as a shared service in a team

### Path C: MCP Server (for Claude/Cursor)

```bash
pip install certainlogic-mcp
certainlogic-mcp --host 127.0.0.1 --port 8000
```

**Server required only for:** Agent integration via MCP protocol.

## GBrain Skill Requirements

**If using the GBrain skill:**

| Requirement | Version | Notes |
|---|---|---|
| GBrain | v1.0.0+ | Frontmatter skills format |
| OpenClaw | Any | Or standalone GBrain |
| CertainLogic | CLI installed | `hallucination-guard install` |
| Brain API | Optional | Only if not using local facts file |

**The GBrain skill is a Markdown file.** It references the CLI but doesn't require a persistent server. Each validation spawns a short-lived CLI process.

## What Does NOT Require a Server

| Feature | Server Needed? | Why |
|---|---|---|
| CLI fact lookup | ❌ No | Direct JSON file read |
| Cache hits | ❌ No | SQLite read |
| Domain gate | ❌ No | Regex classification in-process |
| Hit rate tracking | ❌ No | Local JSON file |
| Offline operation | ❌ No | All files local |
| Air-gapped deploy | ❌ No | No network calls |

## What DOES Require a Server

| Feature | Server Needed? | Why |
|---|---|---|
| HTTP API access | ✅ Yes | FastAPI/uvicorn |
| Semantic cache | ✅ Yes | Sentence-transformers model |
| Multi-machine shared cache | ✅ Yes | Centralized SQLite or Redis |
| MCP protocol | ✅ Yes | MCP server process |
| Remote monitoring | ✅ Yes | Prometheus/metrics endpoint |

## Docker Deployment

```dockerfile
FROM python:3.12-slim
RUN pip install hallucination-guard
COPY free_tier_facts.json /app/
ENV FACTS_DB_PATH=/app/free_tier_facts.json
CMD ["hallucination-guard", "serve", "--host", "0.0.0.0"]
```

**Image size:** ~180 MB (slim Python + package + 100 facts)
**With semantic cache:** ~450 MB (includes transformer model)

## Health Check Commands

```bash
# Check if CLI works
hallucination-guard status

# Check if API server is up (if running)
curl -s http://127.0.0.1:8000/health

# Check facts are loaded
hallucination-guard verify "What is Python's latest version?"

# Check cache hit rates
hallucination-guard report

# GBrain skill check (if applicable)
gbrain doctor
gbrain skillpack-check
```

## Monitoring

| Metric | Source | Alert If |
|---|---|---|
| Cache hit rate | `hallucination-guard report` | < 50% |
| API latency | `/metrics` endpoint | > 500ms p99 |
| Fact DB size | `ls -lh facts_db.json` | Growth > 10%/week |
| Audit log size | `wc -l audit.jsonl` | > 1M entries |
| Domain gate skip rate | `hallucination-guard report` | > 40% unexpected |

## Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| `hallucination-guard: command not found` | Not in PATH | `pip install --user` or use full path |
| `facts_db.json not found` | Not installed | Run `hallucination-guard install` |
| `BRAIN_API_KEY required` | Calling API without key | Set key or use local CLI mode |
| `Connection refused on :8000` | Server not running | Start with `hallucination-guard serve` or skip API |
| `Out of memory` | Semantic cache on small machine | Omit `[semantic_cache]` extra |
| `Permission denied on ~/.hallucination-guard` | Home dir not writable | Set `HALLUCINATION_GUARD_DATA=/path/to/writable/dir` |

## Summary

**Minimum viable setup:**
```bash
pip install hallucination-guard
hallucination-guard install
# Done. Works offline. No server. 100 facts ready.
```

**Most users never need a server.** The CLI + local files handles 95% of use cases. Add a server only when you need HTTP access, semantic cache, or multi-machine deployments.
