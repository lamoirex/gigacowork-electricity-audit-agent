"""Negative and zero consumption."""

from pathlib import Path

import openpyxl


def generate(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(
        [
            "ID магазина",
            "Период",
            "Потребление",
            "Единица измерения",
            "Сумма без НДС",
            "Номер документа",
            "Тип начисления",
            "Начало периода",
            "Конец периода",
        ]
    )
    ws.append(
        ["S01", "2025-01", -50, "кВт·ч", -250, "D-1", "перерасчёт", "2025-01-01", "2025-01-31"]
    )
    ws.append(["S02", "2025-01", 0, "кВт·ч", 0, "D-2", "основное", "2025-01-01", "2025-01-31"])
    wb.save(out / "negative.xlsx")


if __name__ == "__main__":
    generate(Path(__file__).parent.parent / "out")
