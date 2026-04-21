# Quick Start

Get CertainLogic Verifier running in 2 minutes.

## 1. Clone & Install

```bash
git clone https://github.com/CertainLogicAI/hallucination-guard.git
cd hallucination-guard
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Start the Service

```bash
export FACTS_DB_PATH=./facts_db.json
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 3. Validate a Response

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 2+2?", "response": "The answer is 5."}'
```

Response:

```json
{
  "valid": false,
  "confidence": 0.5,
  "severity": "medium",
  "flags": ["Factual mismatch detected"]
}
```

## 4. Test Token Reduction

```bash
curl -X POST http://localhost:8000/reduce \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain quantum entanglement in simple terms", "semantic": true}'
```

On a cache hit, you get the answer with **zero LLM tokens spent**.

## 5. Check Health

```bash
curl http://localhost:8000/health
# {"status": "ok", "components": {...}}
```

## Next Steps

- [Full installation options](installation.md) (pip, Docker, Helm)
- [Configuration reference](configuration.md)
- [API endpoints](../api/endpoints.md)
