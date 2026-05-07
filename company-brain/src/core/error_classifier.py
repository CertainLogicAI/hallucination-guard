"""
Error Classifier — Brain OS Production Hardening

Distinguishes transient errors (retryable) from permanent errors (not retryable).

Transient: timeout, file lock, connection issue, process error
Permanent: bad slug, no matches, invalid input

Usage:
    from error_classifier import classify_error
    
    try:
        result = brain.query("...")
    except Exception as e:
        if classify_error(e) == "TRANSIENT":
            retry_with_backoff()
        else:
            raise  # Permanent, don't retry
"""

import subprocess
import sqlite3


def classify_error(error: Exception) -> str:
    """
    Classify an exception as TRANSIENT or PERMANENT.
    
    Returns:
        "TRANSIENT" — retry with backoff
        "PERMANENT" — don't retry, propagate immediately
    """
    error_type = type(error).__name__
    error_msg = str(error).lower()

    # Transient errors
    transient_types = (subprocess.TimeoutExpired,)
    transient_messages = [
        "timeout",
        "database is locked",
        "resource temporarily unavailable",
        "try again",
        "connection reset",
        "no such process",
    ]

    if isinstance(error, transient_types):
        return "TRANSIENT"

    for msg in transient_messages:
        if msg in error_msg:
            return "TRANSIENT"

    # Permanent errors
    permanent_types = (ValueError, KeyError, TypeError, AssertionError)
    permanent_messages = [
        "invalid",
        "bad slug",
        "not found",
        "does not exist",
        "no matches",
        "malformed",
        "forbidden",
    ]

    if isinstance(error, permanent_types):
        return "PERMANENT"

    for msg in permanent_messages:
        if msg in error_msg:
            return "PERMANENT"

    # Default: unknown errors treated as transient (safer to retry once)
    return "TRANSIENT"
