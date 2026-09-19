---
name: finviz
description: "Scraper de Finviz: datos fundamentales, técnicos, insider trading, news y screener para acciones US. Sin API oficial."
license: MIT
---

# Finviz — Scraper de Datos Financieros

Scraper de [Finviz](https://finviz.com/) que extrae datos **fundamentales** (P/E, EPS, PEG, márgenes, etc.), **técnicos** (RSI, MACD, SMA, ATR), **insider trading**, **noticias** y **screener** para acciones del mercado US.

Finviz no tiene API pública oficial. Este skill scrapea el HTML de las páginas públicas usando `requests` + `BeautifulSoup`.

---

## ⚠️ Aviso Legal

- Finviz **no tiene API pública oficial**. Este scraper accede a datos públicamente disponibles en la web.
- Respetá los **términos de servicio** de Finviz.
- Implementá **rate limiting** (mín 2 segundos entre requests).
- No uses este scraper para uso comercial sin verificar los ToS de Finviz.
- El sitio puede cambiar su estructura HTML, rompiendo el scraper.

---

## Instalación de dependencias

```bash
pip install requests beautifulsoup4
```

---

## Scripts

| Script | Descripción |
|--------|-------------|
| **[fetch_quote.py](./scripts/fetch_quote.py)** | Extrae perfil, fundamentales, técnicos, noticias e insider trading de un ticker. |

---

## Uso rápido

```bash
# Fetch completo de un ticker
python scripts/fetch_quote.py --ticker AAPL

# Solo fundamentales
python scripts/fetch_quote.py --ticker AAPL --fields fundamentals

# Output a archivo JSON
python scripts/fetch_quote.py --ticker MSFT --output msft_data.json

# Múltiples tickers
python scripts/fetch_quote.py --ticker AAPL,MSFT,GOOGL

# Headlines de noticias (default: 5)
python scripts/fetch_quote.py --ticker NVDA --news-headlines 10
```

---

## Campos extraídos del quote page

### Fundamentales

| Campo | Descripción |
|-------|-------------|
| `Market Cap` | Capitalización de mercado |
| `P/E` | Price-to-Earnings ratio |
| `Forward P/E` | Forward P/E |
| `PEG` | PEG ratio |
| `P/S` | Price-to-Sales |
| `P/B` | Price-to-Book |
| `EPS (ttm)` | Earnings Per Share (trailing 12 months) |
| `EPS next Y` | Estimated EPS next year |
| `Sales` | Revenue |
| `Profit Margin` | Profit margin |
| `ROE` | Return on Equity |
| `ROA` | Return on Assets |
| `Debt/Eq` | Debt-to-Equity |
| `Dividend %` | Dividend yield |
| `Insider Own` | Insider ownership |
| `Instit Own` | Institutional ownership |
| `Short Float` | Short float percentage |
| `Target Price` | Analyst target price |
| `Rating` | Analyst rating |

### Técnicos

| Campo | Descripción |
|-------|-------------|
| `RSI (14)` | Relative Strength Index |
| `SMA 20` | Simple Moving Average 20d |
| `SMA 50` | Simple Moving Average 50d |
| `SMA 200` | Simple Moving Average 200d |
| `MACD` | MACD value |
| `ATR` | Average True Range |
| `BB` | Bollinger Bands midpoint |
| `Volatility` | Volatility |
| `Beta` | Beta |

---

## Estructura del skill

```
skills/finviz/
├── SKILL.md                     # Este archivo
├── references/
│   └── QUOTE_REFERENCE.md       # Referencia de campos extraídos
└── scripts/
    └── fetch_quote.py           # Scraper principal
```
