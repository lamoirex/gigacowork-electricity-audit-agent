import json
import subprocess
import sys
from pathlib import Path

from tests._helpers import load_engine

ROOT = Path(__file__).resolve().parent.parent


def test_integration_against_expected(tmp_path):
    gen = ROOT / "testdata" / "generate.py"
    subprocess.run([sys.executable, str(gen)], cwd=ROOT, check=True, capture_output=True)
    out = ROOT / "testdata" / "out"
    cc = load_engine()
    decisions = cc.reconcile(
        cc.read_table(out / "charges.xlsx", "charges"),
        cc.read_table(out / "norms.xlsx", "norms"),
        cc.read_table(out / "stores.xlsx", "stores"),
    )
    expected = json.loads((out / "expected.json").read_text(encoding="utf-8"))
    by_row = {d.row: d for d in decisions}
    for e in expected:
        got = by_row[e["row"]]
        assert got.status == e["status"], (
            f"row {e['row']}: expected {e['status']}, got {got.status} ({got.reason})"
        )
