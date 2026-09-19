# Drawdowns & Volatility

## Drawdowns

### Definition

A **drawdown** is the peak-to-trough decline of an investment or index
during a specific period. It is measured from the highest point (peak)
to the lowest point (trough) before a new high is reached.

```
Drawdown = (Current Value - Peak Value) / Peak Value
```

### Maximum Drawdown (MaxDD)

The largest peak-to-trough decline over the entire history. For S&P 500:

| Drawdown | Peak | Trough | Decline | Recovery |
|----------|------|--------|---------|----------|
| Great Depression | Sep 1929 | Jun 1932 | -86% | ~25 years |
| 2008 Financial Crisis | Oct 2007 | Mar 2009 | -57% | ~4 years |
| Dot-com Bubble | Mar 2000 | Oct 2002 | -49% | ~4.5 years |
| COVID-19 | Feb 2020 | Mar 2020 | -34% | ~6 months |
| 1973-74 Oil Crisis | Jan 1973 | Sep 1974 | -48% | ~5 years |
| 2022 Inflation | Jan 2022 | Oct 2022 | -25% | ~2 years |

### Intrayear Drawdown vs Year-End Return

Most years have a double-digit intrayear drawdown (median ~-14%), but
year-end returns are positive ~73% of the time. This is the **"tunnel
vision" effect**: investors who look at year-end only miss the intra-year
volatility.

### Recovery Time

Average recovery from >-20% drawdowns: **3-4 years**. Faster recoveries
are associated with V-shaped crashes (COVID), slower with structural
crises (2008, Great Depression).

---

## Volatility

### Realized Volatility

Standard deviation of daily returns over a rolling window (typically 20
or 60 trading days), annualized:

```
Vol = sqrt(252) * std(daily_returns)
```

| Index | Median Realized Vol (20d) |
|-------|--------------------------|
| S&P 500 | ~15% |
| Nasdaq 100 | ~22% |
| SOX | ~28% |
| XLF | ~25% |

### VIX / VXN

- **VIX**: CBOE Volatility Index based on S&P 500 options (since 1990).
  Often called the "fear index". Mean: ~20, median: ~18.
- **VXN**: CBOE Nasdaq 100 Volatility Index (since 2001). Similar
  methodology but on NDX options. Mean: ~25, median: ~22.

### Volatility Regimes

Volatility clusters: high-vol periods tend to be followed by high-vol
periods, and low-vol by low-vol (GARCH effect). Common regimes:

| Regime | VIX Range | Frequency |
|--------|-----------|-----------|
| Low | < 15 | ~25% |
| Normal | 15-25 | ~45% |
| Elevated | 25-35 | ~15% |
| Crisis | > 35 | ~15% |

---

## Related Datasets

| Dataset | Descripcion |
|---------|-------------|
| `/api/sp500/drawdowns.json` | All SPX drawdowns with cause & recovery days |
| `/api/sp500/intrayear-dd.json` | Intrayear drop vs year-end return |
| `/api/sp500/volatility.json` | Realized vol 20d/60d |
| `/api/sp500/vix.json` | VIX daily since 1990 |
| `/api/ndx/drawdowns.json` | NDX drawdowns (59 events) |
| `/api/ndx/vxn.json` | VXN daily since 2001 |
| `/api/semi/drawdowns.json` | SOX drawdowns |
| `/api/xlk/drawdowns.json` | XLK drawdowns |
| `/api/fin/drawdowns.json` | XLF drawdowns (incl 2008 -84%) |
