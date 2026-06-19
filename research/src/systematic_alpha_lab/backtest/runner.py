"""Run all strategies and benchmarks, assemble metric/JSON/parquet outputs."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..data.dataset import Dataset
from ..signals.base import SignalResult
from ..signals.registry import SIGNAL_META, SIGNAL_ORDER
from ..portfolio.rebalancing import build_weight_schedule
from ..utils.dates import rebalance_dates
from ..utils.io import load_config, write_json, write_parquet
from . import metrics as M
from .benchmarks import run_benchmarks, BENCH_LABELS
from .costs import COST_SCENARIO_ORDER
from .engine import run_backtest, BacktestResult, CASH

MOM_LOOKBACK = 273   # 252 + 21 skip: enough history for every signal


def common_backtest_start(calendar: pd.DatetimeIndex, rebalance_freq: str,
                          min_pos: int = MOM_LOOKBACK) -> pd.Timestamp:
    rb = rebalance_dates(calendar, rebalance_freq)
    positions = calendar.searchsorted(rb)
    eligible = rb[positions >= min_pos]
    return eligible.min()


def run_strategy(ds: Dataset, signal: SignalResult, method: str, constraints: dict,
                 rebalance_freq: str, cost_bps: float, common_start: pd.Timestamp,
                 start: str | None = None, end: str | None = None) -> BacktestResult:
    sched = build_weight_schedule(signal, ds.calendar, ds.tradable, ds.groups,
                                  method, constraints, rebalance_freq)
    sched = sched[sched.index >= common_start]
    win_start = start or str(common_start.date())
    return run_backtest(sched, ds.returns_with_cash, cost_bps, start=win_start, end=end)


def _strategy_note(core: dict, rel: dict) -> str:
    drag = core["transaction_cost_drag"]
    rr = rel["benchmark_relative_return"]
    bits = [f"net Sharpe {core['sharpe']:.2f}",
            f"max DD {core['max_drawdown']*100:.0f}%",
            f"cost drag {drag*100:.2f}%/yr"]
    bits.append("ahead of SPY" if rr > 0 else "behind SPY")
    return "; ".join(bits)


def run_all(ds: Dataset, signals: dict[str, SignalResult]) -> dict:
    bt = load_config("backtest_params")
    constraints = bt["constraints"]
    rb_freq = "monthly"
    cost_map = bt["costs_bps"]
    base_cost = cost_map[bt["primary_cost"]]
    method_map = bt["weighting_method"]

    common_start = common_backtest_start(ds.calendar, rb_freq)

    # --- benchmarks at base cost ---
    bench = run_benchmarks(ds, base_cost, common_start, rebalance_freq=rb_freq)
    spy = bench["spy_buy_hold"]

    # --- strategies: full set of cost scenarios + gross ---
    strat_results: dict[str, dict[str, BacktestResult]] = {}
    for name in SIGNAL_ORDER:
        method = method_map[name]
        per_cost: dict[str, BacktestResult] = {}
        per_cost["gross"] = run_strategy(ds, signals[name], method, constraints,
                                         rb_freq, 0.0, common_start)
        for lvl in COST_SCENARIO_ORDER:
            per_cost[lvl] = run_strategy(ds, signals[name], method, constraints,
                                         rb_freq, cost_map[lvl], common_start)
        strat_results[name] = per_cost

    # ---- assemble metrics ----
    strategy_metrics, benchmark_comparison = [], []
    returns_rows, values_rows, weights_rows = [], [], []
    turnover_rows, cost_rows, dd_rows = [], [], []

    for name in SIGNAL_ORDER:
        r = strat_results[name]
        base, gross = r["base"], r["gross"]
        core = M.core_metrics(base.net_returns, gross.net_returns, ds.rf_daily, base.turnover)
        rel = M.relative_metrics(base.net_returns, spy.net_returns)
        meta = SIGNAL_META[name]
        strategy_metrics.append({
            "strategy_name": meta["signal_name"],
            "signal_family": name,
            "rebalance_frequency": rb_freq,
            "cost_bps": base_cost,
            "weighting_method": method_map[name],
            "cagr": core["cagr"],
            "gross_cagr": core["gross_cagr"],
            "annualized_volatility": core["annualized_volatility"],
            "sharpe": core["sharpe"],
            "gross_sharpe": core["gross_sharpe"],
            "max_drawdown": core["max_drawdown"],
            "worst_month": core["worst_month"],
            "annualized_turnover": core["annualized_turnover"],
            "transaction_cost_drag": core["transaction_cost_drag"],
            "benchmark_relative_return": rel["benchmark_relative_return"],
            "information_ratio": rel["information_ratio"],
            "classification_input_note": _strategy_note(core, rel),
        })

        # per-benchmark comparison
        for bname, bres in bench.items():
            bcore = M.core_metrics(bres.net_returns, bres.gross_returns, ds.rf_daily, bres.turnover)
            rel_b = M.relative_metrics(base.net_returns, bres.net_returns)
            benchmark_comparison.append({
                "strategy_name": meta["signal_name"],
                "signal_family": name,
                "benchmark_name": BENCH_LABELS[bname],
                "benchmark_key": bname,
                "strategy_cagr": core["cagr"],
                "benchmark_cagr": bcore["cagr"],
                "strategy_sharpe": core["sharpe"],
                "benchmark_sharpe": bcore["sharpe"],
                "strategy_max_drawdown": core["max_drawdown"],
                "benchmark_max_drawdown": bcore["max_drawdown"],
                "excess_return": rel_b["benchmark_relative_return"],
                "information_ratio": rel_b["information_ratio"],
                "comparison_note": ("beats" if rel_b["benchmark_relative_return"] > 0
                                    else "trails") + f" {BENCH_LABELS[bname]} by "
                                   f"{abs(rel_b['benchmark_relative_return'])*100:.1f}%/yr",
            })

        # parquet rows (base cost primary)
        label = meta["signal_name"]
        for dt in base.net_returns.index:
            returns_rows.append((dt, label, base.gross_returns[dt], base.net_returns[dt]))
            values_rows.append((dt, label, base.values[dt], base.gross_values[dt]))
            turnover_rows.append((dt, label, base.turnover[dt]))
            cost_rows.append((dt, label, base.costs[dt]))
            dd_rows.append((dt, label, base.drawdown[dt]))
        w = base.weights.copy()
        w.insert(0, "strategy_name", label)
        weights_rows.append(w.reset_index().rename(columns={"index": "date"}))

    # benchmark metrics
    benchmark_metrics = []
    for bname, bres in bench.items():
        bcore = M.core_metrics(bres.net_returns, bres.gross_returns, ds.rf_daily, bres.turnover)
        benchmark_metrics.append({
            "benchmark_name": BENCH_LABELS[bname],
            "benchmark_key": bname,
            "cagr": bcore["cagr"],
            "annualized_volatility": bcore["annualized_volatility"],
            "sharpe": bcore["sharpe"],
            "max_drawdown": bcore["max_drawdown"],
            "annualized_turnover": bcore["annualized_turnover"],
        })

    # ---- write outputs ----
    write_json("backtests", "strategy_metrics.json", strategy_metrics)
    write_json("backtests", "benchmark_metrics.json", benchmark_metrics)
    write_json("backtests", "benchmark_comparison.json", benchmark_comparison)

    write_parquet("backtests", "portfolio_returns.parquet",
                  pd.DataFrame(returns_rows, columns=["date", "strategy_name", "gross_return", "net_return"]))
    write_parquet("backtests", "portfolio_values.parquet",
                  pd.DataFrame(values_rows, columns=["date", "strategy_name", "net_value", "gross_value"]))
    write_parquet("backtests", "turnover.parquet",
                  pd.DataFrame(turnover_rows, columns=["date", "strategy_name", "turnover"]))
    write_parquet("backtests", "transaction_costs.parquet",
                  pd.DataFrame(cost_rows, columns=["date", "strategy_name", "transaction_cost"]))
    write_parquet("backtests", "drawdowns.parquet",
                  pd.DataFrame(dd_rows, columns=["date", "strategy_name", "drawdown"]))
    write_parquet("backtests", "portfolio_weights.parquet", pd.concat(weights_rows, ignore_index=True))

    return {
        "common_start": common_start,
        "base_cost": base_cost,
        "cost_map": cost_map,
        "strategies": strat_results,
        "benchmarks": bench,
        "strategy_metrics": strategy_metrics,
        "benchmark_metrics": benchmark_metrics,
        "benchmark_comparison": benchmark_comparison,
        "method_map": method_map,
        "constraints": constraints,
    }
