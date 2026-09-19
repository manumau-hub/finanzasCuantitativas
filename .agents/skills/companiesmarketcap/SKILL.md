---
name: companiesmarketcap
description: "Scraper de CompaniesMarketCap: rankings (marketcap, earnings, revenue, employees, ratios), stock history y ETF holdings. Sin API key."
license: MIT
---

# CompaniesMarketCap — Financial Rankings Scraper

Scraper de [CompaniesMarketCap](https://companiesmarketcap.com/) que extrae **rankings financieros** (market cap, earnings, revenue, employees, P/E, márgenes, activos, deuda, cash), **marketcap histórico de stocks** y **ETF holdings**.

Usa el sistema de **CSV download** nativo del sitio (`?download=csv`) — no requiere API key y es más mantenible que scrapear HTML.

---

## ⚠️ Aviso Legal

- CompaniesMarketCap **no tiene API pública oficial**. Usa el endpoint CSV que está públicamente disponible.
- Respetá los **términos de servicio** del sitio.
- Implementá **rate limiting** (mín 2 segundos entre requests).

---

## Instalación

```bash
pip install requests beautifulsoup4
```

---

## Scripts

| Script | Descripción |
|--------|-------------|
| **[fetch_cmc.py](./scripts/fetch_cmc.py)** | Script principal: rankings, stock history, ETF holdings |

---

## Uso rápido

```bash
# Ranking de market cap (default)
python scripts/fetch_cmc.py --rankings

# Ranking de earnings
python scripts/fetch_cmc.py --rankings --metric earnings

# Ranking de revenue (top 10)
python scripts/fetch_cmc.py --rankings --metric revenue --limit 10

# Stock marketcap histórico
python scripts/fetch_cmc.py --stock NVDA
python scripts/fetch_cmc.py --stock GGAL

# ETF holdings
python scripts/fetch_cmc.py --etf SPY --holdings

# Todo junto + output a JSON
python scripts/fetch_cmc.py --stock AAPL --rankings --output aapl_full.json

# Modo silencioso (solo JSON)
python scripts/fetch_cmc.py --rankings --metric earnings --limit 5 --quiet
```

---

## Endpoints

| Flag | Data | Método | Detalle |
|------|------|--------|---------|
| `--rankings` | Ranking list | CSV download | 12 métricas + ETFs, ~10,852 empresas |
| `--stock TICKER` | Marketcap histórico | HTML | 28-31 años por stock |
| `--etf TICKER --holdings` | ETF holdings | HTML | ~505 posiciones (SPY) |
| `--etf TICKER` | ETF summary | HTML | Información del ETF |

### Rankings disponibles (`--metric`)

| Métrica | Descripción |
|---------|-------------|
| `marketcap` (default) | Market Capitalization |
| `earnings` | Earnings (TTM) |
| `revenue` | Revenue (TTM) |
| `employees` | Employee count |
| `pe_ratio` | Price/Earnings ratio |
| `operating_margin` | Operating margin (TTM) |
| `total_assets` | Total assets |
| `net_assets` | Net assets |
| `liabilities` | Total liabilities |
| `debt` | Total debt |
| `cash` | Cash on hand |
| `pb_ratio` | Price/Book ratio |
| `etfs` | ETF market caps |

---

## Flags adicionales

| Flag | Descripción |
|------|-------------|
| `--limit N` | Limitar a N filas en rankings |
| `--output archivo.json` | Guardar output a archivo |
| `--delay N` | Delay entre requests (default: 2.0s) |
| `--quiet` | Modo silencioso (solo JSON) |

---

## Resolución automática ticker → slug

El scraper resuelve automáticamente el slug de la URL a partir del nombre de la compañía en el CSV:

| Ticker | Nombre → Slug |
|--------|---------------|
| NVDA | NVIDIA → `nvidia` |
| AAPL | Apple → `apple` |
| GGAL | Galicia Financial Group → `galicia-financial-group` |
| SPY | SPDR S&P 500 ETF → `spdr-sp-500-etf` |
| BRK-B | Berkshire Hathaway → `berkshire-hathaway` |

---

## Estructura del skill

```
skills/companiesmarketcap/
├── SKILL.md                              # Este archivo
├── references/
│   └── REFERENCE.md                      # Documentación completa
└── scripts/
    └── fetch_cmc.py                      # Script principal
```

---

> **📖 Documentación detallada:** Consultá [references/REFERENCE.md](./references/REFERENCE.md) para la documentación exhaustiva de cada endpoint, columnas, ejemplos y consideraciones técnicas.
