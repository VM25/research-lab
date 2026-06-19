"""Clean raw prices and produce the data-quality report.

Cleaning rules (see docs/02_DATA_SPEC.md):
  - drop duplicate (date, ticker) rows
  - drop rows with missing/zero/negative adjusted close
  - FLAG (not delete) daily returns whose absolute value exceeds 25%
  - never forward-fill prices for return calculation
"""
from __future__ import annotations

import pandas as pd

EXTREME_RETURN_THRESHOLD = 0.25


def clean_prices(long: pd.DataFrame, requested_start: str
                 ) -> tuple[pd.DataFrame, dict]:
    """Return (clean_long_df, quality_report)."""
    report: dict = {"requested_start_date": requested_start}
    n_raw = len(long)

    dup_mask = long.duplicated(subset=["date", "ticker"], keep="last")
    duplicate_rows = int(dup_mask.sum())
    long = long[~dup_mask]

    invalid_mask = long["adjusted_close"].isna() | (long["adjusted_close"] <= 0)
    invalid_prices = int(invalid_mask.sum())
    long = long[~invalid_mask].copy()

    # Per-ticker extreme-return flags (computed on adjusted close, chronological).
    long = long.sort_values(["ticker", "date"])
    long["adj_ret"] = long.groupby("ticker")["adjusted_close"].pct_change()
    extreme_mask = long["adj_ret"].abs() > EXTREME_RETURN_THRESHOLD
    extreme_flags = int(extreme_mask.sum())
    long = long.drop(columns="adj_ret")

    per_ticker = (
        long.groupby("ticker")["date"]
        .agg(first="min", last="max", count="count")
        .reset_index()
    )
    final_tickers = sorted(long["ticker"].unique().tolist())

    report.update(
        {
            "ticker_count": len(final_tickers),
            "final_tickers": final_tickers,
            "excluded_tickers": [],
            "exclusion_reasons": {},
            "sample_start": long["date"].min().strftime("%Y-%m-%d"),
            "sample_end": long["date"].max().strftime("%Y-%m-%d"),
            "actual_start_date": long["date"].min().strftime("%Y-%m-%d"),
            "actual_end_date": long["date"].max().strftime("%Y-%m-%d"),
            "row_count": int(len(long)),
            "raw_row_count": n_raw,
            "missing_values": int(invalid_prices),
            "duplicate_rows": duplicate_rows,
            "invalid_prices": invalid_prices,
            "extreme_return_flags": extreme_flags,
            "final_observation_count": int(len(long)),
            "per_ticker_history": {
                row.ticker: {
                    "first_date": row.first.strftime("%Y-%m-%d"),
                    "last_date": row.last.strftime("%Y-%m-%d"),
                    "observations": int(row.count),
                }
                for row in per_ticker.itertuples()
            },
        }
    )
    return long, report
