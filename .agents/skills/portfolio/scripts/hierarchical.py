"""
Hierarchical portfolio construction: HRP, HERC, NCO.

Flat functions, vectorized with numpy + scipy.cluster.hierarchy.
No classes, no objects.

References:
  - Lopez de Prado (2016), "Building Diversified Portfolios that Outperform
    Out of Sample" (HRP)
  - De Prado (2019), "Nested Clustered Optimization" (NCO)
  - Pfitzinger & Katzke (2019), "NCO with Constraints"

Part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.cluster import hierarchy as sch
from scipy.spatial.distance import squareform

try:
    from . import covariance as cov_lib
    from . import portfolio as ptf
except (ImportError, ValueError):
    import covariance as cov_lib
    import portfolio as ptf


def correlation_to_distance(corr):
    """Convert correlation matrix to distance matrix.

    d = sqrt(2 * (1 - rho))

    This is a proper Euclidean distance metric.
    """
    corr = np.asarray(corr, dtype=float)
    return np.sqrt(2 * (1 - np.clip(corr, -1, 1)))


def cluster_assets(corr, linkage_method='ward'):
    """Hierarchical clustering of assets.

    Parameters
    ----------
    corr : (N, N) array
        Correlation matrix.
    linkage_method : str
        'single', 'complete', 'average', 'ward', 'centroid', 'median'

    Returns
    -------
    linkage : (N-1, 4) array
        Linkage matrix (scipy format).
    """
    dist = correlation_to_distance(corr)
    condensed = squareform(dist, checks=False)
    return sch.linkage(condensed, method=linkage_method)


def get_quasi_diag(linkage):
    """Get quasi-diagonal order from linkage matrix (seriation).

    Orders assets so that similar ones are adjacent.
    """
    return sch.leaves_list(linkage)


def _get_cluster_assets(linkage, n_assets, n_clusters):
    """Assign each asset to a cluster."""
    from scipy.cluster.hierarchy import fcluster
    return fcluster(linkage, n_clusters, criterion='maxclust') - 1


def hrp_portfolio(returns, cov=None, linkage_method='ward'):
    """Hierarchical Risk Parity (HRP).

    Allocates using a top-down recursive bisection of the dendrogram.
    No quadratic optimization needed.

    Parameters
    ----------
    returns : (T, N) array-like
    cov : (N, N) array or None
        If None, computed from returns.
    linkage_method : str

    Returns
    -------
    dict with 'weights', 'clusters'
    """
    X = np.asarray(returns, dtype=float)
    X = X[~np.isnan(X).any(axis=1)]

    if cov is None:
        cov = cov_lib.cov_hist(X)
    corr = cov / np.outer(np.sqrt(np.diag(cov)), np.sqrt(np.diag(cov)))
    corr = np.clip(corr, -1, 1)

    linkage = cluster_assets(corr, linkage_method)
    order = get_quasi_diag(linkage)

    N = X.shape[1]
    w = np.ones(N) / N

    # Recursive bisection on ordered assets
    def _bisect(assets_idx):
        if len(assets_idx) < 2:
            return
        mid = len(assets_idx) // 2
        left = assets_idx[:mid]
        right = assets_idx[mid:]

        cov_lr = cov[np.ix_(left, right)]
        var_left = np.trace(cov[np.ix_(left, left)])
        var_right = np.trace(cov[np.ix_(right, right)])

        alpha = 1 - var_left / (var_left + var_right)
        alpha = np.clip(alpha, 0, 1)

        w_left = alpha * 2  # Scale to double weight for this sub-portfolio
        w_right = (1 - alpha) * 2

        for i in left:
            w[i] *= w_left
        for i in right:
            w[i] *= w_right

        _bisect(left)
        _bisect(right)

    _bisect(order)
    w = w / w.sum()

    return {'weights': w, 'order': order, 'linkage': linkage}


def herc_portfolio(returns, cov=None, linkage_method='ward'):
    """Hierarchical Equal Risk Contribution (HERC).

    Allocates risk equally across clusters, then within each cluster
    using equal risk contribution.

    Parameters
    ----------
    returns : (T, N) array-like
    cov : (N, N) array or None
    linkage_method : str

    Returns
    -------
    dict with 'weights', 'cluster_weights', 'clusters'
    """
    X = np.asarray(returns, dtype=float)
    X = X[~np.isnan(X).any(axis=1)]

    if cov is None:
        cov = cov_lib.cov_hist(X)
    corr = cov / np.outer(np.sqrt(np.diag(cov)), np.sqrt(np.diag(cov)))
    corr = np.clip(corr, -1, 1)

    N = X.shape[1]
    linkage = cluster_assets(corr, linkage_method)
    order = get_quasi_diag(linkage)

    w = np.ones(N) / N

    def _bisect_equal_risk(assets_idx):
        if len(assets_idx) < 2:
            return
        mid = len(assets_idx) // 2
        left = assets_idx[:mid]
        right = assets_idx[mid:]

        cov_l = cov[np.ix_(left, left)]
        cov_r = cov[np.ix_(right, right)]
        risk_l = np.sqrt(np.mean(np.diag(cov_l)))
        risk_r = np.sqrt(np.mean(np.diag(cov_r)))
        total = risk_l + risk_r
        alpha = risk_r / total if total > 0 else 0.5

        w_left = alpha * 2
        w_right = (1 - alpha) * 2

        for i in left:
            w[i] *= w_left
        for i in right:
            w[i] *= w_right

        _bisect_equal_risk(left)
        _bisect_equal_risk(right)

    _bisect_equal_risk(order)
    w = w / w.sum()

    return {'weights': w, 'order': order, 'linkage': linkage}


def nco_portfolio(returns, n_clusters=4, cov=None, linkage_method='ward',
                  rf=0.0, bounds=None):
    """Nested Clustered Optimization (NCO).

    Steps:
    1. Cluster assets into n_clusters
    2. Within each cluster, optimize Markowitz
    3. Between clusters, optimize allocation

    Parameters
    ----------
    returns : (T, N) array-like
    n_clusters : int
        Number of asset clusters.
    cov : (N, N) or None
    linkage_method : str
    rf : float
    bounds : list of tuple or None

    Returns
    -------
    dict with 'weights', 'cluster_weights', 'intra_weights', 'clusters'
    """
    X = np.asarray(returns, dtype=float)
    X = X[~np.isnan(X).any(axis=1)]

    if cov is None:
        cov = cov_lib.cov_hist(X) * 252
    corr = cov / np.outer(np.sqrt(np.diag(cov)), np.sqrt(np.diag(cov)))
    corr = np.clip(corr, -1, 1)

    N = X.shape[1]
    linkage = cluster_assets(corr, linkage_method)
    clusters = _get_cluster_assets(linkage, N, min(n_clusters, N - 1))
    n_c = clusters.max() + 1

    # Intra-cluster optimization (Markowitz)
    intra_weights = []
    cluster_rets = []
    cluster_vars = []

    for c in range(n_c):
        idx = np.where(clusters == c)[0]
        if len(idx) == 1:
            intra_weights.append(np.array([1.0]))
            cluster_rets.append(X[:, idx].mean() * 252)
            cluster_vars.append(np.var(X[:, idx], ddof=1) * 252)
        else:
            rets_c = X[:, idx]
            # Subset bounds if provided
            c_bounds = None
            if bounds is not None:
                c_bounds = [bounds[i] for i in idx]
            opt = ptf.max_sharpe_optim(rets_c, rf=rf, bounds=c_bounds)
            intra_weights.append(opt['weights'])
            cluster_rets.append(opt['ret'])
            cluster_vars.append(opt['vol'] ** 2)

    # Between-cluster optimization
    C_cluster = np.diag(cluster_vars)
    mu_cluster = np.array(cluster_rets)
    w_cluster = np.array([1.0 / n_c] * n_c)
    from scipy import optimize as scipy_opt
    cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    result = scipy_opt.minimize(
        lambda w: -((w @ mu_cluster) / np.sqrt(w @ C_cluster @ w)) if np.sqrt(w @ C_cluster @ w) > 0 else 0,
        w_cluster,
        method='SLSQP',
        bounds=[(0, 1)] * n_c,
        constraints=cons
    )
    w_cluster_opt = result['x']

    # Combine
    weights = np.zeros(N)
    for c in range(n_c):
        idx = np.where(clusters == c)[0]
        for j, i in enumerate(idx):
            weights[i] = w_cluster_opt[c] * intra_weights[c][j]

    return {
        'weights': weights / weights.sum(),
        'cluster_weights': w_cluster_opt,
        'intra_weights': intra_weights,
        'clusters': clusters,
        'linkage': linkage
    }


def nco_with_constraints(returns, w_min=None, w_max=None, n_clusters=4,
                         cov=None, linkage_method='ward', rf=0.0):
    """NCO with per-asset weight constraints.

    Parameters
    ----------
    returns : (T, N) array-like
    w_min : (N,) array or None
        Minimum weight per asset.
    w_max : (N,) array or None
        Maximum weight per asset.
    n_clusters : int
    cov : (N, N) or None
    linkage_method : str
    rf : float

    Returns
    -------
    dict with 'weights', 'clusters'
    """
    N = returns.shape[1] if isinstance(returns, pd.DataFrame) else np.asarray(returns, dtype=float).shape[1]
    if w_min is None:
        w_min = np.zeros(N)
    if w_max is None:
        w_max = np.ones(N)
    bounds = list(zip(w_min, w_max))
    return nco_portfolio(returns, n_clusters, cov, linkage_method, rf, bounds)


def risk_contribution(weights, cov):
    """Risk contribution per asset (for HRP/HERC validation)."""
    try:
        from .risk_measures import risk_contribution as rc
    except (ImportError, ValueError):
        from risk_measures import risk_contribution as rc
    return rc(weights, cov)


def dendrogram_data(returns, linkage_method='ward'):
    """Return linkage matrix for dendrogram visualization."""
    X = np.asarray(returns, dtype=float)
    X = X[~np.isnan(X).any(axis=1)]
    cov = cov_lib.cov_hist(X)
    corr = cov / np.outer(np.sqrt(np.diag(cov)), np.sqrt(np.diag(cov)))
    corr = np.clip(corr, -1, 1)
    linkage = cluster_assets(corr, linkage_method)
    return linkage


def hrp_constraints(constraints_df, asset_classes):
    """Process constraints DataFrame into w_min/w_max arrays.

    Mimics Riskfolio-Lib's hrp_constraints() interface.

    Parameters
    ----------
    constraints_df : DataFrame
        Columns: Type, Set, Position, Sign, Weight
    asset_classes : DataFrame
        Columns: Assets, [class_column]

    Returns
    -------
    w_min, w_max : arrays
    """
    assets = asset_classes['Assets'].values if 'Assets' in asset_classes.columns else asset_classes.iloc[:, 0].values
    N = len(assets)
    w_min = np.zeros(N)
    w_max = np.ones(N)

    asset_to_class = {}
    if len(asset_classes.columns) > 1:
        class_col = asset_classes.columns[1]
        for _, row in asset_classes.iterrows():
            asset_to_class[row.iloc[0]] = row[class_col]

    for _, row in constraints_df.iterrows():
        if row.get('Disabled', False):
            continue
        typ = row['Type']
        sign = row['Sign']
        weight = float(row['Weight'])

        if typ == 'Assets':
            asset = row['Position']
            for i, a in enumerate(assets):
                if a == asset:
                    if sign == '>=':
                        w_min[i] = max(w_min[i], weight)
                    elif sign == '<=':
                        w_max[i] = min(w_max[i], weight)
        elif typ == 'All Assets':
            for i in range(N):
                if sign == '<=':
                    w_max[i] = min(w_max[i], weight)
                elif sign == '>=':
                    w_min[i] = max(w_min[i], weight)
        elif typ == 'Each asset in a class':
            class_name = row['Position']
            for i, a in enumerate(assets):
                if asset_to_class.get(a) == class_name:
                    if sign == '>=':
                        w_min[i] = max(w_min[i], weight)
                    elif sign == '<=':
                        w_max[i] = min(w_max[i], weight)

    return w_min, w_max


def expected_returns(returns, method='hist'):
    """Compute expected returns using various methods.

    Parameters
    ----------
    returns : (T, N) array-like
    method : str
        'hist' - historical mean (annualized)
        'ewma' - exponentially weighted

    Returns
    -------
    (N,) array
    """
    X = np.asarray(returns, dtype=float)
    X = X[~np.isnan(X).any(axis=1)]
    if method == 'ewma':
        lam = 0.94
        T = X.shape[0]
        w = np.array([(1 - lam) * lam ** (T - 1 - i) for i in range(T)])
        w = w / w.sum()
        return (w[:, None] * X).sum(axis=0) * 252
    return X.mean(axis=0) * 252
