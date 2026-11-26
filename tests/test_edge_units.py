from tests._helpers import load_engine


def test_kwh_variants_equivalent_after_lower():
    cc = load_engine()
    assert cc.norm_header("кВт·ч") == cc.norm_header("кВт·Ч")


def test_kw_not_kwh():
    cc = load_engine()
    assert cc.norm_header("кВт") != cc.norm_header("кВт·ч")
