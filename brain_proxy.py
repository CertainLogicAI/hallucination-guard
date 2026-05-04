#!/usr/bin/env python3
"""OpenAI-compatible proxy for CertainLogic Brain API.

Makes the brain API available as an OpenAI-compatible chat completions endpoint.
Hermes (and any other agent) can route through this to get cache + validation.

Usage:
    python3 brain_proxy.py  # listens on 127.0.0.1:8001
    
In agent config, set model to point at this proxy:
    model: "brain-local"  # (if OpenClaw supports custom endpoints)
    
Or configure OpenClaw openai provider with base_url = http://127.0.0.1:8001
"""
import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import HTTPError

BRAIN_API = os.getenv("BRAIN_API", "http://127.0.0.1:8000")
PROXY_PORT = int(os.getenv("BRAIN_PROXY_PORT", "8001"))


class BrainProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Suppress default logging
        pass

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "proxy_for": BRAIN_API})
        else:
            self._send_json(404, {"error": "Only /v1/chat/completions and /health supported"})

    def do_POST(self):
        if self.path == "/v1/chat/completions":
            self._handle_chat_completion()
        else:
            self._send_json(404, {"error": "Unknown endpoint"})

    def _handle_chat_completion(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8")
        try:
            req = json.loads(body)
        except json.JSONDecodeError:
            return self._send_json(400, {"error": "Invalid JSON"})

        # Extract messages into a single prompt
        messages = req.get("messages", [])
        prompt = "\n".join(m.get("content", "") for m in messages if m.get("content"))

        # Call brain API
        brain_req = {
            "query": prompt,
            "response": "",  # Brain generates response
            "task": req.get("model", "general"),
            "force_deterministic": False  # ALLOW LLM FALLBACK
        }

        try:
            breq = Request(
                f"{BRAIN_API}/query",
                data=json.dumps(brain_req).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urlopen(breq, timeout=120) as resp:
                brain_result = json.loads(resp.read().decode())
        except Exception as e:
            return self._send_json(502, {"error": f"Brain API error: {e}"})

        # Format as OpenAI chat completion response
        choice_text = brain_result.get("response", brain_result.get("cached_response", "No response"))
        finish_reason = "stop"

        # If brain returned null/empty and there was a fallback
        if not choice_text or choice_text == "No response":
            choice_text = brain_result.get("llm_response", "Brain returned empty response")

        openai_response = {
            "id": f"brain-{brain_result.get('run_id', 'local')}",
            "object": "chat.completion",
            "created": brain_result.get("timestamp", 0),
            "model": req.get("model", "brain-local"),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": choice_text
                },
                "finish_reason": finish_reason
            }],
            "usage": {
                "prompt_tokens": brain_result.get("prompt_tokens", len(prompt.split())),
                "completion_tokens": brain_result.get("completion_tokens", len(str(choice_text).split())),
                "total_tokens": brain_result.get("total_tokens", 0)
            }
        }

        self._send_json(200, openai_response)

    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PROXY_PORT), BrainProxyHandler)
    print(f"Brain proxy running on http://127.0.0.1:{PROXY_PORT} -> {BRAIN_API}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
        server.shutdown()
