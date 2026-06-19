# 05_VALIDATION_AND_ROBUSTNESS.md

# Systematic Alpha Research Lab — Validation and Robustness Specification

## Validation Objective

Test whether each signal survives beyond a single backtest.

Validation must determine whether performance is:

```text id="kz6jxv"
credible
conditional
fragile
cost-destroyed
benchmark-inferior
rejected
```

The final output must support one verdict per signal:

```text id="i7yo09"
Survived
Conditional
Rejected
```

## Validation Pipeline

```text id="c0szyk"
Strategy Results
→ Gross vs Net
→ Benchmark Comparison
→ Train/Test Split
→ Walk-Forward Test
→ Cost Sensitivity
→ Parameter Robustness
→ Rebalance Sensitivity
→ Regime/Crisis Checks
→ Verdict
```

## Primary Validation Standard

Each signal must be tested across:

| Test                  | Purpose                              |
| --------------------- | ------------------------------------ |
| Gross vs net          | measure transaction-cost damage      |
| Benchmark comparison  | test value over passive alternatives |
| Train/test split      | separate fitting from evidence       |
| Walk-forward          | test out-of-sample stability         |
| Cost sensitivity      | test execution realism               |
| Parameter robustness  | test fragility                       |
| Rebalance sensitivity | test timing dependence               |
| Regime analysis       | test market-condition dependence     |
| Crisis analysis       | test stress behavior                 |

## Train/Test Split

Default split:

```text id="a2vbmo"
Train: 2006-01-01 to 2016-12-31
Test: 2017-01-01 to latest complete available date
```

Training data may be used to choose default parameters.

Testing data must be used for final out-of-sample evidence.

Required output:

```text id="tchykc"
train_test_results.json
```

Required fields:

```text id="wxga2d"
strategy_name
train_start
train_end
test_start
test_end
train_cagr
test_cagr
train_sharpe
test_sharpe
train_max_drawdown
test_max_drawdown
train_turnover
test_turnover
train_cost_drag
test_cost_drag
test_verdict_note
```

## Walk-Forward Validation

Use expanding-window walk-forward tests.

Default windows:

| Train     | Test        |
| --------- | ----------- |
| 2006-2012 | 2013-2016   |
| 2006-2016 | 2017-2019   |
| 2006-2019 | 2020-2022   |
| 2006-2022 | 2023-latest |

For each window:

1. choose parameters using training data only
2. freeze parameters
3. test on the next period
4. compare against benchmarks
5. assign window result

Required output:

```text id="w61on9"
walk_forward_results.json
```

Required fields:

```text id="twq2lr"
strategy_name
train_start
train_end
test_start
test_end
selected_parameters
test_cagr
test_sharpe
test_max_drawdown
test_turnover
test_cost_drag
test_excess_return_vs_benchmark
window_result
window_note
```

## Cost Sensitivity

Test each signal under:

| Scenario |   Cost |
| -------- | -----: |
| low      |   1 bp |
| base     |  5 bps |
| high     | 10 bps |
| stress   | 25 bps |

Required output:

```text id="e83vmv"
cost_sensitivity.json
```

Required fields:

```text id="g54reb"
strategy_name
cost_bps
gross_cagr
net_cagr
gross_sharpe
net_sharpe
annual_turnover
cost_drag
classification_at_cost_level
```

A signal with strong gross results but weak net results must be marked cost-sensitive or rejected.

## Parameter Robustness

Test whether results depend on narrow settings.

Required tests:

| Signal                   | Parameters                 |
| ------------------------ | -------------------------- |
| Time-Series Momentum     | 6M, 9M, 12M, 12M-1M        |
| Cross-Sectional Momentum | top 20%, top 30%, top 40%  |
| Short-Term Reversal      | 5D, 10D, 21D               |
| Volatility Scaling       | 21D, 63D, 126D vol windows |

Required output:

```text id="f3xpum"
parameter_robustness.json
```

Required fields:

```text id="k0puax"
strategy_name
parameter_set
cagr
sharpe
max_drawdown
turnover
cost_drag
benchmark_relative_return
parameter_result
```

A signal should not be classified as Survived if only one narrow parameter set works.

## Rebalance Sensitivity

Test:

```text id="b0fqtu"
weekly
monthly
quarterly
```

Required output:

```text id="n5cynp"
rebalance_sensitivity.json
```

Required fields:

```text id="v2u638"
strategy_name
rebalance_frequency
net_cagr
net_sharpe
max_drawdown
annual_turnover
cost_drag
classification_at_frequency
```

Primary reported setting remains monthly unless evidence clearly supports another frequency.

## Regime Analysis

Evaluate each signal under market conditions.

Required regimes:

```text id="ak59ew"
Risk-On
Risk-Off
High Volatility
Rate Shock
Inflation Stress
Normal
```

Required output:

```text id="xgifjy"
regime_breakdown.json
```

Required fields:

```text id="j1i7xx"
strategy_name
regime_name
observation_count
cagr
sharpe
max_drawdown
hit_rate
turnover
cost_drag
regime_note
```

Regime dependence should usually support a Conditional verdict.

## Crisis Analysis

Required stress windows:

| Period                           | Dates                    |
| -------------------------------- | ------------------------ |
| Global Financial Crisis          | 2007-10-01 to 2009-03-31 |
| Eurozone / U.S. downgrade stress | 2011-07-01 to 2011-12-31 |
| COVID crash                      | 2020-02-01 to 2020-04-30 |
| Inflation / rate shock           | 2022-01-01 to 2022-12-31 |
| Higher-rate regime               | 2023-01-01 to latest     |

Required output:

```text id="wasn82"
crisis_period_analysis.json
```

Required fields:

```text id="t99g0v"
strategy_name
crisis_period
start_date
end_date
cumulative_return
max_drawdown
benchmark_relative_return
turnover
cost_drag
crisis_note
```

## Classification Rules

### Survived

A signal may be classified as Survived only if:

* net performance is positive or benchmark-competitive
* drawdowns are acceptable
* turnover is not excessive
* out-of-sample evidence is credible
* results are not dependent on one narrow parameter
* failure modes are limited and explainable

### Conditional

A signal is Conditional if:

* it works only in certain regimes
* it works only under low costs
* results are parameter-sensitive but not useless
* it improves risk control more than raw returns
* it is useful as an overlay, not standalone alpha

### Rejected

A signal is Rejected if:

* transaction costs destroy it
* turnover is excessive
* out-of-sample results fail
* benchmark-relative results are weak
* parameter robustness fails
* the economic explanation is not supported

## Required Final Outputs

```text id="q6ju1w"
train_test_results.json
walk_forward_results.json
cost_sensitivity.json
parameter_robustness.json
rebalance_sensitivity.json
regime_breakdown.json
crisis_period_analysis.json
signal_classification.json
failure_modes.json
```

## `signal_classification.json`

Required schema:

```json id="w05kiy"
{
  "strategy_name": "",
  "classification": "Survived | Conditional | Rejected",
  "primary_evidence": [],
  "weaknesses": [],
  "best_use_case": "",
  "final_research_note": ""
}
```

## `failure_modes.json`

Allowed failure types:

```text id="l8ad4s"
cost_failure
turnover_failure
parameter_fragility
regime_dependency
drawdown_failure
out_of_sample_failure
benchmark_underperformance
```

## Hard Rules

* Do not classify a signal from total return alone.
* Do not hide failed walk-forward windows.
* Do not hide cost damage.
* Do not hide parameter fragility.
* Do not claim a signal survived if it only worked in-sample.
* Do not turn validation into a chart dump.

Validation succeeds if the final verdict is obvious from the evidence.
