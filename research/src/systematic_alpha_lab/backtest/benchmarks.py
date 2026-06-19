"""Benchmark weight schedules, run through the same engine and cost model."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..data.dataset import Dataset
from ..utils.dates import rebalance_dates
from .engine import run_backtest, BacktestResult, CASH

BENCH_LABELS = {
    "spy_buy_hold": "SPY Buy & Hold",
    "sixty_forty": "60/40 (SPY/IEF)",
    "equal_weight_universe": "Equal-Weight Universe",
    "cash_proxy": "Cash / T-Bills",
    "inverse_volatility": "Inverse-Volatility",
}


def _schedule(rb_dates, cols, rows: dict) -> pd.DataFrame:
    df = pd.DataFrame.from_dict(rows, orient="index").reindex(columns=cols).fillna(0.0)
    df.index.name = "date"
    return df.sort_index()


def build_benchmark_schedules(ds: Dataset, rebalance_freq: str = "monthly"
                              ) -> dict[str, pd.DataFrame]:
    cols = list(ds.tradable) + [CASH]
    rb = rebalance_dates(ds.calendar, rebalance_freq)
    prices = ds.prices
    rets = ds.returns
    schedules: dict[str, pd.DataFrame] = {}

    # SPY buy & hold: a single allocation, then hold (≈ zero turnover).
    first = rb.min()
    schedules["spy_buy_hold"] = _schedule(
        [first], cols, {first: pd.Series({"SPY": 1.0})})

    # 60/40, rebalanced each period.
    schedules["sixty_forty"] = _schedule(
        rb, cols, {d: pd.Series({"SPY": 0.6, "IEF": 0.4}) for d in rb})

    # Equal-weight across all ETFs with a valid price on the rebalance date.
    ew_rows = {}
    for d in rb:
        avail = [t for t in ds.tradable if pd.notna(prices.loc[d, t])] \
            if d in prices.index else []
        if avail:
            ew_rows[d] = pd.Series(1.0 / len(avail), index=avail)
    schedules["equal_weight_universe"] = _schedule(rb, cols, ew_rows)

    # Cash / T-bills.
    schedules["cash_proxy"] = _schedule(rb, cols, {d: pd.Series({CASH: 1.0}) for d in rb})

    # Inverse-volatility across available ETFs (optional benchmark).
    realized = rets.rolling(63, min_periods=63).std(ddof=0) * np.sqrt(252)
    iv_rows = {}
    for d in rb:
        if d not in realized.index:
            continue
        vol = realized.loc[d, ds.tradable].dropna()
        vol = vol[vol > 0]
        if len(vol):
            inv = 1.0 / vol
            iv_rows[d] = inv / inv.sum()
    schedules["inverse_volatility"] = _schedule(rb, cols, iv_rows)
    return schedules


def run_benchmarks(ds: Dataset, cost_bps: float, common_start: pd.Timestamp,
                   end: str | None = None, rebalance_freq: str = "monthly"
                   ) -> dict[str, BacktestResult]:
    schedules = build_benchmark_schedules(ds, rebalance_freq)
    R = ds.returns_with_cash
    out = {}
    for name, sched in schedules.items():
        out[name] = run_backtest(sched, R, cost_bps,
                                 start=str(common_start.date()), end=end)
    return out
