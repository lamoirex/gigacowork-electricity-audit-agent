from tests._helpers import load_engine


def _minimal_ctx():
    cc = load_engine()
    stores = [{"store_id": "S01"}, {"store_id": "S02"}]
    norms = [
        {"store_id": "S01", "period": "2025-01", "norm_consumption": 1000,
         "norm_unit": "кВт·ч", "norm_amount": 5000, "version": 1,
         "valid_from": "2024-01-01"},
        {"store_id": "S01", "period": "2025-01", "norm_consumption": 900,
         "norm_unit": "кВт·ч", "norm_amount": 4500, "version": 2,
         "valid_from": "2025-01-01"},
    ]
    return cc, stores, norms


def _row(**kw):
    base = {"__row__": 2, "store_id": "S01", "period": "2025-01",
            "consumption": 1000, "amount_net": 5000, "unit": "кВт·ч",
            "doc_number": "D-1", "charge_type": "основное",
            "period_start": "2025-01-01", "period_end": "2025-01-31"}
    base.update(kw)
    return base


def test_rule_1_missing_id():
    cc, stores, norms = _minimal_ctx()
    d = cc.reconcile([_row(store_id="")], norms, stores)[0]
    assert d.rule == 1 and d.status == "требуется уточнение"


def test_rule_2_store_not_found():
    cc, stores, norms = _minimal_ctx()
    d = cc.reconcile([_row(store_id="S99")], norms, stores)[0]
    assert d.rule == 2


def test_rule_3_duplicate_keeps_first():
    cc, stores, norms = _minimal_ctx()
    ds = cc.reconcile([_row(), _row()], norms, stores)
    assert ds[0].rule == 8
    assert ds[1].rule == 3 and ds[1].status == "исключение: дубль"


def test_rule_4_recalc():
    cc, stores, norms = _minimal_ctx()
    d = cc.reconcile([_row(charge_type="Перерасчёт")], norms, stores)[0]
    assert d.rule == 4


def test_rule_5_partial_month():
    cc, stores, norms = _minimal_ctx()
    d = cc.reconcile([_row(period_start="2025-01-15")], norms, stores)[0]
    assert d.rule == 5


def test_rule_6_no_norm():
    cc, stores, norms = _minimal_ctx()
    d = cc.reconcile(
        [_row(period="2025-03", period_start="2025-03-01", period_end="2025-03-31")],
        norms, stores,
    )[0]
    assert d.rule == 6


def test_rule_7_units_mismatch():
    cc, stores, norms = _minimal_ctx()
    d = cc.reconcile([_row(unit="кВт")], norms, stores)[0]
    assert d.rule == 7


def test_rule_8_uses_latest_version():
    cc, stores, norms = _minimal_ctx()
    d = cc.reconcile([_row(consumption=1000, amount_net=5000)], norms, stores)[0]
    assert d.version == 2
    assert d.status == "превышение"
