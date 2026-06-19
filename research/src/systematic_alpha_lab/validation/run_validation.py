"""Run the full validation suite and classification in one call."""
from __future__ import annotations

import pandas as pd

from ..data.dataset import Dataset
from . import robustness as R
from . import train_test as TT
from . import walk_forward as WF
from . import classification as CL


def run_validation(ds: Dataset, bt: dict) -> dict:
    strat = bt["strategies"]
    rf = ds.rf_daily
    common_start = bt["common_start"]
    method_map = bt["method_map"]
    constraints = bt["constraints"]
    base_cost = bt["base_cost"]
    cost_map = bt["cost_map"]
    spy = bt["benchmarks"]["spy_buy_hold"]

    train_test = TT.run_train_test(strat, rf, common_start)
    walk_forward = WF.run_walk_forward(ds, common_start, method_map, constraints, base_cost)
    cost_sensitivity = R.cost_sensitivity(strat, rf, cost_map)
    parameter_robustness = R.parameter_robustness(ds, method_map, constraints, base_cost, common_start)
    rebalance_sensitivity = R.rebalance_sensitivity(ds, strat, method_map, constraints, base_cost)
    regime_breakdown = R.regime_breakdown(ds, strat, rf)
    crisis = R.crisis_analysis(ds, strat, spy)

    classifications, failure_modes, conclusions = CL.classify_all(
        bt["strategy_metrics"], bt["benchmark_metrics"], train_test, walk_forward,
        cost_sensitivity, parameter_robustness, regime_breakdown, crisis)

    return {
        "train_test": train_test,
        "walk_forward": walk_forward,
        "cost_sensitivity": cost_sensitivity,
        "parameter_robustness": parameter_robustness,
        "rebalance_sensitivity": rebalance_sensitivity,
        "regime_breakdown": regime_breakdown,
        "crisis": crisis,
        "classifications": classifications,
        "failure_modes": failure_modes,
        "conclusions": conclusions,
    }
