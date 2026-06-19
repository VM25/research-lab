# 00_PROJECT_SCOPE.md

# Systematic Alpha Research Lab — Project Scope

## Project Name

**Systematic Alpha Research Lab**

## Project Folder

```text
research-lab/
```

## Project Objective

Build a focused quant research project that tests whether explainable trading signals survive realistic validation.

The project must not present a collection of disconnected charts. It must present a guided signal-testing experience:

```text
Pick a signal
→ understand the hypothesis
→ inspect the evidence
→ stress the assumptions
→ receive a verdict
```

## Core Research Question

Do simple systematic alpha signals survive after transaction costs, out-of-sample testing, robustness checks, and market-regime stress?

## Product Concept

The project is a **Signal Survival Lab**.

Each signal is treated as a research case. The lab shows the signal’s logic, tests it under realistic assumptions, and classifies it as:

```text
Survived
Conditional
Rejected
```

The goal is not to claim a live profitable strategy. The goal is to demonstrate disciplined quant research judgment.

## Target Candidate Signal

The project must show ability to:

* form testable trading hypotheses
* build clean financial time-series pipelines
* avoid look-ahead bias
* convert signals into portfolios
* model turnover and transaction costs
* run walk-forward validation
* test robustness across assumptions
* explain why a signal works, weakens, or fails
* communicate results clearly to technical and non-technical viewers

## Target Roles

Primary fit:

* Quant Researcher
* Quant Data Scientist
* Quant Trader
* Quant Strategist
* Algorithmic Trading
* Quant Analyst

Secondary fit:

* Risk Quant
* Quant Developer
* Financial Engineer
* Financial Analyst

## Research Universe

Use a liquid ETF universe with real historical adjusted-close data.

Required asset groups:

* U.S. equities
* international equities
* Treasuries
* inflation-linked bonds
* credit
* commodities
* gold
* cash / T-bill proxy

Do not use simulated ETF prices for the main research results.

## Signal Families

Include a small, defensible set of signals:

1. Time-Series Momentum
2. Cross-Sectional Momentum
3. Short-Term Reversal
4. Volatility-Scaled Momentum
5. Equal-Weight Signal Ensemble

Each signal must include:

* plain-English hypothesis
* formula
* portfolio rule
* expected strength
* expected weakness
* validation evidence
* final verdict

## Required Research Components

The project must include:

* data audit
* signal construction
* portfolio construction
* cost-aware backtest
* benchmark comparison
* train/test split
* walk-forward validation
* cost sensitivity
* parameter robustness
* regime and crisis checks
* final signal classification

## Required Benchmarks

Compare strategies against:

* SPY buy-and-hold
* 60/40 proxy
* equal-weight ETF universe
* cash / T-bill proxy

Optional:

* inverse-volatility benchmark

## Required Metrics

Report only metrics that help evaluate signal survival:

* CAGR
* annualized volatility
* Sharpe ratio
* max drawdown
* turnover
* transaction-cost drag
* benchmark-relative return
* out-of-sample return
* classification verdict

## Final Deliverables

The project must include:

1. **Python research engine**

   * data ingestion
   * cleaning
   * signal generation
   * portfolio construction
   * backtesting
   * validation
   * output export

2. **Generated research outputs**

   * JSON for website
   * CSV or Parquet audit files
   * metrics
   * verdicts
   * failure notes

3. **Interactive website**

   * guided signal case files
   * evidence views
   * assumption stress tests
   * final classification board

4. **Public documentation**

   * README
   * methodology summary
   * reproducibility steps
   * limitations
   * final conclusions

## Product Boundaries

The project must not become:

* a live trading system
* a generic dashboard
* a giant technical appendix
* a paper pasted into a website
* a strategy marketplace
* an over-optimized backtest

Every section must answer:

```text
Does this signal survive reality?
```

If a section does not support that question, remove it.

## Success Criteria

The final project succeeds if a viewer can understand within two minutes:

* what signal is being tested
* why the signal might work
* how it was tested
* whether costs hurt it
* whether it survives out-of-sample
* why it was classified as Survived, Conditional, or Rejected
