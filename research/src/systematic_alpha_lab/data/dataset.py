"""Build the cleaned, aligned research dataset and the data-audit outputs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import os
import pandas as pd

from ..utils.io import load_config, write_json, write_parquet, ensure_dirs
from .fetch_prices import fetch_prices
from .fetch_macro import fetch_macro
from .clean_prices import clean_prices
from .align_calendar import build_price_panel, to_long_prices
from .returns import simple_returns, returns_long


@dataclass
class Dataset:
    prices: pd.DataFrame          # wide adjusted-close panel (date x ticker)
    returns: pd.DataFrame         # wide simple returns (date x ticker)
    rf_daily: pd.Series           # daily risk-free (decimal)
    macro: pd.DataFrame           # vix, yields, cpi_yoy, nber_recession, ...
    groups: dict[str, str]        # ticker -> asset group
    asset_names: dict[str, str]   # ticker -> display name
    cash_asset: str
    tradable: list[str]           # tradable ETF tickers (excludes synthetic CASH)
    calendar: pd.DatetimeIndex
    quality: dict
    provenance: dict
    universe_meta: dict

    @property
    def returns_with_cash(self) -> pd.DataFrame:
        """Returns panel including the synthetic CASH column (= risk-free)."""
        out = self.returns.copy()
        out[self.cash_asset] = self.rf_daily.reindex(out.index).ffill().fillna(0.0)
        return out


def build_dataset(use_cache: bool = True) -> Dataset:
    ensure_dirs()
    uni = load_config("universe")
    src = load_config("data_sources")

    start = os.environ.get("DATA_REQUESTED_START") or uni["requested_start"]
    end = os.environ.get("DATA_REQUESTED_END") or \
        datetime.now(timezone.utc).strftime("%Y-%m-%d")

    tickers = [a["ticker"] for a in uni["assets"]]
    groups = {a["ticker"]: a["group"] for a in uni["assets"]}
    names = {a["ticker"]: a["name"] for a in uni["assets"]}

    long, price_prov = fetch_prices(tickers, start, end, src["prices"]["yahoo_base"],
                                    use_cache=use_cache)
    clean_long, quality = clean_prices(long, start)

    panel = build_price_panel(clean_long, src["calendar_reference"])
    calendar = panel.index
    rets = simple_returns(panel)

    macro, rf_daily, macro_prov = fetch_macro(src, start, end, use_cache=use_cache)
    macro = macro.reindex(calendar).ffill()
    rf_daily = rf_daily.reindex(calendar).ffill().fillna(0.0)

    provenance = {**price_prov, **macro_prov}

    universe_meta = {
        "requested_start": start,
        "requested_end": end,
        "actual_start": calendar.min().strftime("%Y-%m-%d"),
        "actual_end": calendar.max().strftime("%Y-%m-%d"),
        "trading_days": int(len(calendar)),
        "trading_days_per_year": uni["trading_days_per_year"],
        "calendar_reference": src["calendar_reference"],
        "return_basis": "dividend- and split-adjusted close (used as a total-return approximation)",
        "price_source": src["prices"]["primary"],
        "cash_asset": uni["cash_asset"],
        "cash_proxy_etf": uni.get("cash_proxy_etf"),
        "cash_handling": (
            "Cash / T-bill exposure (the cash fallback and the cash benchmark) earns the "
            "13-week US Treasury-bill yield from Yahoo (^IRX), applied continuously across "
            "the full sample. BIL and SHV are included as tradable ETFs, but the continuous "
            "T-bill rate is used for cash so there is no 2007 inception gap."
        ),
        "assets": [
            {
                "ticker": t,
                "name": names[t],
                "group": groups[t],
                "first_date": quality["per_ticker_history"][t]["first_date"],
                "last_date": quality["per_ticker_history"][t]["last_date"],
                "observations": quality["per_ticker_history"][t]["observations"],
                "source": price_prov.get(t, {}).get("source_name", "yahoo"),
                "status": "included",
            }
            for t in tickers if t in quality["per_ticker_history"]
        ],
        "excluded_assets": quality.get("excluded_tickers", []),
        "no_lookahead_rule": (
            "feature[t] uses data through t; signal[t] formed at t; "
            "position[t+1] uses signal[t]; return[t+1] earned by position[t+1]."
        ),
    }

    # --- persist data-audit + processed outputs ---
    write_parquet("data_audit", "prices.parquet", to_long_prices(clean_long, calendar))
    write_parquet("data_audit", "returns.parquet",
                  rets.stack().rename("simple_return").reset_index()
                  .rename(columns={"level_1": "ticker"}))
    write_parquet("data_audit", "risk_free.parquet",
                  rf_daily.rename("risk_free_daily").to_frame())
    write_parquet("data_audit", "macro.parquet", macro)
    write_parquet("data_audit", "regime_inputs.parquet",
                  macro[["vix", "ten_year_yield", "cpi_yoy", "nber_recession"]])

    write_json("data_audit", "universe_metadata.json", universe_meta)
    write_json("data_audit", "data_quality_report.json", quality)
    write_json("data_audit", "data_provenance.json",
               {"sources": list({v["source_name"] for v in provenance.values()}),
                "series": provenance})

    tradable = [t for t in tickers if t in panel.columns]

    return Dataset(
        prices=panel, returns=rets, rf_daily=rf_daily, macro=macro,
        groups=groups, asset_names=names, cash_asset=uni["cash_asset"],
        tradable=tradable, calendar=calendar, quality=quality,
        provenance=provenance, universe_meta=universe_meta,
    )
