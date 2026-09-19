"""
Technical indicators organized in 10 classes, following the course material
taxonomy (slides 8-22).

Class 1a: Trend-Following on price (tardíos)
Class 1b: Oscillators on price
Class 1c: Contrarians (saturación)
Class 2:  Flow (volume, derivatives)
Class 3:  Combined (cross-weighting + codomain bounding)
Class 4:  Discrete counts (Poisson, Binomial)
Class 5:  Seasonality (Fourier, STL)
Class 6:  Statistical (vol, skew, kurt, distribution fitting)
Class 7:  Referential (alpha, beta, correlations)
Class 8:  Fundamental ratios - see fundamental_ratios.py
Class 9:  Sentiment - see references/OTHER_FEATURES.md
Class 10: Exogenous - see references/OTHER_FEATURES.md

All functions take numpy arrays or pandas Series and return the same shape
(or shorter when windowing is applied; leading NaN are kept for alignment).

Skill part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Class 1a: Trend-Following
# ---------------------------------------------------------------------------

def sma(close, n=20):
    """Simple Moving Average."""
    return pd.Series(np.asarray(close, dtype=float)).rolling(n).mean().to_numpy()


def ema(close, n=20):
    """Exponential Moving Average (span=n)."""
    return pd.Series(np.asarray(close, dtype=float)).ewm(span=n, adjust=False).mean().to_numpy()


def wma(close, n=20):
    """Weighted Moving Average (linear weights, most recent heaviest)."""
    p = np.asarray(close, dtype=float)
    weights = np.arange(1, n + 1)
    s = pd.Series(p)
    out = s.rolling(n).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    return out.to_numpy()


def dema(close, n=20):
    """Double EMA: 2*EMA(n) - EMA(EMA(n))."""
    p = np.asarray(close, dtype=float)
    e1 = ema(p, n)
    e2 = ema(e1, n)
    return 2 * e1 - e2


def trima(close, n=20):
    """Triangular MA: SMA of SMA."""
    p = np.asarray(close, dtype=float)
    half = n // 2
    return sma(sma(p, n), half + 1)


def tema(close, n=20):
    """Triple EMA: 3*EMA1 - 3*EMA2 + EMA3."""
    p = np.asarray(close, dtype=float)
    e1 = ema(p, n)
    e2 = ema(e1, n)
    e3 = ema(e2, n)
    return 3 * e1 - 3 * e2 + e3


def macd(close, fast=12, slow=26, signal=9):
    """MACD line, signal, histogram. Returns 3 arrays."""
    p = np.asarray(close, dtype=float)
    e_fast = ema(p, fast)
    e_slow = ema(p, slow)
    macd_line = e_fast - e_slow
    sig = ema(macd_line, signal)
    hist = macd_line - sig
    return macd_line, sig, hist


def _adx_components(high, low, close, n=14):
    """Internal: returns +DI, -DI, ADX."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    c = pd.Series(np.asarray(close, dtype=float))
    up = h.diff()
    dn = -l.diff()
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = pd.concat([
        h - l,
        (h - c.shift()).abs(),
        (l - c.shift()).abs()
    ], axis=1).max(axis=1)
    atr_n = tr.ewm(alpha=1 / n, adjust=False).mean()
    plus_di = 100 * pd.Series(plus_dm).ewm(alpha=1 / n, adjust=False).mean() / atr_n
    minus_di = 100 * pd.Series(minus_dm).ewm(alpha=1 / n, adjust=False).mean() / atr_n
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.ewm(alpha=1 / n, adjust=False).mean()
    return plus_di.to_numpy(), minus_di.to_numpy(), adx.to_numpy()


def adx(high, low, close, n=14):
    """Average Directional Movement Index."""
    return _adx_components(high, low, close, n)[2]


def dx(high, low, close, n=14):
    """Directional Movement Index (unsmoothed)."""
    plus_di, minus_di, _ = _adx_components(high, low, close, n)
    dx_val = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
    return dx_val


def adxr(high, low, close, n=14):
    """ADX Rating: average of current ADX and ADX n periods ago."""
    a = adx(high, low, close, n)
    return pd.Series(a).rolling(n).mean().to_numpy()


