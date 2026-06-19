# 09_BUILD_PLAN.md

# Systematic Alpha Research Lab — Build Plan

## Build Objective

Build the final **Signal Survival Lab** in one focused implementation.

The project must include:

* Python research engine
* real historical ETF data pipeline
* signal engine
* cost-aware backtest
* validation engine
* generated outputs
* interactive website
* README

The build must stay focused on one question:

```text id="ucyeer"
Does this signal survive reality?
```

## Final Repository Structure

```text id="sf9qzy"
research-lab/
  README.md
  .gitignore
  .env.example

  docs/
    00_PROJECT_SCOPE.md
    01_RESEARCH_THESIS.md
    02_DATA_SPEC.md
    03_SIGNAL_SPEC.md
    04_BACKTEST_ENGINE_SPEC.md
    05_VALIDATION_AND_ROBUSTNESS.md
    06_OUTPUTS_AND_REPORTING.md
    07_PRODUCT_REQUIREMENTS.md
    08_DESIGN_SYSTEM.md
    09_BUILD_PLAN.md

  research/
    requirements.txt
    config/
    data/
    src/systematic_alpha_lab/
    outputs/

  web/
    app/
    components/
    lib/
    public/research-data/
```

## Build Phase 1 — Setup

Create the repository structure.

Required files:

```text id="omfc4f"
README.md
.gitignore
.env.example
requirements.txt
```

Required config files:

```text id="oxrz5c"
universe.yaml
data_sources.yaml
signal_params.yaml
backtest_params.yaml
validation_params.yaml
```

## Build Phase 2 — Data Pipeline

Implement real data ingestion and cleaning.

Required modules:

```text id="mcrj6s"
fetch_prices.py
clean_prices.py
returns.py
fetch_macro.py
align_calendar.py
```

Required outputs:

```text id="tc7z2s"
prices.parquet
returns.parquet
risk_free.parquet
macro.parquet
universe_metadata.json
data_quality_report.json
data_provenance.json
```

Hard rule:

```text id="zrwy7s"
Do not use simulated ETF prices for main results.
```

## Build Phase 3 — Signal Engine

Implement five signal cases:

```text id="wuyzz2"
time_series_momentum.py
cross_sectional_momentum.py
short_term_reversal.py
volatility_scaled_momentum.py
ensemble.py
```

Each signal must output:

```text id="zlxaf7"
date
ticker
signal_name
raw_score
normalized_score
trade_signal
lookback_window
rebalance_frequency
```

Each signal must include:

* hypothesis
* formula
* portfolio rule
* expected strength
* expected weakness

## Build Phase 4 — Portfolio Construction

Implement:

```text id="xhvydo"
weighting.py
constraints.py
rebalancing.py
```

Primary rules:

```text id="a9ppxh"
long-only
no leverage
no shorting
monthly rebalance
cash fallback
```

Supported methods:

* equal-weight selected assets
* score-weighted allocation
* volatility-adjusted allocation

## Build Phase 5 — Backtest Engine

Implement:

```text id="o9yrqk"
engine.py
costs.py
metrics.py
benchmarks.py
```

Required behavior:

* shift signals before returns
* calculate target weights
* apply constraints
* track weight drift
* calculate turnover
* apply transaction costs
* calculate gross and net returns
* build benchmarks
* export metrics

Required cost scenarios:

```text id="hn1f8i"
1 bp
5 bps
10 bps
25 bps
```

Primary reported cost:

```text id="vajmqk"
5 bps
```

## Build Phase 6 — Validation Engine

Implement:

```text id="tix2os"
train_test.py
walk_forward.py
robustness.py
classification.py
```

Required validation:

* train/test split
* walk-forward windows
* cost sensitivity
* parameter robustness
* rebalance sensitivity
* regime checks
* crisis checks

Final verdicts:

```text id="n4d52x"
Survived
Conditional
Rejected
```

## Build Phase 7 — Website Outputs

Generate website-ready JSON:

```text id="vjwk5a"
overview.json
data_summary.json
signal_cases.json
backtest_summary.json
validation_summary.json
classification_board.json
failure_modes.json
```

No website metric may be manually hardcoded.

## Build Phase 8 — Website

Build a guided interactive website.

Required flow:

```text id="jmv8q3"
Hero
→ Signal Selector
→ Signal Case
→ Evidence Panel
→ Stress Test Panel
→ Verdict Board
→ Methodology
```

Required interactions:

* signal selector
* gross/net toggle
* benchmark selector
* cost scenario selector
* parameter comparison
* verdict change indicator
* methodology drawer

The website must not become a generic dashboard.

## Build Phase 9 — README

Write a concise README with:

* project summary
* research question
* signal list
* data note
* methodology summary
* verdict table
* reproducibility steps
* limitations
* not investment advice

## Required Tests

Add minimal tests for:

```text id="q8zm3d"
return calculation
signal lagging
weight sums
transaction costs
portfolio compounding
no-lookahead timing
```

Do not overbuild the test suite.

## Final Checks

Before completion, verify:

* real price data is used
* no-lookahead timing is enforced
* gross and net results both exist
* costs reduce net returns
* all verdicts come from generated outputs
* website reads JSON only
* every chart has a takeaway
* users are not overwhelmed

## Hard Build Rules

* Do not create a giant research dossier.
* Do not add unnecessary signal variants.
* Do not add excessive charts.
* Do not bury verdicts.
* Do not use forbidden fonts or colors.
* Do not use simulated ETF prices for main evidence.
* Do not claim live-trading readiness.
* Do not manually hardcode results.
* Do not let methodology dominate the product.

The build succeeds if the user can choose a signal, understand the hypothesis, inspect the evidence, stress the assumptions, and explain the final verdict.
