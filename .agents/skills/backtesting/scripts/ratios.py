"""
Risk and performance ratios for backtesting.

Flat functions, vectorized with numpy, accepting 1-D arrays (pandas Series
or numpy.ndarray) and returning scalars or arrays. No classes, no objects.

Returns types convention:
  - linear returns: pct_change of prices
  - log returns:    ln(p / p.shift())

The course material (slides 77-86) specifies that trade statistics
(payoff ratio, profit factor, win/loss ratio, Rachev A/B/C, OWR/OLR, CSR)
MUST be computed on log returns. Use linear returns for: VaR, cVaR,
volatility, R-squared, beta, tracking error.

Source: course material slides 45-86, course notebooks in temp/.
Skill part of the Gauss314 Skills Repository: https://github.com/gauss314/skills
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Base returns
# ---------------------------------------------------------------------------

def linear_returns(prices):
    """Linear returns: r_t = P_t / P_{t-1} - 1."""
    p = np.asarray(prices, dtype=float)
    return pd.Series(p).pct_change().to_numpy()


def log_returns(prices):
    """Log returns: r_t = ln(P_t / P_{t-1})."""
    p = np.asarray(prices, dtype=float)
    return np.log(p / np.concatenate(([np.nan], p[:-1])))


def cumulative_returns(lin):
    """Cumulative return: cumprod(1 + r) - 1.

    out[i] is the cumulative return after observing returns r[0]..r[i].
    out[0] includes r[0], out[-1] includes all returns.
    """
    r = np.asarray(lin, dtype=float)
    if len(r) == 0:
        return np.array([])
    return np.cumprod(1.0 + r) - 1.0


def cumulative_log_returns(log_r):
    """Cumulative return from log returns: exp(sum) - 1."""
    r = np.asarray(log_r, dtype=float)
    out = np.empty_like(r)
    out[0] = 0.0
    if len(r) > 1:
        out[1:] = np.exp(np.cumsum(r[1:])) - 1
    return out


def cagr(cumret, years):
    """Compound Annual Growth Rate: (1 + cumret) ** (1 / years) - 1."""
    if years <= 0:
        return np.nan
    return (1 + cumret) ** (1 / years) - 1


def tea(cumret, days_in_market):
    """Annual Equivalent Rate (Tasa Efectiva Anual): (1 + cumret) ** (365 / days) - 1.

    Used in course notebooks to annualize trade returns accounting for time
    actually spent in the market, not calendar days.
    """
    if days_in_market <= 0:
        return 0.0
    return (1 + cumret) ** (365 / days_in_market) - 1


# ---------------------------------------------------------------------------
# Distribution moments
# ---------------------------------------------------------------------------

def annualized_vol(returns, periods=252):
    """Annualized volatility: std(returns) * sqrt(periods)."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return 0.0
    return float(np.std(r, ddof=1) * np.sqrt(periods))


def skewness(returns):
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 3:
        return 0.0
    return float(stats.skew(r, bias=False))


def kurtosis(returns):
    """Excess kurtosis (Fisher), matching pandas .kurt()."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 4:
        return 0.0
    return float(stats.kurtosis(r, fisher=True, bias=False))


# ---------------------------------------------------------------------------
# Risk-adjusted return ratios (use linear returns)
# ---------------------------------------------------------------------------

def sharpe_ratio(returns, rf=0.0, periods=252, annualized=True):
    """Sharpe Ratio: (mean(r) * periods - rf) / (std(r) * sqrt(periods))."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return np.nan
    sd = np.std(r, ddof=1)
    if sd == 0:
        return np.nan
    if annualized:
        return (np.mean(r) * periods - rf) / (sd * np.sqrt(periods))
    return (np.mean(r) - rf) / sd


