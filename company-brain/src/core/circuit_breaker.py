"""
Circuit Breaker — Brain OS Production Hardening

Prevents cascading failures by stopping queries after N consecutive failures.
Automatically recovers after a timeout.

Usage:
    cb = CircuitBreaker(failure_threshold=5, recovery_timeout=600)
    if cb.should_allow():
        try:
            result = brain.query("...")
            cb.record_success()
        except Exception:
            cb.record_failure()
            raise
    else:
        raise BrainUnavailable("Circuit breaker open")
"""

import time
import threading
from typing import Optional


class CircuitBreaker:
    """Simple thread-safe circuit breaker."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 600.0, name: str = "default"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name

        self._state = "CLOSED"  # CLOSED (normal), OPEN (blocked), HALF_OPEN (testing)
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = threading.Lock()

    def should_allow(self) -> bool:
        """Check if a query should proceed."""
        with self._lock:
            if self._state == "CLOSED":
                return True
            if self._state == "OPEN":
                if self._recovery_time_elapsed():
                    self._state = "HALF_OPEN"
                    return True
                return False
            if self._state == "HALF_OPEN":
                return True
            return True

    def record_success(self):
        """Record a successful query."""
        with self._lock:
            self._failure_count = 0
            if self._state == "HALF_OPEN":
                self._state = "CLOSED"

    def record_failure(self):
        """Record a failed query."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._failure_count >= self.failure_threshold:
                self._state = "OPEN"

    def _recovery_time_elapsed(self) -> bool:
        """Check if recovery timeout has passed since last failure."""
        if self._last_failure_time is None:
            return True
        elapsed = time.time() - self._last_failure_time
        return elapsed >= self.recovery_timeout

    def get_state(self) -> dict:
        """Return current state for diagnostics."""
        with self._lock:
            return {
                "name": self.name,
                "state": self._state,
                "failure_count": self._failure_count,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "last_failure_time": self._last_failure_time,
            }
