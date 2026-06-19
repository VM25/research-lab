"""Target weights: sum to 1, non-negative, no leverage, caps respected."""
import pandas as pd

from systematic_alpha_lab.portfolio.weighting import target_weights, CASH
from systematic_alpha_lab.portfolio.constraints import apply_constraints

GROUPS = {"SPY": "us_equity", "QQQ": "us_equity", "IWM": "us_equity",
          "IEF": "treasury", "GLD": "gold"}
CONSTRAINTS = {
    "max_single_asset": 0.25,
    "group_caps": {"us_equity": 0.70, "treasury": 0.70, "gold": 0.25},
}


def test_weights_sum_to_one_and_nonnegative():
    trade = pd.Series({"SPY": 1, "QQQ": 1, "IEF": 1, "GLD": 1, "IWM": 0})
    score = pd.Series({"SPY": 1.0, "QQQ": 0.5, "IEF": 0.2, "GLD": 0.1, "IWM": -1.0})
    w = target_weights(trade, score, "equal_weight", GROUPS, CONSTRAINTS)
    assert abs(w.sum() - 1.0) < 1e-9
    assert (w >= -1e-12).all()                       # no shorting
    assert w.drop(CASH).max() <= 0.25 + 1e-9         # single-asset cap (CASH exempt)
    assert w.get("IWM", 0.0) == 0.0                  # not selected -> no allocation


def test_cash_fallback_when_none_selected():
    trade = pd.Series({"SPY": 0, "QQQ": 0, "IEF": 0, "GLD": 0, "IWM": 0})
    score = pd.Series({k: 0.0 for k in trade.index})
    w = target_weights(trade, score, "equal_weight", GROUPS, CONSTRAINTS)
    assert abs(w[CASH] - 1.0) < 1e-9                  # 100% cash


def test_group_cap_enforced():
    # four US equities equally weighted would be 100% US equity; cap is 70%.
    w = apply_constraints(pd.Series({"SPY": 0.25, "QQQ": 0.25, "IWM": 0.25, "IEF": 0.25}),
                          GROUPS, CONSTRAINTS)
    us = w[["SPY", "QQQ", "IWM"]].sum()
    assert us <= 0.70 + 1e-9
    assert abs(w.sum() - 1.0) < 1e-9
    assert w[CASH] > 0                                # clipped weight routed to cash


def test_no_leverage():
    w = apply_constraints(pd.Series({"SPY": 0.9, "IEF": 0.9}), GROUPS, CONSTRAINTS)
    assert w.drop(CASH).sum() <= 1.0 + 1e-9
