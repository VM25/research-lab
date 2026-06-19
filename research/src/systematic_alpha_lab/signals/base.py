"""Shared signal scaffolding."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class SignalResult:
    """Per-date, per-ticker signal panels (index = dates, columns = tickers)."""
    name: str
    raw_score: pd.DataFrame
    normalized_score: pd.DataFrame
    trade_signal: pd.DataFrame
    lookback_window: int
    rebalance_frequency: str
    extra: dict = field(default_factory=dict)   # e.g. {'scale': DataFrame}

    def to_long(self) -> pd.DataFrame:
        """Long-format signal table matching docs/03_SIGNAL_SPEC.md output fields."""
        raw = self.raw_score.stack().rename("raw_score")
        norm = self.normalized_score.stack().rename("normalized_score")
        trade = self.trade_signal.stack().rename("trade_signal")
        out = pd.concat([raw, norm, trade], axis=1).reset_index()
        out.columns = ["date", "ticker", "raw_score", "normalized_score", "trade_signal"]
        out["signal_name"] = self.name
        out["lookback_window"] = self.lookback_window
        out["rebalance_frequency"] = self.rebalance_frequency
        return out[["date", "ticker", "signal_name", "raw_score",
                    "normalized_score", "trade_signal", "lookback_window",
                    "rebalance_frequency"]]


def cross_sectional_zscore(scores: pd.DataFrame) -> pd.DataFrame:
    """Standardize each row across tickers (ignoring NaN/ineligible assets)."""
    mu = scores.mean(axis=1)
    sd = scores.std(axis=1, ddof=0)
    z = scores.sub(mu, axis=0).div(sd.replace(0.0, np.nan), axis=0)
    return z


def momentum_12_1(prices: pd.DataFrame, lookback_long: int, lookback_skip: int
                  ) -> pd.DataFrame:
    """adj[t-skip] / adj[t-long] - 1, NaN until `lookback_long` history exists."""
    return prices.shift(lookback_skip) / prices.shift(lookback_long) - 1.0