def sortino(returns, rf=0.0, periods=252, method='from_mean'):
    """Sortino Ratio. Two variants from course notebooks:

    method='from_mean'   : semi-deviation from mean of negative returns.
                            semi = sqrt(mean((r[ r < 0 ] - mean_neg) ** 2))
    method='from_zero'    : semi-deviation from zero, like empyrical/quantstats.
                            semi = sqrt(mean(r[ r < 0 ] ** 2))
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return np.nan
    neg = r[r < 0]
    if len(neg) == 0:
        return np.inf
    if method == 'from_mean':
        sd = np.sqrt(np.mean((neg - np.mean(neg)) ** 2))
    else:
        sd = np.sqrt(np.mean(neg ** 2))
    if sd == 0:
        return np.nan
    excess = np.mean(r) * periods - rf
    return excess / (sd * np.sqrt(periods))


def rolling_sharpe(prices, window=252, rf=0.0):
    """Rolling TTM Sharpe ratio. Returns Series."""
    p = np.asarray(prices, dtype=float)
    r = pd.Series(p).pct_change()
    roll_ret = r.rolling(window).mean() * window
    roll_std = r.rolling(window).std(ddof=1) * np.sqrt(window)
    return (roll_ret - rf) / roll_std


def information_ratio(strategy_returns, benchmark_returns):
    """Information ratio: mean(strategy - benchmark) / std(strategy - benchmark)."""
    s = np.asarray(strategy_returns, dtype=float)
    b = np.asarray(benchmark_returns, dtype=float)
    diff = s - b
    diff = diff[~np.isnan(diff)]
    if len(diff) < 2:
        return np.nan
    sd = np.std(diff, ddof=1)
    if sd == 0:
        return np.nan
    return float(np.mean(diff) / sd)


def tracking_error(strategy_returns, benchmark_returns, periods=252):
    """Tracking error: std(strategy - benchmark) * sqrt(periods)."""
    s = np.asarray(strategy_returns, dtype=float)
    b = np.asarray(benchmark_returns, dtype=float)
    diff = s - b
    diff = diff[~np.isnan(diff)]
    if len(diff) < 2:
        return 0.0
    return float(np.std(diff, ddof=1) * np.sqrt(periods))


# ---------------------------------------------------------------------------
# Drawdown ratios (use prices)
# ---------------------------------------------------------------------------

def max_drawdown(prices):
    """Max drawdown: (P / cummax(P) - 1).min(). Negative number."""
    p = np.asarray(prices, dtype=float)
    pk = np.maximum.accumulate(p)
    dd = p / pk - 1
    return float(np.min(dd))


def avg_drawdown(prices):
    """Average drawdown: mean(1 - P / cummax(P))."""
    p = np.asarray(prices, dtype=float)
    pk = np.maximum.accumulate(p)
    dd = 1 - p / pk
    return float(np.mean(dd))


def drawdown_durations(prices, top_n=10):
    """Top N longest drawdown durations in days. Returns array of timedeltas."""
    p = pd.Series(np.asarray(prices, dtype=float))
    is_ath = (p.cummax() == p)
    if is_ath.sum() < 2:
        return np.array([], dtype='timedelta64[ns]')
    ath_idx = p.index[is_ath]
    diffs = pd.Series(ath_idx).diff()
    return diffs.dropna().sort_values(ascending=False).head(top_n).values


def avg_drawdown_duration(prices, top_n=10):
    """Average duration of top N drawdowns, in days."""
    durs = drawdown_durations(prices, top_n)
    if len(durs) == 0:
        return 0
    return float(np.mean(durs).astype('timedelta64[D]').astype(int))


def ulcer_index(prices, period=252):
    """Ulcer Index: sqrt(EMA of (P - cummax(P)) / cummax(P) squared)."""
    p = pd.Series(np.asarray(prices, dtype=float))
    rsq = ((p - p.cummax()) / p.cummax()) ** 2
    rsq = rsq.ewm(span=period).mean()
    return float(np.sqrt(rsq.mean()))


def recovery_factor(prices):
    """Recovery Factor: cumulative return / |max drawdown|."""
    p = np.asarray(prices, dtype=float)
    r = p[1:] / p[:-1] - 1
    cum = (1 + r).prod() - 1
    dd = max_drawdown(p)
    if dd == 0:
        return np.nan
    return float(cum / abs(dd))


# ---------------------------------------------------------------------------
# Linearity and benchmark relations
# ---------------------------------------------------------------------------

def r_squared(strategy_returns, benchmark_returns):
    """R^2 = corr(strategy, benchmark) ** 2."""
    s = np.asarray(strategy_returns, dtype=float)
    b = np.asarray(benchmark_returns, dtype=float)
    mask = ~np.isnan(s) & ~np.isnan(b)
    s, b = s[mask], b[mask]
    if len(s) < 2:
        return np.nan
    return float(np.corrcoef(s, b)[0, 1] ** 2)


def linearity_coefficient(prices):
    """Bill Ackman's linearity coefficient: correlation of price series with
    a straight line from P0 with slope (P_last - P0) / N.

    Values close to 1 mean a near-linear (low-volatility) trajectory.
    """
    p = np.asarray(prices, dtype=float)
    p = p[~np.isnan(p)]
    n = len(p)
    if n < 2:
        return np.nan
    x = np.arange(1, n + 1)
    slope = (p[-1] - p[0]) / n
    L = p[0] + slope * x
    return float(np.corrcoef(p, L)[0, 1])


# ---------------------------------------------------------------------------
# Calmar
# ---------------------------------------------------------------------------

def calmar_ratio(cagr_val, max_dd):
    """Calmar = CAGR / |MaxDD|. Calmar degenerates to ~0.1 over 20+ years because
    CAGR converges to 5-7% and MaxDD floors at ~40% for equity. Use only for
    relative comparisons over same horizon."""
    if max_dd == 0:
        return np.nan
    return float(cagr_val / abs(max_dd))


# ---------------------------------------------------------------------------
# Kelly criterion (use LOG returns)
# ---------------------------------------------------------------------------

def kelly_fraction(log_returns):
    """Kelly fraction: p_win / avg_loss - p_loss / avg_win.

    From course notebook getKelly(). log_returns REQUIRED.
    Returns f (Kelly optimal bet size). f > 1 means leverage.
    """
    r = np.asarray(log_returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 1:
        return 0.0
    winners = r[r > 0]
    losers = r[r < 0]
    if len(winners) == 0 or len(losers) == 0:
        return 0.0
    p_win = len(winners) / len(r)
    p_loss = 1 - p_win
    win_m = winners.mean()
    loss_m = -losers.mean()
    if loss_m == 0 or win_m == 0:
        return 0.0
    return float(p_win / loss_m - p_loss / win_m)


# ---------------------------------------------------------------------------
# Risk of Ruin (use linear returns)
# ---------------------------------------------------------------------------

def risk_of_ruin_normal(returns, capital=1.0):
    """Risk of Ruin assuming normal distribution (closed-form).

    Formula from course material slide 65:
        r = sqrt(mu^2 + sigma^2)
        RoR = (2 / (1 + mu/r) - 1) ** (capital / r)
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return 0.0
    mu = np.mean(r)
    sigma = np.std(r, ddof=1)
    if mu == 0 and sigma == 0:
        return 0.0
    rd = np.sqrt(mu ** 2 + sigma ** 2)
    if rd == 0:
        return 0.0
    base = 2 / (1 + mu / rd) - 1
    if base <= 0 or np.isnan(base):
        return 0.0
    return float(base ** (capital / rd))


