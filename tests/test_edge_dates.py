from datetime import date
from tests._helpers import load_engine


def test_period_iso():
    assert load_engine().period_key("2025-01") == "2025-01"


def test_period_eu():
    assert load_engine().period_key("01.2025") == "2025-01"


def test_period_date_object():
    assert load_engine().period_key(date(2025, 3, 1)) == "2025-03"


def test_to_date_variants():
    cc = load_engine()
    assert cc.to_date("2025-01-15") == date(2025, 1, 15)
    assert cc.to_date("15.01.2025") == date(2025, 1, 15)
    assert cc.to_date("не дата") is None
