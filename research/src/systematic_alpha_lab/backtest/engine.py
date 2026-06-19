"""Daily portfolio simulation with weight drift, turnover, and costs.

No-lookahead timing:
  - target weights are set at the close of a rebalance date t (from signal[t]);
  - they earn returns starting on t+1;
  - between rebalances, weights drift with realized returns;
  - turnover is measured against the drifted pre-trade weights.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

CASH = "CASH"


@dataclass
class BacktestResult:
    gross_returns: pd.Series
    net_returns: pd.Series
    values: pd.Series            # net-of-cost portfolio value (compounded)
    gross_values: pd.Series      # gross portfolio value
    turnover: pd.Series          # per-day (nonzero only on rebalance days)
    costs: pd.Series             # per-day transaction-cost drag
    weights: pd.DataFrame        # post-trade weights each day
    cost_bps: float

    @property
    def drawdown(self) -> pd.Series:
        return self.values / self.values.cummax() - 1.0


def run_backtest(weight_schedule: pd.DataFrame, returns_with_cash: pd.DataFrame,
                 cost_bps: float, initial_value: float = 1.0,
                 start: str | None = None, end: str | None = None) -> BacktestResult:
    cols = list(weight_schedule.columns)
    R = returns_with_cash.reindex(columns=cols).copy()
    R[CASH] = returns_with_cash[CASH]
    R = R.fillna(0.0)

    cal = R.index
    if start is not None:
        cal = cal[cal >= pd.Timestamp(start)]
    if end is not None:
        cal = cal[cal <= pd.Timestamp(end)]
    if len(cal) == 0:
        raise ValueError("empty backtest window")

    rbs = weight_schedule.index
    rb_lookup = weight_schedule
    rb_set = set(rbs)

    # Initialise the position from the most recent rebalance before the window.
    prior = rbs[rbs < cal[0]]
    if len(prior) > 0:
        w = weight_schedule.loc[prior.max()].copy()
    else:
        # No prior rebalance: begin the day after the first rebalance in-window.
        upcoming = rbs[rbs >= cal[0]]
        if len(upcoming) == 0:
            raise ValueError("no rebalance dates available for this window")
        first_rb = upcoming.min()
        cal = cal[cal > first_rb]
        if len(cal) == 0:
            raise ValueError("no backtest dates after the first rebalance")
        w = weight_schedule.loc[first_rb].copy()

    idx, g_list, n_list, to_list, c_list, w_rows = [], [], [], [], [], []
    value = initial_value
    gvalue = initial_value
    cost_frac = cost_bps / 10000.0

    for dt in cal:
        r = R.loc[dt]
        gross = float((w * r).sum())
        denom = 1.0 + gross
        w_drift = (w * (1.0 + r)) / denom if denom != 0 else w.copy()

        turnover = 0.0
        cost = 0.0
        if dt in rb_set:
            target = rb_lookup.loc[dt]
            turnover = float((target - w_drift).abs().sum())
            cost = turnover * cost_frac
            w_new = target.copy()
        else:
            w_new = w_drift

        net = gross - cost
        value *= (1.0 + net)
        gvalue *= (1.0 + gross)

        idx.append(dt)
        g_list.append(gross)
        n_list.append(net)
        to_list.append(turnover)
        c_list.append(cost)
        w_rows.append(w_new.values)
        w = w_new

    gross_returns = pd.Series(g_list, index=idx, name="gross_return")
    net_returns = pd.Series(n_list, index=idx, name="net_return")
    return BacktestResult(
        gross_returns=gross_returns,
        net_returns=net_returns,
        values=pd.Series(n_list, index=idx).add(1).cumprod().mul(initial_value).rename("value"),
        gross_values=pd.Series(g_list, index=idx).add(1).cumprod().mul(initial_value).rename("gross_value"),
        turnover=pd.Series(to_list, index=idx, name="turnover"),
        costs=pd.Series(c_list, index=idx, name="cost"),
        weights=pd.DataFrame(w_rows, index=idx, columns=cols),
        cost_bps=cost_bps,
    )
