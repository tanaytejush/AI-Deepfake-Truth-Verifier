"""
Rate limiter backends (in-memory and Redis) with a shared interface.
"""

from collections import defaultdict, deque
from threading import Lock
import logging
import time
from typing import Tuple

from .config import settings

logger = logging.getLogger(__name__)


class BaseRateLimiter:
    """Shared limiter interface."""

    def check(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        raise NotImplementedError

    def reset(self):
        """Optional reset hook for tests."""
        return None


class InMemoryRateLimiter(BaseRateLimiter):
    """Thread-safe in-memory sliding-window rate limiter."""

    def __init__(self):
        self._events = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
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
        with self._lock:
            self._events.clear()


class RedisRateLimiter(BaseRateLimiter):
    """Redis-backed sliding-window limiter using sorted sets."""

    def __init__(self, redis_url: str):
        import redis

        self._client = redis.Redis.from_url(redis_url, decode_responses=True)
        self._client.ping()

    def check(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        now = time.time()
        cutoff = now - window_seconds

        pipe = self._client.pipeline()
        pipe.zremrangebyscore(key, 0, cutoff)
        pipe.zcard(key)
        _, count = pipe.execute()

        if int(count) >= limit:
            oldest = self._client.zrange(key, 0, 0, withscores=True)
            retry_after = 1
            if oldest:
                retry_after = max(1, int((oldest[0][1] + window_seconds) - now))
            return False, retry_after

        member = f"{now:.9f}"
        pipe = self._client.pipeline()
        pipe.zadd(key, {member: now})
        pipe.expire(key, window_seconds + 1)
        pipe.execute()
        return True, 0

    def reset(self):
        # No-op in production; tests typically use in-memory backend.
        return None


def build_rate_limiter() -> BaseRateLimiter:
    """
    Build a limiter using configured backend.
    Falls back to in-memory on Redis errors to avoid outage.
    """
    backend = settings.RATE_LIMIT_BACKEND.strip().lower()
    if backend == "redis":
        try:
            logger.info("Using Redis-backed rate limiter")
            return RedisRateLimiter(settings.REDIS_URL)
        except Exception as error:
            logger.warning(f"Redis limiter unavailable, falling back to memory: {error}")

    logger.info("Using in-memory rate limiter")
    return InMemoryRateLimiter()


rate_limiter = build_rate_limiter()
