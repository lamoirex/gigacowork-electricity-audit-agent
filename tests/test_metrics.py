import importlib.util
import time
from pathlib import Path


def _load():
    p = (Path(__file__).resolve().parent.parent
         / "agent" / "skill" / "utility-check" / "scripts" / "metrics.py")
    spec = importlib.util.spec_from_file_location("metrics", str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_incr():
    met = _load().Metrics()
    met.incr("x")
    met.incr("x", 2)
    assert met.counters["x"] == 3


def test_timer_observes():
    met = _load().Metrics()
    with met.timer("work"):
        time.sleep(0.01)
    assert met.timings["work"] >= 0.01


def test_snapshot():
    met = _load().Metrics()
    met.incr("a")
    s = met.snapshot()
    assert s["counters"]["a"] == 1
