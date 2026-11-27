"""Simulate a completely different customer Excel format."""
from datetime import date
from pathlib import Path

import openpyxl


def generate(out: Path):
    out.mkdir(parents=True, exist_ok=True)

    # 1. Stores
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "СПИСОК_ТТ"
    ws.append(["СЧЁТЧИК", "ЛИЦЕВОЙ СЧЁТ", "КОД ТТ", "НАЗВАНИЕ", "РЕЖИМ"])
    ws.append(["M-1", "ЛС-001", "S01", "ТЦ-1", "10-22"])
    ws.append(["M-2", "ЛС-002", "S02", "ТЦ-2", "09-21"])
    wb.save(out / "stores_foreign.xlsx")

    # 2. Norms
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "НОРМАТИВЫ_2025"
    headers = [
        "КОД ТТ", "МЕСЯЦ", "НОРМАТИВ_КВТЧ", "ЕД_ИЗМ",
        "НОРМАТИВ_РУБ", "ВЕРСИЯ", "ДЕЙСТВУЕТ_С"
    ]
    ws.append(headers)
    ws.append(["S01", "2025-01", 1000, "кВт·ч", 5000, 1, "2024-01-01"])
    ws.append(["S02", "2025-01", 1000, "кВт·ч", 5000, 1, "2024-01-01"])
    wb.save(out / "norms_foreign.xlsx")

    # 3. Charges
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ВЫГРУЗКА_СЧЕТОВ"
    headers = [
        "ТИП_НАЧИСЛЕНИЯ", "ПЕРИОД", "КОД ТТ", "ДАТА_НАЧ", "ДАТА_КОН",
        "ПОТРЕБЛЕНИЕ", "ЕД_ИЗМ", "СУММА_БЕЗ_НДС", "НДС",
        "СУММА_С_НДС", "НОМЕР_ДОК", "ЛИШНЯЯ_КОЛОНКА_1", "ЛИШНЯЯ_КОЛОНКА_2"
    ]
    ws.append(headers)
    ws.append([
        "основное", "2025-01", "S01", date(2025, 1, 1), date(2025, 1, 31),
        1000, "кВт·ч", 5000, 1000, 6000, "D-001", "x", "y"
    ])
    ws.append([
        "основное", "2025-01", "S02", date(2025, 1, 1), date(2025, 1, 31),
        1200, "кВт·ч", 6000, 1200, 7200, "D-002", "x", "y"
    ])
    wb.save(out / "charges_foreign.xlsx")


if __name__ == "__main__":
    generate(Path(__file__).parent.parent / "out" / "foreign")
