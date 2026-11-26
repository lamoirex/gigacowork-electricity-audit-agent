import openpyxl

from tests._helpers import load_engine


def test_empty_charges_returns_empty(tmp_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID магазина", "Период", "Потребление"])
    p = tmp_path / "c.xlsx"
    wb.save(p)
    assert load_engine().read_table(p, "charges") == []
