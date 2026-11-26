from tests._helpers import load_engine


def test_missing_field_in_reason():
    cc = load_engine()
    d = cc.reconcile(
        [{"__row__": 2, "store_id": "", "period": "2025-01", "consumption": 100}],
        [],
        [],
    )[0]
    assert "ID магазина" in d.reason


def test_units_in_reason():
    cc = load_engine()
    stores = [{"store_id": "S1"}]
    norms = [
        {
            "store_id": "S1",
            "period": "2025-01",
            "norm_consumption": 100,
            "norm_amount": 500,
            "norm_unit": "кВт·ч",
            "version": 1,
            "valid_from": "2024-01-01",
        }
    ]
    d = cc.reconcile(
        [
            {
                "__row__": 2,
                "store_id": "S1",
                "period": "2025-01",
                "consumption": 100,
                "amount_net": 500,
                "unit": "кВт",
                "doc_number": "D",
                "charge_type": "основное",
                "period_start": "2025-01-01",
                "period_end": "2025-01-31",
            }
        ],
        norms,
        stores,
    )[0]
    assert "несовпадение единиц" in d.reason
