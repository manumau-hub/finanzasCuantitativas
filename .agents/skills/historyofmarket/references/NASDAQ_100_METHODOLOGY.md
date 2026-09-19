# Nasdaq 100 Methodology

## Overview

The Nasdaq 100 Index (NDX) includes **100 of the largest non-financial
companies** listed on the Nasdaq Stock Market. It is modified
market-capitalization weighted and covers major industry groups including
technology, consumer services, health care, and industrials.

Launched: **January 31, 1985** (base value: 250)

---

## Eligibility Criteria

### Listing Requirements

- Must be listed exclusively on the **Nasdaq Stock Market**
- Must have a **minimum average daily trading volume** of 200,000 shares
- Must have been listed for at least **3 full months** (unless a spin-off)

### Financial Requirements

- **Market capitalization** must be sufficiently large to rank among the
  largest non-financial Nasdaq-listed companies
- Companies in **liquidation** or **bankruptcy** are ineligible
- **Financial companies** (GICS 40) are excluded by design

### Sector Composition

Unlike S&P 500, Nasdaq 100 explicitly excludes financial companies. The
index is heavily tilted toward:

- Technology (~50-55%)
- Consumer Services (~20-25%)
- Health Care (~8-10%)
- Industrials (~5-8%)

---

## Reconstitution

### Annual Reconstitution

- Conducted **annually** in December
- Reference date for rankings: **end of October**
- Changes effective: **3rd Friday of December** (before market open)

### Special Rebalancing

If the aggregated weight of the top 5 companies exceeds **40%** or the
weight of any single company exceeds **24%**, a special rebalancing is
triggered (rare; triggered in 1998, 2011, 2023).

### Weight Caps (Modified Market Cap)

- Top 5 constituents with highest market cap: capped at **40.5%** combined
  weight (maximum)
- Single company: capped at **20%** (for annual reconstitution) or **24%**
  (for special rebalancing)
- Excess weight is redistributed proportionally among remaining companies

---

## Related Datasets

| Dataset | Descripcion |
|---------|-------------|
| `/api/nasdaq/100.json` | Current 100 constituents with sector, weight, returns |
| `/api/ndx/changes.json` | Historical adds/removes with date |
| `/api/ndx/daily.json` | NDX daily closes since 1985 |
| `/api/ndx/drawdowns.json` | 59 historical drawdowns (dotcom peak -83%) |
| `/api/ndx/forward-pe.json` | Bloomberg forward PE since 2001 |
| `/api/qqq/return-details.json` | QQQ return decomposition |
