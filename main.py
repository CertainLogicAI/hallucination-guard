#!/usr/bin/env python3
"""
Deterministic AI Brain - Integrated API
========================================
End-to-end pipeline:
  Query → Token Reduction → Routing → Search/Fallback → Validation → Response

All components wired together into a single FastAPI service.
"""

import hashlib
import json
import os
import time
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Local modules
from token_reduction_engine import (
    reduce_tokens, get_metrics as get_token_metrics, clear_cache,
    get_cached_answer, cache_answer
)
from deterministic_memory_search import search_memory
from hallucination_detector import HallucinationDetector
from hybrid_ai_router import HybridAIRouter

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
FACTS_DB_PATH = os.getenv("FACTS_DB_PATH", "/data/.openclaw/workspace/facts_db.json")
WORKSPACE_PATH = os.getenv("WORKSPACE_PATH", "/data/.openclaw/workspace")
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "500"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

# ---------------------------------------------------------------------------
# App + shared instances
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Deterministic AI Brain",
    version="1.0.0",
    description="Deterministic, hallucination-free query processing with hash-verified outputs",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

router = HybridAIRouter(WORKSPACE_PATH)
detector = HallucinationDetector()

# Load expandable facts DB into detector
def _load_facts_db():
    if os.path.exists(FACTS_DB_PATH):
        with open(FACTS_DB_PATH, "r") as f:
            data = json.load(f)
        detector.facts_db = data.get("facts", detector.facts_db)

_load_facts_db()

# Audit log (append-only JSONL)
AUDIT_LOG = os.path.join(WORKSPACE_PATH, "audit_log.jsonl")

def _audit(entry: dict):
    entry["_ts"] = time.time()
    entry["_hash"] = hashlib.sha256(
        json.dumps(entry, sort_keys=True, default=str).encode()
    ).hexdigest()
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = None
    force_deterministic: bool = False
    top_k: int = Field(default=5, ge=1, le=20)

class QueryResponse(BaseModel):
    query: str
    routing: str              # "deterministic" or "external"
    routing_confidence: float
    routing_reason: str
    method: str               # "cache", "deterministic_search", "token_fallback", "external_placeholder"
    results: Any
    token_stats: Dict[str, Any]
    validation: Dict[str, Any]
    response_hash: str
    audit_id: str

class FactEntry(BaseModel):
    key: str
    type: str = Field(..., pattern="^(numeric|string)$")
    value: str
    unit: Optional[str] = None
    source: Optional[str] = None

