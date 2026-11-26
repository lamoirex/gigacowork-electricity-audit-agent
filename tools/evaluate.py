#!/usr/bin/env python3
"""Compare reconciliation.xlsx against expected.json."""
import json
import sys
from pathlib import Path

from openpyxl import load_workbook


def load_actual(xlsx: Path) -> dict:
    wb = load_workbook(xlsx)
    ws = wb["Журнал решений"]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    return {r[0]: {"rule": r[1], "status": r[2], "reason": r[3]} for r in rows}


def main(result_xlsx: str, expected_json: str) -> int:
    actual = load_actual(Path(result_xlsx))
    expected = json.loads(Path(expected_json).read_text(encoding="utf-8"))
    ok = 0
    total = len(expected)
    mismatches = []
    for e in expected:
        a = actual.get(e["row"], {})
        if a.get("status") == e["status"] and a.get("rule") == e["rule"]:
            ok += 1
        else:
            mismatches.append((e["row"], e["status"], a.get("status")))
    for row, exp, got in mismatches:
        print(f"  row {row}: expected {exp}, got {got}")
    print(f"accuracy: {ok}/{total} = {ok / total * 100:.2f}%")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
