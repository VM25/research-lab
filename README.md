# Systematic Alpha Research Lab

**Does this signal survive reality?**

A focused quant research project that tests whether simple, explainable trading
signals survive realistic validation — transaction costs, out-of-sample data,
parameter changes, and market stress — on **20 years of real ETF data**.

It is a *Signal Survival Lab*. Each signal is treated as a research case and
walked through one question:

```
Pick a signal → understand the hypothesis → inspect the evidence
→ stress the assumptions → receive a verdict
```

The goal is not the best-looking backtest. The goal is disciplined research
judgment: showing which signals deserve further research, which work only
conditionally, and which should be rejected.

---

## Research question

> Do systematic alpha signals still look useful after costs, turnover,
> parameter changes, regime shifts, and out-of-sample testing?

A signal is credible only if it survives the whole process:

```
Hypothesis → Signal Rule → Portfolio Rule → Cost-Aware Backtest
→ Benchmark Comparison → Out-of-Sample Test → Robustness → Verdict
```

## Signals tested

| # | Signal | Idea (plain English) |
|---|--------|----------------------|
| 1 | **Time-Series Momentum** | Hold assets whose own 12-month trend is positive. |
| 2 | **Cross-Sectional Momentum** | Own only the strongest-trending assets relative to peers. |
| 3 | **Short-Term Reversal** | Buy assets that just sold off sharply, betting on a bounce. |
| 4 | **Volatility-Scaled Momentum** | Run momentum, but shrink positions when markets get volatile. |
| 5 | **Equal-Weight Signal Ensemble** | Average the four signals and hold what the committee likes. |

## Final verdicts

Verdicts are **computed from the generated evidence** using documented
thresholds — never hand-assigned.

| Signal | Verdict | Net CAGR | Sharpe | Max DD | Turnover/yr |
|--------|:-------:|---------:|-------:|-------:|------------:|
| Time-Series Momentum | ✅ **Survived** | 5.7% | 0.57 | −15% | 3.2× |
| Cross-Sectional Momentum | ✅ **Survived** | 8.8% | 0.62 | −18% | 4.2× |
| Equal-Weight Signal Ensemble | ✅ **Survived** | 7.7% | 0.59 | −22% | 6.0× |
| Volatility-Scaled Momentum | ⚠️ **Conditional** | 4.3% | 0.58 | −12% | 3.2× |
| Short-Term Reversal | ❌ **Rejected** | 5.2% | 0.45 | −29% | 12.9× |

*Net of the primary 5 bps cost assumption. SPY buy-and-hold over the same window
returned ~11% CAGR but with a **−55%** max drawdown — the strategies trade raw
return for far steadier risk.*

**Headline:** the momentum complex survives; volatility scaling is a risk-control
overlay (conditional); short-term reversal is rejected — its 12.9×/yr turnover
trails every passive benchmark and degrades sharply as costs rise.

## Data

- **Universe:** 15 liquid ETFs across U.S. & international equity, Treasuries,
  TIPS, credit, commodities, gold, and a cash/T-bill proxy.
- **Price sample:** 2006-01-03 → 2026-06-18 on the SPY trading calendar
  (~5,150 trading days). Most ETFs cover the full span; **DBC, SHV, HYG and BIL
  start later** (see table) and each ETF enters the strategy on its own inception
  once it has the required signal history.
- **Backtest calendar:** strategies and benchmarks share a common calendar that
  begins **2007-02-28**, when a 12-month momentum history first exists.
- **Source:** real **Yahoo Finance** prices using the **dividend- and
  split-adjusted close** (a total-return approximation), plus Yahoo macro series
  (VIX, 10-year and 13-week Treasury yields) and **FRED** CPI. **NBER** recession
  dates and fixed crisis windows are used only for retrospective regime labeling.
  No simulated prices are used anywhere.
- **Cash proxy:** cash/T-bill exposure (the cash fallback and the cash benchmark)
  earns the **13-week US Treasury-bill yield** (Yahoo `^IRX`), applied
  continuously. BIL and SHV are tradable ETFs, but the continuous T-bill rate is
  used for cash so there is no 2007 inception gap.
- Every series' provenance is recorded in
  `research/outputs/data_audit/data_provenance.json`.

### ETF universe

