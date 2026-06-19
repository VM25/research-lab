"""Performance metrics. Only metrics that inform signal survival."""
from __future__ import annotations

import numpy as np
import pandas as pd

ANN = 252


def _to_value(returns: pd.Series, initial: float = 1.0) -> pd.Series:
    return (1.0 + returns).cumprod() * initial


def cagr(returns: pd.Series) -> float:
    n = len(returns)
    if n == 0:
        return float("nan")
    end = float((1.0 + returns).prod())
    if end <= 0:
        return float("nan")
    return end ** (ANN / n) - 1.0


def annualized_return(returns: pd.Series) -> float:
    return float(returns.mean() * ANN)


def annualized_vol(returns: pd.Series) -> float:
    return float(returns.std(ddof=0) * np.sqrt(ANN))


def sharpe(returns: pd.Series, rf_daily: pd.Series) -> float:
    rf = rf_daily.reindex(returns.index).fillna(0.0)
    excess = returns - rf
    sd = excess.std(ddof=0)
    if sd == 0 or np.isnan(sd):
        return float("nan")
    return float(excess.mean() * ANN / (sd * np.sqrt(ANN)))


def max_drawdown(returns: pd.Series) -> float:
    val = _to_value(returns)
    dd = val / val.cummax() - 1.0
    return float(dd.min())


def worst_month(returns: pd.Series) -> float:
    monthly = (1.0 + returns).resample("ME").prod() - 1.0
    return float(monthly.min()) if len(monthly) else float("nan")


def annualized_turnover(turnover: pd.Series) -> float:
    n_years = len(turnover) / ANN
    return float(turnover.sum() / n_years) if n_years > 0 else float("nan")


def tracking_error(returns: pd.Series, bench: pd.Series) -> float:
    excess = (returns - bench.reindex(returns.index)).dropna()
    return float(excess.std(ddof=0) * np.sqrt(ANN))


def information_ratio(returns: pd.Series, bench: pd.Series) -> float:
    excess = (returns - bench.reindex(returns.index)).dropna()
    te = excess.std(ddof=0)
    if te == 0 or np.isnan(te):
        return float("nan")
    return float(excess.mean() * ANN / (te * np.sqrt(ANN)))


def core_metrics(net: pd.Series, gross: pd.Series, rf_daily: pd.Series,
                 turnover: pd.Series) -> dict:
    """Standalone metrics for a strategy (no benchmark)."""
    return {
        "cagr": cagr(net),
        "gross_cagr": cagr(gross),
        "annualized_return": annualized_return(net),
        "annualized_volatility": annualized_vol(net),
        "sharpe": sharpe(net, rf_daily),
        "gross_sharpe": sharpe(gross, rf_daily),
        "max_drawdown": max_drawdown(net),
        "worst_month": worst_month(net),
        "annualized_turnover": annualized_turnover(turnover),
        "transaction_cost_drag": cagr(gross) - cagr(net),
        "n_days": int(len(net)),
    }


def relative_metrics(net: pd.Series, bench_net: pd.Series) -> dict:
    return {
        "benchmark_relative_return": cagr(net) - cagr(bench_net),
        "tracking_error": tracking_error(net, bench_net),
        "information_ratio": information_ratio(net, bench_net),
    }
