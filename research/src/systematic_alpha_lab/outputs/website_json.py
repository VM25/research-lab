"""Generate the seven website JSON files from the research artifacts.

No metric is hand-written here — everything is read from the computed backtest
and validation results. Equity curves are sampled to month-end and rebased to
100 to keep the payloads small and chart-ready.
"""
from __future__ import annotations

import pandas as pd

from ..backtest.benchmarks import BENCH_LABELS
from ..data.dataset import Dataset
from ..signals.registry import SIGNAL_META, SIGNAL_ORDER
from ..utils.io import write_web_json, write_json

VERDICT_ORDER = ["Survived", "Conditional", "Rejected"]

# Public-facing display names for raw provenance source keys.
SOURCE_DISPLAY = {
    "yahoo": "Yahoo Finance",
    "tiingo": "Tiingo",
    "fred": "FRED",
    "NBER": "NBER",
}


def _source_label(key: str) -> str:
    return SOURCE_DISPLAY.get(key, key)


def _monthly_index(start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    return pd.date_range(start, end, freq="ME")


def _rebased_monthly(values: pd.Series, axis: pd.DatetimeIndex) -> list:
    v = values.reindex(values.index.union(axis)).ffill().reindex(axis)
    first = v.dropna().iloc[0] if v.dropna().size else 1.0
    return [round(float(x / first * 100.0), 3) if pd.notna(x) else None for x in v]


def _drawdown_monthly(values: pd.Series, axis: pd.DatetimeIndex) -> list:
    v = values.reindex(values.index.union(axis)).ffill().reindex(axis)
    dd = v / v.cummax() - 1.0
    return [round(float(x), 4) if pd.notna(x) else None for x in dd]


def build_curves(ds: Dataset, bt: dict) -> dict:
    start = bt["common_start"]
    end = ds.calendar.max()
    axis = _monthly_index(start, end)
    cost_levels = ["low", "base", "high", "stress"]

    strat_curves = {}
    for name in SIGNAL_ORDER:
        r = bt["strategies"][name]
        base = r["base"]
        strat_curves[name] = {
            "net": _rebased_monthly(base.values, axis),
            "gross": _rebased_monthly(r["gross"].values, axis),
            "drawdown": _drawdown_monthly(base.values, axis),
            "net_by_cost": {lvl: _rebased_monthly(r[lvl].values, axis) for lvl in cost_levels},
        }
    bench_curves = {k: _rebased_monthly(v.values, axis) for k, v in bt["benchmarks"].items()}

    return {
        "dates": [d.strftime("%Y-%m") for d in axis],
        "strategies": strat_curves,
        "benchmarks": bench_curves,
    }


def _key_metrics(m: dict, tt: dict) -> dict:
    return {
        "cagr": m["cagr"],
        "annualized_volatility": m["annualized_volatility"],
        "sharpe": m["sharpe"],
        "max_drawdown": m["max_drawdown"],
        "annualized_turnover": m["annualized_turnover"],
        "transaction_cost_drag": m["transaction_cost_drag"],
        "benchmark_relative_return": m["benchmark_relative_return"],
        "out_of_sample_sharpe": tt["test_sharpe"],
        "out_of_sample_cagr": tt["test_cagr"],
        "gross_cagr": m["gross_cagr"],
    }


def generate_website_json(ds: Dataset, bt: dict, val: dict) -> None:
    sm = {m["signal_family"]: m for m in bt["strategy_metrics"]}
    tt = {r["signal_family"]: r for r in val["train_test"]}
    cls = {c["signal_family"]: c for c in val["classifications"]}
    fm = {f["signal_family"]: f for f in val["failure_modes"]}
    cs = _group(val["cost_sensitivity"])
    pr = _group(val["parameter_robustness"])
    rs = _group(val["rebalance_sensitivity"])
    reg = _group(val["regime_breakdown"])
    cr = _group(val["crisis"])
    cmp = _group(bt["benchmark_comparison"])
    wf = _group(val["walk_forward"])

    meta = ds.universe_meta
    groups_present = sorted({a["group"] for a in meta["assets"]})

    # ---------- overview.json ----------
    overview = {
        "project_name": "Systematic Alpha Research Lab",
        "tagline": "Does this signal survive reality?",
        "research_question": val["conclusions"]["research_question"],
        "headline": ("Testing whether systematic alpha signals survive costs, "
                     "out-of-sample validation, and market stress."),
        "signal_count": len(SIGNAL_ORDER),
        "universe_summary": {
            "asset_count": len(meta["assets"]),
            "asset_groups": len(groups_present),
            "sample_start": meta["actual_start"],
            "sample_end": meta["actual_end"],
            "trading_days": meta["trading_days"],
        },
        "validation_standard": [
            "Net-of-cost performance", "Benchmark comparison", "Train/test split",
            "Walk-forward validation", "Cost sensitivity", "Parameter robustness",
            "Rebalance sensitivity", "Regime & crisis stress",
        ],
        "primary_cost_bps": bt["base_cost"],
        "verdict_summary": val["conclusions"]["verdict_counts"],
        "verdict_headline": val["conclusions"]["headline"],
        "backtest_start": bt["common_start"].strftime("%Y-%m-%d"),
        "data_note": (
            f"Dividend- and split-adjusted close for {len(meta['assets'])} ETFs, "
            f"{meta['actual_start']} to {meta['actual_end']}. The cost-aware backtest "
            f"runs from {bt['common_start'].strftime('%Y-%m')} once a 12-month signal "
            f"history exists, and each ETF enters on its own inception date."
        ),
    }
    write_web_json("overview.json", overview)

    # ---------- data_summary.json ----------
    sources = sorted({_source_label(v["source_name"]) for v in ds.provenance.values()})
    late_start = [a["ticker"] for a in meta["assets"] if a["first_date"] > meta["actual_start"]]
    data_summary = {
        "universe": [{"ticker": a["ticker"], "name": a["name"], "group": a["group"],
                      "first_date": a["first_date"], "last_date": a["last_date"],
                      "source": _source_label(a.get("source", "yahoo")),
                      "status": a.get("status", "included")}
                     for a in meta["assets"]],
        "asset_groups": groups_present,
        "sample_period": {
            "start": meta["actual_start"], "end": meta["actual_end"],
            "trading_days": meta["trading_days"],
            "note": (
                f"Span of the daily price panel on the {meta['calendar_reference']} trading "
                f"calendar. {len(meta['assets']) - len(late_start)} ETFs cover the full span; "
                f"{', '.join(late_start)} start later (see first dates) and each ETF enters "
                f"the strategy on its own inception once it has the required signal history."
            ),
        },
        "backtest_period": {
            "start": bt["common_start"].strftime("%Y-%m-%d"), "end": meta["actual_end"],
            "note": ("Strategies and benchmarks share this calendar, which begins when a "
                     "12-month momentum history is first available."),
        },
        "sources": sources,
        "source_summary": (
            "ETF prices from Yahoo Finance (dividend- and split-adjusted close). Macro "
            "series from Yahoo Finance (VIX, 10-year and 13-week Treasury yields) and FRED "
            "(CPI). NBER recession dates and fixed crisis windows are used only for "
            "retrospective regime labeling. Portfolio returns use adjusted close as a "
            "total-return approximation."
        ),
        "return_basis": meta["return_basis"],
        "cash_handling": meta.get("cash_handling", ""),
        "no_lookahead_rule": meta["no_lookahead_rule"],
        "excluded_assets": ds.quality["excluded_tickers"],
        "cost_model": {
            "description": "Cost = turnover x bps / 10000, applied as a return drag.",
            "turnover_definition": ("Turnover = sum of absolute weight changes at a rebalance "
                                    "(total traded notional / NAV, including both buys and sells)."),
            "scenarios": [{"scenario": s, "cost_bps": bt["cost_map"][s]}
                          for s in ["low", "base", "high", "stress"]],
            "primary_cost_bps": bt["base_cost"],
        },
        "regime_note": ("Regime and crisis labels are used for retrospective validation, not "
                        "live trading decisions. Macro inputs are lagged so labels use only "
                        "information observable at the time."),
        "benchmarks": [{"key": k, "name": v} for k, v in BENCH_LABELS.items()],
        "train_test_split": {"train": "2006-01 to 2016-12", "test": "2017-01 to present"},
        "walk_forward_windows": len({(r["train_start"], r["test_start"]) for r in val["walk_forward"]}),
        "primary_strategy_rules": ["Long-only", "No leverage", "No shorting",
                                   "Monthly rebalance", "Cash fallback"],
        "limitations": [
            "Long-only ETF research over one universe and window; not a live trading system.",
            "Transaction costs are modeled as a fixed-bps turnover drag; bid-ask spread, "
            "market impact, and intraday execution are not separately modeled.",
            "Adjusted-close returns approximate total return, assuming dividends are "
            "reinvested without tax.",
            "Cash / T-bill exposure uses the 13-week Treasury-bill yield, not a cash ETF.",
            "Regime and crisis labels are retrospective validation tools, not tradable signals.",
            "Verdicts are qualitative research classifications, not statistical proof of "
            "alpha. Parameter grids are intentionally limited and predeclared to reduce "
            "data-mining risk.",
            "This is research, not investment advice.",
        ],
    }
    write_web_json("data_summary.json", data_summary)

    # ---------- signal_cases.json ----------
    cases = []
    for name in SIGNAL_ORDER:
        md = SIGNAL_META[name]
        m = sm[name]
        c = cls[name]
        cases.append({
            "signal_name": md["signal_name"],
            "signal_family": name,
            "plain_english_hypothesis": md["plain_english_hypothesis"],
            "hypothesis": md["hypothesis"],
            "formula": md["formula"],
            "formula_short": md["formula_short"],
            "portfolio_rule": md["portfolio_rule"],
            "expected_strength": md["expected_strength"],
            "expected_weakness": md["expected_weakness"],
            "lookback_window": md["lookback_window"],
            "rebalance_frequency": md["rebalance_frequency"],
            "weighting_method": m["weighting_method"],
            "key_metrics": _key_metrics(m, tt[name]),
            "benchmark_comparison": cmp[name],
            "stress_test_summary": {
                "cost_sensitivity": cs[name],
                "parameter_robustness": pr.get(name, []),
                "rebalance_sensitivity": rs[name],
                "regimes": reg[name],
                "crisis": cr[name],
                "walk_forward": wf[name],
                "train_test": tt[name],
            },
            "verdict": c["classification"],
            "verdict_reason": c["final_research_note"],
            "primary_evidence": c["primary_evidence"],
            "weaknesses": c["weaknesses"],
            "best_use_case": c["best_use_case"],
            "failure_modes": fm[name]["failure_modes"],
        })
    write_web_json("signal_cases.json", cases)

    # ---------- backtest_summary.json ----------
    backtest_summary = {
        "common_start": bt["common_start"].strftime("%Y-%m-%d"),
        "base_cost_bps": bt["base_cost"],
        "cost_scenarios": [{"scenario": s, "cost_bps": bt["cost_map"][s]}
                           for s in ["low", "base", "high", "stress"]],
        "strategies": bt["strategy_metrics"],
        "benchmarks": bt["benchmark_metrics"],
        "comparison": bt["benchmark_comparison"],
        "benchmark_labels": BENCH_LABELS,
        "curves": build_curves(ds, bt),
    }
    write_web_json("backtest_summary.json", backtest_summary)

    # ---------- validation_summary.json ----------
    validation_summary = {
        "train_test": val["train_test"],
        "walk_forward": val["walk_forward"],
        "cost_sensitivity": val["cost_sensitivity"],
        "parameter_robustness": val["parameter_robustness"],
        "rebalance_sensitivity": val["rebalance_sensitivity"],
        "regime_breakdown": val["regime_breakdown"],
        "crisis_period_analysis": val["crisis"],
        "conclusions": val["conclusions"],
    }
    write_web_json("validation_summary.json", validation_summary)

    # ---------- classification_board.json ----------
    board = {v: [] for v in VERDICT_ORDER}
    for name in SIGNAL_ORDER:
        c = cls[name]
        m = sm[name]
        board[c["classification"]].append({
            "signal_name": c["strategy_name"],
            "signal_family": name,
            "one_line_result": f"Net Sharpe {m['sharpe']:.2f}, max drawdown "
                               f"{m['max_drawdown']*100:.0f}%, "
                               f"{m['cagr']*100:.1f}% CAGR net of 5 bps.",
            "primary_evidence": c["primary_evidence"][0],
            "main_weakness": c["weaknesses"][0] if c["weaknesses"] else "",
            "best_use_case": c["best_use_case"],
            "final_research_note": c["final_research_note"],
            "verdict": c["classification"],
        })
    write_web_json("classification_board.json",
                   {"order": VERDICT_ORDER, "counts": val["conclusions"]["verdict_counts"],
                    "groups": board})

    # ---------- failure_modes.json ----------
    write_web_json("failure_modes.json", {
        "allowed_failure_types": [
            "cost_failure", "turnover_failure", "parameter_fragility",
            "regime_dependency", "drawdown_failure", "out_of_sample_failure",
            "benchmark_underperformance",
        ],
        "signals": val["failure_modes"],
    })

    # mirror classification + conclusions into outputs/validation for the report
    write_json("validation", "research_conclusions.json", val["conclusions"])


def _group(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(r["signal_family"], []).append(r)
    return out
