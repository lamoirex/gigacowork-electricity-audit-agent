from tests._helpers import load_engine


def test_norm_header_case_and_space():
    cc = load_engine()
    assert cc.norm_header("  ID  Магазина ") == "id магазина"


def test_norm_id_strip_zeros_and_case():
    cc = load_engine()
    assert cc.norm_id("007") == "7"
    assert cc.norm_id(" S-01 ") == "s01"
    assert cc.norm_id(None) == ""


def test_to_float_comma():
    cc = load_engine()
    assert cc.to_float("1 234,5") == 1234.5
    assert cc.to_float("") is None


def test_period_key_variants():
    cc = load_engine()
    assert cc.period_key("2025-01") == "2025-01"
    assert cc.period_key("01.2025") == "2025-01"
    assert cc.period_key("") is None
