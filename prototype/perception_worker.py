from __future__ import annotations

import threading
from typing import Any, Callable

from adaptive_attention import AdaptiveAttention
from perception_queue import PerceptionQueue


class PerceptionWorker:
    """Consumes the newest available frame without blocking camera capture."""

    def __init__(self, analyze: Callable[[Any], dict], max_queue: int = 2) -> None:
        self.queue = PerceptionQueue(maxsize=max_queue)
        self.attention = AdaptiveAttention()
        self.analyze = analyze
        self.latest_result: dict = {"status": "waiting"}
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def submit(self, frame: Any, change_score: float = 1.0) -> None:
        if self.attention.should_analyze(change_score):
            self.queue.put_latest(frame)

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                frame = self.queue.get(timeout=0.2)
            except Exception:
                continue
            try:
                self.latest_result = self.analyze(frame)
            except Exception as exc:
                self.latest_result = {"status": "error", "error": str(exc)}