def plus_di(high, low, close, n=14):
    return _adx_components(high, low, close, n)[0]


def minus_di(high, low, close, n=14):
    return _adx_components(high, low, close, n)[1]


def plus_dm(high, low, n=14):
    """Raw +DM (Directional Movement)."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    up = h.diff()
    dn = -l.diff()
    return np.where((up > dn) & (up > 0), up, 0.0)


def minus_dm(high, low, n=14):
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    up = h.diff()
    dn = -l.diff()
    return np.where((dn > up) & (dn > 0), dn, 0.0)


def sar(high, low, acceleration=0.02, max_acc=0.2):
    """Parabolic SAR. Returns array same length as high/low."""
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    n = len(h)
    if n < 2:
        return np.full(n, np.nan)
    out = np.full(n, np.nan)
    af = acceleration
    is_long = True
    ep = l[0]
    sar_val = h[0]
    for i in range(1, n):
        sar_val = sar_val + af * (ep - sar_val)
        if is_long:
            sar_val = min(sar_val, h[i - 1], l[i - 1]) if i > 1 else sar_val
            if l[i] < sar_val:
                is_long = False
                sar_val = ep
                ep = l[i]
                af = acceleration
            else:
                if h[i] > ep:
                    ep = h[i]
                    af = min(af + acceleration, max_acc)
        else:
            sar_val = max(sar_val, h[i - 1], l[i - 1]) if i > 1 else sar_val
            if h[i] > sar_val:
                is_long = True
                sar_val = ep
                ep = h[i]
                af = acceleration
            else:
                if l[i] < ep:
                    ep = l[i]
                    af = min(af + acceleration, max_acc)
        out[i] = sar_val
    return out


def mom(close, n=10):
    """Momentum: P_t - P_{t-n}."""
    p = np.asarray(close, dtype=float)
    out = np.full_like(p, np.nan)
    out[n:] = p[n:] - p[:-n]
    return out


def midpoint(high, low, n=14):
    """Midpoint over OHLC: (max(H) + min(L)) / 2 over window."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    return ((h.rolling(n).max() + l.rolling(n).min()) / 2).to_numpy()


def midprice(high, low, n=14):
    """Midprice: (max(High) + min(Low)) / 2 over window."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    return ((h.rolling(n).max() + l.rolling(n).min()) / 2).to_numpy()


# ---------------------------------------------------------------------------
# Class 1b: Oscillators
# ---------------------------------------------------------------------------

def willr(high, low, close, n=14):
    """Williams %R: -100 * (max_n - C) / (max_n - min_n)."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    c = pd.Series(np.asarray(close, dtype=float))
    max_n = h.rolling(n).max()
    min_n = l.rolling(n).min()
    return (-100 * (max_n - c) / (max_n - min_n)).to_numpy()


def apo(close, fast=12, slow=26):
    """Absolute Price Oscillator: EMA(fast) - EMA(slow)."""
    p = np.asarray(close, dtype=float)
    return ema(p, fast) - ema(p, slow)


def ppo(close, fast=12, slow=26):
    """Percentage Price Oscillator: 100 * (EMA(fast) - EMA(slow)) / EMA(slow)."""
    p = np.asarray(close, dtype=float)
    e_fast = ema(p, fast)
    e_slow = ema(p, slow)
    return 100 * (e_fast - e_slow) / e_slow


def stoch(high, low, close, k_n=14, d_n=3):
    """Stochastic oscillator: K%, D%. Returns 2 arrays."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    c = pd.Series(np.asarray(close, dtype=float))
    max_n = h.rolling(k_n).max()
    min_n = l.rolling(k_n).min()
    k = 100 * (c - min_n) / (max_n - min_n)
    d = k.rolling(d_n).mean()
    return k.to_numpy(), d.to_numpy()


def stochf(high, low, close, k_n=14, d_n=3):
    """Fast stochastic (no smoothing on K)."""
    return stoch(high, low, close, k_n, d_n)


def rsi(close, n=14):
    """Relative Strength Index using Wilder's smoothing."""
    p = pd.Series(np.asarray(close, dtype=float))
    diff = p.diff()
    win = diff.where(diff > 0, 0.0)
    loss = -diff.where(diff < 0, 0.0)
    ema_win = win.ewm(alpha=1 / n, adjust=False).mean()
    ema_loss = loss.ewm(alpha=1 / n, adjust=False).mean()
    rs = ema_win / ema_loss
    return (100 - 100 / (1 + rs)).to_numpy()


