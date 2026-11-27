from testdata.scenarios.foreign_format import generate
from tests._helpers import load_engine


def test_foreign_format_reconciles_both_rows(tmp_path):
    generate(tmp_path)
    engine = load_engine()
    tables = [
        engine.read_table(tmp_path / f"{role}_foreign.xlsx", role)
        for role in ("charges", "norms", "stores")
    ]
    decisions = engine.reconcile(*tables)
    assert [
        (row.store_id, row.status, row.rule, row.dev_kwh, row.dev_rub) for row in decisions
    ] == [
        ("S01", "в норме", 8, 0, 0),
        ("S02", "превышение", 8, 200, 1000),
    ]
