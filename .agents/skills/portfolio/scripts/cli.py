"""
portfolio/cli.py — Unified CLI for the portfolio optimization skill.

Modes:
  markowitz     Max Sharpe via scipy.optimize
  montecarlo    Monte Carlo portfolio simulation
  frontier      Efficient frontier
  cml           CML: leverage/deleverage (risk-free + tangency)
  bl-prior      Black-Litterman prior (market-implied returns)
  bl            Full Black-Litterman + Markowitz
  hrp           Hierarchical Risk Parity
  herc          Hierarchical Equal Risk Contribution
  nco           Nested Clustered Optimization
  nco-con       NCO with weight constraints
  clusters      Dendrogram linkage data (JSON)
  risk          Risk measures for a portfolio
  stats         Individual asset statistics

Part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

import sys
import os
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

try:
    from . import portfolio as ptf
    from . import risk_measures as rm
    from . import black_litterman as bl
    from . import hierarchical as hr
except (ImportError, ValueError):
    import portfolio as ptf
    import risk_measures as rm
    import black_litterman as bl
    import hierarchical as hr


def _load_returns(path, price_col=None):
    """Load returns from CSV. Auto-detect if prices or returns."""
    df = pd.read_csv(path)
    if 'date' in df.columns:
        df = df.set_index('date')

    df = df.select_dtypes(include=[np.number]).dropna(how='all')

    if price_col and price_col in df.columns:
        return pd.DataFrame({price_col: df[price_col].pct_change().dropna()})

    # Check if already returns (small values centered near 0)
    means = df.mean().abs()
    if means.max() < 0.1:
        return df

    # Assume prices -> returns
    return df.pct_change().dropna()


def _load_prices(path):
    df = pd.read_csv(path)
    if 'date' in df.columns:
        df = df.set_index('date')
    for col in ['Close', 'close', 'price', 'Price']:
        if col in df.columns:
            return df[col]
    return df.select_dtypes(include=[np.number]).iloc[:, 0]


def _load_mcaps(path):
    with open(path) as f:
        return json.load(f)


def cmd_markowitz(args):
    rets = _load_returns(args.assets)
    rf = float(args.rf)
    result = ptf.max_sharpe_optim(rets, rf=rf)
    print('Optimal portfolio (max Sharpe):')
    print(f'  ret={result["ret"]:.4f}, vol={result["vol"]:.4f}, sharpe={result["sharpe"]:.4f}')
    if isinstance(rets, pd.DataFrame):
        for a, w in zip(rets.columns, result['weights']):
            print(f'  {a}: {w:.4f}')
    else:
        print(f'  weights: {np.round(result["weights"], 4)}')


def cmd_montecarlo(args):
    rets = _load_returns(args.assets)
    rf = float(args.rf)
    n = int(args.n)
    port_df = ptf.random_portfolios(rets, n, rf, seed=int(args.seed) if args.seed else 42)
    best = port_df.loc[port_df['sharpe'].idxmax()]
    print(f'Best Sharpe: {best["sharpe"]:.4f}')
    print(f'  ret={best["ret"]:.4f}, vol={best["vol"]:.4f}')
    if isinstance(rets, pd.DataFrame):
        for a, w in zip(rets.columns, best['weights']):
            print(f'  {a}: {w:.4f}')
    else:
        print(f'  weights: {np.round(best["weights"], 4)}')
    if args.save:
        port_df[['ret', 'vol', 'sharpe']].to_csv(args.save, index=False)
        print(f'Frontier saved to {args.save}')


def cmd_frontier(args):
    rets = _load_returns(args.assets)
    rf = float(args.rf)
    n = int(args.n)
    frontier = ptf.efficient_frontier(rets, n, rf)
    print(frontier.round(6).to_string())
    if args.save:
        frontier.to_csv(args.save, index=False)


def cmd_bl_prior(args):
    rets = _load_returns(args.assets)
    market_rets = _load_returns(args.market_prices)
    mcaps = _load_mcaps(args.mcaps)
    rf = float(args.rf)
    result = bl.bl_pipeline(rets, market_rets.iloc[:, 0].values, mcaps, rf=rf)
    print(f'Risk aversion (delta): {result["delta"]:.4f}')
    print('\nPrior expected returns:')
    for a, p in zip(result['assets'], result['prior']):
        print(f'  {a}: {p:.6f}')


def cmd_bl(args):
    rets = _load_returns(args.assets)
    market_rets = _load_returns(args.market_prices)
    mcaps = _load_mcaps(args.mcaps)
    rf = float(args.rf)

    view_dict = None
    if args.views:
        view_dict = json.loads(args.views)
    relative_views = None
    if args.relative_views:
        relative_views = json.loads(args.relative_views)
    confidences = None
    if args.confidences:
        confidences = [float(c) for c in args.confidences.split(',')]

    result = bl.bl_pipeline(rets, market_rets.iloc[:, 0].values, mcaps,
                            view_dict=view_dict, view_confidences=confidences,
                            relative_views=relative_views, rf=rf)

    print(f'Risk aversion (delta): {result["delta"]:.4f}')
    print('\nReturns comparison (Prior vs Posterior vs Views):')
    df = pd.DataFrame({
        'Prior': result['prior'],
        'Posterior': result['posterior'],
    })
    if view_dict:
        views_s = pd.Series(view_dict)
        df['Views'] = views_s.reindex(df.index)
    print(df.round(6).to_string())

    # Markowitz with posterior
    if args.optimize:
        try:
            from . import portfolio as ptf2
        except (ImportError, ValueError):
            import portfolio as ptf2
        w = ptf2.max_sharpe_optim(rets.values, rf=rf)
        print(f'\nMarkowitz on BL posterior:')
        print(f'  sharpe={w["sharpe"]:.4f}')
        for a, w_val in zip(result['assets'], w['weights']):
            print(f'  {a}: {w_val:.5f}')


def cmd_hrp(args):
    rets = _load_returns(args.assets)
    result = hr.hrp_portfolio(rets, linkage_method=args.linkage)
    print('HRP weights:')
    if isinstance(rets, pd.DataFrame):
        for a, w in zip(rets.columns, result['weights']):
            print(f'  {a}: {w:.4f}')
    else:
        print(f'  {np.round(result["weights"], 4)}')


def cmd_herc(args):
    rets = _load_returns(args.assets)
    result = hr.herc_portfolio(rets, linkage_method=args.linkage)
    print('HERC weights:')
    if isinstance(rets, pd.DataFrame):
        for a, w in zip(rets.columns, result['weights']):
            print(f'  {a}: {w:.4f}')
    else:
        print(f'  {np.round(result["weights"], 4)}')


def cmd_nco(args):
    rets = _load_returns(args.assets)
    n_clust = int(args.clusters)
    rf = float(args.rf)
    result = hr.nco_portfolio(rets, n_clusters=n_clust, rf=rf,
                              linkage_method=args.linkage)
    print(f'NCO weights (k={n_clust}):')
    if isinstance(rets, pd.DataFrame):
        for a, w in zip(rets.columns, result['weights']):
            print(f'  {a}: {w:.4f}')
    else:
        print(f'  {np.round(result["weights"], 4)}')
    print(f'  Cluster weights: {np.round(result["cluster_weights"], 4)}')


def cmd_nco_con(args):
    rets = _load_returns(args.assets)
    constraints_df = pd.read_csv(args.constraints)
    classes_df = pd.read_csv(args.classes)
    rf = float(args.rf)
    n_clust = int(args.clusters)

    w_min, w_max = hr.hrp_constraints(constraints_df, classes_df)
    result = hr.nco_with_constraints(rets, w_min, w_max, n_clusters=n_clust, rf=rf)

    print(f'NCO with constraints weights (k={n_clust}):')
    if isinstance(rets, pd.DataFrame):
        for a, w in zip(rets.columns, result['weights']):
            print(f'  {a}: {w:.5f}')
    else:
        print(f'  {np.round(result["weights"], 5)}')


def cmd_clusters(args):
    rets = _load_returns(args.assets)
    linkage = hr.dendrogram_data(rets, args.linkage)
    # Output as JSON
    out = [{'i': int(i), 'j': int(j), 'dist': float(d), 'count': int(c)}
           for i, j, d, c in linkage]
    print(json.dumps(out, indent=2))


def cmd_risk(args):
    prices = _load_prices(args.prices)
    r = prices.pct_change().dropna().values
    measure = args.measure
    alpha = float(args.alpha)

    measures = {
        'vol': lambda: (np.std(r, ddof=1) * np.sqrt(252)),
        'mad': lambda: rm.mad(r),
        'msv': lambda: rm.msv(r),
        'var': lambda: rm.var_historic(r, alpha),
        'var_gauss': lambda: rm.var_gaussian(r, alpha),
        'cvar': lambda: rm.cvar(r, alpha),
        'mdd': lambda: rm.max_drawdown(prices.values),
        'cdar': lambda: rm.cdar(prices.values, alpha),
        'calmar': lambda: rm.calmar_ratio(np.mean(r) * 252, rm.max_drawdown(prices.values)),
    }

    if measure == 'all':
        for name, fn in measures.items():
            print(f'  {name}: {fn():.6f}')
    elif measure in measures:
        print(f'{measure}: {measures[measure]():.6f}')
    else:
        print(f'Unknown measure. Options: {list(measures)}')


def cmd_cml(args):
    rets = _load_returns(args.assets)
    rf = float(args.rf)
    w = float(args.weight)
    result = ptf.cml_portfolio(rets, rf=rf, weight_tangency=w)
    print(f'CML portfolio (w_tangency={w}):')
    print(f'  ret={result["ret"]:.4f}, vol={result["vol"]:.4f}, sharpe={result["sharpe"]:.4f}')
    print(f'  weight_rf={result["weight_rf"]:.4f}, weight_tangency={result["weight_tangency"]:.4f}')
    print(f'  Tangency: ret={result["tangency_ret"]:.4f}, vol={result["tangency_vol"]:.4f}, '
          f'sharpe={result["tangency_sharpe"]:.4f}')
    if isinstance(rets, pd.DataFrame):
        for a, w_val in zip(rets.columns, result['weights']):
            print(f'  {a}: {w_val:.4f}')
    else:
        print(f'  weights: {np.round(result["weights"], 4)}')


def cmd_stats(args):
    rets = _load_returns(args.assets)
    rf = float(args.rf)
    stats = ptf.asset_stats(rets, rf)
    print(stats.round(6).to_string())


def main():
    parser = argparse.ArgumentParser(description='Portfolio Optimization CLI')
    sub = parser.add_subparsers(dest='mode', required=True)

    p = sub.add_parser('markowitz', help='Max Sharpe via scipy.optimize')
    p.add_argument('--assets', required=True)
    p.add_argument('--rf', default='0.045')
    p.set_defaults(func=cmd_markowitz)

    p = sub.add_parser('montecarlo', help='Monte Carlo simulation')
    p.add_argument('--assets', required=True)
    p.add_argument('--n', default='10000')
    p.add_argument('--rf', default='0.045')
    p.add_argument('--seed', default='42')
    p.add_argument('--save')
    p.set_defaults(func=cmd_montecarlo)

    p = sub.add_parser('frontier', help='Efficient frontier')
    p.add_argument('--assets', required=True)
    p.add_argument('--n', default='50')
    p.add_argument('--rf', default='0.045')
    p.add_argument('--save')
    p.set_defaults(func=cmd_frontier)

    p = sub.add_parser('bl-prior', help='BL market-implied prior')
    p.add_argument('--assets', required=True)
    p.add_argument('--market-prices', required=True)
    p.add_argument('--mcaps', required=True)
    p.add_argument('--rf', default='0.045')
    p.set_defaults(func=cmd_bl_prior)

    p = sub.add_parser('bl', help='Full Black-Litterman')
    p.add_argument('--assets', required=True)
    p.add_argument('--market-prices', required=True)
    p.add_argument('--mcaps', required=True)
    p.add_argument('--views', help='JSON dict of absolute views')
    p.add_argument('--relative-views', help='JSON list of relative views')
    p.add_argument('--confidences', help='Comma-separated confidences')
    p.add_argument('--rf', default='0.045')
    p.add_argument('--optimize', action='store_true', help='Also run Markowitz on posterior')
    p.set_defaults(func=cmd_bl)

    p = sub.add_parser('hrp', help='Hierarchical Risk Parity')
    p.add_argument('--assets', required=True)
    p.add_argument('--linkage', default='ward')
    p.set_defaults(func=cmd_hrp)

    p = sub.add_parser('herc', help='Hierarchical Equal Risk Contribution')
    p.add_argument('--assets', required=True)
    p.add_argument('--linkage', default='ward')
    p.set_defaults(func=cmd_herc)

    p = sub.add_parser('nco', help='Nested Clustered Optimization')
    p.add_argument('--assets', required=True)
    p.add_argument('--clusters', default='4')
    p.add_argument('--rf', default='0.045')
    p.add_argument('--linkage', default='ward')
    p.set_defaults(func=cmd_nco)

    p = sub.add_parser('nco-con', help='NCO with constraints')
    p.add_argument('--assets', required=True)
    p.add_argument('--constraints', required=True)
    p.add_argument('--classes', required=True)
    p.add_argument('--clusters', default='4')
    p.add_argument('--rf', default='0.045')
    p.set_defaults(func=cmd_nco_con)

    p = sub.add_parser('clusters', help='Dendrogram data')
    p.add_argument('--assets', required=True)
    p.add_argument('--linkage', default='ward')
    p.set_defaults(func=cmd_clusters)

    p = sub.add_parser('risk', help='Risk measures')
    p.add_argument('--prices', required=True)
    p.add_argument('--measure', default='all')
    p.add_argument('--alpha', default='0.05')
    p.set_defaults(func=cmd_risk)

    p = sub.add_parser('cml', help='CML portfolio: combine risk-free + tangency (leverage/deleverage)')
    p.add_argument('--assets', required=True)
    p.add_argument('--rf', default='0.045')
    p.add_argument('--weight', default='1.0', help='Weight in tangency portfolio (0-1 deleverage, >1 leverage)')
    p.set_defaults(func=cmd_cml)

    p = sub.add_parser('stats', help='Asset statistics')
    p.add_argument('--assets', required=True)
    p.add_argument('--rf', default='0.045')
    p.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
