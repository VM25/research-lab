"""Static, human-readable metadata for each signal case.

These descriptions feed signal_summary.json and the website signal cases. They
mirror docs/01_RESEARCH_THESIS.md and docs/03_SIGNAL_SPEC.md verbatim in intent.
"""
from __future__ import annotations

SIGNAL_ORDER = [
    "time_series_momentum",
    "cross_sectional_momentum",
    "short_term_reversal",
    "volatility_scaled_momentum",
    "ensemble",
]

SIGNAL_META = {
    "time_series_momentum": {
        "signal_name": "Time-Series Momentum",
        "signal_family": "time_series_momentum",
        "hypothesis": (
            "Assets with positive medium-term trends tend to keep performing, "
            "because capital moves slowly, investors underreact, and macro "
            "regimes persist."
        ),
        "plain_english_hypothesis": (
            "Assets in a sustained year-long uptrend tend to continue; the strategy "
            "holds those with positive medium-term trend."
        ),
        "formula": "momentum_12_1[t] = adj_close[t-21] / adj_close[t-252] - 1",
        "formula_short": "12-month return, skipping the last month.",
        "lookback_window": "252 trading days (skip most recent 21)",
        "rebalance_frequency": "monthly",
        "portfolio_rule": "Hold every asset with positive 12-1 momentum, equal-weighted; park the rest in cash.",
        "expected_strength": [
            "Works in persistent trend regimes",
            "Avoids prolonged drawdowns by stepping aside",
            "Rotates across asset classes",
        ],
        "expected_weakness": [
            "Lags sharp reversals",
            "Underperforms in choppy markets",
            "Misses V-shaped recoveries",
        ],
        "primary_failure_mode": "regime_dependency",
    },
    "cross_sectional_momentum": {
        "signal_name": "Cross-Sectional Momentum",
        "signal_family": "cross_sectional_momentum",
        "hypothesis": (
            "Assets with stronger relative performance tend to keep leading the "
            "weaker ones."
        ),
        "plain_english_hypothesis": (
            "The strongest-trending assets relative to the universe tend to keep "
            "leading; the strategy holds only the relative leaders."
        ),
        "formula": (
            "rank[t,i] = percentile_rank(adj_close[t-21,i] / adj_close[t-252,i] - 1)"
        ),
        "formula_short": "Own the top 30% of assets by 12-1 momentum.",
        "lookback_window": "252 trading days (skip most recent 21)",
        "rebalance_frequency": "monthly",
        "portfolio_rule": "Select the top 30% of assets by relative momentum, equal-weighted; cash if none qualify.",
        "expected_strength": [
            "Captures asset-class leadership",
            "Adapts to changing market themes",
            "Can beat naive equal weight",
        ],
        "expected_weakness": [
            "Can become concentrated",
            "Sensitive to the ranking threshold",
            "Suffers during leadership reversals",
        ],
        "primary_failure_mode": "turnover_failure",
    },
    "short_term_reversal": {
        "signal_name": "Short-Term Reversal",
        "signal_family": "short_term_reversal",
        "hypothesis": (
            "Assets with extreme short-term losses partially rebound because of "
            "overreaction, liquidity pressure, or temporary positioning."
        ),
        "plain_english_hypothesis": (
            "Assets with a sharp multi-day sell-off tend to partially recover; the "
            "strategy holds the most oversold names."
        ),
        "formula": (
            "reversal_z[t,i] = (ret_5d[t,i] - mean_63(ret_5d)) / std_63(ret_5d)"
        ),
        "formula_short": "Buy assets whose 5-day return is more than 1 sigma below normal.",
        "lookback_window": "5-day return, 63-day z-score window",
        "rebalance_frequency": "monthly",
        "portfolio_rule": "Hold the most oversold assets (z <= -1), equal-weighted; cash if none qualify.",
        "expected_strength": [
            "Captures oversold rebounds",
            "Useful for tactical entry timing",
            "Detects short-horizon dislocations",
        ],
        "expected_weakness": [
            "High turnover",
            "High transaction-cost sensitivity",
            "Fails during persistent selloffs",
        ],
        "primary_failure_mode": "cost_failure",
    },
    "volatility_scaled_momentum": {
        "signal_name": "Volatility-Scaled Momentum",
        "signal_family": "volatility_scaled_momentum",
        "hypothesis": (
            "Momentum exposure becomes steadier when position size is reduced "
            "during high-volatility periods."
        ),
        "plain_english_hypothesis": (
            "Trend-following with position sizes scaled down as volatility rises, "
            "holding portfolio risk closer to a fixed target."
        ),
        "formula": (
            "scale[t,i] = min(1, target_vol / realized_vol_63[t,i]); "
            "weight = momentum_weight * scale"
        ),
        "formula_short": "Trend-following, scaled down to a 10% volatility target.",
        "lookback_window": "252-day momentum, 63-day volatility",
        "rebalance_frequency": "monthly",
        "portfolio_rule": "Take momentum positions, then scale each by its volatility target; unused weight to cash.",
        "expected_strength": [
            "Lowers drawdowns",
            "Smooths returns",
            "Improves downside control",
        ],
        "expected_weakness": [
            "Lower upside capture",
            "De-risks after volatility spikes (late)",
            "Can miss rebounds",
        ],
        "primary_failure_mode": "drawdown_failure",
    },
    "ensemble": {
        "signal_name": "Equal-Weight Signal Ensemble",
        "signal_family": "ensemble",
        "hypothesis": (
            "Combining simple signals reduces dependence on any single fragile "
            "signal."
        ),
        "plain_english_hypothesis": (
            "Combine the four signals' standardized scores and hold the assets the "
            "blend rates positively, reducing reliance on any single signal."
        ),
        "formula": "ensemble_score[t,i] = mean(standardized scores of the 4 signals)",
        "formula_short": "Average of the four signals' standardized scores.",
        "lookback_window": "blended (5 to 252 days)",
        "rebalance_frequency": "monthly",
        "portfolio_rule": "Hold every asset with a positive average score, equal-weighted; cash otherwise.",
        "expected_strength": [
            "Lower single-signal dependence",
            "Smoother evidence profile",
            "Broader robustness across regimes",
        ],
        "expected_weakness": [
            "Can dilute a strong signal",
            "Can inherit a weak signal",
            "Failure modes are harder to read",
        ],
        "primary_failure_mode": "regime_dependency",
    },
}
