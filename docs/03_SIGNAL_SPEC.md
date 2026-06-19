# 03_SIGNAL_SPEC.md

# Systematic Alpha Research Lab — Signal Specification

## Signal Objective

Convert clean historical ETF data into explainable trading signals that can be tested, stressed, and classified.

Each signal must be simple enough to explain and rigorous enough to defend.

## Signal Case Format

Each signal must be presented as a research case:

```text id="l8tc2f"
Hypothesis
→ Formula
→ Portfolio Rule
→ Expected Strength
→ Expected Weakness
→ Evidence
→ Verdict
```

## No-Lookahead Rule

Every signal must obey:

```text id="wj8885"
feature[t] uses data through t
signal[t] is created at t
position[t+1] uses signal[t]
return[t+1] is earned by position[t+1]
```

No signal may use same-day returns to create same-day positions.

## Signal Output Format

Each signal must output:

```text id="p3qrdu"
date
ticker
signal_name
raw_score
normalized_score
trade_signal
lookback_window
rebalance_frequency
```

Allowed `trade_signal` values:

```text id="jwpvwv"
1 = long / include
0 = neutral / exclude
```

The main project must be long-only. No shorting in the primary version.

## Rebalance Frequency

Primary setting:

```text id="qehv25"
monthly
```

Robustness tests may compare:

```text id="dcd7xa"
weekly
monthly
quarterly
```

## Signal 1 — Time-Series Momentum

### Hypothesis

Assets with positive medium-term trends may continue performing because of slow-moving capital, underreaction, and persistent macro regimes.

### Formula

Primary signal:

```text id="slq2lb"
momentum_12_1[t] = adjusted_close[t-21] / adjusted_close[t-252] - 1
```

This measures 12-month momentum excluding the most recent month.

### Trade Rule

```text id="k84oqy"
trade_signal[t, i] = 1 if momentum_12_1[t, i] > 0
trade_signal[t, i] = 0 otherwise
```

### Portfolio Use

Allocate across assets with positive trend. Unused capital goes to cash proxy.

### Expected Strength

* persistent trend regimes
* prolonged drawdown avoidance
* cross-asset rotation

### Expected Weakness

* sharp reversals
* choppy markets
* V-shaped recoveries

## Signal 2 — Cross-Sectional Momentum

### Hypothesis

Assets with stronger relative performance may continue leading weaker assets.

### Formula

```text id="m2r1ev"
cross_momentum[t, i] = adjusted_close[t-21, i] / adjusted_close[t-252, i] - 1
rank[t, i] = percentile_rank(cross_momentum[t, i])
```

### Trade Rule

```text id="x7nt67"
trade_signal[t, i] = 1 if rank[t, i] >= 0.70
trade_signal[t, i] = 0 otherwise
```

This selects the top 30% of assets by relative momentum.

### Portfolio Use

Allocate across selected leaders, subject to max-weight constraints.

### Expected Strength

* asset-class leadership
* regime rotation
* relative strength capture

### Expected Weakness

* concentration
* threshold turnover
* leadership reversals

## Signal 3 — Short-Term Reversal

### Hypothesis

Extreme short-term losses may partially reverse because of overreaction, liquidity pressure, or temporary positioning imbalance.

### Formula

```text id="cbclcp"
return_5d[t, i] = adjusted_close[t, i] / adjusted_close[t-5, i] - 1

reversal_z[t, i] =
(return_5d[t, i] - rolling_mean_63d(return_5d[:, i]))
/ rolling_std_63d(return_5d[:, i])
```

### Trade Rule

```text id="q3t2ie"
trade_signal[t, i] = 1 if reversal_z[t, i] <= -1.0
trade_signal[t, i] = 0 otherwise
```

### Portfolio Use

Allocate to oversold assets only. Evaluate gross and net results separately.

### Expected Strength

* oversold rebound capture
* tactical entry timing
* short-horizon dislocation detection

### Expected Weakness

* high turnover
* transaction-cost drag
* persistent downtrends

## Signal 4 — Volatility-Scaled Momentum

### Hypothesis

Momentum exposure may become more stable when exposure is reduced during high-volatility periods.

### Base Signal

Use Time-Series Momentum as the base signal.

### Volatility Formula

```text id="ga0ohq"
realized_vol[t, i] = std(daily_returns[t-63:t, i]) * sqrt(252)
scale[t, i] = min(1.0, target_vol / realized_vol[t, i])
```

Primary target:

```text id="ldmhgd"
target_vol = 10%
```

### Trade Rule

```text id="kguaay"
base_weight[t, i] = momentum_weight[t, i]
scaled_weight[t, i] = base_weight[t, i] * scale[t, i]
unused_weight → cash_proxy
```

### Portfolio Use

Reduce exposure when realized volatility rises.

### Expected Strength

* lower drawdowns
* smoother returns
* better downside control

### Expected Weakness

* lower upside capture
* delayed de-risking
* missed rebounds

## Signal 5 — Equal-Weight Signal Ensemble

### Hypothesis

Combining simple signals may reduce dependence on one fragile signal.

### Formula

Use standardized scores from:

```text id="c0deim"
Time-Series Momentum
Cross-Sectional Momentum
Short-Term Reversal
Volatility-Scaled Momentum
```

Ensemble score:

```text id="n1vq3c"
ensemble_score[t, i] = mean(standardized_signal_scores[t, i])
```

### Trade Rule

```text id="td3tai"
trade_signal[t, i] = 1 if ensemble_score[t, i] > 0
trade_signal[t, i] = 0 otherwise
```

### Portfolio Use

Allocate across assets with positive ensemble score.

### Expected Strength

* lower single-signal dependence
* smoother evidence profile
* broader robustness

### Expected Weakness

* diluted strong signals
* inherited weak signals
* less interpretable failure modes

## Portfolio Conversion Rules

Signals may become weights using:

```text id="j35e3t"
equal-weight selected assets
score-weighted allocation
volatility-adjusted allocation
cash fallback
```

Primary version:

```text id="fq1kkl"
long-only
no leverage
monthly rebalance
cash fallback when no asset qualifies
```

## Required Signal Outputs

```text id="atn49o"
time_series_momentum_scores.parquet
cross_sectional_momentum_scores.parquet
short_term_reversal_scores.parquet
volatility_scaled_momentum_scores.parquet
ensemble_scores.parquet
signal_summary.json
```

## `signal_summary.json`

Each signal must include:

```text id="g8wz89"
signal_name
hypothesis
formula
lookback_window
rebalance_frequency
portfolio_rule
expected_strength
expected_weakness
primary_failure_mode
```

## Hard Rules

* Keep signals explainable.
* Do not optimize until the best result appears.
* Do not hide failed signals.
* Do not create too many signal variants.
* Do not use simulated prices for main signal evidence.
* Do not present any signal as live-trade-ready.

A signal succeeds only if the evidence supports its final verdict.
