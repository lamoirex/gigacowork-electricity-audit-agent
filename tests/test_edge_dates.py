import pytest
from tests._helpers import load_engine


def test_invalid_month_does_not_crash():
    cc = load_engine()
    period = cc.period_key("2025-13")
    assert period is None


def test_mismatched_period_and_dates():
    cc = load_engine()
    stores = [{"store_id": "S1"}]
    norms = [{"store_id": "S1", "period": "2025-01",
              "norm_consumption": 100, "norm_amount": 500,
              "norm_unit": "кВт·ч", "version": 1, "valid_from": "2024-01-01"}]
    d = cc.reconcile(
        [{"__row__": 2, "store_id": "S1", "period": "2025-01",
          "consumption": 100, "amount_net": 500, "unit": "кВт·ч",
          "doc_number": "D", "charge_type": "основное",
          "period_start": "2025-02-01", "period_end": "2025-02-28"}],
        norms, stores,
    )[0]
    assert d.rule == 5
