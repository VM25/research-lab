"""Returns are simple daily returns computed from adjusted close."""
import numpy as np
import pandas as pd

from systematic_alpha_lab.data.returns import simple_returns


def test_simple_returns_match_manual():
    idx = pd.date_range("2020-01-01", periods=4, freq="D")
    panel = pd.DataFrame({"A": [100.0, 110.0, 99.0, 99.0]}, index=idx)
    r = simple_returns(panel)["A"]
    assert np.isnan(r.iloc[0])                     # first day undefined
    assert abs(r.iloc[1] - 0.10) < 1e-12           # 110/100 - 1
    assert abs(r.iloc[2] - (-0.10)) < 1e-12        # 99/110 - 1
    assert abs(r.iloc[3] - 0.0) < 1e-12


def test_returns_undefined_across_gaps():
    idx = pd.date_range("2020-01-01", periods=3, freq="D")
    panel = pd.DataFrame({"A": [np.nan, 100.0, 105.0]}, index=idx)
    r = simple_returns(panel)["A"]
    assert np.isnan(r.iloc[1])                      # no prior price -> undefined
    assert abs(r.iloc[2] - 0.05) < 1e-12
