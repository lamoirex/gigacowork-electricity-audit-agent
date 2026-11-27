"""Three attached XLSX files -> local skill -> GigaChat -> workbook and chat response."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from time import perf_counter

from check_gigachat import LABELS
from gigachat import GigaChat
from summary_layout import matches_summary

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "agent/skill/utility-check/scripts/check_charges.py"


def run_agent(files, target):
    target.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    cli = subprocess.run(
        [sys.executable, str(SKILL), *map(str, files), str(target)],
        capture_output=True,
        text=True,
        check=True,
    )
    summary = json.loads(cli.stdout)
    xlsx = Path(summary.pop("xlsx"))
    if not xlsx.is_file():
        raise FileNotFoundError(xlsx)
    first = " | ".join(f"{label}: {summary[key]}" for key, label in LABELS)
    reasons = ", ".join(f"{label} ({count})" for label, count in summary["reason_counts"].items())
    template = f"{first}\nПричины: {reasons or 'нет'}.\nУведомление: {summary['notification']}"
    model = os.environ.get("GIGACHAT_MODEL", "GigaChat-2-Max")
    api_start = perf_counter()
    with GigaChat(
        credentials=os.environ["GIGACHAT_CREDENTIALS"],
        model=model,
        scope=os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
        ca_bundle_file=os.environ.get("GIGACHAT_CA_BUNDLE") or None,
        verify_ssl_certs=True,
        timeout=60,
    ) as client:
        response = client.chat(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Верни готовую сводку тремя строками дословно, без Markdown.\n\n"
                        + template,
                    }
                ],
                "temperature": 0.1,
            }
        )
    answer = response.choices[0].message.content or ""
    api_seconds = perf_counter() - api_start
    (target / "response.txt").write_text(answer, encoding="utf-8")
    elapsed = perf_counter() - started
    record = dict(
        model=response.model,
        api_seconds=round(api_seconds, 3),
        total_seconds=round(elapsed, 3),
        summary=summary,
        answer=answer,
        chat_ok=matches_summary(answer, template),
    )
    (target / "agent.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", type=Path, nargs=3, metavar="XLSX")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = run_agent(args.files, args.output)
    print(result["answer"])
    print(args.output / "reconciliation.xlsx")
