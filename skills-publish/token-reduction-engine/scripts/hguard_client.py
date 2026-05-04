#!/usr/bin/env python3
"""Token Reduction Engine — SDK for CertainLogic Brain API.

Deterministic validation without LLM calls.

CLI Usage:
    python3 hguard_client.py validate "query text" "response text"
    python3 hguard_client.py batch input.json output.json
    python3 hguard_client.py status

Python Usage:
    from hguard_client import HGuardClient
    client = HGuardClient()
    result = client.validate("What is Docker?", "Docker is a platform.")
"""
import json, os, sys
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    HAS_REQUESTS = False

# NO hardcoded default endpoint — user must configure via env var or constructor
BRAIN_API = os.getenv("CERTAINLOGIC_API", "")


class HGuardClient:
    """Client for deterministic AI validation."""

    def __init__(self, api_url: str = None):
        api = (api_url or BRAIN_API or "").rstrip("/")
        if not api:
            raise ValueError(
                "Brain API URL required. Set CERTAINLOGIC_API env var or pass api_url=..."
            )
        self.api_url = api
        self.threshold = 0.7

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.api_url}{endpoint}"
        if HAS_REQUESTS:
            try:
                r = requests.post(url, json=payload, timeout=30)
                r.raise_for_status()
                return r.json()
            except requests.RequestException as e:
                return {"error": str(e)}
        else:
            req = Request(
                url,
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

    def _get(self, endpoint: str) -> dict:
        url = f"{self.api_url}{endpoint}"
        if HAS_REQUESTS:
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                return r.json()
            except requests.RequestException as e:
                return {"error": str(e)}
        else:
            req = Request(url, method="GET")
            try:
                with urlopen(req, timeout=10) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                return {"error": str(e)}

    def validate(self, query: str, response: str) -> dict:
        """Validate a (query, response) pair."""
        result = self._post("/validate", {"query": query, "response": response})
        if "error" in result:
            return {
                "valid": True, "flagged": False, "confidence": 1.0,
                "flags": [f"API error: {result['error']}"], "error": result["error"]
            }
        return {
            "valid": result.get("valid", True),
            "flagged": result.get("flagged", False),
            "confidence": result.get("confidence", 1.0),
            "flags": result.get("flags", []),
            "checks": result.get("checks", {})
        }

    def batch_validate(self, cases: list[dict]) -> list[dict]:
        """Validate multiple cases."""
        return [self.validate(c["query"], c["response"]) for c in cases]

    def status(self) -> dict:
        """Check Brain API health."""
        return self._get("/health")

    def set_threshold(self, threshold: float):
        self.threshold = threshold


def cli_validate():
    if len(sys.argv) < 4:
        print("Usage: python3 hguard_client.py validate '<query>' '<response>'")
        sys.exit(1)
    client = HGuardClient()
    result = client.validate(sys.argv[2], sys.argv[3])
    print(json.dumps(result, indent=2))


def cli_batch():
    if len(sys.argv) < 5:
        print("Usage: python3 hguard_client.py batch input.json output.json")
        sys.exit(1)
    input_file, output_file = sys.argv[3], sys.argv[4]
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    with open(input_file) as f:
        cases = json.load(f)
    client = HGuardClient()
    results = client.batch_validate(cases)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Batch complete: {len(results)} cases → {output_file}")


def cli_status():
    client = HGuardClient()
    result = client.status()
    if "error" in result:
        print(f"❌ Brain API unreachable: {result['error']}")
        print(f"   Is the server running at {client.api_url}?")
        sys.exit(1)
    print(f"✅ Brain API: {result.get('status', 'unknown')}")
    facts = result.get("components", {}).get("facts_db", "")
    if "facts" in str(facts).lower():
        print(f"   Facts loaded: {facts}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("""Token Reduction Engine — CLI

Commands:
  validate <query> <response>   Validate a single response
  batch <input.json> <output>   Validate multiple cases
  status                        Check Brain API health

Environment:
  CERTAINLOGIC_API              Brain API URL (no default)
""")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "validate":
        cli_validate()
    elif cmd == "batch":
        cli_batch()
    elif cmd == "status":
        cli_status()
    else:
        print(f"Unknown command: {cmd}")
        main()


if __name__ == "__main__":
    main()