def bop(open_, high, low, close, n=14):
    """Balance of Power: SMA((C - O) / (H - L))."""
    o = np.asarray(open_, dtype=float)
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    denom = h - l
    denom = np.where(denom == 0, np.nan, denom)
    return pd.Series((c - o) / denom).rolling(n).mean().to_numpy()


def cmo(close, n=14):
    """Chande Momentum Oscillator: 100 * (sum_up - sum_down) / (sum_up + sum_down)."""
    p = pd.Series(np.asarray(close, dtype=float))
    diff = p.diff()
    sum_up = diff.where(diff > 0, 0.0).rolling(n).sum()
    sum_dn = (-diff.where(diff < 0, 0.0)).rolling(n).sum()
    return (100 * (sum_up - sum_dn) / (sum_up + sum_dn)).to_numpy()


def roc(close, n=12):
    """Rate of Change: 100 * (P_t - P_{t-n}) / P_{t-n}."""
    p = np.asarray(close, dtype=float)
    out = np.full_like(p, np.nan)
    out[n:] = 100 * (p[n:] - p[:-n]) / p[:-n]
    return out


def mfi(high, low, close, volume, n=14):
    """Money Flow Index: volume-weighted RSI."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    c = pd.Series(np.asarray(close, dtype=float))
    v = pd.Series(np.asarray(volume, dtype=float))
    tp = (h + l + c) / 3
    mf = tp * v
    tp_diff = tp.diff()
    pos_mf = mf.where(tp_diff > 0, 0.0).rolling(n).sum()
    neg_mf = mf.where(tp_diff < 0, 0.0).rolling(n).sum()
    mr = pos_mf / neg_mf
    return (100 - 100 / (1 + mr)).to_numpy()


def trix(close, n=14):
    """TRIX: 1-period rate of change of triple EMA."""
    p = np.asarray(close, dtype=float)
    e1 = ema(p, n)
    e2 = ema(e1, n)
    e3 = ema(e2, n)
    out = np.full_like(e3, np.nan)
    out[1:] = 100 * (e3[1:] - e3[:-1]) / e3[:-1]
    return out


def ultosc(high, low, close, n1=7, n2=14, n3=28):
    """Ultimate Oscillator: weighted average of 3 stochastics."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    c = pd.Series(np.asarray(close, dtype=float))
    def _stoch(n):
        max_n = h.rolling(n).max()
        min_n = l.rolling(n).min()
        return (c - min_n) / (max_n - min_n)
    s1 = _stoch(n1).rolling(1).sum()
    s2 = _stoch(n2).rolling(1).sum()
    s3 = _stoch(n3).rolling(1).sum()
    return (100 * (4 * s1 + 2 * s2 + s3) / (4 + 2 + 1)).to_numpy()


# ---------------------------------------------------------------------------
# Class 1c: Contrarians
# ---------------------------------------------------------------------------

def cci(high, low, close, n=20):
    """Commodity Channel Index: (TP - SMA(TP)) / (0.015 * mean_deviation)."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    c = pd.Series(np.asarray(close, dtype=float))
    tp = (h + l + c) / 3
    sma_tp = tp.rolling(n).mean()
    md = tp.rolling(n).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    return ((tp - sma_tp) / (0.015 * md)).to_numpy()


def aroon(high, low, n=25):
    """Aroon Up and Down. Returns 2 arrays (up, down)."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    def _aroon(series):
        out = np.full(len(series), np.nan)
        for i in range(n - 1, len(series)):
            window = series.iloc[i - n + 1: i + 1]
            idx_max = window.values.argmax()
            out[i] = 100 * (n - 1 - (n - 1 - idx_max)) / n
        return out
    up = _aroon(h)
    dn = _aroon(l)
    return np.array(up), np.array(dn)


