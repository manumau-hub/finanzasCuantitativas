---
name: cboe-data
description: "Datos de CBOE via APIs publicas: cotizaciones delayed de indices, futuros VX, charts intraday, most-active, market summary (equities + opciones), symbol lookup, futures products. Sin API key."
license: MIT
---

# CBOE — Datos de Mercado via API Publica

Skill para extraer datos de [CBOE](https://www.cboe.com/us/options/market-statistics/) usando sus **APIS publicas** — sin API key, sin autenticacion.

---

## ⚠️ Aviso Legal

- CBOE no tiene API publica oficial gratuita. Estos endpoints son **publicos** y pueden cambiar sin aviso.
- Respetar los **terminos de servicio** del sitio. No hacer mas de 1 request/segundo.
- Los datos son **delayed** (no en tiempo real). Delay aproximado:
  - **quote / intraday**: ~15-20 min
  - **historical**: datos del dia anterior (actualizacion diaria)
  - **options-chain**: underlying ~15-20 min; datos de opciones individuales pueden ser end-of-day
  - **summary / options-summary**: 20 min (campo `delay` explicito en el response)
  - Los campos `timestamp` en el response indican la ultima actualizacion del cache

---

## Scripts

| Script | Descripcion |
|--------|-------------|
| **[fetch_cboe.py](./scripts/fetch_cboe.py)** | Script principal: todos los endpoints disponibles |

---

## Uso rapido

```bash
# Cotizacion delayed de indices y stocks
python scripts/fetch_cboe.py quote _VIX
python scripts/fetch_cboe.py quote _SPX
python scripts/fetch_cboe.py quote _RUT
python scripts/fetch_cboe.py quote _OEX
python scripts/fetch_cboe.py quote _DJX
python scripts/fetch_cboe.py quote _XSP
python scripts/fetch_cboe.py quote _CBTX
python scripts/fetch_cboe.py quote _MBTX
python scripts/fetch_cboe.py quote _MXEF
python scripts/fetch_cboe.py quote _MXEA
python scripts/fetch_cboe.py quote GGAL
python scripts/fetch_cboe.py quote AAPL

# Datos historicos anuales (annual high/low, HV e IV a 30/60/90 dias)
python scripts/fetch_cboe.py historical _VIX
python scripts/fetch_cboe.py historical _SPX
python scripts/fetch_cboe.py historical GGAL
python scripts/fetch_cboe.py historical AAPL

# Chart intraday 1-min (hoy, 1-min bars con calls/puts volume)
python scripts/fetch_cboe.py intraday _VIX
python scripts/fetch_cboe.py intraday _SPX
python scripts/fetch_cboe.py intraday _RUT
python scripts/fetch_cboe.py intraday GGAL
python scripts/fetch_cboe.py intraday AAPL

# Futuros VX (VIX Futures chain)
python scripts/fetch_cboe.py futures VX
python scripts/fetch_cboe.py futures VXM       # Mini VIX Futures
python scripts/fetch_cboe.py futures VA        # S&P 500 Variance Futures
python scripts/fetch_cboe.py futures IBHY      # iBoxx High Yield Bond Futures
python scripts/fetch_cboe.py futures IBIG      # iBoxx IG Bond Futures

# Listado de todos los productos tradables en CBOE
python scripts/fetch_cboe.py products

# Busqueda de simbolos (todos los tickers con company name)
python scripts/fetch_cboe.py lookup
python scripts/fetch_cboe.py lookup --market edgx   # Por mercado especifico

# Resumen de mercado CBOE (volumen por mercado y tape)
python scripts/fetch_cboe.py summary

# Top 10 mas activos por mercado (la API siempre devuelve 10)
python scripts/fetch_cboe.py most-active              # BZX (default)
python scripts/fetch_cboe.py most-active --market edgx  # Mercado EDGX
python scripts/fetch_cboe.py most-active --market byx   # Mercado BYX
python scripts/fetch_cboe.py most-active --market edga  # Mercado EDGA

# Resumen de mercado opciones CBOE (volumen por exchange)
python scripts/fetch_cboe.py options-summary

# Opciones mas activas (calls/puts por categoria: all, index, equity)
python scripts/fetch_cboe.py options-most-active              # Top 25 (default)
python scripts/fetch_cboe.py options-most-active --limit 10   # Top 10
python scripts/fetch_cboe.py options-most-active --limit 50   # Top 50
python scripts/fetch_cboe.py options-most-active --limit 100  # Top 100

# Productos futuros tradables en CBOE
python scripts/fetch_cboe.py futures-products

# Cadena de opciones completa con greeks (stocks y ETFs)
python scripts/fetch_cboe.py options-chain GGAL
python scripts/fetch_cboe.py options-chain AAPL
python scripts/fetch_cboe.py options-chain BMA -o bma_chain.json

# Todos los datos de un simbolo
python scripts/fetch_cboe.py all _VIX
python scripts/fetch_cboe.py all _SPX

# Guardar output a archivo
python scripts/fetch_cboe.py quote _VIX -o vix_quote.json
python scripts/fetch_cboe.py futures VX -o vx_futures.json

# Modo silencioso (solo JSON)
python scripts/fetch_cboe.py quote _SPX -q
```

---

## Endpoints disponibles

| Modo | Data | Endpoint |
|------|------|----------|
| `quote` | Cotizacion delayed de indices y stocks (precio, cambio, IV30, OHLC) | `cdn.cboe.com/api/global/delayed_quotes/quotes/{symbol}.json` |
| `historical` | Datos historicos anuales (annual high/low, HV e IV 30/60/90) | `cdn.cboe.com/api/global/delayed_quotes/historical_data/{symbol}.json` |
| `intraday` | Chart intraday 1-min con volumen de opciones (calls/puts) | `cdn.cboe.com/api/global/delayed_quotes/charts/intraday/{symbol}.json` |
| `futures` | Cadena de futuros (vencimientos, settlement, OI) | `www-api.cboe.com/us/futures/api/data/?symbol={symbol}` |
| `products` | Todos los productos tradables (indices, futuros, opciones) | `www-api.cboe.com/tradable_products/data/` |
| `lookup` | Busqueda de simbolos (todos los tickers + company name) | `ww2.cboe.com/us/equities/market_statistics/book_viewer_2/symbol_lookup_data/` |
| `summary` | Resumen de mercado equities CBOE (volumen por mercado y tape A/B/C) | `www-api.cboe.com/us/equities/market_statistics/summary_lite/market/data/` |
| `most-active` | Top 10 mas activos por mercado (volumen, bid/ask, last) | `www-api.cboe.com/us/equities/market_statistics/most_active/data/10/` |
| `options-summary` | Resumen de mercado opciones CBOE (volumen por exchange) | `www-api.cboe.com/us/options/market_statistics/summary_lite/market/data/` |
| `options-most-active` | Top N opciones mas activas (calls/puts por categoria) | `www-api.cboe.com/us/options/market_statistics/most_active/data/?mkt=cone&limit={N}` |
| `futures-products` | Productos futuros tradables en CBOE (15 productos) | `www-api.cboe.com/us/futures/api/tradable_future_products_data/` |
| `options-chain` | Cadena de opciones completa con greeks (stocks y ETFs) | `cdn.cboe.com/api/global/delayed_quotes/options/{symbol}.json` |
| `options-directory` | Instrumentos listados con opciones por exchange (~5,500) | `www-api.cboe.com/us/options/symboldir/{exchange}/data/` |
| `all` | Todos los datos disponibles para un simbolo (quote + historical + intraday + futures si aplica) | - |

---

## Simbolos disponibles

### Quotes / Historical / Intraday (indices y stocks)

Funciona tanto para **indices CBOE** (prefijo `_`) como para **stocks y ETFs** (sin prefijo).

| Simbolo | Descripcion |
|---------|-------------|
| `_VIX` | CBOE Volatility Index |
| `_SPX` | S&P 500 Index |
| `_OEX` | S&P 100 Index |
| `_RUT` | Russell 2000 Index |
| `_DJX` | Dow Jones Industrial Average |
| `_XSP` | Mini S&P 500 Index |
| `_CBTX` | Cboe Bitcoin U.S. ETF Index |
| `_MBTX` | Cboe Mini Bitcoin U.S. ETF Index |
| `_MXEF` | MSCI Emerging Markets Index |
| `_MXEA` | MSCI EAFE Index |
| `GGAL` | Grupo Financiero Galicia |
| `AAPL` | Apple Inc |
| `TSLA` | Tesla Inc |
| `SPY` | SPDR S&P 500 ETF |
| `QQQ` | Invesco QQQ Trust |
| `NVDA` | NVIDIA Corp |

> Cualquier ticker listado en CBOE funciona para `quote`, `historical` e `intraday`.

### Futuros (via endpoint `futures`)

| Simbolo | Descripcion |
|---------|-------------|
| `VX` | VIX Futures |
| `VXM` | Mini VIX Futures |
| `VA` | S&P 500 Variance Futures |
| `IBHY` | iBoxx High Yield Corporate Bond Futures |
| `IBIG` | iBoxx Investment Grade Corporate Bond Futures |
| `IEMD` | iBoxx Emerging Market Bond Index Futures |

---

## Consideraciones Tecnicas

### Datos devueltos por `quote`

Funciona para indices (`security_type: "index"`) y stocks (`security_type: "stock"`).

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `current_price` | float | Precio actual |
| `price_change` | float | Cambio neto |
| `price_change_percent` | float | Cambio porcentual |
| `open` | float | Apertura del dia |
| `high` | float | Maximo del dia |
| `low` | float | Minimo del dia |
| `close` | float | Ultimo precio (cierre) |
| `prev_day_close` | float | Cierre anterior |
| `iv30` | float | Volatilidad implicita a 30 dias |
| `iv30_change` | float | Cambio en IV30 |
| `bid` / `ask` | float | Bid/Ask (0.0 en indices, real en stocks) |
| `volume` | int | Volumen (0 en indices, real en stocks) |
| `last_trade_time` | datetime | Ultima operacion |
| `tick` | string | `up` / `down` / `unchanged` |
| `security_type` | string | `index` o `stock` |

### Datos devueltos por `historical`

Datos historicos anuales. Misma estructura para indices y stocks.

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `annual_high` | float | Maximo del ultimo ano |
| `annual_low` | float | Minimo del ultimo ano |
| `hv30_annual_high` | float | Historical Volatility 30d - maximo anual |
| `hv30_annual_low` | float | Historical Volatility 30d - minimo anual |
| `hv60_annual_high` | float | Historical Volatility 60d - maximo anual |
| `hv60_annual_low` | float | Historical Volatility 60d - minimo anual |
| `hv90_annual_high` | float | Historical Volatility 90d - maximo anual |
| `hv90_annual_low` | float | Historical Volatility 90d - minimo anual |
| `iv30_annual_high` | float | Implied Volatility 30d - maximo anual |
| `iv30_annual_low` | float | Implied Volatility 30d - minimo anual |
| `iv60_annual_high` | float | Implied Volatility 60d - maximo anual |
| `iv60_annual_low` | float | Implied Volatility 60d - minimo anual |
| `iv90_annual_high` | float | Implied Volatility 90d - maximo anual |
| `iv90_annual_low` | float | Implied Volatility 90d - minimo anual |

### Datos devueltos por `intraday`

Funciona para indices y stocks. Cada barra de 1-min contiene:

| Campo | Descripcion |
|-------|-------------|
| `datetime` | Timestamp de la barra |
| `price.open` | Apertura |
| `price.high` | Maximo |
| `price.low` | Minimo |
| `price.close` | Cierre |
| `volume.stock_volume` | Volumen de acciones (0 en indices, real en stocks) |
| `volume.calls_volume` | Volumen de opciones call |
| `volume.puts_volume` | Volumen de opciones put |
| `volume.total_options_volume` | Volumen total de opciones |

### Datos devueltos por `futures`

| Campo | Descripcion |
|-------|-------------|
| `symbol` | Nombre del futuro (ej: `VX/M6`) |
| `expiration` | Fecha de vencimiento |
| `last_price` | Ultimo precio |
| `settlement` | Settlement price |
| `prev_settlement` | Settlement anterior |
| `volume` | Volumen |
| `prev_open_int` | Open interest del dia anterior |
| `change` | Cambio vs settlement anterior |

### Datos devueltos por `lookup`

Devuelve un array `symbolsLookupData` con todos los simbolos:

| Campo | Descripcion |
|-------|-------------|
| `name` | Ticker del simbolo |
| `company_name` | Nombre completo de la empresa/ETF |

Cobertura: ~15,000+ simbolos (acciones, ETFs, units, warrants).

### Datos devueltos por `summary`

Resumen del mercado CBOE con volumen por mercado y tape:

| Campo | Descripcion |
|-------|-------------|
| `batsMarketData[].market` | Nombre del mercado (Cboe Total, BZX, BYX, EDGX, EDGA) |
| `batsMarketData[].total.value` | Volumen total del mercado |
| `batsMarketData[].tapea.value` | Volumen Tape A (NYSE) |
| `batsMarketData[].tapeb.value` | Volumen Tape B (Regionals) |
| `batsMarketData[].tapec.value` | Volumen Tape C (Nasdaq) |
| `marketTotals` | Totales consolidados de todos los mercados |
| `date` | Fecha de los datos |
| `delay` | Minutos de delay |

### Datos devueltos por `most-active`

Cada elemento en `data.{market}` es un array con:

| Indice | Campo | Descripcion |
|--------|-------|-------------|
| [0] | symbol | Ticker |
| [1] | volume | Volumen acumulado |
| [2] | - | (dato interno) |
| [3] | bid | Bid price |
| [4] | ask | Ask price |
| [5] | - | (dato interno) |
| [6] | last_price | Ultimo precio negociado |
| [7] | price_change | Cambio neto |
| [8] | company_name | Nombre de la empresa |

### Datos devueltos por `options-summary`

Resumen de mercado opciones CBOE con volumen por exchange:

| Campo | Descripcion |
|-------|-------------|
| `batsMarketData[].market` | Nombre del exchange (Cboe Options, C2, EDGX, BZX) |
| `batsMarketData[].volume` | Volumen total del exchange |
| `batsMarketData[].percent` | Market share porcentual |
| `date` | Fecha de los datos |
| `delay` | Minutos de delay |

### Datos devueltos por `options-most-active`

Devuelve 3 categorias (`all`, `index`, `equity`), cada una con arrays `calls` y `puts`:

| Campo | Descripcion |
|-------|-------------|
| `categories[].category` | Nombre de la categoria (`all`, `index`, `equity`) |
| `categories[].calls[]` | Array de opciones call mas activas |
| `categories[].puts[]` | Array de opciones put mas activas |
| `calls/puts[].symbol` | Simbolo del underlying |
| `calls/puts[].expires` | Fecha de expiracion |
| `calls/puts[].strike` | Strike price |
| `calls/puts[].volume` | Volumen del dia |

`--limit` solo acepta: 10, 25, 50, 100. Cualquier otro valor es ignorado (default: 25).

### Datos devueltos por `futures-products`

Lista de 15 productos futuros tradables en CBOE:

| Campo | Descripcion |
|-------|-------------|
| `underlying_root` | Simbolo raiz (VX, VXM, VA, IBHY, IBIG, IEMD, etc.) |
| `title` | Nombre completo del producto |
| `volume` | Volumen del dia anterior |
| `open_interest` | Open interest |
| `trading_dt` | Fecha de los datos de trading |

### Datos devueltos por `options-chain`

Cadena de opciones completa con greeks. Solo funciona para **stocks y ETFs** (no indices con prefijo `_`).
Incluye el quote del simbolo + todos los contratos (calls y puts).

| Campo | Descripcion |
|-------|-------------|
| `data.options[]` | Array de todos los contratos de opciones |
| `option` | Ticker del contrato (formato: `ROOT` + `YYMMDD` + `C/P` + `strike*1000`) |
| `bid` / `ask` | Bid/Ask del contrato |
| `iv` | Volatilidad implicita |
| `delta` / `gamma` / `theta` / `vega` / `rho` | Greeks |
| `theo` | Precio teorico |
| `volume` | Volumen del dia |
| `open_interest` | Open interest |
| `last_trade_price` | Ultimo precio negociado |

Usar `parse_option_ticker(ticker)` para decodificar el ticker en root, expiry, type (call/put), strike.

### Datos devueltos por `options-directory`

Directorio de todos los instrumentos (stocks, ETFs, indices) que tienen opciones listadas en CBOE.

| Campo | Descripcion |
|-------|-------------|
| `underlying` | Ticker del instrumento |
| `company_name` | Nombre completo de la empresa/ETF |
| `pmm` | Primary Market Maker asignado |
| `post_station` | Post/Station en el trading floor (solo Cboe Options) |
| `gth_mm` | GTH Market Maker (solo Cboe Options) |
| `prod_types` | Tipos de producto |
| `cycles` | Ciclos de vencimiento |

**Flags:**
- `--exchange cboe|edgx` — Cboe Options (default) o EDGX Options
- `--sid X` — Filtrar por letra inicial del company_name (A-Z). Sin filtro devuelve todos
- `--date YYYY-MM-DD` — Fecha especifica. Sin fecha usa la mas reciente

### Flags adicionales

| Flag | Descripcion |
|------|-------------|
| `--market X` | Mercado para `most-active` o `lookup` (default: `bzx`, tambien: `byx`, `edgx`, `edga`) |
| `--limit N` | Resultados por categoria para `options-most-active` (default: 25). Solo: 10, 25, 50, 100 |
| `--exchange X` | Exchange para `options-directory` (default: `cboe`). Valores: `cboe`, `edgx` |
| `--sid X` | Letra inicial del company_name para `options-directory` (A-Z). Sin filtro devuelve todos |
| `--date YYYY-MM-DD` | Fecha para `options-directory`. Sin fecha usa la mas reciente |
| `-o archivo.json` | Guardar output a archivo |
| `-q` / `--quiet` | Modo silencioso (solo JSON) |

### Rate limiting

No hay rate limiting documentado. Se recomienda:
- Minimo 1 segundo entre requests
- Usar `-q` para scripting

### Manejo de errores

CBOE devuelve **403 Forbidden** (no 404) para simbolos que no existen o endpoints que no aplican. El script maneja estos errores gracefulmente, registrando un warning y continuando.

---

## Estructura del skill

```
skills/cboe-data/
├── SKILL.md                          # Este archivo (guia rapida)
├── references/
│   └── REFERENCE.md                  # Documentacion completa de todos los endpoints
└── scripts/
    └── fetch_cboe.py                 # Script principal
```

---

> **Documentacion detallada:** Consultar [references/REFERENCE.md](./references/REFERENCE.md) para la documentacion exhaustiva de cada endpoint, estructuras JSON, ejemplos y consideraciones tecnicas.
