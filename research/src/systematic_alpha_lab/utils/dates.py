"""Trading-calendar helpers: rebalance schedules and period slicing."""
from __future__ import annotations

import pandas as pd


def rebalance_dates(calendar: pd.DatetimeIndex, frequency: str) -> pd.DatetimeIndex:
    """Return the last trading day of each period for the given frequency.

    The calendar is the master list of real trading days. Rebalances occur on
    the last available trading day of each week/month/quarter, so a scheduled
    date that is not a trading day rolls back to the prior trading day.
    """
    cal = pd.DatetimeIndex(calendar).sort_values()
    s = pd.Series(cal, index=cal)
    if frequency == "weekly":
        keys = cal.to_period("W")
    elif frequency == "monthly":
        keys = cal.to_period("M")
    elif frequency == "quarterly":
        keys = cal.to_period("Q")
    else:
        raise ValueError(f"unknown rebalance frequency: {frequency}")
    # last trading day within each period bucket
    last = s.groupby(keys).max()
    return pd.DatetimeIndex(last.values).sort_values()


def slice_period(df: pd.DataFrame, start: str | None, end: str | None) -> pd.DataFrame:
    """Inclusive date slice; None bounds mean open-ended."""
    out = df
    if start is not None:
        out = out[out.index >= pd.Timestamp(start)]
    if end is not None:
        out = out[out.index <= pd.Timestamp(end)]
    return out
