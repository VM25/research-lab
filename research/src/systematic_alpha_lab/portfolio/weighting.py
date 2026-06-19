"""Convert a signal snapshot into constrained target weights."""
from __future__ import annotations

import pandas as pd

from .constraints import apply_constraints

CASH = "CASH"


def _raw_weights(method: str, selected: list[str], scores: pd.Series,
                 scale: pd.Series | None) -> pd.Series:
    if not selected:
        return pd.Series(dtype=float)

    if method == "equal_weight":
        return pd.Series(1.0 / len(selected), index=selected)

    if method == "score_weighted":
        pos = scores.reindex(selected).clip(lower=0.0)
        # shift so the least-attractive selected name still gets a sliver
        pos = pos - pos.min() + 1e-9 if pos.sum() == 0 else pos
        if pos.sum() <= 0:
            return pd.Series(1.0 / len(selected), index=selected)
        return pos / pos.sum()

    if method == "vol_scaled":
        # equal-weight base, attenuated by each asset's vol scale; rest -> cash
        base = pd.Series(1.0 / len(selected), index=selected)
        sc = (scale.reindex(selected) if scale is not None else 1.0)
        return (base * sc).clip(lower=0.0)

    raise ValueError(f"unknown weighting method: {method}")


def target_weights(trade_row: pd.Series, score_row: pd.Series, method: str,
                   groups: dict[str, str], constraints: dict,
                   scale_row: pd.Series | None = None) -> pd.Series:
    """Target weights (assets + CASH, summing to 1.0) for one rebalance date."""
    selected = [t for t in trade_row.index if trade_row.get(t, 0) == 1
                and pd.notna(score_row.get(t))]
    raw = _raw_weights(method, selected, score_row, scale_row)
    return apply_constraints(raw, groups, constraints, cash_asset=CASH)
