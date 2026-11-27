"""Independent acceptance checks for the three labelled synthetic datasets."""

import json
from pathlib import Path

from openpyxl import load_workbook

COLUMNS = (
    "ID магазина|Период|Потребление, кВт·ч|Начислено без НДС, руб.|Норматив, кВт·ч|"
    "Норматив, руб.|Версия норматива|Отклонение, кВт·ч|Отклонение, % (кВт·ч)|"
    "Отклонение, руб.|Отклонение, % (руб.)|Статус|Обоснование"
).split("|")
SCHEMA = {
    "Отклонения": COLUMNS,
    "Реестр исключений": ["Строка", "ID магазина", "Период", "Статус", "Причина", "Действие"],
    "Журнал решений": ["Строка", "Правило", "Статус", "Основание"],
}
FIELDS = ("norm", "sum", "version", "dev_kwh", "dev_kwh_pct", "dev_rub", "dev_rub_pct")
SOURCE = {"base": (0, 3, 8, 11), "foreign": (2, 1, 5, 7), "extended": (0, 1, 6, 8)}


def sheets(file):
    book = load_workbook(file, read_only=True)
    try:
        return {ws.title: list(ws.values) for ws in book.worksheets}
    finally:
        book.close()


def reason_matches(reason, e, source):
    text = str(reason or "").lower()
    rule = e["rule"]
    if rule == 1:
        labels = ["id магазина", "периода", "потребления"]
        return text == "нет " + ", ".join(
            k for k, v in zip(labels, source[:3], strict=True) if v is None
        )
    if rule == 8:
        pct = [
            f"{float(e[k])}%" if e[k] is not None else "н/д" for k in ("dev_kwh_pct", "dev_rub_pct")
        ]
        expected = (
            f"факт {float(source[2])} кВт·ч / {float(source[3])} руб. vs норматив "
            f"{float(e['norm'])} кВт·ч / {float(e['sum'])} руб.; откл. {pct[0]} / {pct[1]}"
        )
        if e["norm"] == 0 or e["sum"] == 0:
            expected += " (Факт положительный при нулевом нормативе)"
        return text == expected.lower()
    phrases = {
        2: "магазин не найден в справочнике",
        3: "повтор строки (магазин+период+документ+тип)",
        4: "с нормативом не сравнивается",
        5: "даты периода не покрывают календарный месяц или не совпадают с ним",
        6: "нет норматива",
        7: "несовпадение единиц: 'квт·ч' vs 'квт'",
    }
    return text == phrases[rule]


def evaluate(name, xlsx, charges, oracle):
    expected = json.loads(Path(oracle).read_text(encoding="utf-8"))
    source_rows = next(iter(sheets(charges).values()))
    tabs = sheets(xlsx)
    schema = list(tabs) == list(SCHEMA) and all(
        tabs[k] and list(tabs[k][0]) == cols for k, cols in SCHEMA.items()
    )
    dev, registry, log = (tabs.get(k, [])[1:] for k in SCHEMA)
    registry_rows = [e["row"] for e in expected if e["rule"] != 8]
    shape = (
        len(dev) == len(log) == len(expected)
        and [r[0] for r in registry] == registry_rows
        and [r[0] for r in log] == [e["row"] for e in expected]
    )
    reg = {r[0]: r for r in registry}
    correct = dict.fromkeys([*COLUMNS, "Правило", "Реестр", "Журнал"], 0)
    exact = substitutions = 0
    for index, e in enumerate(expected):
        src = [source_rows[e["row"] - 1][i] for i in SOURCE[name]]
        src[0] = str(src[0]).strip() if src[0] is not None else None
        if src[1] == "2025-13":
            src[1] = None
        values = [*src, *(e.get(k) for k in FIELDS), e["status"]]
        if index >= len(dev) or len(dev[index]) != 13 or index >= len(log):
            continue
        row, journal = dev[index], log[index]
        checks = [v == a for v, a in zip(values, row[:12], strict=True)]
        substitutions += sum(
            v is None and a is not None for v, a in zip(values[:11], row[:11], strict=True)
        )
        reason = reason_matches(row[-1], e, src)
        item = reg.get(e["row"])
        registry_ok = (
            item is None
            if e["rule"] == 8
            else item
            == (
                e["row"],
                src[0],
                src[1],
                e["status"],
                row[-1],
                "уточнить данные" if e["status"] == "требуется уточнение" else "проверить вручную",
            )
        )
        checks.extend(
            [
                reason,
                journal[1] == e["rule"],
                registry_ok,
                journal == (e["row"], e["rule"], e["status"], row[-1]),
            ]
        )
        for key, passed in zip(correct, checks, strict=True):
            correct[key] += int(passed)
        exact += int(all(checks))
    return dict(
        rows=len(expected),
        exact=exact,
        correct_by_field=correct,
        substitutions=substitutions,
        schema=schema,
        shape=shape,
    )
