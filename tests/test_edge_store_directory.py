from tests._helpers import load_engine


def test_empty_directory():
    cc = load_engine()
    d = cc.reconcile(
        [
            {
                "__row__": 2,
                "store_id": "S1",
                "period": "2025-01",
                "consumption": 100,
                "amount_net": 500,
                "unit": "кВт·ч",
                "doc_number": "D",
                "charge_type": "основное",
                "period_start": "2025-01-01",
                "period_end": "2025-01-31",
            }
        ],
        [],
        [],
    )[0]
    assert d.rule == 2


def test_directory_with_normalized_ids():
    cc = load_engine()
    stores = [{"store_id": "s-01"}, {"store_id": "S02 "}]
    assert cc.norm_id(stores[0]["store_id"]) == "s01"
    assert cc.norm_id(stores[1]["store_id"]) == "s02"
