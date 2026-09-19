"""
Event-driven backtesting engine and the supporting trade-summary helpers.

The engine implements the pattern from the course notebooks: an explicit
bar-by-bar loop with a signalled state (in / out), a trade table built
from entry / exit signals, and a daily P&L series. Built-in strategies
are exposed as plain functions; the engine itself is engine-neutral.

CRITICAL: the engine shifts every signal by one bar so that the decision
to buy or sell is made on data available BEFORE the day it is acted on.
The course material emphasises this point in the notebooks ("importantisimo
el shift()!"). Any custom strategy function should return the signal that
should be ACTED on given the data at bar t, not the bar t+1.

Skill part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Trade-summary helpers (from course notebooks getTrades / resumen)
# ---------------------------------------------------------------------------

def _pairs_from_signals(signals):
    """Reduce a series of buy/sell/hold signals to a clean list of (date, signal)
    pairs, alternating buy / sell with the first buy before the first sell.
    """
    s = pd.Series(signals)
    s = s[s != 'hold']
    s = s[s != '']
    s = s.dropna()
    out = []
    for ts, val in s.items():
        if not out:
            if val == 'buy':
                out.append((ts, 'buy'))
        else:
            last_ts, last_val = out[-1]
            if last_val != val:
                out.append((ts, val))
    return out


def get_trades(actions, tipo='long', cost=0.0):
    """Build a trade table from a sequence of actions (Series with values in
    {'buy','sell','hold'}). Returns DataFrame with buy/sell dates and
    per-trade return.

    From course notebook getTrades().
    """
    pairs = _pairs_from_signals(actions)
    rows = []
    if tipo == 'long':
        buys = [p for p in pairs if p[1] == 'buy']
        sells = [p for p in pairs if p[1] == 'sell']
        for (b_date, _), (s_date, _) in zip(buys, sells):
            pass
        for i in range(min(len(buys), len(sells))):
            b_date, _ = buys[i]
            s_date, _ = sells[i]
            rows.append({
                'buy_date': b_date,
                'sell_date': s_date,
                'days': (s_date - b_date).days if hasattr(s_date - b_date, 'days') else int(s_date - b_date),
            })
    if not rows:
        return pd.DataFrame(columns=['buy_date', 'sell_date', 'days', 'buy_px', 'sell_px', 'return', 'result', 'cum_return'])
    df = pd.DataFrame(rows)
    return df


def resumen_trades(df_trades, prices_at):
    """Compute per-trade returns and a summary table from a trades DataFrame.

    prices_at: dict {date -> price} used to look up buy and sell prices.
    """
    if len(df_trades) == 0:
        return pd.DataFrame(), {'return': 0, 'days_in': 0, 'tea': 0}
    df = df_trades.copy()
    df['buy_px'] = df['buy_date'].map(prices_at)
    df['sell_px'] = df['sell_date'].map(prices_at)
    df['return'] = (df['sell_px'] / df['buy_px']) - 1
    df['result'] = np.where(df['return'] > 0, 'winner', 'loser')
    df['cum_return'] = (1 + df['return']).cumprod()

    counts = df.groupby('result').size()
    means = df.groupby('result')['return'].mean()
    sum_days = df.groupby('result')['days'].sum()
    mean_days = df.groupby('result')['days'].mean()
    summary = pd.concat([counts, means, sum_days, mean_days], axis=1)
    summary.columns = ['count', 'mean_return', 'total_days', 'mean_days']

    total_return = float(df['cum_return'].iloc[-1] - 1)
    t_win = summary['total_days'].get('winner', 0)
    t_loss = summary['total_days'].get('loser', 0)
    days_in = int(t_win + t_loss)
    if days_in > 0:
        tea = (1 + total_return) ** (365 / days_in) - 1
    else:
        tea = 0.0
    metrics = {'return': total_return, 'days_in': days_in, 'tea': tea}
    return summary, metrics


# ---------------------------------------------------------------------------
# Built-in strategies
# ---------------------------------------------------------------------------

def strategy_sma_crossover(close, fast=50, slow=200, **kwargs):
    """Long when SMA(fast) > SMA(slow), out otherwise.

    Returns Series of {'buy','sell','hold'}.
    """
    p = pd.Series(np.asarray(close, dtype=float))
    sma_fast = p.rolling(fast).mean()
    sma_slow = p.rolling(slow).mean()
    state = (sma_fast > sma_slow).astype(int)
    out = pd.Series('hold', index=p.index)
    prev = state.shift(1)
    out[(prev == 0) & (state == 1)] = 'buy'
    out[(prev == 1) & (state == 0)] = 'sell'
    # Check if state was already 1 when both MAs first had data
    both_valid = sma_fast.notna() & sma_slow.notna()
    first_valid_idx = both_valid.idxmax() if both_valid.any() else None
    if first_valid_idx is not None and state.loc[first_valid_idx] == 1:
        out.iloc[0] = 'buy'
    return out


def strategy_rsi_meanrev(close, n=14, low=30, high=70, **kwargs):
    """Buy when RSI crosses above low (recovery from oversold), sell when
    RSI crosses below high (overbought)."""
    p = pd.Series(np.asarray(close, dtype=float))
    diff = p.diff()
    win = diff.where(diff > 0, 0.0)
    loss = (-diff).where(diff < 0, 0.0)
    ema_w = win.ewm(alpha=1 / n, adjust=False).mean()
    ema_l = loss.ewm(alpha=1 / n, adjust=False).mean()
    rs = ema_w / ema_l
    rsi = 100 - 100 / (1 + rs)
    out = pd.Series('hold', index=p.index)
    prev = rsi.shift(1)
    out[(prev <= low) & (rsi > low)] = 'buy'
    out[(prev >= high) & (rsi < high)] = 'sell'
    return out


def strategy_rsi_cross(close, fast=10, slow=60, rsi_q=20, buy_cr=0, buy_rsi=65,
                        sell_cr=0, sell_rsi=35, **kwargs):
    """From course notebook addSignal(). Long when SMA(fast)/SMA(slow) - 1 > buy_cr
    AND RSI > buy_rsi. Out when conditions fail symmetrically.
    """
    p = pd.Series(np.asarray(close, dtype=float))
    sma_f = p.rolling(fast).mean()
    sma_s = p.rolling(slow).mean()
    cruce = (sma_f / sma_s - 1) * 100
    diff = p.diff()
    win = diff.where(diff > 0, 0.0)
    loss = (-diff).where(diff < 0, 0.0)
    ema_w = win.ewm(alpha=1 / rsi_q, adjust=False).mean()
    ema_l = loss.ewm(alpha=1 / rsi_q, adjust=False).mean()
    rs = ema_w / ema_l
    rsi = 100 - 100 / (1 + rs)
    out = pd.Series('hold', index=p.index)
    out[(cruce > buy_cr) & (rsi > buy_rsi)] = 'buy'
    out[(cruce < sell_cr) & (rsi < sell_rsi)] = 'sell'
    return out


def strategy_bbands_contrarian(close, n=20, k=2, **kwargs):
    """Buy when Close < lower Bollinger Band, sell when Close > SMA(n)."""
    p = pd.Series(np.asarray(close, dtype=float))
    mid = p.rolling(n).mean()
    sd = p.rolling(n).std(ddof=0)
    lower = mid - k * sd
    out = pd.Series('hold', index=p.index)
    out[p < lower] = 'buy'
    out[p > mid] = 'sell'
    return out


def strategy_momentum(close, lookback=252, threshold=0.0, **kwargs):
    """Buy if rolling 12-month return > threshold, sell otherwise."""
    p = pd.Series(np.asarray(close, dtype=float))
    ret = p / p.shift(lookback) - 1
    out = pd.Series('hold', index=p.index)
    out[ret > threshold] = 'buy'
    out[ret <= threshold] = 'sell'
    return out


def strategy_macd_crossover(close, fast=12, slow=26, signal=9, **kwargs):
    """Long when MACD line crosses above signal, out when crosses below."""
    p = pd.Series(np.asarray(close, dtype=float))
    e_fast = p.ewm(span=fast, adjust=False).mean()
    e_slow = p.ewm(span=slow, adjust=False).mean()
    macd_line = e_fast - e_slow
    sig = macd_line.ewm(span=signal, adjust=False).mean()
    out = pd.Series('hold', index=p.index)
    prev_diff = (macd_line - sig).shift(1)
    cur_diff = macd_line - sig
    out[(prev_diff <= 0) & (cur_diff > 0)] = 'buy'
    out[(prev_diff >= 0) & (cur_diff < 0)] = 'sell'
    return out


def strategy_adx_trend(high, low, close, n=14, threshold=25, **kwargs):
    """Buy when ADX > threshold and +DI > -DI. Sell when ADX drops below threshold
    or +DI < -DI."""
    try:
        from .indicators import _adx_components
    except (ImportError, ValueError):
        from indicators import _adx_components
    pdi, mdi, adx_v = _adx_components(high, low, close, n)
    out = pd.Series('hold', index=pd.Series(close).index)
    out[(adx_v > threshold) & (pdi > mdi)] = 'buy'
    out[(adx_v < threshold) | (pdi < mdi)] = 'sell'
    return out


def strategy_growth_momentum_combo(close, **kwargs):
    """Combined Growth + Momentum strategy from course slide 26-27.

    Simplified: take a slow trend filter (SMA 200) plus a momentum confirmation
    (return over last 6 months > 0). Long when both conditions are met.
    """
    p = pd.Series(np.asarray(close, dtype=float))
    sma200 = p.rolling(200).mean()
    ret6 = p / p.shift(126) - 1
    long = (p > sma200) & (ret6 > 0)
    out = pd.Series('hold', index=p.index)
    prev = long.shift(1).fillna(False)
    out[(~prev) & long] = 'buy'
    out[prev & (~long)] = 'sell'
    return out


STRATEGY_REGISTRY = {
    'sma_crossover': (strategy_sma_crossover, ['close']),
    'rsi_meanrev': (strategy_rsi_meanrev, ['close']),
    'rsi_cross': (strategy_rsi_cross, ['close']),
    'bbands_contrarian': (strategy_bbands_contrarian, ['close']),
    'momentum': (strategy_momentum, ['close']),
    'macd_crossover': (strategy_macd_crossover, ['close']),
    'adx_trend': (strategy_adx_trend, ['high', 'low', 'close']),
    'growth_momentum_combo': (strategy_growth_momentum_combo, ['close']),
}


# ---------------------------------------------------------------------------
# Event-driven backtest engine
# ---------------------------------------------------------------------------

class BacktestEngine:
    """Bar-by-bar event-driven backtest engine.

    Usage:
        eng = BacktestEngine(initial_capital=1.0, commission=0.0, slippage=0.0)
        eng.load_data(df_ohlcv)
        result = eng.run(strategy='sma_crossover', strategy_params={'fast': 50, 'slow': 200})
        print(result['trades'])
        print(result['metrics'])
    """

    def __init__(self, initial_capital=1.0, commission=0.0, slippage=0.0, mode='long'):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.mode = mode
        self.data = None
        self.signals = None
        self.trades = None
        self.strategy_returns = None
        self.metrics = None
        self.summary = None

    def load_data(self, df_ohlcv):
        """df_ohlcv must have at minimum a 'Close' column and a DatetimeIndex."""
        if not isinstance(df_ohlcv, pd.DataFrame):
            raise TypeError("df_ohlcv must be a DataFrame")
        if 'Close' not in df_ohlcv.columns:
            if 'close' in df_ohlcv.columns:
                df_ohlcv = df_ohlcv.rename(columns={'close': 'Close'})
            else:
                raise ValueError("df_ohlcv must contain a 'Close' column")
        self.data = df_ohlcv.sort_index()
        return self

    def _generate_signals(self, strategy, strategy_params):
        fn, required_cols = STRATEGY_REGISTRY[strategy]
        kwargs = {col: self.data[col].squeeze() if col in self.data.columns else self.data['Close'].squeeze()
                  for col in required_cols}
        kwargs.update(strategy_params)
        sig = fn(**kwargs)
        # Strategy functions create Series with RangeIndex from np arrays.
        # Force the correct index so reindex works.
        sig = pd.Series(sig.values, index=self.data.index).fillna('hold')
        if self.mode == 'long':
            sig = sig.where(sig.isin(['buy', 'sell', 'hold']), 'hold')
        return sig

    def run(self, strategy='sma_crossover', strategy_params=None):
        """Run the backtest. Returns dict with 'trades', 'summary', 'metrics',
        'strategy_returns', 'signals'."""
        if self.data is None:
            raise RuntimeError("Call load_data() first")
        if strategy not in STRATEGY_REGISTRY:
            raise ValueError(f"Unknown strategy '{strategy}'. Available: {list(STRATEGY_REGISTRY)}")
        if strategy_params is None:
            strategy_params = {}
        self.signals = self._generate_signals(strategy, strategy_params)
        self._execute()
        self._compute_metrics()
        return {
            'signals': self.signals,
            'trades': self.trades,
            'summary': self.summary,
            'metrics': self.metrics,
            'strategy_returns': self.strategy_returns,
        }

    def _execute(self):
        """Event-driven loop: simulate holding state and build trade list."""
        n = len(self.data)
        close = self.data['Close'].values
        sig = self.signals.values
        positions = np.zeros(n)
        in_pos = self.mode == 'long' and sig[0] == 'buy' if n > 0 else False
        buys = []
        sells = []
        if in_pos:
            positions[0] = 1
            buys.append((self.data.index[0], close[0] * (1 + self.slippage)))
        ret = np.zeros(n)
        for i in range(1, n):
            signal = sig[i - 1]  # shift: use prior bar signal
            if not in_pos and signal == 'buy':
                in_pos = True
                buy_px = close[i] * (1 + self.slippage)
                positions[i] = 1
                ret[i] = (close[i] / (close[i - 1] if i > 0 else close[i])) - 1 - self.commission
                buys.append((self.data.index[i], buy_px))
            elif in_pos and signal == 'sell':
                sell_px = close[i] * (1 - self.slippage)
                in_pos = False
                ret[i] = -self.commission
                sells.append((self.data.index[i], sell_px))
            elif in_pos:
                positions[i] = 1
                ret[i] = (close[i] / close[i - 1]) - 1
        self.positions = positions
        self.strategy_returns = pd.Series(ret, index=self.data.index)
        rows = []
        for j in range(min(len(buys), len(sells))):
            b_date, b_px = buys[j]
            s_date, s_px = sells[j]
            rows.append({
                'buy_date': b_date,
                'sell_date': s_date,
                'buy_px': b_px,
                'sell_px': s_px,
                'days': (s_date - b_date).days,
                'return': (s_px / b_px) - 1 - 2 * self.commission,
            })
        self.trades = pd.DataFrame(rows)
        if len(self.trades) > 0:
            self.trades['result'] = np.where(self.trades['return'] > 0, 'winner', 'loser')
            self.trades['cum_return'] = (1 + self.trades['return']).cumprod()

    def _compute_metrics(self):
        try:
            from .ratios import (
                cagr, sharpe_ratio, max_drawdown, recovery_factor, annualized_vol,
                skewness, kurtosis, ulcer_index, kelly_fraction, log_returns,
                r_squared, var_empirical, var_normal, var_johnsonsu, cvar_empirical,
                cvar_normal, cvar_johnsonsu, payoff_ratio, profit_factor,
                win_loss_ratio, rachev_a, rachev_b, rachev_c, common_sense_ratio,
                outlier_win_ratio, outlier_loss_ratio, days_in_market_pct,
                risk_of_ruin_normal, risk_of_ruin_empirical, linearity_coefficient,
            )
        except (ImportError, ValueError):
            from ratios import (
                cagr, sharpe_ratio, max_drawdown, recovery_factor, annualized_vol,
                skewness, kurtosis, ulcer_index, kelly_fraction, log_returns,
                r_squared, var_empirical, var_normal, var_johnsonsu, cvar_empirical,
                cvar_normal, cvar_johnsonsu, payoff_ratio, profit_factor,
                win_loss_ratio, rachev_a, rachev_b, rachev_c, common_sense_ratio,
                outlier_win_ratio, outlier_loss_ratio, days_in_market_pct,
                risk_of_ruin_normal, risk_of_ruin_empirical, linearity_coefficient,
            )
        p = self.data['Close'].values
        r = self.strategy_returns.values
        # Strategy equity curve (start at 1)
        strat_equity = (1 + np.nan_to_num(r)).cumprod()
        lr = log_returns(p)
        years = max(1e-9, (len(p) - 1) / 252)
        cum = float((1 + r[1:]).prod() - 1) if len(r) > 1 else 0.0
        days_in = int((self.strategy_returns != 0).sum())
        self.metrics = {
            'cagr': cagr(cum, years),
            'annualized_vol': annualized_vol(r),
            'sharpe_ratio': sharpe_ratio(r),
            'max_drawdown': max_drawdown(strat_equity),
            'recovery_factor': recovery_factor(strat_equity),
            'ulcer_index': ulcer_index(strat_equity),
            'linearity_coefficient': linearity_coefficient(strat_equity),
            'skewness': skewness(r),
            'kurtosis': kurtosis(r),
            'kelly_fraction': kelly_fraction(lr),
            'var_empirical_95': var_empirical(r, alpha=0.05),
            'var_normal_95': var_normal(r, alpha=0.05),
            'var_johnsonsu_95': var_johnsonsu(r, alpha=0.05),
            'cvar_empirical_95': cvar_empirical(r, alpha=0.05),
            'cvar_normal_95': cvar_normal(r, alpha=0.05),
            'cvar_johnsonsu_95': cvar_johnsonsu(r, alpha=0.05),
            'payoff_ratio': payoff_ratio(lr),
            'profit_factor': profit_factor(lr),
            'win_loss_ratio': win_loss_ratio(lr),
            'rachev_a': rachev_a(lr),
            'rachev_b': rachev_b(lr),
            'rachev_c': rachev_c(lr),
            'common_sense_ratio': common_sense_ratio(lr),
            'outlier_win_ratio': outlier_win_ratio(lr),
            'outlier_loss_ratio': outlier_loss_ratio(lr),
            'days_in_market_pct': days_in_market_pct(r),
            'risk_of_ruin_normal': risk_of_ruin_normal(r),
            'risk_of_ruin_empirical': risk_of_ruin_empirical(r),
            'cumulative_return': cum,
            'days_in': days_in,
            'years': years,
        }
        if len(self.trades) > 0:
            try:
                from .ratios import tea
            except (ImportError, ValueError):
                from ratios import tea
            self.metrics['tea'] = tea(cum, max(1, days_in))
        else:
            self.metrics['tea'] = 0.0
        if len(self.trades) > 0:
            counts = self.trades.groupby('result').size()
            means = self.trades.groupby('result')['return'].mean()
            sum_days = self.trades.groupby('result')['days'].sum()
            mean_days = self.trades.groupby('result')['days'].mean()
            self.summary = pd.concat([counts, means, sum_days, mean_days], axis=1)
            self.summary.columns = ['count', 'mean_return', 'total_days', 'mean_days']
        else:
            self.summary = pd.DataFrame()
