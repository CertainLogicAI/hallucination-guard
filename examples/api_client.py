#!/usr/bin/env python3
"""
Example: interact with the hallucination-guard API service.

Prerequisites:
    # Start the service first:
    uvicorn main:app --host 0.0.0.0 --port 8000

Usage:
    python examples/api_client.py
"""

import json
import urllib.request

BASE_URL = "http://localhost:8000"


def post(endpoint: str, data: dict) -> dict:
    """Send POST request to the API."""
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get(endpoint: str) -> dict:
    """Send GET request to the API."""
    with urllib.request.urlopen(f"{BASE_URL}{endpoint}") as resp:
        return json.loads(resp.read())


# --- Health check ---
print("=== Health ===")
print(json.dumps(get("/health"), indent=2))
print()

# --- Validate a response ---
print("=== Validate ===")
result = post(
    "/validate",
    {
        "query": "What is the capital of France?",
        "response": "Paris",
    },
)
print(json.dumps(result, indent=2))
print()

# --- Token reduction ---
print("=== Reduce ===")
result = post(
    "/reduce",
    {
        "query": "Explain the theory of relativity in great detail including all equations",
        "semantic": True,
    },
)
print(json.dumps(result, indent=2))
print()

# --- Intent routing ---
print("=== Route ===")
result = post(
    "/route",
    {
        "query": "What is the price of GPT-5?",
    },
)
print(json.dumps(result, indent=2))
print()

# --- Search memory ---
print("=== Search ===")
result = post(
    "/search",
    {
        "query": "Python",
        "top_k": 3,
    },
)
print(json.dumps(result, indent=2))
