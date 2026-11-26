from tests._helpers import load_engine


def test_recalc_variants():
    cc = load_engine()
    for t in ["перерасчёт", "Перерасчёт", "ПЕРЕРАСЧЁТ", "перерасчет"]:
        d = cc.reconcile(
            [{"__row__": 2, "store_id": "S1", "period": "2025-01",
              "consumption": 100, "amount_net": 500, "unit": "кВт·ч",
              "doc_number": "D", "charge_type": t,
              "period_start": "2025-01-01", "period_end": "2025-01-31"}],
            [], [{"store_id": "S1"}],
        )[0]
        assert d.rule == 4
