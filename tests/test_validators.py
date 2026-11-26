import importlib.util
from pathlib import Path

import pytest


def _load():
    p = (
        Path(__file__).resolve().parent.parent
        / "agent"
        / "skill"
        / "utility-check"
        / "scripts"
        / "validators.py"
    )
    spec = importlib.util.spec_from_file_location("validators", str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_missing_file():
    m = _load()
    with pytest.raises(m.ValidationError):
        m.validate_file(Path("/nope.xlsx"), "charges")


def test_wrong_extension(tmp_path):
    m = _load()
    p = tmp_path / "x.csv"
    p.write_text("")
    with pytest.raises(m.ValidationError):
        m.validate_file(p, "charges")
