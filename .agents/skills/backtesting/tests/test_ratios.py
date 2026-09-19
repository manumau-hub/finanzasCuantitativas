"""
Tests for the backtesting skill ratios module.

Validates key ratios against known synthetic cases.

Run with: pytest tests/test_ratios.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import numpy as np
import pandas as pd
from scipy import stats

try:
    from . import ratios
except (ImportError, ValueError):
    import ratios


def _gen_normal(mu=0.001, sigma=0.02, n=1000, seed=42):
    rng = np.random.default_rng(seed)
    return rng.normal(mu, sigma, n)


def test_sharpe_normal():
    r = _gen_normal(n=1000)
    s = ratios.sharpe_ratio(r)
    # The Sharpe function computes (mean * 252) / (std * sqrt(252))
    # Verify it matches the direct formula
    expected = (r.mean() * 252) / (r.std(ddof=1) * np.sqrt(252))
    assert abs(s - expected) < 0.0001, f"Sharpe {s} != {expected}"


def test_var_normal():
    r = _gen_normal()
    v = ratios.var_normal(r, alpha=0.05)
    expected = -0.001 - 0.02 * stats.norm.ppf(0.05)
    assert abs(v - expected) < 0.005, f"VaR {v} != {expected}"


def test_max_drawdown():
    prices = np.array([100, 110, 120, 130, 80, 90, 100])
    mdd = ratios.max_drawdown(prices)
    expected = -38.4615 / 100
    assert abs(mdd - expected) < 0.005, f"MDD {mdd} != {expected}"


def test_cagr_constant():
    r = np.full(1000, 0.01)
    prices = np.cumprod(1 + r)
    years = (len(prices) - 1) / 252
    cumret = prices[-1] / prices[0] - 1
    c = ratios.cagr(cumret, years)
    expected = (1.01) ** 252 - 1
    assert abs(c - expected) < 0.01, f"CAGR {c} != {expected}"


def test_payoff_ratio():
    r = np.array([0.01, -0.005] * 500)
    lr = np.log1p(r)
    po = ratios.payoff_ratio(lr)
    assert abs(po - 2.0) < 0.1, f"Payoff {po} != 2.0"


def test_profit_factor():
    r = np.array([0.01, -0.005] * 500)
    lr = np.log1p(r)
    pf = ratios.profit_factor(lr)
    assert abs(pf - 2.0) < 0.1, f"PF {pf} != 2.0"


def test_kelly_binomial():
    r = np.array([0.01, -0.005] * 500)
    lr = np.log1p(r)
    k = ratios.kelly_fraction(lr)
    # p_win=0.5, loss_m=~0.005, win_m=~0.01 -> k = 0.5/0.005 - 0.5/0.01 = 100 - 50 = 50
    assert abs(k - 50) < 10, f"Kelly {k} != ~50"


def test_recovery_factor():
    prices = np.array([100, 110, 120, 130, 80, 90, 100])
    rf = ratios.recovery_factor(prices)
    mdd = ratios.max_drawdown(prices)
    cumret = prices[-1] / prices[0] - 1
    expected = cumret / abs(mdd)
    assert abs(rf - expected) < 0.005, f"RF {rf} != {expected}"


def test_linearity_coefficient():
    """Perfectly linear series should have coef = 1."""
    prices = np.linspace(100, 200, 100)
    coef = ratios.linearity_coefficient(prices)
    assert abs(coef - 1.0) < 0.01, f"CoefLin {coef} != 1.0"


def test_annualized_vol():
    r = _gen_normal()
    v = ratios.annualized_vol(r)
    expected = 0.02 * np.sqrt(252)
    assert abs(v - expected) < 0.005, f"Vol {v} != {expected}"


def test_outlier_win_ratio():
    r = _gen_normal()
    lr = np.log1p(r)
    owr = ratios.outlier_win_ratio(lr)
    assert owr >= 1.0, f"OWR {owr} < 1.0"
    assert owr < 10.0, f"OWR {owr} > 10.0"


def test_risk_of_ruin():
    rng = np.random.default_rng(123)
    r = rng.normal(0.001, 0.02, 2000)
    ror = ratios.risk_of_ruin_normal(r, capital=0.5)
    assert 0 <= ror <= 1.0, f"RoR {ror} out of range [0,1]"


def test_kurtosis_normal():
    r = _gen_normal()
    k = abs(ratios.kurtosis(r))
    assert k < 1.0, f"Kurtosis {k} too high for normal"


def test_log_returns():
    prices = np.array([100, 110, 121])
    lr = ratios.log_returns(prices)
    expected = np.array([np.nan, np.log(1.1), np.log(1.1)])
    assert np.isnan(lr[0])
    assert abs(lr[1] - np.log(1.1)) < 0.001
    assert abs(lr[2] - np.log(1.1)) < 0.001


def test_cumulative_returns():
    r = np.array([0.01, 0.02, -0.01])
    cum = ratios.cumulative_returns(r)
    # out[i] = cumprod(1+r[:i+1]) - 1
    assert abs(cum[0] - r[0]) < 0.0001, f"cum[0]={cum[0]} != {r[0]}"
    expected1 = (1+r[0])*(1+r[1])-1
    assert abs(cum[1] - expected1) < 0.0001, f"cum[1]={cum[1]} != {expected1}"
    expected2 = (1+r[0])*(1+r[1])*(1+r[2])-1
    assert abs(cum[2] - expected2) < 0.0001, f"cum[2]={cum[2]} != {expected2}"


def test_ulcer_index():
    prices = np.array([100, 110, 120, 130, 80, 90, 100])
    ui = ratios.ulcer_index(prices, period=252)
    assert ui > 0, f"Ulcer {ui} should be > 0"


def test_rachev_a():
    lr = np.log1p(np.random.default_rng(42).normal(0, 0.02, 1000))
    ra = ratios.rachev_a(lr, alpha=0.05)
    assert ra > 0, f"RachevA {ra} should be > 0"


def test_rolling_sharpe():
    prices = np.cumprod(1 + np.random.default_rng(42).normal(0.0005, 0.02, 1000))
    rs = ratios.rolling_sharpe(prices, window=252)
    assert len(rs) == len(prices)
    assert not np.all(np.isnan(rs))


if __name__ == '__main__':
    from scipy import stats
    # Run tests manually
    test_funcs = [v for k, v in globals().items() if k.startswith('test_')]
    for f in test_funcs:
        try:
            f()
            print(f'  OK {f.__name__}')
        except Exception as e:
            print(f'  FAIL {f.__name__}: {e}')
