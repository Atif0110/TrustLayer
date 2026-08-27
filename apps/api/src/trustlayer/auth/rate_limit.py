from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
from time import monotonic


@dataclass(frozen=True)
class LimitRule:
    max_attempts: int
    window_seconds: int


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, rule: LimitRule) -> bool:
        now = monotonic()
        cutoff = now - rule.window_seconds
        with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= rule.max_attempts:
                return False
            bucket.append(now)
            return True


limiter = SlidingWindowRateLimiter()


SIGNUP_IP_RULE = LimitRule(max_attempts=10, window_seconds=10 * 60)
SIGNUP_EMAIL_RULE = LimitRule(max_attempts=5, window_seconds=10 * 60)
LOGIN_IP_RULE = LimitRule(max_attempts=20, window_seconds=10 * 60)
LOGIN_EMAIL_RULE = LimitRule(max_attempts=10, window_seconds=10 * 60)
