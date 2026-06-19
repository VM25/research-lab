# 01_RESEARCH_THESIS.md

# Systematic Alpha Research Lab — Research Thesis

## Research Objective

Test whether simple, explainable systematic trading signals can survive realistic research validation.

The project must evaluate signals using historical ETF data, cost-aware backtesting, out-of-sample testing, robustness checks, and final research verdicts.

The objective is evidence, not the best-looking backtest.

## Core Research Question

Do systematic alpha signals still look useful after costs, turnover, parameter changes, regime shifts, and out-of-sample testing?

## Research Thesis

A signal is not credible because it performs well once.

A signal is credible only if it survives a research process:

```text id="y6agwu"
Hypothesis
→ Signal Rule
→ Portfolio Rule
→ Cost-Aware Backtest
→ Benchmark Comparison
→ Out-of-Sample Test
→ Robustness Check
→ Verdict
```

The project must show which signals deserve further research, which only work conditionally, and which should be rejected.

## Research Philosophy

The project must prioritize research discipline over performance marketing.

Acceptable conclusions include:

* the signal survives
* the signal only works in certain regimes
* the signal fails after transaction costs
* the signal is too parameter-sensitive
* the signal underperforms simple benchmarks
* the signal is not worth further research

A rejected signal is still a valid research result if the evidence is clear.

## Research Universe

Use liquid ETFs across major asset groups.

Required groups:

* U.S. equities
* international equities
* Treasuries
* inflation-linked bonds
* credit
* commodities
* gold
* cash / T-bill proxy

The universe must be simple enough to understand and broad enough to test cross-asset behavior.

Main research results must use real historical adjusted-close price data.

## Signal Cases

Each signal must be presented as a research case.

Required cases:

1. Time-Series Momentum
2. Cross-Sectional Momentum
3. Short-Term Reversal
4. Volatility-Scaled Momentum
5. Equal-Weight Signal Ensemble

Each case must answer:

* What is the hypothesis?
* Why might it work?
* How is the signal calculated?
* How does it become a portfolio?
* What can break it?
* What does the evidence show?
* What is the final verdict?

## Hypothesis 1 — Time-Series Momentum

Assets with positive medium-term trends may continue to perform because of slow-moving capital, investor underreaction, and persistent macro regimes.

Expected strengths:

* works in persistent trends
* may reduce exposure during prolonged drawdowns
* can rotate across asset classes

Expected weaknesses:

* lags sharp reversals
* may underperform in choppy markets
* can miss V-shaped recoveries

## Hypothesis 2 — Cross-Sectional Momentum

Assets with stronger relative performance may continue leading weaker assets.

Expected strengths:

* captures asset-class leadership
* adapts to changing market themes
* may outperform naive equal-weight allocation

Expected weaknesses:

* can become concentrated
* suffers during leadership reversals
* sensitive to ranking thresholds

## Hypothesis 3 — Short-Term Reversal

Assets with extreme short-term losses may partially rebound because of overreaction, liquidity pressure, or temporary positioning imbalance.

Expected strengths:

* may identify oversold conditions
* useful as a tactical signal
* can improve entry timing

Expected weaknesses:

* high turnover
* high transaction-cost sensitivity
* may fail during persistent selloffs

## Hypothesis 4 — Volatility-Scaled Momentum

Momentum exposure may become more stable when position size is reduced during high-volatility periods.

Expected strengths:

* lowers drawdowns
* reduces tail risk
* improves risk control

Expected weaknesses:

* cuts exposure after volatility spikes
* may miss rebounds
* may reduce upside capture

## Hypothesis 5 — Equal-Weight Signal Ensemble

Combining simple signals may reduce dependence on one fragile signal.

Expected strengths:

* smoother evidence profile
* lower single-signal dependence
* more stable across regimes

Expected weaknesses:

* may dilute strong signals
* may inherit weak signals
* can hide failure modes

## Benchmarks

Each signal must be compared against:

* SPY buy-and-hold
* 60/40 proxy
* equal-weight ETF universe
* cash / T-bill proxy

Optional benchmark:

* inverse-volatility allocation

## Validation Standard

Each signal must be tested using:

* gross vs net performance
* transaction-cost drag
* turnover
* benchmark comparison
* train/test split
* walk-forward validation
* parameter robustness
* cost sensitivity
* regime and crisis checks

## Classification Rules

Final verdicts:

```text id="dyh7l7"
Survived
Conditional
Rejected
```

### Survived

A signal survives if it shows useful net-of-cost performance, acceptable drawdowns, reasonable turnover, and stable out-of-sample evidence.

### Conditional

A signal is conditional if it works only under specific regimes, assumptions, cost levels, or parameter choices.

### Rejected

A signal is rejected if performance is cost-destroyed, fragile, benchmark-inferior, unstable out-of-sample, or not economically defensible.

## Final Research Standard

The final conclusion must be clear enough for a recruiter and defensible enough for a quant interviewer.

Every result must support the same question:

```text id="rbpian"
Does this signal survive reality?
```
