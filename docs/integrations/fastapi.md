# FastAPI Middleware

Use CertainLogic Verifier as middleware in your existing FastAPI application.

## Basic Middleware

```python
from fastapi import FastAPI, Request
import httpx

app = FastAPI()
GUARD_URL = "http://localhost:8000"

@app.middleware("http")
async def verify_ai_output(request: Request, call_next):
    response = await call_next(request)

    # Only validate AI-generated endpoints
    if request.url.path.startswith("/ai/"):
        body = await response.body()
        async with httpx.AsyncClient() as client:
            validation = await client.post(
                f"{GUARD_URL}/validate",
                json={
                    "query": request.query_params.get("q", ""),
                    "response": body.decode()
                }
            )
            result = validation.json()
            if not result["valid"]:
                # Log, block, or flag the response
                logger.warning(f"Hallucination detected: {result['flags']}")

    return response
```

## Sidecar Pattern

Run CertainLogic Verifier as a sidecar container alongside your API:

```yaml
# docker-compose.yml
services:
  your-api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - GUARD_URL=http://guard:8000

  guard:
    image: ghcr.io/certainlogicai/hallucination-guard:latest
    volumes:
      - ./facts_db.json:/app/facts_db.json:ro
```

Your API calls `http://guard:8000/validate` before returning AI-generated responses to users.