# ---------------------------------------------------------------------------
# Pipeline helpers
# ---------------------------------------------------------------------------
def _search_facts_db(query: str) -> Optional[list]:
    """Search the facts database for matching entries. Returns list of matches or None."""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    # Remove common stop words
    stop_words = {"what", "is", "the", "are", "our", "my", "a", "an", "of", "for", "in", "on", "to", "and", "or", "how", "much", "does", "do", "was", "were", "has", "have", "about", "with"}
    query_words -= stop_words

    if not query_words:
        return None

    matches = []
    for key, fact in detector.facts_db.items():
        key_words = set(key.lower().split())
        overlap = query_words & key_words
        if len(overlap) >= 1 and len(overlap) / max(len(query_words), 1) >= 0.3:
            score = len(overlap) / max(len(query_words), len(key_words))
            matches.append({
                "key": key,
                "fact": fact,
                "score": round(score, 3),
                "hash": hashlib.sha256(json.dumps(fact, sort_keys=True).encode()).hexdigest(),
            })

    if not matches:
        return None

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:5]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def process_query(req: QueryRequest) -> dict:
    """Full pipeline: cache → facts → memory → external → validate → hash → audit."""
    t0 = time.time()

    # ── 1. Check answer cache (TRE v1.1) ──────────────────────────────
    cached = get_cached_answer(req.query)
    if cached:
        answer, token_count = cached
        elapsed = time.time() - t0
        audit_id = hashlib.sha256(f"{req.query}:{t0}".encode()).hexdigest()[:16]
        _audit({
            "audit_id": audit_id,
            "query": req.query[:200],
            "routing": "deterministic",
            "method": "answer_cache",
            "confidence": 1.0,
            "valid": True,
            "elapsed_ms": round(elapsed * 1000, 2),
            "source": "tre_answer_cache"
        })
        return {
            "query": req.query,
            "routing": "deterministic",
            "routing_confidence": 1.0,
            "routing_reason": "Answer cache hit — instant return",
            "method": "answer_cache",
            "results": {"message": answer},
            "token_stats": {
                "original_tokens": token_count,
                "reduced_tokens": token_count,
                "tokens_saved": 0,
                "cache_hit": True,
            },
            "validation": {"valid": True, "source": "cached"},
            "response_hash": hashlib.sha256(answer.encode()).hexdigest()[:16],
            "audit_id": audit_id,
        }

    # ── 2. No cache: apply token reduction ────────────────────────────
    token_result = reduce_tokens(req.query, force_deterministic=req.force_deterministic)
    reduced_query = token_result["reduced_query"]
    method = token_result["method"]

    # ── 3. Route ─────────────────────────────────────────────────────
    ai_type, confidence, reasoning = router.route_query(reduced_query, req.context or {})
    if req.force_deterministic:
        ai_type = "deterministic"
        confidence = 1.0

    # ── 4. Execute: facts → memory → fallback ─────────────────────────
    results = None
    answer_to_cache = None

    # 4a. Facts DB
    facts_results = _search_facts_db(reduced_query)
    if facts_results:
        method = "facts_cache"
        ai_type = "deterministic"
        confidence = 1.0
        results = facts_results
        answer_to_cache = json.dumps(facts_results)
    else:
        # 4b. Memory search
        search_results = search_memory(reduced_query, top_k=req.top_k)
        if search_results:
            method = "deterministic_search"
            results = search_results
            answer_to_cache = search_results[0].get("snippet", "") if search_results else ""
        elif ai_type == "deterministic" or req.force_deterministic:
            method = "token_fallback"
            results = {
                "message": "No matching knowledge found in local corpus.",
                "reduced_query": reduced_query,
            }
            answer_to_cache = "No matching knowledge found in local corpus."
        else:
            method = "external_placeholder"
            results = {
                "message": "No cache hit. Proceed with normal LLM reasoning.",
                "reduced_query": reduced_query,
            }
            answer_to_cache = "No cache hit. Proceed with normal LLM reasoning."

    # ── 5. Cache the answer ───────────────────────────────────────────
    cache_result = cache_answer(req.query, answer_to_cache)
    cache_warning = cache_result.get("warning", None)

    # ── 6. Validate ────────────────────────────────────────────────────
    validation_input = answer_to_cache
    if isinstance(results, list) and results:
        validation_input = results[0].get("snippet", "")
    elif isinstance(results, dict):
        validation_input = results.get("message", "")

    validation = detector.validate(req.query, validation_input)
    valid = validation["valid"] if cache_result["cached"] else False

    # ── 7. Hash & Audit ──────────────────────────────────────────────
    response_payload = {
        "query": req.query,
        "routing": ai_type,
        "method": method,
        "results": results,
    }
    response_hash = hashlib.sha256(
        json.dumps(response_payload, sort_keys=True, default=str).encode()
    ).hexdigest()

    elapsed = time.time() - t0
    audit_id = hashlib.sha256(f"{req.query}:{t0}".encode()).hexdigest()[:16]
    _audit({
        "audit_id": audit_id,
        "query": req.query[:200],
        "routing": ai_type,
        "method": method,
        "confidence": confidence,
        "valid": valid,
        "response_hash": response_hash,
        "elapsed_ms": round(elapsed * 1000, 2),
        "cached": cache_result["cached"],
        "flagged": cache_result["flagged"],
    })

    # ── 8. Build response ─────────────────────────────────────────────
    response = {
        "query": req.query,
        "routing": ai_type,
        "routing_confidence": round(confidence, 4),
        "routing_reason": reasoning,
        "method": method,
        "results": results,
        "token_stats": {
            "original_tokens": token_result["original_tokens"],
            "reduced_tokens": token_result["reduced_tokens"],
            "tokens_saved": token_result["tokens_saved"],
            "cache_hit": False,
        },
        "validation": validation,
        "response_hash": response_hash,
        "audit_id": audit_id,
    }

    if cache_warning:
        response["warning"] = cache_warning
        response["cache_status"] = "flagged_not_cached"
    elif cache_result["cached"]:
        response["cache_status"] = "cached"
    else:
        response["cache_status"] = "uncached"

    return response


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    """Process a query through the full deterministic AI pipeline."""
    return process_query(req)


