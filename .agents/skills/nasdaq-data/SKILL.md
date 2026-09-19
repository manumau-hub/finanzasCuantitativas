---
name: nasdaq-data
description: "Scraper de datos de Nasdaq.com via API REST interna: cotizaciones, short interest, financials, institutional holdings, opciones, noticias. Sin API key."
license: MIT
---

# Nasdaq — Datos de Mercado via API Interna

Skill para extraer datos de [Nasdaq.com](https://www.nasdaq.com/market-activity/stocks) usando sus **APIs REST internas** — sin API key, sin autenticacion, sin rate limiting agresivo.

---

## ⚠️ Aviso Legal

- Nasdaq **no tiene API publica oficial** gratuita. Estos endpoints son **internos** y pueden cambiar sin aviso.
- Implementar **rate limiting** (minimo 0.3s entre requests).
- Respetar los **terminos de servicio** del sitio.

---

## Instalacion

El script usa `requests` (ya disponible en el entorno).

---

## Scripts

| Script | Descripcion |
|--------|-------------|
| **[fetch_nasdaq.py](./scripts/fetch_nasdaq.py)** | Script principal: todos los endpoints disponibles |

---

## Uso rapido

```bash
# Informacion de la empresa + precio
python scripts/fetch_nasdaq.py info NVDA
python scripts/fetch_nasdaq.py info GGAL

# Short interest historico
python scripts/fetch_nasdaq.py short-interest GGAL

# Chart OHLCV (ultimo año por defecto)
python scripts/fetch_nasdaq.py chart NVDA
python scripts/fetch_nasdaq.py chart NVDA --from 2025-01-01 --to 2026-06-04

# Estados financieros (Income Statement, Balance Sheet, Cash Flow, Ratios)
python scripts/fetch_nasdaq.py financials NVDA

# Institutional holdings (13F)
python scripts/fetch_nasdaq.py institutional-holdings NVDA

# ETFs donde el stock es Top 10 Holding
python scripts/fetch_nasdaq.py holdings NVDA
python scripts/fetch_nasdaq.py holdings GGAL

# Top 10 Holdings de un ETF
python scripts/fetch_nasdaq.py etf-holdings SPY
python scripts/fetch_nasdaq.py etf-holdings QQQ

# Perfil de la empresa
python scripts/fetch_nasdaq.py company-profile AAPL

# Dividendos
python scripts/fetch_nasdaq.py dividends NVDA
python scripts/fetch_nasdaq.py eps NVDA                  # EPS histórico + upcoming

# Insider trading
python scripts/fetch_nasdaq.py insider-trades NVDA       # Summary 3/12m + transacciones
python scripts/fetch_nasdaq.py insider-trades NVDA --type buy
python scripts/fetch_nasdaq.py insider-trades NVDA --type sell
python scripts/fetch_nasdaq.py insider-trades NVDA --limit 20

# Opciones
python scripts/fetch_nasdaq.py option-chain NVDA

# Ultimas noticias
python scripts/fetch_nasdaq.py news NVDA --limit 5

# Screener de acciones
python scripts/fetch_nasdaq.py screener --exchange nasdaq --limit 10

# Screener de ETFs (4551 ETFs listados)
python scripts/fetch_nasdaq.py screener-etf --limit 5

# Calendarios globales
python scripts/fetch_nasdaq.py ipo-calendar                        # IPO upcoming (mes actual)
python scripts/fetch_nasdaq.py ipo-calendar --type spo             # SPO: secondary offerings
python scripts/fetch_nasdaq.py ipo-calendar --date 2026-05         # IPOs de Mayo 2026
python scripts/fetch_nasdaq.py ipo-calendar --type spo --date 2026-06  # SPOs de Junio 2026
python scripts/fetch_nasdaq.py earnings-calendar                   # Earnings hoy
python scripts/fetch_nasdaq.py earnings-calendar --date 2026-06-05 # Earnings de una fecha especifica
python scripts/fetch_nasdaq.py economic-calendar                   # Economic calendar (hoy)
python scripts/fetch_nasdaq.py economic-calendar --date 2026-06-04 # Economic calendar de una fecha
python scripts/fetch_nasdaq.py dividend-calendar                   # Dividendos hoy
python scripts/fetch_nasdaq.py dividend-calendar --date 2026-06-04 # Dividendos de una fecha
python scripts/fetch_nasdaq.py splits-calendar                     # Stock splits

# TODO: todos los endpoints en uno
python scripts/fetch_nasdaq.py all GGAL
python scripts/fetch_nasdaq.py all NVDA -o nvda_all.json

# Modo silencioso (solo JSON)
python scripts/fetch_nasdaq.py info AAPL -q
python scripts/fetch_nasdaq.py all MSFT -o msft.json -q
```

---

## Endpoints disponibles

| Modo | Data | Metodo | Endpoint Interno |
|------|------|--------|------------------|
| `info` | Cotizacion, precio, key stats | API REST | `/api/quote/{ticker}/info` |
| `short-interest` | Short interest historico | API REST | `/api/quote/{ticker}/short-interest` |
| `chart` | OHLCV historico | API REST | `/api/quote/{ticker}/chart` |
| `financials` | Income Statement, BS, CF, Ratios | API REST | `/api/company/{ticker}/financials` |
| `institutional-holdings` | Tenencias institucionales (13F) | API REST | `/api/company/{ticker}/institutional-holdings` |
| `holdings` | ETFs donde el stock es Top 10 Holding | API REST | `/api/company/{ticker}/holdings` |
| `etf-holdings` | Top 10 Holdings de un ETF | API REST | `/api/company/{ticker}/holdings` |
| `company-profile` | Descripcion, sector, direccion | API REST | `/api/company/{ticker}/company-profile` |
| `dividends` | Dividendos | API REST | `/api/quote/{ticker}/dividends` |
| `eps` | EPS historico + upcoming por ticker | API REST | `/api/quote/{ticker}/eps` |
| `insider-trades` | Insider trading: summary 3/12m + transacciones | API REST | `/api/company/{ticker}/insider-trades` |
| `option-chain` | Cadena de opciones | API REST | `/api/quote/{ticker}/option-chain` |
| `news` | Ultimas noticias | API REST | `/api/news/topic/articlebysymbol` |
| `screener` | Screener de acciones | API REST | `/api/screener/stocks` |
| `screener-etf` | Screener de ETFs | API REST | `/api/screener/etf` |
| `ipo-calendar` | IPO + SPO calendar | API REST | `/api/ipo/calendar` |
| `earnings-calendar` | Earnings calendar con EPS | API REST | `/api/calendar/earnings` |
| `economic-calendar` | Economic events (actual, consensus, previous) | API REST | `/api/calendar/economicevents` |
| `dividend-calendar` | Dividendos (ex-date, pay-date, rate) | API REST | `/api/calendar/dividends` |
| `splits-calendar` | Stock splits | API REST | `/api/calendar/splits` |
| `all` | Todos los anteriores combinados | - | - |

---

## Flags adicionales

| Flag | Descripcion |
|------|-------------|
| `--from YYYY-MM-DD` | Fecha inicio para chart |
| `--to YYYY-MM-DD` | Fecha fin para chart |
| `--limit N` | Limite de resultados (news, screener) |
| `--offset N` | Offset para paginacion (screener) |
| `--exchange X` | Exchange para screener (default: nasdaq) |
| `--type ipo\|spo\|all\|buy\|sell` | Tipo: ipo/spo (ipo-calendar) o all/buy/sell (insider-trades) |
| `--date YYYY-MM\|DD` | Fecha para calendarios: YYYY-MM (ipo) o YYYY-MM-DD (earnings/dividend) |
| `-o archivo.json` | Guardar output a archivo |
| `-q` / `--quiet` | Modo silencioso (solo JSON) |

---

## Rate limiting

| Delay | Resultado |
|-------|-----------|
| <0.2s | Riesgo de 429/baneo |
| 0.3s | ✅ Seguro (default en `--all`) |
| 1s+ | ✅ Ideal para multiples requests |

---

## Endpoints NO disponibles via API

Los siguientes datos **no tienen endpoint JSON interno** y requeririan scraping HTML:

| Pagina | Estado | Alternativa |
|--------|--------|-------------|
| Holiday Schedule | ❌ No hay API interna detectada | Solo HTML |
| ETF Detail (AUM, fees, desc) | ❌ No hay API interna | Usar `companiesmarketcap --etf TICKER` |

---

## Estructura del skill

```
skills/nasdaq-data/
├── SKILL.md                          # Este archivo (guia rapida)
├── references/
│   └── REFERENCE.md                  # Documentacion completa de todos los endpoints
└── scripts/
    └── fetch_nasdaq.py               # Script principal
```

---

> **Documentacion detallada:** Consultar [references/REFERENCE.md](./references/REFERENCE.md) para la documentacion exhaustiva de cada endpoint, estructuras JSON, ejemplos y consideraciones tecnicas.
