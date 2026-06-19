"""Long-only portfolio constraints.

Applies a single-asset cap and per-group caps. Any weight clipped off a capped
position is routed to cash (never redistributed in a way that re-breaches a
cap, and never used to create leverage). Shorting and leverage are disabled.
"""
from __future__ import annotations

import pandas as pd


def apply_constraints(weights: pd.Series, groups: dict[str, str],
                      constraints: dict, cash_asset: str = "CASH") -> pd.Series:
    """Return constrained weights over the same index, plus a CASH entry.

    Input `weights` are non-negative asset weights summing to <= 1. Output sums
    to exactly 1.0 with the remainder in `cash_asset`.
    """
    w = weights.clip(lower=0.0).copy()
    if cash_asset in w.index:
        w = w.drop(cash_asset)

    max_single = float(constraints["max_single_asset"])
    group_caps = constraints.get("group_caps", {})

    # 1) single-asset cap
    w = w.clip(upper=max_single)

    # 2) group caps — scale a breaching group down to its cap
    for grp, cap in group_caps.items():
        members = [t for t in w.index if groups.get(t) == grp]
        if not members:
            continue
        grp_sum = w[members].sum()
        if grp_sum > cap and grp_sum > 0:
            w[members] = w[members] * (cap / grp_sum)

    total = w.sum()
    if total > 1.0:                      # numerical safety: never exceed fully invested
        w = w / total
        total = 1.0

    out = w.copy()
    out[cash_asset] = max(0.0, 1.0 - total)
    return out
