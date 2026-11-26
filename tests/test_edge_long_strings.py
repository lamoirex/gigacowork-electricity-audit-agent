from tests._helpers import load_engine


def test_very_long_id():
    cc = load_engine()
    long_id = "S" * 500
    assert cc.norm_id(long_id) == long_id.lower()


def test_very_long_reason():
    cc = load_engine()
    d = cc.reconcile(
        [{"__row__": 2, "store_id": "", "period": "", "consumption": None}],
        [],
        [],
    )[0]
    assert len(d.reason) < 500
