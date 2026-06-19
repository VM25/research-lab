# 02_DATA_SPEC.md

# Systematic Alpha Research Lab — Data Specification

## Data Objective

Use clean, real, aligned financial time-series data to test whether systematic signals survive realistic validation.

The data layer must support:

```text id="8h6nqv"
prices
returns
features
signals
portfolios
benchmarks
validation
website outputs
```

Main research results must use real historical market data, not simulated ETF prices.

## Primary Universe

Use liquid ETFs across major asset groups.

| Group                  | Example Tickers |
| ---------------------- | --------------- |
| U.S. Equity            | SPY, QQQ, IWM   |
| International Equity   | EFA, EEM        |
| Treasuries             | SHY, IEF, TLT   |
| Inflation-Linked Bonds | TIP             |
| Credit                 | LQD, HYG        |
| Commodities            | DBC             |
| Gold                   | GLD             |
| Cash / T-Bill Proxy    | BIL, SHV        |

The final universe may be smaller if data quality requires exclusions.

## Price Data

Collect daily adjusted price data.

Required fields:

```text id="xyfhhj"
date
ticker
open
high
low
close
adjusted_close
volume
source
```

Portfolio returns must use `adjusted_close`.

Raw close may be stored only for audit.

## Acceptable Price Sources

Use at least one reliable source with adjusted historical prices:

* Stooq
* Yahoo Finance
* Tiingo
* Nasdaq Data Link
* Alpha Vantage
* Polygon
* other documented market-data source

The engine must record the source used for every ticker.

## Sample Period

Target period:

```text id="j0ulre"
2006-01-01 through latest complete available trading date
```

If full history is unavailable, report:

```text id="gbg6cn"
requested_start_date
actual_start_date
actual_end_date
excluded_tickers
reason_for_exclusion
```

Do not silently fill missing asset history.

## Trading Calendar

Use the U.S. equity trading calendar.

Rules:

* align all ETFs to the same trading dates
* remove dates with missing core price data
* do not forward-fill prices for return calculation
* do not create artificial returns on non-trading days
* align macro data only after it is observable

## Return Calculation

Use simple daily returns:

```text id="kl7hza"
r[t] = adjusted_close[t] / adjusted_close[t-1] - 1
```

Use simple returns for portfolio backtests.

Log returns may be calculated only for diagnostics.

Annualization:

```text id="zsh9gv"
trading_days_per_year = 252
```

## Risk-Free Rate

Use a short-rate or T-bill proxy.

Acceptable sources:

* FRED 3-month T-bill
* BIL / SHV ETF returns
* Kenneth French risk-free rate

If using an annualized rate:

```text id="qxx8vy"
risk_free_daily[t] = annual_rate[t] / 252
```

Convert percentages to decimals before use.

## Macro and Regime Data

Collect only data needed for regime and stress checks.

Required series:

| Series              | Purpose            |
| ------------------- | ------------------ |
| VIX                 | volatility regime  |
| 10Y Treasury yield  | rate regime        |
| 2Y Treasury yield   | curve/rate context |
| CPI YoY             | inflation regime   |
| recession indicator | crisis context     |

Preferred sources:

* FRED
* Cboe
* NBER
* U.S. Treasury

Macro data must be lagged or forward-filled conservatively so future information is never used.

## Data Cleaning Rules

The engine must check:

| Issue                         | Action                       |
| ----------------------------- | ---------------------------- |
| duplicate dates               | remove or flag               |
| missing adjusted close        | exclude affected row         |
| zero or negative prices       | flag invalid                 |
| extreme returns               | flag for audit               |
| missing volume                | allow if price data is valid |
| inconsistent dates            | normalize                    |
| factor or rate scale mismatch | convert correctly            |

Flag, do not automatically delete, daily returns with absolute value above 25%.

## No-Lookahead Rules

The data layer must enforce:

```text id="h5cm4q"
feature[t] uses data available through t
signal[t] is generated from feature[t]
position[t+1] uses signal[t]
return[t+1] is earned by position[t+1]
```

No same-day signal may trade on same-day return.

## Required Processed Outputs

```text id="ff7vbr"
prices.parquet
returns.parquet
risk_free.parquet
macro.parquet
regime_inputs.parquet
universe_metadata.json
data_quality_report.json
data_provenance.json
```

## Data Provenance

`data_provenance.json` must include:

```text id="foir0t"
source_name
ticker_or_series
download_timestamp
first_date
last_date
field_coverage
missing_values
adjusted_price_available
notes
```

## Data Quality Report

`data_quality_report.json` must include:

```text id="ww6n5h"
ticker_count
final_tickers
excluded_tickers
sample_start
sample_end
row_count
missing_values
duplicate_rows
invalid_prices
extreme_return_flags
final_observation_count
```

## Website Data Summary

The website must display a simple data note:

* universe used
* sample period
* source summary
* excluded assets, if any
* adjusted-close return basis
* no-lookahead timing rule

Do not overload the website with raw data tables.

## Hard Rules

* Do not use simulated ETF prices for main results.
* Do not hide missing data.
* Do not mix tickers with inconsistent histories without disclosure.
* Do not forward-fill asset prices.
* Do not use future macro data.
* Do not hardcode website numbers manually.

The data layer succeeds if every research result can be traced back to real, documented, cleaned source data.
