"""
Risk measures for portfolio optimization.

Flat functions, vectorized with numpy. All functions accept 1-D arrays
of returns and return scalar values.

Part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def annualized_vol(returns, periods=252):
    """Annualized volatility: std(returns) * sqrt(periods)."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return 0.0
    return float(np.std(r, ddof=1) * np.sqrt(periods))


def annualized_return(returns, periods=252):
    """Annualized return: mean(returns) * periods."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return 0.0
    return float(np.mean(r) * periods)


def mad(returns):
    """Mean Absolute Deviation: mean(|r - mean(r)|)."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return 0.0
    return float(np.mean(np.abs(r - np.mean(r))))


def msv(returns):
    """Semi-deviation (downside): sqrt(mean(r[r < 0] ** 2)).

    Measures only negative return volatility.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    neg = r[r < 0]
    if len(neg) == 0:
        return 0.0
    return float(np.sqrt(np.mean(neg ** 2)))


def var_historic(returns, alpha=0.05):
    """Value at Risk (historic/empirical).

    Returns the alpha-quantile of returns (negative = loss).
    For 95% VaR, use alpha=0.05.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return 0.0
    return float(np.quantile(r, alpha))


def var_gaussian(returns, alpha=0.05):
    """Value at Risk under normal assumption."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return 0.0
    mu, sigma = stats.norm.fit(r)
    return float(mu + sigma * stats.norm.ppf(alpha))


def cvar(returns, alpha=0.05):
    """Conditional VaR (Expected Shortfall).

    Mean of returns below the VaR(alpha) threshold.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return 0.0
    threshold = np.quantile(r, alpha)
    tail = r[r <= threshold]
    if len(tail) == 0:
        return float(threshold)
    return float(tail.mean())


def max_drawdown(prices):
    """Maximum drawdown: (P / cummax(P) - 1).min(). Negative number."""
    p = np.asarray(prices, dtype=float)
    pk = np.maximum.accumulate(p)
    dd = p / pk - 1
    return float(np.min(dd))


def cdar(prices, alpha=0.05):
    """Conditional Drawdown at Risk.

    Mean of the worst (1-alpha) drawdowns.
    """
    p = np.asarray(prices, dtype=float)
    pk = np.maximum.accumulate(p)
    dd = p / pk - 1
    sort_dd = np.sort(dd)
    n = max(1, int(len(sort_dd) * alpha))
    return float(sort_dd[:n].mean())


def diversification_ratio(weights, cov):
    """Diversification Ratio: sum(w_i * sigma_i) / sigma_p.

    DR >= 1, higher means more diversified.
    """
    w = np.asarray(weights, dtype=float)
    C = np.asarray(cov, dtype=float)
    sigma_p = np.sqrt(w @ C @ w)
    if sigma_p == 0:
        return 1.0
    weighted_sigma = w @ np.sqrt(np.diag(C))
    return float(weighted_sigma / sigma_p)


def risk_contribution(weights, cov):
    """Marginal risk contribution per asset.

    Returns array of RC for each asset. Sum(RC) = portfolio vol.
    """
    w = np.asarray(weights, dtype=float)
    C = np.asarray(cov, dtype=float)
    sigma_p = np.sqrt(w @ C @ w)
    if sigma_p == 0:
        return np.zeros_like(w)
    mrc = (C @ w) / sigma_p
    rc = w * mrc
    return rc


def risk_contribution_pct(weights, cov):
    """Risk contribution as % of total portfolio vol."""
    rc = risk_contribution(weights, cov)
    total = rc.sum()
    if total == 0:
        return np.zeros_like(rc)
    return rc / total


def calmar_ratio(annual_ret, mdd):
    """Calmar Ratio: annualized return / |max drawdown|."""
    if mdd == 0:
        return np.nan
    return float(annual_ret / abs(mdd))
