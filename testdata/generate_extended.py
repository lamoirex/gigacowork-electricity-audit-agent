import calendar
import json
from datetime import date
from pathlib import Path

from generate import write

OUT = Path(__file__).resolve().parent / "out" / "extended"
ENERGY = "кВт·ч"
QUESTION = "требуется уточнение"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stores, norms, charges, expected = [], [], [], []

    for i in range(1, 11):
        sid = f"X{i:02d}"
        month = 1 + (i - 1) % 3
        period = f"2024-{month:02d}"
        start = date(2024, month, 1)
        end = date(2024, month, calendar.monthrange(2024, month)[1])
        future = date(2024, month, 15)
        kwh, rub = 1000 * i, 5000 * i
        stores.append([sid])
        norms.extend(
            [
                [sid, period, kwh * 2, ENERGY, rub * 2, 1, date(2023, 12, 1)],
                [sid, period, kwh, ENERGY, rub, 2, start],
                [sid, period, kwh * 3, ENERGY, rub * 3, 3, future],
                [sid, "2024-04", kwh, ENERGY, rub, 1, date(2024, 4, 2)],
            ]
        )

        # Статусы, номера правил и версия заданы независимо от движка.
        cases = [
            ("equal", 8, "в норме", {}),
            ("at-limit", 8, "в норме", {"consumption": kwh * 11 // 10}),
            ("rub-only", 8, "превышение", {"amount": rub * 6 // 5}),
            ("kwh-only", 8, "превышение", {"consumption": kwh * 6 // 5}),
            ("recalc", 4, "исключение: перерасчёт", {"kind": "перерасчёт", "consumption": -i}),
            ("recalc", 3, "исключение: дубль", {"kind": "перерасчёт", "consumption": -i}),
            (
                "partial",
                5,
                "исключение: неполный месяц",
                {"start": date(2024, month, 2), "unit": "кВт"},
            ),
            ("missing", 1, QUESTION, {"store": "X999", "consumption": None}),
            (
                "future-only",
                6,
                QUESTION,
                {"period": "2024-04", "start": date(2024, 4, 1), "end": date(2024, 4, 30)},
            ),
        ]
        for label, rule, status, changes in cases:
            values = dict(
                store=sid,
                period=period,
                start=start,
                end=end,
                document=f"{sid}-{label}",
                kind="основное",
                consumption=kwh,
                unit=ENERGY,
                amount=rub,
            )
            values.update(changes)
            charges.append(list(values.values()))
            record = dict(row=len(charges) + 1, case=label, rule=rule, status=status)
            if rule == 8:
                dk = values["consumption"] - kwh
                dr = values["amount"] - rub
                record.update(
                    norm=kwh,
                    sum=rub,
                    version=2,
                    dev_kwh=dk,
                    dev_rub=dr,
                    dev_kwh_pct=round(dk * 100 / kwh, 2),
                    dev_rub_pct=round(dr * 100 / rub, 2),
                )
            expected.append(record)

    write(OUT / "stores.xlsx", ["ID магазина"], stores)
    write(
        OUT / "norms.xlsx",
        [
            "ID магазина",
            "Период",
            "Норматив потребления",
            "Единица измерения",
            "Норматив суммы",
            "Версия",
            "Действует с",
        ],
        norms,
    )
    write(
        OUT / "charges.xlsx",
        [
            "ID магазина",
            "Период",
            "Начало периода",
            "Конец периода",
            "Номер документа",
            "Тип начисления",
            "Потребление",
            "Единица измерения",
            "Сумма без НДС",
        ],
        charges,
    )
    (OUT / "expected.json").write_text(
        json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
