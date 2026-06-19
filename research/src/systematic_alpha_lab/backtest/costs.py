"""Transaction-cost model: cost is a return drag proportional to turnover.

    transaction_cost[t] = turnover[t] * cost_bps / 10000
    net_return[t]       = gross_return[t] - transaction_cost[t]

Turnover here is the sum of absolute weight changes at a rebalance (both the
buy and sell legs), matching docs/04_BACKTEST_ENGINE_SPEC.md.
"""
from __future__ import annotations

import pandas as pd

COST_SCENARIO_ORDER = ["low", "base", "high", "stress"]


def transaction_cost(turnover, cost_bps: float):
    """Cost drag for a given turnover (scalar or Series)."""
    return turnover * (cost_bps / 10000.0)


def apply_costs(gross_return: pd.Series, turnover: pd.Series,
                cost_bps: float) -> pd.Series:
    return gross_return - transaction_cost(turnover, cost_bps)
