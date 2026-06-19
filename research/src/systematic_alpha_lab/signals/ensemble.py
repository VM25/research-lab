"""Signal 5 — Equal-Weight Signal Ensemble.

Averages the standardized (cross-sectional z-scored) scores of the four base
signals and holds every asset whose average score is positive.
"""
from __future__ import annotations

import pandas as pd

from .base import SignalResult, cross_sectional_zscore


def compute(member_results: dict, params: dict, rebalance: str) -> SignalResult:
    members = params["members"]
    thresh = float(params["entry_threshold"])

    norms = [member_results[m].normalized_score for m in members]
    # Mean across members element-wise (skip NaN so partial coverage still scores).
    ensemble_score = sum(n.fillna(0) for n in norms) / \
        sum((~n.isna()).astype(float) for n in norms).replace(0, float("nan"))

    trade = (ensemble_score > thresh).astype(float)
    trade = trade.where(ensemble_score.notna(), 0.0)
    return SignalResult(
        name="ensemble",
        raw_score=ensemble_score,
        normalized_score=cross_sectional_zscore(ensemble_score),
        trade_signal=trade,
        lookback_window=252,
        rebalance_frequency=rebalance,
    )
