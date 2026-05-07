"""
CLI Pool — Brain OS Production Hardening

Prevents fork-bomb by limiting concurrent gbrain CLI processes.
Uses a thread-safe queue with max 4 workers.

Usage:
    from cli_pool import CLIPool
    
    pool = CLIPool(max_workers=4)
    result = pool.run(["bun", "run", "src/cli.ts", "query", "moat"])
"""

import subprocess
import threading
import queue
import time
from typing import List, Optional


class CLIPool:
    """Thread-safe process pool for CLI calls."""

    def __init__(self, max_workers: int = 4, timeout: float = 30.0):
        self.max_workers = max_workers
        self.timeout = timeout
        self._lock = threading.Lock()
        self._active = 0
        self._queue = queue.Queue()
        self._results = {}  # request_id -> result
        self._workers = []
        self._shutdown = False
        self._worker_id_counter = 0

    def run(self, cmd: List[str], cwd: Optional[str] = None, 
            input_data: Optional[str] = None,
            timeout: Optional[float] = None) -> dict:
        """
        Execute a CLI command through the pool.
        
        If pool is at capacity, the call blocks until a slot is available.
        """
        request_id = self._next_request_id()
        item = {
            "request_id": request_id,
            "cmd": cmd,
            "cwd": cwd,
            "input_data": input_data,
            "timeout": timeout or self.timeout,
        }
        self._queue.put(item)

        # Wait for result
        start = time.time()
        while request_id not in self._results:
            elapsed = time.time() - start
            if elapsed > (timeout or self.timeout) + 5:  # buffer
                raise TimeoutError(f"CLI pool wait timeout for {cmd}")
            time.sleep(0.01)

        result = self._results.pop(request_id)
        return result

    def _next_request_id(self) -> int:
        with self._lock:
            self._worker_id_counter += 1
            return self._worker_id_counter

    def start_workers(self):
        """Start worker threads. Call once at pool init."""
        for _ in range(self.max_workers):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self._workers.append(t)

    def _worker_loop(self):
        """Worker thread: pull from queue, execute, store result."""
        while not self._shutdown:
            try:
                item = self._queue.get(timeout=1)
            except queue.Empty:
                continue

            try:
                result = subprocess.run(
                    item["cmd"],
                    capture_output=True,
                    text=True,
                    timeout=item["timeout"],
                    cwd=item.get("cwd"),
                    input=item.get("input_data"),
                )
                self._results[item["request_id"]] = {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                }
            except subprocess.TimeoutExpired:
                self._results[item["request_id"]] = {
                    "success": False,
                    "error": "timeout",
                    "stdout": "",
                    "stderr": "",
                }
            except Exception as e:
                self._results[item["request_id"]] = {
                    "success": False,
                    "error": str(e),
                    "stdout": "",
                    "stderr": "",
                }

    def shutdown(self):
        """Shutdown the pool gracefully."""
        self._shutdown = True
        for w in self._workers:
            w.join(timeout=2)


# Global singleton pool — shared across all brain queries
_global_pool: Optional[CLIPool] = None
_pool_lock = threading.Lock()


def get_cli_pool() -> CLIPool:
    """Get the global CLI pool (lazy init)."""
    global _global_pool
    with _pool_lock:
        if _global_pool is None:
            _global_pool = CLIPool(max_workers=4, timeout=30.0)
            _global_pool.start_workers()
        return _global_pool
