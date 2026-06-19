"""Expanding-window walk-forward: choose params on train, freeze, test."""
from __future__ import annotations

import pandas as pd

from ..backtest.benchmarks import run_benchmarks
from ..backtest.runner import run_strategy
from ..data.dataset import Dataset
from ..signals.registry import SIGNAL_META, SIGNAL_ORDER
from ..utils.io import load_config, write_json
from .common import window_metrics, cumulative_return
from .variants import param_grid, build_variant


def run_walk_forward(ds: Dataset, common_start: pd.Timestamp, method_map: dict,
                     constraints: dict, base_cost: float) -> list[dict]:
    vcfg = load_config("validation_params")
    sig_cfg = load_config("signal_params")
    windows = vcfg["walk_forward"]["windows"]
    rb = "monthly"
    rows = []

    for name in SIGNAL_ORDER:
        method = method_map[name]
        grid = param_grid(name, sig_cfg)
        meta = SIGNAL_META[name]
        for win in windows:
            tr_s = max(pd.Timestamp(win["train_start"]), common_start)
            tr_e = pd.Timestamp(win["train_end"])
            te_s = pd.Timestamp(win["test_start"])
            te_e = pd.Timestamp(win["test_end"]) if win["test_end"] else None

            # --- choose parameters on the training window (max train Sharpe) ---
            if grid:
                best_name, best_sharpe, best_sig = None, -1e9, None
                for vname, params in grid.items():
                    sig = build_variant(ds, name, params, rb, sig_cfg)
                    res = run_strategy(ds, sig, method, constraints, rb, base_cost,
                                       common_start, start=str(tr_s.date()),
                                       end=str(tr_e.date()))
                    m = window_metrics(res, ds.rf_daily, tr_s, tr_e)
                    sh = m["sharpe"] if m["sharpe"] == m["sharpe"] else -1e9
                    if sh > best_sharpe:
                        best_name, best_sharpe, best_sig = vname, sh, sig
                selected = best_name
                test_sig = best_sig
            else:
                selected = sig_cfg.get(name, {}).get("default_param", "default")
                test_sig = build_variant(ds, name, {}, rb, sig_cfg)

            # --- freeze and test on the out-of-sample window ---
            test_res = run_strategy(ds, test_sig, method, constraints, rb, base_cost,
                                    common_start, start=str(te_s.date()),
                                    end=str(te_e.date()) if te_e else None)
            tm = window_metrics(test_res, ds.rf_daily, te_s, te_e)

            spy = run_benchmarks(ds, base_cost, common_start)["spy_buy_hold"]
            spy_net = spy.net_returns
            spy_net = spy_net[(spy_net.index >= te_s) & (
                spy_net.index <= (te_e if te_e else spy_net.index.max()))]
            strat_cum = cumulative_return(
                test_res.net_returns[(test_res.net_returns.index >= te_s)])
            excess = strat_cum - cumulative_return(spy_net)

            passed = (tm["sharpe"] == tm["sharpe"]) and tm["sharpe"] > 0.2 and tm["cagr"] > 0
            rows.append({
                "strategy_name": meta["signal_name"],
                "signal_family": name,
                "train_start": tr_s.strftime("%Y-%m-%d"),
                "train_end": tr_e.strftime("%Y-%m-%d"),
                "test_start": te_s.strftime("%Y-%m-%d"),
                "test_end": (te_e.strftime("%Y-%m-%d") if te_e
                             else test_res.net_returns.index.max().strftime("%Y-%m-%d")),
                "selected_parameters": selected,
                "test_cagr": tm["cagr"],
                "test_sharpe": tm["sharpe"],
                "test_max_drawdown": tm["max_drawdown"],
                "test_turnover": tm["annualized_turnover"],
                "test_cost_drag": tm["cost_drag"],
                "test_excess_return_vs_benchmark": excess,
                "window_result": "pass" if passed else "fail",
                "window_note": (f"OOS Sharpe {tm['sharpe']:.2f}, "
                                f"{'beat' if excess > 0 else 'trailed'} SPY by "
                                f"{abs(excess)*100:.1f}% over the window."),
            })
    write_json("validation", "walk_forward_results.json", rows)
    return rows
