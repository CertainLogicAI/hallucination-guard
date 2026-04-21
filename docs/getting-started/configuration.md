# Configuration

CertainLogic Verifier is configured via environment variables.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FACTS_DB_PATH` | `./facts_db.json` | Path to the verified facts database |
| `CACHE_DB_PATH` | `./cache.db` | SQLite cache location |
| `MEMORY_DIR` | `./memory` | Directory for markdown memory files (TF-IDF search) |
| `PORT` | `8000` | HTTP port |
| `HOST` | `0.0.0.0` | Bind address |
| `LOG_LEVEL` | `info` | Logging level (`debug`, `info`, `warning`, `error`) |

## Facts Database

The facts database is a JSON file with verified ground-truth entries. See the [Facts Schema reference](../api/facts-schema.md) for the full specification.

```bash
export FACTS_DB_PATH=/path/to/your/company_facts.json
```

## Semantic Cache

To enable semantic caching (requires `sentence-transformers`):

```bash
pip install "hallucination-guard[semantic_cache]"
```

The semantic cache automatically downloads and caches the embedding model on first use (~500MB).

## Docker Configuration

Pass environment variables to Docker:

```bash
docker run -d \
  -e FACTS_DB_PATH=/app/data/facts.json \
  -e CACHE_DB_PATH=/app/data/cache.db \
  -v ./data:/app/data \
  -p 8000:8000 \
  ghcr.io/certainlogicai/hallucination-guard:latest
```
