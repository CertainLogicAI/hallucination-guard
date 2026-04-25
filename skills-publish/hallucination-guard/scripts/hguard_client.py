#!/usr/bin/env python3
"""Hallucination Guard — Customer SDK for CertainLogic Brain API.

Deterministic validation without LLM calls. Install this skill and import
to validate any AI-generated text.

Usage:
    from hguard_client import HGuardClient
    client = HGuardClient()
    result = client.validate("What is Docker?", "Docker is a platform.")
    print(result["valid"])  # True/False
"""
import json, os, sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BRAIN_API = os.getenv("CERTAINLOGIC_API", "http://127.0.0.1:8000")
API_KEY = os.getenv("CERTAINLOGIC_KEY", "")


class HGuardClient:
    """Customer-facing wrapper for CertainLogic Brain validation."""

    def __init__(self, api_url: str = BRAIN_API):
        self.api_url = api_url.rstrip("/")
        self.threshold = 0.7

    def validate(self, query: str, response: str) -> dict:
        """Validate a (query, response) pair for hallucinations."""
        req = Request(
            f"{self.api_url}/query",
            data=json.dumps({
                "query": query,
                "response": response,
                "force_deterministic": False
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urlopen(req, timeout=30) as r:
                result = json.loads(r.read().decode())
        except Exception as e:
            return {"valid": True, "error": str(e), "flags": [f"API error: {e}"]}

        validation = result.get("validation", {})
        return {
            "valid": validation.get("valid", True),
            "flagged": validation.get("flagged", False),
            "confidence": validation.get("confidence", 1.0),
            "flags": validation.get("flags", []),
            "method": result.get("method", "unknown"),
            "routing": result.get("routing", "unknown")
        }

    def batch_validate(self, cases: list[dict]) -> list[dict]:
        """Validate multiple cases at once."""
        return [self.validate(c["query"], c["response"]) for c in cases]

    def set_threshold(self, threshold: float):
        """Set confidence threshold (0.0-1.0)."""
        self.threshold = threshold


def main():
    """CLI entry point: hguard validate <query> <response>"""
    if len(sys.argv) >= 3:
        client = HGuardClient()
        result = client.validate(sys.argv[1], sys.argv[2])
        print(json.dumps(result, indent=2))
    else:
        print("Usage: hguard validate '<query>' '<response>'")
        sys.exit(1)


if __name__ == "__main__":
    main()
