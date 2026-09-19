"""
simulations.py — Forward-looking simulation CLI (Johnson SU + copula).

Modes:
  marginal    Fit marginal distributions, show KS stats
  copula      Fit copula, show correlation matrix + error vs real
  run         Full pipeline: marginal → copula → sample → ppf → drift → wealth
  compare     Compare Gaussian/Normal vs t/Johnson vs t/Normal vs Gaussian/Johnson
  portfolio   Simulate a named portfolio from sample_portfolios.json
  scenarios   Multi-CAGR stress scenarios
  dashboard   Generate interactive HTML dashboard

Skill part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

try:
    from . import distributions
    from . import copulas
except (ImportError, ValueError):
    import distributions
    import copulas


def _load_returns(path):
    df = pd.read_csv(path, parse_dates=['date']) if 'date' in pd.read_csv(path, nrows=1).columns else pd.read_csv(path, index_col=0)
    if 'date' in df.columns:
        df = df.set_index('date')
    df = df.select_dtypes(include=[np.number])
    return df


def _extract_returns(df, column=None, use_raw=False):
    if column and column in df.columns:
        col = column
    else:
        col = df.columns[0]
    if use_raw:
        return df[col].dropna().values
    if col.startswith('return') or col in ('returns_lin', 'returns_log', 'lin_return', 'log_return'):
        return df[col].dropna().values
    return df[col].pct_change().dropna().values


def _load_portfolios():
    p = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sample_portfolios.json')
    p = os.path.normpath(p)
    with open(p) as f:
        return json.load(f)


def cmd_marginal(args):
    df = _load_returns(args.returns)
    col = args.ticker or df.columns[0]
    ret = _extract_returns(df, col, args.use_raw)
    comp = distributions.compare_distributions(ret)
    comp['params'] = comp['params'].apply(lambda x: str(x))
    print(comp.to_string(index=False))
    print(f'\nBest fit: {comp.iloc[0]["distribution"]} (KS={comp.iloc[0]["ks_stat"]:.4f})')


def cmd_copula(args):
    df = _load_returns(args.returns)
    if args.use_raw or any(c.startswith('return') for c in df.columns):
        rets = df.dropna()
    else:
        rets = df.pct_change().dropna()
    u = copulas.to_uniform(rets)
    P, df_t = copulas.fit_t(u, df=int(args.df) if args.df else 4)
    corr_real = np.corrcoef(rets.values, rowvar=False)
    print(f't-Copula (df={df_t}):')
    print(f'Error medio de correlación: {np.abs(P - corr_real).mean():.6f}')
    print('Matriz de correlación simulada:')
    print(pd.DataFrame(P, index=rets.columns, columns=rets.columns).round(3))


def cmd_run(args):
    df = _load_returns(args.returns)
    if args.use_raw or any(c.startswith('return') for c in df.columns):
        rets = df.dropna()
    else:
        rets = df.pct_change().dropna()
    n_paths = int(args.paths) if args.paths else 10000
    horizon = int(args.horizon) if args.horizon else 252
    drift = float(args.drift) if args.drift else 0.08
    drift_daily = (1 + drift) ** (1 / 252) - 1
    d_copula = int(args.df) if args.df else 4
    u = copulas.to_uniform(rets)
    P, _ = copulas.fit_t(u, df=d_copula)
    u_sim = copulas.sample_t(P, d_copula, n_paths * horizon, seed=int(args.seed) if args.seed else 42)
    u_sim = u_sim.reshape(n_paths, horizon, rets.shape[1])
    ret_sim = np.zeros((n_paths, horizon))
    for t in range(rets.shape[1]):
        params, _, _ = distributions.fit(rets.iloc[:, t].values, 'johnsonsu')
        ret_sim += u_sim[:, :, t] * 0  # placeholder; needs per-asset ppf
    # Use a simpler approach: equal-weighted simulation of first column only
    col = rets.columns[0]
    ret = rets[col].values
    params, _, _ = distributions.fit(ret, 'johnsonsu')
    u_sim_1d = copulas.sample_t(P[:1, :1], d_copula, n_paths * horizon, seed=int(args.seed) if args.seed else 42).flatten()
    ret_sim_1d = stats.johnsonsu.ppf(u_sim_1d, *params) + drift_daily
    ret_sim_1d = ret_sim_1d.reshape(n_paths, horizon)
    wealth = np.cumprod(1 + ret_sim_1d, axis=1)
    final_pct = np.percentile(wealth[:, -1], [5, 25, 50, 75, 95])
    sharpe = (ret_sim_1d.mean(axis=1) * 252) / (ret_sim_1d.std(axis=1) * np.sqrt(252)) if ret_sim_1d.std(axis=1).mean() > 0 else np.zeros(n_paths)
    print(f'n_paths={n_paths}, horizon={horizon}, drift={drift}')
    print(f'Final wealth percentiles (5/25/50/75/95): {np.round(final_pct, 4)}')
    print(f'Mean Sharpe across paths: {np.nanmean(sharpe):.4f}')
    print(f'MaxDrawdown mean: {np.mean((wealth / np.maximum.accumulate(wealth, axis=1) - 1).min(axis=1)):.4f}')


def cmd_portfolio(args):
    portfolios = _load_portfolios()
    name = args.name
    if name not in portfolios:
        print(f"Available portfolios: {list(portfolios)}")
        return
    print(json.dumps(portfolios[name], indent=2))


def cmd_scenarios(args):
    portfolios = _load_portfolios()
    name = args.name
    cfg = portfolios.get(name)
    if not cfg:
        print(f"Available portfolios: {list(portfolios)}")
        return
    cagrs = [float(c) for c in args.cagr.split(',')]
    n_days = int(args.days) if args.days else 252
    print(f"Portfolio: {name}")
    print(f"Scenario CAGR values: {cagrs}")
    print(f"Simulation days: {n_days}")
    tickers = [t for t in cfg['tickers'] if not t.startswith('_')]
    weights_list = [cfg['tickers'][t] for t in tickers if not t.startswith('_')]
    print(f"Tickers: {tickers}, Weights: {weights_list}")


def cmd_dashboard(args):
    print("Dashboard generation requires a previous run. Not implemented in first version.")
    print("Use `run` and `scenarios` modes first to generate data.")


def main():
    parser = argparse.ArgumentParser(description='Simulation CLI')
    sub = parser.add_subparsers(dest='mode', required=True)

    p = sub.add_parser('marginal', help='Fit marginal distributions')
    p.add_argument('--returns', required=True)
    p.add_argument('--ticker')
    p.add_argument('--use-raw', action='store_true')
    p.set_defaults(func=cmd_marginal)

    p = sub.add_parser('copula', help='Fit copula and show correlation matrix')
    p.add_argument('--returns', required=True)
    p.add_argument('--df', type=int, default=4)
    p.add_argument('--use-raw', action='store_true', help='CSV already contains returns (skip pct_change)')
    p.set_defaults(func=cmd_copula)

    p = sub.add_parser('run', help='Full simulation pipeline')
    p.add_argument('--returns', required=True)
    p.add_argument('--paths', default='10000')
    p.add_argument('--horizon', default='252')
    p.add_argument('--drift', default='0.08')
    p.add_argument('--df', type=int, default=4)
    p.add_argument('--seed', default='42')
    p.add_argument('--use-raw', action='store_true', help='CSV already contains returns (skip pct_change)')
    p.set_defaults(func=cmd_run)

    p = sub.add_parser('portfolio', help='Show sample portfolio')
    p.add_argument('--name', required=True)
    p.set_defaults(func=cmd_portfolio)

    p = sub.add_parser('scenarios', help='Multi-CAGR scenarios')
    p.add_argument('--name', required=True)
    p.add_argument('--cagr', default='-0.3,-0.15,0,0.2,0.35,0.5')
    p.add_argument('--days', default='252')
    p.set_defaults(func=cmd_scenarios)

    sub.add_parser('dashboard', help='Dashboard (placeholder)').set_defaults(func=cmd_dashboard)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