def aroonosc(high, low, n=25):
    """Aroon Oscillator: aroon_up - aroon_down."""
    up, dn = aroon(high, low, n)
    return up - dn


def bbands(close, n=20, k=2):
    """Bollinger Bands: SMA +/- k * std. Returns (upper, mid, lower)."""
    p = pd.Series(np.asarray(close, dtype=float))
    mid = p.rolling(n).mean()
    sd = p.rolling(n).std(ddof=0)
    return (mid + k * sd).to_numpy(), mid.to_numpy(), (mid - k * sd).to_numpy()


def trange(high, low, close):
    """True Range: max(H-L, |H-C_prev|, |L-C_prev|)."""
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    c = pd.Series(np.asarray(close, dtype=float))
    pc = c.shift()
    return pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1).to_numpy()


def atr(high, low, close, n=14):
    """Average True Range: Wilder-smoothed true range."""
    return pd.Series(trange(high, low, close)).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


# ---------------------------------------------------------------------------
# Class 2: Flow
# ---------------------------------------------------------------------------

def vwap(high, low, close, volume):
    """Volume-Weighted Average Price (cumulative from start)."""
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    v = np.asarray(volume, dtype=float)
    tp = (h + l + c) / 3
    cum_v = np.cumsum(v)
    cum_v = np.where(cum_v == 0, np.nan, cum_v)
    return np.cumsum(tp * v) / cum_v


def obv(close, volume):
    """On-Balance Volume: cumulative volume, signed by price direction."""
    p = pd.Series(np.asarray(close, dtype=float))
    v = np.asarray(volume, dtype=float)
    sign = np.sign(p.diff().fillna(0))
    return np.cumsum(sign * v)


def ad(high, low, close, volume):
    """Chaikin Accumulation/Distribution."""
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    v = np.asarray(volume, dtype=float)
    denom = h - l
    denom = np.where(denom == 0, np.nan, denom)
    mfm = ((c - l) - (h - c)) / denom
    mfv = mfm * v
    return np.cumsum(mfv)


def adosc(high, low, close, volume, fast=3, slow=10):
    """Chaikin A/D Oscillator: EMA(fast) - EMA(slow) of A/D."""
    a = ad(high, low, close, volume)
    return ema(a, fast) - ema(a, slow)


def put_call_ratio(put_volume, call_volume):
    """Put/Call ratio from options data."""
    if call_volume == 0:
        return np.nan
    return put_volume / call_volume


def funding_rate_zscore(funding_series, window=30):
    """Rolling z-score of funding rate (perpetual futures)."""
    s = pd.Series(np.asarray(funding_series, dtype=float))
    mu = s.rolling(window).mean()
    sd = s.rolling(window).std(ddof=0)
    return ((s - mu) / sd).to_numpy()


def open_interest_change(oi_series, period=1):
    """Period-over-period change in open interest."""
    s = pd.Series(np.asarray(oi_series, dtype=float))
    return s.diff(period).to_numpy()


# ---------------------------------------------------------------------------
# Class 3: Combined (cross-weighting + codomain bounding)
# ---------------------------------------------------------------------------

def cross_indicator(ind_a, ind_b, method='zscore_weight', window=20, factor=1.0):
    """Combine two indicators by weighting ind_a with the z-score of ind_b.

    Method 'zscore_weight':
        result = ind_a * (1 + factor * zscore_norm(ind_b, window))

    Example: an RSI strengthened by a high-volume signal.

    Both inputs are arrays. The output combines both signals.
    """
    a = np.asarray(ind_a, dtype=float)
    b = np.asarray(ind_b, dtype=float)
    if method != 'zscore_weight':
        raise ValueError("Only 'zscore_weight' is supported in this version")
    z = zscore_norm(b, window=window)
    return a * (1 + factor * z)


