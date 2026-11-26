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


def load_deviations(xlsx: Path) -> dict:
    wb = load_workbook(xlsx)
    ws = wb["Отклонения"]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    return {i + 2: {
        "norm_cons": r[4], "norm_amt": r[5],
        "dev_kwh": r[7], "dev_rub": r[9]
    } for i, r in enumerate(rows)}


def main(result_xlsx: str, expected_json: str) -> int:
    actual_log = load_actual(Path(result_xlsx))
    actual_dev = load_deviations(Path(result_xlsx))
    expected = json.loads(Path(expected_json).read_text(encoding="utf-8"))
    ok = 0
    total = len(expected)
    mismatches = []
    for e in expected:
        a_log = actual_log.get(e["row"], {})
        a_dev = actual_dev.get(e["row"], {})

        match = (a_log.get("status") == e["status"] and a_log.get("rule") == e["rule"])
        if "norm" in e:
            match = match and (a_dev.get("norm_cons") == e["norm"])
            match = match and (a_dev.get("norm_amt") == e["sum"])
        if "dev_kwh" in e:
            match = match and (a_dev.get("dev_kwh") == e["dev_kwh"])
            match = match and (a_dev.get("dev_rub") == e["dev_rub"])

        if match:
            ok += 1
        else:
            mismatches.append(e["row"])

    for row in mismatches:
        print(f"  mismatch at row {row}")
    print(f"accuracy: {ok}/{total} = {ok / total * 100:.2f}%")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
