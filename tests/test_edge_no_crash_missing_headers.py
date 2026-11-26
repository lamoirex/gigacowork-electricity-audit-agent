from tests._helpers import load_engine


def test_missing_period_column():
    cc = load_engine()
    d = cc.reconcile(
        [
            {
                "__row__": 2,
                "store_id": "S1",
                "period": None,
                "consumption": 100,
                "amount_net": 500,
                "unit": "кВт·ч",
                "doc_number": "D",
                "charge_type": "основное",
                "period_start": None,
                "period_end": None,
            }
        ],
        [],
        [{"store_id": "S1"}],
    )[0]
    assert d.rule == 1


def test_missing_consumption_column():
    cc = load_engine()
    d = cc.reconcile(
        [
            {
                "__row__": 2,
                "store_id": "S1",
                "period": "2025-01",
                "consumption": None,
                "amount_net": 500,
                "unit": "кВт·ч",
                "doc_number": "D",
                "charge_type": "основное",
                "period_start": "2025-01-01",
                "period_end": "2025-01-31",
            }
        ],
        [],
        [{"store_id": "S1"}],
    )[0]
    assert d.rule == 1
