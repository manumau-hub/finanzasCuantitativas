# TradingView — Referencia Completa de la API

> **TradingView** es la plataforma global de market data, analisis tecnico y
> social trading mas usada en el mundo (>50M usuarios activos). Aunque no
> tiene API publica oficial gratuita, sus apps web exponen varias APIs
> internas accesibles **sin autenticacion y sin API key**.
>
> Esta documentacion cubre **6 hosts** identificados por reverse-engineering
> del HTML de las paginas de simbolo, **verificados empiricamente** al
> 2026-06.

---

## Indice

1. [Resumen de endpoints](#1-resumen-de-endpoints)
2. [Hosts de la API](#2-hosts-de-la-api)
3. [Convenciones](#3-convenciones)
4. [Scanner API — el endpoint principal](#4-scanner-api--el-endpoint-principal)
5. [Symbol Search v3](#5-symbol-search-v3)
6. [News Headlines](#6-news-headlines)
7. [HTML scraping de subpages](#7-html-scraping-de-subpages)
8. [Recommend.All / .MA / .Other (ratings)](#8-recommendall--ma--other-ratings)
9. [Manejo de errores](#9-manejo-de-errores)
10. [Limitaciones conocidas](#10-limitaciones-conocidas)
11. [Consideraciones tecnicas](#11-consideraciones-tecnicas)
12. [Otros hosts identificados (no implementados)](#12-otros-hosts-identificados-no-implementados)

---

## 1. Resumen de endpoints

| # | Modo CLI | URL | Metodo | Notas |
|---|----------|-----|--------|-------|
| 1 | `quote SYM` + variantes | `/{market}/scan` | POST | Scanner por simbolo (10 variantes por grupo de columnas) |
| 2 | `screen`, `country`, `sector`, `market` | `/{market}/scan` | POST | Scanner masivo con filtros |
| 3 | `search QUERY` | `/symbol_search/v3/` | GET | Buscador global con ISIN/CUSIP/CIK |
| 4 | `news SYM` / `news-global` | `/v2/headlines` | GET | News por simbolo o global |
| 5 | `story STORY_PATH` | `{web}/{storyPath}` | GET | Fetch HTML body de noticia |
| 6 | `subpage SYM PATH` | `{web}/symbols/{ex}-{sym}/{path}/` | GET | HTML + extraccion `prs.init-data+json` |
| 7 | `columns`, `groups`, `markets` | (local) | — | Catalogos sin HTTP |
| 8 | `all SYM` | combina 6 calls | POST+GET | Quote completo todo-en-uno |

**Total: ~24 modos CLI sobre 4 endpoints HTTP unicos** (el Scanner es uno solo, usado para casi todos los modos de quote/screen).

---

## 2. Hosts de la API

Identificados via `window.*` assignments en el HTML de cualquier symbol page:

| Variable JS | Host | Para |
|-------------|------|------|
| `window.SCREENER_HOST` | `https://scanner.tradingview.com` | **Scanner** — el endpoint principal |
| `window.SS_HOST` | `symbol-search.tradingview.com` | Symbol Search |
| `window.NEWS_SERVICE_URL` | `https://news-headlines.tradingview.com` | News |
| `window.WEBSOCKET_HOST` | `data.tradingview.com` | WebSocket cotizaciones (no impl.) |
| `window.WEBSOCKET_PRO_HOST` | `prodata.tradingview.com` | WS premium (no impl.) |
| `window.WEBSOCKET_HOST_FOR_DEEP_BACKTESTING` | `history-data.tradingview.com` | WS historicos profundos |
| `window.PUSHSTREAM_URL` | `wss://pushstream.tradingview.com` | WS push streaming |
| `window.ECONOMIC_CALENDAR_URL` | `economic-calendar.tradingview.com` | Calendario economico |
| `window.EARNINGS_CALENDAR_URL` | `scanner.tradingview.com` | (alias del scanner) |
| `window.CHARTEVENTS_URL` | `chartevents-reuters.tradingview.com` | Eventos de charts |
| `window.OPTIONS_CHARTING_URL` | `options-charting.tradingview.com` | Opciones charting |
| `window.PORTFOLIO_URL` | `portfolio.tradingview.com/portfolio/v1` | Portfolios |
| `window.PINE_FACADE` | `pine-facade.tradingview.com/pine-facade` | Pine Script |
| (logos) | `s3-symbol-logo.tradingview.com` | Logos PNG/SVG |

---

## 3. Convenciones

### Sin autenticacion

Ningun endpoint requiere API key, token, cookie ni session ID. Funciona
desde scripts headless, CI/CD, Docker, etc.

### Headers recomendados

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Origin": "https://es.tradingview.com",
    "Referer": "https://es.tradingview.com/",
}
```

Para los endpoints POST del Scanner, agregar:

```python
"Content-Type": "application/json"
```

(`requests` lo agrega automaticamente al usar `json=payload`).

### Formato de simbolos

| Formato | Donde |
|---------|-------|
| `{EXCHANGE}:{TICKER}` | Scanner, News, todos los APIs JSON |
| `{EXCHANGE}-{TICKER}` | URLs HTML (es.tradingview.com/symbols/) |

Conversion: simplemente `:` ↔ `-`. Ejemplo: `NASDAQ:GGAL` ↔ `NASDAQ-GGAL`.

### Encoding

UTF-8 valido en TODOS los endpoints. En consolas Windows (cp1252) pueden
aparecer `?` en lugar de caracteres especiales. Workaround universal:

```python
import sys
sys.stdout.reconfigure(encoding="utf-8")
```

O guardar a archivo con `json.dumps(..., ensure_ascii=False)`.

---

## 4. Scanner API — el endpoint principal

**URL:** `POST https://scanner.tradingview.com/{market}/scan`

Es la API mas potente. Devuelve cualquier combinacion de **300+ columnas**
para uno o varios simbolos, con soporte de filtros, sort y paginacion.

### Markets validos

| Market | Cobertura tipica |
|--------|------------------|
| `global` | Todos los mercados (>100k tickers) |
| `america` | NYSE, NASDAQ, AMEX, OTC (~15k) |
| `argentina` | BCBA/BYMA (~300) |
| `brazil` | B3/Bovespa (~500) |
| `spain` | BME (~200) |
| `italy` | Borsa Italiana (~400) |
| `germany` | Xetra/Frankfurt (~1k) |
| `uk` | LSE (~2k) |
| `france` | Euronext Paris (~800) |
| `russia` | MOEX (~200) |
| `crypto` | Cryptos (>50k) |
| `forex` | Forex pairs |
| `bonds` | Bonos globales |

Ver detalles en `assets/markets.json` y `references/MARKETS_EXCHANGES.md`.

### Estructura del request

```json
{
  "symbols": {"tickers": ["NASDAQ:GGAL"]},   // opcional: lista de simbolos
  "filter": [                                  // opcional: filtros
    {"left": "sector", "operation": "equal", "right": "Finance"},
    {"left": "market_cap_basic", "operation": "greater", "right": 100000000000}
  ],
  "columns": ["name", "close", "RSI"],        // requerido
  "range": [0, 30],                            // [offset, offset_end]
  "sort": {                                    // opcional
    "sortBy": "market_cap_basic",
    "sortOrder": "desc"
  },
  "options": {"lang": "en"}                    // opcional
}
```

> ⚠️ **Sin `columns`** la API devuelve `data: [{"s": "...", "d": []}]` (vacio).
> Pasar siempre `columns` explicitas.
>
> ⚠️ **Sin `symbols` ni `filter`** la API filtra todo. Pasar `"filter": []`
> para no filtrar (lista TODOS los del mercado).

### Estructura del response

```json
{
  "totalCount": 1,
  "data": [
    {
      "s": "NASDAQ:GGAL",
      "d": [48.62, 0.6, 729353, "Finance", ...]
    }
  ]
}
```

**Es columnar:** `data[i].d[j]` corresponde a `columns[j]` (mismo orden).

Para denormalizar a dicts (lo que hace `fetch_tradingview.py`):

```python
record = {"symbol": row["s"]}
for col, val in zip(columns_requested, row["d"]):
    record[col] = val
```

### Columnas

Ver lista exhaustiva en `references/SCANNER_COLUMNS.md` y el catalogo
estructurado en `assets/scanner_columns.json`.

### Filtros

Ver `references/SCANNER_FILTERS.md` para operaciones validas (equal, greater,
in_range, match, etc.).

---

## 5. Symbol Search v3

**URL:** `GET https://symbol-search.tradingview.com/symbol_search/v3/?text={query}`

Buscador global. Devuelve los matches con ISIN, CUSIP, CIK, currency,
exchange, logoid, descripcion. Coverage: TODA la base de TradingView.

### Query params

| Param | Descripcion | Default |
|-------|-------------|---------|
| `text` | Texto a buscar (ticker, ISIN, CUSIP, nombre) | (requerido) |
| `search_type` | `stocks` \| `funds` \| `futures` \| `forex` \| `crypto` \| `indices` \| `bonds` \| `options` | sin filtro |
| `exchange` | Filtrar por exchange (`NASDAQ`, `NYSE`, `BCBA`, `BME`, etc.) | sin filtro |
| `lang` | Idioma del response (en, es) | en |
| `domain` | `production` | production |
| `hl` | 1 = `<em>` highlights en `description` | 1 |

### Response

```json
{
  "symbols_remaining": 0,
  "symbols": [
    {
      "symbol": "GGAL",
      "description": "Grupo Financiero <em>Galicia</em> S.A.",
      "type": "dr",
      "exchange": "NASDAQ",
      "found_by_isin": false,
      "found_by_cusip": false,
      "cusip": "399909100",
      "isin": "US3999091008",
      "cik_code": "0001114700",
      "currency_code": "USD",
      "currency-logoid": "country/US",
      "logoid": "gpo-fin-galicia",
      "logo": {"style": "single", "logoid": "gpo-fin-galicia"},
      "provider_id": "ice",
      "source_logoid": "source/NASDAQ",
      "source2": {"id": "NASDAQ", "name": "Nasdaq Stock Market"}
    }
  ]
}
```

Ver mas en `references/SYMBOL_SEARCH.md`.

---

## 6. News Headlines

**URL:** `GET https://news-headlines.tradingview.com/v2/headlines`

Hasta 200 noticias recientes por request.

### Query params

| Param | Descripcion |
|-------|-------------|
| `client` | `web` (siempre) |
| `lang` | `en` (recomendado — `es` y otros devuelven menos coverage) |
| `symbol` | (opcional) `NASDAQ:AAPL`, etc. Sin symbol = headlines globales |

### Response

```json
{
  "items": [
    {
      "id": "DJN_DN20260604009289:0",
      "title": "Apple's Plan for AI Dominance...",
      "provider": "dow-jones",
      "sourceLogoId": "dow-jones",
      "published": 1780619400,
      "source": "Dow Jones Newswires",
      "urgency": 2,
      "permission": "provider",
      "relatedSymbols": [
        {"symbol": "NASDAQ:AAPL", "logoid": "apple"}
      ],
      "storyPath": "/news/DJN_DN20260604009289:0/"
    }
  ]
}
```

### Detalle de noticia

El endpoint API directo (`/v2/story?id=...`) retorna **400**. Workaround:
scrapear `https://es.tradingview.com{storyPath}` (HTML 200, ~190 KB).

Ver mas en `references/NEWS_API.md`.

---

## 7. HTML scraping de subpages

**URL:** `GET https://es.tradingview.com/symbols/{EX}-{SYM}/{subpath}/`

Cada pagina de simbolo tiene varias subpages HTML (200 OK con HTML
~200-1000 KB) que contienen data SSR (Server-Side Rendered).

### Subpages validas (16 confirmadas)

| Subpath | Tamaño | Contenido |
|---------|--------|-----------|
| `` (base) | 400 KB | Overview |
| `technicals` | 211 KB | Ratings + indicadores |
| `financials-overview` | 217 KB | Resumen financiero |
| `financials-income-statement` | 610 KB | Income (multi-periodo) |
| `financials-balance-sheet` | 386 KB | Balance |
| `financials-cash-flow` | 333 KB | Cash flow |
| `financials-statistics-and-ratios` | 1 MB | Statistics + ratios |
| `financials-dividends` | 203 KB | Historico dividendos |
| `financials-revenue` | 205 KB | Revenue breakdown |
| `financials-earnings` | 215 KB | Earnings + forecast |
| `forecast` | 200 KB | Price targets |
| `ideas` | 438 KB | Ideas comunidad |
| `options-chain` | 398 KB | Cadena opciones |
| `seasonals` | 194 KB | Estacionalidad |
| `bonds` | 218 KB | Bonos relacionados |
| `etfs` | 256 KB | ETFs que contienen el ticker |
| `minds` | 278 KB | Comentarios cortos comunidad |

### Subpages que NO existen (HTTP 404)

`/news/`, `/analysis/`, `/profile/`, `/markets/`, `/insider-trading/`,
`/financials-statistics/`, `/financials-statements-and-ratios/`.

### Como extraer data del HTML

El HTML tiene **bloques `<script type="application/prs.init-data+json">`**
con la data SSR. Ver `references/HTML_SCRAPING.md` para los patrones de regex.

---

## 8. Recommend.All / .MA / .Other (ratings)

Los campos `Recommend.All`, `Recommend.MA`, `Recommend.Other` del Scanner
son los **ratings agregados de TradingView**, valores entre `-1.0` y `+1.0`.

| Valor | Bucket | Etiqueta UI |
|-------|--------|-------------|
| -1.00 a -0.50 | STRONG_SELL | Venta fuerte |
| -0.50 a -0.10 | SELL | Venta |
| -0.10 a +0.10 | NEUTRAL | Neutral |
| +0.10 a +0.50 | BUY | Compra |
| +0.50 a +1.00 | STRONG_BUY | Compra fuerte |

| Campo | Calculado a partir de |
|-------|----------------------|
| `Recommend.All` | Promedio agregado de TODOS los indicadores |
| `Recommend.MA` | Solo medias moviles (SMA/EMA 10..200, VWMA, Ichimoku, HullMA) |
| `Recommend.Other` | Solo osciladores (RSI, Stoch, MACD, ADX, CCI, BBP, UO, W%R, AO) |

Mapeo persistido en `assets/recommend_ratings.json`. El script tiene
`recommend_label(value)` para convertir directo.

---

## 9. Manejo de errores

| Status | Causas |
|--------|--------|
| 200 | OK. Para Scanner verificar `totalCount > 0` y `data[0].d` no vacio. |
| 400 | Payload invalido (columna desconocida, filter mal formado, `null` body) |
| 403 | Path inexistente o headers faltantes (algunos endpoints requieren `Origin`/`Referer`) |
| 404 | Subpage HTML no existe (ej: `/news/`) |
| 405 | Metodo erroneo (ej: `/v3/headlines` GET no existe, es solo v2) |

### Errores tipicos del Scanner

- `data: [{"s": "X", "d": []}]` → falta `columns` en el payload.
- `data: []` y `totalCount: 0` → el ticker no existe en ese market (probar `global` o el market correcto).
- HTTP 200 pero campo vacio en una columna → el ticker no soporta esa columna (ej: ETFs no tienen EPS).

### Errores tipicos de Symbol Search

- HTTP 200 con `symbols: []` → query no matcheo. Probar version corta del nombre.

---

## 10. Limitaciones conocidas

1. **No hay endpoint de OHLCV historico** via REST publica.
   El historico real-time esta detras del WebSocket `wss://data.tradingview.com`
   (formato propietario, no implementado). El Scanner devuelve solo
   `close` actual + `Perf.W/1M/3M/...` returns.

2. **News coverage desigual**: stocks grandes (AAPL/MSFT/NVDA/JPM) = ~200
   noticias por request, stocks chicos o no-US = 1-10. `lang=es` devuelve casi nada.

3. **Sin doc oficial**: los endpoints son internos y pueden cambiar
   sin aviso. La estructura columnar del Scanner es estable desde 2017+.

4. **Scanner `page` no aplica**: el Scanner usa `range: [offset, end]`
   no pagination tradicional. Para traer mas de 30: `range: [0, 5000]`.

5. **Algunas columnas devuelven `null`** para ciertos tipos de instrumento:
   - ETFs/funds: `earnings_per_share_*`, `revenue_*`
   - Crypto: la mayoria de fundamentals
   - Bonds: `EPS`, `P/E`, `dividend_*`

6. **`/argentina/scan` con `NASDAQ:GGAL`** devuelve 0 — el ticker tiene
   que matchear el mercado (`BCBA:GGAL` para argentina, `NASDAQ:GGAL`
   para america).

7. **`symbol_search_type=forex`** con `text=BTCUSD` devuelve 0 — el filtro
   por type tiene que coincidir con el universo (BTCUSD es `crypto`, no
   `forex`).

8. **HTML responses tienen latin-1 escapes**: la pagina es UTF-8 pero
   algunos campos vienen como `&amp;`, `&quot;`, etc. en HTML entities.
   Usar `html.unescape()` antes de parsear JSON embebido.

9. **WebSocket para real-time**: no implementado en este skill. Para feed
   live verdadero (sin delay), usar libs como `tvDatafeed` o `tradingview-ta`
   (no oficiales, scrapean el WS).

---

## 11. Consideraciones tecnicas

### Rate limiting

No hay documentado, pero observado:
- **Scanner**: tolera ~5 req/s sin throttle.
- **News**: tolera ~3 req/s.
- **Symbol Search**: tolera ~5 req/s.
- **HTML subpages**: el WAF es mas estricto (~1 req/s para evitar 429).

Recomendacion: `time.sleep(0.3)` entre requests para uso normal.

### Delay de datos

- **Quote (`close`, `change`, `volume`)**: ~15 min delay tipico de mercado.
- **Indicadores tecnicos**: calculados sobre delayed data (~15-20 min).
- **Earnings/forecast**: actualizados al cierre del reporte (T+0).
- **News**: real-time.
- **Historico (`Perf.*`)**: actualizado al cierre diario.

### CORS

Los endpoints aceptan CORS desde dominios de TradingView. Para uso desde
frontend (browser fuera de TV), usar proxy backend.

### Aviso legal

- TradingView NO publica documentacion oficial de estas APIs.
- Los endpoints pueden cambiar sin aviso (en ~6 años de tracking comunitario,
  cambios han sido raros y graduales).
- Respetar los terminos de uso de TradingView. Para uso comercial intensivo,
  contratar la **TradingView REST API oficial** (de pago, requiere acuerdo
  con el equipo de partnerships).
- **No abusar**: respetar rate limits razonables, no hacer scraping
  agresivo, no redistribuir data como si fuera propia.

---

## 12. Otros hosts identificados (no implementados)

Detectados en `window.*` del HTML pero requeririan mas reverse engineering:

| Host | Hipotesis de uso |
|------|------------------|
| `wss://data.tradingview.com` | WS feed real-time cotizaciones (protocolo propietario) |
| `wss://prodata.tradingview.com` | WS feed premium (requiere subscription token) |
| `wss://history-data.tradingview.com` | WS historicos profundos (1m/5m/15m/1h candles) |
| `wss://pushstream.tradingview.com` | Notifications push |
| `economic-calendar.tradingview.com` | Calendario economico (probado: 403 sin params correctos) |
| `chartevents-reuters.tradingview.com` | Eventos de Reuters sobre charts |
| `options-charting.tradingview.com` | Greeks + chains avanzadas (probable que requiera login) |
| `options-storage.tradingview.com` | Storage de configuraciones de opciones |
| `portfolio.tradingview.com/portfolio/v1` | Portfolios (requiere login) |
| `pine-facade.tradingview.com/pine-facade` | Pine Script execution (login) |

Las WebSockets son la frontera mas interesante — exponen tick-by-tick
real-time pero requieren handshake especifico. Hay libs OSS que lo
implementan (ver `tvDatafeed`, `tradingview-ta`).

---

## Referencias

- **TradingView Oficial:** https://www.tradingview.com
- **TradingView REST API oficial (paga):** https://www.tradingview.com/rest-api/
- **Lista de columnas comunitaria:** mayormente reverse-engineered
- **Libs OSS relacionadas:**
  - `tvDatafeed` (Python WS client)
  - `tradingview-ta` (Python Scanner client)
  - `tvjs` (JS Scanner client)
