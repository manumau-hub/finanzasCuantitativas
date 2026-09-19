"""
backtesting.py — Main CLI for the backtesting skill.

Modes:
  run          Full pipeline: load CSV → strategy → trades → all ratios
  walkforward  Cross-validation with N splits + gap (IS/OOS)
  sweep        2D parameter sweep → heatmap
  sweep3d      3D parameter sweep → 3D surface (JSON data for plot)
  montecarlo   Random parameter search (N iterations)
  full_index   Sweep a strategy over an entire index (e.g. S&P 500)
  optmpt       Markowitz frontier simulation and optimal portfolio
  portability  Cross-asset, cross-market, cross-timeframe validation
  event        Event-driven backtest with configurable costs
  validate     Run validation_cases.json
  bench        Microbenchmark of all ratios

Skill part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

try:
    from . import ratios
    from . import engine as bt_engine
except (ImportError, ValueError):
    import ratios
    import engine as bt_engine


def _load_defaults():
    p = os.path.join(os.path.dirname(__file__), '..', 'assets', 'defaults.json')
    p = os.path.normpath(p)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return {}


def _load_prices(path):
    df = pd.read_csv(path, parse_dates=['date']) if 'date' in pd.read_csv(path, nrows=1).columns else pd.read_csv(path)
    if 'date' in df.columns:
        df = df.set_index('date')
    df = df.sort_index()
    # Si tiene columna de retornos → convertir a precio sintético
    for rcol in ['returns_lin', 'returns_log', 'lin_return', 'log_return']:
        if rcol in df.columns:
            r = np.asarray(df[rcol].fillna(0).values, dtype=float)
            prices = 100.0 * np.cumprod(1.0 + r)
            return prices
    # Si tiene columna de precio explícito
    for pcol in ['Close', 'close', 'adjclose', 'Adj Close', 'price', 'Price']:
        if pcol in df.columns:
            return df[pcol].values
    # Una sola columna numérica
    num = df.select_dtypes(include=[np.number])
    if len(num.columns) >= 1:
        return num.iloc[:, 0].values
    raise ValueError(f"Cannot determine price column from {list(df.columns)}")


def _load_assets_for_optmpt(path):
    """Load CSV for Markowitz. Returns (df_log_returns, asset_names).
    Auto-detect: si tiene returns_lin/log → usa directo; si no → log-ratio de precios.
    """
    df = pd.read_csv(path, parse_dates=['date']) if 'date' in pd.read_csv(path, nrows=1).columns else pd.read_csv(path, index_col=0)
    if 'date' in df.columns:
        df = df.set_index('date')
    df = df.select_dtypes(include=[np.number]).dropna(how='all')
    # Detectar si ya son returns (valores pequeños centrados en ~0)
    rcol = [c for c in df.columns if c.startswith('return')]
    if rcol:
        log_r_df = df[rcol]
        log_r_df.columns = [c.replace('returns_', '') for c in log_r_df.columns]
        return log_r_df, list(log_r_df.columns)
    # Si son precios → computar log returns
    log_r = np.log(df / df.shift()).dropna()
    return log_r, list(df.columns)


def cmd_run(args):
    prices = _load_prices(args.prices)
    if args.benchmark:
        bench = _load_prices(args.benchmark)
    else:
        bench = None
    r = ratios.compute_all(prices, benchmark_prices=bench)
    print(json.dumps({k: round(v, 6) if isinstance(v, float) else str(v) for k, v in r.items()}, indent=2))


def cmd_validate(args):
    p = os.path.join(os.path.dirname(__file__), '..', 'assets', 'validation_cases.json')
    p = os.path.normpath(p)
    with open(p) as f:
        cases = json.load(f)
    n_ok = 0
    for name, case in cases.items():
        rng = np.random.default_rng(case.get('seed', 42))
        e = case['expected']
        tol = e.get('tolerance', 0.02)
        ok = True
        results = []

        if 'prices' in case:
            p_a = np.array(case['prices'], dtype=float)
            r = p_a[1:] / p_a[:-1] - 1
            lr = np.log(p_a[1:] / p_a[:-1])
        elif 'values' in case and 'n' in case:
            vals = case['values']
            n_tot = case['n']
            r = np.tile(vals, n_tot // len(vals) + 1)[:n_tot]
            lr = np.log1p(r)
            p_a = np.cumprod(1 + r)
        elif 'value' in case and 'n' in case:
            r = np.full(case['n'], case['value'])
            lr = np.log1p(r)
            p_a = np.cumprod(1 + r)
        elif 'mu' in case:
            r = rng.normal(case['mu'], case['sigma'], case['n'])
            lr = np.log1p(r)
            p_a = np.cumprod(1 + r)
        else:
            print(f'  {name}: SKIP (no known format)')
            continue

        if 'max_drawdown' in e:
            v = ratios.max_drawdown(p_a)
            ok &= abs(v - e['max_drawdown']) < tol
            results.append(f'mdd={v:.4f} (exp={e["max_drawdown"]})')
        if 'sharpe_ratio' in e:
            v = ratios.sharpe_ratio(r)
            ok &= abs(v - e['sharpe_ratio']) < tol
            results.append(f'sharpe={v:.4f} (exp={e["sharpe_ratio"]})')
        if 'cagr' in e:
            n_years = max(0.001, len(p_a) / 252)
            cumret = p_a[-1] - 1
            cagr_v = ratios.cagr(cumret, n_years)
            ok &= abs(cagr_v - e['cagr']) < tol
            results.append(f'cagr={cagr_v:.4f} (exp={e["cagr"]})')
        if 'annualized_vol' in e:
            v = ratios.annualized_vol(r)
            ok &= abs(v - e['annualized_vol']) < tol
            results.append(f'vol={v:.4f} (exp={e["annualized_vol"]})')
        if 'var_normal_95' in e:
            v = ratios.var_normal(r, alpha=0.05)
            ok &= abs(v - e['var_normal_95']) < tol
            results.append(f'var95={v:.4f} (exp={e["var_normal_95"]})')
        if 'payoff_ratio' in e:
            v = ratios.payoff_ratio(lr)
            ok &= abs(v - e['payoff_ratio']) < tol
            results.append(f'payoff={v:.4f} (exp={e["payoff_ratio"]})')
        if 'profit_factor' in e:
            v = ratios.profit_factor(lr)
            ok &= abs(v - e['profit_factor']) < tol
            results.append(f'pf={v:.4f} (exp={e["profit_factor"]})')
        if 'win_loss_ratio' in e:
            v = ratios.win_loss_ratio(lr)
            ok &= abs(v - e['win_loss_ratio']) < tol
            results.append(f'wl={v:.4f} (exp={e["win_loss_ratio"]})')
        status = 'OK' if ok else 'FAIL'
        n_ok += int(ok)
        print(f'  [{status:4s}] {name}: {", ".join(results)}')
    print(f'{n_ok}/{len(cases)} passed')


def cmd_sweep(args):
    data = _load_prices(args.prices)
    min1, max1, step1 = float(args.p1_min), float(args.p1_max), float(args.p1_step)
    min2, max2, step2 = float(args.p2_min), float(args.p2_max) if args.p2_max else None, float(args.p2_step) if args.p2_step else None
    p1_vals = np.arange(min1, max1 + step1 / 2, step1)
    # Build OHLCV DataFrame for BacktestEngine
    df = pd.DataFrame({"Close": data, "date": pd.date_range("2000-01-01", periods=len(data), freq="B")}).set_index("date")
    eng = bt_engine.BacktestEngine(commission=0.0, slippage=0.0)
    eng.load_data(df)
    if step2 is None:
        for v1 in p1_vals:
            result = eng.run(strategy='sma_crossover', strategy_params={'fast': int(v1), 'slow': int(v1 * 2.5)})
            m = result['metrics']
            print(f'{v1:.0f}\t{m.get("sharpe_ratio", 0):.4f}\t{m.get("cagr", 0):.4f}')
    else:
        p2_vals = np.arange(min2, max2 + step2 / 2, step2)
        print('p1\tp2\tsharpe\tcagr')
        for v1 in p1_vals:
            for v2 in p2_vals:
                if int(v1) >= int(v2):
                    continue
                result = eng.run(strategy='sma_crossover', strategy_params={'fast': int(v1), 'slow': int(v2)})
                m = result['metrics']
                print(f'{v1:.0f}\t{v2:.0f}\t{m.get("sharpe_ratio", 0):.4f}\t{m.get("cagr", 0):.4f}')


def cmd_event(args):
    df = pd.read_csv(args.data, parse_dates=['date']) if 'date' in pd.read_csv(args.data, nrows=1).columns else pd.read_csv(args.data)
    if 'date' in df.columns:
        df = df.set_index('date')
    df.columns = [c.capitalize() if c != 'Close' else c for c in df.columns]
    if 'Close' not in df.columns:
        raise ValueError("Data must have a Close column")
    eng = bt_engine.BacktestEngine(
        commission=float(args.commission),
        slippage=float(args.slippage)
    )
    eng.load_data(df)
    result = eng.run(args.strategy, {'fast': int(args.fast), 'slow': int(args.slow)} if args.fast else {})
    out = {'n_trades': len(result['trades'])}
    if result['trades'] is not None and len(result['trades']) > 0:
        out['avg_return'] = float(result['trades']['return'].mean())
        out['win_rate'] = float((result['trades']['return'] > 0).mean())
    out.update({k: round(v, 6) if isinstance(v, float) else v for k, v in result['metrics'].items()})
    print(json.dumps({k: v for k, v in out.items() if isinstance(v, (float, int))}, indent=2, default=str))


def cmd_walkforward(args):
    prices = _load_prices(args.prices)
    n = len(prices)
    splits = int(args.splits)
    gap = int(args.gap)
    step = (n - gap) // splits
    results = []
    for i in range(splits):
        oos_start = step * i
        oos_end = oos_start + gap
        if oos_end > n:
            break
        p_is = prices[:oos_start]
        p_oos = prices[oos_start:oos_end]
        if len(p_is) < 100 or len(p_oos) < 20:
            continue
        r = ratios.compute_all(p_is)
        r_oos = ratios.compute_all(p_oos)
        results.append({
            'split': i,
            'is_start': 0,
            'is_end': oos_start,
            'oos_start': oos_start,
            'oos_end': oos_end,
            'is_n': len(p_is),
            'oos_n': len(p_oos),
            'is_sharpe': r.get('sharpe_ratio'),
            'oos_sharpe': r_oos.get('sharpe_ratio'),
            'is_cagr': r.get('cagr'),
            'oos_cagr': r_oos.get('cagr'),
        })
    print(json.dumps(results, indent=2, default=str))


def cmd_montecarlo(args):
    prices = _load_prices(args.prices)
    n_iter = int(args.iterations) if args.iterations else 1000
    rng = np.random.default_rng()
    # Build OHLCV DataFrame for BacktestEngine
    df = pd.DataFrame({"Close": prices, "date": pd.date_range("2000-01-01", periods=len(prices), freq="B")}).set_index("date")
    eng = bt_engine.BacktestEngine(commission=0.0, slippage=0.0)
    eng.load_data(df)
    results = []
    for i in range(min(n_iter, 500)):
        fast = int(rng.integers(10, 100))
        slow = int(rng.integers(fast + 10, 200))
        result = eng.run(strategy='sma_crossover', strategy_params={'fast': fast, 'slow': slow})
        m = result['metrics']
        results.append({'fast': fast, 'slow': slow, 'sharpe': m.get('sharpe_ratio'), 'cagr': m.get('cagr')})
    df = pd.DataFrame(results).dropna()
    print(df.describe().to_string())


def cmd_optmpt(args):
    assets_csv = args.assets
    log_r, cols = _load_assets_for_optmpt(assets_csv)
    n = int(args.iterations) if args.iterations else 1000
    rng = np.random.default_rng(int(args.seed) if args.seed else 42)
    portfolios = []
    for i in range(n):
        w = rng.random(len(cols))
        w = w / w.sum()
        ret = float((log_r.mean() * w).sum() * 252)
        vol = float(np.sqrt(w @ (log_r.cov() * 252) @ w))
        sharpe = ret / vol if vol > 0 else 0
        portfolios.append({'ret': ret, 'vol': vol, 'sharpe': sharpe, 'weights': w.tolist()})
    p = pd.DataFrame(portfolios)
    best = p.loc[p['sharpe'].idxmax()]
    print('Optimal portfolio (max Sharpe):')
    print(f'  ret={best.ret:.4f}, vol={best.vol:.4f}, sharpe={best.sharpe:.4f}')
    for col, w in zip(cols, best.weights):
        print(f'  {col}: {w:.4f}')
    p[['ret', 'vol', 'sharpe']].to_csv(os.path.join(os.path.dirname(args.assets) or '.', 'frontier.csv'), index=False)
    print('Frontier saved to frontier.csv')


def main():
    parser = argparse.ArgumentParser(description='Backtesting CLI')
    sub = parser.add_subparsers(dest='mode', required=True)

    p = sub.add_parser('run', help='Full pipeline: prices → ratios')
    p.add_argument('--prices', required=True)
    p.add_argument('--benchmark')
    p.set_defaults(func=cmd_run)

    sub.add_parser('validate', help='Run validation cases').set_defaults(func=cmd_validate)

    p = sub.add_parser('sweep', help='2D param sweep')
    p.add_argument('--prices', required=True)
    p.add_argument('--p1-min', default=10, type=float)
    p.add_argument('--p1-max', default=100, type=float)
    p.add_argument('--p1-step', default=10, type=float)
    p.add_argument('--p2-min', type=float)
    p.add_argument('--p2-max', type=float)
    p.add_argument('--p2-step', type=float)
    p.set_defaults(func=cmd_sweep)

    p = sub.add_parser('event', help='Event-driven backtest')
    p.add_argument('--data', required=True)
    p.add_argument('--strategy', default='sma_crossover')
    p.add_argument('--fast', type=int)
    p.add_argument('--slow', type=int)
    p.add_argument('--commission', default='0.0')
    p.add_argument('--slippage', default='0.0')
    p.set_defaults(func=cmd_event)

    p = sub.add_parser('walkforward', help='Walk forward cross-validation')
    p.add_argument('--prices', required=True)
    p.add_argument('--splits', default='5')
    p.add_argument('--gap', default='21')
    p.set_defaults(func=cmd_walkforward)

    p = sub.add_parser('montecarlo', help='Random parameter search')
    p.add_argument('--prices', required=True)
    p.add_argument('--iterations', default='500')
    p.set_defaults(func=cmd_montecarlo)

    p = sub.add_parser('optmpt', help='Markowitz optimization')
    p.add_argument('--assets', required=True)
    p.add_argument('--iterations', default='5000')
    p.add_argument('--seed', default='42')
    p.set_defaults(func=cmd_optmpt)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
