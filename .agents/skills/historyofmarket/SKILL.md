---
name: historyofmarket
description: "History of Market (historyofmarket.com) — API publica con 88 datasets historicos de indices US desde 1871. S&P 500 (price, CAPE, EPS, drawdowns, changes, constituents), Nasdaq Composite/Nasdaq 100 (price, volatility, VXN, changes), Dow Jones, SOX/SMH, sector ETFs (XLK, XLF), Magnificent 7 y macro. Sin API key, CORS libre, CC BY 4.0."
license: MIT
---

# History of Market

Skill para acceder a la API publica **historyofmarket.com** — 88 datasets
pre-generados (JSON estatico) sobre la historia de los mercados financieros
de EE.UU. desde 1871. Sin API key, sin autenticacion, CORS libre, licencia
CC BY 4.0.

Cada dataset es un archivo JSON pre-generado (sin parametros). Cache:
`max-age=300` con `stale-while-revalidate=3600`. Soporta ETag.

---

## 🎯 Que datos cubre

| Categoria | Indices / ETFs | Datos disponibles |
|-----------|----------------|-------------------|
| **S&P 500** | SPX | Daily desde 1928, CAPE desde 1871, EPS, drawdowns, volatilidad, VIX, constituents, changes, sectors, forward PE, ROE, driver decomp, return details |
| **Nasdaq Composite** | COMP | Daily desde 1971 |
| **Nasdaq 100** | NDX | Daily desde 1985, constituents, annual returns, drawdowns, VXN, forward PE, driver decomp, rolling 5y, changes |
| **QQQ** | QQQ | Return details (price + dividend + buyback) |
| **Dow Jones** | DJIA | Daily desde 1914 |
| **Philadelphia Semi** | SOX | Daily desde 1994, 30 constituents, SMH holdings, memory valuation, ratios SOX/SPX, ETF compare |
| **Sector ETFs** | XLK, XLF | Price, annual returns, drawdowns, volatility, holdings, GICS reclassifications (2018/2023) |
| **Mag 7** | AAPL/MSFT/NVDA/GOOGL/AMZN/META/TSLA | Equal-weighted composite, concentration, correlation, AI valuation, AI capex, lineage |
| **Macro** | — | AIAE (equity allocation), NBER recessions, yield curve, forward PE by sector |

---

## ⚡ Singularidades de este skill

1. **CAPE (Shiller PE) desde 1871** — el unico skill del repo con PE10
   historico. `references/VALUATION_METRICS.md`

2. **Drawdowns con causa** — cada drawdown incluye el evento que lo
   desencadeno y dias de recuperacion. `references/DRAWDOWN_VOLATILITY.md`

3. **Driver decomposition** — descompone el retorno anual en rerating
   (cambio de PE) vs revision (cambio de EPS). `references/VALUATION_METRICS.md`

4. **GICS reclassification** — impacto de los cambios de sector GICS 2018
   y 2023 en XLK y XLF. `references/SECTOR_ETFS.md`

5. **Reconstitucion historica** — los scripts permiten reconstruir
   miembros historicos de S&P 500 y Nasdaq 100 a una fecha dada.

---

## 🚀 Quick start

```bash
# S&P 500 — century closes
curl https://historyofmarket.com/api/sp500/century.json

# Shiller CAPE
curl https://historyofmarket.com/api/sp500/pe.json

# Drawdowns historicos con causa
curl https://historyofmarket.com/api/sp500/drawdowns.json

# Constituyentes actuales S&P 500
curl https://historyofmarket.com/api/sp500/constituents.json

# Cambios historicos S&P 500 (adds/removes)
curl https://historyofmarket.com/api/sp500/changes.json

# Nasdaq 100 constituyentes actuales
curl https://historyofmarket.com/api/nasdaq/100.json

# Mag 7 concentracion en S&P 500
curl https://historyofmarket.com/api/mag7/concentration.json

# NBER recessions
curl https://historyofmarket.com/api/recessions.json
```

