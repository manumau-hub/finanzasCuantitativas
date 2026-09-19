# Magnificent 7

## Overview

The **Magnificent 7** refers to the seven mega-cap US technology and
technology-adjacent companies that drove the majority of S&P 500 returns
in 2023-2024:

| Ticker | Company | Sector | Weight in SPX (2024) |
|--------|---------|--------|---------------------|
| AAPL | Apple | Technology | ~7% |
| MSFT | Microsoft | Technology | ~7% |
| NVDA | NVIDIA | Technology | ~6% |
| GOOGL | Alphabet | Communication Services | ~4% |
| AMZN | Amazon | Consumer Discretionary | ~4% |
| META | Meta Platforms | Communication Services | ~3% |
| TSLA | Tesla | Consumer Discretionary | ~2% |

**Combined weight in S&P 500: ~33%** (up from ~13% in 2018).

---

## Historical Lineage

### Nifty Fifty (1960s-1970s)

The first "must-own" basket of growth stocks (Xerox, IBM, Polaroid,
Coca-Cola, McDonald's). Narrative: "one-decision" stocks — buy and
hold forever. Many collapsed in the 1973-74 bear market.

### FANG / FAANG (2013-2022)

- **Facebook** (META), **Amazon** (AMZN), **Netflix** (NFLX),
  **Google** (GOOGL) — "FANG" coined by Jim Cramer in 2013
- Later expanded to FAANG: **Apple** (AAPL) added
- Narrative: disruptors, platform monopolies

### Magnificent 7 (2023-present)

Term coined by Bank of America analyst Michael Hartnett in 2023.
Narrative: **AI winners** — companies with the scale, data, and
compute to dominate AI.

---

## Concentration Risk

The Mag 7's weight in the S&P 500 exceeds the concentration of the
**top 7 stocks at the 2000 dot-com peak** (~25% vs ~33%). This is
the highest concentration in the index's history.

### Implications

- **Single-stock risk**: The S&P 500 is effectively tilting on the
  performance of 7 stocks
- **Correlation risk**: As Mag 7 goes, so goes the index. In 2022,
  M7 fell ~40-60%, dragging SPX down ~19%
- **Regime change risk**: If AI narrative falters, concentration
  amplifies downside

---

## AI Capex

The Mag 7 are spending unprecedented amounts on AI infrastructure:

- **NVDA**: +1000%+ revenue growth (2023-2025)
- **MSFT**: $50B+/year on AI data centers
- **GOOGL**: $40B+/year capex, majority AI
- **META**: $35B+/year on AI compute
- **AMZN**: $60B+/year on AWS AI infrastructure

Total AI capex across the Mag 7: **$200B+/year** (2024-2025 est).

---

## Pairwise Correlation

60-day rolling correlation between Mag 7 members has increased
significantly (from ~0.3-0.4 in 2018 to ~0.6-0.8 in 2024). This
reduces the diversification benefit within the group.

---

## AI Valuation vs Dot-com

The dataset `mag7/ai-valuation.json` compares NVDA/MSFT/META/GOOGL
TTM P/E ratios to the 1999 dot-com bands for the SOX index:

| Metric | 1999 Dot-com | 2024 AI Peak |
|--------|-------------|--------------|
| NVDA TTM P/E | N/A | ~50-80x |
| MSFT TTM P/E | ~60x | ~35x |
| META TTM P/E | N/A | ~25x |
| GOOGL TTM P/E | ~80x | ~25x |

Unlike 1999, the current Mag 7 **actually have earnings** to support
their valuations, though absolute P/E ratios are elevated.

---

## Related Datasets

| Dataset | Descripcion |
|---------|-------------|
| `/api/m7/index.json` | Mag 7 equal-weighted composite |
| `/api/mag7/concentration.json` | % of S&P 500 cap (2018→2024) |
| `/api/mag7/drawdown.json` | Per-member peak-to-date drawdown |
| `/api/mag7/correlation.json` | 60-day rolling pairwise correlation |
| `/api/mag7/ai-valuation.json` | TTM PE vs dotcom bands |
| `/api/mag7/ai-capex.json` | AI capital expenditure |
| `/api/mag7/predecessors.json` | Nifty Fifty → FANG → Mag 7 lineage |
