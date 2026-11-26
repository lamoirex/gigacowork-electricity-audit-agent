"""Unicode stores."""

from pathlib import Path

import openpyxl


def generate(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID магазина", "Название", "Лицевой счёт", "Счётчик"])
    for r in [
        ["S01", "Магазин №1 Ёлка", "ЛС-001", "M-1"],
        ["S02", "Cafe & Co", "ЛС-002", "M-2"],
        ["S03", "ТЦ Маяк", "ЛС-003", "M-3"],
    ]:
        ws.append(r)
    wb.save(out / "unicode_stores.xlsx")


if __name__ == "__main__":
    generate(Path(__file__).parent.parent / "out")
