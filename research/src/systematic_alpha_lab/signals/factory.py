"""Compute signals from the dataset and write signal outputs."""
from __future__ import annotations

import pandas as pd

from ..data.dataset import Dataset
from ..utils.io import load_config, write_parquet, write_json
from . import (time_series_momentum, cross_sectional_momentum,
               short_term_reversal, volatility_scaled_momentum, ensemble)
from .base import SignalResult
from .registry import SIGNAL_META, SIGNAL_ORDER

_PARQUET_NAME = {
    "time_series_momentum": "time_series_momentum_scores.parquet",
    "cross_sectional_momentum": "cross_sectional_momentum_scores.parquet",
    "short_term_reversal": "short_term_reversal_scores.parquet",
    "volatility_scaled_momentum": "volatility_scaled_momentum_scores.parquet",
    "ensemble": "ensemble_scores.parquet",
}


def compute_all_signals(ds: Dataset, cfg: dict | None = None
                        ) -> dict[str, SignalResult]:
    cfg = cfg or load_config("signal_params")
    rb = cfg["rebalance_frequency"]
    prices, rets = ds.prices, ds.returns

    results: dict[str, SignalResult] = {}
    results["time_series_momentum"] = time_series_momentum.compute(
        prices, rets, cfg["time_series_momentum"], rb)
    results["cross_sectional_momentum"] = cross_sectional_momentum.compute(
        prices, rets, cfg["cross_sectional_momentum"], rb)
    results["short_term_reversal"] = short_term_reversal.compute(
        prices, rets, cfg["short_term_reversal"], rb)
    results["volatility_scaled_momentum"] = volatility_scaled_momentum.compute(
        prices, rets, cfg["volatility_scaled_momentum"], rb,
        mom_params=cfg["time_series_momentum"])
    results["ensemble"] = ensemble.compute(
        results, cfg["ensemble"], rb)
    return results


def write_signal_outputs(results: dict[str, SignalResult]) -> None:
    for name, res in results.items():
        write_parquet("signals", _PARQUET_NAME[name], res.to_long())

    summary = []
    for name in SIGNAL_ORDER:
        m = SIGNAL_META[name]
        summary.append({
            "signal_name": m["signal_name"],
            "signal_family": m["signal_family"],
            "hypothesis": m["hypothesis"],
            "formula": m["formula"],
            "lookback_window": m["lookback_window"],
            "rebalance_frequency": m["rebalance_frequency"],
            "portfolio_rule": m["portfolio_rule"],
            "expected_strength": m["expected_strength"],
            "expected_weakness": m["expected_weakness"],
            "primary_failure_mode": m["primary_failure_mode"],
        })
    write_json("signals", "signal_summary.json", summary)
