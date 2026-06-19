"""Shared helpers for validation: window slicing and metric computation."""
from __future__ import annotations

import pandas as pd

from ..backtest import metrics as M
from ..backtest.engine import BacktestResult


def _slice(s: pd.Series, start, end) -> pd.Series:
    out = s
    if start is not None:
        out = out[out.index >= pd.Timestamp(start)]
    if end is not None:
        out = out[out.index <= pd.Timestamp(end)]
    return out


def window_metrics(result: BacktestResult, rf_daily: pd.Series,
                   start=None, end=None) -> dict:
    """CAGR/Sharpe/MaxDD/turnover/cost-drag over a sub-window of a backtest."""
    net = _slice(result.net_returns, start, end)
    gross = _slice(result.gross_returns, start, end)
    turn = _slice(result.turnover, start, end)
    if len(net) == 0:
        return {"cagr": float("nan"), "sharpe": float("nan"),
                "max_drawdown": float("nan"), "annualized_turnover": float("nan"),
                "cost_drag": float("nan"), "n_days": 0}
    return {
        "cagr": M.cagr(net),
        "gross_cagr": M.cagr(gross),
        "sharpe": M.sharpe(net, rf_daily),
        "max_drawdown": M.max_drawdown(net),
        "annualized_turnover": M.annualized_turnover(turn),
        "cost_drag": M.cagr(gross) - M.cagr(net),
        "n_days": int(len(net)),
    }


def cumulative_return(s: pd.Series) -> float:
    return float((1.0 + s).prod() - 1.0)
