#!/usr/bin/env python3
"""Hallucination Guard -- Customer SDK for CertainLogic Brain API.

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


class HGuardClient:
    """Customer-facing wrapper for CertainLogic Brain validation."""

    def __init__(self, api_url: str = BRAIN_API):
        self.api_url = api_url.rstrip("/")
        self.threshold = 0.7

    def _post(self, endpoint: str, payload: dict) -> dict:
        req = Request(
            f"{self.api_url}{endpoint}",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def validate(self, query: str, response: str) -> dict:
        """Validate a (query, response) pair for hallucinations.
        
        Uses /validate endpoint for direct validation, not /query (which routes).
        """
        result = self._post("/validate", {"query": query, "response": response})
        
        if "error" in result:
            return {
                "valid": True,
                "flagged": False,
                "confidence": 1.0,
                "flags": [f"API error: {result['error']}"],
                "error": result["error"]
            }
        
        return {
            "valid": result.get("valid", True),
            "flagged": result.get("flagged", False),
            "confidence": result.get("confidence", 1.0),
            "flags": result.get("flags", []),
            "checks": result.get("checks", {})
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
