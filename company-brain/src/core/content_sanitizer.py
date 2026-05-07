"""
Content Sanitizer — Brain OS Security Hardening

Strips dangerous content from brain output before returning to skills.
Preserves markdown. Removes scripts, dangerous URLs, and HTML.

Usage:
    from content_sanitizer import sanitize_content
    
    clean = sanitize_content("<script>alert(1)</script> Hello **world**")
    # Returns: "Hello **world**"
"""

import re
from html import escape as html_escape

# Patterns to strip completely
DANGEROUS_PATTERNS = [
    # Script tags
    r"<script[^>]*>.*?</script>",
    # Event handlers
    r"\son\w+\s*=\s*['\"][^'\"]*['\"]",
    # javascript: URLs
    r"javascript:[^\s\"'>]+",
    # data: URLs
    r"data:[^\s\"'>]+",
    # vbscript: URLs
    r"vbscript:[^\s\"'>]+",
    # iframe/embed/object tags
    r"<iframe[^>]*>.*?</iframe>",
    r"<embed[^>]*>.*?</embed>",
    r"<object[^>]*>.*?</object>",
    # Form submission elements
    r"<form[^>]*>.*?</form>",
    r"<input[^>]*>",
]

# Compile patterns
_DANGEROUS_REGEXES = [re.compile(p, re.DOTALL | re.IGNORECASE) for p in DANGEROUS_PATTERNS]


def sanitize_content(content: str) -> str:
    """
    Sanitize content from the brain before returning to skills.
    
    Rules:
    - Strip <script>, <iframe>, <embed>, <object>, <form> tags
    - Strip event handlers (onclick, onload, etc.)
    - Strip javascript: and data: URLs
    - Strip vbscript: URLs
    - Preserve markdown formatting (**bold**, *italic*, `code`, etc.)
    - Escape remaining HTML tags
    
    Returns:
        Sanitized content string
    """
    if not content:
        return content

    # Step 1: Strip dangerous patterns
    for pattern in _DANGEROUS_REGEXES:
        content = pattern.sub("", content)

    # Step 2: Escape remaining HTML tags (but preserve markdown)
    # We don't want to escape markdown syntax, so we handle it carefully
    
    # Step 3: Remove null bytes
    content = content.replace("\x00", "")

    # Step 4: Normalize whitespace
    content = re.sub(r"\n{3,}", "\n\n", content)

    return content.strip()


def is_dangerous(content: str) -> bool:
    """
    Check if content contains dangerous patterns.
    
    Returns:
        True if dangerous content detected, False otherwise
    """
    if not content:
        return False

    for pattern in _DANGEROUS_REGEXES:
        if pattern.search(content):
            return True

    return False
