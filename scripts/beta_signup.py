#!/usr/bin/env python3
"""
Beta Signup Server — CertainLogic
Handles beta signup form submissions, validates data, stores to JSONL.

Usage:
    python3 scripts/beta_signup.py
    # Server runs on localhost:8001
    
    curl -X POST http://localhost:8001/api/beta/signup \
      -H "Content-Type: application/json" \
      -d '{"product": "deterministic-brain", "email": "test@example.com"}'
"""

import json
import os
import re
import time
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs

# ── Config ────────────────────────────────────────────────────────────────
BETA_DIR = Path(os.getenv("BETA_DATA_DIR", "/data/.openclaw/workspace/data/beta"))
SIGNUPS_FILE = BETA_DIR / "signups.jsonl"
INDEX_FILE = BETA_DIR / "signups_by_email.json"
RATE_LIMIT_FILE = BETA_DIR / "rate_limit.jsonl"

# Allowed products
VALID_PRODUCTS = {
    "deterministic-brain", "hallucination-guard", "faulttrace",
    "skill-vetter", "agentpathfinder", "other"
}

# Ensure dirs
BETA_DIR.mkdir(parents=True, exist_ok=True)

# ── Storage ───────────────────────────────────────────────────────────────
def store_signup(data: dict) -> str:
    """Store signup to append-only JSONL, return ID."""
    signup_id = str(uuid.uuid4())[:8]
    record = {
        "_id": signup_id,
        "submitted_at": time.time(),
        "status": "pending",
        "onboarded_at": None,
        "feedback_count": 0,
        "plan": "free",
        **data,
    }
    
    # Write to JSONL
    with open(SIGNUPS_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")
    
    # Update email index
    index = {}
    if INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            index = json.load(f)
    index[data["email"].lower()] = signup_id
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)
    
    return signup_id

def check_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded 5 signups in the last hour."""
    now = time.time()
    if not RATE_LIMIT_FILE.exists():
        return True
    
    count = 0
    with open(RATE_LIMIT_FILE) as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry["ip"] == ip and (now - entry["ts"]) < 3600:
                    count += 1
            except:
                continue
    
    if count >= 5:
        return False
    
    # Log this attempt
    with open(RATE_LIMIT_FILE, "a") as f:
        f.write(json.dumps({"ip": ip, "ts": now}) + "\n")
    return True

def validate_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_duplicate(email: str) -> bool:
    """Check if email already signed up."""
    if not INDEX_FILE.exists():
        return False
    with open(INDEX_FILE) as f:
        index = json.load(f)
    return email.lower() in index

# ── HTTP Handler ──────────────────────────────────────────────────────────
class BetaHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging (add proper logging later)
        pass
    
    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
    
    def do_POST(self):
        if self.path == "/api/beta/signup":
            self._handle_signup()
        else:
            self._send_json(404, {"error": "Not found"})
    
    def do_GET(self):
        if self.path == "/api/beta/health":
            self._send_json(200, {"status": "ok"})
        elif self.path == "/api/beta/stats":
            self._handle_stats()
        else:
            self._send_json(404, {"error": "Not found"})
    
    def _handle_signup(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        
        # Validation
        product = data.get("product", "")
        if product not in VALID_PRODUCTS:
            self._send_json(400, {"error": f"Invalid product. Valid: {VALID_PRODUCTS}"})
            return
        
        email = data.get("email", "").strip().lower()
        if not email or not validate_email(email):
            self._send_json(400, {"error": "Valid email required"})
            return
        
        # Rate limit by IP (use X-Forwarded-For if behind proxy)
        client_ip = self.headers.get("X-Forwarded-For", self.client_address[0])
        if not check_rate_limit(client_ip):
            self._send_json(429, {"error": "Rate limit exceeded. Try again later."})
            return
        
        # Duplicate check
        if is_duplicate(email):
            self._send_json(200, {
                "success": True,
                "message": "Already signed up! Check your email.",
                "id": None
            })
            return
        
        # Store
        signup_id = store_signup(data)
        
        self._send_json(200, {
            "success": True,
            "id": signup_id,
            "message": "Thanks! You'll receive onboarding instructions shortly."
        })
    
    def _handle_stats(self):
        # Simple stats (no auth for now — add API key later)
        if not SIGNUPS_FILE.exists():
            self._send_json(200, {"total": 0, "by_status": {}})
            return
        
        total = 0
        by_status = {}
        by_product = {}
        
        with open(SIGNUPS_FILE) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    total += 1
                    by_status[entry.get("status", "unknown")] = by_status.get(entry.get("status", "unknown"), 0) + 1
                    by_product[entry.get("product", "unknown")] = by_product.get(entry.get("product", "unknown"), 0) + 1
                except:
                    continue
        
        self._send_json(200, {
            "total": total,
            "by_status": by_status,
            "by_product": by_product,
            "generated_at": time.time()
        })

# ── Server ────────────────────────────────────────────────────────────────
def run_server(port=8001):
    server = HTTPServer(("", port), BetaHandler)
    print(f"Beta signup server running on http://localhost:{port}")
    print(f"  POST /api/beta/signup → Submit signup")
    print(f"  GET  /api/beta/stats   → View stats")
    print(f"  GET  /api/beta/health  → Health check")
    server.serve_forever()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    run_server(port)
