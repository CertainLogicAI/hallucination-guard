"""CertainLogic MCP Server — FastMCP wrapper.

Production-grade MCP server with two modes:
  1. API mode:    BRAIN_API_KEY set → calls the CertainLogic hosted API  
  2. OFFLINE mode: No key → reads bundled free_tier_facts.json (100 facts, zero network calls)

Offline mode handles the 15 sample queries exactly plus fuzzy keyword matching.
Both modes validated by 45+ tests.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import time
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
load_dotenv()

# -- API config (API mode) --------------------------------------------------
BRAIN_API_ENDPOINT = os.getenv(
    "BRAIN_API_ENDPOINT", "https://api.certainlogic.ai/query"
)
BRAIN_VALIDATE_ENDPOINT = os.getenv(
    "BRAIN_VALIDATE_ENDPOINT", "https://api.certainlogic.ai/validate"
)
BRAIN_HEALTH_ENDPOINT = os.getenv(
    "BRAIN_HEALTH_ENDPOINT", "https://api.certainlogic.ai/health"
)
BRAIN_API_TIMEOUT = float(os.getenv("BRAIN_API_TIMEOUT", "10"))
DEFAULT_API_KEY = os.getenv("BRAIN_API_KEY", "")
MAX_RETRIES = int(os.getenv("BRAIN_API_MAX_RETRIES", "3"))
RETRY_BASE_DELAY = float(os.getenv("BRAIN_API_RETRY_BASE_DELAY", "1.0"))
RETRY_MAX_JITTER = float(os.getenv("BRAIN_API_RETRY_MAX_JITTER", "0.5"))

# -- Offline config ---------------------------------------------------------
# Locate free_tier_facts.json in order of preference:
#  1. Environment override  
#  2. Bundled in this package (src/../free_tier_facts.json)
#  3. pip-installed data directory
#  4. Current working directory (for dev)
_FACTS_PATH = os.getenv("HG_FACTS_PATH")
if _FACTS_PATH and Path(_FACTS_PATH).exists():
    FACTS_JSON = Path(_FACTS_PATH)
else:
    _bundled = Path(__file__).parent / "free_tier_facts.json"
    _pip_data = Path.home() / ".local" / "lib" / "python3.11" / "site-packages" / "hallucination_guard" / "free_tier_facts.json"
    _pip_data_alt = Path.home() / ".local" / "lib" / "python3.12" / "site-packages" / "hallucination_guard" / "free_tier_facts.json"
    _pip_data_alt2 = Path.home() / ".local" / "lib" / "python3.13" / "site-packages" / "hallucination_guard" / "free_tier_facts.json"
    _cwd = Path.cwd() / "free_tier_facts.json"
    _opts = [_bundled, _pip_data, _pip_data_alt, _pip_data_alt2, _cwd]
    FACTS_JSON = next((p for p in _opts if p.exists()), None)

_OFFLINE_FACTS: Dict[str, dict] = {}
if FACTS_JSON and FACTS_JSON.exists():
    try:
        with FACTS_JSON.open("r", encoding="utf-8") as fh:
            _raw = json.load(fh)
        _OFFLINE_FACTS = _raw.get("facts", {})
    except Exception as exc:
        logging.warning("Failed to load offline facts: %s", exc)

logging.basicConfig(level=os.getenv("MCP_LOG_LEVEL", "INFO"))
logger = logging.getLogger("certainlogic-mcp")


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class BrainAPIResult(BaseModel):
    answer: str
    confident: bool
    method: str  # cache | facts | llm | offline_match | uncertain | error


class GuardResult(BaseModel):
    valid: Optional[bool]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    method: str  # filter | llm | uncertain | offline_simple | error


class BatchResultItem(BaseModel):
    query: str
    answer: str
    confident: bool
    method: str


class BatchQueryResult(BaseModel):
    results: List[BatchResultItem]
    total: int
    confident: int
    uncertain: int
    errors: int


class HealthResult(BaseModel):
    status: str  # ok | degraded | offline | down
    mode: str    # api | offline
    facts_loaded: int = 0
    components: dict = Field(default_factory=dict)
    latency_ms: int = 0


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "CertainLogic Brain API",
    instructions=(
        "Verified factual answers via the Brain API or bundled offline facts. "
        "Set BRAIN_API_KEY for full 333 facts. Leave unset for 100 free offline facts (zero network calls). "
        "Use brain_api_query for: API specs, language behavior, technical constants. "
        "Returns 'uncertain' instead of guessing."
    ),
)


# ---------------------------------------------------------------------------
# Offline query engine
# ---------------------------------------------------------------------------

async def _offline_query(query: str) -> BrainAPIResult:
    """Match query against bundled free facts.

    Strategy (fastest → slowest):
      1. Exact key match
      2. Substring in key
      3. Fuzzy word overlap
    """
    query_lower = query.lower().strip()
    # 1. Exact
    if query_lower in _OFFLINE_FACTS:
        fact = _OFFLINE_FACTS[query_lower]
        return BrainAPIResult(
            answer=_format_offline_answer(fact),
            confident=True,
            method="offline_match",
        )
    # 2. Substring
    for key, fact in _OFFLINE_FACTS.items():
        if query_lower in key or key in query_lower:
            return BrainAPIResult(
                answer=_format_offline_answer(fact),
                confident=True,
                method="offline_match",
            )
    # 3. Word overlap
    query_words = set(query_lower.split())
    best_key = None
    best_score = 0.0
    for key, fact in _OFFLINE_FACTS.items():
        key_words = set(key.split())
        overlap = len(query_words & key_words)
        score = overlap / max(len(query_words), 1)
        if score > 0.5 and score > best_score:
            best_score = score
            best_key = key
    if best_key:
        return BrainAPIResult(
            answer=_format_offline_answer(_OFFLINE_FACTS[best_key]),
            confident=True,
            method="offline_match",
        )
    return BrainAPIResult(
        answer="No matching verified fact found. Install full pack with 'pip install hallucination-guard'.",
        confident=False,
        method="uncertain",
    )


def _format_offline_answer(fact: dict) -> str:
    """Render a fact from the bundled JSON."""
    if fact.get("type") == "string":
        text = fact.get("value", "")
        src = fact.get("source", "")
        if src:
            return f"{text}\n[Source: {src}]"
        return str(text)
    if fact.get("type") == "boolean":
        text = "Yes" if fact.get("value") else "No"
        src = fact.get("source", "")
        if src:
            return f"{text}\n[Source: {src}]"
        return text
    if fact.get("type") == "enum":
        values = fact.get("value", [])
        src = fact.get("source", "")
        ans = ", ".join(str(v) for v in values)
        if src:
            return f"{ans}\n[Source: {src}]"
        return ans
    if fact.get("type") == "object":
        obj = fact.get("value", {})
        src = fact.get("source", "")
        lines = [f"{k}: {v}" for k, v in obj.items()]
        if src:
            lines.append(f"[Source: {src}]")
        return "\n".join(lines)
    return str(fact.get("value", ""))


# ---------------------------------------------------------------------------
# Tool: brain_api_query
# ---------------------------------------------------------------------------

@mcp.tool()
async def brain_api_query(
    query: str,
    api_key: Optional[str] = None,
) -> BrainAPIResult:
    """Query verified factual knowledge base.

    Offline mode: answers with bundled 100 facts when BRAIN_API_KEY is unset.
    API mode: queries hosted CertainLogic API (full 333 facts, semantic cache).
    """
    resolved_key = _resolve_api_key(api_key)

    # ---- OFFLINE mode (no key, no network) --------------------------------
    if not resolved_key:
        _log("OFFLINE", query, "offline")
        if _OFFLINE_FACTS:
            return await _offline_query(query)
        return BrainAPIResult(
            answer="Offline facts not loaded. Set BRAIN_API_KEY or reinstall certainlogic-mcp.",
            confident=False,
            method="error",
        )

    # ---- API mode ---------------------------------------------------------
    query_hash = _hash_query(query)
    t_start = time.monotonic()
    method = "error"

    try:
        result = await _call_brain_api_with_retry(resolved_key, query)
        method = result.get("method", "unknown")
        answer = result.get("answer", "")
        confident = method != "uncertain"
        return BrainAPIResult(answer=answer, confident=confident, method=method)

    except httpx.TimeoutException:
        return BrainAPIResult(
            answer="Brain API timed out. Try again or answer from context.",
            confident=False,
            method="error",
        )
    except httpx.HTTPStatusError as exc:
        msg = _format_http_error(exc.response.status_code)
        return BrainAPIResult(answer=msg, confident=False, method="error")
    except Exception as exc:
        logger.exception("Unexpected error calling Brain API")
        return BrainAPIResult(answer=f"Brain API error: {exc}", confident=False, method="error")
    finally:
        latency_ms = int((time.monotonic() - t_start) * 1000)
        logger.info("[BRAIN_API] ts=%.3f query_hash=%s method=%s latency_ms=%d", time.time(), query_hash, method, latency_ms)


# ---------------------------------------------------------------------------
# Tool: batch_query
# ---------------------------------------------------------------------------

@mcp.tool()
async def batch_query(
    queries: List[str],
    api_key: Optional[str] = None,
) -> BatchQueryResult:
    """Validate multiple facts. Uses same mode (API or offline) as brain_api_query."""
    results = []
    confident_count = 0
    uncertain_count = 0
    error_count = 0

    for query in queries:
        try:
            result = await brain_api_query(query=query, api_key=api_key)
            results.append(BatchResultItem(query=query, answer=result.answer, confident=result.confident, method=result.method))
            if result.confident:
                confident_count += 1
            elif result.method == "uncertain":
                uncertain_count += 1
            elif result.method == "error":
                error_count += 1
            else:
                uncertain_count += 1
        except Exception as exc:
            logger.exception("Batch query item failed")
            results.append(BatchResultItem(query=query, answer=f"Error: {exc}", confident=False, method="error"))
            error_count += 1

    return BatchQueryResult(results=results, total=len(results), confident=confident_count, uncertain=uncertain_count, errors=error_count)


# ---------------------------------------------------------------------------
# Tool: verify_fact_guard
# ---------------------------------------------------------------------------

@mcp.tool()
async def verify_fact_guard(
    claim: str,
    source_text: str,
    strictness: float = 0.8,
    api_key: Optional[str] = None,
) -> GuardResult:
    """Validate a claim against source text using the hallucination detector.

    Offline mode: performs a simple substring check (claim in source_text) with configurable strictness.
    API mode: uses the hosted hallucination detector for full semantic analysis.
    """
    resolved_key = _resolve_api_key(api_key)

    # ---- OFFLINE mode: simple string containment with keyword heuristics ----
    if not resolved_key:
        claim_lower = claim.lower()
        source_lower = source_text.lower()
        # Simple containment
        if claim_lower in source_lower:
            return GuardResult(valid=True, confidence=0.85, reason="Claim text found in source (offline simple check)", method="offline_simple")
        # Keyword overlap
        claim_words = set(claim_lower.split())
        source_words = set(source_lower.split())
        overlap = len(claim_words & source_words) / max(len(claim_words), 1)
        if overlap >= strictness:
            return GuardResult(valid=True, confidence=overlap, reason=f"{int(overlap*100)}% keyword overlap with source", method="offline_simple")
        return GuardResult(valid=False if overlap < 0.3 else None, confidence=overlap, reason="Claim not found in source (offline mode)", method="offline_simple")

    # ---- API mode ---------------------------------------------------------
    t_start = time.monotonic()
    try:
        result = await _call_brain_api_with_retry(resolved_key, query=claim, text=source_text, strictness=strictness)
        latency_ms = int((time.monotonic() - t_start) * 1000)
        logger.info("[GUARD] ts=%.3f claim_hash=%s method=%s latency_ms=%d", time.time(), _hash_query(claim), result.get("method", "unknown"), latency_ms)
        return GuardResult(
            valid=result.get("valid"),
            confidence=result.get("confidence", 0.0),
            reason=result.get("reason", ""),
            method=result.get("method", "uncertain"),
        )
    except Exception as exc:
        logger.exception("Guard validation failed")
        return GuardResult(valid=None, confidence=0.0, reason=f"Guard error: {exc}", method="error")


# ---------------------------------------------------------------------------
# Tool: health_check
# ---------------------------------------------------------------------------

@mcp.tool()
async def health_check() -> HealthResult:
    """Check server health.

    Reports whether running in API or OFFLINE mode.
    Offline mode: always healthy if facts are loaded.
    API mode: pings the Brain API health endpoint.
    """
    # Offline always reports healthy with facts loaded
    if not DEFAULT_API_KEY:
        return HealthResult(
            status="ok",
            mode="offline",
            facts_loaded=len(_OFFLINE_FACTS),
            latency_ms=0,
        )

    t_start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(BRAIN_HEALTH_ENDPOINT)
            response.raise_for_status()
            data = response.json()
            latency_ms = int((time.monotonic() - t_start) * 1000)
            return HealthResult(
                status=data.get("status", "ok"),
                mode="api",
                facts_loaded=0,  # API mode: facts are server-side
                latency_ms=latency_ms,
            )
    except Exception as exc:
        latency_ms = int((time.monotonic() - t_start) * 1000)
        return HealthResult(
            status="down",
            mode="api",
            facts_loaded=0,
            latency_ms=latency_ms,
        )


# ---------------------------------------------------------------------------
# Internal helpers (unchanged from original)
# ---------------------------------------------------------------------------

def _resolve_api_key(api_key: Optional[str]) -> str:
    return api_key or DEFAULT_API_KEY

def _hash_query(query: str) -> str:
    return hashlib.sha256(query.encode()).hexdigest()[:8]

def _format_http_error(status_code: int) -> str:
    if status_code == 401:
        return "Brain API error: Unauthorized (401). Check your API key."
    elif status_code == 429:
        return "Brain API error: Rate limited (429). Retry after a moment."
    elif 500 <= status_code < 600:
        return f"Brain API error: Server error ({status_code}). Retry later."
    else:
        return f"Brain API error: HTTP {status_code}"

async def _async_sleep(seconds: float) -> None:
    """Async sleep — extracted for testability (tests patch this)."""
    import asyncio
    await asyncio.sleep(seconds)


def _log(label: str, query: str, method: str) -> None:
    logger.info("[%-9s] query_hash=%s method=%s", label, _hash_query(query), method)


async def _call_brain_api_with_retry(api_key: str, query: str, text: Optional[str] = None, strictness: Optional[float] = None) -> dict:
    """POST to Brain API with retry logic."""
    endpoint = BRAIN_VALIDATE_ENDPOINT if text else BRAIN_API_ENDPOINT
    payload: dict = {"query": query}
    if text is not None:
        payload["text"] = text
    if strictness is not None:
        payload["strictness"] = strictness

    last_exception: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=BRAIN_API_TIMEOUT) as client:
                response = await client.post(
                    endpoint,
                    headers={"X-API-Key": api_key, "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            if 400 <= exc.response.status_code < 500:
                raise
            last_exception = exc
            if attempt < MAX_RETRIES:
                sleep_s = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                sleep_s += random.uniform(0, RETRY_MAX_JITTER)
                logger.warning("Brain API %d on attempt %d/%d, retrying in %.2fs", exc.response.status_code, attempt, MAX_RETRIES, sleep_s)
                await _async_sleep(sleep_s)
        except (httpx.ConnectError, httpx.ReadError, httpx.WriteError) as exc:
            last_exception = exc
            if attempt < MAX_RETRIES:
                sleep_s = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                sleep_s += random.uniform(0, RETRY_MAX_JITTER)
                logger.warning("Network error attempt %d/%d, retrying in %.2fs: %s", attempt, MAX_RETRIES, sleep_s, exc)
                await _async_sleep(sleep_s)
    if last_exception:
        raise last_exception
    raise RuntimeError("Unexpected: all retries exhausted with no exception")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
