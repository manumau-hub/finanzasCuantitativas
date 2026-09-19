# Sector ETFs: XLK & XLF

## XLK — Technology Select Sector SPDR

### Overview

XLK tracks the **Technology Select Sector Index** of the S&P 500.
Launched: **December 16, 1998**. Expense ratio: 0.10%.

### Composition

The top holdings concentrate massively:

| Ticker | Company | Weight (approx) |
|--------|---------|-----------------|
| AAPL | Apple | ~22% |
| MSFT | Microsoft | ~20% |
| NVDA | NVIDIA | ~15% |
| AVGO | Broadcom | ~5% |
| CRM | Salesforce | ~3% |

**Top 3 > 57%, top 5 > 65%.** XLK is essentially a bet on AAPL + MSFT + NVDA.

### GICS 2018 Reclassification

On **September 28, 2018**, MSCI and S&P reclassified:

- **GOOGL**, **GOOG** (Alphabet), **META** (Facebook), **NFLX** (Netflix)
  moved from Information Technology → **Communication Services** (new GICS
  sector XLC)

This was the single largest sector reclassification in S&P 500 history,
affecting ~$2 trillion in market cap and ~5% of XLK's weight.

---

## XLF — Financials Select Sector SPDR

### Overview

XLF tracks the **Financials Select Sector Index** of the S&P 500.
Launched: **December 16, 1998**. Expense ratio: 0.10%.

### Composition

| Ticker | Company | Weight (approx) |
|--------|---------|-----------------|
| BRK.B | Berkshire Hathaway | ~13% |
| JPM | JPMorgan Chase | ~10% |
| V | Visa | ~5% |
| MA | Mastercard | ~4% |
| BAC | Bank of America | ~4% |

### 2008 Financial Crisis

XLF lost **-84%** from peak to trough (Oct 2007 - Mar 2009). Five major
financial institutions vanished:

| Institution | Fate |
|-------------|------|
| **Bear Stearns** | Acquired by JPMorgan (Mar 2008) |
| **Lehman Brothers** | Bankruptcy (Sep 2008) |
| **Washington Mutual** | Seized by FDIC, sold to JPMorgan |
| **Wachovia** | Acquired by Wells Fargo |
| **AIG** | Government bailout |

Contrast with the **"survived"** institutions (JPM, GS, MS, BAC, WFC)
which saw massive share dilution but eventually recovered.

### GICS 2023 Reclassification

On **March 17, 2023**, several payment companies moved from
Information Technology → **Financials**:

- **V** (Visa), **MA** (Mastercard), **PYPL** (PayPal),
  **FIS** (Fidelity National), **Fiserv**

This added ~$1 trillion in market cap to XLF and was the largest single
inflow to the Financials sector since inception.

---

## Yield Curve & Financials

The `/api/fin/rates.json` dataset shows the relationship between the
**2y-10y yield curve** and XLF 12-month forward returns:

- **Steepening curve** (2y-10y widening): Bullish for banks (net interest
  margin expands)
- **Inverted curve** (2y > 10y): Bearish for banks (NIM compression;
  historically signals recession)

---

## Related Datasets

| Dataset | Descripcion |
|---------|-------------|
| `/api/xlk/price.json` | XLK daily since 1998 |
| `/api/xlk/holdings.json` | Top 10 holdings with weights |
| `/api/xlk/reclass-2018.json` | GICS 2018 reclassification impact |
| `/api/fin/price.json` | XLF daily since 1998 |
| `/api/fin/holdings.json` | Top holdings (BRK.B + JPM ~23%) |
| `/api/fin/crisis-2008.json` | 5 vanished vs 5 survived |
| `/api/fin/rates.json` | Yield curve vs XLF returns |
| `/api/fin/reclass-2023.json` | GICS 2023 reclassification |
