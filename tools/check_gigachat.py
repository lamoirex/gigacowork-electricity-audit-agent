import argparse
import json
import os
from pathlib import Path
from tempfile import mkdtemp
from time import perf_counter

from gigachat import GigaChat

LABELS = (
    ("checked", "Проверено"),
    ("ok", "В норме"),
    ("exceeded", "Превышений"),
    ("exceptions", "Исключений"),
    ("clarifications", "Уточнений"),
)


def verify_answer(answer, expected_line):
    lines = answer.strip().splitlines()
    if not lines or lines[0].strip() != expected_line:
        return False

    prefix = "Уведомление:"
    for index, line in enumerate(lines[1:], start=1):
        line = line.strip()
        if line.startswith(prefix):
            body = "\n".join([line[len(prefix) :], *lines[index + 1 :]])
            return bool(body.strip())

    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cli_log", type=Path, help="Лог прогона на синтетических данных")
    parser.add_argument("--model", default=os.getenv("GIGACHAT_MODEL", "GigaChat-2-Max"))
    args = parser.parse_args()

    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if not credentials:
        parser.error("Задайте GIGACHAT_CREDENTIALS в терминале.")

    raw = args.cli_log.read_text(encoding="utf-8")
    source, _ = json.JSONDecoder().raw_decode(raw.lstrip())
    summary = {key: source[key] for key, _ in LABELS}
    summary["reasons"] = source["reasons"]
    expected_line = " | ".join(f"{label}: {summary[key]}" for key, label in LABELS)
    prompt = (
        "Напиши сводку на русском. Первой строкой дословно выведи строку ниже, "
        "без Markdown и вступления. Затем поясни причины по JSON. "
        "Заверши строкой «Уведомление: ...» с черновиком для ответственного. "
        "Превышение является сигналом к проверке. Используй только данные JSON.\n\n"
        f"{expected_line}\n\n{json.dumps(summary, ensure_ascii=False)}"
    )

    runs = Path("runs")
    runs.mkdir(exist_ok=True)
    output = Path(mkdtemp(prefix="gigachat-", dir=runs))
    records = []

    with GigaChat(
        credentials=credentials,
        scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
        model=args.model,
        ca_bundle_file=os.getenv("GIGACHAT_CA_BUNDLE") or None,
        verify_ssl_certs=True,
        timeout=60,
    ) as client:
        for number in range(1, 4):
            started = perf_counter()
            response = client.chat(
                {"messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            )
            elapsed = round(perf_counter() - started, 3)
            answer = response.choices[0].message.content or ""
            passed = verify_answer(answer, expected_line)
            (output / f"response-{number}.txt").write_text(answer, encoding="utf-8")
            records.append(
                dict(run=number, model=response.model, api_seconds=elapsed, passed=passed)
            )
            print(f"#{number}: {'OK' if passed else 'FAIL'}, {elapsed:.3f} с")

    metrics = dict(input_summary=summary, expected_line=expected_line, runs=records)
    (output / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Ответы и метрики: {output}")
    return 0 if all(item["passed"] for item in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
