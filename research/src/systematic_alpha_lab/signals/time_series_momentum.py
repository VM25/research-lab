"""Signal 1 — Time-Series Momentum (12-1)."""
from __future__ import annotations

import pandas as pd

from .base import SignalResult, cross_sectional_zscore, momentum_12_1


def compute(prices: pd.DataFrame, returns: pd.DataFrame, params: dict,
            rebalance: str) -> SignalResult:
    long = int(params["lookback_long"])
    skip = int(params["lookback_skip"])
    mom = momentum_12_1(prices, long, skip)
    trade = (mom > 0).astype(float)
    trade = trade.where(mom.notna(), 0.0)   # ineligible (NaN) -> excluded
    return SignalResult(
        name="time_series_momentum",
        raw_score=mom,
        normalized_score=cross_sectional_zscore(mom),
        trade_signal=trade,
        lookback_window=long,
        rebalance_frequency=rebalance,
    )
