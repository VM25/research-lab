"""Final signal classification.

Verdicts (Survived / Conditional / Rejected) are computed from the generated
evidence using documented thresholds — never hand-assigned. The same evidence
drives failure_modes.json and research_conclusions.json.
"""
from __future__ import annotations

import numpy as np

from ..signals.registry import SIGNAL_META, SIGNAL_ORDER
from ..utils.io import load_config, write_json

ALLOWED_FAILURES = [
    "cost_failure", "turnover_failure", "parameter_fragility", "regime_dependency",
    "drawdown_failure", "out_of_sample_failure", "benchmark_underperformance",
]


def _by_family(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(r["signal_family"], []).append(r)
    return out


def _pct(x: float) -> str:
    return f"{x*100:.1f}%"


def classify_all(strategy_metrics, benchmark_metrics, train_test, walk_forward,
                 cost_sensitivity, parameter_robustness, regime_breakdown,
                 crisis) -> tuple[list[dict], list[dict], dict]:
    th = load_config("validation_params")["classification"]
    cash_cagr = next(b["cagr"] for b in benchmark_metrics if b["benchmark_key"] == "cash_proxy")
    sixty = next(b for b in benchmark_metrics if b["benchmark_key"] == "sixty_forty")
    ew = next(b for b in benchmark_metrics if b["benchmark_key"] == "equal_weight_universe")
    spy_b = next(b for b in benchmark_metrics if b["benchmark_key"] == "spy_buy_hold")

    sm = {m["signal_family"]: m for m in strategy_metrics}
    tt = {r["signal_family"]: r for r in train_test}
    wf = _by_family(walk_forward)
    cs = _by_family(cost_sensitivity)
    pr = _by_family(parameter_robustness)
    rb = _by_family(regime_breakdown)
    cr = _by_family(crisis)

    classifications, failure_rows = [], []

    for name in SIGNAL_ORDER:
        meta = SIGNAL_META[name]
        m = sm[name]
        t = tt[name]
        cost_rows = {c["scenario"]: c for c in cs[name]}
        base_cost = cost_rows["base"]
        stress_cost = cost_rows["stress"]

        # --- evidence signals ---
        net_sharpe = m["sharpe"]
        net_cagr = m["cagr"]
        gross_cagr = m["gross_cagr"]
        max_dd = m["max_drawdown"]
        turnover = m["annualized_turnover"]
        test_sharpe = t["test_sharpe"]
        oos_held = t["out_of_sample_held"]
        cost_drag_ratio = (base_cost["cost_drag"] / gross_cagr) if gross_cagr > 0 else 1.0

        wf_rows = wf.get(name, [])
        wf_pass = sum(1 for r in wf_rows if r["window_result"] == "pass")
        wf_total = max(1, len(wf_rows))
        wf_rate = wf_pass / wf_total

        params = pr.get(name, [])
        if params:
            param_hits = sum(1 for r in params if r["sharpe"] == r["sharpe"]
                             and r["sharpe"] > 0.1 and r["benchmark_relative_return"] is not None)
            # count parameter sets that remain economically useful (positive sharpe)
            param_hit_rate = sum(1 for r in params if r["sharpe"] == r["sharpe"]
                                 and r["sharpe"] > 0.1) / len(params)
        else:
            param_hit_rate = 1.0 if net_sharpe > th["survived_min_test_sharpe"] else 0.5

        regime_sharpes = [r["sharpe"] for r in rb.get(name, [])
                          if r["regime_name"] != "Normal" and r["sharpe"] == r["sharpe"]]
        regime_dispersed = (len(regime_sharpes) >= 2 and
                            (max(regime_sharpes) - min(regime_sharpes) > 0.8))

        beats_cash = net_cagr > cash_cagr
        cost_survives = (stress_cost["net_sharpe"] == stress_cost["net_sharpe"]
                         and stress_cost["net_sharpe"] > 0.1
                         and cost_drag_ratio < th["rejected_cost_drag_ratio"])
        excessive_turnover = turnover > th["high_turnover_annual"]
        acceptable_dd = max_dd > -0.35
        robust_params = param_hit_rate >= th["survived_min_param_hit_rate"]
        bench_competitive = net_sharpe >= 0.45 or (beats_cash and max_dd > -0.25)
        # Trails every passive alternative on a risk-adjusted basis.
        benchmark_inferior = (net_sharpe < spy_b["sharpe"] and net_sharpe < sixty["sharpe"]
                              and net_sharpe < ew["sharpe"])

        # --- failure modes ---
        failures = []
        if cost_drag_ratio >= th["rejected_cost_drag_ratio"] or not cost_survives:
            failures.append("cost_failure")
        if excessive_turnover:
            failures.append("turnover_failure")
        if not robust_params:
            failures.append("parameter_fragility")
        if regime_dispersed:
            failures.append("regime_dependency")
        if not acceptable_dd:
            failures.append("drawdown_failure")
        if (test_sharpe <= th["rejected_max_test_sharpe"]) or (not oos_held) or wf_rate < 0.25:
            failures.append("out_of_sample_failure")
        if (not beats_cash) or benchmark_inferior:
            failures.append("benchmark_underperformance")
        failures = [f for f in ALLOWED_FAILURES if f in failures]   # stable order, unique

        # --- verdict ---
        survived = (test_sharpe >= th["survived_min_test_sharpe"] and beats_cash
                    and robust_params and oos_held and cost_survives
                    and not excessive_turnover and acceptable_dd and wf_rate >= 0.5)
        rejected = ((test_sharpe <= th["rejected_max_test_sharpe"])
                    or (not beats_cash)
                    or ("cost_failure" in failures and stress_cost["net_sharpe"] < 0.1)
                    # excessive turnover that still can't beat passive alternatives
                    or (excessive_turnover and benchmark_inferior)
                    # high turnover plus cost-fragility (degrades sharply under stress)
                    or (excessive_turnover and not cost_survives)
                    or wf_rate < 0.25
                    or (not bench_competitive and not acceptable_dd))
        if survived and not rejected:
            verdict = "Survived"
        elif rejected and not survived:
            verdict = "Rejected"
        else:
            verdict = "Conditional"

        # --- evidence + narrative ---
        primary_evidence = [
            f"Net Sharpe {net_sharpe:.2f} at 5 bps with {_pct(max_dd)} max drawdown "
            f"(SPY drew down {_pct(next(b['max_drawdown'] for b in benchmark_metrics if b['benchmark_key']=='spy_buy_hold'))}).",
            f"Out-of-sample (2017+) Sharpe {test_sharpe:.2f} vs in-sample {t['train_sharpe']:.2f}.",
            f"Walk-forward: {wf_pass}/{wf_total} windows passed.",
            f"Survives 25 bps stress at Sharpe {stress_cost['net_sharpe']:.2f}"
            if cost_survives else
            f"At 25 bps costs net Sharpe falls to {stress_cost['net_sharpe']:.2f}.",
        ]
        weaknesses = []
        if "cost_failure" in failures:
            weaknesses.append(f"Transaction costs erase {_pct(base_cost['cost_drag'])}/yr of gross return.")
        if "turnover_failure" in failures:
            weaknesses.append(f"High turnover ({turnover:.1f}x/yr) makes it execution-sensitive.")
        if "parameter_fragility" in failures:
            weaknesses.append("Results depend on the chosen parameter window.")
        if "regime_dependency" in failures:
            weaknesses.append("Performance is uneven across market regimes.")
        if not beats_cash:
            weaknesses.append("Net return does not clear the cash benchmark.")
        if not weaknesses:
            weaknesses = meta["expected_weakness"][:2]

        best_use = _best_use(name, verdict, max_dd, net_sharpe)
        note = _final_note(meta, verdict, net_sharpe, net_cagr, max_dd, test_sharpe,
                           cost_survives, beats_cash)

        classifications.append({
            "strategy_name": meta["signal_name"],
            "signal_family": name,
            "classification": verdict,
            "primary_evidence": primary_evidence,
            "weaknesses": weaknesses,
            "best_use_case": best_use,
            "final_research_note": note,
        })
        failure_rows.append({
            "strategy_name": meta["signal_name"],
            "signal_family": name,
            "failure_modes": failures,
            "primary_failure_mode": meta["primary_failure_mode"],
            "notes": (", ".join(failures) if failures
                      else "No disqualifying failure mode detected."),
        })

    write_json("validation", "signal_classification.json", classifications)
    write_json("validation", "failure_modes.json", failure_rows)

    counts = {"Survived": 0, "Conditional": 0, "Rejected": 0}
    for c in classifications:
        counts[c["classification"]] += 1
    conclusions = {
        "research_question": "Do simple systematic alpha signals survive costs, "
                             "out-of-sample testing, robustness checks, and market stress?",
        "verdict_counts": counts,
        "headline": _headline(counts),
        "key_findings": _key_findings(classifications, sm, cash_cagr),
        "signals_evaluated": len(classifications),
    }
    write_json("validation", "research_conclusions.json", conclusions)
    return classifications, failure_rows, conclusions


def _best_use(name, verdict, max_dd, sharpe):
    if verdict == "Rejected":
        return ("Not recommended as a standalone allocation on this evidence; at most a "
                "low-cost tactical input, never a return-maximizing strategy.")
    base = {
        "time_series_momentum": "Use as a long-only de-risking trend overlay that controls drawdowns, not as a standalone return-maximizing strategy.",
        "cross_sectional_momentum": "Use as a relative-strength allocation sleeve within a diversified book, not as proof of standalone alpha.",
        "short_term_reversal": "Use only as a low-cost tactical timing input, not as a standalone strategy.",
        "volatility_scaled_momentum": "Use as a volatility-control overlay when drawdown control matters more than raw return, not as a return maximizer.",
        "ensemble": "Use as a diversified, lower-variance core blend, not as a single-signal bet or proof of alpha.",
    }
    return base[name]


def _final_note(meta, verdict, sharpe, cagr, max_dd, test_sharpe, cost_survives, beats_cash):
    if verdict == "Survived":
        return (f"{meta['signal_name']} holds up: net Sharpe {sharpe:.2f}, "
                f"{_pct(max_dd)} max drawdown, and out-of-sample Sharpe {test_sharpe:.2f}. "
                "It survives realistic costs and parameter variation.")
    if verdict == "Rejected":
        why = "costs and turnover erode it" if not cost_survives else "it does not clear simple benchmarks"
        return (f"{meta['signal_name']} is rejected on this evidence: {why}; "
                f"net Sharpe {sharpe:.2f}, out-of-sample Sharpe {test_sharpe:.2f}.")
    return (f"{meta['signal_name']} is conditional: it adds value mainly through "
            f"risk control (net Sharpe {sharpe:.2f}, {_pct(max_dd)} max drawdown) "
            "rather than raw return, and depends on costs or regime.")


def _headline(counts):
    def was(n):
        return "was" if n == 1 else "were"
    s, c, r = counts["Survived"], counts["Conditional"], counts["Rejected"]
    return (f"Of five signals, {s} survived, "
            f"{c} {was(c)} conditional, and {r} {was(r)} rejected — "
            "discipline, not a single best backtest, separates them.")


def _key_findings(classifications, sm, cash_cagr):
    out = []
    for c in classifications:
        m = sm[c["signal_family"]]
        out.append(f"{c['strategy_name']}: {c['classification']} "
                   f"(net Sharpe {m['sharpe']:.2f}, max DD {_pct(m['max_drawdown'])}).")
    return out
