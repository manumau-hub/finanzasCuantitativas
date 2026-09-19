# Broader Market

## Dow Jones Industrial Average

### Overview

The **Dow Jones Industrial Average (DJIA)** is the second-oldest US stock
market index (after the Dow Jones Transportation). Created by **Charles
Dow** in **1896**, it originally had 12 components and was expanded to 30
in 1928.

### Methodology

- **Price-weighted** (not market-cap weighted). Higher-priced stocks have
  more influence regardless of company size.
- **Divisor**: Adjusts for stock splits, spin-offs, and substitutions.
  Currently ~0.15 (as of 2024).
- **30 components** selected by the editors of the Wall Street Journal
  (not a committee). Selection is based on reputation, sector
  representation, and broad market coverage.

### Criticisms

- Price weighting is arbitrary — a $500 stock affects the index 10x more
  than a $50 stock, even if the $50 company is larger
- Only 30 stocks → high idiosyncratic risk
- Excludes tech giants like NVDA, META, GOOGL (until recent changes)

### Key Statistics

- **Inception**: May 26, 1896 (base: 40.94)
- **First close > 100**: Jan 12, 1906
- **First close > 1,000**: Nov 14, 1972
- **First close > 10,000**: Mar 29, 1999
- **First close > 20,000**: Jan 25, 2017
- **First close > 30,000**: Nov 24, 2020

---

## Philadelphia Semiconductor Index (SOX)

### Overview

The **Philadelphia Stock Exchange Semiconductor Index (SOX)** tracks 30
semiconductor companies. Created in **1993**. Owned by Nasdaq since 2007.

### 30 Constituents

Companies are categorized by sub-industry:

| Sub-industry | Examples | Weight (approx) |
|-------------|----------|-----------------|
| **Fabless** | NVDA, AMD, QCOM, MRVL | ~55% |
| **Foundry** | TSM (ADR) | ~10% |
| **Memory** | MU, STX, WDC | ~8% |
| **IDM** | INTC, TXN | ~12% |
| **Equipment** | ASML, AMAT, LRCX, KLAC | ~12% |
| **Chip design IP** | ARM, CDNS, SNPS | ~3% |

### SMH ETF

VanEck Semiconductor ETF (SMH) tracks a modified-market-cap-weighted
index of 25 semiconductor companies. Top holdings:

- NVDA (~20%), TSM (~12%), ASML (~8%), AVGO (~7%), AMAT (~5%)

### SOX/SOX Ratio

The ratio SOX/SPX measures semiconductors' relative performance vs the
broad market. Rebasing to 100 at a given date shows whether semis are
leading or lagging.

---

## NBER Recessions

### Definition

The **National Bureau of Economic Research (NBER)** is the official
arbiter of US recessions. Their Business Cycle Dating Committee defines
a recession as:

> "A significant decline in economic activity that is spread across the
> economy and lasts more than a few months"

### US Recessions Since 1929

| Period | Duration (months) | Severity |
|--------|------------------|----------|
| Aug 1929 - Mar 1933 | 43 | Great Depression |
| May 1937 - Jun 1938 | 13 | Depression within Depression |
| Feb 1945 - Oct 1945 | 8 | Post-WWII |
| Nov 1948 - Oct 1949 | 11 | Post-war adjustment |
| Jul 1953 - May 1954 | 10 | Post-Korean War |
| Aug 1957 - Apr 1958 | 8 | Eisenhower recession |
| Apr 1960 - Feb 1961 | 10 | |
| Dec 1969 - Nov 1970 | 11 | |
| Nov 1973 - Mar 1975 | 16 | Oil crisis |
| Jan 1980 - Jul 1980 | 6 | Volcker recession |
| Jul 1981 - Nov 1982 | 16 | Double-dip |
| Jul 1990 - Mar 1991 | 8 | Gulf War |
| Mar 2001 - Nov 2001 | 8 | Dot-com bust |
| Dec 2007 - Jun 2009 | 18 | Financial Crisis |
| Feb 2020 - Apr 2020 | 2 | COVID-19 (shortest) |

---

## Yield Curve

### 2y-10y Spread

The difference between the 10-year US Treasury yield and the 2-year US
Treasury yield. A closely watched recession predictor:

- **Positive spread** (normal curve): Long-term rates > short-term rates
- **Inverted spread** (2y > 10y): Historically predicts recessions 12-18
  months ahead. Has preceded every US recession since 1970.
- **Steepening**: Typically occurs as the Fed cuts rates during/after a
  recession

---

## AIAE — Aggregate Investor Allocation to Equities

AIAE measures the aggregate allocation of US institutional and retail
investors to equities. Developed by the dataset provider. It has been
shown to be a **better predictor of 10-year forward returns than CAPE**.

| AIAE Level | Signal |
|------------|--------|
| < 40% | Strongly bullish (low equity allocation) |
| 40-50% | Moderately bullish |
| 50-60% | Neutral |
| 60-70% | Moderately bearish |
| > 70% | Strongly bearish (crowded equities) |

---

## Related Datasets

| Dataset | Descripcion |
|---------|-------------|
| `/api/dow/century.json` | DJIA daily since 1914 |
| `/api/semi/price.json` | SOX daily since 1994 |
| `/api/semi/composition.json` | 30 constituents by sub-industry |
| `/api/semi/smh.json` | SMH ETF holdings |
| `/api/semi/ratios.json` | SOX/SPX, XLK/SPX ratios |
| `/api/recessions.json` | NBER recession dates |
| `/api/yield-curve.json` | 2y-10y yield curve data |
| `/api/aiae.json` | Aggregate Investor Allocation to Equities |