def range_bound(series, window):
    """Bound a series to [0, 1] using rolling min/max.

    CRITICAL: Uses a rolling window, NOT the global min/max. Using global
    statistics causes look-ahead bias / data leakage in backtesting.

    Example: convert unbounded MOM to [0,1] for cross-indicator comparison.
    """
    s = pd.Series(np.asarray(series, dtype=float))
    rmin = s.rolling(window).min()
    rmax = s.rolling(window).max()
    rng = (rmax - rmin).replace(0, np.nan)
    return ((s - rmin) / rng).to_numpy()


def zscore_norm(series, window):
    """Normalize a series to z-score using rolling mu/sigma.

    CRITICAL: Uses a rolling window, NOT the global statistics. Using global
    statistics causes look-ahead bias / data leakage in backtesting.
    """
    s = pd.Series(np.asarray(series, dtype=float))
    mu = s.rolling(window).mean()
    sd = s.rolling(window).std(ddof=0)
    sd = sd.replace(0, np.nan)
    return ((s - mu) / sd).to_numpy()


# ---------------------------------------------------------------------------
# Class 4: Discrete Counts
# ---------------------------------------------------------------------------

def poisson_rate(event_count, period):
    """Estimate rate of rare events per unit time.

    Example: number of flash crashes in N days. Used to size black-swan
    reserves or set margin buffers.
    """
    if period <= 0:
        return 0.0
    return event_count / period


def binomial_ratio(successes, trials):
    """Estimate p of discrete events. Example: fraction of up days.

    Unbiased estimator: p_hat = (successes + 0) / trials. For sample-size
    correction see unbiased_estimator().
    """
    if trials <= 0:
        return 0.0
    return successes / trials


def unbiased_estimator(p_hat, n):
    """Bias correction for small samples under binomial:
    p_unbiased = (successes + 1) / (n + 2).
    Use when n < 30 to avoid extreme p_hat = 0 or 1.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    successes = p_hat * n
    return (successes + 1) / (n + 2)


def event_probability(rate, threshold, k=None):
    """P(X >= threshold) under Poisson with given rate. Threshold integer.

    If k is given, returns P(X == k); otherwise P(X >= threshold).
    """
    if rate <= 0:
        return 0.0
    if k is not None:
        return float(stats.poisson.pmf(int(k), rate))
    return float(1 - stats.poisson.cdf(int(threshold) - 1, rate))


# ---------------------------------------------------------------------------
# Class 5: Seasonality
# ---------------------------------------------------------------------------

def seasonal_profile(series, period='W'):
    """Average value of the series for each sub-period (weekday, month, etc.).

    Returns a Series indexed by the sub-period.
    """
    s = pd.Series(np.asarray(series, dtype=float))
    if period == 'W':
        return s.groupby(s.index.dayofweek).mean()
    if period == 'M':
        return s.groupby(s.index.month).mean()
    if period == 'H':
        return s.groupby(s.index.hour).mean()
    raise ValueError("period must be 'W' (weekday) | 'M' (month) | 'H' (hour)")


def fourier_terms(T, n_terms):
    """Generate sin/cos Fourier features for a period T.

    Returns DataFrame with columns cos_1..cos_n, sin_1..sin_n, each of length T.
    Use as exogenous features for ML models or seasonal feature engineering.
    """
    t = np.arange(T)
    cols = {}
    for k in range(1, n_terms + 1):
        cols[f'cos_{k}'] = np.cos(2 * np.pi * k * t / T)
        cols[f'sin_{k}'] = np.sin(2 * np.pi * k * t / T)
    return pd.DataFrame(cols)


def stl_decompose(series, period):
    """STL decomposition (trend + seasonal + residual) using statsmodels.

    Falls back to classical decomposition if statsmodels.tsa unavailable.
    """
    from statsmodels.tsa.seasonal import STL
    s = pd.Series(np.asarray(series, dtype=float)).dropna()
    stl = STL(s, period=period, robust=True).fit()
    return stl.trend, stl.seasonal, stl.resid


# ---------------------------------------------------------------------------
# Class 6: Statistical
# ---------------------------------------------------------------------------

def rolling_vol(returns, window=20, periods=252):
    r = pd.Series(np.asarray(returns, dtype=float))
    return (r.rolling(window).std(ddof=1) * np.sqrt(periods)).to_numpy()


def rolling_skew(returns, window=20):
    r = pd.Series(np.asarray(returns, dtype=float))
    return r.rolling(window).skew().to_numpy()


def rolling_kurt(returns, window=20):
    r = pd.Series(np.asarray(returns, dtype=float))
    return r.rolling(window).kurt().to_numpy()


def tails_ratio(returns, alpha=0.05):
    """Ratio between the upper and lower alpha quantiles.

    Values > 1 indicate right-skewed tails; values < 1 left-skewed.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return np.nan
    upper = np.quantile(r, 1 - alpha)
    lower = abs(np.quantile(r, alpha))
    if lower == 0:
        return np.nan
    return float(upper / lower)


