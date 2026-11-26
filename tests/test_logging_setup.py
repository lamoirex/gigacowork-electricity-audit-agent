import importlib.util
from pathlib import Path


def _load():
    p = (
        Path(__file__).resolve().parent.parent
        / "agent"
        / "skill"
        / "utility-check"
        / "scripts"
        / "logging_setup.py"
    )
    spec = importlib.util.spec_from_file_location("logging_setup", str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_configure_returns_logger():
    m = _load()
    log = m.configure("DEBUG")
    assert log.name == "utility_check"


def test_configure_idempotent():
    m = _load()
    a = m.configure("INFO")
    b = m.configure("DEBUG")
    assert a is b
