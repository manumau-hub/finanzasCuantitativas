"""
Distribution fitting and selection for backtesting and forward simulation.

Five continuous distributions are supported:
  - Normal
  - t-Student
  - Non-Central t
  - Laplace
  - Johnson SU

The course material (slides 70-71) shows empirically that Johnson SU
outperforms Normal for VaR estimation on US equities and bonds: Normal
consistently underestimates VaR, while Johnson SU produces errors that
are approximately zero-mean (neither systematic over- nor under-estimation).

Skill part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


_DISTRIBUTIONS = ['normal', 't', 'nct', 'laplace', 'johnsonsu']


def fit(returns, dist_name):
    """Fit a single distribution by name.

    Parameters
    ----------
    returns : array-like
        Return series.
    dist_name : str
        One of 'normal', 't', 'nct', 'laplace', 'johnsonsu'.

    Returns
    -------
    params : tuple
        Distribution parameters in the same order as scipy.stats.
    ks_stat : float
        Kolmogorov-Smirnov statistic.
    ks_pvalue : float
        p-value of the KS test against the fitted distribution.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 10:
        raise ValueError("Need at least 10 observations to fit a distribution")
    if dist_name == 'normal':
        params = stats.norm.fit(r)
        dist = stats.norm(*params)
    elif dist_name == 't':
        params = stats.t.fit(r)
        dist = stats.t(*params)
    elif dist_name == 'nct':
        params = stats.nct.fit(r)
        dist = stats.nct(*params)
    elif dist_name == 'laplace':
        params = stats.laplace.fit(r)
        dist = stats.laplace(*params)
    elif dist_name == 'johnsonsu':
        params = stats.johnsonsu.fit(r)
        dist = stats.johnsonsu(*params)
    else:
        raise ValueError(f"Unknown dist_name '{dist_name}'. Choose from {_DISTRIBUTIONS}")
    ks_stat, ks_pvalue = stats.kstest(r, dist.cdf)
    return params, ks_stat, ks_pvalue


def best_fit(returns, distributions=None):
    """Try multiple distributions and return the one with the lowest KS stat.

    Returns
    -------
    dict with keys: name, params, ks_stat, ks_pvalue.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if distributions is None:
        distributions = _DISTRIBUTIONS
    results = []
    for name in distributions:
        try:
            params, ks_stat, ks_pvalue = fit(r, name)
            results.append({
                'name': name,
                'params': params,
                'ks_stat': ks_stat,
                'ks_pvalue': ks_pvalue,
            })
        except Exception:
            continue
    if not results:
        raise RuntimeError("No distribution could be fit")
    results.sort(key=lambda x: x['ks_stat'])
    return results[0]


def compare_distributions(returns):
    """Fit all distributions and return a comparison DataFrame."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    rows = []
    for name in _DISTRIBUTIONS:
        try:
            params, ks_stat, ks_pvalue = fit(r, name)
            rows.append({
                'distribution': name,
                'params': params,
                'ks_stat': ks_stat,
                'ks_pvalue': ks_pvalue,
                'aic': _aic(r, name, params),
            })
        except Exception as e:
            rows.append({
                'distribution': name,
                'params': None,
                'ks_stat': np.nan,
                'ks_pvalue': np.nan,
                'aic': np.nan,
            })
    df = pd.DataFrame(rows)
    return df.sort_values('ks_stat').reset_index(drop=True)


def _aic(returns, dist_name, params):
    """Akaike Information Criterion (rough, for ranking only)."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    k = len(params)
    try:
        if dist_name == 'normal':
            log_lik = np.sum(stats.norm.logpdf(r, *params))
        elif dist_name == 't':
            log_lik = np.sum(stats.t.logpdf(r, *params))
        elif dist_name == 'nct':
            log_lik = np.sum(stats.nct.logpdf(r, *params))
        elif dist_name == 'laplace':
            log_lik = np.sum(stats.laplace.logpdf(r, *params))
        elif dist_name == 'johnsonsu':
            log_lik = np.sum(stats.johnsonsu.logpdf(r, *params))
        else:
            return np.nan
        return 2 * k - 2 * log_lik
    except Exception:
        return np.nan


def sample(returns, dist_name, n, seed=None):
    """Sample n returns from a fitted distribution.

    Returns an array of shape (n,) with the same statistical properties.
    """
    params, _, _ = fit(returns, dist_name)
    rng = np.random.default_rng(seed)
    if dist_name == 'normal':
        return rng.normal(*params, size=n)
    if dist_name == 't':
        return stats.t.rvs(*params, size=n, random_state=rng)
    if dist_name == 'nct':
        return stats.nct.rvs(*params, size=n, random_state=rng)
    if dist_name == 'laplace':
        return stats.laplace.rvs(*params, size=n, random_state=rng)
    if dist_name == 'johnsonsu':
        return stats.johnsonsu.rvs(*params, size=n, random_state=rng)
    raise ValueError(f"Unknown dist_name '{dist_name}'")
