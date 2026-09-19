"""
Portfolio optimization: Markowitz, Sharpe, efficient frontier.

Flat functions, vectorized with numpy. All functions accept arrays
of returns and return numpy arrays or scalars.

Part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize
from scipy import stats as scipy_stats

try:
    from . import covariance as cov_lib
except (ImportError, ValueError):
    import covariance as cov_lib


def portfolio_return(weights, mean_returns):
    """E(Rp) = w^T @ mu."""
    w = np.asarray(weights, dtype=float)
    mu = np.asarray(mean_returns, dtype=float)
    return float(w @ mu)


def portfolio_vol(weights, cov_matrix):
    """sigma_p = sqrt(w^T @ Sigma @ w)."""
    w = np.asarray(weights, dtype=float)
    C = np.asarray(cov_matrix, dtype=float)
    return float(np.sqrt(w @ C @ w))


def portfolio_sharpe(weights, mean_returns, cov_matrix, rf=0.0):
    """Sharpe Ratio: (E(Rp) - rf) / sigma_p."""
    ret = portfolio_return(weights, mean_returns)
    vol = portfolio_vol(weights, cov_matrix)
    if vol == 0:
        return 0.0
    return (ret - rf) / vol


def _neg_sharpe(weights, mean_rets, cov, rf):
    return -portfolio_sharpe(weights, mean_rets, cov, rf)


def max_sharpe_optim(returns, rf=0.0, bounds=None, constraints=None, method=None):
    """Maximize Sharpe ratio via scipy.optimize.

    Parameters
    ----------
    returns : (T, N) array-like
        Historical returns DataFrame or array.
    rf : float
        Risk-free rate (annualized).
    bounds : list of tuple or None
        Per-asset weight bounds, e.g. [(0, 1), (0, 1), ...].
        Default: (0, 1) for all.
    constraints : list of dict or None
        Additional scipy-style constraints.
        Default: sum(w) = 1.

    Returns
    -------
    dict with 'weights', 'ret', 'vol', 'sharpe', 'success'
    """
    X = np.asarray(returns, dtype=float)
    X = X[~np.isnan(X).any(axis=1)]
    T, N = X.shape

    mu = X.mean(axis=0) * 252
    cov = cov_lib.cov_hist(X) * 252

    if bounds is None:
        bounds = [(0, 1)] * N

    cons = constraints if constraints else [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    init = np.array([1.0 / N] * N)

    result = optimize.minimize(
        _neg_sharpe, init,
        args=(mu, cov, rf),
        method=method or 'SLSQP',
        bounds=bounds,
        constraints=cons
    )

    w = result['x']
    return {
        'weights': w,
        'ret': portfolio_return(w, mu),
        'vol': portfolio_vol(w, cov),
        'sharpe': portfolio_sharpe(w, mu, cov, rf),
        'success': result['success']
    }


def min_variance_optim(returns, bounds=None, constraints=None):
    """Minimize portfolio variance.

    Parameters
    ----------
    returns : (T, N) array-like
    bounds : list of tuple or None
    constraints : list of dict or None

    Returns
    -------
    dict with 'weights', 'ret', 'vol', 'success'
    """
    X = np.asarray(returns, dtype=float)
    X = X[~np.isnan(X).any(axis=1)]
    T, N = X.shape

    mu = X.mean(axis=0) * 252
    cov = cov_lib.cov_hist(X) * 252

    if bounds is None:
        bounds = [(0, 1)] * N
    cons = constraints if constraints else [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    init = np.array([1.0 / N] * N)

    def _portfolio_var(w):
        return portfolio_vol(w, cov)

    result = optimize.minimize(
        _portfolio_var, init,
        method='SLSQP',
        bounds=bounds,
        constraints=cons
    )

    w = result['x']
    return {
        'weights': w,
        'ret': portfolio_return(w, mu),
        'vol': portfolio_vol(w, cov),
        'success': result['success']
    }


def random_portfolios(returns, n_portfolios=10000, rf=0.0, seed=None):
    """Monte Carlo simulation of random portfolios.

    Parameters
    ----------
    returns : (T, N) array-like
    n_portfolios : int
    rf : float
    seed : int or None

    Returns
    -------
    DataFrame with columns: ret, vol, sharpe, weights
    """
    X = np.asarray(returns, dtype=float)
    X = X[~np.isnan(X).any(axis=1)]
    T, N = X.shape

    mu = X.mean(axis=0) * 252
    cov = cov_lib.cov_hist(X) * 252

    rng = np.random.default_rng(seed)
    portfolios = []

    for _ in range(n_portfolios):
        w = rng.random(N)
        w = w / w.sum()
        ret = float(w @ mu)
        vol = float(np.sqrt(w @ cov @ w))
        sr = (ret - rf) / vol if vol > 0 else 0.0
        portfolios.append({'ret': ret, 'vol': vol, 'sharpe': sr, 'weights': w.copy()})

    return pd.DataFrame(portfolios)


def efficient_frontier(returns, n_points=50, rf=0.0):
    """Compute the efficient frontier via target return optimization.

    Returns DataFrame with ret, vol, sharpe columns.
    """
    X = np.asarray(returns, dtype=float)
    X = X[~np.isnan(X).any(axis=1)]
    T, N = X.shape

    mu = X.mean(axis=0) * 252
    cov = cov_lib.cov_hist(X) * 252

    # Min and max achievable returns
    bounds = [(0, 1)] * N
    cons_base = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]

    min_var = min_variance_optim(returns, bounds=bounds)

    ret_min = min_var['ret']
    ret_max = mu.max()
    targets = np.linspace(ret_min, ret_max, n_points)

    frontier = []
    for t_ret in targets:
        cons = cons_base + [{'type': 'eq', 'fun': lambda w, tr=t_ret: w @ mu - tr}]
        result = optimize.minimize(
            lambda w: portfolio_vol(w, cov),
            np.array([1.0 / N] * N),
            method='SLSQP',
            bounds=bounds,
            constraints=cons
        )
        if result['success']:
            w = result['x']
            vol = portfolio_vol(w, cov)
            sr = (t_ret - rf) / vol if vol > 0 else 0.0
            frontier.append({'ret': t_ret, 'vol': vol, 'sharpe': sr})

    return pd.DataFrame(frontier)


def max_sharpe_monte_carlo(returns, n_portfolios=10000, rf=0.0, seed=None):
    """Find max Sharpe portfolio via Monte Carlo (no scipy.optimize)."""
    port_df = random_portfolios(returns, n_portfolios, rf, seed)
    best = port_df.loc[port_df['sharpe'].idxmax()]
    return {
        'weights': best['weights'],
        'ret': best['ret'],
        'vol': best['vol'],
        'sharpe': best['sharpe']
    }


def asset_stats(returns, rf=0.0):
    """Return DataFrame with individual asset stats: ret, vol, sharpe."""
    X = np.asarray(returns, dtype=float)
    X = X[~np.isnan(X).any(axis=1)]

    if isinstance(returns, pd.DataFrame):
        cols = returns.columns
    else:
        cols = [f'Asset_{i}' for i in range(X.shape[1])]

    mu = X.mean(axis=0) * 252
    sigma = X.std(axis=0, ddof=1) * np.sqrt(252)
    sr = (mu - rf) / sigma

    return pd.DataFrame({
        'retorno': mu,
        'volatilidad': sigma,
        'sharpe': sr
    }, index=cols)


def tangent_line(returns, rf=0.0):
    """Capital Market Line: returns (slope, intercept) of the tangent
    from rf to the efficient frontier."""
    best = max_sharpe_optim(returns, rf=rf)
    slope = best['sharpe']
    return {
        'slope': slope,
        'intercept': rf,
        'optimal_weights': best['weights'],
        'optimal_ret': best['ret'],
        'optimal_vol': best['vol']
    }


def cml_portfolio(returns, rf=0.0, weight_tangency=1.0, bounds=None):
    """Combine the tangency portfolio with the risk-free asset along the CML.

    The Capital Market Line (CML) shows all optimal combinations of the
    risk-free asset and the tangency (max Sharpe) portfolio.

    Parameters
    ----------
    returns : (T, N) array-like
        Historical returns.
    rf : float
        Risk-free rate (annualized).
    weight_tangency : float
        Weight allocated to the tangency portfolio:
        - 0 < w < 1 : deleverage (mix with rf) — lower risk/return, same Sharpe
        - w = 1     : pure tangency portfolio
        - w > 1     : leverage (borrow at rf) — higher risk/return, same Sharpe
    bounds : list of tuple or None
        Per-asset weight bounds for the tangency portfolio optimization.

    Returns
    -------
    dict with 'weights', 'ret', 'vol', 'sharpe', 'weight_tangency', 'weight_rf'
    """
    opt = max_sharpe_optim(returns, rf=rf, bounds=bounds)
    w_t = np.asarray(opt['weights']) * weight_tangency
    w_rf = 1.0 - weight_tangency
    ret = w_rf * rf + weight_tangency * opt['ret']
    vol = abs(weight_tangency) * opt['vol']
    sharpe = (ret - rf) / vol if vol > 0 else 0.0
    return {
        'weights': w_t,
        'weight_rf': w_rf,
        'ret': ret,
        'vol': vol,
        'sharpe': sharpe,
        'tangency_ret': opt['ret'],
        'tangency_vol': opt['vol'],
        'tangency_sharpe': opt['sharpe'],
        'weight_tangency': weight_tangency
    }