def risk_of_ruin_empirical(returns, capital=1.0):
    """Risk of Ruin without distribution assumption (empirical).

    From course notebook RoRemp(). Uses Pw, Pl, avg_w, avg_l.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return 0.0
    wins = r[r > 0]
    losses = r[r < 0]
    if len(wins) == 0 or len(losses) == 0:
        return 0.0
    avg_w = wins.mean()
    avg_l = abs(losses.mean())
    Pw = len(wins) / len(r)
    Pl = len(losses) / len(r)
    inner = Pw * avg_w ** 2 - Pl * avg_l ** 2
    if inner <= 0:
        return 0.0
    A = np.sqrt(inner)
    Z = Pw * avg_w - Pl * avg_l
    P = 0.5 * (1 + Z / A)
    if P <= 0 or P >= 1:
        return 0.0 if P <= 0 else 1.0
    return float(((1 - P) / P) ** (capital / A))


def ruin_curve(returns, steps=10000):
    """Risk of Ruin curve across capital fractions 0 to 1.

    Returns array of shape (steps, 2): [capital_fraction, ruin_probability].
    """
    cap = np.linspace(1 / steps, 1.0, steps)
    out = np.empty((steps, 2))
    for i, c in enumerate(cap):
        out[i, 0] = c
        out[i, 1] = risk_of_ruin_empirical(returns, capital=c)
    return out


# ---------------------------------------------------------------------------
# VaR (use linear returns)
# ---------------------------------------------------------------------------

def var_normal(returns, alpha=0.05):
    """VaR under normal assumption. Two equivalent formulations."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return 0.0
    mu, sigma = stats.norm.fit(r)
    return float(-mu - sigma * stats.norm.ppf(alpha))


