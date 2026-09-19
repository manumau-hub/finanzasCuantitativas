---
name: macrotrends
description: "Scraper de Macrotrends: financial statements, ratios, employee count con 15+ años de data histórica. Sin API key."
license: MIT
---

# Macrotrends — Financial Data Scraper

Scraper de [Macrotrends](https://www.macrotrends.net/) que extrae datos financieros históricos: **income statements**, **balance sheets**, **cash flow statements**, **financial ratios** y **employee count** con hasta **15+ años de data** para **~6,500 tickers de mercados US** (NYSE, NASDAQ, AMEX), incluyendo **ADRs internacionales** de +30 países.

Los datos vienen en JSON embebido en la página (no requiere API key, solo `requests` + `BeautifulSoup`).

---

## ⚠️ Aviso Legal

- Macrotrends **no tiene API pública oficial**. Este scraper accede a datos públicamente disponibles en la web.
- Respetá los **términos de servicio** de Macrotrends.
- Implementá **rate limiting** (mín 2 segundos entre requests, recomendado 3s).
- El sitio puede cambiar su estructura HTML/JS, rompiendo el scraper.

---

## Instalación

```bash
pip install requests beautifulsoup4
```

---

## Scripts

| Script | Descripción |
|--------|-------------|
| **[fetch_financials.py](./scripts/fetch_financials.py)** | Script principal: statements, ratios, employees |

---

## Uso rápido

```bash
# Income statement anual
python scripts/fetch_financials.py --ticker NVDA --income

# Todo lo disponible (income + balance + cashflow + ratios + employees)
python scripts/fetch_financials.py --ticker AAPL --all

# Statements trimestrales
python scripts/fetch_financials.py --ticker MSFT --income --quarterly
python scripts/fetch_financials.py --ticker MSFT --balance --quarterly

# Ratios anuales o trimestrales
python scripts/fetch_financials.py --ticker NVDA --ratios
python scripts/fetch_financials.py --ticker GGAL --ratios --quarterly

# Employee count
python scripts/fetch_financials.py --ticker NVDA --employees

# Output a archivo JSON
python scripts/fetch_financials.py --ticker AAPL --all --output data.json

# Silencioso (solo JSON)
python scripts/fetch_financials.py --ticker NVDA --all --quiet
```

---

## Endpoints disponibles

| Flag | Data | Frecuencias | Períodos |
|------|------|-------------|----------|
| `--income` | Income Statement | Anual, Trimestral | ~15 años / ~60 quarters |
| `--balance` | Balance Sheet | Anual, Trimestral | ~15 años / ~60 quarters |
| `--cashflow` | Cash Flow | Solo anual | ~15 años |
| `--ratios` | Financial Ratios (20 ratios) | Anual, Trimestral | ~15 años / ~60 quarters |
| `--employees` | Employee Count | Anual | ~15 años |
| `--all` | Todos los anteriores | Según `--quarterly` | - |

### Flags adicionales

| Flag | Descripción |
|------|-------------|
| `--quarterly` | Usa frecuencia trimestral (donde esté disponible) |
| `--output` | Archivo JSON de salida (default: stdout) |
| `--slug` | Slug manual (si el search no funciona) |
| `--delay` | Delay entre requests (default: 3.0s) |
| `--quiet` | Modo silencioso |

---

## Resolución ticker → slug

Macrotrends usa URLs con el formato `/stocks/charts/{TICKER}/{SLUG}/financial-statements`.

El slug se resuelve automáticamente via el search endpoint interno. Ejemplos:

| Ticker | Slug |
|--------|------|
| AAPL | `apple` |
| NVDA | `nvidia` |
| MSFT | `microsoft` |
| GGAL | `grupo-financiero-galicia-sa` |
| TSLA | `tesla` |

Si el search falla, se puede pasar el slug manualmente:

```bash
python scripts/fetch_financials.py --ticker GGAL --slug grupo-financiero-galicia-sa --all
```

---

## Datos disponibles por statement

### Income Statement (22 campos)
Revenue, COGS, Gross Profit, R&D, SG&A, Operating Income, Net Income, EBITDA, EBIT, EPS, Shares Outstanding, etc.

### Balance Sheet (23 campos)
Cash, Receivables, Inventory, Total Assets, Total Liabilities, Shareholders Equity, Debt, Retained Earnings, etc.

### Cash Flow (29 campos)
Net Income, Depreciation, Working Capital Changes, Capex, Free Cash Flow, Dividends, Stock Repurchases, etc.

### Financial Ratios (20 ratios)
Current Ratio, Debt/Equity, Gross/Operating/Net Margins, ROE, ROA, ROI, Book Value/Share, FCF/Share, etc.

### Employee Count
Año a año, empleados totales.

Ver referencia completa de campos en [references/STATEMENTS_REFERENCE.md](./references/STATEMENTS_REFERENCE.md).

---

## Cobertura de Mercados

Macrotrends cubre **~6,500 tickers** que cotizan en **NYSE, NASDAQ y AMEX** (incluyendo ADRs).

| Tipo | Cantidad | Ejemplos |
|------|:--------:|----------|
| US Common Stocks | ~5,300 | AAPL, NVDA, MSFT |
| ADRs Internacionales | ~276+ | **GGAL** (Argentina), **BABA** (China), **TM** (Japón), **PBR** (Brasil), **SAN** (España), **BP** (UK) |
| ETFs & Fondos | ~91 | SPY, QQQ, VTI |
| Class A/B Shares | ~22 | BRK.A, BRK.B |

Ver detalle completo de mercados, ADRs por país y cómo buscar tickers en [references/MARKETS_REFERENCE.md](./references/MARKETS_REFERENCE.md).

---

## Rate Limits

| Comportamiento | Recomendación |
|----------------|---------------|
| Requests seguidos sin delay | 429 Too Many Requests |
| Delay recomendado | 3 segundos entre requests |
| Tickers por ejecución | ~5-6 como máximo (para evitar bloqueo) |
| Backoff | Si recibís 429, esperá 30-60s |

---

## Errores comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `429 Too Many Requests` | Rate limit | Aumentar `--delay` o esperar |
| `slug not found` | No se pudo resolver el ticker | Usar `--slug` manualmente |
| `No data found for X` | Endpoint no disponible | Verificar que el ticker existe en Macrotrends |
| `originalData not found` | Página cambió estructura | Reportar issue |

---

## Estructura del skill

```
skills/macrotrends/
├── SKILL.md                              # Este archivo
├── references/
│   ├── STATEMENTS_REFERENCE.md           # Referencia de campos
│   └── MARKETS_REFERENCE.md             # Cobertura de mercados y ADRs
└── scripts/
    └── fetch_financials.py               # Script principal
```
