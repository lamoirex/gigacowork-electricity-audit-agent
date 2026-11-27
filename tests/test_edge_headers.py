from tests._helpers import load_engine


def test_case_insensitive():
    assert load_engine().find_col(["ID Магазина"], ["ID магазина"]) == 0


def test_extra_spaces():
    assert load_engine().find_col(["  ID   Магазина "], ["ID магазина"]) == 0


def test_missing():
    assert load_engine().find_col(["Другое"], ["ID магазина"]) is None


def test_inactive_sheet_and_source_row(tmp_path):
    from openpyxl import Workbook

    book = Workbook()
    book.active.append(["Лист согласования"])
    data = book.create_sheet("Март")
    data.append(["Отчёт за март"])
    data.append(["код тт"])
    data.append(["0021"])
    path = tmp_path / "stores.xlsx"
    book.save(path)
    rows = load_engine().read_table(path, "stores", validate_headers=True)
    assert [(r["__row__"], r["store_id"]) for r in rows] == [(3, "0021")]
