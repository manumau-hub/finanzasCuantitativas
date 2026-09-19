---
name: tradingview
description: "Datos de mercado de TradingView via APIs publicas internas sin auth: Scanner (~300 columnas con quote/indicadores tecnicos/financials/earnings/ratings/targets), Symbol Search v3 (ISIN/CUSIP/CIK), News Headlines, scraping HTML de subpages (technicals/financials/forecast/options/ideas). Cobertura GLOBAL: 100k+ stocks, 50k+ cryptos, indices, forex, bonos. 24 modos CLI."
license: MIT
---

# TradingView — Market Data via APIs Publicas

Skill **premium** para extraer datos de mercado de [TradingView](https://www.tradingview.com)
via sus **APIs publicas internas** descubiertas por reverse-engineering — **sin
API key, sin autenticacion**.

TradingView es la plataforma de market data + analisis tecnico + social
trading mas usada del mundo (>50M usuarios activos). Este skill expone:

- **Scanner API** con ~300 columnas: quote, indicadores tecnicos pre-calculados,
  fundamentals, earnings, analyst targets, ratings BUY/SELL agregados.
- **Symbol Search v3** con **ISIN, CUSIP, CIK** (joineable con SEC EDGAR).
- **News Headlines** (~200 noticias por simbolo, Dow Jones / Reuters / etc.).
- **HTML scraping** de 16+ subpages (`technicals`, `financials-*`, `forecast`,
  `options-chain`, `ideas`, etc.) con extraccion de `prs.init-data+json`.
- **Screener masivo** con filtros + sort + paginacion (~100k+ instrumentos).

---

## ⚠️ Aviso Legal

- TradingView **NO publica documentacion oficial** de estas APIs. Pueden cambiar sin aviso.
- En **~6 años** de tracking comunitario los cambios han sido graduales — la estructura del Scanner es estable desde 2017+.
- Respetar terminos de uso. Para uso comercial intensivo, contratar la **REST API oficial** (de pago).
- Los datos son **delayed** (~15 min tipico). Real-time va por WebSockets propietarios (no implementados aqui).

---

## 🚀 Quick start

```bash
# Quote rapido
py scripts/fetch_tradingview.py quote NASDAQ:GGAL

# Todo-en-uno (6 requests combinadas)
py scripts/fetch_tradingview.py all NASDAQ:GGAL

# Screener masivo
py scripts/fetch_tradingview.py country Argentina --limit 30
py scripts/fetch_tradingview.py sector Finance --market america --limit 20

# News (~200 por simbolo)
py scripts/fetch_tradingview.py news NASDAQ:AAPL

# Symbol Search con ISIN/CUSIP/CIK
py scripts/fetch_tradingview.py search "Galicia"
```

---

## Estructura del skill

```
skills/tradingview/
├── SKILL.md                              # Este archivo (guia rapida)
├── references/                           # 8 documentos detallados
│   ├── REFERENCE.md                      # Overview general de la API
│   ├── SCANNER_COLUMNS.md                # Catalogo de 130+ columnas con tablas
│   ├── SCANNER_FILTERS.md                # Operaciones de filtro + queries complejos
│   ├── MARKETS_EXCHANGES.md              # Mercados validos + exchanges por pais
│   ├── NEWS_API.md                       # News API deep dive
│   ├── SYMBOL_SEARCH.md                  # Symbol Search v3 deep dive
│   ├── HTML_SCRAPING.md                  # Extraccion de prs.init-data+json
│   └── COOKBOOK.md                       # 30 recetas listas para copy-paste
├── assets/                               # 4 archivos JSON
│   ├── scanner_columns.json              # Catalogo de columnas con descripciones
│   ├── column_groups.json                # Bundles pre-armados por caso de uso
│   ├── markets.json                      # Mercados validos + cobertura
│   └── recommend_ratings.json            # Mapeo Recommend.* a STRONG_BUY/etc
└── scripts/
    └── fetch_tradingview.py              # Script principal con 24 modos CLI
```

---

## Endpoints disponibles (4 HTTP unicos, 24 modos CLI)

### Scanner API (1 endpoint, 14 modos CLI)

`POST https://scanner.tradingview.com/{market}/scan`

| Modo | Bundle de columnas | Descripcion |
|------|-------------------|-------------|
| `quote SYM` | `quote_basic` (14 cols) | Quote basico |
| `quote-extended SYM` | `quote_extended` (30 cols) | Quote + indicadores + valuacion |
| `technicals SYM` | `technicals` (36 cols) | RSI, MACD, EMAs, SMAs, ratings |
| `pivots SYM` | `pivots` (17 cols) | Pivots mensuales (5 metodos) |
| `financials SYM` | `financials` (35 cols) | Balance + income + cashflow + ratios |
| `earnings SYM` | `earnings` (12 cols) | Earnings pasados + forecast |
| `targets SYM` | `targets` (10 cols) | Price targets + analyst recommendations |
| `performance SYM` | `performance` (18 cols) | Returns (W/1M/3M/6M/Y/YTD/5Y/All) + volatilidad + beta |
| `dividends SYM` | `dividends` (8 cols) | Yield + DPS + payout + crecimiento |
| `ownership SYM` | `ownership` (10 cols) | Float + institucional + insiders + short |
| `screen` | custom | Screener generico con filtros + sort + paginacion |
| `country COUNTRY` | `quote_basic` | Stocks de un pais |
| `sector SECTOR` | `quote_basic` | Stocks de un sector |
| `market MARKET` | `quote_basic` | Listar mercado completo |

### Symbol Search v3 (1 endpoint, 1 modo)

`GET https://symbol-search.tradingview.com/symbol_search/v3/`

| Modo | Descripcion |
|------|-------------|
| `search QUERY` | Busqueda global con ISIN, CUSIP, CIK, logoid, exchange |

### News API (1 endpoint, 3 modos)

`GET https://news-headlines.tradingview.com/v2/headlines`

| Modo | Descripcion |
|------|-------------|
| `news SYM` | Headlines de un simbolo (hasta 200 items) |
| `news-global` | Headlines globales del mercado (hasta 200 items) |
| `story STORY_PATH` | Detalle/body de una noticia (scraping HTML) |

### HTML Scraping (1 endpoint, 1 modo)

`GET https://es.tradingview.com/symbols/{EX}-{SYM}/{path}/`

| Modo | Descripcion |
|------|-------------|
| `subpage SYM PATH` | Fetch HTML + extrae bloques `prs.init-data+json` |

### Catalogos locales (3 modos)

| Modo | Descripcion |
|------|-------------|
| `columns [GROUP]` | Listar columnas (todas o un grupo concreto) |
| `groups` | Listar bundles pre-armados |
| `markets` | Listar mercados validos |

### Combinado (1 modo)

| Modo | Descripcion |
|------|-------------|
| `all SYM` | Combina 6 requests (quote_extended + technicals + financials + earnings + targets + news) |

---

## Uso rapido — ejemplos por categoria

### Quote y tecnicos

```bash
py scripts/fetch_tradingview.py quote NASDAQ:GGAL                  # 14 cols
py scripts/fetch_tradingview.py quote-extended NASDAQ:AAPL         # 30 cols
py scripts/fetch_tradingview.py technicals NASDAQ:GGAL             # 36 cols
py scripts/fetch_tradingview.py pivots NASDAQ:AAPL                 # 17 cols
py scripts/fetch_tradingview.py performance NYSE:JPM               # returns W/1M/3M/6M/Y/YTD/5Y/All
```

### Financials

```bash
py scripts/fetch_tradingview.py financials NASDAQ:AAPL             # balance + income + cashflow + ratios
py scripts/fetch_tradingview.py earnings NASDAQ:GGAL               # past + forecast
py scripts/fetch_tradingview.py targets NASDAQ:NVDA                # analyst targets + recos
py scripts/fetch_tradingview.py dividends NYSE:KO                  # yield + DPS + payout
py scripts/fetch_tradingview.py ownership NASDAQ:NVDA              # float + inst + insiders + short
```

### Screening

```bash
# Filtros arbitrarios — pasar JSON con la sintaxis del Scanner
py scripts/fetch_tradingview.py screen \
  --filter '[["sector","equal","Finance"],["market_cap_basic","greater",100000000000]]' \
  --sort market_cap_basic:desc --limit 10

# Atajos
py scripts/fetch_tradingview.py country Argentina --limit 30
py scripts/fetch_tradingview.py sector Finance --market america --limit 20
py scripts/fetch_tradingview.py market crypto --limit 20
```

### Symbol Search

```bash
py scripts/fetch_tradingview.py search "GGAL"                                       # auto type
py scripts/fetch_tradingview.py search "Apple" --type stocks --exchange NASDAQ
py scripts/fetch_tradingview.py search "BTC" --type crypto
py scripts/fetch_tradingview.py search "US3999091008"                                # por ISIN
```

### News

```bash
py scripts/fetch_tradingview.py news NASDAQ:AAPL                   # hasta 200 items
py scripts/fetch_tradingview.py news-global                        # global headlines
py scripts/fetch_tradingview.py story "/news/DJN_DN20260604009289:0/"  # body de noticia
```

### HTML scraping

```bash
py scripts/fetch_tradingview.py subpage NASDAQ:GGAL technicals     # subpage HTML
py scripts/fetch_tradingview.py subpage NASDAQ:GGAL financials-income-statement
py scripts/fetch_tradingview.py subpage NASDAQ:GGAL options-chain
py scripts/fetch_tradingview.py subpage NASDAQ:GGAL forecast
```

### Catalogos

```bash
py scripts/fetch_tradingview.py columns                            # todas las columnas
py scripts/fetch_tradingview.py columns technicals                 # un grupo
py scripts/fetch_tradingview.py groups                             # todos los bundles
py scripts/fetch_tradingview.py markets                            # mercados validos
```

### Combinado

```bash
py scripts/fetch_tradingview.py all NASDAQ:GGAL                    # 6 requests en 1
py scripts/fetch_tradingview.py all NASDAQ:GGAL -o ggal_full.json  # guarda a archivo
```

### Custom columns

```bash
py scripts/fetch_tradingview.py quote NASDAQ:GGAL \
  --columns "name,close,RSI,MACD.macd,Recommend.All,price_target_average"
```

### Output / silencio

```bash
py scripts/fetch_tradingview.py quote NASDAQ:GGAL -o ggal_quote.json   # archivo
py scripts/fetch_tradingview.py quote NASDAQ:GGAL -q                    # silencioso
```

---

## Formato de simbolos

| Donde | Formato | Ejemplos |
|-------|---------|----------|
| Scanner / News / Search (JSON APIs) | `{EXCHANGE}:{TICKER}` | `NASDAQ:GGAL`, `BCBA:YPF`, `BINANCE:BTCUSDT` |
| HTML subpages | `{EXCHANGE}-{TICKER}` | `NASDAQ-GGAL` (en URL) |

Conversion automatica: el script convierte `:` → `-` cuando arma URLs HTML.

---

## Markets soportados

| Market | Cobertura | Tickers tipo |
|--------|-----------|--------------|
| `global` | Todos los mercados (100k+) | Cualquier `EX:TKR` |
| `america` | US: NYSE, NASDAQ, AMEX, OTC (15k+) | `NASDAQ:AAPL` |
| `argentina` | BCBA / BYMA (300+) | `BCBA:GGAL` |
| `brazil` | B3 / Bovespa (500+) | `BMFBOVESPA:PETR4` |
| `spain` | BME (200+) | `BME:SAN` |
| `italy` | Borsa Italiana (400+) | `MIL:ENI` |
| `germany` | Xetra / FWB (1k+) | `XETR:SAP` |
| `uk` | LSE (2k+) | `LSE:HSBA` |
| `france` | Euronext Paris (800+) | `EURONEXT:MC` |
| `russia` | MOEX (200+) | `MOEX:SBER` |
| `crypto` | Cryptos (50k+) | `BINANCE:BTCUSDT` |
| `forex` | Forex pairs (1k+) | `FX:EURUSD` |
| `bonds` | Bonos globales (TVC) | `TVC:US10Y` |

> Detalles completos en [references/MARKETS_EXCHANGES.md](./references/MARKETS_EXCHANGES.md).

---

## Tipos de instrumento (`type` field)

| Tipo | Descripcion |
|------|-------------|
| `stock` | Acciones comunes |
| `dr` | Depositary Receipt (ADRs en US, CEDEARs en BCBA, BDRs en BMFBOVESPA) |
| `etf` | Exchange-Traded Fund |
| `fund` | Mutual fund |
| `structured` | Producto estructurado |
| `bond` | Bono |
| `crypto` | Criptomoneda |
| `forex` | Par de monedas |
| `index` | Indice |
| `future` | Futuro |
| `option` | Opcion |

---

## Ratings BUY/SELL (Recommend.*)

TradingView calcula 3 ratings agregados a partir de los indicadores:

| Campo | Calculado a partir de |
|-------|----------------------|
| `Recommend.All` | TODOS los indicadores (medias moviles + osciladores) |
| `Recommend.MA` | Solo medias moviles (SMA/EMA 10..200, VWMA, Ichimoku, HullMA) |
| `Recommend.Other` | Solo osciladores (RSI, Stoch, MACD, ADX, CCI, BBP, UO, W%R, AO) |

Valores en `[-1.0, +1.0]`. Mapeo a buckets:

| Rango | Bucket | UI label |
|-------|--------|----------|
| -1.00 a -0.50 | `STRONG_SELL` | Venta fuerte |
| -0.50 a -0.10 | `SELL` | Venta |
| -0.10 a +0.10 | `NEUTRAL` | Neutral |
| +0.10 a +0.50 | `BUY` | Compra |
| +0.50 a +1.00 | `STRONG_BUY` | Compra fuerte |

> El script tiene `recommend_label(value)` para conversion directa.
> Asset estructurado en [assets/recommend_ratings.json](./assets/recommend_ratings.json).

---

## Flags principales

| Flag | Descripcion |
|------|-------------|
| `--market X` | Market del Scanner (default: `global`) |
| `--columns "a,b,c"` | Columnas custom (override del bundle del modo) |
| `--filter '[...]'` | Filtro JSON para `screen` (ver [SCANNER_FILTERS.md](./references/SCANNER_FILTERS.md)) |
| `--sort field:order` | Sort (ej: `market_cap_basic:desc`) |
| `--limit N` | Limite de resultados (default: 30) |
| `--offset N` | Offset para paginacion (default: 0) |
| `--type X` | search_type para `search` (`stocks`, `crypto`, `forex`, etc.) |
| `--exchange X` | Filtro exchange para `search` |
| `--lang X` | Idioma para news/search (default: `en`) |
| `-o archivo` | Guardar output a archivo (JSON o markdown) |
| `-q` / `--quiet` | Modo silencioso (sin logs INFO) |

---

## Diferencial vs otros skills del repo

| Feature | TradingView | Yahoo Finance | Finnhub | Investing.com | Morningstar |
|---------|:-----------:|:-------------:|:-------:|:-------------:|:-----------:|
| API publica sin key | ✅ | ✅ | Freemium | ✅ | ✅ |
| Quote real-time | ⚠️ delayed | ⚠️ delayed | ✅ | ⚠️ delayed | ❌ |
| **Indicadores tecnicos pre-calc (~30+)** | ✅ **UNICO** | ❌ | ❌ | ❌ | ❌ |
| **Ratings BUY/SELL agregados** | ✅ **UNICO** | ❌ | ⚠️ | ⚠️ | ❌ |
| **Pivots S/R (5 metodos)** | ✅ **UNICO** | ❌ | ❌ | ❌ | ❌ |
| Financials | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Analyst targets | ✅ | ⚠️ | ✅ | ✅ | ❌ |
| **ISIN/CUSIP/CIK en search** | ✅ **UNICO** | ❌ | ⚠️ | ❌ | ❌ |
| Screener multi-pais | ✅ (~100k+) | ⚠️ | ⚠️ | ⚠️ | ✅ |
| News | ✅ (200 items) | ✅ | ✅ | ✅ | ❌ |
| Cobertura cryptos | ✅ (50k+) | ⚠️ | ⚠️ | ✅ | ❌ |

**Ventajas unicas de TradingView:**
1. **Indicadores tecnicos pre-calculados** del lado servidor (RSI, MACD, EMAs, ratings) — no hay que calcular nada cliente-side.
2. **Pivots mensuales con 5 metodos** (Classic, Fibonacci, Camarilla, Woodie, DeMark).
3. **Symbol Search con ISIN/CUSIP/CIK** — directamente joineable con SEC EDGAR.
4. **Screener masivo** con filtros tipo SQL sobre 100k+ instrumentos en un sola request.

**Cuando NO usar TradingView:**
- News para stocks chicos no-US → mejor Yahoo Finance.
- Real-time tick-by-tick → requiere WebSocket (no implementado).
- Datos historicos OHLCV largos → no expone REST publico; usar Alpha Vantage o Yahoo Finance.
- Fundamentals con multiples periodos (5 años de income statements) → mejor SEC EDGAR para US, simplywallst para coverage global.

---

## Consideraciones tecnicas

### Sin auth

Ningun endpoint requiere API key, token, cookie ni session ID. Funciona
desde scripts headless, CI/CD, Docker, etc.

### Headers recomendados

Ya configurados en el script:

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 ...",
    "Accept": "*/*",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Origin": "https://es.tradingview.com",
    "Referer": "https://es.tradingview.com/",
}
```

### Rate limiting

No documentado. Observado:
- **Scanner**: tolera ~5 req/s.
- **News**: ~3 req/s.
- **Symbol Search**: ~5 req/s.
- **HTML subpages**: ~1 req/s (WAF de CloudFlare).

Recomendacion: `time.sleep(0.3)` entre requests. El modo `all` lo usa automaticamente.

### Encoding

UTF-8 valido. En consolas Windows (cp1252) pueden aparecer `?` en lugar
de caracteres especiales. El script reconfigura `sys.stdout` a UTF-8
automaticamente al inicio.

### Manejo de errores

| Status | Causa tipica |
|--------|--------------|
| 200 | OK. Para Scanner verificar `totalCount > 0`. |
| 400 | Payload invalido (columna desconocida, filter mal formado, body null) |
| 403 | Path inexistente o headers faltantes |
| 404 | Subpage HTML que no existe (ej: `/news/`) |
| 405 | Metodo erroneo (ej: `/v3/headlines` GET no existe, solo v2) |

### Limitaciones conocidas

1. **No hay endpoint OHLCV historico via REST**: solo `Perf.*` returns en el Scanner. Para historicos largos usar otros skills.
2. **News con coverage desigual**: stocks grandes US = 200 items, stocks chicos = 1-5.
3. **`lang=es` en news**: casi vacio. Usar `lang=en` por defecto.
4. **WebSocket real-time no implementado** (`wss://data.tradingview.com`).
5. **Argentina market**: `BCBA:GGAL` para argentina, `NASDAQ:GGAL` para america — NO intercambiables.

