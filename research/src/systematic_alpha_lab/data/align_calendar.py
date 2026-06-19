"""Align all tickers to one master trading calendar and build wide panels.

The master calendar is the set of trading days of the reference ticker (SPY).
Assets enter the panel on their own inception date; values before inception
stay NaN (we never forward-fill missing asset history). Returns are computed
only where consecutive real prices exist.
"""
from __future__ import annotations

import pandas as pd


def build_price_panel(long: pd.DataFrame, calendar_reference: str
                      ) -> pd.DataFrame:
    """Wide adjusted-close panel: index = trading dates, columns = tickers."""
    wide = long.pivot(index="date", columns="ticker", values="adjusted_close")
    wide = wide.sort_index()
    if calendar_reference not in wide.columns:
        raise ValueError(f"calendar reference {calendar_reference} not in universe")
    cal = wide.index[wide[calendar_reference].notna()]
    wide = wide.loc[cal]
    wide.index.name = "date"
    return wide


def to_long_prices(long: pd.DataFrame, calendar: pd.DatetimeIndex) -> pd.DataFrame:
    """Restrict the long price table to the master calendar (for prices.parquet)."""
    out = long[long["date"].isin(calendar)].copy()
    return out.sort_values(["date", "ticker"]).reset_index(drop=True)
