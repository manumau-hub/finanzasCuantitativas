"""
Covariance estimation methods for portfolio optimization.

Flat functions, vectorized with numpy. No classes, no objects.

All functions accept (T, N) DataFrames or arrays of returns and return
(N, N) covariance matrices.

Part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _to_array(X):
    if isinstance(X, pd.DataFrame):
        return X.values
    return np.asarray(X, dtype=float)


def cov_hist(returns):
    """Historical (empirical) covariance matrix.

    Standard sample covariance with ddof=1.
    """
    X = _to_array(returns)
    X = X[~np.isnan(X).any(axis=1)]
    if len(X) < 2:
        return np.eye(X.shape[1]) * 1e-6
    return np.cov(X, rowvar=False)


def _fix_nonpositive_semidefinite(matrix):
    """Fix non-positive semidefinite matrix via spectral method.

    Zeroes negative eigenvalues and rebuilds the matrix.
    Same as PyPortfolioOpt's fix_nonpositive_semidefinite(..., 'spectral').
    """
    q = np.linalg.eigvalsh(matrix)
    if np.all(q > -1e-12):
        return matrix
    q, V = np.linalg.eigh(matrix)
    q = np.where(q > 0, q, 0)
    return V @ np.diag(q) @ V.T


def _cov_ledoit_wolf_flat(X):
    """Flat numpy implementation of Ledoit-Wolf shrinkage."""
    T, N = X.shape
    if T < 2 or N < 2:
        return np.cov(X, rowvar=False)

    S = np.cov(X, rowvar=False)
    X_centered = X - X.mean(axis=0)

    mean_var = np.trace(S) / N
    target = np.eye(N) * mean_var

    X_centered2 = X_centered ** 2
    phi_mat = (X_centered2.T @ X_centered2) / T - S ** 2
    phi = np.sum(phi_mat)
    gamma = np.sum((S - target) ** 2)

    kappa = phi / gamma if gamma > 0 else 0.0
    shrinkage = max(0, min(1, kappa / T))

    return (1 - shrinkage) * S + shrinkage * target


def cov_ledoit_wolf(returns):
    """Ledoit-Wolf shrinkage covariance estimator.

    Two implementations:
    1. sklearn.covariance.LedoitWolf (when available) — exact match
    2. Flat numpy fallback (no sklearn needed)

    Handles NaN as PyPortfolioOpt does: np.nan_to_num (NaN -> 0).

    Reference: Ledoit & Wolf (2004), "A well-conditioned estimator for
    large-dimensional covariance matrices".
    """
    X = _to_array(returns)
    X = np.nan_to_num(X, nan=0.0)

    try:
        from sklearn.covariance import LedoitWolf
        return _fix_nonpositive_semidefinite(LedoitWolf().fit(X).covariance_)
    except ImportError:
        pass

    return _fix_nonpositive_semidefinite(_cov_ledoit_wolf_flat(X))


def cov_oas(returns):
    """Oracle Approximating Shrinkage (OAS) estimator.

    Similar to Ledoit-Wolf but with a closed-form optimal shrinkage
    intensity under Gaussian assumption.

    Reference: Chen et al. (2010), "Shrinkage Algorithms for MMSE
    Covariance Estimation".
    """
    X = _to_array(returns)
    X = X[~np.isnan(X).any(axis=1)]
    T, N = X.shape
    if T < 2 or N < 2:
        return cov_hist(X)

    S = np.cov(X, rowvar=False)
    X_centered = X - X.mean(axis=0)
    S_diag = np.diag(S)

    # Target: diagonal with mean variance
    mean_var = np.trace(S) / N
    target = np.eye(N) * mean_var

    # OAS shrinkage intensity
    num = (1 - 2 / N) * np.trace(S @ S) + np.trace(S) ** 2
    denom = (T + 1 - 2 / N) * (np.trace(S @ S) - np.trace(S) ** 2 / N)
    rho = min(1, num / denom) if denom > 0 else 0.0

    return (1 - rho) * S + rho * target


def cov_ewma(returns, lambda_=0.94):
    """Exponentially Weighted Moving Average covariance.

    Standard RiskMetrics approach with decay factor lambda.
    Default lambda=0.94 (RiskMetrics standard for daily data).

    Parameters
    ----------
    returns : (T, N) array-like
    lambda_ : float
        Decay factor (0 < lambda_ < 1).
    """
    X = _to_array(returns)
    X = X[~np.isnan(X).any(axis=1)]
    T, N = X.shape
    if T < 2:
        return cov_hist(X)

    weights = np.array([(1 - lambda_) * lambda_ ** (T - 1 - i) for i in range(T)])
    weights = weights / weights.sum()

    mean = (weights[:, None] * X).sum(axis=0)
    X_centered = X - mean
    cov = np.zeros((N, N))
    for t in range(T):
        cov += weights[t] * np.outer(X_centered[t], X_centered[t])
    return cov


def cov_shrunk(returns, delta=0.5):
    """Generic shrinkage with configurable intensity.

    delta=0: sample covariance (no shrinkage).
    delta=1: diagonal target only.
    """
    S = cov_hist(returns)
    target = np.eye(S.shape[0]) * np.trace(S) / S.shape[0]
    return (1 - delta) * S + delta * target
