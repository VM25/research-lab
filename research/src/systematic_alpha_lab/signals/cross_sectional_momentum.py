"""Signal 2 — Cross-Sectional Momentum (relative strength, top quantile)."""
from __future__ import annotations

import pandas as pd

from .base import SignalResult, cross_sectional_zscore, momentum_12_1


def compute(prices: pd.DataFrame, returns: pd.DataFrame, params: dict,
            rebalance: str) -> SignalResult:
    long = int(params["lookback_long"])
    skip = int(params["lookback_skip"])
    top_q = float(params["top_quantile"])
    mom = momentum_12_1(prices, long, skip)
    # Percentile rank across eligible assets each date (0..1).
    rank = mom.rank(axis=1, pct=True)
    trade = (rank >= top_q).astype(float)
    trade = trade.where(mom.notna(), 0.0)
    return SignalResult(
        name="cross_sectional_momentum",
        raw_score=mom,
        normalized_score=cross_sectional_zscore(mom),
        trade_signal=trade,
        lookback_window=long,
        rebalance_frequency=rebalance,
    )
