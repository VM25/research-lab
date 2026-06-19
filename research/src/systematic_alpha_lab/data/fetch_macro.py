"""Fetch macro/regime series used for stress and regime checks.

  VIX, 10Y yield, 13-week T-bill yield  -> Yahoo Finance (^VIX, ^TNX, ^IRX)
  CPI (CPIAUCSL)                         -> FRED CSV
  NBER recession windows                 -> documented historical constants

All series are observable-lagged before use by the regime engine so future
information is never consumed.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from ..utils.io import RAW_DIR
from .fetch_prices import _yahoo_url

_UA = {"User-Agent": "Mozilla/5.0 (research-lab; systematic-alpha)"}

# NBER-dated US recessions (peak month -> trough month), published historical fact.
NBER_RECESSIONS = [
    ("2007-12-01", "2009-06-30"),
    ("2020-02-01", "2020-04-30"),
]


def _yahoo_series(symbol: str, base: str, start: str, end: str,
                  use_cache: bool = True) -> pd.Series:
    safe = symbol.replace("^", "_idx_")
    cache = RAW_DIR / f"yahoo_{safe}.json"
    if use_cache and cache.exists():
        with open(cache, "r") as fh:
            payload = json.load(fh)
    else:
        url = _yahoo_url(base, symbol, start, end)
        payload = None
        for attempt in range(4):
            resp = requests.get(url, headers=_UA, timeout=40)
            if resp.status_code == 200:
                payload = resp.json()
                RAW_DIR.mkdir(parents=True, exist_ok=True)
                with open(cache, "w") as fh:
                    json.dump(payload, fh)
                break
            time.sleep(1.5 * (attempt + 1))
        if payload is None:
            raise RuntimeError(f"Could not download macro series {symbol} from Yahoo.")
    res = payload["chart"]["result"][0]
    idx = pd.to_datetime(res["timestamp"], unit="s").normalize()
    close = res["indicators"]["quote"][0]["close"]
    s = pd.Series(close, index=idx, name=symbol).dropna()
    return s[~s.index.duplicated(keep="last")].sort_index()


def _fred_series(symbol: str, fred_base: str, use_cache: bool = True) -> pd.Series:
    cache = RAW_DIR / f"fred_{symbol}.csv"
    if use_cache and cache.exists():
        text = cache.read_text()
    else:
        resp = requests.get(f"{fred_base}?id={symbol}", headers=_UA, timeout=40)
        resp.raise_for_status()
        text = resp.text
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        cache.write_text(text)
    from io import StringIO

    df = pd.read_csv(StringIO(text))
    date_col, val_col = df.columns[0], df.columns[1]
    df[date_col] = pd.to_datetime(df[date_col]).dt.normalize()
    s = pd.Series(pd.to_numeric(df[val_col], errors="coerce").values,
                  index=df[date_col], name=symbol).dropna()
    return s.sort_index()


def fetch_macro(cfg: dict, start: str, end: str, use_cache: bool = True
                ) -> tuple[pd.DataFrame, pd.Series, dict[str, dict]]:
    """Return (macro_df, risk_free_daily, provenance).

    macro_df columns: vix, ten_year_yield, short_rate_yield, cpi, cpi_yoy,
                      nber_recession.
    risk_free_daily: daily decimal risk-free rate from the 13-week T-bill yield.
    """
    m = cfg["macro"]
    yb = cfg["prices"]["yahoo_base"]
    prov: dict[str, dict] = {}

    vix = _yahoo_series(m["vix"]["symbol"], yb, start, end, use_cache)
    tnx = _yahoo_series(m["ten_year"]["symbol"], yb, start, end, use_cache)
    irx = _yahoo_series(m["short_rate"]["symbol"], yb, start, end, use_cache)
    cpi = _fred_series(m["cpi"]["symbol"], m["fred_base"], use_cache)

    cal = vix.index.union(tnx.index).union(irx.index)
    cal = cal[(cal >= pd.Timestamp(start)) & (cal <= pd.Timestamp(end))]

    macro = pd.DataFrame(index=cal)
    macro["vix"] = vix.reindex(cal).ffill()
    macro["ten_year_yield"] = tnx.reindex(cal).ffill()
    macro["short_rate_yield"] = irx.reindex(cal).ffill()
    # CPI is monthly and released with a lag; forward-fill onto daily and
    # shift one trading day so the level is only used once observable.
    macro["cpi"] = cpi.reindex(cal).ffill()
    cpi_yoy = cpi.pct_change(12)
    macro["cpi_yoy"] = cpi_yoy.reindex(cal).ffill().shift(1)

    rec = pd.Series(0, index=cal, dtype=int)
    for s0, s1 in NBER_RECESSIONS:
        rec.loc[(cal >= pd.Timestamp(s0)) & (cal <= pd.Timestamp(s1))] = 1
    macro["nber_recession"] = rec

    # Risk-free: 13-week T-bill yield is an annualized percent; to daily decimal.
    rf_daily = (macro["short_rate_yield"] / 100.0) / cfg["risk_free"]["annualization"]
    rf_daily = rf_daily.clip(lower=0.0).rename("risk_free_daily")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for key, sym, src, ser in [
        ("vix", m["vix"]["symbol"], "yahoo", vix),
        ("ten_year_yield", m["ten_year"]["symbol"], "yahoo", tnx),
        ("short_rate_yield", m["short_rate"]["symbol"], "yahoo", irx),
        ("cpi", m["cpi"]["symbol"], "fred", cpi),
    ]:
        prov[key] = {
            "source_name": src,
            "ticker_or_series": sym,
            "download_timestamp": now,
            "first_date": ser.index.min().strftime("%Y-%m-%d"),
            "last_date": ser.index.max().strftime("%Y-%m-%d"),
            "adjusted_price_used": False,
            "notes": "Macro/regime input; observable-lagged before use.",
        }
    prov["nber_recession"] = {
        "source_name": "NBER",
        "ticker_or_series": "US recession dates",
        "download_timestamp": now,
        "first_date": NBER_RECESSIONS[0][0],
        "last_date": NBER_RECESSIONS[-1][1],
        "adjusted_price_used": False,
        "notes": "Documented historical recession windows (constants).",
    }
    return macro, rf_daily, prov
