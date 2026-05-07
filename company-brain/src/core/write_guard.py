"""
Write Guard — Brain OS Security Hardening

Restricts write access to the brain. Read path is fast and unrestricted.
Write path requires explicit authorization.

Usage:
    from write_guard import WriteGuard
    
    guard = WriteGuard()
    if guard.can_write("brain.put_page", caller="my_script.py"):
        # Proceed with write
    else:
        raise PermissionError("Write access denied")
"""

import os
from typing import Set

# Files allowed to write to the brain
ALLOWED_WRITERS: Set[str] = {
    "deterministic_brain.py",
    "brain_wrapper.py",
    "admin_ingest.py",
    "admin_cleanup.py",
}

# Environment variable override: comma-separated list of additional writers
def get_allowed_writers() -> Set[str]:
    """Get the set of files allowed to write to the brain."""
    writers = set(ALLOWED_WRITERS)
    
    env_overrides = os.getenv("BRAIN_WRITE_ALLOWLIST", "")
    if env_overrides:
        for writer in env_overrides.split(","):
            writer = writer.strip()
            if writer:
                writers.add(writer)
    
    return writers


class WriteGuard:
    """Controls write access to the brain."""

    def __init__(self):
        self._allowed_writers = get_allowed_writers()

    def can_write(self, operation: str, caller: str = "") -> bool:
        """
        Check if the caller is allowed to perform a write operation.
        
        Args:
            operation: The brain operation (e.g., "brain.put_page")
            caller: The name of the calling file/module
        
        Returns:
            True if write is allowed, False otherwise
        """
        # Extract filename from caller path
        if "/" in caller:
            caller = caller.split("/")[-1]
        if "\\" in caller:
            caller = caller.split("\\")[-1]

        # Check if caller is in allowlist
        if caller in self._allowed_writers:
            return True

        # Check without .py extension
        caller_no_ext = caller.replace(".py", "")
        if caller_no_ext in {w.replace(".py", "") for w in self._allowed_writers}:
            return True

        return False

    def get_allowlist(self) -> Set[str]:
        """Return the current allowlist (for diagnostics)."""
        return set(self._allowed_writers)