### Aviso comercial

- API no documentada → puede cambiar.
- **No abusar**: respetar rate limits razonables.
- Para uso comercial intensivo, contratar la TradingView REST API oficial (de pago).

---

## Documentacion completa

| Documento | Contenido |
|-----------|-----------|
| [references/REFERENCE.md](./references/REFERENCE.md) | Overview general de los 4 endpoints HTTP + arquitectura |
| [references/SCANNER_COLUMNS.md](./references/SCANNER_COLUMNS.md) | Lista exhaustiva de 130+ columnas con tablas |
| [references/SCANNER_FILTERS.md](./references/SCANNER_FILTERS.md) | Operaciones de filtro + queries complejos + ejemplos |
| [references/MARKETS_EXCHANGES.md](./references/MARKETS_EXCHANGES.md) | Mercados validos + exchanges por pais + formato tickers |
| [references/NEWS_API.md](./references/NEWS_API.md) | News API deep dive: providers, schema, story detail |
| [references/SYMBOL_SEARCH.md](./references/SYMBOL_SEARCH.md) | Symbol Search v3 deep dive: ISIN/CUSIP/CIK |
| [references/HTML_SCRAPING.md](./references/HTML_SCRAPING.md) | Extraccion de prs.init-data+json + casos donde scrapear |
| [references/COOKBOOK.md](./references/COOKBOOK.md) | **30 recetas listas para copy-paste** |
| [assets/scanner_columns.json](./assets/scanner_columns.json) | Catalogo de columnas con descripciones |
| [assets/column_groups.json](./assets/column_groups.json) | Bundles pre-armados por caso de uso |
| [assets/markets.json](./assets/markets.json) | Mercados validos + cobertura |
| [assets/recommend_ratings.json](./assets/recommend_ratings.json) | Mapeo Recommend.* a buckets |

---

## Casos de uso destacados

> **30 recetas completas en [references/COOKBOOK.md](./references/COOKBOOK.md).**

```bash
# Top 10 acciones US por market cap
py scripts/fetch_tradingview.py screen \
  --filter '[["country","equal","United States"],["type","equal","stock"]]' \
  --sort market_cap_basic:desc --limit 10

# Stocks oversold con high dividend
py scripts/fetch_tradingview.py screen \
  --filter '[["RSI","less",30],["dividend_yield_recent","greater",5]]' \
  --sort dividend_yield_recent:desc --limit 20

# Empresas argentinas en cualquier mercado
py scripts/fetch_tradingview.py country Argentina --limit 30

# Pipeline: search → quote → news
py scripts/fetch_tradingview.py search "Apple" -q | jq -r '.symbols[0].symbol'
py scripts/fetch_tradingview.py quote NASDAQ:AAPL
py scripts/fetch_tradingview.py news NASDAQ:AAPL

# Joinear con SEC EDGAR via CIK
py scripts/fetch_tradingview.py search "GGAL" -q | jq -r '.symbols[0].cik_code'
# -> 0001114700  (usar este CIK en sec-data skill)
```
