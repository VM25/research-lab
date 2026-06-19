"""Return calculation from adjusted close.

Simple daily returns: r[t] = adjusted_close[t] / adjusted_close[t-1] - 1.
Returns are only defined where two consecutive real prices exist (no
forward-filling across gaps), so an asset's return series begins the day after
its first observation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def simple_returns(price_panel: pd.DataFrame) -> pd.DataFrame:
    """Daily simple returns from a wide adjusted-close panel."""
    rets = price_panel.pct_change()
    # Only keep returns where both endpoints were real (pct_change already
    # yields NaN if either side is NaN). First row is NaN by construction.
    return rets


def log_returns(price_panel: pd.DataFrame) -> pd.DataFrame:
    """Log returns, for diagnostics only."""
    return np.log(price_panel / price_panel.shift(1))


def returns_long(rets: pd.DataFrame, rf_daily: pd.Series) -> pd.DataFrame:
    """Long-format returns table with the aligned risk-free column."""
    long = rets.stack().rename("simple_return").reset_index()
    long.columns = ["date", "ticker", "simple_return"]
    rf = rf_daily.reindex(rets.index).ffill()
    long["risk_free_daily"] = long["date"].map(rf)
    return long.sort_values(["date", "ticker"]).reset_index(drop=True)
