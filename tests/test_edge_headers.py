from tests._helpers import load_engine


def test_case_insensitive():
    assert load_engine().find_col(["ID Магазина"], ["ID магазина"]) == 0


def test_extra_spaces():
    assert load_engine().find_col(["  ID   Магазина "], ["ID магазина"]) == 0


def test_missing():
    assert load_engine().find_col(["Другое"], ["ID магазина"]) is None
