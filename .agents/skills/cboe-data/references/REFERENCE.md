# CBOE Data — Referencia Completa

## Indice
1. [Resumen de Endpoints](#1-resumen-de-endpoints)
2. [Quote — Cotizacion Delayed de Indices y Stocks](#2-quote--cotizacion-delayed-de-indices-y-stocks)
3. [Historical — Datos Historicos Anuales](#3-historical--datos-historicos-anuales)
4. [Intraday — Chart OHLCV 1-min](#4-intraday--chart-ohlcv-1-min)
5. [Futures — Cadena de Futuros](#5-futures--cadena-de-futuros)
6. [Products — Productos Tradables](#6-products--productos-tradables)
7. [All — Fetch Combinado](#7-all--fetch-combinado)
8. [Lookup — Busqueda de Simbolos](#8-lookup--busqueda-de-simbolos)
9. [Summary — Resumen de Mercado Equities](#9-summary--resumen-de-mercado-equities)
10. [Most Active — Top 10 Mas Activos (Equities)](#10-most-active--top-10-mas-activos-equities)
11. [Options Summary — Resumen de Mercado Opciones](#11-options-summary--resumen-de-mercado-opciones)
12. [Options Most Active — Top N Opciones Mas Activas](#12-options-most-active--top-n-opciones-mas-activas)
13. [Options Chain — Cadena de Opciones Completa](#13-options-chain--cadena-de-opciones-completa)
14. [Options Directory — Instrumentos Listados con Opciones](#14-options-directory--instrumentos-listados-con-opciones)
15. [Futures Products — Productos Futuros Tradables](#15-futures-products--productos-futuros-tradables)
16. [Consideraciones Tecnicas](#16-consideraciones-tecnicas)

---

## 1. Resumen de Endpoints

| Modo | Endpoint | Metodo | Output |
|------|----------|--------|--------|
| `quote` | `https://cdn.cboe.com/api/global/delayed_quotes/quotes/{symbol}.json` | GET | JSON ~1KB |
| `historical` | `https://cdn.cboe.com/api/global/delayed_quotes/historical_data/{symbol}.json` | GET | JSON ~0.5KB |
| `intraday` | `https://cdn.cboe.com/api/global/delayed_quotes/charts/intraday/{symbol}.json` | GET | JSON ~15-110KB |
| `futures` | `https://www-api.cboe.com/us/futures/api/data/?symbol={symbol}` | GET | JSON ~3-8KB |
| `products` | `https://www-api.cboe.com/tradable_products/data/` | GET | JSON ~3KB |
| `lookup` | `https://ww2.cboe.com/us/equities/market_statistics/book_viewer_2/symbol_lookup_data/?mkt={market}` | GET | JSON ~500KB+ |
| `summary` | `https://www-api.cboe.com/us/equities/market_statistics/summary_lite/market/data/` | GET | JSON ~3KB |
| `most-active` | `https://www-api.cboe.com/us/equities/market_statistics/most_active/data/10/?mkts={market}` | GET | JSON ~2KB |
| `options-summary` | `https://www-api.cboe.com/us/options/market_statistics/summary_lite/market/data/` | GET | JSON ~0.5KB |
| `options-most-active` | `https://www-api.cboe.com/us/options/market_statistics/most_active/data/?mkt=cone&limit={N}` | GET | JSON ~5-24KB |
| `options-chain` | `https://cdn.cboe.com/api/global/delayed_quotes/options/{symbol}.json` | GET | JSON ~100KB-2.3MB |
| `options-directory` | `https://www-api.cboe.com/us/options/symboldir/{exchange}/data/?dt={date}&sid={letter}` | GET | JSON ~50-100KB |
| `futures-products` | `https://www-api.cboe.com/us/futures/api/tradable_future_products_data/` | GET | JSON ~2.5KB |

**Headers requeridos:**
```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}
```

---

## 2. Quote — Cotizacion Delayed de Indices y Stocks

**Endpoint:** `GET https://cdn.cboe.com/api/global/delayed_quotes/quotes/{symbol}.json`

Endpoint principal que devuelve la cotizacion actual de indices CBOE y stocks: precio, cambio, datos de mercado, IV30 (volatilidad implicita a 30 dias).

Funciona tanto para indices (prefijo `_`) como para stocks y ETFs (sin prefijo). La estructura del response es identica; el campo `security_type` distingue `"index"` de `"stock"`.

### Simbolos disponibles

#### Indices CBOE

| Simbolo | Descripcion | Coverage |
|---------|-------------|----------|
| `_VIX` | CBOE Volatility Index | ✅ |
| `_SPX` | S&P 500 Index | ✅ |
| `_OEX` | S&P 100 Index | ✅ |
| `_RUT` | Russell 2000 Index | ✅ |
| `_DJX` | Dow Jones Industrial Average | ✅ |
| `_XSP` | Mini S&P 500 Index | ✅ |
| `_CBTX` | Cboe Bitcoin U.S. ETF Index | ✅ |
| `_MBTX` | Cboe Mini Bitcoin U.S. ETF Index | ✅ |
| `_MXEF` | MSCI Emerging Markets Index | ✅ |
| `_MXEA` | MSCI EAFE Index | ✅ |

#### Stocks y ETFs

Cualquier ticker listado en CBOE funciona. Ejemplos verificados:

| Simbolo | Descripcion | Coverage |
|---------|-------------|----------|
| `GGAL` | Grupo Financiero Galicia | ✅ |
| `AAPL` | Apple Inc | ✅ |
| `TSLA` | Tesla Inc | ✅ |
| `SPY` | SPDR S&P 500 ETF | ✅ |
| `QQQ` | Invesco QQQ Trust | ✅ |
| `NVDA` | NVIDIA Corp | ✅ |
| `MNST` | Monster Beverage | ✅ |
| `XYZ` | Block Inc | ✅ |

### Campos del response

```json
{
  "timestamp": "2026-06-04 15:43:30",
  "data": {
    "symbol": "^VIX",
    "security_type": "index",
    "exchange_id": 5,
    "current_price": 15.66,
    "price_change": -0.4,
    "price_change_percent": -2.4907,
    "bid": 0.0,
    "ask": 0.0,
    "bid_size": 0,
    "ask_size": 0,
    "open": 16.44,
    "high": 16.44,
    "low": 15.62,
    "close": 15.66,
    "prev_day_close": 16.06,
    "volume": 0,
    "iv30": 72.349,
    "iv30_change": -13.546,
    "iv30_change_percent": -15.7704,
    "seqno": 31675007780,
    "last_trade_time": "2026-06-04T11:28:16",
    "tick": "up"
  },
  "symbol": "_VIX"
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `data.symbol` | string | Simbolo interno (^VIX, ^SPX, GGAL, AAPL, etc.) |
| `data.security_type` | string | Tipo: `index` o `stock` |
| `data.current_price` | float | Precio actual |
| `data.price_change` | float | Cambio neto en puntos |
| `data.price_change_percent` | float | Cambio porcentual |
| `data.bid` | float | Bid (0.0 en indices, real en stocks) |
| `data.ask` | float | Ask (0.0 en indices, real en stocks) |
| `data.open` | float | Apertura del dia |
| `data.high` | float | Maximo del dia |
| `data.low` | float | Minimo del dia |
| `data.close` | float | Ultimo precio |
| `data.prev_day_close` | float | Cierre del dia anterior |
| `data.volume` | int | Volumen (0 para indices, real para stocks) |
| `data.iv30` | float | **Volatilidad implicita a 30 dias** |
| `data.iv30_change` | float | Cambio en IV30 |
| `data.iv30_change_percent` | float | Cambio porcentual en IV30 |
| `data.last_trade_time` | string | Ultima actualizacion (ISO) |
| `data.tick` | string | `up` / `down` / `unchanged` |
| `symbol` | string | Simbolo consultado |

### IV30 (Implied Volatility 30-day)

El campo `iv30` es particularmente importante:
- **VIX**: iv30 ES el valor del indice VIX (ej: 72.35)
- **SPX**: iv30 representa la volatilidad implicita del SPX (ej: 12.71)
- **RUT**: iv30 para Russell 2000 (ej: 21.02)
- **Stocks**: iv30 para cualquier stock listado (ej: GGAL iv30=52.45)

### Diferencias index vs stock

| Campo | Index | Stock |
|-------|-------|-------|
| `security_type` | `"index"` | `"stock"` |
| `bid` / `ask` | `0.0` | Valores reales |
| `bid_size` / `ask_size` | `0` | Valores reales |
| `volume` | `0` | Volumen real de acciones |
| `exchange_id` | `5` (CBOE) | `2` (listado en exchange) |

### Coverage horaria

| Data | Disponibilidad |
|------|---------------|
| Precios | Durante horario de mercado (9:30-16:00 ET) |
| IV30 | Se actualiza durante el dia |
| Datos delayed | ~15-20 min de delay |

### Ejemplo

```bash
python scripts/fetch_cboe.py quote _VIX
python scripts/fetch_cboe.py quote _SPX -q
python scripts/fetch_cboe.py quote _RUT -o rut_quote.json
python scripts/fetch_cboe.py quote GGAL
python scripts/fetch_cboe.py quote AAPL -q
```

---

## 3. Historical — Datos Historicos Anuales

**Endpoint:** `GET https://cdn.cboe.com/api/global/delayed_quotes/historical_data/{symbol}.json`

Devuelve datos historicos anuales: precio annual high/low, Historical Volatility (HV) e Implied Volatility (IV) a 30, 60 y 90 dias, con sus respectivos high y low del ultimo ano.

Funciona tanto para indices (prefijo `_`) como para stocks y ETFs.

### Simbolos disponibles

Los mismos simbolos que `quote` (indices CBOE y cualquier stock/ETF listado).

### Campos del response

```json
{
  "timestamp": "2026-06-04 11:05:04",
  "data": {
    "symbol": "GGAL",
    "annual_high": 62.5099983215332,
    "hv30_annual_high": 136.83999633789062,
    "hv60_annual_high": 120.06300354003906,
    "hv90_annual_high": 101.5,
    "iv30_annual_high": 127.98300170898438,
    "iv60_annual_high": 112.2969970703125,
    "iv90_annual_high": 98.3759994506836,
    "annual_low": 25.889999389648438,
    "hv30_annual_low": 31.202999114990234,
    "hv60_annual_low": 36.32699966430664,
    "hv90_annual_low": 38.96860122680664,
    "iv30_annual_low": 43.83399963378906,
    "iv60_annual_low": 43.347999572753906,
    "iv90_annual_low": 43.983001708984375
  },
  "symbol": "GGAL"
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `data.symbol` | string | Simbolo consultado |
| `data.annual_high` | float | Maximo del precio en los ultimos 12 meses |
| `data.annual_low` | float | Minimo del precio en los ultimos 12 meses |
| `data.hv30_annual_high` | float | Historical Volatility 30d - maximo anual |
| `data.hv30_annual_low` | float | Historical Volatility 30d - minimo anual |
| `data.hv60_annual_high` | float | Historical Volatility 60d - maximo anual |
| `data.hv60_annual_low` | float | Historical Volatility 60d - minimo anual |
| `data.hv90_annual_high` | float | Historical Volatility 90d - maximo anual |
| `data.hv90_annual_low` | float | Historical Volatility 90d - minimo anual |
| `data.iv30_annual_high` | float | Implied Volatility 30d - maximo anual |
| `data.iv30_annual_low` | float | Implied Volatility 30d - minimo anual |
| `data.iv60_annual_high` | float | Implied Volatility 60d - maximo anual |
| `data.iv60_annual_low` | float | Implied Volatility 60d - minimo anual |
| `data.iv90_annual_high` | float | Implied Volatility 90d - maximo anual |
| `data.iv90_annual_low` | float | Implied Volatility 90d - minimo anual |

### HV vs IV

| Metrica | Significado | Uso |
|---------|-------------|-----|
| **HV (Historical Volatility)** | Volatilidad realizada basada en precios pasados | Cuanto se movio el activo |
| **IV (Implied Volatility)** | Volatilidad implicita deducida de las opciones | Cuanto el mercado espera que se mueva |
| **IV > HV** | - | Mercado espera mas movimiento del que hubo (posible evento) |
| **IV < HV** | - | Mercado espera menos movimiento (posible calma) |

### Ejemplo

```bash
python scripts/fetch_cboe.py historical _VIX
python scripts/fetch_cboe.py historical GGAL
python scripts/fetch_cboe.py historical AAPL -o aapl_historical.json
python scripts/fetch_cboe.py historical _SPX -q
```

---

## 4. Intraday — Chart OHLCV 1-min

**Endpoint:** `GET https://cdn.cboe.com/api/global/delayed_quotes/charts/intraday/{symbol}.json`

Devuelve barras OHLC de **1 minuto** para el dia de hoy, incluyendo volumen de opciones (calls, puts, total).

Funciona tanto para indices (prefijo `_`) como para stocks y ETFs.

### Simbolos disponibles

Los mismos simbolos que `quote` (indices CBOE y cualquier stock/ETF listado).

### Campos del response

```json
{
  "timestamp": "2026-06-04 15:43:09",
  "data": [
    {
      "datetime": "2026-06-04T09:31:00",
      "sequence_number": 180666537,
      "price": {
        "open": 16.44,
        "high": 16.44,
        "low": 16.34,
        "close": 16.35
      },
      "volume": {
        "stock_volume": 0,
        "calls_volume": 884,
        "puts_volume": 8278,
        "total_options_volume": 9162
      }
    }
  ]
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `datetime` | string | Timestamp ISO de la barra (HH:MM:00) |
| `sequence_number` | long | Numero de secuencia |
| `price.open` | float | Precio de apertura del minuto |
| `price.high` | float | Maximo del minuto |
| `price.low` | float | Minimo del minuto |
| `price.close` | float | Precio de cierre del minuto |
| `volume.stock_volume` | int | Volumen de acciones (0 para indices, real para stocks) |
| `volume.calls_volume` | int | **Volumen de opciones call** en ese minuto |
| `volume.puts_volume` | int | **Volumen de opciones put** en ese minuto |
| `volume.total_options_volume` | int | Volumen total de opciones |

### Put/Call Ratio intraday

Con los campos `calls_volume` y `puts_volume` se puede calcular el **Put/Call Ratio** minuto a minuto:

```
PCR = puts_volume / calls_volume
```

### Coverage

| Aspecto | Detalle |
|---------|---------|
| Periodo | Dia actual solamente |
| Resolucion | 1 minuto |
| Barras por dia | ~390 (6.5h * 60min) |
| Disponibilidad | Durante y despues del horario de mercado |

### Ejemplo

```bash
python scripts/fetch_cboe.py intraday _VIX
python scripts/fetch_cboe.py intraday _SPX
python scripts/fetch_cboe.py intraday GGAL
python scripts/fetch_cboe.py intraday _SPX -o spx_intraday.json
```

---

## 5. Futures — Cadena de Futuros

**Endpoint:** `GET https://www-api.cboe.com/us/futures/api/data/?symbol={symbol}`

Devuelve la cadena completa de futuros para un simbolo dado, con precios, settlement, volumen y open interest.

### Simbolos disponibles

| Simbolo | Descripcion | Coverage |
|---------|-------------|----------|
| `VX` | VIX Futures | 13+ contratos (~1 ano) |
| `VXM` | Mini VIX Futures | 6+ contratos |
| `VA` | S&P 500 Variance Futures | 8+ contratos |
| `IBHY` | iBoxx High Yield Corporate Bond Futures | 3+ contratos |
| `IBIG` | iBoxx Investment Grade Corporate Bond Futures | 2+ contratos |
| `IEMD` | iBoxx Emerging Market Bond Index Futures | 2+ contratos |

### Campos del response

```json
{
  "data": [
    {
      "symbol_id": "000jyc",
      "symbol": "VX/M6",
      "expiration": "06/17/2026",
      "open": 17.85,
      "last_price": 17.38,
      "high": 18.07,
      "low": 17.25,
      "prev_close": 17.81,
      "settlement": 17.6055,
      "prev_settlement": 17.6055,
      "change": -0.2255,
      "volume": 35231,
      "prev_open_int": 164149,
      "current_open_int": 0,
      "current_volume": 0,
      "root_symbol": false
    }
  ],
  "lastUpdate": "2026-06-04T10:43:56.738175-05:00"
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `symbol` | string | Nombre del contrato (ej: `VX/M6` = VX Junio 2026) |
| `expiration` | string | Fecha de vencimiento (MM/DD/YYYY) |
| `open` | float | Precio de apertura |
| `last_price` | float | Ultimo precio negociado |
| `high` | float | Maximo del dia |
| `low` | float | Minimo del dia |
| `prev_close` | float | Cierre anterior |
| `settlement` | float | **Precio de settlement** (referencia oficial) |
| `prev_settlement` | float | Settlement anterior |
| `change` | float/null | Cambio vs settlement anterior |
| `volume` | int | Volumen del dia |
| `prev_open_int` | int | **Open interest** del dia anterior |
| `root_symbol` | bool | `true` si es el simbolo raiz (no un contrato especifico) |

### Convencion de nombres de contratos

Los simbolos de futuros VX siguen el formato `VX/{CODIGO}` donde:

| Letra | Mes | Codigo |
|-------|-----|--------|
| M | Junio | 6 |
| N | Julio | 7 |
| Q | Agosto | 8 |
| U | Septiembre | 9 |
| V | Octubre | 10 |
| X | Noviembre | 11 |
| Z | Diciembre | 12 |
| F | Enero (proximo ano) | 1 |
| G | Febrero (proximo ano) | 2 |

Ejemplos: `VX/M6` = VIX Junio 2026, `VX/Z6` = VIX Diciembre 2026, `VX/F7` = VIX Enero 2027.

### Interpretacion

| Aspecto | Significado |
|---------|-------------|
| **Front-month** | Contrato con vencimiento mas cercano (ej: `VX/M6` = Jun 17) |
| **Segundo mes** | Siguiente contrato (ej: `VX/N6` = Jul 22) |
| **Settlement vs Last** | Diferencia indica si el contrato cotiza en premium/discount vs el valor oficial |
| **Open Interest alto** | Alta liquidez en ese contrato |
| **Term structure** | La curva de futuros VX (front month vs back months) indica contango/backwardation |

### VIX Futures Term Structure

La relacion entre los precios de los distintos contratos VX indica:

| Estado | Front < Back | Front > Back |
|--------|-------------|-------------|
| Nombre | Contango | Backwardation |
| Significado | Mercado espera que la volatilidad suba en el futuro | Volatilidad actual alta, se espera que baje |
| Tipico en | Mercados tranquilos | Mercados en crisis |

### Coverage temporal

| Simbolo | Contratos | Periodo |
|---------|-----------|---------|
| VX | 13+ | Jun 2026 - Feb 2027 |
| VXM | 6+ | Jun 2026 - Nov 2026 |
| VA | 8+ | Jun 2026 - Jun 2027 |
| IBHY | 3 | Sep 2026 - Mar 2027 |

### Ejemplo

```bash
python scripts/fetch_cboe.py futures VX
python scripts/fetch_cboe.py futures VXM
python scripts/fetch_cboe.py futures VA -q
```

---

## 6. Products — Productos Tradables

**Endpoint:** `GET https://www-api.cboe.com/tradable_products/data/`

Devuelve la lista completa de productos tradables en CBOE, organizados por categoria.

### Campos del response

```json
{
  "data": {
    "equity": [
      {
        "underlying_root": "SPX",
        "trading_dt": "2026-06-03",
        "volume": 4684651,
        "open_interest": 23950581,
        "title": "S&P 500 Index Options",
        "display": "full"
      },
      { "underlying_root": "OEX", "title": "S&P 100 Index Options", "display": "short", "category": "equity" }
    ],
    "volatility": [
      { "underlying_root": "VIX", "volume": 878594, "open_interest": 11796529, "title": "VIX Options", "display": "full" },
      { "underlying_root": "VX", "volume": 170983, "open_interest": 420313, "title": "VIX Futures", "display": "full" }
    ],
    "credit_interest": [
      { "underlying_root": "IBHY", "volume": 1477, "open_interest": 6961, "title": "iBoxx High Yield Bond Futures", "display": "full" }
    ],
    "international_equity": [
      { "underlying_root": "MXEF", "title": "MSCI Emerging Market Index Options", "display": "full" }
    ],
    "crypto": [
      { "underlying_root": "CBTX", "title": "Cboe Bitcoin U.S. ETF Index", "display": "full" }
    ]
  }
}
```

### Categorias

| Categoria | Descripcion | Ejemplos |
|-----------|-------------|----------|
| `equity` | Opciones sobre indices de acciones | SPX, XSP, RUT, OEX, DJX |
| `volatility` | Opciones y futuros de volatilidad | VIX, VX, VXM, VA, UX |
| `credit_interest` | Futuros de bonos corporativos | IBHY, IBIG, IEMD |
| `international_equity` | Opciones sobre indices internacionales | MXEF, MXEA |
| `crypto` | Indices y futuros crypto | CBTX, MBTX, XBTF |

### Campos

| Campo | Descripcion |
|-------|-------------|
| `underlying_root` | Simbolo raiz del producto |
| `title` | Nombre completo del producto |
| `volume` | Volumen del dia anterior (si disponible) |
| `open_interest` | Open interest (si disponible) |
| `display` | `full` = datos disponibles, `short` = solo referencia |
| `trading_dt` | Fecha de los datos de trading |

### Coverage

| Categoria | Productos |
|-----------|-----------|
| Equity | 8 productos |
| Volatility | 5 productos |
| Credit/Interest | 3 productos |
| International Equity | 2 productos |
| Crypto | 3 productos |

### Ejemplo

```bash
python scripts/fetch_cboe.py products
python scripts/fetch_cboe.py products -q
```

---

## 7. All — Fetch Combinado

El modo `all` ejecuta los endpoints disponibles para un simbolo secuencialmente: quote, historical, intraday y futures (si aplica).

### Output

```json
{
  "symbol": "_VIX",
  "timestamp": "2026-06-04T15:45:00",
  "quote": { ... },
  "historical": { ... },
  "intraday": { ... }
}
```

### Lo que incluye

| Componente | Descripcion |
|------------|-------------|
| `quote` | Cotizacion delayed del simbolo |
| `historical` | Datos historicos anuales (annual high/low, HV e IV) |
| `intraday` | Chart intraday 1-min |
| `futures` | Futuros (solo si el simbolo esta en la lista de futuros: VX, VXM, VA, IBHY, IBIG, IEMD) |

**Comportamiento:** Si un simbolo no soporta quote/intraday (ej: VX es solo futuros), el `all` mode lo maneja gracefulmente — registra un warning y continua con los demas endpoints.

### Tiempo estimado

| Simbolo | Tiempo |
|---------|--------|
| _VIX | ~3s |
| _SPX | ~3s |
| GGAL | ~3s |

### Ejemplo

```bash
python scripts/fetch_cboe.py all _VIX
python scripts/fetch_cboe.py all _SPX -o spx_all.json
```

---

## 8. Lookup — Busqueda de Simbolos

**Endpoint:** `GET https://ww2.cboe.com/us/equities/market_statistics/book_viewer_2/symbol_lookup_data/?mkt={market}`

Devuelve la lista completa de todos los simbolos negociables en CBOE con sus nombres de empresa. Esencialmente un directorio maestro de tickers.

### Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `mkt` | `bzx` | Mercado (`bzx`, `edgx`, etc.) |

### Campos del response

```json
{
  "symbolsLookupData": [
    { "name": "A", "company_name": "AGILENT TECHNOLOGIES INC COM" },
    { "name": "AA", "company_name": "ALCOA CORP COM" },
    { "name": "AAPL", "company_name": "APPLE INC COM" }
  ]
}
```

### Campos clave

| Campo | Descripcion |
|-------|-------------|
| `name` | Ticker del simbolo |
| `company_name` | Nombre completo de la empresa, ETF, unit o warrant |

### Coverage

| Aspecto | Detalle |
|---------|---------|
| Cantidad de simbolos | ~15,000+ |
| Tipos incluidos | Stocks, ETFs, Units, Warrants, Rights, ADRs |
| Actualizacion | Diaria |

### Notas

- El response es grande (~500KB+), puede tardar unos segundos en descargarse.
- El parametro `mkt` no parece cambiar los resultados significativamente (es el mismo universo de simbolos).
- Util para: construir un autocomplete de tickers, validar si un simbolo existe, obtener el company name.

### Ejemplo

```bash
python scripts/fetch_cboe.py lookup
python scripts/fetch_cboe.py lookup --market edgx -q
python scripts/fetch_cboe.py lookup -o cboe_symbols.json
```

---

## 9. Summary — Resumen de Mercado Equities

**Endpoint:** `GET https://www-api.cboe.com/us/equities/market_statistics/summary_lite/market/data/`

Devuelve un resumen del volumen de mercado de CBOE, desglosado por mercado operador (BZX, BYX, EDGX, EDGA) y por tape (A, B, C).

### Campos del response

```json
{
  "columns": [
    { "key": "tapea", "val": "Tape A (NYSE)" },
    { "key": "tapeb", "val": "Tape B (Regionals)" },
    { "key": "tapec", "val": "Tape C (Nasdaq)" },
    { "key": "total", "val": "Total" }
  ],
  "batsMarketData": [
    {
      "market": "BZX Equities",
      "marketID": "Z",
      "total": { "display": "422.2M", "value": 422233272, "percent": "3.61" },
      "tapea": { "display": "117.8M", "value": 117751133, "percent": "4.25" },
      "tapeb": { "display": "115.6M", "value": 115550730, "percent": "3.80" },
      "tapec": { "display": "188.9M", "value": 188931409, "percent": "3.22" }
    }
  ],
  "marketTotals": { "display": "2.2B", "value": 2170494820, "percent": "18.58" },
  "date": "Jun 04",
  "delay": 20,
  "ttl": 60000
}
```

### Campos clave

| Campo | Descripcion |
|-------|-------------|
| `columns` | Definicion de tapes: Tape A (NYSE), Tape B (Regionals), Tape C (Nasdaq) |
| `batsMarketData` | Array con datos por mercado operador |
| `batsMarketData[].market` | Nombre del mercado (Cboe Total, BZX Equities, BYX Equities, EDGX Equities, EDGA Equities) |
| `batsMarketData[].marketID` | ID del mercado (Z= BZX, Y= BYX, K= EDGX, J= EDGA) |
| `batsMarketData[].total.value` | Volumen total del mercado |
| `batsMarketData[].total.display` | Volumen formateado (ej: "422.2M") |
| `batsMarketData[].total.percent` | Market share porcentual |
| `tapea.value` | Volumen en Tape A (NYSE listings) |
| `tapeb.value` | Volumen en Tape B (Regional/Other listings) |
| `tapec.value` | Volumen en Tape C (Nasdaq listings) |
| `marketTotals` | Totales consolidados de todos los mercados CBOE |
| `date` | Fecha de los datos |
| `delay` | Minutos de delay |

### Mercados incluidos

| Mercado | Market ID | Descripcion |
|---------|-----------|-------------|
| Cboe Total | - | Total consolidado de todos los mercados CBOE |
| BZX Equities | Z | Principal exchange CBOE |
| BYX Equities | Y | Exchange secundario CBOE |
| EDGX Equities | K | Exchange EDGX |
| EDGA Equities | J | Exchange EDGA |

### Interpretacion de tapes

| Tape | Descripcion |
|------|-------------|
| Tape A | Acciones listadas en NYSE |
| Tape B | Acciones listadas en exchanges regionales (ARCA, etc.) |
| Tape C | Acciones listadas en Nasdaq |

### Ejemplo

```bash
python scripts/fetch_cboe.py summary
python scripts/fetch_cboe.py summary -q
```

---

## 10. Most Active — Top 10 Mas Activos (Equities)

**Endpoint:** `GET https://www-api.cboe.com/us/equities/market_statistics/most_active/data/10/?mkts={market}`

Devuelve los 10 simbolos mas activos por volumen en un mercado CBOE especifico. La API ignora el parametro N del path y siempre devuelve 10 resultados.

### Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `mkts` | - | Mercado (`bzx`, `byx`, `edgx`, `edga`) |

### Mercados disponibles

| Mercado | Parametro |
|---------|-----------|
| BZX | `bzx` |
| BYX | `byx` |
| EDGX | `edgx` |
| EDGA | `edga` |

### Campos del response

```json
{
  "success": "True",
  "ttl": 7500,
  "ts": "2026-06-04 13:47:17",
  "data": {
    "bzx": [
      ["SOXS","19277847","145955","5.13000000","5.14000000","144557","5.13000000","0.22000000","DIREXION SHARES ETF TRUST DAI SEM 3X ETF"],
      ["NVDA","4148291","410","219.21000000","219.23000000","30","219.26000000","4.76000000","NVIDIA CORPORATION COM"]
    ]
  },
  "mo": true
}
```

### Campos clave

Cada elemento en `data.{market}` es un array con 9 posiciones:

| Indice | Campo | Tipo | Descripcion |
|--------|-------|------|-------------|
| [0] | symbol | string | Ticker |
| [1] | volume | string | Volumen acumulado del dia |
| [2] | - | string | (dato interno no documentado) |
| [3] | bid | string | Bid price |
| [4] | ask | string | Ask price |
| [5] | - | string | (dato interno no documentado) |
| [6] | last_price | string | Ultimo precio negociado |
| [7] | price_change | string | Cambio neto en USD |
| [8] | company_name | string | Nombre de la empresa |

### Coverage

| Aspecto | Detalle |
|---------|---------|
| Cantidad | Siempre 10 resultados (la API ignora el parametro N) |
| Mercados | BZX, BYX, EDGX, EDGA |
| Columnas por simbolo | 9 campos |
| Actualizacion | Tiempo real (con delay de 20 min) |

### Ejemplo

```bash
python scripts/fetch_cboe.py most-active                    # Top 10 BZX
python scripts/fetch_cboe.py most-active --market edgx      # Top 10 EDGX
python scripts/fetch_cboe.py most-active --market byx       # Top 10 BYX
python scripts/fetch_cboe.py most-active --market edga -q   # Top 10 EDGA
```

---

## 11. Options Summary — Resumen de Mercado Opciones

**Endpoint:** `GET https://www-api.cboe.com/us/options/market_statistics/summary_lite/market/data/`

Devuelve un resumen del volumen de mercado de opciones CBOE, desglosado por exchange.

### Parametros

Sin parametros.

### Campos del response

```json
{
  "date": "Jun 04",
  "batsMarketData": [
    {
      "market": "Cboe Options Exchange",
      "marketID": "C",
      "volumeFormatted": "9,285,577",
      "volume": 9285577.0,
      "percent": "17.36"
    },
    {
      "market": "Cboe C2 Options Exchange",
      "marketID": "W",
      "volumeFormatted": "1,192,784",
      "volume": 1192784.0,
      "percent": "2.23"
    },
    {
      "market": "Cboe EDGX Options Exchange",
      "marketID": "E",
      "volumeFormatted": "2,686,069",
      "volume": 2686069.0,
      "percent": "5.02"
    },
    {
      "market": "Cboe BZX Options Exchange",
      "marketID": "Z",
      "volumeFormatted": "2,153,836",
      "volume": 2153836.0,
      "percent": "4.03"
    }
  ],
  "delay": 20,
  "ttl": 60000
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `date` | string | Fecha de los datos |
| `batsMarketData` | array | Datos por exchange de opciones |
| `batsMarketData[].market` | string | Nombre del exchange (Cboe Options, C2, EDGX, BZX) |
| `batsMarketData[].marketID` | string | ID del exchange (C, W, E, Z) |
| `batsMarketData[].volume` | float | Volumen total del exchange |
| `batsMarketData[].volumeFormatted` | string | Volumen formateado (ej: "9,285,577") |
| `batsMarketData[].percent` | string | Market share porcentual |
| `delay` | int | Minutos de delay |

### Exchanges incluidos

| Exchange | Market ID | Descripcion |
|----------|-----------|-------------|
| Cboe Options Exchange | C | Exchange principal de opciones CBOE |
| Cboe C2 Options Exchange | W | Exchange C2 |
| Cboe EDGX Options Exchange | E | Exchange EDGX opciones |
| Cboe BZX Options Exchange | Z | Exchange BZX opciones |

### Ejemplo

```bash
python scripts/fetch_cboe.py options-summary
python scripts/fetch_cboe.py options-summary -q
```

---

## 12. Options Most Active — Top N Opciones Mas Activas

**Endpoint:** `GET https://www-api.cboe.com/us/options/market_statistics/most_active/data/?mkt=cone&limit={N}`

Devuelve las opciones mas activas por volumen, separadas en calls y puts, agrupadas por categoria.

### Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `mkt` | - | Mercado. Solo `cone` funciona (otros valores retornan 404) |
| `limit` | 25 | Cantidad de resultados por calls/puts por categoria. Solo acepta: **10, 25, 50, 100** |

### Valores de limit

| Valor | Resultado |
|-------|-----------|
| `10` | 10 calls + 10 puts por categoria |
| `25` | 25 calls + 25 puts por categoria (default) |
| `50` | 50 calls + 50 puts por categoria |
| `100` | 100 calls + 100 puts por categoria |
| Otro | Ignorado, devuelve 25 (default) |

### Categorias

El response incluye 3 categorias:

| Categoria | Display | Descripcion |
|-----------|---------|-------------|
| `all` | All Options | Todas las opciones (indices + equities) |
| `index` | Index Options | Opciones sobre indices (SPX, VIX, etc.) |
| `equity` | Equity Options | Opciones sobre acciones individuales |

### Campos del response

```json
{
  "limit": 10,
  "description": "The current, most actively traded options on the Cboe Options Exchange.",
  "categories": [
    {
      "category": "all",
      "display": "All Options",
      "calls": [
        {
          "symbol": "SPXW",
          "expires": "2026-06-04",
          "strike": 7600.0,
          "volume": 132380
        }
      ],
      "puts": [
        {
          "symbol": "SPXW",
          "expires": "2026-06-04",
          "strike": 7550.0,
          "volume": 58172
        }
      ]
    },
    {
      "category": "index",
      "display": "Index Options",
      "calls": [...],
      "puts": [...]
    },
    {
      "category": "equity",
      "display": "Equity Options",
      "calls": [...],
      "puts": [...]
    }
  ]
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `limit` | int | Limite efectivo aplicado |
| `description` | string | Descripcion del endpoint |
| `categories` | array | Array de categorias (all, index, equity) |
| `categories[].category` | string | Nombre de la categoria |
| `categories[].display` | string | Nombre para mostrar |
| `categories[].calls` | array | Top N calls mas activas |
| `categories[].puts` | array | Top N puts mas activas |
| `calls/puts[].symbol` | string | Simbolo del underlying (SPXW, SPY, VIX, QQQ, etc.) |
| `calls/puts[].expires` | string | Fecha de expiracion (YYYY-MM-DD) |
| `calls/puts[].strike` | float | Strike price |
| `calls/puts[].volume` | int | Volumen del dia |

### Underings mas frecuentes

| Simbolo | Descripcion |
|---------|-------------|
| `SPXW` | S&P 500 Index Weeklys |
| `SPY` | SPDR S&P 500 ETF |
| `QQQ` | Invesco QQQ Trust |
| `VIX` | CBOE Volatility Index |
| `IWM` | iShares Russell 2000 ETF |
| `AAPL` | Apple Inc |

### Ejemplo

```bash
python scripts/fetch_cboe.py options-most-active              # Top 25 (default)
python scripts/fetch_cboe.py options-most-active --limit 10   # Top 10
python scripts/fetch_cboe.py options-most-active --limit 50   # Top 50
python scripts/fetch_cboe.py options-most-active --limit 100  # Top 100
python scripts/fetch_cboe.py options-most-active --limit 10 -q
python scripts/fetch_cboe.py options-most-active -o options_active.json
```

---

## 13. Options Chain — Cadena de Opciones Completa

**Endpoint:** `GET https://cdn.cboe.com/api/global/delayed_quotes/options/{symbol}.json`

Devuelve la cotizacion del simbolo + la cadena completa de opciones (calls y puts) con greeks, volumen, open interest y precios. Solo funciona para **stocks y ETFs** (no para indices con prefijo `_`).

### Parametros

| Parametro | Descripcion |
|-----------|-------------|
| `{symbol}` | Simbolo del stock/ETF (ej: GGAL, AAPL, BMA, SPY, QQQ) |

### Coverage

| Simbolo | Contratos | Tamaño |
|---------|-----------|--------|
| GGAL | ~250 | ~160KB |
| BMA | ~162 | ~103KB |
| AAPL | ~3,600 | ~2.3MB |
| SPY | ~6,000+ | ~4MB+ |

### Formato del ticker de opciones

Cada contrato tiene un ticker con formato: `ROOT` + `YYMMDD` + `C/P` + `strike*1000` (8 digitos, zero-padded).

Ejemplos:

| Ticker | Root | Expiry | Tipo | Strike |
|--------|------|--------|------|--------|
| `GGAL260618C00030000` | GGAL | 2026-06-18 | Call | 30.0 |
| `GGAL260618P00055000` | GGAL | 2026-06-18 | Put | 55.0 |
| `GGAL260717C00045000` | GGAL | 2026-07-17 | Call | 45.0 |
| `AAPL260605C00300000` | AAPL | 2026-06-05 | Call | 300.0 |

Usar `parse_option_ticker(ticker)` del script para decodificar automaticamente.

### Campos del response

```json
{
  "timestamp": "2026-06-04 19:02:22",
  "data": {
    "symbol": "GGAL",
    "security_type": "stock",
    "current_price": 49.17,
    "options": [
      {
        "option": "GGAL260618C00030000",
        "bid": 18.6,
        "ask": 22.5,
        "iv": 1.4846,
        "delta": 0.9966,
        "gamma": 0.0017,
        "vega": 0.001,
        "theta": -0.0032,
        "rho": 0.0022,
        "theo": 20.3486,
        "volume": 0.0,
        "open_interest": 0.0,
        "last_trade_price": 0.0,
        "last_trade_time": null,
        "change": 0.0,
        "open": 0.0,
        "high": 0.0,
        "low": 0.0,
        "prev_day_close": 21.3999996185303,
        "percent_change": 0.0,
        "tick": "no_change",
        "bid_size": 2.0,
        "ask_size": 2.0
      }
    ]
  },
  "symbol": "GGAL"
}
```

### Campos clave (quote)

El response incluye los mismos campos que `quote` para el underlying.

### Campos clave (options)

Cada contrato en `data.options[]`:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `option` | string | Ticker del contrato (decodificar con parse_option_ticker) |
| `bid` | float | Bid price |
| `ask` | float | Ask price |
| `bid_size` | float | Bid size |
| `ask_size` | float | Ask size |
| `iv` | float | Volatilidad implicita |
| `delta` | float | Delta |
| `gamma` | float | Gamma |
| `theta` | float | Theta |
| `vega` | float | Vega |
| `rho` | float | Rho |
| `theo` | float | Precio teorico |
| `volume` | float | Volumen del dia |
| `open_interest` | float | Open interest |
| `last_trade_price` | float | Ultimo precio negociado |
| `last_trade_time` | string/null | Ultima operacion (ISO) |
| `change` | float | Cambio neto |
| `prev_day_close` | float | Cierre anterior |
| `percent_change` | float | Cambio porcentual |
| `open` | float | Apertura |
| `high` | float | Maximo |
| `low` | float | Minimo |
| `tick` | string | `up` / `down` / `no_change` |

### Ejemplo

```bash
python scripts/fetch_cboe.py options-chain GGAL
python scripts/fetch_cboe.py options-chain AAPL
python scripts/fetch_cboe.py options-chain BMA -o bma_chain.json
python scripts/fetch_cboe.py options-chain SPY -q
```

---

## 14. Options Directory — Instrumentos Listados con Opciones

**Endpoint (Cboe Options):** `GET https://www-api.cboe.com/us/options/symboldir/equity-index-options/data/?dt={date}&sid={letter}`

**Endpoint (EDGX Options):** `GET https://www-api.cboe.com/us/options/symboldir/edgx-equity-index-options/data/?dt={date}&sid={letter}`

Devuelve el directorio de todos los instrumentos (stocks, ETFs, indices) que tienen opciones listadas en CBOE, con el market maker asignado y datos del trading floor.

### Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `dt` | Ultima fecha disponible | Fecha en formato YYYY-MM-DD |
| `sid` | Todos | Letra inicial del company_name (A-Z). Filtra por pagina alfabetica |

Ambos parametros son opcionales. Sin parametros devuelve todos los instrumentos (~5,500).

### Exchanges disponibles

| Exchange | Endpoint path | Diferencias |
|----------|---------------|-------------|
| Cboe Options | `equity-index-options` | Incluye `post_station` y `gth_mm` |
| EDGX Options | `edgx-equity-index-options` | Sin `post_station` ni `gth_mm` |

### Coverage por letra (Cboe Options)

| sid | Instrumentos | sid | Instrumentos | sid | Instrumentos |
|-----|-------------|-----|-------------|-----|-------------|
| A | ~461 | J | ~51 | S | ~435 |
| B | ~220 | K | ~100 | T | ~407 |
| C | ~411 | L | ~150 | U | ~86 |
| D | ~220 | M | ~199 | V | ~219 |
| E | ~186 | N | ~169 | W | ~137 |
| F | ~263 | O | ~107 | X | ~21 |
| G | ~261 | P | ~338 | Y | ~13 |
| H | ~118 | Q | ~22 | Z | ~25 |
| I | ~454 | R | ~204 | | |

Total: ~5,500 instrumentos con opciones listadas.

### Campos del response

```json
{
  "data": [
    {
      "company_name": "BANCO MACRO S A SPON ADR B",
      "underlying": "BMA",
      "pmm": "Wolverine Trading, LLC",
      "prod_types": "",
      "cycles": 0,
      "post_station": "1/1",
      "gth_mm": "-"
    }
  ]
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `underlying` | string | Ticker del instrumento |
| `company_name` | string | Nombre completo de la empresa/ETF |
| `pmm` | string | Primary Market Maker asignado |
| `post_station` | string | Post/Station en el trading floor (solo Cboe Options) |
| `gth_mm` | string | GTH Market Maker (solo Cboe Options) |
| `prod_types` | string | Tipos de producto |
| `cycles` | int | Ciclos de vencimiento |

### Market Makers frecuentes

| Market Maker | Nombre |
|-------------|--------|
| Citadel Securities LLC | Citadel |
| Susquehanna Securities, LLC | Susquehanna |
| Wolverine Trading, LLC | Wolverine |
| Group One Trading LLC | Group One |
| IMC-Chicago, LLC | IMC |
| Jane Street Capital, LLC | Jane Street |
| Belvedere Trading LLC | Belvedere |
| Simplex Trading, LLC | Simplex |

### Ejemplo

```bash
# Todos los instrumentos con opciones (Cboe Options)
python scripts/fetch_cboe.py options-directory

# Filtrar por letra inicial
python scripts/fetch_cboe.py options-directory --sid G

# EDGX Options
python scripts/fetch_cboe.py options-directory --exchange edgx

# Fecha especifica + filtro
python scripts/fetch_cboe.py options-directory --date 2026-01-02 --sid A

# Guardar a archivo
python scripts/fetch_cboe.py options-directory -o options_dir.json

# EDGX + filtro
python scripts/fetch_cboe.py options-directory --exchange edgx --sid B -q
```

---

## 15. Futures Products — Productos Futuros Tradables

**Endpoint:** `GET https://www-api.cboe.com/us/futures/api/tradable_future_products_data/`

Devuelve la lista completa de productos futuros tradables en CBOE, con volumen y open interest del dia anterior.

### Parametros

Sin parametros.

### Campos del response

```json
{
  "data": {
    "products": [
      {
        "underlying_root": "VX",
        "trading_dt": "2026-06-03",
        "volume": 170983,
        "open_interest": 420313,
        "title": "VIX Futures",
        "display": "full"
      }
    ]
  }
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `underlying_root` | string | Simbolo raiz del producto |
| `title` | string | Nombre completo del producto |
| `trading_dt` | string | Fecha de los datos de trading (YYYY-MM-DD) |
| `volume` | int | Volumen del dia anterior |
| `open_interest` | int | Open interest |
| `display` | string | `full` = datos disponibles |

### Productos incluidos (15)

| Root | Descripcion |
|------|-------------|
| `VX` | VIX Futures |
| `VXM` | Mini VIX Futures |
| `VA` | S&P 500 Variance Futures |
| `IBHY` | iBoxx High Yield Corporate Bond Futures |
| `IBYO` | Options on IBHY Futures |
| `IBIG` | iBoxx Investment Grade Corporate Bond Futures |
| `IBGO` | Options on IBIG Futures |
| `IEMD` | iBoxx Emerging Market Bond Index Futures |
| `UX` | Options on VIX Futures |
| `XBTF` | FTSE Bitcoin Index Futures |
| `FBT` | Financially Settled Bitcoin Futures |
| `FET` | Financially Settled Ether Futures |
| `MGTN` | Magnificent 10 Futures |
| `PBT` | Physically Settled Bitcoin Futures |
| `PET` | Physically Settled Ether Futures |

### Ejemplo

```bash
python scripts/fetch_cboe.py futures-products
python scripts/fetch_cboe.py futures-products -q
python scripts/fetch_cboe.py futures-products -o futures_products.json
```

---

## 16. Consideraciones Tecnicas

### Delay de los datos

Todos los datos son **delayed** (no en tiempo real). El delay varia por endpoint:

| Endpoint | Delay | Detalle |
|----------|-------|---------|
| `quote` | ~15-20 min | El campo `timestamp` indica la ultima actualizacion del cache CDN |
| `historical` | ~1 dia | Datos actualizados una vez al dia (muestra fecha del dia anterior) |
| `intraday` | ~15-20 min | El campo `timestamp` indica la ultima actualizacion del cache CDN |
| `options-chain` | ~15-20 min / EOD | El quote del underlying se actualiza intraday (~15-20 min). Los datos de opciones individuales (precios, greeks, volumen) pueden ser end-of-day |
| `summary` | 20 min | Campo `delay: 20` explicito en el response |
| `options-summary` | 20 min | Campo `delay: 20` explicito en el response |
| `most-active` | 20 min | Mismo origen que summary |
| `options-most-active` | ~15-20 min | Sin campo delay explicito |
| `futures` | ~15-20 min | Campo `lastUpdate` con timestamp de la ultima actualizacion |
| `products` / `futures-products` | 1 dia | Datos del dia anterior (campo `trading_dt`) |
| `lookup` | 1 dia | Directorio actualizado diariamente |

**Nota:** El campo `timestamp` en las respuestas del CDN indica cuando se actualizo el cache, no el delay本身. Para estimar el delay real, comparar `last_trade_time` con la hora actual.