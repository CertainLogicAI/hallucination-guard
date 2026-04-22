"""Comprehensive pytest suite for the CertainLogic MCP server.

All tests mock ``httpx.AsyncClient.post`` — no real Brain API calls are made.
Covers: single query, batch query, Guard, health check, retry logic,
telemetry, auth, and error handling.
"""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from certainlogic_mcp.server import (
    brain_api_query,
    batch_query,
    verify_fact_guard,
    health_check,
    BrainAPIResult,
    BatchQueryResult,
    GuardResult,
    HealthResult,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(data: dict, status_code: int = 200) -> MagicMock:
    """Build a mock httpx response object."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = data
    resp.raise_for_status = MagicMock()
    return resp


def _make_http_error(status_code: int) -> httpx.HTTPStatusError:
    """Build an HTTPStatusError with the given status code."""
    request = MagicMock()
    response = MagicMock()
    response.status_code = status_code
    return httpx.HTTPStatusError(
        f"HTTP {status_code}", request=request, response=response
    )


# ---------------------------------------------------------------------------
# Happy path — brain_api_query
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_successful_facts_query(mock_httpx_post):
    """Facts method should yield confident=True."""
    mock_httpx_post.return_value = _make_response(
        {"answer": "Python was created in 1991", "method": "facts"}
    )

    result = await brain_api_query("When was Python created?", api_key="test-key")

    assert isinstance(result, BrainAPIResult)
    assert result.answer == "Python was created in 1991"
    assert result.confident is True
    assert result.method == "facts"
    mock_httpx_post.assert_awaited_once()


@pytest.mark.asyncio
async def test_cache_hit(mock_httpx_post):
    """Cache method should yield confident=True."""
    mock_httpx_post.return_value = _make_response(
        {"answer": "Guido van Rossum", "method": "cache"}
    )

    result = await brain_api_query("Who created Python?", api_key="test-key")

    assert result.confident is True
    assert result.method == "cache"


@pytest.mark.asyncio
async def test_uncertain_response(mock_httpx_post):
    """Uncertain method should yield confident=False."""
    mock_httpx_post.return_value = _make_response(
        {"answer": "I'm not sure", "method": "uncertain"}
    )

    result = await brain_api_query("Will it rain tomorrow?", api_key="test-key")

    assert result.confident is False
    assert result.method == "uncertain"


@pytest.mark.asyncio
async def test_llm_method(mock_httpx_post):
    """LLM method should yield confident=True (answer exists)."""
    mock_httpx_post.return_value = _make_response(
        {"answer": "Paris", "method": "llm"}
    )

    result = await brain_api_query("Capital of France?", api_key="test-key")

    assert result.answer == "Paris"
    assert result.confident is True
    assert result.method == "llm"


# ---------------------------------------------------------------------------
# Auth / key resolution
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_missing_api_key(mock_httpx_post):
    """No param and no env key → error result, no HTTP call."""
    with patch("certainlogic_mcp.server.DEFAULT_API_KEY", ""):
        result = await brain_api_query("What is Python?")

    assert "No API key" in result.answer
    assert result.confident is False
    assert result.method == "error"
    mock_httpx_post.assert_not_awaited()


@pytest.mark.asyncio
async def test_api_key_param_overrides_env(mock_httpx_post):
    """Passed api_key parameter should win over the env var."""
    mock_httpx_post.return_value = _make_response(
        {"answer": "ok", "method": "facts"}
    )

    with patch("certainlogic_mcp.server.DEFAULT_API_KEY", "key1"):
        result = await brain_api_query("test query", api_key="key2")

    assert result.answer == "ok"
    call_kwargs = mock_httpx_post.call_args[1]
    assert call_kwargs["headers"]["X-API-Key"] == "key2"


@pytest.mark.asyncio
async def test_env_key_used_when_no_param(mock_httpx_post):
    """Env var key used when no parameter provided."""
    mock_httpx_post.return_value = _make_response(
        {"answer": "ok", "method": "facts"}
    )

    with patch("certainlogic_mcp.server.DEFAULT_API_KEY", "env-key"):
        result = await brain_api_query("test")

    assert result.method == "facts"
    call_kwargs = mock_httpx_post.call_args[1]
    assert call_kwargs["headers"]["X-API-Key"] == "env-key"


# ---------------------------------------------------------------------------
# HTTP / network errors
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_http_401(mock_httpx_post):
    """401 Unauthorized should surface in the error answer."""
    resp = _make_response({}, status_code=401)
    resp.raise_for_status.side_effect = _make_http_error(401)
    mock_httpx_post.return_value = resp

    result = await brain_api_query("test", api_key="test-key")

    assert result.confident is False
    assert result.method == "error"
    assert "401" in result.answer


@pytest.mark.asyncio
async def test_http_429(mock_httpx_post):
    """429 Rate limited should surface in the error answer."""
    resp = _make_response({}, status_code=429)
    resp.raise_for_status.side_effect = _make_http_error(429)
    mock_httpx_post.return_value = resp

    result = await brain_api_query("test", api_key="test-key")

    assert result.confident is False
    assert result.method == "error"
    assert "429" in result.answer


@pytest.mark.asyncio
async def test_http_500_without_retry(mock_httpx_post):
    """500 server error without retry config should return error."""
    resp = _make_response({}, status_code=500)
    resp.raise_for_status.side_effect = _make_http_error(500)
    mock_httpx_post.return_value = resp

    with patch("certainlogic_mcp.server.MAX_RETRIES", 1):
        result = await brain_api_query("test", api_key="test-key")

    assert result.confident is False
    assert result.method == "error"
    assert "500" in result.answer


@pytest.mark.asyncio
async def test_http_502_retry_exhausted(mock_httpx_post):
    """502 with retries exhausted — error returned."""
    resp = _make_response({}, status_code=502)
    resp.raise_for_status.side_effect = _make_http_error(502)
    mock_httpx_post.return_value = resp

    with patch("certainlogic_mcp.server.MAX_RETRIES", 2):
        with patch("certainlogic_mcp.server._async_sleep", new_callable=AsyncMock):
            result = await brain_api_query("test", api_key="test-key")

    assert result.confident is False
    assert result.method == "error"
    assert mock_httpx_post.call_count == 2


@pytest.mark.asyncio
async def test_retry_success_on_second_attempt(mock_httpx_post):
    """First call 503, second call 200 — should return success."""
    fail_resp = _make_response({}, status_code=503)
    fail_resp.raise_for_status.side_effect = _make_http_error(503)
    success_resp = _make_response(
        {"answer": "Recovered", "method": "facts"}, status_code=200
    )
    mock_httpx_post.side_effect = [fail_resp, success_resp]

    with patch("certainlogic_mcp.server._async_sleep", new_callable=AsyncMock):
        result = await brain_api_query("test", api_key="test-key")

    assert result.confident is True
    assert result.answer == "Recovered"
    assert mock_httpx_post.call_count == 2


@pytest.mark.asyncio
async def test_timeout(mock_httpx_post):
    """TimeoutException should produce a graceful timeout error."""
    mock_httpx_post.side_effect = httpx.TimeoutException("Request timed out")

    result = await brain_api_query("test", api_key="test-key")

    assert result.confident is False
    assert result.method == "error"
    assert "timeout" in result.answer.lower() or "timed out" in result.answer.lower()


@pytest.mark.asyncio
async def test_network_error(mock_httpx_post):
    """ConnectError should be caught gracefully."""
    mock_httpx_post.side_effect = httpx.ConnectError("Connection failed")

    result = await brain_api_query("test", api_key="test-key")

    assert result.confident is False
    assert result.method == "error"
    assert "Brain API error" in result.answer or "Connection failed" in result.answer


@pytest.mark.asyncio
async def test_read_error(mock_httpx_post):
    """ReadError should trigger retry or return error."""
    mock_httpx_post.side_effect = httpx.ReadError("Connection reset")

    with patch("certainlogic_mcp.server.MAX_RETRIES", 1):
        result = await brain_api_query("test", api_key="test-key")

    assert result.confident is False
    assert result.method == "error"


@pytest.mark.asyncio
async def test_unexpected_exception(mock_httpx_post):
    """Generic exception should produce error result."""
    mock_httpx_post.side_effect = RuntimeError("Something weird")

    result = await brain_api_query("test", api_key="test-key")

    assert result.confident is False
    assert result.method == "error"
    assert "Something weird" in result.answer


# ---------------------------------------------------------------------------
# Telemetry / logging
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_telemetry_logging(mock_httpx_post):
    """Logger.info must receive query_hash and method, never the raw query."""
    mock_httpx_post.return_value = _make_response(
        {"answer": "42", "method": "facts"}
    )

    raw_query = "What is the answer to everything?"

    with patch("certainlogic_mcp.server.logger") as mock_logger:
        result = await brain_api_query(raw_query, api_key="test-key")

    assert result.method == "facts"
    mock_logger.info.assert_called_once()

    call_args, _call_kwargs = mock_logger.info.call_args
    log_payload = " ".join(str(arg) for arg in call_args)

    assert "query_hash=" in log_payload
    # The raw query text must NOT appear anywhere in the logged arguments
    assert raw_query not in log_payload


@pytest.mark.asyncio
async def test_error_telemetry_logged(mock_httpx_post):
    """Error responses should also log telemetry with method=error."""
    mock_httpx_post.side_effect = httpx.ConnectError("dead")

    with patch("certainlogic_mcp.server.logger") as mock_logger:
        result = await brain_api_query("test", api_key="test-key")

    assert result.method == "error"
    mock_logger.info.assert_called_once()
    # call_args[0] is a tuple: (template, val1, val2, val3, val4)
    args_tuple = mock_logger.info.call_args[0]
    # The 'error' value should appear in the args
    assert "error" in [str(a) for a in args_tuple]


# ---------------------------------------------------------------------------
# Batch query
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_batch_query_all_confident(mock_httpx_post):
    """Batch query where all items return confident facts."""
    mock_httpx_post.side_effect = [
        _make_response({"answer": "Python", "method": "facts"}),
        _make_response({"answer": "JavaScript", "method": "facts"}),
        _make_response({"answer": "Rust", "method": "facts"}),
    ]

    result = await batch_query(
        queries=["Who created Python?", "Who created JS?", "Who created Rust?"],
        api_key="test-key",
    )

    assert isinstance(result, BatchQueryResult)
    assert result.total == 3
    assert result.confident == 3
    assert result.uncertain == 0
    assert result.errors == 0
    assert all(r.confident for r in result.results)


@pytest.mark.asyncio
async def test_batch_query_mixed_results(mock_httpx_post):
    """Batch query with confident, uncertain, and error results."""
    mock_httpx_post.side_effect = [
        _make_response({"answer": "Yes", "method": "facts"}),
        _make_response({"answer": "I don't know", "method": "uncertain"}),
        _make_response({}, status_code=500),
    ]
    # Third call needs error side_effect
    resp_err = _make_response({}, status_code=500)
    resp_err.raise_for_status.side_effect = _make_http_error(500)
    mock_httpx_post.side_effect = [
        _make_response({"answer": "Yes", "method": "facts"}),
        _make_response({"answer": "I don't know", "method": "uncertain"}),
        resp_err,
    ]

    with patch("certainlogic_mcp.server.MAX_RETRIES", 1):
        result = await batch_query(
            queries=["Q1", "Q2", "Q3"],
            api_key="test-key",
        )

    assert result.total == 3
    assert result.confident == 1
    assert result.uncertain == 1
    assert result.errors == 1


@pytest.mark.asyncio
async def test_batch_query_empty(mock_httpx_post):
    """Empty batch query should return empty results."""
    result = await batch_query(queries=[], api_key="test-key")

    assert result.total == 0
    assert result.confident == 0
    assert result.uncertain == 0
    assert result.errors == 0
    mock_httpx_post.assert_not_awaited()


@pytest.mark.asyncio
async def test_batch_query_missing_key(mock_httpx_post):
    """Batch query without API key should return error."""
    with patch("certainlogic_mcp.server.DEFAULT_API_KEY", ""):
        result = await batch_query(queries=["Q1", "Q2"])

    assert result.total == 0
    assert result.errors == 1
    mock_httpx_post.assert_not_awaited()


# ---------------------------------------------------------------------------
# Guard — verify_fact_guard
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_guard_valid(mock_httpx_post):
    """Guard should return valid=True when claim is supported."""
    mock_httpx_post.return_value = _make_response(
        {
            "valid": True,
            "confidence": 0.99,
            "reason": "Explicitly stated in source text",
            "method": "filter",
        }
    )

    result = await verify_fact_guard(
        claim="Python was created in 1991",
        source_text="Python was created in 1991 by Guido van Rossum.",
        api_key="test-key",
    )

    assert isinstance(result, GuardResult)
    assert result.valid is True
    assert result.confidence == 0.99
    assert result.method == "filter"


@pytest.mark.asyncio
async def test_guard_invalid(mock_httpx_post):
    """Guard should return valid=False when claim is contradicted."""
    mock_httpx_post.return_value = _make_response(
        {
            "valid": False,
            "confidence": 0.95,
            "reason": "Source says 1991, claim says 1989",
            "method": "filter",
        }
    )

    result = await verify_fact_guard(
        claim="Python was created in 1989",
        source_text="Python was created in 1991 by Guido van Rossum.",
        api_key="test-key",
    )

    assert result.valid is False
    assert result.confidence == 0.95
    assert "1989" in result.reason


@pytest.mark.asyncio
async def test_guard_uncertain(mock_httpx_post):
    """Guard should return valid=None when unclear."""
    mock_httpx_post.return_value = _make_response(
        {
            "valid": None,
            "confidence": 0.3,
            "reason": "Source text does not address this claim",
            "method": "uncertain",
        }
    )

    result = await verify_fact_guard(
        claim="Python 4.0 will release in 2027",
        source_text="Python was created in 1991.",
        api_key="test-key",
    )

    assert result.valid is None
    assert result.confidence == 0.3
    assert result.method == "uncertain"


@pytest.mark.asyncio
async def test_guard_missing_key(mock_httpx_post):
    """Guard without API key should return error."""
    with patch("certainlogic_mcp.server.DEFAULT_API_KEY", ""):
        result = await verify_fact_guard(
            claim="test",
            source_text="test source",
        )

    assert result.valid is None
    assert result.method == "error"
    assert "No API key" in result.reason
    mock_httpx_post.assert_not_awaited()


@pytest.mark.asyncio
async def test_guard_uses_validate_endpoint(mock_httpx_post):
    """Guard should POST to the validate endpoint, not query."""
    mock_httpx_post.return_value = _make_response(
        {"valid": True, "confidence": 0.9, "reason": "ok", "method": "filter"}
    )

    with patch("certainlogic_mcp.server.BRAIN_VALIDATE_ENDPOINT", "https://validate.example.com"):
        await verify_fact_guard(
            claim="test",
            source_text="source",
            api_key="test-key",
        )

    assert "validate.example.com" in mock_httpx_post.call_args[0][0]


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_check_ok(mock_httpx_get):
    """Healthy Brain API should return status=ok."""
    mock_httpx_get.return_value = _make_response(
        {"status": "ok", "components": {"db": "ok", "cache": "ok"}}
    )

    result = await health_check()

    assert isinstance(result, HealthResult)
    assert result.status == "ok"
    assert result.components == {"db": "ok", "cache": "ok"}
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_health_check_degraded(mock_httpx_get):
    """Degraded Brain API (non-2xx) should return status=degraded."""
    resp = _make_response({}, status_code=503)
    resp.raise_for_status.side_effect = _make_http_error(503)
    mock_httpx_get.return_value = resp

    result = await health_check()

    assert result.status == "degraded"
    assert "503" in result.components.get("error", "")


@pytest.mark.asyncio
async def test_health_check_down(mock_httpx_get):
    """Unreachable Brain API should return status=down."""
    mock_httpx_get.side_effect = httpx.ConnectError("Connection refused")

    result = await health_check()

    assert result.status == "down"
    assert "Connection refused" in result.components.get("error", "")


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_500_then_200(mock_httpx_post):
    """500 followed by 200: retry succeeds."""
    fail = _make_response({}, status_code=500)
    fail.raise_for_status.side_effect = _make_http_error(500)
    success = _make_response({"answer": "ok", "method": "facts"})

    mock_httpx_post.side_effect = [fail, success]

    with patch("certainlogic_mcp.server._async_sleep", new_callable=AsyncMock):
        result = await brain_api_query("test", api_key="test-key")

    assert result.confident is True
    assert mock_httpx_post.call_count == 2


@pytest.mark.asyncio
async def test_retry_connect_error_then_success(mock_httpx_post):
    """ConnectError followed by success: retry succeeds."""
    success = _make_response({"answer": "ok", "method": "facts"})
    mock_httpx_post.side_effect = [
        httpx.ConnectError("dead"),
        success,
    ]

    with patch("certainlogic_mcp.server._async_sleep", new_callable=AsyncMock):
        result = await brain_api_query("test", api_key="test-key")

    assert result.confident is True
    assert mock_httpx_post.call_count == 2


@pytest.mark.asyncio
async def test_no_retry_on_400(mock_httpx_post):
    """400 Bad Request should NOT be retried."""
    resp = _make_response({}, status_code=400)
    resp.raise_for_status.side_effect = _make_http_error(400)
    mock_httpx_post.return_value = resp

    result = await brain_api_query("test", api_key="test-key")

    assert result.confident is False
    assert mock_httpx_post.call_count == 1  # no retries


# ---------------------------------------------------------------------------
# Performance / latency
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_latency_logged(mock_httpx_post):
    """Latency should be logged and non-negative."""
    mock_httpx_post.return_value = _make_response(
        {"answer": "ok", "method": "facts"}
    )

    with patch("certainlogic_mcp.server.logger") as mock_logger:
        await brain_api_query("test", api_key="test-key")

    mock_logger.info.assert_called_once()
    # call_args[0] = (template, ts_val, hash_val, method_val, latency_val)
    args = mock_logger.info.call_args[0]
    assert len(args) == 5
    latency_ms = args[4]
    assert isinstance(latency_ms, int)
    assert latency_ms >= 0


@pytest.mark.asyncio
async def test_health_latency_logged(mock_httpx_get):
    """Health check latency should be non-negative."""
    mock_httpx_get.return_value = _make_response(
        {"status": "ok"}
    )

    result = await health_check()
    assert result.latency_ms >= 0
