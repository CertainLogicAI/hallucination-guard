# Installation

## From Source (recommended for development)

```bash
git clone https://github.com/CertainLogicAI/hallucination-guard.git
cd hallucination-guard
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## From PyPI

```bash
pip install hallucination-guard
```

With optional semantic cache support:

```bash
pip install "hallucination-guard[semantic_cache]"
```

With LangChain integration:

```bash
pip install "hallucination-guard[langchain]"
```

## Docker

```bash
docker run -d --name hg \
  -p 8000:8000 \
  -v ./facts_db.json:/app/facts_db.json:ro \
  ghcr.io/certainlogicai/hallucination-guard:latest
```

## Kubernetes (Helm)

```bash
helm install hallucination-guard deploy/helm/hallucination-guard \
  --set replicaCount=2 \
  --set persistence.enabled=true
```

See [Kubernetes deployment guide](../deployment/kubernetes.md) for full Helm values.

## Requirements

- Python ≥ 3.11
- No GPU required (CPU-only by default)
- Optional: `sentence-transformers` for semantic cache (requires ~500MB for model download)
