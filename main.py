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
from token_reduction_engine import reduce_tokens, get_metrics as get_token_metrics, clear_cache
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
    """Full pipeline: reduce → route → search → validate → hash → audit."""
    t0 = time.time()

    # 1. Token reduction
    token_result = reduce_tokens(req.query, force_deterministic=req.force_deterministic)

    reduced_query = token_result["reduced_query"]
    method = token_result["method"]

    # 2. Route
    ai_type, confidence, reasoning = router.route_query(reduced_query, req.context or {})

    # Override to deterministic if forced or cache hit
    if req.force_deterministic or method == "cache":
        ai_type = "deterministic"
        confidence = 1.0

    # 3. Execute — always check facts DB and memory search regardless of route
    results = None

    # 3a. Check facts DB for direct matches
    facts_results = _search_facts_db(reduced_query)
    if facts_results:
        method = "facts_cache"
        ai_type = "deterministic"
        confidence = 1.0
        results = facts_results
    else:
        # 3b. Search memory files
        search_results = search_memory(reduced_query, top_k=req.top_k)
        if search_results:
            method = "deterministic_search"
            results = search_results
        elif ai_type == "deterministic" or req.force_deterministic:
            method = "token_fallback"
            results = {
                "message": "No matching knowledge found in local corpus.",
                "reduced_query": reduced_query,
            }
        else:
            method = "external_placeholder"
            results = {
                "message": "No cache hit. Proceed with normal LLM reasoning.",
                "reduced_query": reduced_query,
            }

    # 4. Validate (only meaningful for deterministic results with text)
    validation_input = ""
    if isinstance(results, list) and results:
        validation_input = results[0].get("snippet", "")
    elif isinstance(results, dict):
        validation_input = results.get("message", "")

    validation = detector.validate(req.query, validation_input)

    # 5. Hash the full response for verification
    response_payload = {
        "query": req.query,
        "routing": ai_type,
        "method": method,
        "results": results,
    }
    response_hash = hashlib.sha256(
        json.dumps(response_payload, sort_keys=True, default=str).encode()
    ).hexdigest()

    # 6. Audit
    elapsed = time.time() - t0
    audit_id = hashlib.sha256(f"{req.query}:{t0}".encode()).hexdigest()[:16]
    _audit({
        "audit_id": audit_id,
        "query": req.query[:200],
        "routing": ai_type,
        "method": method,
        "confidence": confidence,
        "valid": validation["valid"],
        "response_hash": response_hash,
        "elapsed_ms": round(elapsed * 1000, 2),
    })

    return {
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
            "cache_hit": token_result["cache_hit"],
        },
        "validation": validation,
        "response_hash": response_hash,
        "audit_id": audit_id,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    """Process a query through the full deterministic AI pipeline."""
    return process_query(req)


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