---

## 📁 File map

```
skills/historyofmarket/
├── SKILL.md
├── assets/
│   └── endpoints.json        ← snapshot de todos los 88 endpoints
├── references/
│   ├── SP500_METHODOLOGY.md  ← S&P 500: elegibilidad, earnings test, cambios
│   ├── NASDAQ_100_METHODOLOGY.md
│   ├── DRAWDOWN_VOLATILITY.md
│   ├── VALUATION_METRICS.md  ← CAPE, forward PE, driver decomp, ROE
│   ├── SECTOR_ETFS.md        ← XLK, XLF, GICS reclass, holdings
│   ├── MAGNIFICENT7.md       ← Mag 7, concentration, AI capex, lineage
│   └── BROADER_MARKET.md     ← Dow, SOX, recessions, yield curve
└── scripts/
    ├── reconstitute_sp500.py  ← reconstruir miembros S&P 500 a fecha dada
    ├── reconstitute_ndx.py    ← reconstruir miembros NDX a fecha dada
    └── sector_rotation.py     ← rotacion sectorial XLK vs XLF vs SPY
```

---

## 📚 Referencias

Para entender la teoria detras de los datos:

| Documento | Contenido |
|-----------|-----------|
| [`references/SP500_METHODOLOGY.md`](./references/SP500_METHODOLOGY.md) | Elegibilidad, earnings test, market cap minimo, comite de indices, historial de cambios |
| [`references/NASDAQ_100_METHODOLOGY.md`](./references/NASDAQ_100_METHODOLOGY.md) | Nasdaq 100 methodology, annual reconstitution, weight caps |
| [`references/DRAWDOWN_VOLATILITY.md`](./references/DRAWDOWN_VOLATILITY.md) | Drawdowns, intrayear vs year-end, volatilidad realizada, VIX/VXN |
| [`references/VALUATION_METRICS.md`](./references/VALUATION_METRICS.md) | Shiller CAPE, forward PE, trailing PE, EPS, ROE, driver decomp |
| [`references/SECTOR_ETFS.md`](./references/SECTOR_ETFS.md) | Sector ETFs XLK/XLF, GICS reclassification 2018/2023, holdings |
| [`references/MAGNIFICENT7.md`](./references/MAGNIFICENT7.md) | Mag 7 composite, concentration in SPX, correlation, AI capex, lineage |
| [`references/BROADER_MARKET.md`](./references/BROADER_MARKET.md) | Dow Jones, SOX/SMH, NBER recessions, yield curve |

---

## 🐍 Scripts

| Script | Proposito | Uso |
|--------|-----------|-----|
| `scripts/reconstitute_sp500.py` | Reconstruir los 500 miembros del S&P 500 en una fecha historica | `py scripts/reconstitute_sp500.py 2020-01-01` |
| `scripts/reconstitute_ndx.py` | Reconstruir los 100 miembros del Nasdaq 100 en una fecha historica | `py scripts/reconstitute_ndx.py 2020-01-01` |
| `scripts/sector_rotation.py` | Analizar rotacion sectorial: rolling returns, correlacion, drawdowns sincronicos | `py scripts/sector_rotation.py` |

---

## 🌐 Entry points

| Endpoint | Descripcion |
|----------|-------------|
| `/api/_manifest.json` | Catalogo completo de los 88 datasets |
| `/api/profile.json` | Perfil del sitio para AI agents |
| `/api/tools.json` | Lista machine-callable de 68 tools |
| `/llms.txt` | Resumen LLM-friendly |
| `/.well-known/llms.txt` | Well-known location |
| `/ai.txt` | AI agent instructions |
| `/sitemap.xml` | Sitemap completo (60+ panels × 6 locales) |
| `/robots.txt` | Robots.txt |

Ver [`assets/endpoints.json`](./assets/endpoints.json) para el snapshot
completo de los 88 endpoints con descripcion.
