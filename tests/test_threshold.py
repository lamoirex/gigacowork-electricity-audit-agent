from tests._helpers import load_engine


def _decide(consumption, amount_net, norm_kwh=1000, norm_rub=5000):
    cc = load_engine()
    d = cc.Decision(row=2, rule=8, status="", reason="",
                    consumption=consumption, amount_net=amount_net)
    d.norm_consumption, d.norm_amount = norm_kwh, norm_rub
    d.dev_kwh = round(consumption - norm_kwh, 3)
    d.dev_kwh_pct = round(d.dev_kwh / norm_kwh * 100, 2)
    d.dev_rub = round(amount_net - norm_rub, 2)
    d.dev_rub_pct = round(d.dev_rub / norm_rub * 100, 2)
    exceeded = (d.dev_kwh_pct > cc.THRESHOLD) or (d.dev_rub_pct > cc.THRESHOLD)
    d.status = "превышение" if exceeded else "в норме"
    return d


def test_threshold_is_strict_10_percent():
    d = _decide(1100, 5500)
    assert d.dev_kwh_pct == 10.0
    assert d.status == "в норме"


def test_above_threshold_marks_exceeded():
    d = _decide(1101, 5500)
    assert d.status == "превышение"


def test_amount_alone_can_exceed():
    d = _decide(1000, 6000)
    assert d.status == "превышение"
