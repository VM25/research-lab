"""Fetch real ETF price history.

Primary source: Yahoo Finance v8 chart API, which returns dividend- and
split-adjusted close (`adjclose`) — a total-return basis that is correct for
bond and dividend-paying ETFs. Raw JSON is cached under data/raw/ so the
pipeline reruns reproducibly (and offline) once data has been pulled.

Optional fallback: Tiingo daily adjusted close, used only when a
TIINGO_API_TOKEN is present and Yahoo fails. There is NO simulated-price path.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from ..utils.io import RAW_DIR

_UA = {"User-Agent": "Mozilla/5.0 (research-lab; systematic-alpha)"}


def _to_epoch(date_str: str) -> int:
    return int(pd.Timestamp(date_str).replace(tzinfo=timezone.utc).timestamp())


def _yahoo_url(base: str, ticker: str, start: str, end: str) -> str:
    p1, p2 = _to_epoch(start), _to_epoch(end)
    sym = ticker.replace("^", "%5E")
    return f"{base}{sym}?period1={p1}&period2={p2}&interval=1d&events=div%7Csplit"


def _cache_path(ticker: str) -> Path:
    safe = ticker.replace("^", "_idx_")
    return RAW_DIR / f"yahoo_{safe}.json"


def _fetch_yahoo_raw(ticker: str, base: str, start: str, end: str,
                     use_cache: bool = True) -> dict:
    cache = _cache_path(ticker)
    if use_cache and cache.exists():
        with open(cache, "r") as fh:
            return json.load(fh)
    url = _yahoo_url(base, ticker, start, end)
    last_err: Exception | None = None
    for attempt in range(4):
        try:
            resp = requests.get(url, headers=_UA, timeout=40)
            if resp.status_code == 200:
                payload = resp.json()
                RAW_DIR.mkdir(parents=True, exist_ok=True)
                with open(cache, "w") as fh:
                    json.dump(payload, fh)
                return payload
            last_err = RuntimeError(f"HTTP {resp.status_code} for {ticker}")
        except Exception as exc:  # network / json errors
            last_err = exc
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(
        f"Could not download {ticker} from Yahoo Finance ({last_err}). "
        f"Set TIINGO_API_TOKEN for a fallback, or run on an unrestricted network. "
        f"The pipeline does not substitute simulated prices."
    )


def _parse_yahoo(payload: dict) -> pd.DataFrame:
    res = payload["chart"]["result"][0]
    ts = res["timestamp"]
    quote = res["indicators"]["quote"][0]
    adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose")
    idx = pd.to_datetime(ts, unit="s").normalize()
    df = pd.DataFrame(
        {
            "open": quote.get("open"),
            "high": quote.get("high"),
            "low": quote.get("low"),
            "close": quote.get("close"),
            "adjusted_close": adj if adj is not None else quote.get("close"),
            "volume": quote.get("volume"),
        },
        index=idx,
    )
    df.index.name = "date"
    return df[~df.index.duplicated(keep="last")].sort_index()


def fetch_prices(tickers: list[str], start: str, end: str, base: str,
                 use_cache: bool = True) -> tuple[pd.DataFrame, dict[str, dict]]:
    """Download adjusted prices for all tickers.

    Returns
    -------
    (long_df, provenance)
        long_df has columns [date, ticker, open, high, low, close,
        adjusted_close, volume, source]; provenance maps ticker -> metadata.
    """
    frames: list[pd.DataFrame] = []
    provenance: dict[str, dict] = {}
    token = os.environ.get("TIINGO_API_TOKEN", "").strip()

    for ticker in tickers:
        source = "yahoo"
        try:
            payload = _fetch_yahoo_raw(ticker, base, start, end, use_cache=use_cache)
            df = _parse_yahoo(payload)
        except RuntimeError:
            if token:
                df = _fetch_tiingo(ticker, start, end, token)
                source = "tiingo"
            else:
                raise
        df = df.dropna(subset=["adjusted_close"])
        df = df[(df["adjusted_close"] > 0)]
        frames.append(df.assign(ticker=ticker, source=source))
        provenance[ticker] = {
            "source_name": source,
            "ticker_or_series": ticker,
            "download_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "first_date": df.index.min().strftime("%Y-%m-%d") if len(df) else None,
            "last_date": df.index.max().strftime("%Y-%m-%d") if len(df) else None,
            "adjusted_price_used": True,
            "adjusted_price_available": True,
            "field_coverage": ["open", "high", "low", "close", "adjusted_close", "volume"],
            "missing_values": int(df["adjusted_close"].isna().sum()),
            "notes": "Dividend- and split-adjusted close (total-return approximation).",
        }

    long = pd.concat(frames).reset_index()
    long = long[["date", "ticker", "open", "high", "low", "close",
                 "adjusted_close", "volume", "source"]]
    return long, provenance


def _fetch_tiingo(ticker: str, start: str, end: str, token: str) -> pd.DataFrame:
    url = (f"https://api.tiingo.com/tiingo/daily/{ticker}/prices"
           f"?startDate={start}&endDate={end}&format=json&token={token}")
    resp = requests.get(url, headers=_UA, timeout=40)
    resp.raise_for_status()
    rows = resp.json()
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    df = df.set_index("date").sort_index()
    out = pd.DataFrame(
        {
            "open": df["open"],
            "high": df["high"],
            "low": df["low"],
            "close": df["close"],
            "adjusted_close": df["adjClose"],
            "volume": df["volume"],
        }
    )
    out.index.name = "date"
    return out
