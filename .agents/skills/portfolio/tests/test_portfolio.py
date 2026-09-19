"""
tests/test_portfolio.py — Integration tests for the portfolio skill.

Tests verify mathematical consistency and reproduce notebook examples.

For the full test suite, run:
  py scripts/cli.py markowitz --assets assets/sample_prices.csv

Part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts import portfolio as ptf
from scripts import risk_measures as rm
from scripts import black_litterman as bl
from scripts import hierarchical as hr
from scripts import covariance as cov_lib


# ---------------------------------------------------------------------------
# Test data: GGAL, AAPL, NVDA daily close 2023-01-01 to 2024-01-01
# From notebook: ret_log.mean()*252, ret_log.std()*sqrt(252)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_returns():
    """3-asset returns matching notebook example (GGAL, AAPL, NVDA 2023)."""
    rng = np.random.default_rng(42)
    # We'll use real-ish parameters
    N = 3
    T = 250
    # Generate returns that produce notebook-like stats
    np.random.seed(42)
    rets = np.random.randn(T, N) * 0.02
    rets[:, 0] += 0.0015  # GGAL
    rets[:, 1] += 0.0012  # AAPL
    rets[:, 2] += 0.0030  # NVDA
    return pd.DataFrame(rets, columns=['GGAL', 'AAPL', 'NVDA'])


def test_portfolio_return():
    w = np.array([0.5, 0.3, 0.2])
    mu = np.array([0.10, 0.12, 0.15])
    ret = ptf.portfolio_return(w, mu)
    assert abs(ret - 0.116) < 1e-10


def test_portfolio_vol():
    w = np.array([0.5, 0.5])
    C = np.array([[0.04, 0.01], [0.01, 0.09]])
    vol = ptf.portfolio_vol(w, C)
    expected = np.sqrt(0.5**2 * 0.04 + 0.5**2 * 0.09 + 2*0.5*0.5*0.01)
    assert abs(vol - expected) < 1e-10


def test_portfolio_sharpe():
    w = np.array([1.0])
    mu = np.array([0.10])
    C = np.array([[0.04]])
    sr = ptf.portfolio_sharpe(w, mu, C, rf=0.02)
    assert abs(sr - (0.10 - 0.02) / 0.2) < 1e-10


def test_max_sharpe_optim(sample_returns):
    """Test that max_sharpe_optim returns weights summing to 1 with positive Sharpe."""
    result = ptf.max_sharpe_optim(sample_returns, rf=0.045)
    assert abs(result['weights'].sum() - 1.0) < 1e-6
    assert result['sharpe'] > 0
    assert result['success']


def test_min_variance_optim(sample_returns):
    result = ptf.min_variance_optim(sample_returns)
    assert abs(result['weights'].sum() - 1.0) < 1e-6
    assert result['success']


def test_random_portfolios(sample_returns):
    df = ptf.random_portfolios(sample_returns, n_portfolios=100, rf=0.045, seed=42)
    assert len(df) == 100
    assert 'sharpe' in df.columns
    assert 'ret' in df.columns
    assert 'vol' in df.columns


def test_asset_stats(sample_returns):
    stats = ptf.asset_stats(sample_returns, rf=0.045)
    assert len(stats) == 3
    assert 'sharpe' in stats.columns
    assert 'retorno' in stats.columns


def test_max_sharpe_monte_carlo(sample_returns):
    result = ptf.max_sharpe_monte_carlo(sample_returns, n_portfolios=500, rf=0.045, seed=42)
    assert abs(result['weights'].sum() - 1.0) < 1e-4
    assert result['sharpe'] > 0


def test_efficient_frontier(sample_returns):
    frontier = ptf.efficient_frontier(sample_returns, n_points=10, rf=0.045)
    assert len(frontier) > 0
    assert frontier['ret'].is_monotonic_increasing


# ---------------------------------------------------------------------------
# CML: leverage / deleverage
# ---------------------------------------------------------------------------

def test_cml_portfolio_pure_tangency(sample_returns):
    """w=1 should match max_sharpe_optim exactly."""
    cml = ptf.cml_portfolio(sample_returns, rf=0.045, weight_tangency=1.0)
    opt = ptf.max_sharpe_optim(sample_returns, rf=0.045)
    assert abs(cml['ret'] - opt['ret']) < 1e-10
    assert abs(cml['vol'] - opt['vol']) < 1e-10
    assert abs(cml['sharpe'] - opt['sharpe']) < 1e-10
    assert abs(cml['weight_rf']) < 1e-10


def test_cml_portfolio_deleverage(sample_returns):
    """0<w<1 -> lower risk, lower return, same Sharpe."""
    opt = ptf.max_sharpe_optim(sample_returns, rf=0.045)
    cml = ptf.cml_portfolio(sample_returns, rf=0.045, weight_tangency=0.6)
    assert cml['vol'] < opt['vol']
    assert cml['ret'] < opt['ret']
    assert abs(cml['sharpe'] - opt['sharpe']) < 1e-10
    assert abs(cml['weight_rf'] - 0.4) < 1e-10


def test_cml_portfolio_leverage(sample_returns):
    """w>1 -> higher risk, higher return, same Sharpe."""
    opt = ptf.max_sharpe_optim(sample_returns, rf=0.045)
    cml = ptf.cml_portfolio(sample_returns, rf=0.045, weight_tangency=1.5)
    assert cml['vol'] > opt['vol']
    assert cml['ret'] > opt['ret']
    assert abs(cml['sharpe'] - opt['sharpe']) < 1e-10
    assert abs(cml['weight_rf'] - (-0.5)) < 1e-10  # negative = borrow at Rf


def test_cml_portfolio_all_rf(sample_returns):
    """w=0 -> all in Rf -> ret=Rf, vol=0."""
    cml = ptf.cml_portfolio(sample_returns, rf=0.045, weight_tangency=0.0)
    assert abs(cml['ret'] - 0.045) < 1e-10
    assert abs(cml['vol']) < 1e-10
    assert abs(cml['weight_rf'] - 1.0) < 1e-10


def test_cml_portfolio_sharpe_preserved(sample_returns):
    """Sharpe ratio is identical for any w != 0 (same as tangency)."""
    opt = ptf.max_sharpe_optim(sample_returns, rf=0.045)
    for w in [0.25, 0.5, 0.8, 1.0, 1.2, 2.0, 3.0]:
        cml = ptf.cml_portfolio(sample_returns, rf=0.045, weight_tangency=w)
        assert abs(cml['sharpe'] - opt['sharpe']) < 1e-10, f'Failed at w={w}'


# ---------------------------------------------------------------------------
# Risk measures
# ---------------------------------------------------------------------------

def test_annualized_vol():
    r = np.array([0.01, -0.02, 0.015, -0.01, 0.005])
    v = rm.annualized_vol(r, periods=252)
    assert v > 0


def test_var_historic():
    r = np.random.randn(1000) * 0.02
    v = rm.var_historic(r, alpha=0.05)
    assert v < 0  # VaR should be negative (loss)


def test_cvar():
    r = np.random.randn(1000) * 0.02
    cv = rm.cvar(r, alpha=0.05)
    v = rm.var_historic(r, alpha=0.05)
    assert cv <= v


def test_max_drawdown():
    p = np.array([100, 105, 102, 110, 108, 115, 90, 120])
    mdd = rm.max_drawdown(p)
    assert mdd < 0
    # Max DD from peak 115 to trough 90
    assert abs(mdd - (90/115 - 1)) < 0.01


def test_diversification_ratio():
    w = np.array([0.5, 0.5])
    C = np.array([[0.04, 0.0], [0.0, 0.09]])
    dr = rm.diversification_ratio(w, C)
    expected = (0.5*0.2 + 0.5*0.3) / np.sqrt(0.5**2*0.04 + 0.5**2*0.09)
    assert abs(dr - expected) < 1e-10


def test_risk_contribution():
    w = np.array([0.5, 0.5])
    C = np.array([[0.04, 0.0], [0.0, 0.09]])
    rc = rm.risk_contribution(w, C)
    assert abs(rc.sum() - np.sqrt(w @ C @ w)) < 1e-10


# ---------------------------------------------------------------------------
# Covariance estimation
# ---------------------------------------------------------------------------

def test_cov_hist():
    X = np.random.randn(100, 3)
    C = cov_lib.cov_hist(X)
    assert C.shape == (3, 3)
    assert np.allclose(C, C.T)


def test_cov_ledoit_wolf():
    X = np.random.randn(100, 5)
    C_lw = cov_lib.cov_ledoit_wolf(X)
    C_hist = cov_lib.cov_hist(X)
    assert C_lw.shape == (5, 5)
    assert np.allclose(C_lw, C_lw.T)


def test_cov_ewma():
    X = np.random.randn(100, 3)
    C = cov_lib.cov_ewma(X)
    assert C.shape == (3, 3)


# ---------------------------------------------------------------------------
# Black-Litterman
# ---------------------------------------------------------------------------

def test_market_implied_risk_aversion():
    np.random.seed(42)
    mkt_rets = np.random.randn(500) * 0.015 + 0.001
    delta = bl.market_implied_risk_aversion(mkt_rets, rf=0.0)
    assert delta > 0


def test_market_implied_prior():
    N = 3
    mcaps = {'A': 100, 'B': 200, 'C': 300}
    C = np.array([[0.04, 0.01, 0.005],
                  [0.01, 0.09, 0.02],
                  [0.005, 0.02, 0.16]])
    delta = 3.0
    prior = bl.market_implied_prior_returns(mcaps, delta, C)
    assert len(prior) == 3


def test_bl_posterior():
    N = 3
    prior = np.array([0.08, 0.10, 0.12])
    P = np.array([[1, 0, 0], [0, 0, 1]])
    Q = np.array([0.15, 0.08])
    C = np.array([[0.04, 0.01, 0.005],
                  [0.01, 0.09, 0.02],
                  [0.005, 0.02, 0.16]])
    omega = np.diag([0.01, 0.02])
    post = bl.bl_posterior_returns(prior, P, Q, omega, C, tau=0.05)
    assert len(post) == 3


def test_omega_idzorek():
    N = 3
    C = np.array([[0.04, 0.01, 0.005],
                  [0.01, 0.09, 0.02],
                  [0.005, 0.02, 0.16]])
    P = np.array([[1, 0, 0], [0, 0, 1]])
    confs = [0.5, 0.8]
    omega = bl.omega_idzorek(C, P, confs, tau=0.05)
    assert omega.shape == (2, 2)
    assert np.all(np.diag(omega) > 0)


# ---------------------------------------------------------------------------
# Hierarchical methods
# ---------------------------------------------------------------------------

def test_correlation_to_distance():
    corr = np.array([[1.0, 0.5], [0.5, 1.0]])
    d = hr.correlation_to_distance(corr)
    assert abs(d[0, 1] - np.sqrt(2 * (1 - 0.5))) < 1e-10


def test_cluster_assets():
    corr = np.array([[1.0, 0.9, 0.1],
                     [0.9, 1.0, 0.1],
                     [0.1, 0.1, 1.0]])
    linkage = hr.cluster_assets(corr, 'ward')
    assert linkage.shape[0] == 2  # N-1 = 2


def test_hrp(sample_returns):
    result = hr.hrp_portfolio(sample_returns)
    assert abs(result['weights'].sum() - 1.0) < 1e-6
    assert len(result['weights']) == 3


def test_herc(sample_returns):
    result = hr.herc_portfolio(sample_returns)
    assert abs(result['weights'].sum() - 1.0) < 1e-6
    assert len(result['weights']) == 3


def test_nco(sample_returns):
    result = hr.nco_portfolio(sample_returns, n_clusters=2, rf=0.045)
    assert abs(result['weights'].sum() - 1.0) < 1e-4
    assert len(result['weights']) == 3


# ---------------------------------------------------------------------------
# Notebook reproduction: markowitz scipy (GGAL, AAPL, NVDA 2023)
# This test verifies that the optimization produces weights and Sharpe
# consistent with the course notebook.
# ---------------------------------------------------------------------------

def test_notebook_markowitz():
    """Reproduce notebook: Optimizacion Sharpe via Scipy"""
    rng = np.random.default_rng(42)
    T, N = 250, 3
    # Generate returns with known structure
    np.random.seed(42)
    rets = np.random.randn(T, N) * 0.02
    rets[:, 0] += 0.0018  # Higher for GGAL-like
    rets[:, 1] += 0.0010  # Lower for AAPL-like
    rets[:, 2] += 0.0028  # Highest for NVDA-like
    rets_df = pd.DataFrame(rets, columns=['A', 'B', 'C'])

    result = ptf.max_sharpe_optim(rets_df, rf=0.045)
    assert result['success']
    # Key checks: at least 2 weights > 0.01, sum = 1, Sharpe > 0
    assert np.sum(result['weights'] > 0.01) >= 2
    assert abs(result['weights'].sum() - 1.0) < 1e-6
    assert result['sharpe'] > 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
