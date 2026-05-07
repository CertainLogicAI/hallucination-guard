"""
Input Validator — Brain OS Security Hardening

Validates all inputs before they reach the brain to prevent injection,
path traversal, and malformed queries.

Usage:
    from input_validator import validate_query, validate_slug
    
    validate_query("what is our moat")  # OK
    validate_query("'; DROP TABLE pages; --")  # Raises ValueError
    
    validate_slug("concepts/moat")  # OK
    validate_slug("../../etc/passwd")  # Raises ValueError
"""

import re
from typing import Optional

# Slug whitelist: allowed characters
SLUG_PATTERN = re.compile(r"^[a-zA-Z0-9_/-]+$")

# Maximum query length
MAX_QUERY_LENGTH = 2000

# SQL-like injection patterns to reject
SQL_PATTERNS = [
    r";\s*--",
    r";\s*DROP\s",
    r";\s*DELETE\s",
    r"UNION\s+SELECT",
    r"INSERT\s+INTO",
    r"UPDATE\s+\w+\s+SET",
    r"EXEC\s*\(",
    r"xp_",
]


def validate_slug(slug: str) -> str:
    """
    Validate a slug string.
    
    Rules:
    - Only alphanumeric, underscores, hyphens, and forward slashes
    - No '..' (path traversal)
    - No absolute paths (starting with /)
    - Maximum length: 500 characters
    
    Returns:
        Cleaned slug (lowercased, stripped)
    
    Raises:
        ValueError: If slug is invalid
    """
    if not slug or not isinstance(slug, str):
        raise ValueError("Slug must be a non-empty string")

    slug = slug.strip().lower()

    if len(slug) > 500:
        raise ValueError(f"Slug too long: {len(slug)} chars (max 500)")

    if ".." in slug:
        raise ValueError(f"Path traversal detected in slug: {slug}")

    if slug.startswith("/"):
        raise ValueError(f"Absolute path not allowed in slug: {slug}")

    if not SLUG_PATTERN.match(slug):
        raise ValueError(f"Invalid characters in slug: {slug}. Only a-z, 0-9, _, -, / allowed")

    return slug


def validate_query(query: str) -> str:
    """
    Validate a query string.
    
    Rules:
    - Maximum length: 2000 characters
    - No SQL injection patterns
    - No null bytes
    
    Returns:
        Cleaned query (stripped)
    
    Raises:
        ValueError: If query is invalid
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")

    query = query.strip()

    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError(f"Query too long: {len(query)} chars (max {MAX_QUERY_LENGTH})")

    if "\x00" in query:
        raise ValueError("Null bytes not allowed in query")

    query_lower = query.lower()
    for pattern in SQL_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            raise ValueError(f"Potential SQL injection detected in query: {query[:100]}...")

    return query


def validate_limit(limit: Optional[int]) -> int:
    """
    Validate a limit parameter.
    
    Returns:
        Validated limit (default 5, max 100)
    """
    if limit is None:
        return 5

    if not isinstance(limit, int):
        raise ValueError("Limit must be an integer")

    if limit < 1:
        raise ValueError("Limit must be >= 1")

    if limit > 100:
        raise ValueError("Limit must be <= 100")

    return limit
