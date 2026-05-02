import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_query():
    response = client.post("/query", json={
        "query": "Explain Python in simple terms"
    })
    assert response.status_code == 200
    data = response.json()
    assert "cached" in data or "openclaw_response" in data

def test_validate_hallucination():
    response = client.post("/validate", json={
        "query": "What is 2+2?",
        "response": "I think it is 5."
    })
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data
    assert data["valid"] is False  # Hedge words detected

def test_validate_correct():
    response = client.post("/validate", json={
        "query": "What is the speed of light?",
        "response": "299,792,458 meters per second."
    })
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data

def test_search_facts():
    response = client.get("/facts/search?q=Python")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "cache_hits" in data or "total_queries" in data

def test_list_facts():
    response = client.get("/facts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
