"""Transaction costs reduce net returns proportionally to turnover and bps."""
import pandas as pd

from systematic_alpha_lab.backtest.costs import transaction_cost, apply_costs


def test_cost_formula():
    # turnover 2.0 (full two-way rotation) at 5 bps -> 0.001 drag
    assert abs(transaction_cost(2.0, 5) - 0.001) < 1e-12
    assert transaction_cost(0.0, 25) == 0.0


def test_net_below_gross_when_trading():
    gross = pd.Series([0.01, 0.01, 0.01])
    turn = pd.Series([0.0, 1.0, 0.0])
    net = apply_costs(gross, turn, 10)
    assert net.iloc[0] == gross.iloc[0]              # no trade -> no cost
    assert net.iloc[1] < gross.iloc[1]               # trade -> cost drag
    assert abs((gross.iloc[1] - net.iloc[1]) - 0.001) < 1e-12  # 1.0 * 10bps


def test_higher_bps_more_drag():
    gross = pd.Series([0.01])
    turn = pd.Series([1.0])
    assert apply_costs(gross, turn, 25).iloc[0] < apply_costs(gross, turn, 5).iloc[0]
