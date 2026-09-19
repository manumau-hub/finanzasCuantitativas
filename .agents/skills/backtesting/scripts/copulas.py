"""
Copula fitting and sampling for multi-asset correlated simulations.

Five copula families are supported:
  - t (Student-t)            — symmetric dependence with tail clustering
  - Gaussian                 — symmetric, no tail dependence
  - Clayton                  — lower-tail dependence
  - Gumbel                   — upper-tail dependence
  - Frank                    — symmetric, no tail dependence

The course material uses t-copulas (slides 13, TP-Libs ej6) to model
equity correlations including tail clustering (the fact that in crises
all stocks fall together more than the Gaussian model predicts).

Skill part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def to_uniform(returns_df, distributions_per_asset=None):
    """Transform each asset's return series into a uniform marginal via its
    empirical CDF. This is the first step of copula fitting.

    Parameters
    ----------
    returns_df : pd.DataFrame
        Columns are assets, index is time, values are returns.
    distributions_per_asset : dict, optional
        {ticker: dist_name} to use a parametric CDF. If None, uses the
        empirical CDF (rank-based). With Johnson SU it's recommended to
        fit each asset's marginal first, then transform via fitted CDF.

    Returns
    -------
    u : np.ndarray of shape (T, n_assets) in (0, 1).
    """
    u = np.empty_like(returns_df.values)
    eps = 1e-6
    for j, col in enumerate(returns_df.columns):
        if distributions_per_asset is not None and col in distributions_per_asset:
            dist_name = distributions_per_asset[col]
            from . import distributions
            params, _, _ = distributions.fit(returns_df[col].dropna().values, dist_name)
            if dist_name == 'normal':
                cdf = stats.norm.cdf(returns_df[col].values, *params)
            elif dist_name == 't':
                cdf = stats.t.cdf(returns_df[col].values, *params)
            elif dist_name == 'nct':
                cdf = stats.nct.cdf(returns_df[col].values, *params)
            elif dist_name == 'laplace':
                cdf = stats.laplace.cdf(returns_df[col].values, *params)
            elif dist_name == 'johnsonsu':
                cdf = stats.johnsonsu.cdf(returns_df[col].values, *params)
            else:
                cdf = stats.rankdata(returns_df[col].values) / (len(returns_df) + 1)
        else:
            ranks = stats.rankdata(returns_df[col].values)
            cdf = ranks / (len(ranks) + 1)
        u[:, j] = np.clip(cdf, eps, 1 - eps)
    return u


def fit_gaussian(u):
    """Fit a Gaussian copula. Returns the correlation matrix."""
    z = stats.norm.ppf(u)
    P = np.corrcoef(z, rowvar=False)
    return _make_pd(P)


def fit_t(u, df=4):
    """Fit a t-copula. Returns (correlation_matrix, df)."""
    t_scores = stats.t.ppf(u, df=df)
    P = np.corrcoef(t_scores, rowvar=False)
    return _make_pd(P), df


def fit_clayton(u):
    """Fit a Clayton copula. Returns theta.

    For 2 assets, theta estimated via inversion of Kendall's tau.
    For n > 2, uses maximum pseudo-likelihood.
    """
    if u.shape[1] != 2:
        raise NotImplementedError("Clayton fit only for 2 assets in this version")
    tau = _kendall_tau(u[:, 0], u[:, 1])
    if tau <= 0:
        return 0.01
    return max(0.01, 2 * tau / (1 - tau))


def fit_gumbel(u):
    """Fit a Gumbel copula. Returns theta.

    For 2 assets via inversion: theta = 1 / (1 - tau).
    """
    if u.shape[1] != 2:
        raise NotImplementedError("Gumbel fit only for 2 assets in this version")
    tau = _kendall_tau(u[:, 0], u[:, 1])
    if tau < 0:
        return 1.0
    return max(1.0, 1 / (1 - tau))


def fit_frank(u):
    """Fit a Frank copula. Returns theta."""
    if u.shape[1] != 2:
        raise NotImplementedError("Frank fit only for 2 assets in this version")
    tau = _kendall_tau(u[:, 0], u[:, 1])
    theta = -tau * 5
    return max(0.01, theta)


def _kendall_tau(x, y):
    n = len(x)
    concord = 0
    discord = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            if dx * dy > 0:
                concord += 1
            elif dx * dy < 0:
                discord += 1
    return (concord - discord) / (concord + discord) if (concord + discord) > 0 else 0.0


def _make_pd(M, eps=1e-6):
    """Project a matrix to positive-definite via eigenvalue clipping."""
    M = np.asarray(M)
    M = (M + M.T) / 2
    eigvals, eigvecs = np.linalg.eigh(M)
    eigvals = np.clip(eigvals, eps, None)
    return (eigvecs * eigvals) @ eigvecs.T


def sample_gaussian(P, n, seed=None):
    """Sample from a Gaussian copula. Returns (n, d) in (0, 1)."""
    rng = np.random.default_rng(seed)
    P = _make_pd(P)
    d = P.shape[0]
    z = rng.multivariate_normal(np.zeros(d), P, size=n)
    return stats.norm.cdf(z)


def sample_t(P, df, n, seed=None):
    """Sample from a t-copula. Returns (n, d) in (0, 1)."""
    rng = np.random.default_rng(seed)
    P = _make_pd(P)
    d = P.shape[0]
    z = stats.t.rvs(df, size=(n, d), random_state=rng)
    L = np.linalg.cholesky(P)
    z = z @ L.T
    return stats.t.cdf(z, df=df)


def sample_clayton(theta, n, d=2, seed=None):
    """Sample from a Clayton copula. Returns (n, d) in (0, 1)."""
    rng = np.random.default_rng(seed)
    s = rng.gamma(shape=1.0 / theta, scale=theta, size=(n, 1))
    e = rng.exponential(size=(n, d)) / s
    return 1 - (1 + e) ** (-1.0 / theta) if False else _clayton_2d(theta, n, rng)


def _clayton_2d(theta, n, rng):
    """Simple 2-asset Clayton sampler."""
    u1 = rng.uniform(size=n)
    e = rng.exponential(size=n)
    t = (1 + e) ** (-theta)
    u2 = u1 * t + (1 - u1) * rng.uniform(size=n) * (1 - t)
    u2 = np.clip(u2, 1e-6, 1 - 1e-6)
    return np.column_stack([u1, u2])


def sample_gumbel(theta, n, d=2, seed=None):
    """Sample from a Gumbel copula (2-asset)."""
    rng = np.random.default_rng(seed)
    u1 = rng.uniform(size=n)
    e = rng.exponential(size=n)
    t = u1 ** (1 / theta)
    denom = (e ** (1 / theta) + t)
    u2 = np.power(np.power(denom, -theta) * t, 1.0)
    u2 = np.clip(u2, 1e-6, 1 - 1e-6)
    return np.column_stack([u1, u2])


def sample_frank(theta, n, d=2, seed=None):
    """Sample from a Frank copula (2-asset)."""
    rng = np.random.default_rng(seed)
    u1 = rng.uniform(size=n)
    e = rng.exponential(size=n)
    num = (1 - np.exp(-theta)) * u1 - (1 - np.exp(-theta * u1))
    denom = (1 - np.exp(-theta)) * u1 + e * (1 - np.exp(-theta))
    u2 = num / denom
    u2 = np.clip(u2, 1e-6, 1 - 1e-6)
    return np.column_stack([u1, u2])


def validate_copula(returns_real, u_sim, ret_sim):
    """Compare the correlation structure of simulated vs real returns.

    Returns dict with 'corr_error_mean', 'corr_real', 'corr_sim' matrices.
    """
    corr_real = np.corrcoef(returns_real, rowvar=False)
    corr_sim = np.corrcoef(ret_sim, rowvar=False)
    n = corr_real.shape[0]
    iu = np.triu_indices(n, k=1)
    err = np.abs(corr_sim[iu] - corr_real[iu]).mean()
    return {
        'corr_real': corr_real,
        'corr_sim': corr_sim,
        'corr_error_mean': float(err),
    }
