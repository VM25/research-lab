"""No-lookahead: signal[t] sets position[t+1], which earns return[t+1].

A signal generated on a rebalance date must NOT capture that same day's return;
it only earns from the next trading day.
"""
import pandas as pd

from systematic_alpha_lab.backtest.engine import run_backtest, CASH


def test_position_earns_next_day_not_same_day():
    idx = pd.date_range("2020-01-01", periods=7, freq="B")  # d0..d6
    a = [0.0] * 7
    a[3] = 0.50   # spike ON the rebalance day d3
    a[4] = 0.30   # move the day AFTER the rebalance
    R = pd.DataFrame({"A": a, CASH: [0.0] * 7}, index=idx)

    # all cash until d3, then rotate fully into A at d3
    sched = pd.DataFrame({"A": [0.0, 1.0], CASH: [1.0, 0.0]},
                         index=[idx[0], idx[3]])
    res = run_backtest(sched, R, cost_bps=0.0)

    # d3 spike happens while still holding cash -> NOT captured
    assert abs(res.gross_returns.loc[idx[3]] - 0.0) < 1e-12
    # d4 move happens while holding A (set by the d3 signal) -> captured
    assert abs(res.gross_returns.loc[idx[4]] - 0.30) < 1e-12


def test_no_same_day_capture_for_buy_and_hold():
    idx = pd.date_range("2020-01-01", periods=5, freq="B")
    R = pd.DataFrame({"A": [0.0, 0.10, 0.0, 0.0, 0.0], CASH: [0.0] * 5}, index=idx)
    # rebalance into A only on d2 (the spike already happened on d1)
    sched = pd.DataFrame({"A": [0.0, 1.0], CASH: [1.0, 0.0]}, index=[idx[0], idx[2]])
    res = run_backtest(sched, R, cost_bps=0.0)
    # the d1 spike is never captured (held cash through d2 rebalance)
    assert res.values.iloc[-1] == 1.0
