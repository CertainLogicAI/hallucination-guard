"""CertainLogic MCP Server — FastMCP wrapper for the Brain API.

Production-grade MCP server with retry logic, batch queries, health checks,
and hallucination-guarded fact validation. Extensively tested and documented.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import time
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Load environment variables from .env file at module level
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

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

logging.basicConfig(level=os.getenv("MCP_LOG_LEVEL", "INFO"))
logger = logging.getLogger("certainlogic-mcp")

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class BrainAPIResult(BaseModel):
    """Structured output from a single Brain API query."""
    answer: str
    confident: bool
    method: str       # cache | facts | llm | uncertain | error


class GuardResult(BaseModel):
    """Result from the hallucination Guard (verify_fact)."""
    valid: Optional[bool]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    method: str       # filter | llm | uncertain


class BatchResultItem(BaseModel):
    """Individual result within a batch query response."""
    query: str
    answer: str
    confident: bool
    method: str


class BatchQueryResult(BaseModel):
    """Structured output from a batch Brain API query."""
    results: List[BatchResultItem]
    total: int
    confident: int
    uncertain: int
    errors: int


class HealthResult(BaseModel):
    """Result from the Brain API health check."""
    status: str       # ok | degraded | down
    components: dict = Field(default_factory=dict)
    latency_ms: int = 0


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "CertainLogic Brain API",
    instructions=(
        "Provides verified factual answers via the Brain API. "
        "Use brain_api_query for: API specs, language behavior, regulatory facts, "
        "technical constants. Returns 'uncertain' instead of guessing. "
        "Use batch_query for validating multiple facts at once. "
        "Use verify_fact_guard to check a claim against source text. "
        "Use health_check to verify Brain API availability."
    ),
)


# ---------------------------------------------------------------------------
# Tool: brain_api_query (single fact)
# ---------------------------------------------------------------------------

@mcp.tool()
async def brain_api_query(
    query: str,
    api_key: Optional[str] = None,
) -> BrainAPIResult:
    """Query verified factual knowledge base.

    Returns verified answer or uncertainty flag.
    Use for: API specs, language behavior, regulatory facts, technical constants.
    Do NOT use for: reasoning, code generation, subjective questions.
    """
    resolved_key = _resolve_api_key(api_key)
    if not resolved_key:
        return BrainAPIResult(
            answer="No API key provided. Set BRAIN_API_KEY env var.",
            confident=False,
            method="error",
        )

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
        return BrainAPIResult(
            answer=f"Brain API error: {exc}",
            confident=False,
            method="error",
        )
    finally:
        latency_ms = int((time.monotonic() - t_start) * 1000)
        logger.info(
            "[BRAIN_API] ts=%.3f query_hash=%s method=%s latency_ms=%d",
            time.time(),
            query_hash,
            method,
            latency_ms,
        )


# ---------------------------------------------------------------------------
# Tool: batch_query
# ---------------------------------------------------------------------------

@mcp.tool()
async def batch_query(
    queries: List[str],
    api_key: Optional[str] = None,
) -> BatchQueryResult:
    """Validate multiple facts in a single call.

    Each query is checked independently against the Brain API.
    Returns aggregated results with counts of confident/uncertain/errors.
    """
    resolved_key = _resolve_api_key(api_key)
    if not resolved_key:
        return BatchQueryResult(
            results=[],
            total=0,
            confident=0,
            uncertain=0,
            errors=1,
        )

    results = []
    confident_count = 0
    uncertain_count = 0
    error_count = 0

    for query in queries:
        try:
            result = await brain_api_query(query=query, api_key=resolved_key)
            results.append(BatchResultItem(
                query=query,
                answer=result.answer,
                confident=result.confident,
                method=result.method,
            ))
            if result.confident:
                confident_count += 1
            elif result.method == "uncertain":
                uncertain_count += 1
            elif result.method == "error":
                error_count += 1
            else:
                uncertain_count += 1
        except Exception as exc:
            logger.exception("Batch query item failed: query=%s", _hash_query(query))
            results.append(BatchResultItem(
                query=query,
                answer=f"Error: {exc}",
                confident=False,
                method="error",
            ))
            error_count += 1

    return BatchQueryResult(
        results=results,
        total=len(results),
        confident=confident_count,
        uncertain=uncertain_count,
        errors=error_count,
    )


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

    Use when you have a specific claim and the text it came from.
    Returns whether the claim is supported, contradicted, or unclear.
    Strictness: 0.7 (coder) | 0.8 (agent) | 0.9 (enterprise).
    """
    resolved_key = _resolve_api_key(api_key)
    if not resolved_key:
        return GuardResult(
            valid=None,
            confidence=0.0,
            reason="No API key provided. Set BRAIN_API_KEY env var.",
            method="error",
        )

    t_start = time.monotonic()
    try:
        result = await _call_brain_api_with_retry(
            resolved_key,
            query=claim,
            text=source_text,
            strictness=strictness,
        )
        latency_ms = int((time.monotonic() - t_start) * 1000)
        logger.info(
            "[GUARD] ts=%.3f claim_hash=%s method=%s latency_ms=%d",
            time.time(),
            _hash_query(claim),
            result.get("method", "unknown"),
            latency_ms,
        )
        return GuardResult(
            valid=result.get("valid"),
            confidence=result.get("confidence", 0.0),
            reason=result.get("reason", ""),
            method=result.get("method", "uncertain"),
        )
    except Exception as exc:
        logger.exception("Guard validation failed")
        return GuardResult(
            valid=None,
            confidence=0.0,
            reason=f"Guard error: {exc}",
            method="error",
        )


