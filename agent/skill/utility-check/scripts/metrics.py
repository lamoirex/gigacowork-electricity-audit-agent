"""Simple metrics collector."""

import time
from contextlib import contextmanager


class Metrics:
    def __init__(self):
        self.counters: dict[str, int] = {}
        self.timings: dict[str, float] = {}

    def incr(self, key: str, by: int = 1) -> None:
        self.counters[key] = self.counters.get(key, 0) + by

    def observe(self, key: str, seconds: float) -> None:
        self.timings[key] = self.timings.get(key, 0.0) + seconds

    @contextmanager
    def timer(self, key: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            self.observe(key, time.perf_counter() - start)

    def snapshot(self) -> dict:
        return {"counters": dict(self.counters), "timings": dict(self.timings)}
