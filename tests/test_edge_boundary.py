from tests._helpers import load_engine


def _decide(consumption, amount_net, norm_kwh=1000, norm_rub=5000):
    cc = load_engine()
    d = cc.Decision(
        row=2, rule=8, status="", reason="", consumption=consumption, amount_net=amount_net
    )
    d.norm_consumption, d.norm_amount = norm_kwh, norm_rub
    d.dev_kwh = round(consumption - norm_kwh, 3)
    d.dev_kwh_pct = round(d.dev_kwh / norm_kwh * 100, 2)
    d.dev_rub = round(amount_net - norm_rub, 2)
    d.dev_rub_pct = round(d.dev_rub / norm_rub * 100, 2)
    exceeded = (d.dev_kwh_pct > cc.THRESHOLD) or (d.dev_rub_pct > cc.THRESHOLD)
    d.status = "превышение" if exceeded else "в норме"
    return d


def test_exactly_10_percent_is_in_norm():
    assert _decide(1100, 5500).status == "в норме"


def test_10_1_percent_is_exceeded():
    assert _decide(1101, 5500).status == "превышение"


def test_amount_10_percent_is_in_norm():
    # 5000 * 1.10 = 5500
    assert _decide(1000, 5500).status == "в норме"


def test_amount_11_percent_is_exceeded():
    # 5000 * 1.11 = 5550
    assert _decide(1000, 5551).status == "превышение"


def test_small_abs_diff_under_threshold_is_in_norm():
    # 1 руб. из 5000 = 0.02% — норма
    assert _decide(1000, 5001).status == "в норме"
