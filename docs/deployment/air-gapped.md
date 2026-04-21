# Air-Gapped Deployment

CertainLogic Verifier is designed to run with **zero external dependencies** after initial setup.

## Setup

### 1. Build the Image on a Connected Machine

```bash
git clone https://github.com/CertainLogicAI/hallucination-guard.git
cd hallucination-guard
docker build -t hallucination-guard:latest .
docker save hallucination-guard:latest | gzip > hallucination-guard.tar.gz
```

### 2. Transfer to Air-Gapped Network

Copy `hallucination-guard.tar.gz` and your `facts_db.json` to the target environment via approved media.

### 3. Load and Run

```bash
docker load < hallucination-guard.tar.gz
docker run -d \
  -p 8000:8000 \
  -v ./facts_db.json:/app/facts_db.json:ro \
  -v guard-data:/app/data \
  --network none \
  hallucination-guard:latest
```

!!! note
    The `--network none` flag ensures the container cannot make any outbound network calls.

## Semantic Cache in Air-Gapped Mode

If using semantic cache, pre-download the sentence-transformers model:

```bash
# On connected machine
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
# Model cached at ~/.cache/huggingface/

# Copy the cache directory to air-gapped machine
tar czf hf-cache.tar.gz ~/.cache/huggingface/
# Transfer and extract on target
```

## Network Policy (Kubernetes)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hallucination-guard-deny-egress
spec:
  podSelector:
    matchLabels:
      app: hallucination-guard
  policyTypes:
    - Egress
  egress: []  # deny all outbound
```

## Verification

After deployment, confirm no external calls:

```bash
# Should work (internal)
curl http://localhost:8000/health

# Verify no DNS resolution from container
docker exec hallucination-guard nslookup google.com
# Should fail
```
