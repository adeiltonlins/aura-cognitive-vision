from __future__ import annotations

import time


class AdaptiveAttention:
    """Decides when the perception model should inspect another frame."""

    def __init__(self, min_interval: float = 0.5, max_interval: float = 3.0) -> None:
        self.min_interval = min_interval
        self.max_interval = max_interval
        self._last_analysis = 0.0
        self._interval = min_interval

    def should_analyze(self, change_score: float = 1.0) -> bool:
        now = time.monotonic()
        if now - self._last_analysis < self._interval:
            return False
        self._last_analysis = now
        self._interval = self._next_interval(change_score)
        return True

    def _next_interval(self, change_score: float) -> float:
        # More visual change -> inspect more frequently.
        if change_score >= 0.7:
            return self.min_interval
        if change_score <= 0.1:
            return self.max_interval
        span = self.max_interval - self.min_interval
        return self.max_interval - (span * change_score)