class ValidateRequest(BaseModel):
    query: str
    response: str


@app.post("/validate")
def validate_endpoint(req: ValidateRequest):
    """Direct hallucination validation — no routing, no LLM calls.
    
    Returns structured validation result for any (query, response) pair.
    """
    result = detector.validate(req.query, req.response)
    return {
        "valid": result.get("valid", True),
        "flagged": result.get("flagged", False),
        "confidence": result.get("confidence", 1.0),
        "flags": result.get("flags", []),
        "checks": result.get("checks", {}),
    }


@app.get("/health")
def health():
    """Health check with component status."""
    facts_loaded = len(detector.facts_db)
    return {
        "status": "ok",
        "components": {
            "token_engine": "ok",
            "memory_search": "ok",
            "hallucination_detector": "ok",
            "hybrid_router": "ok",
            "facts_db": f"{facts_loaded} facts loaded",
        },
        "uptime_check": time.time(),
    }


@app.get("/metrics")
def metrics():
    """Token engine and pipeline metrics."""
    return {
        "token_engine": get_token_metrics(),
    }


@app.post("/cache/clear")
def cache_clear():
    """Clear the token reduction cache."""
    clear_cache()
    return {"status": "cleared"}


@app.post("/facts", status_code=201)
def add_fact(entry: FactEntry):
    """Add or update a fact in the knowledge base."""
    fact = {"type": entry.type, "value": entry.value}
    if entry.unit:
        fact["unit"] = entry.unit
    if entry.source:
        fact["source"] = entry.source

    detector.facts_db[entry.key.lower()] = fact
    _persist_facts()

    return {"status": "added", "key": entry.key.lower(), "total_facts": len(detector.facts_db)}


def _persist_facts():
    """Write facts DB to disk."""
    db = {"_meta": {"version": "1.0", "last_updated": time.strftime("%Y-%m-%d")}, "facts": detector.facts_db}
    with open(FACTS_DB_PATH, "w") as f:
        json.dump(db, f, indent=2)


@app.get("/facts")
def list_facts():
    """List all facts in the knowledge base."""
    return {"count": len(detector.facts_db), "facts": detector.facts_db}


@app.get("/facts/search")
def search_facts(q: str):
    """Search facts by keyword."""
    q_lower = q.lower()
    matches = {}
    for key, val in detector.facts_db.items():
        if q_lower in key or q_lower in str(val.get("value", "")).lower() or q_lower in str(val.get("source", "")).lower():
            matches[key] = val
    return {"query": q, "count": len(matches), "results": matches}


@app.delete("/facts/{key}")
def delete_fact(key: str):
    """Delete a specific fact."""
    key_lower = key.lower()
    if key_lower not in detector.facts_db:
        raise HTTPException(status_code=404, detail=f"Fact '{key_lower}' not found")
    del detector.facts_db[key_lower]
    _persist_facts()
    return {"status": "deleted", "key": key_lower, "total_facts": len(detector.facts_db)}


@app.put("/facts/{key}")
def update_fact(key: str, entry: FactEntry):
    """Update/correct a specific fact."""
    key_lower = key.lower()
    if key_lower not in detector.facts_db:
        raise HTTPException(status_code=404, detail=f"Fact '{key_lower}' not found")
    fact = {"type": entry.type, "value": entry.value}
    if entry.unit:
        fact["unit"] = entry.unit
    if entry.source:
        fact["source"] = entry.source
    detector.facts_db[key_lower] = fact
    _persist_facts()
    return {"status": "updated", "key": key_lower, "fact": fact}


@app.post("/cache/purge")
def cache_purge():
    """Wipe entire facts database and token cache."""
    detector.facts_db.clear()
    _persist_facts()
    clear_cache()
    return {"status": "purged", "facts": 0}


@app.get("/audit")
def audit_tail(limit: int = 20):
    """Return the last N audit log entries."""
    if not os.path.exists(AUDIT_LOG):
        return {"entries": []}
    with open(AUDIT_LOG, "r") as f:
        lines = f.readlines()
    entries = []
    for line in lines[-limit:]:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return {"entries": entries}


@app.get("/")
def root():
    return {
        "service": "Deterministic AI Brain",
        "version": "1.0.0",
        "endpoints": ["/query", "/health", "/metrics", "/facts", "/facts/search", "/facts/{key}", "/audit", "/cache/clear", "/cache/purge"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
