"""
Simple in-memory sliding-window rate limiter.
"""

from collections import defaultdict, deque
from threading import Lock
import time


class InMemoryRateLimiter:
    """Thread-safe in-memory rate limiter keyed by caller identity."""

    def __init__(self):
        self._events = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int):
        """
        Record one request and check if it is within the limit.

        Returns:
            (allowed, retry_after_seconds)
        """
        now = time.time()
        cutoff = now - window_seconds

        with self._lock:
            bucket = self._events[key]

            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= limit:
                retry_after = max(1, int(bucket[0] + window_seconds - now))
                return False, retry_after

            bucket.append(now)
            return True, 0

    def reset(self):
        """Clear all buckets (used in tests)."""
        with self._lock:
            self._events.clear()


rate_limiter = InMemoryRateLimiter()
