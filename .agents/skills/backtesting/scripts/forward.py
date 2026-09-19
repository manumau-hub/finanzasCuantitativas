"""
forward.py — Forward-looking projection and stress-testing CLI.

Modes:
  project    Fan-chart with 5/50/95 bands over N paths
  risk       Forward VaR, cVaR, MaxDD, and ruin probability
  stress     Parametric shock on specific tickers
  summary    Full percentile report for a portfolio from sample_portfolios.json

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
    from . import ratios
    from . import distributions
    from . import copulas
except (ImportError, ValueError):
    import ratios
    import distributions
    import copulas


def _load_returns(path):
    df = pd.read_csv(path, parse_dates=['date']) if 'date' in pd.read_csv(path, nrows=1).columns else pd.read_csv(path, index_col=0)
    if 'date' in df.columns:
        df = df.set_index('date')
    df = df.select_dtypes(include=[np.number])
    return df


def _extract_returns(df, column=None, use_raw=False):
    """Extract returns series from a DataFrame.
    If use_raw or CSV has returns_lin/log → use as-is.
    Otherwise → compute pct_change from prices.
    """
    if column and column in df.columns:
        col = column
    else:
        col = df.columns[0]
    if use_raw:
        return df[col].dropna().values
    if col.startswith('return') or col in ('returns_lin', 'returns_log', 'lin_return', 'log_return'):
        return df[col].dropna().values
    return df[col].pct_change().dropna().values


def cmd_project(args):
    df = _load_returns(args.returns)
    ret = _extract_returns(df, args.column, args.use_raw)
    horizon = int(args.horizon) if args.horizon else 252
    n_paths = int(args.paths) if args.paths else 10000
    drift = float(args.drift) if args.drift else 0.08
    drift_daily = (1 + drift) ** (1 / 252) - 1
    params, ks, pv = distributions.fit(ret, 'johnsonsu')
    sim = stats.johnsonsu.rvs(*params, size=(n_paths, horizon), random_state=np.random.default_rng(42))
    sim = sim + drift_daily
    wealth = np.cumprod(1 + sim, axis=1)
    pcts = np.percentile(wealth, [5, 25, 50, 75, 95], axis=0)
    print('Day\tp5\tp25\tp50\tp75\tp95')
    for i in range(horizon):
        if i % 21 == 0 or i == horizon - 1:
            print(f'{i}\t{pcts[0,i]:.4f}\t{pcts[1,i]:.4f}\t{pcts[2,i]:.4f}\t{pcts[3,i]:.4f}\t{pcts[4,i]:.4f}')
    print(f'\nFinal wealth (median): {np.median(wealth[:,-1]):.4f}')
    print(f'Probability of < 0.8 final wealth: {(wealth[:,-1] < 0.8).mean():.4f}')


def cmd_risk(args):
    df = _load_returns(args.returns)
    ret = _extract_returns(df, args.column, args.use_raw)
    horizon = int(args.horizon) if args.horizon else 252
    n_paths = int(args.paths) if args.paths else 10000
    drift = float(args.drift) if args.drift else 0.08
    drift_daily = (1 + drift) ** (1 / 252) - 1
    params, ks, pv = distributions.fit(ret, 'johnsonsu')
    sim = stats.johnsonsu.rvs(*params, size=(n_paths, horizon), random_state=np.random.default_rng(42))
    sim = sim + drift_daily
    wealth = np.cumprod(1 + sim, axis=1)
    final_ret = wealth[:, -1] / wealth[:, 0] - 1
    var_95 = np.percentile(final_ret, 5)
    var_99 = np.percentile(final_ret, 1)
    # MaxDD per path
    maxdds = (wealth / np.maximum.accumulate(wealth, axis=1) - 1).min(axis=1)
    ruin_prob = (wealth[:, -1] < wealth[:, 0] * (1 - float(args.ruin) / 100) if args.ruin else (wealth[:, -1] < 0.5)).mean()
    print(f'Forward VaR 95%: {var_95:.4f}')
    print(f'Forward VaR 99%: {var_99:.4f}')
    print(f'cVaR 95% (Expected Shortfall): {final_ret[final_ret <= var_95].mean() if len(final_ret[final_ret <= var_95]) > 0 else np.nan:.4f}')
    print(f'MaxDD mean: {maxdds.mean():.4f}')
    print(f'MaxDD 95th: {np.percentile(maxdds, 95):.4f}')
    print(f'Ruin prob (< 50%): {ruin_prob:.4f}')


def cmd_stress(args):
    df = _load_returns(args.returns)
    scenario = args.scenario
    base_drift = float(args.drift) if args.drift else 0.08
    shocks = {}
    for part in scenario.split(','):
        if ':' in part:
            ticker, shock = part.split(':')
            shocks[ticker.strip()] = shock.strip()
    print(f'Stress scenario: {shocks}')
    for col in df.columns:
        if col in shocks or '*' in shocks:
            shock_str = shocks.get(col, shocks.get('*', '-3sigma'))
            mult = float(shock_str.replace('sigma', ''))
            ret = _extract_returns(df, col, args.use_raw)
            shock_val = mult * ret.std()
            expected_impact = base_drift + shock_val
            print(f'  {col}: expected return under stress = {expected_impact:.4f}')


def cmd_summary(args):
    p = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sample_portfolios.json')
    p = os.path.normpath(p)
    with open(p) as f:
        portfolios = json.load(f)
    name = args.name
    cfg = portfolios.get(name)
    if not cfg:
        print(f"Available portfolios: {list(portfolios)}")
        return
    print(json.dumps(cfg, indent=2))
    print(f'\nTickers: {list(cfg.get("tickers", {}))}')
    print(f'Strategy: {cfg.get("strategy", "unknown")}')
    print(f'Source: {cfg.get("source", "unknown")}')


def main():
    parser = argparse.ArgumentParser(description='Forward-looking risk CLI')
    sub = parser.add_subparsers(dest='mode', required=True)

    p = sub.add_parser('project', help='Fan-chart projection')
    p.add_argument('--returns', required=True, help='Path to returns CSV')
    p.add_argument('--column', help='Column name')
    p.add_argument('--horizon', default='252')
    p.add_argument('--paths', default='10000')
    p.add_argument('--drift', default='0.08')
    p.add_argument('--use-raw', action='store_true', help='CSV already contains returns (skip pct_change)')
    p.set_defaults(func=cmd_project)

    p = sub.add_parser('risk', help='Forward risk metrics')
    p.add_argument('--returns', required=True)
    p.add_argument('--column')
    p.add_argument('--horizon', default='252')
    p.add_argument('--paths', default='10000')
    p.add_argument('--drift', default='0.08')
    p.add_argument('--ruin', default='50')
    p.add_argument('--use-raw', action='store_true', help='CSV already contains returns (skip pct_change)')
    p.set_defaults(func=cmd_risk)

    p = sub.add_parser('stress', help='Parametric stress test')
    p.add_argument('--returns', required=True)
    p.add_argument('--scenario', required=True, help='TICKER:-3sigma,TICKER2:+2sigma or *:-3sigma')
    p.add_argument('--drift', default='0.08')
    p.add_argument('--use-raw', action='store_true', help='CSV already contains returns (skip pct_change)')
    p.set_defaults(func=cmd_stress)

    p = sub.add_parser('summary', help='Show portfolio config')
    p.add_argument('--name', required=True)
    p.set_defaults(func=cmd_summary)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
