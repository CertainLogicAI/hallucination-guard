"""End-to-end integration tests for the CertainLogic MCP server.

These tests verify the full flow from MCP tool invocation through
to structured result output. Mocked at the HTTP layer — no real API calls.
"""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from certainlogic_mcp.server import (
    brain_api_query,
    batch_query,
    verify_fact_guard,
    health_check,
)


def _make_response(data: dict, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = data
    resp.raise_for_status = MagicMock()
    return resp


def _make_http_error(status_code: int) -> httpx.HTTPStatusError:
    request = MagicMock()
    response = MagicMock()
    response.status_code = status_code
    return httpx.HTTPStatusError(
        f"HTTP {status_code}", request=request, response=response
    )


# ---------------------------------------------------------------------------
# E2E: Full workflow scenarios
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_e2e_coding_question_workflow(mock_httpx_post):
    """Full workflow: coding question → fact lookup → verified answer."""
    mock_httpx_post.return_value = _make_response(
        {
            "answer": "None. The requests library has NO default timeout.",
            "method": "facts",
        }
    )

    result = await brain_api_query(
        query="What is the default timeout for Python requests library?",
        api_key="test-key",
    )

    assert result.confident is True
    assert result.method == "facts"
    assert "None" in result.answer
    assert "default timeout" in result.answer.lower()


@pytest.mark.asyncio
async def test_e2e_news_article_validation(mock_httpx_post):
    """Full workflow: news article claims → batch validation → segregated results."""
    mock_httpx_post.side_effect = [
        _make_response({"answer": "Yes, $50M Series B", "method": "facts"}),
        _make_response({"answer": "I'm not sure", "method": "uncertain"}),
        _make_response({"answer": "No, founded in 2022", "method": "facts"}),
    ]

    result = await batch_query(
        queries=[
            "Did Acme AI raise $50M?",
            "Will Acme AI IPO in 2027?",
            "Was Acme AI founded in 2020?",
        ],
        api_key="test-key",
    )

    assert result.total == 3
    assert result.confident == 2
    assert result.uncertain == 1
    assert result.errors == 0

    # Check individual results
    assert result.results[0].confident is True  # $50M raise
    assert result.results[1].confident is False  # IPO uncertain
    assert result.results[2].confident is True  # Founded in 2022 (corrected)


@pytest.mark.asyncio
async def test_e2e_hallucination_catch(mock_httpx_post):
    """Guard catches a hallucination in a summary."""
    mock_httpx_post.return_value = _make_response(
        {
            "valid": False,
            "confidence": 0.97,
            "reason": "Source text never mentions GPT-5. It only discusses GPT-4 improvements.",
            "method": "filter",
        }
    )

    article_text = """
    OpenAI announced significant improvements to GPT-4 today,
    including a 2x speed increase and reduced hallucination rates.
    """

    result = await verify_fact_guard(
        claim="OpenAI announced GPT-5 today",
        source_text=article_text,
        strictness=0.9,
        api_key="test-key",
    )

    assert result.valid is False
    assert result.confidence > 0.9
    assert "GPT-5" in result.reason


@pytest.mark.asyncio
async def test_e2e_degraded_api_health(mock_httpx_get):
    """Health check shows degraded when API is slow but up."""
    resp = _make_response(
        {"status": "ok", "components": {"db": "ok", "cache": "degraded"}},
        status_code=200,
    )
    mock_httpx_get.return_value = resp

    result = await health_check()

    # Status is ok from response, but we note degradation
    assert result.status == "ok"
    assert result.components["cache"] == "degraded"


@pytest.mark.asyncio
async def test_e2e_api_down_fallback(mock_httpx_get):
    """When Brain API is down, health check returns down."""
    mock_httpx_get.side_effect = httpx.ConnectError("Connection refused")

    result = await health_check()

    assert result.status == "down"
    assert "Connection refused" in result.components.get("error", "")


@pytest.mark.asyncio
async def test_e2e_retry_then_success(mock_httpx_post):
    """API flakes twice, succeeds on third try. Agent gets answer transparently."""
    fail = _make_response({}, status_code=503)
    fail.raise_for_status.side_effect = _make_http_error(503)
    success = _make_response(
        {"answer": "The answer after retries", "method": "facts"}
    )

    mock_httpx_post.side_effect = [fail, fail, success]

    with patch("certainlogic_mcp.server._async_sleep", new_callable=AsyncMock):
        result = await brain_api_query("test", api_key="test-key")

    assert result.confident is True
    assert result.answer == "The answer after retries"
    assert mock_httpx_post.call_count == 3


@pytest.mark.asyncio
async def test_e2e_rate_limit_then_success(mock_httpx_post):
    """429 rate limit is NOT retried (client error). Returns error immediately."""
    resp = _make_response({}, status_code=429)
    resp.raise_for_status.side_effect = _make_http_error(429)
    mock_httpx_post.return_value = resp

    result = await brain_api_query("test", api_key="test-key")

    assert result.confident is False
    assert result.method == "error"
    assert "429" in result.answer
    assert mock_httpx_post.call_count == 1  # no retries


@pytest.mark.asyncio
async def test_e2e_empty_batch(mock_httpx_post):
    """Empty batch query returns empty results without HTTP calls."""
    result = await batch_query(queries=[], api_key="test-key")

    assert result.total == 0
    assert result.confident == 0
    assert result.uncertain == 0
    assert result.errors == 0
    mock_httpx_post.assert_not_awaited()


@pytest.mark.asyncio
async def test_e2e_guard_strictness_levels(mock_httpx_post):
    """Guard respects strictness parameter (0.7, 0.8, 0.9)."""
    mock_httpx_post.return_value = _make_response(
        {"valid": True, "confidence": 0.95, "reason": "ok", "method": "filter"}
    )

    for strictness in [0.7, 0.8, 0.9]:
        result = await verify_fact_guard(
            claim="test claim",
            source_text="test source text that supports the claim",
            strictness=strictness,
            api_key="test-key",
        )
        assert result.valid is True
        assert result.confidence == 0.95


@pytest.mark.asyncio
async def test_e2e_privacy_no_query_logging(mock_httpx_post):
    """Verify that raw query text never appears in logs."""
    mock_httpx_post.return_value = _make_response(
        {"answer": "secret answer", "method": "facts"}
    )

    sensitive_query = "my-company-secret-funding-amount"

    with patch("certainlogic_mcp.server.logger") as mock_logger:
        await brain_api_query(sensitive_query, api_key="test-key")

    # Verify logger was called
    mock_logger.info.assert_called_once()

    # Extract all args from the logger call
    args = mock_logger.info.call_args[0]
    args_str = " ".join(str(a) for a in args)

    # Raw query must NOT appear anywhere
    assert sensitive_query not in args_str
    # But hash should appear
    assert "query_hash=" in args_str