def var_empirical(returns, alpha=0.05):
    """VaR empirical: alpha-quantile of returns (negative number = loss)."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return 0.0
    return float(np.quantile(r, alpha))


def var_johnsonsu(returns, alpha=0.05):
    """VaR with Johnson SU fit. Returns negative value (loss).

    Note: returns must be non-degenerate. The Johnson SU pdf can fail to
    fit very small or pathological samples.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 4:
        return var_empirical(returns, alpha)
    try:
        gamma, delta, xi, lambda_ = stats.johnsonsu.fit(r)
        return float(stats.johnsonsu.ppf(alpha, gamma, delta, xi, lambda_))
    except Exception:
        return var_empirical(returns, alpha)


def var_all(returns, alpha=0.05):
    """All 3 VaR methods in a dict."""
    return {
        'empirical': var_empirical(returns, alpha),
        'normal': var_normal(returns, alpha),
        'johnsonsu': var_johnsonsu(returns, alpha),
    }


# ---------------------------------------------------------------------------
# cVaR / Expected Shortfall (use linear returns)
# ---------------------------------------------------------------------------

def cvar_normal(returns, alpha=0.05):
    """cVaR under normal assumption: -mu + sigma * pdf(Phi^-1(alpha)) / alpha.

    Note: alpha here is 1-confidence, e.g. 0.05 for 95% VaR.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return 0.0
    mu, sigma = stats.norm.fit(r)
    z = stats.norm.ppf(alpha)
    return float(-mu - sigma * stats.norm.pdf(z) / alpha)


def cvar_empirical(returns, alpha=0.05):
    """cVaR empirical: mean of returns <= VaR(alpha).

    From course notebook cVaRemp().
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return 0.0
    var = var_empirical(returns, alpha)
    tail = r[r <= var]
    if len(tail) == 0:
        return var
    return float(-tail.mean())


