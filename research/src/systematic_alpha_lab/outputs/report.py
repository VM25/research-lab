"""Generate the concise research report (Markdown) from computed outputs."""
from __future__ import annotations

from ..data.dataset import Dataset
from ..signals.registry import SIGNAL_META, SIGNAL_ORDER
from ..utils.io import out_path


def _pct(x, d=1):
    return f"{x*100:.{d}f}%" if x is not None else "n/a"


def generate_report(ds: Dataset, bt: dict, val: dict) -> str:
    sm = {m["signal_family"]: m for m in bt["strategy_metrics"]}
    tt = {r["signal_family"]: r for r in val["train_test"]}
    cls = {c["signal_family"]: c for c in val["classifications"]}
    meta = ds.universe_meta
    L = []

    L.append("# Systematic Alpha Research Lab — Research Report\n")
    L.append("> Does this signal survive reality? A disciplined test of five "
             "explainable signals against costs, out-of-sample data, and stress.\n")

    L.append("## 1. Research Question\n")
    L.append(val["conclusions"]["research_question"] + "\n")
    L.append("A signal is credible only if it survives the full process: "
             "hypothesis → signal rule → portfolio rule → cost-aware backtest → "
             "benchmark comparison → out-of-sample test → robustness → verdict.\n")

    src_labels = {"yahoo": "Yahoo Finance", "tiingo": "Tiingo", "fred": "FRED", "NBER": "NBER"}
    used_sources = sorted({src_labels.get(v["source_name"], v["source_name"])
                           for v in ds.provenance.values()})
    late = [a["ticker"] for a in meta["assets"] if a["first_date"] > meta["actual_start"]]

    L.append("## 2. Data and Universe\n")
    L.append(f"- **Universe:** {len(meta['assets'])} liquid ETFs across "
             f"U.S. & international equity, Treasuries, TIPS, credit, commodities, "
             f"gold, and a cash/T-bill proxy.\n"
             f"- **Price sample:** {meta['actual_start']} to {meta['actual_end']} "
             f"({meta['trading_days']} trading days) on the "
             f"{meta['calendar_reference']} trading calendar.\n"
             f"- **Backtest calendar:** strategies and benchmarks share a common calendar "
             f"from {bt['common_start'].strftime('%Y-%m-%d')} (when a 12-month signal "
             f"history first exists). ETFs {', '.join(late)} start later than 2006 and "
             f"each enters the strategy on its own inception.\n"
             f"- **Source:** {', '.join(used_sources)}; returns use {meta['return_basis']}.\n"
             f"- **Cash proxy:** {meta.get('cash_handling', '')}\n"
             f"- **No look-ahead:** {meta['no_lookahead_rule']}\n")

    L.append("\n| Ticker | Group | First | Last | Source |\n| --- | --- | --- | --- | --- |\n")
    for a in meta["assets"]:
        L.append(f"| {a['ticker']} | {a['group'].replace('_',' ')} | {a['first_date']} | "
                 f"{a['last_date']} | {src_labels.get(a.get('source','yahoo'), 'Yahoo Finance')} |\n")

    L.append("## 3. Signal Cases\n")
    for name in SIGNAL_ORDER:
        md = SIGNAL_META[name]
        L.append(f"### {md['signal_name']}\n")
        L.append(f"- *Hypothesis:* {md['plain_english_hypothesis']}\n"
                 f"- *Formula:* `{md['formula']}`\n"
                 f"- *Portfolio rule:* {md['portfolio_rule']}\n")

    L.append("## 4. Backtest Methodology\n")
    L.append("- Long-only, no leverage, no shorting, monthly rebalance, cash fallback.\n"
             "- Weights drift with returns between rebalances; turnover is measured "
             "against drifted pre-trade weights.\n"
             "- **Turnover** = sum of absolute weight changes at a rebalance (total traded "
             "notional / NAV, including both buys and sells).\n"
             f"- Transaction costs of {bt['base_cost']} bps (primary) with "
             "1 / 5 / 10 / 25 bps sensitivity; cost = turnover x bps / 10000, applied as a "
             "return drag. Bid-ask spread, market impact, and intraday execution are not "
             "separately modeled.\n"
             "- Benchmarks (same calendar & cost model): SPY buy & hold, 60/40, "
             "equal-weight universe, cash/T-bills, and inverse-volatility.\n"
             "- Regime and crisis labels are retrospective validation tools (macro inputs "
             "lagged), not tradable real-time signals.\n")

    L.append("## 5. Validation Results\n")
    L.append("| Signal | Net CAGR | Net Sharpe | Max DD | Turnover/yr | OOS Sharpe | Cost drag |\n"
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |\n")
    for name in SIGNAL_ORDER:
        m = sm[name]
        L.append(f"| {m['strategy_name']} | {_pct(m['cagr'])} | {m['sharpe']:.2f} | "
                 f"{_pct(m['max_drawdown'],0)} | {m['annualized_turnover']:.1f} | "
                 f"{tt[name]['test_sharpe']:.2f} | {_pct(m['transaction_cost_drag'],2)} |\n")
    L.append("\nEach signal was also tested across cost levels, parameter grids, "
             "rebalance frequencies, six market regimes, and five crisis windows.\n")

    L.append("## 6. Final Classification\n")
    L.append(val["conclusions"]["headline"] + "\n\n")
    L.append("| Signal | Verdict | Note |\n| --- | --- | --- |\n")
    for name in SIGNAL_ORDER:
        c = cls[name]
        L.append(f"| {c['strategy_name']} | **{c['classification']}** | "
                 f"{c['final_research_note']} |\n")

    L.append("\n## 7. Limitations\n")
    L.append("- Long-only ETF research over one universe and window; not a live trading "
             "system or investment advice.\n"
             "- Transaction costs are a fixed-bps turnover drag; bid-ask spread, market "
             "impact, intraday execution, and taxes are not separately modeled.\n"
             "- Adjusted-close returns approximate total return (dividends assumed "
             "reinvested without tax).\n"
             "- Cash/T-bill exposure uses the 13-week Treasury-bill yield, not a cash ETF.\n"
             "- Regime and crisis labels are retrospective validation tools, not tradable "
             "signals.\n"
             "- Verdicts are qualitative research classifications, not statistical proof of "
             "alpha. Parameter grids are intentionally limited and predeclared to reduce "
             "data-mining risk.\n")

    text = "".join(L)
    path = out_path("reports", "research_report.md")
    path.write_text(text)
    return text
