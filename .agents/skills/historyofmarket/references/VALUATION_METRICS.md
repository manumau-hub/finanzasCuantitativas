# Valuation Metrics

## Shiller CAPE (Cyclically Adjusted P/E)

### Definition

Also known as **PE10** or **Shiller P/E** (after Robert Shiller). It
divides the real (inflation-adjusted) price by the average of 10 years
of real earnings:

```
CAPE = Real Price / (Average Real EPS over 10 years)
```

### Why 10 years?

A single-year P/E can be distorted by the business cycle. Earnings are
highly cyclical — during recessions EPS collapses, inflating P/E; during
booms EPS surges, deflating P/E. The 10-year average smooths out the
cycle and gives a "through-cycle" valuation.

### Interpretation

| CAPE Range | Valuation Signal | Historical Outcome |
|------------|-----------------|-------------------|
| < 10 | Deeply undervalued | Great buys (1982, 1932) |
| 10-15 | Undervalued | Above-average 10y returns |
| 15-20 | Fair value | Average returns |
| 20-25 | Modestly overvalued | Below-average returns |
| 25-30 | Overvalued | Periods of low returns |
| > 30 | Highly overvalued | Historically rare (1999, 2021) |

### Caveats

- CAPE does NOT predict short-term (1-2 year) returns
- CAPE is a **10-year forward return predictor** (R² ~0.4)
- Changes in accounting standards, sector composition, and interest rates
  affect CAPE levels structurally
- Low interest rates justify higher CAPE (Fed Model / Equity Risk Premium)

---

## Forward P/E vs Trailing P/E

### Trailing P/E

Based on the last 12 months of actual (GAAP) reported earnings.

```
Trailing P/E = Price / TTM GAAP EPS
```

### Forward P/E

Based on analysts' consensus estimates for the next 12 months.

```
Forward P/E = Price / Estimated Next 12M EPS
```

Forward P/E is usually lower than trailing P/E because earnings tend to
grow. Discrepancies widen during earnings recessions.

---

## EPS (Earnings Per Share)

### GAAP TTM EPS

Standard GAAP earnings over the trailing twelve months. Covers the S&P
500 aggregate earnings from 1871. Key observations:

- EPS growth averages ~6-7% nominal, ~3% real
- Sharp contractions during recessions (2008: -89% peak-to-trough)
- Recovery tends to be V-shaped

### Driver Decomposition

Annual return decomposed into:

```
1 + r = (1 + r_PE) * (1 + r_EPS)

where:
  r_PE  = change in valuation multiple (rerating)
  r_EPS = growth in earnings (revision)
```

Historically, long-term returns are driven by EPS growth, but
short-term (1-5 year) returns are dominated by PE multiple changes.

| Period | Annualized Return | Rerating (r_PE) | Revision (r_EPS) |
|--------|------------------|-----------------|-------------------|
| 1928-2024 | ~10% | ~0% | ~10% |
| 2010-2024 | ~13% | ~4% | ~9% |
| 2000-2009 | -1% | -5% | ~4% |

### Return Details

Total return broken into:

```
Total Return = Price Return + Dividend Yield + Buyback Yield
```

- Price return: capital appreciation
- Dividend yield: cash dividends / price
- Buyback yield: net share repurchases / market cap

Buybacks have become the dominant form of returning capital to
shareholders since the 2000s (dividend + buyback yield ~4-5% combined).

---

## ROE (Return on Equity)

```
ROE = Net Income / Shareholders' Equity
```

S&P 500 aggregate ROE has been remarkably stable at ~15% over the past
two decades. ROE above 20% typically signals either high profitability
or high leverage (financial sector).

---

## Related Datasets

| Dataset | Descripcion |
|---------|-------------|
| `/api/sp500/pe.json` | Shiller CAPE from 1871 |
| `/api/sp500/forward-pe.json` | Trailing + Forward PE from 1990 |
| `/api/sp500/eps.json` | GAAP TTM EPS from 1871 |
| `/api/sp500/roe.json` | Return on equity |
| `/api/sp500/driver-decomp.json` | Annual return decomposition |
| `/api/sp500/return-details.json` | Price + dividend + buyback |
| `/api/ndx/forward-pe.json` | NDX forward PE from 2001 |
| `/api/ndx/driver-decomp.json` | NDX annual driver decomposition |
| `/api/mag7/ai-valuation.json` | Mag 7 PE vs dotcom bands |
| `/api/semi/memory-valuation.json` | Semi memory valuation vs 1999 |
