#!/usr/bin/env python3
"""
Beta Onboarding Automation
Processes pending signups and sends welcome emails.

Usage:
    python3 scripts/beta_onboard.py --dry-run  # See what would happen
    python3 scripts/beta_onboard.py             # Actually process

Triggered by cron hourly or manually.
"""

import json
import os
import time
import argparse
from pathlib import Path
from email.mime.text import MIMEText
import smtplib

# ── Config ────────────────────────────────────────────────────────────────
BETA_DIR = Path(os.getenv("BETA_DATA_DIR", "/data/.openclaw/workspace/data/beta"))
SIGNUPS_FILE = BETA_DIR / "signups.jsonl"
SENT_FILE = BETA_DIR / "emails_sent.jsonl"

# Email config (set via env vars)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "beta@certainlogic.ai")

WELCOME_SUBJECT = "Welcome to the CertainLogic Beta"

def get_welcome_body(product: str, name: str = "there") -> str:
    """Generate welcome email based on product."""
    
    install_cmd = """
# Install the Deterministic Brain
bash <(curl -fsSL https://raw.githubusercontent.com/CertainLogicAI/hallucination-guard/cleanup_complete/company-brain/install.sh)

# Quickie
python3 -c "from deterministic_brain import DeterministicBrain; print('Ready')"
"""
    
    return f"""Hi {name},

Welcome to the CertainLogic beta program.

You signed up for: {product}

GET STARTED:
{install_cmd}

QUICKSTART:
https://github.com/CertainLogicAI/hallucination-guard/blob/cleanup_complete/docs/BETA_QUICKSTART.md

DEMO:
python3 scripts/demo_crypto_provenance.py

SUPPORT:
- GitHub Issues: https://github.com/CertainLogicAI/hallucination-guard/issues
- Reply to this email

We're building this with you. Feedback shapes the product.

— Anton & The CertainLogic Team
"""

def send_email(to: str, subject: str, body: str, dry_run: bool = False) -> bool:
    """Send email via SMTP. If dry_run, just log."""
    if dry_run:
        print(f"[DRY RUN] Would email {to}: {subject}")
        return True
    
    if not SMTP_HOST or not SMTP_USER:
        print(f"[SKIP] No SMTP configured. Would email {to}")
        return False
    
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        # Log sent
        with open(SENT_FILE, "a") as f:
            f.write(json.dumps({
                "email": to,
                "ts": time.time(),
                "subject": subject
            }) + "\n")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send to {to}: {e}")
        return False

def process_pending(dry_run: bool = False):
    """Find pending signups and send welcome emails."""
    if not SIGNUPS_FILE.exists():
        print("No signups yet.")
        return
    
    # Read all signups
    signups = []
    with open(SIGNUPS_FILE) as f:
        for line in f:
            try:
                signups.append(json.loads(line))
            except:
                continue
    
    pending = [s for s in signups if s.get("status") == "pending"]
    print(f"Found {len(pending)} pending signups")
    
    processed = 0
    for signup in pending:
        email = signup.get("email")
        product = signup.get("product", "deterministic-brain")
        name = signup.get("name", "there")
        
        body = get_welcome_body(product, name)
        
        if send_email(email, WELCOME_SUBJECT, body, dry_run):
            if not dry_run:
                # Mark as onboarded
                signup["status"] = "onboarded"
                signup["onboarded_at"] = time.time()
                # Update file (rewrite — inefficient but fine for small scale)
                with open(SIGNUPS_FILE, "w") as f:
                    for s in signups:
                        f.write(json.dumps(s) + "\n")
            processed += 1
    
    print(f"Processed {processed} signups")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    args = parser.parse_args()
    
    process_pending(dry_run=args.dry_run)