| Ticker | Asset group | First | Last | Source |
|--------|-------------|-------|------|--------|
| SPY | US equity | 2006-01 | 2026-06 | Yahoo Finance |
| QQQ | US equity | 2006-01 | 2026-06 | Yahoo Finance |
| IWM | US equity | 2006-01 | 2026-06 | Yahoo Finance |
| EFA | Intl equity | 2006-01 | 2026-06 | Yahoo Finance |
| EEM | Intl equity | 2006-01 | 2026-06 | Yahoo Finance |
| SHY | Treasury | 2006-01 | 2026-06 | Yahoo Finance |
| IEF | Treasury | 2006-01 | 2026-06 | Yahoo Finance |
| TLT | Treasury (long) | 2006-01 | 2026-06 | Yahoo Finance |
| TIP | TIPS | 2006-01 | 2026-06 | Yahoo Finance |
| LQD | Credit | 2006-01 | 2026-06 | Yahoo Finance |
| HYG | Credit (high yield) | **2007-04** | 2026-06 | Yahoo Finance |
| DBC | Commodities | **2006-02** | 2026-06 | Yahoo Finance |
| GLD | Gold | 2006-01 | 2026-06 | Yahoo Finance |
| BIL | 1–3M T-Bills | **2007-05** | 2026-06 | Yahoo Finance |
| SHV | Short Treasuries | **2007-01** | 2026-06 | Yahoo Finance |

All 15 ETFs are **included**; none are excluded. The table is generated from
`data_quality_report.json` (see `research/outputs/reports/research_report.md`).

## Methodology highlights

- **No look-ahead, enforced:** `feature[t]` uses data through `t`; `signal[t]` is
  formed at `t`; `position[t+1]` uses `signal[t]`; `return[t+1]` is earned by
  `position[t+1]`.
- **Primary strategy:** long-only, no leverage, no shorting, monthly rebalance,
  cash fallback when nothing qualifies.
- **Turnover:** sum of absolute weight changes at a rebalance — total traded
  notional / NAV, including both buys and sells.
- **Costs:** `cost = turnover × bps / 10000`, applied as a return drag. Reported
  at 1 / 5 / 10 / 25 bps; headline = 5 bps. Gross and net are always shown.
  Bid-ask spread, market impact, and intraday execution are **not** separately
  modeled.
- **Benchmarks (same calendar & cost model):** SPY buy-and-hold, 60/40, equal-
  weight universe, cash/T-bills, and inverse-volatility.
- **Regime & crisis labels** are retrospective validation tools (macro inputs
  lagged so labels use only observable information), not tradable real-time
  signals.
- **Validation:** train/test split (2006–2016 vs 2017+), expanding-window
  walk-forward with parameter selection, cost sensitivity, parameter robustness,
  rebalance sensitivity, six market-regime breakdowns, and five crisis windows.

## Repository

```
research-lab/
  docs/                     # project specification (00–09)
  research/
    config/                 # universe / data / signal / backtest / validation YAML
    src/systematic_alpha_lab/
      data/                 # real price + macro ingestion, cleaning, returns
      signals/              # the five signal families
      portfolio/            # weighting, constraints, rebalancing
      backtest/             # engine, costs, metrics, benchmarks, runner
      validation/           # train/test, walk-forward, robustness, classification
      outputs/              # website JSON + research report generators
      pipeline.py           # end-to-end orchestrator
    tests/                  # return calc, signal lag, weights, costs, compounding, no-lookahead
    outputs/                # generated artifacts (audit / signals / backtests / validation / json / reports)
  web/                      # Next.js site; reads web/public/research-data/*.json
```

## Reproduce

**Research engine** (Python 3.9+):

```bash
cd research
python3 -m pip install -r requirements.txt
PYTHONPATH=src python3 -m systematic_alpha_lab.pipeline   # fetch → signals → backtest → validate → JSON → report
PYTHONPATH=src python3 -m pytest tests/ -q                # correctness tests
```

The pipeline writes audit files, parquet outputs, website JSON
(`web/public/research-data/`), and `research/outputs/reports/research_report.md`.
Raw vendor responses are cached under `research/data/raw/` so reruns are
reproducible and offline. If Yahoo Finance is rate-limited on your machine, set
`TIINGO_API_TOKEN` in `.env` for a keyed fallback — the pipeline never
substitutes simulated prices.

**Website** (Node 18+):

```bash
cd web
npm install
npm run dev      # http://localhost:3000
npm run build    # static export to web/out/
```

The site reads only the generated JSON files. No research result, metric, chart,
or verdict is hardcoded in the front end.

## Limitations

- Long-only ETF research over one universe and window — **not** a live trading
  system and **not** investment advice.
- Transaction costs are a fixed-bps turnover drag; bid-ask spread, market impact,
  intraday execution, and taxes are not separately modeled.
- Adjusted-close returns approximate total return (dividends assumed reinvested
  without tax).
- Cash/T-bill exposure uses the 13-week Treasury-bill yield, not a cash ETF.
- Regime and crisis labels are retrospective validation tools, not tradable
  signals.
- Verdicts are **qualitative research classifications, not statistical proof of
  alpha**. Parameter grids are intentionally limited and predeclared to reduce
  data-mining risk. Past performance does not guarantee future results.

---

*Research and educational project. Not investment advice. Not a live trading system.*
