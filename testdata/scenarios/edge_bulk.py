"""100-row bulk dataset."""

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
    for i in range(100):
        ws.append(
            [
                f"S{i % 10:02d}",
                "2025-01",
                1000 + i,
                "кВт·ч",
                5000 + i * 10,
                f"D-{i:03d}",
                "основное",
                "2025-01-01",
                "2025-01-31",
            ]
        )
    wb.save(out / "bulk_100.xlsx")


if __name__ == "__main__":
    generate(Path(__file__).parent.parent / "out")
