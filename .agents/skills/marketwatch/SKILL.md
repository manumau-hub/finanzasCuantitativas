---
name: marketwatch
description: "Scraper de MarketWatch: quotes, financials (income/balance/cash flow), SEC filings, analyst estimates, options chain, historical OHLCV. Sin API key."
license: MIT
---

# MarketWatch — Financial Data Scraper

Scraper de [MarketWatch](https://www.marketwatch.com/) que extrae **quotes en tiempo real**, **financial statements** (income, balance sheet, cash flow), **SEC filings**, **analyst estimates**, **options chain** y **historical prices** para acciones US y ADRs globales.

No requiere API key. Los datos se extraen del HTML de las páginas públicas.

---

## ⚠️ Aviso Legal

- MarketWatch **no tiene API pública oficial**. Este scraper accede a datos públicamente disponibles en la web.
- MarketWatch usa **Datadome** para protección anti-bot. El scraper utiliza headers de navegador completo para bypass.
- Respetá los **términos de servicio** de MarketWatch.
- Implementá **rate limiting** (mín 3 segundos entre requests, recomendado 5s).
- El sitio puede cambiar su estructura HTML, rompiendo el scraper.

---

## Instalación

```bash
pip install requests beautifulsoup4
```

---

## Scripts

| Script | Descripción |
|--------|-------------|
| **[fetch_marketwatch.py](./scripts/fetch_marketwatch.py)** | Script principal: todos los endpoints |

---

## Uso rápido

```bash
# Quote + perfil de compañía
python scripts/fetch_marketwatch.py --ticker AAPL --quote --profile

# Income statement anual (por defecto)
python scripts/fetch_marketwatch.py --ticker MSFT --income

# Income statement trimestral
python scripts/fetch_marketwatch.py --ticker AAPL --income --quarterly

# Balance sheet + cash flow trimestral
python scripts/fetch_marketwatch.py --ticker NVDA --balance --cashflow --quarterly

# Todos los financials (income + balance + cashflow)
python scripts/fetch_marketwatch.py --ticker AAPL --financials

# SEC filings (10-K, 10-Q, 8-K)
python scripts/fetch_marketwatch.py --ticker AAPL --sec-filings

# Analyst estimates + target price
python scripts/fetch_marketwatch.py --ticker AAPL --analyst

# Options chain
python scripts/fetch_marketwatch.py --ticker AAPL --options

# Historical OHLCV
python scripts/fetch_marketwatch.py --ticker AAPL --historical

# Todo lo disponible
python scripts/fetch_marketwatch.py --ticker GGAL --all

# A JSON
python scripts/fetch_marketwatch.py --ticker AAPL --all --output aapl.json

# Control de rate limiting
python scripts/fetch_marketwatch.py --ticker AAPL --quote --delay 5
```

---

## Endpoints disponibles

| Flag | Data | Frecuencia | Períodos |
|------|------|------------|----------|
| `--quote` | Precio, cambio, performance (5d, 1m, YTD) | Tiempo real | 1 snapshot |
| `--profile` | Ratios clave, sector, industria, empleados | Actual | 1 snapshot |
| `--income` | Income Statement | Anual / Trimestral | ~5 años |
| `--balance` | Balance Sheet | Anual / Trimestral | ~5 años |
| `--cashflow` | Cash Flow Statement | Anual / Trimestral | ~5 años |
| `--financials` | Income + Balance + Cash Flow (atajo) | Según `--quarterly` | ~5 años |
| `--sec-filings` | SEC filings (10-K, 10-Q, 8-K) | Histórico | ~20+ entradas |
| `--analyst` | Estimaciones, target price, recomendaciones | Trimestral/anual | ~15+ campos |
| `--options` | Options chain (calls/puts por strike) | Fechas de expiración | Todas disponibles |
| `--historical` | OHLCV histórico diario | Diario | ~1-3 meses |
| `--all` | Todos los anteriores | Según `--quarterly` | - |

---

## Datos disponibles por endpoint

### Quote
Precio actual, cambio ($), cambio (%), Close anterior, y tabla de performance (5 Day, 1 Month, 3 Month, YTD, 1 Year).

### Company Profile
Hasta 29 ratios financieros incluyendo:
P/E Current, P/E Ratio, EPS, Market Cap, Shares Outstanding, Revenue/Employee, Employees, Dividend Yield, Beta, etc.

### Financial Statements
Cada statement contiene ~40-60 items (Revenue, COGS, Gross Profit, Operating Income, Net Income, EBITDA, EPS, etc. para income; Cash, Receivables, Total Assets, Debt, Equity, etc. para balance sheet; Operating Cash Flow, Free Cash Flow, Capex, etc. para cash flow).

### SEC Filings
Listado de filings con: Filing Date, Document Date, Type (10-K, 10-Q, 8-K), Category.

### Analyst Estimates
Average Recommendation, Average Target Price, Number of Ratings, High/Median/Low target, Current/Next Year Estimates, y tabla de cambios de rating por firma.

### Options
Options chain organizada por fecha de expiración con calls y puts, strikes, precios, volumen, open interest.

### Historical
OHLCV diario con Date, Open, High, Low, Close, Volume (últimos ~60 días).

---

## Protección anti-bot (Datadome)

MarketWatch usa **Datadome** para protegerse de scraping automatizado.

| Situación | Síntoma | Solución |
|-----------|---------|----------|
| Muchos requests seguidos | 401 Unauthorized | Aumentar `--delay` (mín 3s, ideal 5s) |
| IP bloqueada temporalmente | 401 incluso con delay | Esperar 5-10 minutos |
| Headers incorrectos | 401 inmediato | Usar headers de navegador (ya incluidos) |
| Sin session cookies | 401 | El scraper maneja cookies automáticamente |

**Recomendación:** No más de 4-5 endpoints por ticker por ejecución.

---

## Estructura del skill

```
skills/marketwatch/
├── SKILL.md                              # Este archivo
├── references/
│   └── REFERENCE.md                      # Documentación completa de todos los endpoints
└── scripts/
    └── fetch_marketwatch.py              # Script principal
```

---

> **📖 Referencia completa:** Para entender en detalle cada endpoint, columnas de options, campos de financials, estructura de historical data, etc., consultá [references/REFERENCE.md](./references/REFERENCE.md).
