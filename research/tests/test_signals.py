"""Signal lagging: a signal at date t may only use data through t."""
import numpy as np
import pandas as pd

from systematic_alpha_lab.signals.base import momentum_12_1
from systematic_alpha_lab.signals import time_series_momentum as tsm


def _prices(n=300):
    idx = pd.date_range("2018-01-01", periods=n, freq="B")
    # steadily rising series so 12-1 momentum is positive once defined
    return pd.DataFrame({"A": np.linspace(100, 200, n)}, index=idx)


def test_momentum_undefined_before_lookback():
    p = _prices()
    mom = momentum_12_1(p, lookback_long=252, lookback_skip=21)
    assert mom["A"].iloc[:252].isna().all()         # not enough history yet
    assert mom["A"].iloc[260] == mom["A"].iloc[260]  # defined later (not NaN)


def test_momentum_uses_only_past_prices():
    p = _prices()
    mom = momentum_12_1(p, 252, 21)
    t = 280
    expected = p["A"].iloc[t - 21] / p["A"].iloc[t - 252] - 1.0
    assert abs(mom["A"].iloc[t] - expected) < 1e-12   # uses t-21 and t-252 only


def test_trade_signal_excludes_ineligible():
    p = _prices()
    res = tsm.compute(p, p.pct_change(), {"lookback_long": 252, "lookback_skip": 21},
                      "monthly")
    # before enough history, trade signal must be 0 (excluded), never 1
    assert (res.trade_signal["A"].iloc[:252] == 0).all()
