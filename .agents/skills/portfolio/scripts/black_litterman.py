"""
Black-Litterman model: prior, views, posterior.

Flat functions, vectorized with numpy. No classes, no objects.

The BL model combines:
  1. Market equilibrium returns (prior) via reverse-optimization of CAPM
  2. Investor views (absolute or relative) with confidences
  3. Bayesian posterior returns for portfolio optimization

References:
  - Black & Litterman (1992), "Global Portfolio Optimization"
  - Idzorek (2005), "A Step-by-Step Guide to the Black-Litterman Model"
  - Meucci (2006), "Beyond Black-Litterman: Views on Non-Normal Markets"

Part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
import pandas as pd

try:
    from . import covariance as cov_lib
except (ImportError, ValueError):
    import covariance as cov_lib


def market_implied_risk_aversion(market_returns, rf=0.0, periods=252):
    """Market-implied risk aversion delta.

    delta = (E(Rm) - rf) / sigma_m^2

    Parameters
    ----------
    market_returns : array-like
        Historical returns of the market portfolio (e.g. SPY).
    rf : float
        Risk-free rate (annualized).
    periods : int
        Trading periods per year (252 for daily).

    Returns
    -------
    float : risk aversion coefficient
    """
    r = np.asarray(market_returns, dtype=float)
    r = r[~np.isnan(r)]
    excess = np.mean(r) * periods - rf
    var_m = np.var(r, ddof=1) * periods
    if var_m == 0:
        return 1.0
    return excess / var_m


def market_implied_prior_returns(market_caps, delta, cov, rf=0.0):
    """Market-implied equilibrium returns (prior Pi).

    Pi = delta * Sigma * w_mkt + rf

    where w_mkt = market_caps / sum(market_caps).
    Note: Pi is excess return; rf is added to get total return.

    Parameters
    ----------
    market_caps : dict or array-like
        Market capitalizations per asset (same order as cov columns).
    delta : float
        Risk aversion coefficient.
    cov : (N, N) array-like
        Covariance matrix of asset returns.
    rf : float
        Risk-free rate.

    Returns
    -------
    array : prior expected returns (annualized)
    """
    mcaps = np.asarray(list(market_caps.values()) if isinstance(market_caps, dict) else market_caps, dtype=float)
    C = np.asarray(cov, dtype=float)
    w_mkt = mcaps / mcaps.sum()
    return delta * C @ w_mkt + rf


def _to_views_matrix(assets, view_dict):
    """Build P and Q for absolute views.

    Parameters
    ----------
    assets : list of str
        Asset names in order.
    view_dict : dict
        {asset_name: expected_return}

    Returns
    -------
    P : (K, N) array
    Q : (K,) array
    asset_indices : list of int
        Indices of viewed assets
    """
    N = len(assets)
    asset_map = {a: i for i, a in enumerate(assets)}
    K = len(view_dict)
    P = np.zeros((K, N))
    Q = np.zeros(K)
    indices = []
    for idx, (asset, ret) in enumerate(view_dict.items()):
        if asset in asset_map:
            P[idx, asset_map[asset]] = 1
            Q[idx] = ret
            indices.append(asset_map[asset])
    return P, Q, indices


def _to_relative_views_matrix(assets, view_pairs):
    """Build P and Q for relative views.

    view_pairs: list of (asset_i, asset_j, expected_outperformance)
    e.g. [('GGAL', 'SUPV', 0.11)] means GGAL > SUPV by 11%.
    """
    N = len(assets)
    asset_map = {a: i for i, a in enumerate(assets)}
    K = len(view_pairs)
    P = np.zeros((K, N))
    Q = np.zeros(K)
    for idx, (a, b, val) in enumerate(view_pairs):
        if a in asset_map and b in asset_map:
            P[idx, asset_map[a]] = 1
            P[idx, asset_map[b]] = -1
            Q[idx] = val
    return P, Q


def omega_idzorek(cov, P, view_confidences, tau=0.05):
    """Omega matrix via Idzorek's method.

    Maps view confidences (0 to 1) to uncertainty matrix Omega.
    Uses the proportionality of Omega to P @ Sigma @ P^T.

    Parameters
    ----------
    cov : (N, N) array-like
        Covariance matrix.
    P : (K, N) array
        Views mapping matrix.
    view_confidences : list of float
        Confidences between 0 and 1 for each view.
    tau : float
        Scaling parameter (usually 0.01 to 0.05).

    Returns
    -------
    Omega : (K, K) array
    """
    C = np.asarray(cov, dtype=float)
    P_C_PT = P @ C @ P.T
    diag = np.diag(P_C_PT)
    omega = np.diag(diag)
    for i, conf in enumerate(view_confidences):
        if conf > 0:
            omega[i, i] = omega[i, i] * (1 - conf) / conf
        else:
            omega[i, i] = np.inf
    return omega * tau


def bl_posterior_returns(prior, P, Q, omega, cov, tau=0.05):
    """Black-Litterman posterior expected returns.

    E(R) = [(tau*Sigma)^-1 + P^T Omega^-1 P]^-1 *
           [(tau*Sigma)^-1 * Pi + P^T Omega^-1 * Q]

    Parameters
    ----------
    prior : (N,) array
        Prior expected returns (Pi).
    P : (K, N) array
        Views mapping matrix.
    Q : (K,) array
        Views expected returns vector.
    omega : (K, K) array
        Views uncertainty matrix.
    cov : (N, N) array
        Covariance matrix (Sigma).
    tau : float
        Scaling parameter.

    Returns
    -------
    (N,) array : posterior expected returns
    """
    pi = np.asarray(prior, dtype=float)
    C = np.asarray(cov, dtype=float)

    tau_C_inv = np.linalg.inv(tau * C)
    omega_inv = np.linalg.inv(omega)
    P_T_omega_inv = P.T @ omega_inv

    M_inv = np.linalg.inv(tau_C_inv + P_T_omega_inv @ P)
    return M_inv @ (tau_C_inv @ pi + P_T_omega_inv @ Q)


def bl_cov(cov, prior, P, omega, tau=0.05):
    """Posterior covariance matrix under BL.

    Sigma_post = Sigma + [(tau*Sigma)^-1 + P^T Omega^-1 P]^-1
    """
    C = np.asarray(cov, dtype=float)
    tau_C_inv = np.linalg.inv(tau * C)
    omega_inv = np.linalg.inv(omega)
    M_inv = np.linalg.inv(tau_C_inv + P.T @ omega_inv @ P)
    return C + M_inv


def bl_pipeline(returns, market_returns, market_caps, view_dict=None,
                view_confidences=None, relative_views=None, rf=0.0, tau=0.05,
                cov=None):
    """Full Black-Litterman pipeline: risk aversion -> prior -> posterior.

    Parameters
    ----------
    returns : (T, N) DataFrame
        Historical asset returns.
    market_returns : array-like
        Market benchmark returns (e.g. SPY).
    market_caps : dict
        {asset_name: market_cap}
    view_dict : dict or None
        Absolute views {asset: expected_return}
    view_confidences : list or None
        Confidences for absolute views.
    relative_views : list or None
        Relative views [(asset_i, asset_j, outperformance), ...]
    rf : float
        Risk-free rate.
    tau : float
        BL scaling parameter.

    Returns
    -------
    dict with 'prior', 'posterior', 'omega', 'delta', 'P', 'Q',
             'posterior_cov', 'view_dict'
    """
    X = np.asarray(returns, dtype=float)
    assets = list(returns.columns) if isinstance(returns, pd.DataFrame) else [f'A{i}' for i in range(X.shape[1])]

    if cov is None:
        cov = cov_lib.cov_ledoit_wolf(X) * 252
    # Ensure cov is numpy array
    if hasattr(cov, 'values'):
        cov = np.asarray(cov.values, dtype=float)
    delta = market_implied_risk_aversion(market_returns, 0.0)

    # Filter market_caps to only include assets present in returns
    mcaps_filtered = {k: v for k, v in market_caps.items() if k in assets}
    prior = market_implied_prior_returns(mcaps_filtered, delta, cov, rf)

    if view_dict is None and relative_views is None:
        return {
            'prior': prior, 'delta': delta, 'cov': cov,
            'assets': assets,
            'message': 'No views provided. Prior only.'
        }

    # Combine absolute + relative views
    P_list, Q_list, conf_list = [], [], []

    if view_dict:
        P_abs, Q_abs, _ = _to_views_matrix(assets, view_dict)
        P_list.append(P_abs)
        Q_list.append(Q_abs)
        if view_confidences:
            conf_list.extend(view_confidences)
        else:
            conf_list.extend([0.5] * len(view_dict))

    if relative_views:
        P_rel, Q_rel = _to_relative_views_matrix(assets, relative_views)
        P_list.append(P_rel)
        Q_list.append(Q_rel)
        conf_list.extend([0.5] * len(relative_views))

    P = np.vstack(P_list)
    Q = np.concatenate(Q_list)

    omega = omega_idzorek(cov, P, conf_list, tau)
    posterior = bl_posterior_returns(prior, P, Q, omega, cov, tau)
    post_cov = bl_cov(cov, prior, P, omega, tau)

    return {
        'prior': prior,
        'posterior': posterior,
        'omega': omega,
        'delta': delta,
        'P': P,
        'Q': Q,
        'cov': cov,
        'posterior_cov': post_cov,
        'view_dict': view_dict or {},
        'relative_views': relative_views or [],
        'assets': assets
    }
