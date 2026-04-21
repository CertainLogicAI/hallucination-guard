# Docker Deployment

## Quick Start

```bash
docker run -d --name hallucination-guard \
  -p 8000:8000 \
  -v ./facts_db.json:/app/facts_db.json:ro \
  ghcr.io/certainlogicai/hallucination-guard:latest
```

## Docker Compose

```yaml
version: "3.8"
services:
  hallucination-guard:
    image: ghcr.io/certainlogicai/hallucination-guard:latest
    ports:
      - "8000:8000"
    volumes:
      - ./facts_db.json:/app/facts_db.json:ro
      - guard-data:/app/data
    environment:
      - FACTS_DB_PATH=/app/facts_db.json
      - CACHE_DB_PATH=/app/data/cache.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  guard-data:
```

## Build From Source

```bash
git clone https://github.com/CertainLogicAI/hallucination-guard.git
cd hallucination-guard
docker build -t hallucination-guard .
docker run -d -p 8000:8000 hallucination-guard
```

## Persistent Data

Mount a volume for the data directory to persist cache across restarts:

```bash
docker run -d \
  -v guard-data:/app/data \
  -p 8000:8000 \
  ghcr.io/certainlogicai/hallucination-guard:latest
```

## Resource Requirements

- **CPU:** 1 core minimum, 2 recommended
- **RAM:** 512MB minimum (2GB if using semantic cache with sentence-transformers)
- **Disk:** 100MB + size of your facts database + cache growth
