#!/usr/bin/env python3
"""Hermes Brain Client — CertainLogic SaaS Integration Layer.

Treats the local CertainLogic Brain API (localhost:8000) as a customer
would use our paid API. Provides:
  1. Token reduction on input (saves ~20% tokens)
  2. Hallucination validation on output
  3. Metrics logging per task/session

Usage in Hermes specs:
    from hermes_brain_client import BrainClient
    client = BrainClient()
    
    # Before calling LLM
    reduced, savings = client.reduce(spec_text)
    
    # After LLM returns
    result = client.validate(query, llm_response)
    if not result['valid']:
        print(f"Hallucination detected: {result['flags']}")
    
    # Log metrics for this task
    client.log_task(task_name, tokens_saved= savings, validation=result)
"""
import json, os, time, hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BRAIN_API = os.getenv("BRAIN_API", "http://127.0.0.1:8000")
LOG_DIR = Path(__file__).parent / "brain_logs"
LOG_DIR.mkdir(exist_ok=True)


class BrainClient:
    """Customer-facing wrapper for CertainLogic Brain API."""

    def __init__(self, api_url: str = BRAIN_API):
        self.api_url = api_url.rstrip("/")
        self.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        self.tasks: list[dict] = []
        self._check_health()

    def _check_health(self):
        try:
            with urlopen(f"{self.api_url}/health", timeout=5) as r:
                data = json.loads(r.read())
                self.brain_ready = data.get("status") == "ok"
        except Exception:
            self.brain_ready = False
            print(f"[BrainClient] WARNING: Brain API at {self.api_url} not reachable")

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

    def reduce(self, text: str) -> tuple[str, int]:
        """Reduce tokens in a prompt before sending to LLM.
        Returns: (reduced_text, tokens_saved_estimate)
        """
        result = self._post("/query", {
            "query": f"TOKEN_REDUCE: {text}",
            "force_deterministic": False
        })
        
        # Brain returns structure with reduced_query in token_stats
        reduced = result.get("token_stats", {}).get("reduced_query", text)
        original_len = len(text.split())
        reduced_len = len(reduced.split())
        saved = max(0, original_len - reduced_len)
        
        return reduced, saved

    def validate(self, query: str, response: str) -> dict:
        """Validate an LLM response for hallucinations.
        Returns: dict with valid, flagged, confidence, flags
        """
        result = self._post("/query", {
            "query": query,
            "response": response,
            "force_deterministic": False
        })
        
        # Extract validation results
        validation = result.get("validation", {})
        return {
            "valid": validation.get("valid", True),
            "flagged": validation.get("flagged", False),
            "confidence": validation.get("confidence", 1.0),
            "flags": validation.get("flags", []),
            "method": result.get("method", "unknown"),
            "routing": result.get("routing", "unknown"),
            "cache_hit": result.get("method") in ["cache", "facts_cache"],
            "raw": result
        }

    def log_task(self, task_name: str, tokens_saved: int = 0, validation: dict = None):
        """Log a task for session metrics."""
        self.tasks.append({
            "task": task_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tokens_saved": tokens_saved,
            "validation": validation or {},
            "session": self.session_id
        })

    def get_metrics(self) -> dict:
        """Get aggregated metrics for this session."""
        total_tasks = len(self.tasks)
        cache_hits = sum(1 for t in self.tasks if t["validation"].get("cache_hit"))
        validations = [t["validation"] for t in self.tasks if t["validation"]]
        valid_count = sum(1 for v in validations if v.get("valid"))
        flagged_count = sum(1 for v in validations if v.get("flagged"))
        total_tokens_saved = sum(t["tokens_saved"] for t in self.tasks)
        
        return {
            "session_id": self.session_id,
            "total_tasks": total_tasks,
            "cache_hits": cache_hits,
            "cache_hit_rate_pct": round(cache_hits / total_tasks * 100, 2) if total_tasks else 0,
            "validations_passed": valid_count,
            "validations_flagged": flagged_count,
            "total_tokens_saved": total_tokens_saved,
            "brain_ready": self.brain_ready
        }

    def save_session_log(self):
        """Persist session metrics to disk."""
        log_file = LOG_DIR / f"hermes_session_{self.session_id}.json"
        data = {
            "session_id": self.session_id,
            "start_time": self.tasks[0]["timestamp"] if self.tasks else datetime.now(timezone.utc).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat(),
            "metrics": self.get_metrics(),
            "tasks": self.tasks
        }
        with open(log_file, "w") as f:
            json.dump(data, f, indent=2)
        return str(log_file)


def main():
    """CLI: test the integration."""
    client = BrainClient()
    print(f"[HermesBrain] Session: {client.session_id}")
    print(f"[HermesBrain] Brain ready: {client.brain_ready}")
    
    # Demo: reduce tokens
    spec = "Write a Python function to check if a string is a palindrome. The function should handle edge cases like empty strings and non-alphabetic characters."
    reduced, saved = client.reduce(spec)
    print(f"\nToken reduction: {len(spec.split())} -> {len(reduced.split())} (saved ~{saved})")
    
    # Demo: validate a response
    query = "What is the default max recursion depth in Python?"
    response = "Python's default maximum recursion depth is 1000."
    result = client.validate(query, response)
    print(f"\nValidation: valid={result['valid']}, confidence={result['confidence']:.2f}")
    if result["flags"]:
        print(f"Flags: {result['flags']}")
    
    client.log_task("demo_reduce_validate", tokens_saved=saved, validation=result)
    
    # Save log
    log_path = client.save_session_log()
    print(f"\nSession log: {log_path}")


if __name__ == "__main__":
    main()
