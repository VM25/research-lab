"""Portfolio value compounds net returns; turnover drives cost drag."""
import numpy as np
import pandas as pd

from systematic_alpha_lab.backtest.engine import run_backtest, CASH


def _setup(daily_a=0.01, n=11):
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    R = pd.DataFrame({"A": [daily_a] * n, CASH: [0.0] * n}, index=idx)
    sched = pd.DataFrame({"A": [1.0], CASH: [0.0]}, index=[idx[0]])
    return R, sched, idx


def test_value_compounds():
    R, sched, idx = _setup(0.01, 11)
    res = run_backtest(sched, R, cost_bps=0.0)
    # engine starts the day after the single rebalance (idx[0]); 10 active days
    k = len(res.values)
    assert k == 10
    expected = 1.01 ** k
    assert abs(res.values.iloc[-1] - expected) < 1e-9
    # value[t] == value[t-1]*(1+net[t])
    rebuilt = (1.0 + res.net_returns).cumprod()
    assert np.allclose(res.values.values, rebuilt.values)


def test_costs_reduce_terminal_value():
    R, sched, idx = _setup(0.01, 11)
    # add a second rebalance that fully rotates A<->CASH to create turnover
    sched2 = pd.DataFrame({"A": [1.0, 0.0], CASH: [0.0, 1.0]},
                          index=[idx[0], idx[5]])
    free = run_backtest(sched2, R, cost_bps=0.0)
    costly = run_backtest(sched2, R, cost_bps=25.0)
    assert costly.values.iloc[-1] < free.values.iloc[-1]
    assert costly.turnover.loc[idx[5]] > 0           # turnover recorded at rebalance
