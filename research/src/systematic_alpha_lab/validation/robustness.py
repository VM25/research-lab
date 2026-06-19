"""Robustness suite: cost, parameter, rebalance, regime and crisis tests."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..backtest import metrics as M
from ..backtest.engine import BacktestResult
from ..backtest.runner import run_strategy, common_backtest_start
from ..data.dataset import Dataset
from ..signals.registry import SIGNAL_META, SIGNAL_ORDER
from ..utils.io import load_config, write_json
from .common import window_metrics, cumulative_return
from .regimes import label_regimes, REGIME_ORDER
from .variants import param_grid, build_variant

CASH_CAGR_REF = 0.015   # ~T-bill; used only for short qualitative labels


def _label(net_sharpe: float, net_cagr: float) -> str:
    if net_sharpe != net_sharpe:
        return "weak"
    if net_sharpe >= 0.4 and net_cagr > CASH_CAGR_REF:
        return "viable"
    if net_sharpe >= 0.1:
        return "marginal"
    return "weak"


# --------------------------------------------------------------------------- #
def cost_sensitivity(strat_results: dict[str, dict[str, BacktestResult]],
                     rf_daily: pd.Series, cost_map: dict) -> list[dict]:
    order = ["low", "base", "high", "stress"]
    rows = []
    for name in SIGNAL_ORDER:
        per_cost = strat_results[name]
        gross = per_cost["gross"]
        gcagr = M.cagr(gross.net_returns)
        gsharpe = M.sharpe(gross.net_returns, rf_daily)
        for lvl in order:
            res = per_cost[lvl]
            ncagr = M.cagr(res.net_returns)
            nsharpe = M.sharpe(res.net_returns, rf_daily)
            rows.append({
                "strategy_name": SIGNAL_META[name]["signal_name"],
                "signal_family": name,
                "cost_bps": cost_map[lvl],
                "scenario": lvl,
                "gross_cagr": gcagr,
                "net_cagr": ncagr,
                "gross_sharpe": gsharpe,
                "net_sharpe": nsharpe,
                "annual_turnover": M.annualized_turnover(res.turnover),
                "cost_drag": gcagr - ncagr,
                "classification_at_cost_level": _label(nsharpe, ncagr),
            })
    write_json("validation", "cost_sensitivity.json", rows)
    return rows


# --------------------------------------------------------------------------- #
def parameter_robustness(ds: Dataset, method_map: dict, constraints: dict,
                         base_cost: float, common_start: pd.Timestamp) -> list[dict]:
    sig_cfg = load_config("signal_params")
    rb = "monthly"
    rows = []
    for name in SIGNAL_ORDER:
        grid = param_grid(name, sig_cfg)
        if not grid:
            continue
        method = method_map[name]
        # baseline (default param) sharpe for fragility comparison
        sharpes = {}
        per_variant = {}
        for vname, params in grid.items():
            sig = build_variant(ds, name, params, rb, sig_cfg)
            res = run_strategy(ds, sig, method, constraints, rb, base_cost, common_start)
            m = window_metrics(res, ds.rf_daily)
            rel = M.relative_metrics(res.net_returns,
                                     _spy_cache(ds, base_cost, common_start).net_returns)
            sharpes[vname] = m["sharpe"]
            per_variant[vname] = (m, rel)
        positive = [s for s in sharpes.values() if s == s and s > 0.1]
        robust = len(positive) >= max(2, int(0.6 * len(sharpes)))
        for vname, (m, rel) in per_variant.items():
            rows.append({
                "strategy_name": SIGNAL_META[name]["signal_name"],
                "signal_family": name,
                "parameter_set": vname,
                "cagr": m["cagr"],
                "sharpe": m["sharpe"],
                "max_drawdown": m["max_drawdown"],
                "turnover": m["annualized_turnover"],
                "cost_drag": m["cost_drag"],
                "benchmark_relative_return": rel["benchmark_relative_return"],
                "parameter_result": "stable" if robust else "fragile",
            })
    write_json("validation", "parameter_robustness.json", rows)
    return rows


_SPY_CACHE: dict = {}


def _spy_cache(ds, base_cost, common_start):
    key = (base_cost, str(common_start.date()))
    if key not in _SPY_CACHE:
        from ..backtest.benchmarks import run_benchmarks
        _SPY_CACHE[key] = run_benchmarks(ds, base_cost, common_start)["spy_buy_hold"]
    return _SPY_CACHE[key]


# --------------------------------------------------------------------------- #
def rebalance_sensitivity(ds: Dataset, signals: dict, method_map: dict,
                          constraints: dict, base_cost: float) -> list[dict]:
    sig_cfg = load_config("signal_params")
    rows = []
    for name in SIGNAL_ORDER:
        method = method_map[name]
        for freq in ["weekly", "monthly", "quarterly"]:
            cstart = common_backtest_start(ds.calendar, freq)
            sig = build_variant(ds, name, _default_params(name, sig_cfg), freq, sig_cfg)
            res = run_strategy(ds, sig, method, constraints, freq, base_cost, cstart)
            m = window_metrics(res, ds.rf_daily)
            rows.append({
                "strategy_name": SIGNAL_META[name]["signal_name"],
                "signal_family": name,
                "rebalance_frequency": freq,
                "net_cagr": m["cagr"],
                "net_sharpe": m["sharpe"],
                "max_drawdown": m["max_drawdown"],
                "annual_turnover": m["annualized_turnover"],
                "cost_drag": m["cost_drag"],
                "classification_at_frequency": _label(m["sharpe"], m["cagr"]),
            })
    write_json("validation", "rebalance_sensitivity.json", rows)
    return rows


def _default_params(name: str, sig_cfg: dict) -> dict:
    fam = sig_cfg.get(name, {})
    return {k: v for k, v in fam.items() if k != "robustness_grid"}


# --------------------------------------------------------------------------- #
def regime_breakdown(ds: Dataset, strat_results: dict, rf_daily: pd.Series
                     ) -> list[dict]:
    params = load_config("validation_params")["regimes"]
    regimes = label_regimes(ds, params)
    rows = []
    for name in SIGNAL_ORDER:
        base = strat_results[name]["base"]
        net = base.net_returns
        gross = base.gross_returns
        turn = base.turnover
        reg = regimes.reindex(net.index).fillna(False)
        for rname in REGIME_ORDER:
            mask = reg[rname].values
            r = net[mask]
            g = gross[mask]
            t = turn[mask]
            if len(r) == 0:
                continue
            ann_ret = float(r.mean() * 252)
            sd = r.std(ddof=0)
            sharpe = float((r - rf_daily.reindex(r.index).fillna(0)).mean() * 252 /
                           (sd * np.sqrt(252))) if sd > 0 else float("nan")
            val = (1 + r).cumprod()
            mdd = float((val / val.cummax() - 1).min())
            rows.append({
                "strategy_name": SIGNAL_META[name]["signal_name"],
                "signal_family": name,
                "regime_name": rname,
                "observation_count": int(len(r)),
                "cagr": ann_ret,
                "sharpe": sharpe,
                "max_drawdown": mdd,
                "hit_rate": float((r > 0).mean()),
                "turnover": M.annualized_turnover(t),
                "cost_drag": M.cagr(g) - M.cagr(r) if len(r) > 30 else float("nan"),
                "regime_note": f"{ann_ret*100:.1f}% annualized over {len(r)} days.",
            })
    write_json("validation", "regime_breakdown.json", rows)
    return rows


# --------------------------------------------------------------------------- #
def crisis_analysis(ds: Dataset, strat_results: dict, spy: BacktestResult
                    ) -> list[dict]:
    periods = load_config("validation_params")["crisis_periods"]
    rows = []
    for name in SIGNAL_ORDER:
        base = strat_results[name]["base"]
        for p in periods:
            s = pd.Timestamp(p["start"])
            e = pd.Timestamp(p["end"]) if p["end"] else base.net_returns.index.max()
            net = base.net_returns[(base.net_returns.index >= s) & (base.net_returns.index <= e)]
            gross = base.gross_returns[(base.gross_returns.index >= s) & (base.gross_returns.index <= e)]
            turn = base.turnover[(base.turnover.index >= s) & (base.turnover.index <= e)]
            spy_net = spy.net_returns[(spy.net_returns.index >= s) & (spy.net_returns.index <= e)]
            if len(net) == 0:
                continue
            cum = cumulative_return(net)
            val = (1 + net).cumprod()
            mdd = float((val / val.cummax() - 1).min())
            rel = cum - cumulative_return(spy_net)
            rows.append({
                "strategy_name": SIGNAL_META[name]["signal_name"],
                "signal_family": name,
                "crisis_period": p["name"],
                "start_date": s.strftime("%Y-%m-%d"),
                "end_date": e.strftime("%Y-%m-%d"),
                "cumulative_return": cum,
                "max_drawdown": mdd,
                "benchmark_relative_return": rel,
                "turnover": M.annualized_turnover(turn),
                "cost_drag": cumulative_return(gross) - cum,
                "crisis_note": (f"{cum*100:+.1f}% vs SPY {cumulative_return(spy_net)*100:+.1f}% "
                                f"({'outperformed' if rel > 0 else 'underperformed'})."),
            })
    write_json("validation", "crisis_period_analysis.json", rows)
    return rows
