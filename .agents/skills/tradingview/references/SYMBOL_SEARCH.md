# Symbol Search v3 — Referencia Detallada

> Endpoint: `GET https://symbol-search.tradingview.com/symbol_search/v3/?text={query}`
>
> Buscador global de TradingView. Devuelve los matches con **ISIN, CUSIP,
> CIK, currency, exchange, logoid, descripcion**. Sin auth.

---

## Indice

1. [Endpoint y parametros](#1-endpoint-y-parametros)
2. [Schema del response](#2-schema-del-response)
3. [Campos detallados](#3-campos-detallados)
4. [search_type — universos disponibles](#4-search_type--universos-disponibles)
5. [Filtros adicionales](#5-filtros-adicionales)
6. [Variantes del endpoint](#6-variantes-del-endpoint)
7. [Casos de uso comunes](#7-casos-de-uso-comunes)
8. [Limitaciones](#8-limitaciones)

---

## 1. Endpoint y parametros

### URL

```
GET https://symbol-search.tradingview.com/symbol_search/v3/
```

### Query params

| Param | Tipo | Descripcion | Default |
|-------|------|-------------|---------|
| `text` | str | Texto a buscar (ticker, ISIN, CUSIP, nombre empresa) | (requerido) |
| `search_type` | str | Tipo de instrumento (ver seccion 4) | sin filtro (todos) |
| `exchange` | str | Filtrar por exchange (NASDAQ, NYSE, BCBA, BME, etc.) | sin filtro |
| `lang` | str | Idioma del response (en, es) | en |
| `domain` | str | `production` (siempre) | production |
| `hl` | int | 1 = `<em>` highlights en `description` | 1 |

### Headers

Identicos a los de scanner:

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Origin": "https://es.tradingview.com",
    "Referer": "https://es.tradingview.com/",
}
```

---

## 2. Schema del response

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

| Campo top-level | Tipo | Descripcion |
|-----------------|------|-------------|
| `symbols_remaining` | int | Items adicionales no retornados (0 si todos cabieron) |
| `symbols` | list | Array de matches |

---

## 3. Campos detallados

### Identificadores estandar

| Campo | Descripcion |
|-------|-------------|
| `symbol` | Ticker corto (ej: `GGAL`). NO incluye exchange. Para usar en Scanner concatenar `exchange:symbol`. |
| `description` | Nombre completo. Con `hl=1` viene con `<em>` en los matches. |
| `type` | `stock`, `dr` (ADR/CEDEAR), `etf`, `fund`, `crypto`, `forex`, `bond`, `index`, `future`, `option` |
| `exchange` | Exchange code |
| `currency_code` | Moneda de cotizacion ISO 4217 (USD, EUR, ARS, BRL, etc.) |

### Identificadores universales (gold!)

| Campo | Descripcion |
|-------|-------------|
| `isin` | **ISIN** (International Securities Identification Number). Estandar global 12 chars. Ej: `US3999091008` |
| `cusip` | **CUSIP** (US standard 9 chars). Ej: `399909100` |
| `cik_code` | **CIK code** (SEC US filer ID, 10 digits). Ej: `0001114700`. Usar para joinear con SEC EDGAR. |
| `found_by_isin` | true si el match vino por ISIN match (no por nombre) |
| `found_by_cusip` | true si el match vino por CUSIP match |

> Estos 3 codes son ORO para arbitrar datos entre fuentes:
> - **ISIN**: estandar global, identifica unicamente una emision.
> - **CUSIP**: para US, sub-identifier de ISIN.
> - **CIK**: para joinear con SEC EDGAR (10-K, 10-Q, 8-K filings).

### Logos

| Campo | Uso |
|-------|-----|
| `logoid` | ID del logo. URL completa: `https://s3-symbol-logo.tradingview.com/{logoid}--big.svg` |
| `logo` | dict con `style` (`single` o `dual`) y `logoid` |
| `currency-logoid` | ID del logo de la moneda (ej: `country/US`) |
| `source_logoid` | ID del logo del exchange (ej: `source/NASDAQ`) |

### Fuente

| Campo | Descripcion |
|-------|-------------|
| `provider_id` | Provider de los datos (`ice`, `nasdaq`, `cboe`, etc.) |
| `source2` | `{id, name}` del exchange |

---

## 4. search_type — universos disponibles

| Tipo | Descripcion | Ejemplo |
|------|-------------|---------|
| `stocks` | Acciones + ADRs + CEDEARs + fondos cerrados | `text=GGAL` |
| `funds` | Mutual funds + ETFs | `text=SPY` |
| `futures` | Futuros | `text=ES1!` |
| `forex` | Forex pairs | `text=EURUSD` |
| `crypto` | Cryptocurrencies | `text=BTC` |
| `indices` | Indices | `text=SPX` |
| `bonds` | Bonos | `text=US10Y` |
| `economic` | Indicadores economicos | `text=CPI` |
| `options` | Opciones | `text=AAPL` |

> Sin `search_type` devuelve TODOS los tipos. Util para descubrir si un
> ticker existe en multiples universos.

### Que NO funciona

- `search_type=etf` (los ETFs estan dentro de `funds`)
- `search_type=cedear` (los CEDEARs estan en `stocks` con `type=dr`)

---

## 5. Filtros adicionales

### Por exchange

```
GET /symbol_search/v3/?text=Apple&exchange=NASDAQ
```

→ Devuelve solo matches en NASDAQ.

### Por idioma

```
GET /symbol_search/v3/?text=GGAL&lang=es
```

→ Devuelve descripciones traducidas cuando estan disponibles.

### Highlight matches

```
GET /symbol_search/v3/?text=Apple&hl=1
```

→ `description` viene con `<em>Apple</em>` envolviendo el match.

Con `hl=0` viene texto plano.

---

## 6. Variantes del endpoint

| Path | Status | Tipo de response |
|------|--------|------------------|
| `/symbol_search/v3/` | ✅ 200 | dict `{symbols_remaining, symbols[]}` |
| `/symbol_search/` | ✅ 200 | list `[...]` directo (formato antiguo) |
| `/local_search/v3/` | ✅ 200 | Identico a `/symbol_search/v3/` |
| `/symbol_search/v2/` | ❓ | (no testeado) |

**Recomendacion:** usar **`/v3/`** — formato estructurado con `symbols_remaining`.

---

## 7. Casos de uso comunes

### 1. Resolver simbolo desde ticker corto

```python
results = symbol_search("GGAL", search_type="stocks")
# Devuelve hasta 50 matches con GGAL en distintos exchanges
```

### 2. Buscar por nombre de empresa

```python
results = symbol_search("Apple", search_type="stocks")
# Primer match: NASDAQ:AAPL
```

### 3. Resolver por ISIN

```python
results = symbol_search("US3999091008")
# El response tendra found_by_isin: true para el match correcto
```

### 4. Resolver por CUSIP

```python
results = symbol_search("399909100")
# found_by_cusip: true
```

### 5. Filtrar por exchange especifico

```python
results = symbol_search("AAPL", exchange="NASDAQ")
# Solo NASDAQ:AAPL (no XETR:APC, BMV:AAPL, etc.)
```

### 6. Listar todos los exchanges donde cotiza un ticker

```python
results = symbol_search("AAPL", search_type="stocks")
exchanges = [s["exchange"] for s in results["symbols"]]
# ['NASDAQ', 'XETR', 'BMV', 'LSE', 'MEX', ...]
```

### 7. Buscar criptos por ticker

```python
results = symbol_search("BTC", search_type="crypto")
# Devuelve BTCUSD, BTCEUR, BTCUSDT en multiples exchanges
```

### 8. Joinear con SEC EDGAR via CIK

```python
ggal = symbol_search("GGAL", search_type="stocks")["symbols"][0]
cik = ggal["cik_code"]
# Ahora usar SEC EDGAR API:
# https://data.sec.gov/submissions/CIK{cik}.json
```

### 9. Pipeline search → quote

```python
# 1. Buscar
matches = symbol_search("Galicia", search_type="stocks")
nasdaq_match = next((s for s in matches["symbols"] if s["exchange"] == "NASDAQ"), None)
# 2. Quote
ticker = f"{nasdaq_match['exchange']}:{nasdaq_match['symbol']}"
quote_data = quote(ticker)
```

### 10. Verificar si un ticker existe

```python
results = symbol_search("XYZQ", search_type="stocks")
exists = len(results["symbols"]) > 0
```

---

## 8. Limitaciones

1. **Maximo ~50 resultados por request** (segun `symbols_remaining`).
   No hay paginacion. Para mas, hacer queries mas especificas con
   `exchange` filter.

2. **search_type debe matchear el universo real**:
   - `text=BTCUSD` con `search_type=forex` → 0 results (es crypto).
   - `text=EURUSD` con `search_type=crypto` → 0 results (es forex).

3. **No hay filtro por country**: para filtrar por country usar el
   Scanner con `filter: country = X`.

4. **No hay filtro por type secundario** (CEDEAR vs ADR): ambos son
   `type=dr`. Distinguir por exchange (`BCBA:*` vs `NASDAQ:*`).

5. **Tickers locales no-latinos** (japoneses, chinos, hebreos) pueden
   tener problemas de display en consolas que no soportan UTF-8 completo.
   Salvar a archivo con `ensure_ascii=False` para verlos correctamente.

6. **No hay endpoint de "lista todos los tickers de un exchange"** via
   symbol_search. Para eso usar el Scanner:

```python
all_nasdaq = scanner_scan(
    columns=["name", "description"],
    filter_=[{"left": "exchange", "operation": "equal", "right": "NASDAQ"}],
    market="america",
    range_=(0, 5000),
)
```

---

## Apendice: integracion con otros skills del repo

| Skill | Como integrar via SymbolSearch |
|-------|--------------------------------|
| **sec-data** | Obtener `cik_code` → fetch 10-K/10-Q de SEC EDGAR |
| **finviz** | Obtener `symbol` US → query Finviz por ticker |
| **macrotrends** | Obtener nombre exacto + ticker → URL Macrotrends |
| **yahoo-finance** | Obtener ticker + exchange → Yahoo Finance |
| **byma** | Obtener ticker BCBA (`exchange=BCBA`) → panel BYMA |
| **investing** | Obtener `description` para slug Investing |
