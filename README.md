# CertainLogic Verifier – Open‑source deterministic AI verification

> **Deterministic AI verification middleware for regulated industries (healthcare, finance, government).**
> Transparent, auditable, and self‑hosted. Built for compliance, trust, and control.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)

---

## Why CertainLogic Verifier?

AI hallucinations are a business‑critical risk. But closed‑source “black box” verification tools create their own risks: lack of auditability, data‑residency concerns, and vendor lock‑in.

**CertainLogic Verifier** gives you:
- **Open‑source transparency** – every line of verification logic is inspectable by your security/compliance teams.
- **Self‑hosted deployment** – runs entirely inside your VPC, air‑gapped environment, or on‑premises infrastructure.
- **Deterministic verification** – cross‑checks AI outputs against a versioned, curated facts database.
- **Zero‑cost token reduction** – cached queries bypass LLM calls entirely, cutting inference costs by up to 98%.
- **Regulatory‑ready** – designed for HIPAA, GDPR, SOC2, FedRAMP, and other compliance frameworks.

Built for **enterprises, consultancies, and regulated industries** that need trustworthy AI without sacrificing control.

---

## What’s Included

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Hallucination Detector** | Fact‑consistency validation | Rule‑based factual matching, uncertainty detection, internal contradiction checks, specificity validation |
| **Token Reduction Engine** | Token budgeting + caching | SQLite‑backed LRU cache, semantic similarity lookup, deterministic summarization fallback |
| **Semantic Cache (L2)** | Similarity‑based retrieval | Sentence‑transformers embeddings, cosine similarity, optional extra dependency |
| **Deterministic Memory Search** | Local document retrieval | Embedding‑free TF‑IDF search over `.md` files, hash‑verified snippets |
| **Intent Classifier** | Rule‑based query routing | Zero‑LLM classification, configurable model mapping, domain detection |
| **Intent Router** | Orchestration layer | Combines token reduction + classification for routing decisions |
| **FastAPI Service** | Production‑ready API | REST endpoints for validation, reduction, search, routing, metrics |

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/certainlogic/verifier.git
cd verifier
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Run the Service

```bash
export FACTS_DB_PATH=./facts_db.json
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Validate Your First Query

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?", "response": "Paris"}'
```

**Response:**
```json
{
  "query": "What is the capital of France?",
  "response_length": 5,
  "valid": true,
  "flagged": false,
  "confidence": 1.0,
  "severity": "none",
  "checks": { ... },
  "flags": []
}
```

### 4. Reduce Token Count

```bash
curl -X POST http://localhost:8000/reduce \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain quantum entanglement in simple terms...", "semantic": true}'
```

---

## Deployment Patterns

### Docker (Single Container)

```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes (Helm)

Example Helm chart included in `deploy/helm/`.

### Air‑Gapped / On‑Premises

1. Build the Docker image inside your secure network.
2. Push to a private registry.
3. Deploy with persistent volume for `cache.db` and `facts_db.json`.
4. Configure network policies to block all egress (no external API calls).

---

## Configuration

All components are configured via environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `FACTS_DB_PATH` | `./facts_db.json` | Path to versioned facts database |
| `CACHE_DB_PATH` | `./cache.db` | SQLite cache database path |
| `TOKEN_MAX_PER_QUERY` | `512` | Hard token limit before summarization |
| `CACHE_SIZE_LIMIT` | `1000` | Maximum cache entries |
| `CACHE_TTL_SECONDS` | `3600` | Cache entry time‑to‑live |
| `SEMANTIC_THRESHOLD` | `0.92` | Cosine similarity floor for semantic lookup |
| `SEMANTIC_MODEL` | `all-MiniLM-L6-v2` | Sentence‑transformers model name |
| `MEMORY_DIR` | `./memory` | Directory for deterministic search files |
| `MODEL_HAIKU` | `anthropic/claude-haiku-4-5` | Model name for simple queries |
| `MODEL_SONNET` | `anthropic/claude-sonnet-4-6` | Model name for moderate queries |
| `MODEL_OPUS` | `anthropic/claude-opus-4-6` | Model name for complex queries |
| `FACTS_DOMAINS` | `plc,l5x,compliance,...` | Comma‑separated domain keywords |

---

## API Reference

### `POST /validate`
Validate a query–response pair.

**Request:**
```json
{
  "query": "What is 2+2?",
  "response": "The answer is 5."
}
```

**Response:** Full validation result with confidence, flags, and per‑check scores.

### `POST /reduce`
Reduce token count of a query (cached or summarised).

**Request:**
```json
{
  "query": "A very long query...",
  "force_deterministic": false,
  "semantic": true
}
```

**Response:** Reduced query, token counts, cache hit status, and routing decision.

### `POST /search`
Search local memory files using TF‑IDF.

**Request:**
```json
{
  "query": "PLC safety standards",
  "top_k": 5
}
```

**Response:** Snippets with file paths, line numbers, and SHA‑256 hashes.

### `POST /route`
Token‑reduce + classify a query.

**Request:** `query` string as plain text.

**Response:** Original and compressed query, token count, intent classification, recommended model and handler.

### `GET /metrics`
Cache hit rate, token savings, and engine statistics.

### `DELETE /cache`
Clear the token‑reduction cache (keeps schema).

---

## Extending the Facts Database

The facts database is a versioned JSON file:

```json
{
  "facts": {
    "unique fact key": {
      "type": "numeric|string",
      "value": "expected value",
      "tolerance": 0.01,           // optional, for numeric facts
      "unit": "m/s"                // optional, for numeric facts
    }
  }
}
```

**Example workflow:**
1. Export your internal knowledge base (prices, policies, compliance rules, product specs) to JSON.
2. Load via `FACTS_DB_PATH`.
3. The detector will flag any AI response that contradicts these facts.

---

## Integration Examples

### LangChain / LlamaIndex

```python
from hallucination_detector import HallucinationDetector