def cvar_johnsonsu(returns, alpha=0.05):
    """cVaR with Johnson SU. Closed-form formula from course slide 75.

    ES_alpha(X) = -xi - (lambda / (2*alpha)) * [
        exp((1 - 2*gamma*delta) / (2*delta^2)) * Phi(Phi^-1(alpha) - 1/delta)
        - exp((1 + 2*gamma*delta) / (2*delta^2)) * Phi(Phi^-1(alpha) + 1/delta)
    ]
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 4:
        return cvar_empirical(returns, alpha)
    try:
        gamma, delta, xi, lambda_ = stats.johnsonsu.fit(r)
        cdf = stats.norm.cdf
        ppf = stats.norm.ppf
        return float(
            -xi - (lambda_ / (2 * alpha)) * (
                np.exp((1 - 2 * gamma * delta) / (2 * delta ** 2)) * cdf(ppf(alpha) - 1 / delta)
                - np.exp((1 + 2 * gamma * delta) / (2 * delta ** 2)) * cdf(ppf(alpha) + 1 / delta)
            )
        )
    except Exception:
        return cvar_empirical(returns, alpha)


def cvar_all(returns, alpha=0.05):
    """All 3 cVaR methods."""
    return {
        'empirical': cvar_empirical(returns, alpha),
        'normal': cvar_normal(returns, alpha),
        'johnsonsu': cvar_johnsonsu(returns, alpha),
    }


# ---------------------------------------------------------------------------
# Trade statistics (use LOG returns — required by course material)
# ---------------------------------------------------------------------------

def payoff_ratio(log_returns):
    """Payoff ratio: -mean(winners) / mean(losers).

    From course slide 77. LOG RETURNS REQUIRED.
    """
    r = np.asarray(log_returns, dtype=float)
    r = r[~np.isnan(r)]
    winners = r[r > 0]
    losers = r[r < 0]
    if len(winners) == 0 or len(losers) == 0:
        return np.nan
    return float(-winners.mean() / losers.mean())


def profit_factor(log_returns):
    """Profit factor: -sum(winners) / sum(losers).

    From course slide 78. LOG RETURNS REQUIRED.
    """
    r = np.asarray(log_returns, dtype=float)
    r = r[~np.isnan(r)]
    winners = r[r > 0]
    losers = r[r < 0]
    if len(winners) == 0 or len(losers) == 0:
        return np.nan
    return float(-winners.sum() / losers.sum())


def win_loss_ratio(log_returns):
    """Win/Loss ratio: count(winners) / count(losers).

    From course slide 79. LOG RETURNS REQUIRED.
    """
    r = np.asarray(log_returns, dtype=float)
    r = r[~np.isnan(r)]
    winners = r[r > 0]
    losers = r[r < 0]
    if len(losers) == 0:
        return np.nan
    return float(len(winners) / len(losers))


def payoff_summary(strategy_prices, benchmark_prices):
    """Combined Payoff/WinLoss/ProfitFactor across daily timeframe.

    From course notebook payoff_summary(). Returns DataFrame.
    """
    sp = pd.Series(np.asarray(strategy_prices, dtype=float))
    bp = pd.Series(np.asarray(benchmark_prices, dtype=float))
    if len(sp) < 2 or len(bp) < 2:
        return pd.DataFrame()
    s_log = np.log(sp / sp.shift()).dropna()
    b_log = np.log(bp / bp.shift()).dropna()
    s_pay = -s_log[s_log > 0].mean() / s_log[s_log < 0].mean() if (s_log < 0).sum() > 0 else np.nan
    b_pay = -b_log[b_log > 0].mean() / b_log[b_log < 0].mean() if (b_log < 0).sum() > 0 else np.nan
    s_wl = (s_log > 0).sum() / (s_log < 0).sum() if (s_log < 0).sum() > 0 else np.nan
    b_wl = (b_log > 0).sum() / (b_log < 0).sum() if (b_log < 0).sum() > 0 else np.nan
    s_pf = -s_log[s_log > 0].sum() / s_log[s_log < 0].sum() if (s_log < 0).sum() > 0 else np.nan
    b_pf = -b_log[b_log > 0].sum() / b_log[b_log < 0].sum() if (b_log < 0).sum() > 0 else np.nan
    return pd.DataFrame([{
        'timeframe': 'D',
        'strategy_payoff': s_pay,
        'benchmark_payoff': b_pay,
        'strategy_wl': s_wl,
        'benchmark_wl': b_wl,
        'strategy_pf': s_pf,
        'benchmark_pf': b_pf,
    }]).set_index('timeframe')


# ---------------------------------------------------------------------------
# Tail ratios (use LOG returns)
# ---------------------------------------------------------------------------

def rachev_a(log_returns, alpha=0.05):
    """Rachev A: ratio of upper quantile to |lower quantile|.

    From course slide 82. LOG RETURNS REQUIRED.
    """
    r = np.asarray(log_returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return np.nan
    right = np.quantile(r, 1 - alpha)
    left = abs(np.quantile(r, alpha))
    if left == 0:
        return np.nan
    return float(right / left)


def rachev_b(log_returns, alpha=0.05):
    """Rachev B: ratio of mean(tail-up) to mean(tail-down).

    From course slide 83. LOG RETURNS REQUIRED.
    """
    r = np.asarray(log_returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return np.nan
    qR = np.quantile(r, 1 - alpha)
    qL = np.quantile(r, alpha)
    tail_R = r[r > qR]
    tail_L = r[r < qL]
    if len(tail_L) == 0 or len(tail_R) == 0:
        return np.nan
    return float(-tail_R.mean() / tail_L.mean())


def rachev_c(log_returns, alpha=0.05):
    """Rachev C: ratio of areas under PDF tails, weighted by probability.

    From course slide 84. LOG RETURNS REQUIRED. Uses normal PDF for
    weighting the tail observations.
    """
    r = np.asarray(log_returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return np.nan
    qL = np.quantile(r, alpha)
    qR = np.quantile(r, 1 - alpha)
    L = np.array([abs(x) for x in r if x < qL])
    R = np.array([x for x in r if x > qR])
    if len(L) == 0 or len(R) == 0:
        return np.nan
    num = (stats.norm.pdf(R) * R).sum()
    den = (stats.norm.pdf(L) * L).sum()
    if den == 0:
        return np.nan
    return float(num / den)


def common_sense_ratio(log_returns, alpha=0.05):
    """Common Sense Ratio (CSR) = Rachev_C * Profit Factor.

    From course slide 85. Combines the entire distribution ratio with
    the tail ratio. LOG RETURNS REQUIRED.
    """
    rc = rachev_c(log_returns, alpha)
    pf = profit_factor(log_returns)
    if np.isnan(rc) or np.isnan(pf):
        return np.nan
    return float(rc * pf)


def outlier_win_ratio(log_returns, alpha=0.01):
    """Outlier Win Ratio: mean(top-alpha quantile) / mean(all positives).

    From course slide 86. LOG RETURNS REQUIRED.
    """
    r = np.asarray(log_returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return np.nan
    out_w = r[r >= np.quantile(r, 1 - alpha)]
    pos = r[r > 0]
    if len(pos) == 0 or len(out_w) == 0:
        return np.nan
    return float(out_w.mean() / pos.mean())


def outlier_loss_ratio(log_returns, alpha=0.01):
    """Outlier Loss Ratio: mean(bottom-alpha quantile) / mean(all negatives).

    From course slide 86. LOG RETURNS REQUIRED.
    """
    r = np.asarray(log_returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return np.nan
    out_l = r[r <= np.quantile(r, alpha)]
    neg = r[r < 0]
    if len(neg) == 0 or len(out_l) == 0:
        return np.nan
    return float(out_l.mean() / neg.mean())


# ---------------------------------------------------------------------------
# Exposure (time in market)
# ---------------------------------------------------------------------------

def days_in_market_pct(strategy_returns):
    """Fraction of days the strategy was in the market (returns != 0)."""
    r = np.asarray(strategy_returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return 0.0
    return float((r != 0).sum() / len(r))


def time_exposure(strategy_returns, total_days):
    """Days the strategy was active / total days of the period."""
    r = np.asarray(strategy_returns, dtype=float)
    r = r[~np.isnan(r)]
    if total_days == 0:
        return 0.0
    return float((r != 0).sum() / total_days)


# ---------------------------------------------------------------------------
# Resample metrics
# ---------------------------------------------------------------------------

def resample_metrics(strategy_prices, benchmark_prices, period='M'):
    """Resample to given period and compute expected / worst / best return.

    From course notebook getResampleMetrics().
    """
    sp = pd.Series(np.asarray(strategy_prices, dtype=float))
    bp = pd.Series(np.asarray(benchmark_prices, dtype=float))
    rsp = sp.resample(period).last().dropna()
    rbp = bp.resample(period).last().dropna()
    if len(rsp) < 2 or len(rbp) < 2:
        return None
    rsp_ret = rsp / rsp.shift() - 1
    rbp_ret = rbp / rbp.shift() - 1
    rsp_ret = rsp_ret.dropna()
    rbp_ret = rbp_ret.dropna()
    return {
        'exp_strategy': (rsp.iloc[-1] / rsp.iloc[0]) ** (1 / len(rsp)) - 1,
        'exp_benchmark': (rbp.iloc[-1] / rbp.iloc[0]) ** (1 / len(rbp)) - 1,
        'worst_strategy': rsp_ret.min(),
        'worst_benchmark': rbp_ret.min(),
        'best_strategy': rsp_ret.max(),
        'best_benchmark': rbp_ret.max(),
    }


# ---------------------------------------------------------------------------
# Min/max by period
# ---------------------------------------------------------------------------

def min_return(returns, period='D'):
    r = pd.Series(np.asarray(returns, dtype=float))
    rs = r.resample(period).last().pct_change().dropna()
    return float(rs.min())


def max_return(returns, period='D'):
    r = pd.Series(np.asarray(returns, dtype=float))
    rs = r.resample(period).last().pct_change().dropna()
    return float(rs.max())


# ---------------------------------------------------------------------------
# Module entry
# ---------------------------------------------------------------------------

def compute_all(prices, benchmark_prices=None, log_prices=True, defaults=None):
    """Compute the full standard risk-metric panel for a price series.

    Parameters
    ----------
    prices : array-like
        Strategy or asset price series.
    benchmark_prices : array-like, optional
        Benchmark price series. If provided, R^2, beta, IR, tracking error
        and min/max by period are also computed.
    log_prices : bool
        If True, the first element of prices is treated as valid and all
        ratios derived from returns are computed.
    defaults : dict, optional
        Override default parameters (alpha for VaR, window, etc.).

    Returns
    -------
    dict of metric name -> value.
    """
    p = np.asarray(prices, dtype=float)
    p = p[~np.isnan(p)]
    if len(p) < 2:
        return {}
    r = linear_returns(p)
    lr = log_returns(p)
    d = defaults or {}
    var_alpha = d.get('var_confidence', 0.95)
    cvar_alpha = 1 - d.get('cvar_confidence', 0.99)
    rachev_alpha = d.get('rachev_alpha', 0.05)
    out_alpha = d.get('outlier_alpha', 0.01)

    out = {
        'cagr': cagr((p[-1] / p[0]) - 1, (len(p) - 1) / 252),
        'annualized_vol': annualized_vol(r),
        'skewness': skewness(r),
        'kurtosis': kurtosis(r),
        'sharpe_ratio': sharpe_ratio(r),
        'sortino': sortino(r, method=d.get('sortino_method', 'from_mean')),
        'max_drawdown': max_drawdown(p),
        'avg_drawdown': avg_drawdown(p),
        'avg_drawdown_duration': avg_drawdown_duration(p),
        'ulcer_index': ulcer_index(p),
        'recovery_factor': recovery_factor(p),
        'linearity_coefficient': linearity_coefficient(p),
        'kelly_fraction': kelly_fraction(lr),
        'risk_of_ruin_normal': risk_of_ruin_normal(r),
        'risk_of_ruin_empirical': risk_of_ruin_empirical(r),
        'var_empirical': var_empirical(r, alpha=1 - var_alpha),
        'var_normal': var_normal(r, alpha=1 - var_alpha),
        'var_johnsonsu': var_johnsonsu(r, alpha=1 - var_alpha),
        'cvar_empirical': cvar_empirical(r, alpha=1 - cvar_alpha),
        'cvar_normal': cvar_normal(r, alpha=1 - cvar_alpha),
        'cvar_johnsonsu': cvar_johnsonsu(r, alpha=1 - cvar_alpha),
        'payoff_ratio': payoff_ratio(lr),
        'profit_factor': profit_factor(lr),
        'win_loss_ratio': win_loss_ratio(lr),
        'rachev_a': rachev_a(lr, alpha=rachev_alpha),
        'rachev_b': rachev_b(lr, alpha=rachev_alpha),
        'rachev_c': rachev_c(lr, alpha=rachev_alpha),
        'common_sense_ratio': common_sense_ratio(lr, alpha=rachev_alpha),
        'outlier_win_ratio': outlier_win_ratio(lr, alpha=out_alpha),
        'outlier_loss_ratio': outlier_loss_ratio(lr, alpha=out_alpha),
        'days_in_market_pct': days_in_market_pct(r),
        'calmar_ratio': calmar_ratio(
            cagr((p[-1] / p[0]) - 1, (len(p) - 1) / 252), max_drawdown(p)
        ),
    }
    if benchmark_prices is not None:
        bp = np.asarray(benchmark_prices, dtype=float)
        bp = bp[~np.isnan(bp)]
        if len(bp) == len(p):
            br = linear_returns(bp)
            out['r_squared'] = r_squared(r, br)
            out['information_ratio'] = information_ratio(r, br)
            out['tracking_error'] = tracking_error(r, br)
            blr = log_returns(bp)
            out['payoff_summary'] = payoff_summary(p, bp)
    return out
