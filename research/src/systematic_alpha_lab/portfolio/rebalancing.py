"""Build a target-weight schedule from a signal over the rebalance calendar."""
from __future__ import annotations

import pandas as pd

from ..signals.base import SignalResult
from ..utils.dates import rebalance_dates
from .weighting import target_weights, CASH


def build_weight_schedule(signal: SignalResult, calendar: pd.DatetimeIndex,
                          tradable: list[str], groups: dict[str, str],
                          method: str, constraints: dict,
                          rebalance_frequency: str) -> pd.DataFrame:
    """Target weights at each rebalance date (index), columns = tradable + CASH.

    Signals are sampled at the rebalance date using data through that date; the
    backtest engine applies these weights only from the next trading day (the
    no-lookahead rule is enforced there).
    """
    rb_dates = rebalance_dates(calendar, rebalance_frequency)
    scale_panel = signal.extra.get("scale")
    cols = list(tradable) + [CASH]
    rows: dict[pd.Timestamp, pd.Series] = {}

    for dt in rb_dates:
        if dt not in signal.trade_signal.index:
            continue
        trade_row = signal.trade_signal.loc[dt, tradable]
        score_row = signal.normalized_score.loc[dt, tradable]
        scale_row = scale_panel.loc[dt, tradable] if scale_panel is not None else None
        w = target_weights(trade_row, score_row, method, groups, constraints, scale_row)
        rows[dt] = w.reindex(cols).fillna(0.0)

    sched = pd.DataFrame.from_dict(rows, orient="index").reindex(columns=cols).fillna(0.0)
    sched.index.name = "date"
    return sched
