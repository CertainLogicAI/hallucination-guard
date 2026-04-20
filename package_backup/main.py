#!/usr/bin/env python3
"""
CertainLogic Verifier - FastAPI Service
Integrated hallucination detection, token reduction, semantic caching, and deterministic search.
MIT License
"""

import os
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from hallucination_guard.hallucination_detector import HallucinationDetector
from hallucination_guard.token_reduction_engine import reduce_tokens, get_metrics, clear_cache
from hallucination_guard.deterministic_memory_search import search_memory
from hallucination_guard.intent_router import IntentRouter

# Configuration
FACTS_DB_PATH = os.getenv("FACTS_DB_PATH", "./facts_db.json")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize core components
try:
    detector = HallucinationDetector(facts_db_path=FACTS_DB_PATH)
except Exception as e:
    logger.warning(f"Could not load facts database: {e}")
    detector = HallucinationDetector()  # fallback to hardcoded facts

router = IntentRouter()

# FastAPI app
app = FastAPI(
    title="CertainLogic Verifier",
    description="Open‑source middleware for deterministic AI verification.",
    version="1.0.0",
)


# Pydantic models
class ValidateRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    response: str = Field(..., min_length=1, max_length=10000)


class ReduceRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    force_deterministic: bool = False
    semantic: bool = True


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: Optional[int] = 5


# API endpoints
@app.get("/health")
def health():
    return {"status": "ok", "service": "certainlogic-verifier"}


@app.get("/metrics")
def metrics():
    return get_metrics()


@app.post("/validate")
def validate(data: ValidateRequest):
    """Validate a (query, response) pair for factual consistency."""
    result = detector.validate(data.query, data.response)
    return result


@app.post("/reduce")
def reduce(data: ReduceRequest):
    """Reduce token count of a query."""
    result = reduce_tokens(
        data.query,
        force_deterministic=data.force_deterministic,
        semantic=data.semantic,
    )
    return result


@app.post("/search")
def search(data: SearchRequest):
    """Search local memory files for a query (deterministic TF‑IDF)."""
    results = search_memory(data.query, top_k=data.top_k)
    return {"query": data.query, "results": results}


@app.post("/route")
def route(query: str):
    """Route a query through token reduction and intent classification."""
    return router.route(query)


@app.delete("/cache")
def delete_cache():
    """Clear the token‑reduction cache."""
    clear_cache()
    return {"cleared": True}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)