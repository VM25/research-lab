"""Train/test split: in-sample fitting period vs out-of-sample evidence."""
from __future__ import annotations

import pandas as pd

from ..backtest.engine import BacktestResult
from ..signals.registry import SIGNAL_META, SIGNAL_ORDER
from ..utils.io import load_config, write_json
from .common import window_metrics


def run_train_test(strat_results: dict[str, dict[str, BacktestResult]],
                   rf_daily: pd.Series, common_start: pd.Timestamp) -> list[dict]:
    cfg = load_config("validation_params")["train_test"]
    tr_start = max(pd.Timestamp(cfg["train_start"]), common_start)
    tr_end = pd.Timestamp(cfg["train_end"])
    te_start = pd.Timestamp(cfg["test_start"])

    rows = []
    for name in SIGNAL_ORDER:
        base = strat_results[name]["base"]
        tr = window_metrics(base, rf_daily, tr_start, tr_end)
        te = window_metrics(base, rf_daily, te_start, None)
        held = (te["sharpe"] >= 0.5 * tr["sharpe"]) if tr["sharpe"] and tr["sharpe"] > 0 else te["sharpe"] > 0
        note = (f"Out-of-sample Sharpe {te['sharpe']:.2f} vs in-sample {tr['sharpe']:.2f}; "
                + ("held up" if held else "weakened") + " out-of-sample.")
        rows.append({
            "strategy_name": SIGNAL_META[name]["signal_name"],
            "signal_family": name,
            "train_start": tr_start.strftime("%Y-%m-%d"),
            "train_end": tr_end.strftime("%Y-%m-%d"),
            "test_start": te_start.strftime("%Y-%m-%d"),
            "test_end": base.net_returns.index.max().strftime("%Y-%m-%d"),
            "train_cagr": tr["cagr"], "test_cagr": te["cagr"],
            "train_sharpe": tr["sharpe"], "test_sharpe": te["sharpe"],
            "train_max_drawdown": tr["max_drawdown"], "test_max_drawdown": te["max_drawdown"],
            "train_turnover": tr["annualized_turnover"], "test_turnover": te["annualized_turnover"],
            "train_cost_drag": tr["cost_drag"], "test_cost_drag": te["cost_drag"],
            "out_of_sample_held": bool(held),
            "test_verdict_note": note,
        })
    write_json("validation", "train_test_results.json", rows)
    return rows
