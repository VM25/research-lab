# 04_BACKTEST_ENGINE_SPEC.md

# Systematic Alpha Research Lab — Backtest Engine Specification

## Engine Objective

Convert signal scores into portfolios, apply realistic trading assumptions, calculate performance, and generate evidence for each signal’s final verdict.

The engine must answer:

```text id="xezm9q"
Did the signal survive after costs, turnover, and benchmark comparison?
```

## Backtest Pipeline

```text id="yuslf7"
Returns
→ Signal Scores
→ Target Weights
→ Constraints
→ Rebalance
→ Turnover
→ Costs
→ Net Returns
→ Metrics
→ Verdict Inputs
```

## Required Inputs

```text id="rpv64o"
returns.parquet
risk_free.parquet
signals/*.parquet
universe_metadata.json
backtest_config.yaml
```

Signal input fields:

```text id="o3g4wn"
date
ticker
signal_name
raw_score
normalized_score
trade_signal
lookback_window
rebalance_frequency
```

Return input fields:

```text id="y8j2el"
date
ticker
simple_return
risk_free_daily
```

## Timing Rule

The engine must prevent look-ahead bias.

```text id="qcttu0"
signal[t] determines target_weight[t+1]
target_weight[t+1] earns asset_return[t+1]
```

No same-day return may influence same-day position.

## Rebalance Schedule

Primary setting:

```text id="wv9w0w"
monthly
```

Robustness settings:

```text id="gf02mr"
weekly
monthly
quarterly
```

If a scheduled rebalance date is not a trading day, use the next available trading day.

## Portfolio Construction

Primary version:

```text id="rpk5vq"
long-only
no leverage
no shorting
cash fallback
```

Supported weighting methods:

### Equal-Weight Selected Assets

```text id="ajzfhf"
weight[t, i] = 1 / N_selected
```

### Score-Weighted Allocation

```text id="coceer"
positive_score[t, i] = max(normalized_score[t, i], 0)
weight[t, i] = positive_score[t, i] / sum(positive_score[t, :])
```

### Volatility-Adjusted Allocation

```text id="z9zgtq"
raw_weight[t, i] = positive_score[t, i] / realized_vol[t, i]
weight[t, i] = raw_weight[t, i] / sum(raw_weight[t, :])
```

### Cash Fallback

If no asset qualifies:

```text id="jr9o7e"
cash_proxy_weight = 100%
```

Primary cash proxy:

```text id="o4dpjd"
BIL or SHV
```

## Portfolio Constraints

Default constraints:

| Constraint                     |    Value |
| ------------------------------ | -------: |
| Max single asset               |      25% |
| Max U.S. equity group          |      70% |
| Max international equity group |      40% |
| Max Treasury group             |      70% |
| Max long-duration Treasury     |      40% |
| Max credit group               |      30% |
| Max commodity group            |      35% |
| Max gold                       |      25% |
| Leverage                       | disabled |
| Shorting                       | disabled |

If weights breach constraints, clip and renormalize remaining weight to eligible assets or cash.

## Weight Drift

Between rebalances, weights must drift with returns.

```text id="fqerpe"
post_return_weight[t, i] =
weight[t-1, i] * (1 + asset_return[t, i])
/ (1 + gross_portfolio_return[t])
```

Turnover must be calculated against drifted pre-trade weights.

## Turnover

```text id="vx53py"
turnover[t] = sum(abs(target_weight[t, i] - pre_trade_weight[t, i]))
```

Required output fields:

```text id="it8m1u"
date
strategy_name
turnover
annualized_turnover
```

## Transaction Costs

Apply transaction costs as return drag.

```text id="pzplca"
transaction_cost[t] = turnover[t] * cost_bps / 10000
net_return[t] = gross_return[t] - transaction_cost[t]
```

Cost scenarios:

| Scenario |   Cost |
| -------- | -----: |
| low      |   1 bp |
| base     |  5 bps |
| high     | 10 bps |
| stress   | 25 bps |

Primary reported result:

```text id="s37bhk"
base = 5 bps
```

## Portfolio Returns

Gross return:

```text id="m5pwds"
gross_return[t] = sum(weight[t-1, i] * asset_return[t, i])
```

Net return:

```text id="nnc2ck"
net_return[t] = gross_return[t] - transaction_cost[t]
```

Portfolio value:

```text id="yj6rl2"
portfolio_value[t] = portfolio_value[t-1] * (1 + net_return[t])
```

Initial value:

```text id="cce1ab"
1.00
```

## Benchmarks

Required benchmarks:

| Benchmark             | Construction               |
| --------------------- | -------------------------- |
| SPY                   | 100% SPY                   |
| 60/40 proxy           | 60% SPY, 40% IEF           |
| Equal-weight universe | equal-weight eligible ETFs |
| Cash proxy            | 100% BIL or SHV            |

Optional:

| Benchmark          | Construction                                        |
| ------------------ | --------------------------------------------------- |
| Inverse-volatility | weights proportional to inverse realized volatility |

Benchmarks must use the same calendar and metrics as strategies.

## Required Metrics

Calculate only metrics needed for signal survival:

```text id="d9k6yk"
CAGR
annualized_return
annualized_volatility
Sharpe_ratio
max_drawdown
turnover
transaction_cost_drag
benchmark_relative_return
tracking_error
information_ratio
worst_month
```

CAGR:

```text id="f8d4d3"
CAGR = (ending_value / starting_value)^(252 / n_trading_days) - 1
```

Volatility:

```text id="r1sa8k"
annualized_volatility = std(daily_returns) * sqrt(252)
```

Sharpe:

```text id="y52twq"
Sharpe = annualized_excess_return / annualized_volatility
```

Drawdown:

```text id="dqx1xk"
drawdown[t] = portfolio_value[t] / rolling_max(portfolio_value[:t]) - 1
```

## Required Outputs

```text id="fpvexk"
portfolio_returns.parquet
portfolio_values.parquet
portfolio_weights.parquet
turnover.parquet
transaction_costs.parquet
drawdowns.parquet
strategy_metrics.json
benchmark_metrics.json
benchmark_comparison.json
```

## `strategy_metrics.json`

Required fields:

```text id="zosp17"
strategy_name
signal_family
rebalance_frequency
cost_bps
weighting_method
cagr
annualized_volatility
sharpe
max_drawdown
annualized_turnover
transaction_cost_drag
benchmark_relative_return
information_ratio
classification_input_note
```

## `benchmark_comparison.json`

Required fields:

```text id="vnnmx8"
strategy_name
benchmark_name
strategy_cagr
benchmark_cagr
strategy_sharpe
benchmark_sharpe
strategy_max_drawdown
benchmark_max_drawdown
excess_return
information_ratio
comparison_note
```

## Engine Checks

The engine must test:

* signals are shifted before returns
* weights sum to 1.0
* no leverage in primary version
* no short positions in primary version
* costs reduce net returns
* turnover uses drifted weights
* benchmarks share the same calendar
* portfolio values compound correctly

## Hard Rules

* Do not optimize the backtest to maximize results.
* Do not report gross results without net results.
* Do not hide transaction-cost damage.
* Do not hide high turnover.
* Do not manually hardcode website metrics.
* Do not claim live-trading readiness.

The backtest succeeds if it produces clean, auditable evidence for each signal’s survival verdict.
