"""Build parameter/rebalance variants of each signal for robustness testing."""
from __future__ import annotations

import pandas as pd

from ..data.dataset import Dataset
from ..signals import (time_series_momentum, cross_sectional_momentum,
                       short_term_reversal, volatility_scaled_momentum, ensemble)
from ..signals.base import SignalResult


def param_grid(family: str, sig_cfg: dict) -> dict[str, dict]:
    """variant_name -> full parameter dict for the family (defaults + override)."""
    fam = sig_cfg[family]
    grid = fam.get("robustness_grid", {})
    out: dict[str, dict] = {}
    for vname, override in grid.items():
        params = {k: v for k, v in fam.items() if k not in ("robustness_grid",)}
        params.update(override)
        out[vname] = params
    return out


def build_variant(ds: Dataset, family: str, params: dict, rebalance: str,
                  sig_cfg: dict) -> SignalResult:
    prices, rets = ds.prices, ds.returns
    if family == "time_series_momentum":
        return time_series_momentum.compute(prices, rets, params, rebalance)
    if family == "cross_sectional_momentum":
        return cross_sectional_momentum.compute(prices, rets, params, rebalance)
    if family == "short_term_reversal":
        return short_term_reversal.compute(prices, rets, params, rebalance)
    if family == "volatility_scaled_momentum":
        return volatility_scaled_momentum.compute(
            prices, rets, params, rebalance, mom_params=sig_cfg["time_series_momentum"])
    if family == "ensemble":
        members = {}
        members["time_series_momentum"] = time_series_momentum.compute(
            prices, rets, sig_cfg["time_series_momentum"], rebalance)
        members["cross_sectional_momentum"] = cross_sectional_momentum.compute(
            prices, rets, sig_cfg["cross_sectional_momentum"], rebalance)
        members["short_term_reversal"] = short_term_reversal.compute(
            prices, rets, sig_cfg["short_term_reversal"], rebalance)
        members["volatility_scaled_momentum"] = volatility_scaled_momentum.compute(
            prices, rets, sig_cfg["volatility_scaled_momentum"], rebalance,
            mom_params=sig_cfg["time_series_momentum"])
        return ensemble.compute(members, sig_cfg["ensemble"], rebalance)
    raise ValueError(family)
