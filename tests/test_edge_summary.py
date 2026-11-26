from tests._helpers import load_engine


def test_summary_counts():
    cc = load_engine()
    decisions = [
        cc.Decision(row=2, rule=8, status="в норме", reason="ok"),
        cc.Decision(row=3, rule=8, status="превышение", reason="bad"),
        cc.Decision(row=4, rule=1, status="требуется уточнение", reason="missing"),
        cc.Decision(row=5, rule=3, status="исключение: дубль", reason="dup"),
    ]
    s = cc.summarize(decisions)
    assert s["checked"] == 4
    assert s["ok"] == 1
    assert s["exceeded"] == 1
    assert s["clarifications"] == 1
    assert s["exceptions"] == 1


def test_reasons_dictionary():
    cc = load_engine()
    decisions = [
        cc.Decision(row=2, rule=8, status="превышение", reason="r1"),
        cc.Decision(row=3, rule=8, status="превышение", reason="r2"),
    ]
    assert cc.summarize(decisions)["reasons"]["превышение"] == 2
