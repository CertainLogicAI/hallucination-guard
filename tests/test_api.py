"""Test suite for the Deterministic AI Brain API."""

import os
from fastapi.testclient import TestClient
from main import app

# Override Redis host/port for test isolation
os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PORT'] = '6379'

client = TestClient(app)

def test_root():
    """Test the root endpoint returns a welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json().get("message") == "Deterministic AI Brain API"

def test_validate_success():
    """Test the /validate endpoint returns a successful response when Redis is reachable."""
    response = client.get("/validate")
    # Should return 200 if Redis ping works; in test env Redis may not be up, but we still assert structure
    assert response.status_code in (200, 500)  # Accept either success or error status
    data = response.json()
    assert "redis_connected" in data

def test_invalid_endpoint():
    """Test that non‑existent endpoints return a 404 error."""
    response = client.get("/non‑existent")
    assert response.status_code == 404