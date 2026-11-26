from tests._helpers import load_engine


def test_same_valid_from_picks_latest():
    norms = [
        {"store_id": "S1", "period": "2025-01", "valid_from": "2024-01-01",
         "version": 1, "norm_consumption": 100, "norm_amount": 500},
        {"store_id": "S1", "period": "2025-01", "valid_from": "2024-01-01",
         "version": 2, "norm_consumption": 120, "norm_amount": 600},
    ]
    n = load_engine().pick_norm(norms, "s1", "2025-01")
    assert n["version"] == 2


def test_future_version_skipped():
    norms = [
        {"store_id": "S1", "period": "2025-01", "valid_from": "2025-02-01",
         "version": 2, "norm_consumption": 100, "norm_amount": 500},
    ]
    assert load_engine().pick_norm(norms, "s1", "2025-01") is None
