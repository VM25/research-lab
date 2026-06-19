"""Label each trading day by market regime using observable-lagged macro data.

Regimes overlap by design (e.g. a 2022 day can be Risk-Off, High Volatility and
Inflation Stress at once); each regime's statistics are computed over the days
that belong to it. All macro inputs are lagged one trading day so no
forward-looking information is used.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

REGIME_ORDER = ["Risk-On", "Risk-Off", "High Volatility", "Rate Shock",
                "Inflation Stress", "Normal"]


def label_regimes(ds, params: dict) -> pd.DataFrame:
    cal = ds.calendar
    macro = ds.macro.reindex(cal).ffill()

    vix = macro["vix"].shift(1)
    ten = macro["ten_year_yield"].shift(1)
    cpi_yoy = macro["cpi_yoy"]              # already observable-lagged
    rate_chg = (ten - ten.shift(63)).abs()

    spy = ds.prices["SPY"].reindex(cal)
    spy_dd = spy / spy.cummax() - 1.0

    high_vol = params["high_vol_vix"]
    rate_shock_bp = params["rate_shock_bp_3m"]
    infl = params["inflation_cpi_yoy"]
    risk_off_dd = params["risk_off_drawdown"]

    df = pd.DataFrame(index=cal)
    df["High Volatility"] = (vix > high_vol).fillna(False)
    df["Rate Shock"] = (rate_chg > rate_shock_bp).fillna(False)
    df["Inflation Stress"] = (cpi_yoy > infl).fillna(False)
    df["Risk-Off"] = (spy_dd <= risk_off_dd).fillna(False)
    df["Risk-On"] = ((spy_dd > -0.05) & (vix < high_vol)).fillna(False)
    stress = df[["High Volatility", "Rate Shock", "Inflation Stress", "Risk-Off"]].any(axis=1)
    df["Normal"] = ~stress
    return df.astype(bool)
