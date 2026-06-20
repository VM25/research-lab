# Systematic Alpha Research Lab: Research Report
> Does this signal survive reality? A disciplined test of five explainable signals against costs, out-of-sample data, and stress.
## 1. Research Question
Do simple systematic alpha signals survive costs, out-of-sample testing, robustness checks, and market stress?
A signal is credible only if it survives the full process: hypothesis → signal rule → portfolio rule → cost-aware backtest → benchmark comparison → out-of-sample test → robustness → verdict.
## 2. Data and Universe
- **Universe:** 15 liquid ETFs across U.S. & international equity, Treasuries, TIPS, credit, commodities, gold, and a cash/T-bill proxy.
- **Price sample:** 2006-01-03 to 2026-06-18 (5147 trading days) on the SPY trading calendar.
- **Backtest calendar:** strategies and benchmarks share a common calendar from 2007-02-28 (when a 12-month signal history first exists). ETFs HYG, DBC, BIL, SHV start later than 2006 and each enters the strategy on its own inception.
- **Source:** FRED, NBER, Yahoo Finance; returns use dividend- and split-adjusted close (used as a total-return approximation).
- **Cash proxy:** Cash / T-bill exposure (the cash fallback and the cash benchmark) earns the 13-week US Treasury-bill yield from Yahoo (^IRX), applied continuously across the full sample. BIL and SHV are included as tradable ETFs, but the continuous T-bill rate is used for cash so there is no 2007 inception gap.
- **No look-ahead:** feature[t] uses data through t; signal[t] formed at t; position[t+1] uses signal[t]; return[t+1] earned by position[t+1].

| Ticker | Group | First | Last | Source |
| --- | --- | --- | --- | --- |
| SPY | us equity | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| QQQ | us equity | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| IWM | us equity | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| EFA | intl equity | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| EEM | intl equity | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| SHY | treasury | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| IEF | treasury | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| TLT | treasury long | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| TIP | tips | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| LQD | credit | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| HYG | credit | 2007-04-11 | 2026-06-18 | Yahoo Finance |
| DBC | commodity | 2006-02-06 | 2026-06-18 | Yahoo Finance |
| GLD | gold | 2006-01-03 | 2026-06-18 | Yahoo Finance |
| BIL | cash like | 2007-05-30 | 2026-06-18 | Yahoo Finance |
| SHV | cash like | 2007-01-11 | 2026-06-18 | Yahoo Finance |
## 3. Signal Cases
### Time-Series Momentum
- *Hypothesis:* Assets in a sustained year-long uptrend tend to continue; the strategy holds those with positive medium-term trend.
- *Formula:* `momentum_12_1[t] = adj_close[t-21] / adj_close[t-252] - 1`
- *Portfolio rule:* Hold every asset with positive 12-1 momentum, equal-weighted; park the rest in cash.
### Cross-Sectional Momentum
- *Hypothesis:* The strongest-trending assets relative to the universe tend to keep leading; the strategy holds only the relative leaders.
- *Formula:* `rank[t,i] = percentile_rank(adj_close[t-21,i] / adj_close[t-252,i] - 1)`
- *Portfolio rule:* Select the top 30% of assets by relative momentum, equal-weighted; cash if none qualify.
### Short-Term Reversal
- *Hypothesis:* Assets with a sharp multi-day sell-off tend to partially recover; the strategy holds the most oversold names.
- *Formula:* `reversal_z[t,i] = (ret_5d[t,i] - mean_63(ret_5d)) / std_63(ret_5d)`
- *Portfolio rule:* Hold the most oversold assets (z <= -1), equal-weighted; cash if none qualify.
### Volatility-Scaled Momentum
- *Hypothesis:* Trend-following with position sizes scaled down as volatility rises, holding portfolio risk closer to a fixed target.
- *Formula:* `scale[t,i] = min(1, target_vol / realized_vol_63[t,i]); weight = momentum_weight * scale`
- *Portfolio rule:* Take momentum positions, then scale each by its volatility target; unused weight to cash.
### Equal-Weight Signal Ensemble
- *Hypothesis:* Combine the four signals' standardized scores and hold the assets the blend rates positively, reducing reliance on any single signal.
- *Formula:* `ensemble_score[t,i] = mean(standardized scores of the 4 signals)`
- *Portfolio rule:* Hold every asset with a positive average score, equal-weighted; cash otherwise.
## 4. Backtest Methodology
- Long-only, no leverage, no shorting, monthly rebalance, cash fallback.
- Weights drift with returns between rebalances; turnover is measured against drifted pre-trade weights.
- **Turnover** = sum of absolute weight changes at a rebalance (total traded notional / NAV, including both buys and sells).
- Transaction costs of 5 bps (primary) with 1 / 5 / 10 / 25 bps sensitivity; cost = turnover x bps / 10000, applied as a return drag. Bid-ask spread, market impact, and intraday execution are not separately modeled.
- Benchmarks (same calendar & cost model): SPY buy & hold, 60/40, equal-weight universe, cash/T-bills, and inverse-volatility.
- Regime and crisis labels are retrospective validation tools (macro inputs lagged), not tradable real-time signals.
## 5. Validation Results
| Signal | Net CAGR | Net Sharpe | Max DD | Turnover/yr | OOS Sharpe | Cost drag |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Time-Series Momentum | 5.7% | 0.57 | -15% | 3.2 | 0.48 | 0.17% |
| Cross-Sectional Momentum | 8.8% | 0.62 | -18% | 4.2 | 0.73 | 0.23% |
| Short-Term Reversal | 5.2% | 0.45 | -29% | 12.9 | 0.33 | 0.68% |
| Volatility-Scaled Momentum | 4.3% | 0.58 | -12% | 3.2 | 0.39 | 0.16% |
| Equal-Weight Signal Ensemble | 7.7% | 0.59 | -22% | 6.0 | 0.59 | 0.33% |