# ---------------------------------------------------------------------------
# Tool: health_check
# ---------------------------------------------------------------------------

@mcp.tool()
async def health_check() -> HealthResult:
    """Check if the Brain API is available and responsive."""
    t_start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(BRAIN_HEALTH_ENDPOINT)
            response.raise_for_status()
            data = response.json()
            latency_ms = int((time.monotonic() - t_start) * 1000)
            return HealthResult(
                status=data.get("status", "ok"),
                components=data.get("components", {}),
                latency_ms=latency_ms,
            )
    except httpx.HTTPStatusError as exc:
        latency_ms = int((time.monotonic() - t_start) * 1000)
        return HealthResult(
            status="degraded",
            components={"error": f"HTTP {exc.response.status_code}"},
            latency_ms=latency_ms,
        )
    except Exception as exc:
        latency_ms = int((time.monotonic() - t_start) * 1000)
        return HealthResult(
            status="down",
            components={"error": str(exc)},
            latency_ms=latency_ms,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_api_key(api_key: Optional[str]) -> str:
    """Resolve API key: parameter > env var > .env file."""
    return api_key or DEFAULT_API_KEY


def _hash_query(query: str) -> str:
    """Compute SHA-256 hash of query, first 8 hex chars."""
    return hashlib.sha256(query.encode()).hexdigest()[:8]


def _format_http_error(status_code: int) -> str:
    """Format human-readable error for HTTP status code."""
    if status_code == 401:
        return "Brain API error: Unauthorized (401). Check your API key."
    elif status_code == 429:
        return "Brain API error: Rate limited (429). Retry after a moment."
    elif 500 <= status_code < 600:
        return f"Brain API error: Server error ({status_code}). Retry later."
    else:
        return f"Brain API error: HTTP {status_code}"


async def _call_brain_api_with_retry(
    api_key: str,
    query: str,
    text: Optional[str] = None,
    strictness: Optional[float] = None,
) -> dict:
    """POST to Brain API with configurable retry and exponential backoff.

    Retries on 5xx server errors and transient network failures.
    Does NOT retry on 4xx client errors (bad request, unauthorized, etc.).
    """
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
                    headers={
                        "X-API-Key": api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            # Do not retry client errors (4xx)
            if 400 <= status < 500:
                raise
            # Retry server errors (5xx)
            last_exception = exc
            if attempt < MAX_RETRIES:
                sleep_s = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                sleep_s += random.uniform(0, RETRY_MAX_JITTER)
                logger.warning(
                    "Brain API %d on attempt %d/%d, retrying in %.2fs",
                    status, attempt, MAX_RETRIES, sleep_s,
                )
                await _async_sleep(sleep_s)
            continue

        except (httpx.ConnectError, httpx.ReadError, httpx.WriteError) as exc:
            last_exception = exc
            if attempt < MAX_RETRIES:
                sleep_s = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                sleep_s += random.uniform(0, RETRY_MAX_JITTER)
                logger.warning(
                    "Brain API network error on attempt %d/%d, retrying in %.2fs: %s",
                    attempt, MAX_RETRIES, sleep_s, exc,
                )
                await _async_sleep(sleep_s)
            continue

    # All retries exhausted
    if last_exception:
        raise last_exception
    raise RuntimeError("Unexpected: all retries exhausted with no exception")


async def _async_sleep(seconds: float) -> None:
    """Async sleep. Extracted for testability (patch target)."""
    await _import_asyncio().sleep(seconds)


def _import_asyncio():
    """Lazy import asyncio. Extracted for test patching."""
    import asyncio
    return asyncio


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the MCP server (stdio transport by default)."""
    mcp.run()
