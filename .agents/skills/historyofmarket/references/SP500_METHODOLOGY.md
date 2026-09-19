# S&P 500 Methodology

## Overview

The S&P 500 is a market-capitalization-weighted index of 500 leading US
publicly traded companies. It is maintained by the S&P Dow Jones Indices
Committee and is widely regarded as the best single gauge of large-cap US
equities.

---

## Eligibility Criteria

### Market Capitalization

- Minimum **unadjusted company float-adjusted market cap** of USD
  **22.7 billion** (as of 2026; adjusted periodically)
- At least **10%** of shares must be publicly traded (float-adjusted)

### Liquidity

- **Value traded ratio** (annual dollar value traded / float-adjusted market
  cap) >= 0.75
- **Number of shares traded** each month for the 6 months before evaluation
  date must be >= 250,000

### Financial Viability

- **Earnings test**: Sum of trailing four consecutive quarters' GAAP earnings
  (as-reported) must be positive in the most recent quarter AND positive over
  the most recent four quarters (trailing twelve months)
- Companies in the S&P Total Market Index (TMI) that are not in the S&P 500
  but meet the above criteria are eligible

### Public Float & Listing

- **IPO/Spin-off seasoning**: Generally 12 months of trading history on a
  major US exchange (NYSE, Nasdaq, Cboe)
- **Domicile**: Must be incorporated in the US and listed on a US exchange
- **Structure**: REITs and certain partnership structures are eligible;
  closed-end funds, ETFs, and holding companies are not

---

## Index Committee

The S&P 500 is not purely rules-based. A **committee** (S&P DJI) has
discretion over:

- Additions (not just by market cap ranking)
- Removals (mergers, bankruptcies, severe distress)
- Sector classification changes (GICS)

The committee meets **monthly** but can act at any time (e.g., bankruptcy
removals are immediate).

---

## Reconstitution & Rebalancing

- **Reconstitution**: Additions occur as-needed (not on a fixed schedule).
  The committee evaluates candidates continuously.
- **Rebalancing**: Quarterly (March, June, September, December) to ensure
  float-adjusted weights reflect current shares outstanding.
- **Share updates**: Between rebalances, share changes >5% are applied
  immediately; smaller changes accumulate to the next rebalance.

---

## GICS Sector Classification

The S&P 500 uses the **Global Industry Classification Standard (GICS)**,
developed by MSCI and S&P DJI. Major sectors tracked by this API:

| GICS Sector | Ticker | ETF | Weight in SPX (approx) |
|-------------|--------|-----|------------------------|
| Information Technology | XLK | ~30% |
| Financials | XLF | ~13% |
| Health Care | XLV | ~12% |
| Consumer Discretionary | XLY | ~11% |
| Communication Services | XLC | ~9% |
| Industrials | XLI | ~8% |
| Consumer Staples | XLP | ~6% |
| Energy | XLE | ~4% |
| Utilities | XLU | ~3% |
| Real Estate | XLRE | ~2% |
| Materials | XLB | ~2% |

---

## Related Datasets

| Dataset | Descripcion |
|---------|-------------|
| `/api/sp500/rules.json` | Full methodology document from S&P DJI |
| `/api/sp500/constituents.json` | Current 500 members with sector, weight, 1y return |
| `/api/sp500/changes.json` | Historical adds/removes with date, reason, source |
| `/api/sp500/sectors.json` | GICS sector weights |
