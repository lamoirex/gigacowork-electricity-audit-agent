"""Generate a submission and record measurements, including failed checks."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile

from acceptance_pdf import render
from field_metrics import evaluate
from run_control import CLI, INPUTS, ROOT, workbook_signature


def python(*args):
    return subprocess.check_output([sys.executable, *map(str, args)], cwd=ROOT, text=True)


def replay_record(dest, files, oracle, original_revision):
    """Read the original API evidence and verify its input fingerprint."""
    from check_gigachat import LABELS
    from summary_layout import matches_summary

    original_runner = subprocess.check_output(
        ["git", "show", f"{original_revision}:tools/run_agent.py"], cwd=ROOT
    )
    digest = hashlib.sha256()
    for path in [*files, oracle, CLI]:
        digest.update(path.read_bytes())
    digest.update(original_runner)
    if digest.hexdigest() != (dest / "inputs.sha256").read_text().strip():
        raise ValueError(f"Исходные данные или версия скрипта изменились: {dest}")

    record = json.loads((dest / "agent.json").read_text())
    answer = (dest / "response.txt").read_text()
    if answer != record["answer"]:
        raise ValueError(f"Сохранённый ответ отличается от agent.json: {dest}")

    summary = record["summary"]
    first = " | ".join(f"{label}: {summary[key]}" for key, label in LABELS)
    reasons = ", ".join(f"{label} ({count})" for label, count in summary["reason_counts"].items())
    template = f"{first}\nПричины: {reasons or 'нет'}.\nУведомление: {summary['notification']}"
    return {
        **record,
        "original_chat_ok": record["chat_ok"],
        "chat_ok": matches_summary(answer, template),
    }


def execute(offline, session, out, replay_revision=None):
    session.mkdir(parents=True, exist_ok=True)
    mode = "Python CLI" if offline else "Python + GigaChat API"
    pointer = session / "control.txt"
    if not pointer.exists():
        log = python("tools/run_control.py")
        print(log, flush=True)
        pointer.write_text(log.split("Метрики и логи: ")[-1].strip())
    control = ROOT / pointer.read_text().strip()
    local = json.loads((control / "metrics.json").read_text())
    runs = []
    ok = True
    for name, folder, suffix, oracle in [
        ("base", INPUTS, "", INPUTS / "expected.json"),
        ("foreign", INPUTS / "foreign", "_foreign", control / "expected_foreign.json"),
        ("extended", INPUTS / "extended", "", INPUTS / "extended/expected.json"),
    ]:
        files = [folder / (role + suffix + ".xlsx") for role in ("charges", "norms", "stores")]
        expected = json.loads(oracle.read_text())
        for i in range(1, 4):
            dest = control / name / str(i)
            result = dict(dataset=name, repeat=i, mode=mode)
            if offline:
                summary, _ = json.JSONDecoder().raw_decode((dest / "run.log").read_text().lstrip())
                summary.pop("xlsx", None)
                result.update(
                    seconds=local[name]["runs"][i - 1]["seconds"],
                    transcript=json.dumps(summary, ensure_ascii=False, indent=2),
                )
            else:
                from run_agent import run_agent

                dest = session / name / str(i)
                cache = dest / "agent.json"
                fingerprint = hashlib.sha256(
                    b"".join(
                        p.read_bytes() for p in [*files, oracle, CLI, ROOT / "tools/run_agent.py"]
                    )
                ).hexdigest()
                stamp = dest / "inputs.sha256"
                if replay_revision:
                    record = replay_record(dest, files, oracle, replay_revision)
                    result["original_chat_ok"] = record["original_chat_ok"]
                    result["replay_revision"] = replay_revision
                elif cache.exists() and stamp.exists() and stamp.read_text() == fingerprint:
                    record = json.loads(cache.read_text())
                else:
                    record = run_agent(files, dest)
                    stamp.write_text(fingerprint)
                summary = record["summary"]
                result.update(
                    seconds=record["total_seconds"],
                    api_seconds=record["api_seconds"],
                    model=record["model"],
                    chat_ok=record["chat_ok"],
                    transcript=record["answer"],
                )
            book = dest / "reconciliation.xlsx"
            fields = evaluate(name, book, files[0], oracle)
            signature, shape = workbook_signature(
                book, len(expected), sum(e["rule"] != 8 for e in expected)
            )
            statuses = Counter(e["status"] for e in expected)
            counters = dict(
                checked=len(expected),
                ok=statuses["в норме"],
                exceeded=statuses["превышение"],
                clarifications=statuses["требуется уточнение"],
                exceptions=sum(v for k, v in statuses.items() if k.startswith("исключение")),
            )
            result["counts_ok"] = all(summary[k] == v for k, v in counters.items())
            result.update(fields=fields, sha256=signature)
            result["passed"] = (
                result["counts_ok"]
                and shape
                and fields["shape"]
                and fields["schema"]
                and fields["exact"] / fields["rows"] >= 0.95
                and fields["substitutions"] == 0
                and result.get("chat_ok", True)
                and (offline or result["seconds"] <= 60)
            )
            runs.append(result)
            ok &= result["passed"]
            print(
                f"{name} #{i}: {fields['exact']}/{fields['rows']}, {result['seconds']} с, "
                f"{'OK' if result['passed'] else 'FAIL'}",
                flush=True,
            )
            if name == "base" and i == 1:
                example = book
        ok &= len({r["sha256"] for r in runs if r["dataset"] == name}) == 1
    out.mkdir(exist_ok=True)
    python("build_skill.py")
    for filename in ("agent.zip", "testdata.zip"):
        with ZipFile(ROOT / "dist" / filename) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"Повреждён {filename}")
        shutil.copy2(ROOT / "dist" / filename, out / filename)
    shutil.copy2(example, out / "reconciliation.xlsx")
    (out / "metrics.json").write_text(
        json.dumps(dict(passed=ok, runs=runs), ensure_ascii=False, indent=2) + "\n"
    )
    (out / "run-1.txt").write_text(runs[0]["transcript"] + "\n")
    render(ROOT, out / "report.pdf", runs)
    print(f"Материалы: {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--session", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "submission")
    parser.add_argument("--replay-revision", help="Версия исходного API-прогона")
    args = parser.parse_args()
    if args.replay_revision and (args.offline or args.session is None):
        parser.error("--replay-revision требует --session и режима API")
    (ROOT / "runs").mkdir(exist_ok=True)
    session = args.session or Path(mkdtemp(prefix="acceptance-", dir=ROOT / "runs"))
    sys.exit(execute(args.offline, session, args.output, args.replay_revision))
