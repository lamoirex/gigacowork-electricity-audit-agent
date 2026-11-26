from tests._helpers import load_engine


def test_cyrillic_store_id():
    cc = load_engine()
    assert cc.norm_id("МАГАЗИН-1") == cc.norm_id("магазин 1")


def test_comma_decimals():
    assert load_engine().to_float("1 000,50") == 1000.5
