"""
Log Redactor — Brain OS Security Hardening

Prevents credential leakage in logs by redacting sensitive patterns.

Usage:
    from log_redactor import redact_query, redact_log_entry
    
    safe_query = redact_query("api_key=sk-abc123")
    # Returns: "api_key=[REDACTED_CREDENTIAL]"
"""

import re
from typing import Any, Dict

# Patterns that look like credentials
CREDENTIAL_PATTERNS = [
    # API keys
    r"(api[_-]?key|apikey)\s*[:=]\s*\S+",
    # Secrets
    r"(secret|private[_-]?key)\s*[:=]\s*\S+",
    # Tokens
    r"(token|access[_-]?token|refresh[_-]?token)\s*[:=]\s*\S+",
    # Passwords
    r"(password|passwd|pwd)\s*[:=]\s*\S+",
    # Credentials
    r"(credential|auth)\s*[:=]\s*\S+",
    # AWS keys
    r"AKIA[0-9A-Z]{16}",
    # Generic hex keys (32+ chars)
    r"\b[0-9a-f]{32,}\b",
    # Generic base64 keys (40+ chars)
    r"[A-Za-z0-9+/]{40,}={0,2}",
]

# Compile patterns for performance
_CREDENTIAL_REGEXES = [re.compile(p, re.IGNORECASE) for p in CREDENTIAL_PATTERNS]


def redact_query(query: str) -> str:
    """
    Redact potential credentials from a query string.
    
    Returns:
        Query with credentials replaced by [REDACTED_CREDENTIAL]
    """
    if not query:
        return query

    for pattern in _CREDENTIAL_REGEXES:
        query = pattern.sub("[REDACTED_CREDENTIAL]", query)

    return query


def redact_log_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact credentials from a log entry dictionary.
    
    Modifies:
    - "query" field
    - Any field containing "key", "token", "secret", "password", "credential"
    
    Returns:
        New dictionary with redacted values (does not modify original)
    """
    redacted = {}
    for key, value in entry.items():
        if isinstance(value, str):
            # Redact known sensitive fields entirely
            if any(s in key.lower() for s in ["key", "token", "secret", "password", "credential"]):
                redacted[key] = "[REDACTED]"
            # Redact queries that might contain credentials
            elif key.lower() in ["query", "q", "text", "input"]:
                redacted[key] = redact_query(value)
            else:
                redacted[key] = value
        else:
            redacted[key] = value

    return redacted


def redact_string(text: str) -> str:
    """
    Redact any credentials found in arbitrary text.
    
    Useful for error messages, stack traces, etc.
    """
    return redact_query(text)