Each signal was also tested across cost levels, parameter grids, rebalance frequencies, six market regimes, and five crisis windows.
## 6. Final Classification
Of five signals, 3 survived, 1 was conditional, and 1 was rejected. Discipline, not a single best backtest, separates them.

| Signal | Verdict | Note |
| --- | --- | --- |
| Time-Series Momentum | **Survived** | Time-Series Momentum holds up: net Sharpe 0.57, -15.3% max drawdown, and out-of-sample Sharpe 0.48. It survives realistic costs and parameter variation. |
| Cross-Sectional Momentum | **Survived** | Cross-Sectional Momentum holds up: net Sharpe 0.62, -18.4% max drawdown, and out-of-sample Sharpe 0.73. It survives realistic costs and parameter variation. |
| Short-Term Reversal | **Rejected** | Short-Term Reversal is rejected on this evidence: it does not clear simple benchmarks; net Sharpe 0.45, out-of-sample Sharpe 0.33. |
| Volatility-Scaled Momentum | **Conditional** | Volatility-Scaled Momentum is conditional: it adds value mainly through risk control (net Sharpe 0.58, -11.8% max drawdown) rather than raw return, and depends on costs or regime. |
| Equal-Weight Signal Ensemble | **Survived** | Equal-Weight Signal Ensemble holds up: net Sharpe 0.59, -21.8% max drawdown, and out-of-sample Sharpe 0.59. It survives realistic costs and parameter variation. |

## 7. Limitations
- Long-only ETF research over one universe and window; not a live trading system or investment advice.
- Transaction costs are a fixed-bps turnover drag; bid-ask spread, market impact, intraday execution, and taxes are not separately modeled.
- Adjusted-close returns approximate total return (dividends assumed reinvested without tax).
- Cash/T-bill exposure uses the 13-week Treasury-bill yield, not a cash ETF.
- Regime and crisis labels are retrospective validation tools, not tradable signals.
- Verdicts are qualitative research classifications, not statistical proof of alpha. Parameter grids are intentionally limited and predeclared to reduce data-mining risk.
