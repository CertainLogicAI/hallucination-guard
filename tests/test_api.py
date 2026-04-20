#!/usr/bin/env python3
"""
Unit tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient

# We need to import the app from main. However main uses relative imports.
# Since we are inside the opensource directory, we can safely import the app.
# Let's do a hack: we'll copy the app initialization into a separate file, or run actual service.
# For simplicity, we'll run the actual server on test port (maybe with asyncio).
# We'll need to use TestClient with imported app.
# Let's see if we can import main and get the app.
from main import app

client = TestClient(app)


def test_validate_endpoint():
    """Test /validate endpoint with known fact."""
    payload = {"query": "What is 2+2?", "response": "4"}
    response = client.post("/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Expect valid or at least something
    assert "valid" in data
    assert "confidence" in data


def test_validate_onunverifiable():
    """Test /validate with query that has no fact in DB."""
    payload = {"query": "What is 9+10?", "response": "19"}
    response = client.post("/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Expect valid=False (confidence below threshold)
    assert not data.get("valid")


def test_reduce_endpoint():
    """Test /reduce endpoint (token reduction)."""
    payload = {"query": "Explain quantum theory...", "semantic": True}
    response = client.post("/reduce", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Expect reduced_tokens maybe
    assert "reduced_query" in data


def test_search_endpoint():
    """Test TF-IDF search over memory."""
    payload = {"query": "PLC safety", "top_k": 5}
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Expect dict with results list
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)


def test_route_endpoint():
    """Test intent router."""
    payload = {"query": "What is the price of GPT-5?"}
    response = client.post("/route", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Expect brain_handler key (main routing output)
    assert "brain_handler" in data


if __name__ == "__main__":
    pytest.main(["-v", __file__])