detector = HallucinationDetector(facts_db_path="./company_facts.json")

def validate_chain_output(query: str, response: str) -> bool:
    result = detector.validate(query, response)
    if not result["valid"]:
        logger.warning(f"Hallucination detected: {result['flags']}")
    return result["valid"]
```

### FastAPI Middleware

```python
from fastapi import FastAPI, Request
app = FastAPI()

@app.middleware("http")
async def verify_ai_output(request: Request, call_next):
    response = await call_next(request)
    # Extract query/response from request/response
    # Validate using detector
    # Log or block invalid outputs
    return response
```

### Airflow / Prefect Pipeline

```python
from token_reduction_engine import reduce_tokens

def compress_query(task_instance):
    query = task_instance.xcom_pull(task_ids="previous")
    reduced = reduce_tokens(query, semantic=True)
    task_instance.xcom_push(key="compressed_query", value=reduced["reduced_query"])
```

---

## Compliance & Security

### Audit Trail
Every validation event can be logged to an append‑only JSONL file with SHA‑256 hash chaining. Example logging configuration provided in `examples/audit_logger.py`.

### Data Residency
No data leaves your environment. The entire stack runs inside your VPC, private cloud, or air‑gapped network.

### SBOM & Vulnerability Scanning
We provide a Software Bill of Materials (SBOM) in `sbom.spdx.json`. Regularly updated with vulnerability reports.

### Certification Support
Our deployment patterns are designed to meet:
- **HIPAA** – No PHI exfiltration, audit logging, access controls.
- **GDPR** – Data locality, right to erasure (cache clearing), transparency.
- **SOC2** – Security, availability, processing integrity.
- **FedRAMP** – Controlled environments, no external dependencies.

---

## Roadmap

- **Q2 2026** – GPU‑accelerated embedding backfill, PostgreSQL vector store support.
- **Q3 2026** – Multi‑modal verification (image, audio, video), real‑time streaming validation.
- **Q4 2026** – Federated learning for fact‑database sharing (enterprise‑only).

---

## License

MIT License – see [LICENSE](LICENSE) for details.

---

## Commercial Support & Fact Packs

CertainLogic offers **verified fact packs** for specific industries:

| Pack | Price | Contents |
|------|-------|----------|
| **Coder Pack** | $39 | 158 coding facts (Python, JavaScript, APIs, frameworks) |
| **Industrial Pack** | $199 | 500+ industrial automation facts (PLC, L5X, IEC, ISO) |
| **Healthcare Pack** | $199 | 300+ medical coding, HIPAA, FDA regulation facts |
| **Finance Pack** | $199 | 400+ SOX, PCI, GAAP, SEC regulation facts |

We also provide **cache‑warming services** (pre‑warmed facts from your internal documents) and **compliance consulting** for regulated deployments.

**Contact:** [sales@certainlogic.ai](mailto:sales@certainlogic.ai) | [@CertainLogicAI](https://x.com/CertainLogicAI)

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Built with transparency, for trust.**