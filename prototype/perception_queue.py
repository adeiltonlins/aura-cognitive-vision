from __future__ import annotations

from queue import Empty, Queue
from typing import Any


class PerceptionQueue:
    """Bounded queue that keeps the newest frames when perception is busy."""

    def __init__(self, maxsize: int = 2) -> None:
        self._queue: Queue[Any] = Queue(maxsize=maxsize)

    def put_latest(self, frame: Any) -> None:
        if self._queue.full():
            try:
                self._queue.get_nowait()
            except Empty:
                pass
        try:
            self._queue.put_nowait(frame)
        except Exception:
            pass

    def get(self, timeout: float | None = None) -> Any:
        return self._queue.get(timeout=timeout)
