"""Shared pytest fixtures for the certainlogic-mcp test suite.

All tests mock ``httpx.AsyncClient`` — no real Brain API calls are made.
"""

import os
from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest


# ---------------------------------------------------------------------------
# API key fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def brain_api_key_env(monkeypatch) -> Generator[str, None, None]:
    """Set BRAIN_API_KEY env var for the duration of a test, then unset."""
    key = "env-test-key"
    monkeypatch.setenv("BRAIN_API_KEY", key)
    yield key
    monkeypatch.delenv("BRAIN_API_KEY", raising=False)


# ---------------------------------------------------------------------------
# HTTP mocking fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_httpx_post() -> Generator[AsyncMock, None, None]:
    """Mock httpx.AsyncClient.post so tests never hit the real Brain API.

    Tests configure the returned response (or exception) via
    ``mock_httpx_post.return_value`` or ``mock_httpx_post.side_effect``.
    """
    with patch(
        "certainlogic_mcp.server.httpx.AsyncClient.post", new_callable=AsyncMock
    ) as mock_post:
        yield mock_post


@pytest.fixture
def mock_httpx_get() -> Generator[AsyncMock, None, None]:
    """Mock httpx.AsyncClient.get for health check tests."""
    with patch(
        "certainlogic_mcp.server.httpx.AsyncClient.get", new_callable=AsyncMock
    ) as mock_get:
        yield mock_get
