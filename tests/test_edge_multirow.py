from tests._helpers import load_engine


def test_multiple_rows_dedup():
    cc = load_engine()
    stores = [{"store_id": "S1"}]
    norms = [{"store_id": "S1", "period": "2025-01",
              "norm_consumption": 100, "norm_amount": 500,
              "norm_unit": "кВт·ч", "version": 1, "valid_from": "2024-01-01"}]
    row = {"__row__": 2, "store_id": "S1", "period": "2025-01",
           "consumption": 100, "amount_net": 500, "unit": "кВт·ч",
           "doc_number": "D1", "charge_type": "основное",
           "period_start": "2025-01-01", "period_end": "2025-01-31"}
    rows = [dict(row, __row__=i) for i in range(2, 7)]
    decisions = cc.reconcile(rows, norms, stores)
    statuses = [d.status for d in decisions]
    assert statuses[0] == "в норме"
    assert all("дубль" in s for s in statuses[1:])
