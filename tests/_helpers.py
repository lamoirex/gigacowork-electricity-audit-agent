from pathlib import Path
import importlib.util
import sys


def load_engine():
    p = (Path(__file__).resolve().parent.parent
         / "agent" / "skill" / "utility-check" / "scripts" / "check_charges.py")
    spec = importlib.util.spec_from_file_location("check_charges", str(p))
    m = importlib.util.module_from_spec(spec)
    sys.modules["check_charges"] = m
    spec.loader.exec_module(m)
    return m
