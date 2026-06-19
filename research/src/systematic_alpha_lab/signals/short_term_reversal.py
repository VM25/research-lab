"""Signal 3 — Short-Term Reversal (oversold rebound)."""
from __future__ import annotations

import pandas as pd

from .base import SignalResult, cross_sectional_zscore


def compute(prices: pd.DataFrame, returns: pd.DataFrame, params: dict,
            rebalance: str) -> SignalResult:
    k = int(params["lookback_return"])
    win = int(params["zscore_window"])
    thresh = float(params["entry_threshold"])

    ret_k = prices / prices.shift(k) - 1.0
    roll_mean = ret_k.rolling(win, min_periods=win).mean()
    roll_std = ret_k.rolling(win, min_periods=win).std(ddof=0)
    reversal_z = (ret_k - roll_mean) / roll_std

    # Buy oversold (z <= threshold). Score is attractiveness: more oversold -> higher.
    raw_score = -reversal_z
    trade = (reversal_z <= thresh).astype(float)
    trade = trade.where(reversal_z.notna(), 0.0)
    return SignalResult(
        name="short_term_reversal",
        raw_score=raw_score,
        normalized_score=cross_sectional_zscore(raw_score),
        trade_signal=trade,
        lookback_window=k,
        rebalance_frequency=rebalance,
    )
