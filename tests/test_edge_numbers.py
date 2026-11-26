from tests._helpers import load_engine


def test_large():
    assert load_engine().to_float("9" * 10) == 9999999999.0


def test_negative():
    assert load_engine().to_float("-500") == -500.0


def test_scientific():
    assert load_engine().to_float("1e3") == 1000.0


def test_none_and_empty():
    cc = load_engine()
    assert cc.to_float(None) is None
    assert cc.to_float("") is None
