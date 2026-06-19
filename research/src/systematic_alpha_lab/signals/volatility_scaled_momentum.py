"""Signal 4 — Volatility-Scaled Momentum.

Selection is by time-series momentum sign; each position is then scaled toward a
volatility target. The per-asset `scale` panel is carried in `extra` so the
portfolio layer can shrink weights and route the remainder to cash.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import SignalResult, cross_sectional_zscore, momentum_12_1
from . import time_series_momentum as tsmom


def realized_vol(returns: pd.DataFrame, window: int, ann: int = 252) -> pd.DataFrame:
    return returns.rolling(window, min_periods=window).std(ddof=0) * np.sqrt(ann)


def vol_scale(returns: pd.DataFrame, window: int, target_vol: float) -> pd.DataFrame:
    rv = realized_vol(returns, window)
    scale = (target_vol / rv).clip(upper=1.0)
    return scale


def compute(prices: pd.DataFrame, returns: pd.DataFrame, params: dict,
            rebalance: str, mom_params: dict | None = None) -> SignalResult:
    window = int(params["vol_window"])
    target = float(params["target_vol"])
    mp = mom_params or {"lookback_long": 252, "lookback_skip": 21}

    mom = momentum_12_1(prices, int(mp["lookback_long"]), int(mp["lookback_skip"]))
    scale = vol_scale(returns, window, target)

    # Selection: positive momentum (same as TSMOM); weighting uses `scale`.
    base = tsmom.compute(prices, returns, mp, rebalance)
    trade = base.trade_signal

    vol_scaled_score = mom * scale          # attenuated momentum
    return SignalResult(
        name="volatility_scaled_momentum",
        raw_score=vol_scaled_score,
        normalized_score=cross_sectional_zscore(vol_scaled_score),
        trade_signal=trade,
        lookback_window=int(mp["lookback_long"]),
        rebalance_frequency=rebalance,
        extra={"scale": scale},
    )
