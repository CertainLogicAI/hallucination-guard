"""
Brain Wrapper — Production-Hardened Interface for CertainLogic Brain OS

Drop-in replacement for agent brain queries. Integrates:
- Intent classification with boosting
- Timeout + retry logic
- Circuit breaker for resilience
- Input validation (security)
- Log redaction (security)
- Content sanitization (security)
- Metrics collection (observability)
- Process pool management (anti fork-bomb)

Usage:
    from brain_wrapper import Brain

    brain = Brain()
    result = brain.query("what is our moat strategy")
    print(result["answer"])
    print(result["sources"])
"""

import concurrent.futures
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add company-brain to path
sys.path.insert(0, str(Path(__file__).parent))

from certainlogic_router import CertainLogicRouter, classify_intent
from src.core.circuit_breaker import CircuitBreaker
from src.core.error_classifier import classify_error
from src.core.cli_pool import get_cli_pool
from src.core.input_validator import validate_query, validate_limit
from src.core.log_redactor import redact_query
from src.core.content_sanitizer import sanitize_content
from src.core.metrics import record_query

try:
    from intent_cache import get_intent_cache
    from query_cache import get_query_cache
    _CACHE_AVAILABLE = True
except Exception:
    _CACHE_AVAILABLE = False


class Brain:
    """
    Production-hardened brain interface for CertainLogic skills.

    Features:
    - Automatic intent classification
    - Source boost routing
    - Circuit breaker protection
    - Input validation
    - Content sanitization
    - Structured logging
    - Graceful degradation
    """

    def __init__(self, domain: str = "default"):
        self._router = CertainLogicRouter()
        self._circuit = CircuitBreaker(failure_threshold=5, recovery_timeout=600.0, name="brain")
        self._pool = get_cli_pool()
        self.domain = domain

        # Caches (Phase 4F)
        if _CACHE_AVAILABLE:
            self._intent_cache = get_intent_cache()
            self._query_cache = get_query_cache()
        else:
            self._intent_cache = None
            self._query_cache = None

    def query(self, text: str, intent: Optional[str] = None,
              limit: int = 5, timeout: float = 2.0) -> Dict[str, Any]:
        """
        Execute a routed brain query with all safety layers.

        Args:
            text: The query text
            intent: Optional intent override (strategy|product|data|operations)
            limit: Max results (1-100, default 5)
            timeout: Query timeout in seconds (default 2s)

        Returns:
            {
                "query": str,
                "intent": str,
                "answer": str,
                "sources": list of {slug, title, score},
                "confidence": float,
                "brain_sourced": bool,
                "latency_ms": float,
                "error": str or None,
            }
        """
        start_time = time.time()
        redacted_query = redact_query(text)

        try:
            # 1. Input validation
            validate_query(text)
            limit = validate_limit(limit)

            # 2. Circuit breaker check
            if not self._circuit.should_allow():
                return self._empty_result(
                    text, intent or "unknown",
                    error="brain_unavailable",
                    latency_ms=self._elapsed_ms(start_time)
                )

            # 3. Classify intent
            detected_intent = intent or classify_intent(text)

            # 3c. Check intent cache if we auto-classified
            if not intent and self._intent_cache:
                cached_intent = self._intent_cache.get(text)
                if cached_intent:
                    detected_intent = cached_intent
                else:
                    self._intent_cache.put(text, detected_intent)

            # 3d. Check query result cache
            if self._query_cache:
                cached_result = self._query_cache.get(text, detail_level="medium", limit=limit)
                if cached_result is not None:
                    latency_ms = self._elapsed_ms(start_time)
                    record_query(
                        query=redacted_query,
                        intent=detected_intent,
                        confidence=cached_result.get("confidence", 0),
                        latency_ms=latency_ms,
                        hit=cached_result.get("brain_sourced", False),
                        error=None,
                        brain_sourced=cached_result.get("brain_sourced", False),
                    )
                    # Return a copy to prevent mutation of cached data
                    return dict(cached_result)

            # 4. Execute query with timeout
            try:
                # 4a. Store in query cache on success
                result = self._execute_query(text, detected_intent, limit, timeout)
                self._circuit.record_success()

                if self._query_cache:
                    self._query_cache.put(text, result, detail_level="medium", limit=limit)

                # 5. Record metrics
                latency_ms = self._elapsed_ms(start_time)
                hit = result.get("confidence", 0) > 0.2
                record_query(
                    query=redacted_query,
                    intent=detected_intent,
                    confidence=result.get("confidence", 0),
                    latency_ms=latency_ms,
                    hit=hit,
                    error=None,
                    brain_sourced=hit,
                )

                # 6. Sanitize content in answer
                if "answer" in result:
                    result["answer"] = sanitize_content(result["answer"])

                result["latency_ms"] = latency_ms
                return result

            except Exception as e:
                # Classify and handle error
                error_type = classify_error(e)
                if error_type == "TRANSIENT":
                    # Retry with backoff
                    result = self._retry_query(text, detected_intent, limit, timeout)
                    self._circuit.record_success()
                    latency_ms = self._elapsed_ms(start_time)
                    record_query(
                        query=redacted_query,
                        intent=detected_intent,
                        confidence=result.get("confidence", 0),
                        latency_ms=latency_ms,
                        hit=result.get("confidence", 0) > 0.2,
                        error=None,
                        brain_sourced=result.get("confidence", 0) > 0.2,
                    )
                    result["latency_ms"] = latency_ms
                    return result
                else:
                    # Permanent error, don't retry
                    self._circuit.record_failure()
                    latency_ms = self._elapsed_ms(start_time)
                    record_query(
                        query=redacted_query,
                        intent=detected_intent,
                        confidence=0,
                        latency_ms=latency_ms,
                        hit=False,
                        error=str(e),
                        brain_sourced=False,
                    )
                    return self._empty_result(text, detected_intent, error=str(e), latency_ms=latency_ms)

        except ValueError as e:
            # Input validation failure
            latency_ms = self._elapsed_ms(start_time)
            return self._empty_result(text, "unknown", error=str(e), latency_ms=latency_ms)
        except Exception as e:
            # Unexpected error
            latency_ms = self._elapsed_ms(start_time)
            self._circuit.record_failure()
            return self._empty_result(text, "unknown", error=str(e), latency_ms=latency_ms)

    def _execute_query(self, text: str, intent: str, limit: int,
                       timeout: float) -> Dict[str, Any]:
        """Execute a brain query via the router with timeout."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._router.query, text, limit=limit)
            try:
                result = future.result(timeout=timeout)
                return self._format_result(text, intent, result)
            except concurrent.futures.TimeoutError:
                raise TimeoutError(f"Brain query timed out after {timeout}s")

    def _retry_query(self, text: str, intent: str, limit: int,
                     timeout: float, max_retries: int = 3) -> Dict[str, Any]:
        """Retry a failed query with exponential backoff."""
        base_delay = 0.1
        for attempt in range(max_retries):
            delay = base_delay * (2 ** attempt)  # 0.1, 0.2, 0.4
            time.sleep(delay)
            try:
                return self._execute_query(text, intent, limit, timeout)
            except Exception:
                if attempt == max_retries - 1:
                    raise

    def _format_result(self, query: str, intent: str,
                       raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw router result into clean response."""
        sources = raw_result.get("results", [])

        if sources:
            top = sources[0]
            answer = top.get("excerpt", "") or top.get("title", "")
            confidence = top.get("score", 0)
        else:
            answer = "No relevant information found in the brain."
            confidence = 0

        return {
            "query": query,
            "intent": intent,
            "answer": answer,
            "sources": [
                {"slug": s["slug"], "title": s["title"], "score": s["score"]}
                for s in sources[:5]
            ],
            "confidence": confidence,
            "brain_sourced": confidence > 0.2,
            "source_attribution": raw_result.get("source_attribution", ""),
            "detail_level": raw_result.get("detail_level", "medium"),
            "brain_query": raw_result,
        }

    def _empty_result(self, query: str, intent: str,
                      error: Optional[str] = None, latency_ms: float = 0) -> Dict[str, Any]:
        """Return an empty result structure."""
        return {
            "query": query,
            "intent": intent,
            "answer": "Brain query failed. Falling back to legacy path.",
            "sources": [],
            "confidence": 0,
            "brain_sourced": False,
            "error": error,
            "latency_ms": latency_ms,
        }

    def _elapsed_ms(self, start: float) -> float:
        """Calculate elapsed time in milliseconds."""
        return round((time.time() - start) * 1000, 2)

    # --- Shorthand methods ---

    def strategy(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Query specifically for strategy/moat content."""
        return self.query(query, intent="strategy", limit=limit)

    def product(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Query specifically for product content."""
        return self.query(query, intent="product", limit=limit)

    def metrics(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Query specifically for metrics/evidence content."""
        return self.query(query, intent="data", limit=limit)

    def ops(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Query specifically for operations content."""
        return self.query(query, intent="operations", limit=limit)


# Convenience: export Brain class as default
__all__ = ["Brain"]