def zscore(series, window=None):
    """Z-score normalization. If window is None uses global mu/sigma (analysis only).

    For backtesting, ALWAYS pass a window. The global version can be used
    to inspect a series but introduces look-ahead bias if used for
    feature engineering.
    """
    s = pd.Series(np.asarray(series, dtype=float))
    if window is None:
        mu = s.mean()
        sd = s.std(ddof=0)
    else:
        mu = s.rolling(window).mean()
        sd = s.rolling(window).std(ddof=0)
    sd = sd.replace(0, np.nan)
    return ((s - mu) / sd).to_numpy()


def fit_distribution(returns, dist_name):
    """Fit a single continuous distribution. Returns (params, ks_stat, ks_pvalue)."""
    from . import distributions
    return distributions.fit(returns, dist_name)


def best_fit_dist(returns):
    """Try Normal, t, NCt, Laplace, JohnsonSU. Return the best by KS."""
    from . import distributions
    return distributions.best_fit(returns)


# ---------------------------------------------------------------------------
# Class 7: Referential
# ---------------------------------------------------------------------------

def alpha(strategy_returns, benchmark_returns, rf=0.0, periods=252):
    """Jensen's alpha: actual strategy return minus expected return from beta.

    alpha = (R_strategy - rf) - beta * (R_benchmark - rf)
    """
    s = np.asarray(strategy_returns, dtype=float)
    b = np.asarray(benchmark_returns, dtype=float)
    mask = ~np.isnan(s) & ~np.isnan(b)
    s, b = s[mask], b[mask]
    if len(s) < 2:
        return np.nan
    s_ann = s.mean() * periods
    b_ann = b.mean() * periods
    cov = np.cov(s, b, ddof=1)[0, 1]
    var_b = np.var(b, ddof=1)
    if var_b == 0:
        return np.nan
    beta = cov / var_b
    return float(s_ann - (rf + beta * (b_ann - rf)))


def beta(strategy_returns, benchmark_returns):
    s = np.asarray(strategy_returns, dtype=float)
    b = np.asarray(benchmark_returns, dtype=float)
    mask = ~np.isnan(s) & ~np.isnan(b)
    s, b = s[mask], b[mask]
    if len(s) < 2:
        return np.nan
    var_b = np.var(b, ddof=1)
    if var_b == 0:
        return np.nan
    cov = np.cov(s, b, ddof=1)[0, 1]
    return float(cov / var_b)


def rolling_corr(a, b, window, method='pearson'):
    s = pd.Series(np.asarray(a, dtype=float))
    t = pd.Series(np.asarray(b, dtype=float))
    return s.rolling(window).corr(t, pairwise=False, method=method).to_numpy()


def cross_asset_matrix(returns_df, method='pearson'):
    """Correlation matrix across multiple asset return series.

    returns_df: DataFrame with one column per asset.
    """
    return returns_df.corr(method=method)


def cross_timeframe_corr(asset_a, asset_b, periods=(21, 63, 252)):
    """Correlation at different horizons.

    Returns dict {period: corr}.
    """
    out = {}
    for p in periods:
        a_r = pd.Series(np.asarray(asset_a, dtype=float)).rolling(p).sum()
        b_r = pd.Series(np.asarray(asset_b, dtype=float)).rolling(p).sum()
        out[p] = float(a_r.corr(b_r))
    return out
