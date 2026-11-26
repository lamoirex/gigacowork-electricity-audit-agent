"""Mixed ID spellings."""

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
    for i, sid in enumerate(["S01", "s01", "S-01", " S01 ", "007", "7"]):
        ws.append(
            [sid, "2025-01", 100, "кВт·ч", 500, f"D-{i}", "основное", "2025-01-01", "2025-01-31"]
        )
    wb.save(out / "mixed_ids.xlsx")


if __name__ == "__main__":
    generate(Path(__file__).parent.parent / "out")
