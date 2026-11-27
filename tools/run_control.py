import hashlib
import json
import subprocess
import sys
from pathlib import Path
from tempfile import mkdtemp
from time import perf_counter

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "agent/skill/utility-check/scripts/check_charges.py"
INPUTS = ROOT / "testdata/out"
ROLES = ("charges", "norms", "stores")
SHEETS = ["Отклонения", "Реестр исключений", "Журнал решений"]


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def generate(script):
    result = run(script)
    if result.returncode:
        raise SystemExit(result.stderr or result.stdout)


def workbook_signature(path, rows, exceptions):
    book = load_workbook(path, read_only=True)
    try:
        if book.sheetnames != SHEETS:
            raise ValueError(f"Неожиданные листы: {book.sheetnames}")
        values = [list(book[name].values) for name in SHEETS]
        shape_ok = (
            len(values[0]) == len(values[2]) == rows + 1
            and len(values[1]) == exceptions + 1
            and len(values[0][0]) == 13
        )
        serialized = json.dumps(values, ensure_ascii=False, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest(), shape_ok
    finally:
        book.close()


def main():
    generate(ROOT / "testdata/generate.py")
    generate(ROOT / "testdata/scenarios/foreign_format.py")
    (ROOT / "runs").mkdir(exist_ok=True)
    output = Path(mkdtemp(prefix="control-", dir=ROOT / "runs"))

    foreign_oracle = output / "expected_foreign.json"
    foreign_rows = [
        dict(row=2, status="в норме", dev_kwh=0, dev_rub=0, dev_kwh_pct=0, dev_rub_pct=0),
        dict(row=3, status="превышение", dev_kwh=200, dev_rub=1000, dev_kwh_pct=20, dev_rub_pct=20),
    ]
    for row in foreign_rows:
        row.update(rule=8, norm=1000, sum=5000, version=1)
    foreign_oracle.write_text(json.dumps(foreign_rows, ensure_ascii=False), encoding="utf-8")

    datasets = (
        ("base", INPUTS, "", INPUTS / "expected.json"),
        ("foreign", INPUTS / "foreign", "_foreign", foreign_oracle),
    )
    report = {}
    passed = True
    for name, folder, suffix, oracle in datasets:
        expected = json.loads(oracle.read_text(encoding="utf-8"))
        exceptions = sum(row["rule"] != 8 for row in expected)
        inputs = [folder / f"{role}{suffix}.xlsx" for role in ROLES]
        runs = []
        for number in range(1, 4):
            target = output / name / str(number)
            target.mkdir(parents=True)
            started = perf_counter()
            result = run(CLI, *inputs, target)
            seconds = perf_counter() - started
            log = result.stdout + result.stderr
            signature = None
            ok = False
            if result.returncode == 0:
                xlsx = target / "reconciliation.xlsx"
                checked = run(ROOT / "tools/evaluate.py", xlsx, oracle)
                log += checked.stdout + checked.stderr
                signature, shape_ok = workbook_signature(xlsx, len(expected), exceptions)
                ok = checked.returncode == 0 and shape_ok
            (target / "run.log").write_text(log, encoding="utf-8")
            runs.append(dict(run=number, seconds=round(seconds, 4), passed=ok, sha256=signature))
            print(f"{name} #{number}: {'OK' if ok else 'FAIL'}, {seconds:.3f} c")
        hashes = {item["sha256"] for item in runs}
        stable = len(hashes) == 1 and None not in hashes
        report[name] = dict(rows_per_run=len(expected), stable=stable, runs=runs)
        passed = passed and stable and all(item["passed"] for item in runs)
    (output / "metrics.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Метрики и логи: {output.relative_to(ROOT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
