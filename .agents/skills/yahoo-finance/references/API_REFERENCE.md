# Yahoo Finance API Reference Completa

> Documentación exhaustiva de los endpoints no oficiales de Yahoo Finance.
> Actualizada a Junio 2026 — basada en ingeniería inversa de `yfinance` y testing directo.

---

## Índice

1. [Autenticación: Cookie + Crumb](#1-autenticación-cookie--crumb)
2. [v8/finance/chart — Históricos OHLCV](#2-v8financechart--históricos-ohlcv)
3. [v7/finance/quote — Precio en tiempo real](#3-v7financequote--precio-en-tiempo-real)
4. [v10/finance/quoteSummary — Fundamentos](#4-v10financequotesummary--fundamentos)
5. [v7/finance/options — Cadena de opciones](#5-v7financeoptions--cadena-de-opciones)
6. [v1/finance/search — Búsqueda y noticias](#6-v1financesearch--búsqueda-y-noticias)
7. [v6/finance/recommendationsbysymbol — Recomendaciones](#7-v6financerecommendationsbysymbol--recomendaciones)
8. [v1/finance/trending — Trending symbols](#8-v1financetrending--trending-symbols)
9. [v1/finance/lookup — Lookup de tickers](#9-v1financelookup--lookup-de-tickers)
10. [v1/finance/screener — Screener](#10-v1financescreener--screener)
11. [WebSocket streaming](#11-websocket-streaming)
12. [Rate Limiting y Estrategias](#12-rate-limiting-y-estrategias)
13. [Códigos de Error y Troubleshooting](#13-códigos-de-error-y-troubleshooting)
14. [Tickers Internacionales](#14-tickers-internacionales)
15. [Campos Comunes entre Endpoints](#15-campos-comunes-entre-endpoints)

---

## 1. Autenticación: Cookie + Crumb

Yahoo usa un sistema **cookie + crumb** para proteger ciertos endpoints contra bots.
No es OAuth ni requiere API key — es un CSRF token casero.

### Flujo completo

```
  Cliente                          Yahoo
    |                                |
    |  GET https://fc.yahoo.com      |
    |-------------------------------->|
    |  Set-Cookie: A3=XXXXXXXXX...   |
    |<--------------------------------|
    |                                |
    |  GET /v1/test/getcrumb         |
    |  (con cookie A3)               |
    |-------------------------------->|
    |  crumb: "abcdef123456"         |
    |<--------------------------------|
    |                                |
    |  GET /v7/finance/quote         |
    |  ?crumb=abcdef123456           |
    |-------------------------------->|
    |  JSON con datos                |
    |<--------------------------------|
```

### Implementación en Python

```python
import requests

BASE = "https://query1.finance.yahoo.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def yahoo_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get("https://fc.yahoo.com", timeout=10)          # paso 1: obtener cookie A3
    crumb = s.get(f"{BASE}/v1/test/getcrumb", timeout=10).text.strip()  # paso 2: obtener crumb
    s.params = {"crumb": crumb}                         # paso 3: adjuntar crumb a todas las requests
    return s
```

### Endpoints que requieren crumb

| Endpoint | Requiere crumb |
|----------|:--------------:|
| `v8/finance/chart` | ❌ No |
| `v7/finance/quote` | ✅ Sí |
| `v10/finance/quoteSummary` | ✅ Sí |
| `v7/finance/options` | ✅ Sí |
| `v1/finance/search` | ❌ No |
| `v6/finance/recommendationsbysymbol` | ✅ Sí |
| `v1/finance/trending` | ❌ No |
| `v1/finance/lookup` | ❌ No |
| `v1/finance/screener` | ✅ Sí (a veces) |

### El crumb expira

- El crumb tiene validez de ~unos minutos a varias horas.
- No hay un TTL documentado. Si recibís `{"finance":{"error":{"code":"Bad Request"}}}`, hay que regenerar el crumb.
- Estrategia segura: crear una nueva sesión por cada request que requiera crumb, o cachear y reintentar si falla.

---

## 2. v8/finance/chart — Históricos OHLCV

### Endpoint

```
GET https://query1.finance.yahoo.com/v8/finance/chart/{symbol}
```

### Parámetros

| Parámetro | Valores | Obligatorio | Descripción |
|-----------|---------|:-----------:|-------------|
| `range` | `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max` | No* | Período de tiempo |
| `interval` | `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `1h`, `1d`, `1wk`, `1mo` | Sí | Frecuencia de los datos |
| `period1` | Unix timestamp | No* | Fecha de inicio (alternativa a `range`) |
| `period2` | Unix timestamp | No* | Fecha de fin (default: now) |
| `events` | `div`, `splits`, `div,splits` | No | Incluir dividendos y/o splits |
| `includePrePost` | `true`, `false` | No | Incluir datos pre/post market (intraday) |

\* Usar `range` o `period1`/`period2`, no ambos.

### Combinaciones range/interval válidas

Típicamente Yahoo limita qué intervalos podés usar según el rango:

| Range | Intervales válidos |
|-------|-------------------|
| `1d` | `1m`, `2m`, `5m` |
| `5d` | `1m`, `2m`, `5m`, `15m`, `30m` |
| `1mo` | `1m`, `5m`, `15m`, `30m`, `60m`, `1h`, `1d` |
| `3mo` | `1d`, `1wk` |
| `6mo` | `1d`, `1wk` |
| `1y` | `1d`, `1wk` |
| `2y` | `1d`, `1wk`, `1mo` |
| `5y` | `1d`, `1wk`, `1mo` |
| `max` | `1d`, `1wk`, `1mo` |

**Nota:** Intraday (`1m`, `5m`) solo retiene 7-60 días de datos.

### Respuesta JSON

```json
{
  "chart": {
    "result": [
      {
        "meta": {
          "currency": "USD",
          "symbol": "AAPL",
          "exchangeName": "NMS",
          "instrumentType": "EQUITY",
          "firstTradeDate": 345479400,
          "regularMarketTime": 1717439040,
          "regularMarketPrice": 196.89,
          "regularMarketOpen": 195.19,
          "regularMarketDayHigh": 197.92,
          "regularMarketDayLow": 194.81,
          "regularMarketVolume": 45200000,
          "regularMarketPreviousClose": 194.50,
          "gmtoffset": -14400,
          "timezone": "EDT",
          "exchangeTimezoneName": "America/New_York",
          "chartPreviousClose": 194.50,
          "previousClose": 194.50,
          "scale": 3,
          "priceHint": 2,
          "currentTradingPeriod": {
            "pre": {
              "timezone": "EDT",
              "start": 1717401600,
              "end": 1717421400,
              "gmtoffset": -14400
            },
            "regular": {
              "timezone": "EDT",
              "start": 1717421400,
              "end": 1717444800,
              "gmtoffset": -14400
            },
            "post": {
              "timezone": "EDT",
              "start": 1717444800,
              "end": 1717459200,
              "gmtoffset": -14400
            }
          },
          "dataGranularity": "1d",
          "range": "1mo",
          "validRanges": ["1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"]
        },
        "timestamp": [1715904000, 1715990400, 1716076800, ...],
        "indicators": {
          "quote": [
            {
              "open": [189.43, 187.70, 189.02, ...],
              "high": [190.68, 188.70, 190.00, ...],
              "low": [187.88, 186.80, 188.33, ...],
              "close": [189.66, 188.27, 189.83, ...],
              "volume": [34600800, 30563400, 29645200, ...]
            }
          ],
          "adjclose": [
            {
              "adjclose": [189.56, 188.17, 189.73, ...]
            }
          ]
        },
        "events": {
          "dividends": {
            "1718323200": {
              "amount": 0.25,
              "date": 1718323200
            }
          },
          "splits": {
            "1598572800": {
              "date": 1598572800,
              "numerator": 4,
              "denominator": 1,
              "splitRatio": "4:1"
            }
          }
        }
      }
    ],
    "error": null
  }
}
```

### Cómo parsear

```python
r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AAPL",
                 params={"range": "1y", "interval": "1d", "events": "div,splits"},
                 headers=HEADERS)
data = r.json()
result = data["chart"]["result"][0]

# Timestamps
timestamps = result["timestamp"]

# OHLCV como arrays paralelos
opens = result["indicators"]["quote"][0]["open"]
highs = result["indicators"]["quote"][0]["high"]
lows = result["indicators"]["quote"][0]["low"]
closes = result["indicators"]["quote"][0]["close"]
volumes = result["indicators"]["quote"][0]["volume"]

# Precios ajustados
adj_closes = result["indicators"]["adjclose"][0]["adjclose"]

# Meta
meta = result["meta"]
print(meta["symbol"], meta["currency"], meta["regularMarketPrice"])

# Eventos
events = result.get("events", {})
dividends = events.get("dividends", {})
splits = events.get("splits", {})
```

### Arrays paralelos

Los datos vienen como arrays paralelos indexados por timestamp. Para convertirlos a filas:

```python
rows = []
for i in range(len(timestamps)):
    rows.append({
        "date": datetime.fromtimestamp(timestamps[i], tz=timezone.utc),
        "open": opens[i],
        "high": highs[i],
        "low": lows[i],
        "close": closes[i],
        "volume": volumes[i],
        "adjclose": adj_closes[i],
    })
```

### Dividendos y splits

Los dividendos y splits vienen en un formato diferente (mapeados por timestamp como string):

```python
for ts_str, div in dividends.items():
    print(f"Divi: ${div['amount']} en {datetime.fromtimestamp(int(ts_str))}")

for ts_str, split in splits.items():
    print(f"Split: {split['numerator']}:{split['denominator']} "
          f"en {datetime.fromtimestamp(int(ts_str))}")
```

### Notas importantes sobre v8/chart

- **Es el endpoint más estable** de Yahoo Finance. Funciona sin autenticación.
- **User-Agent es obligatorio.** Sin un User-Agent de navegador, Yahoo devuelve error o datos vacíos.
- **No usar con `yfinance`** — este skill usa requests directas.
- Los `null` aparecen cuando no hay trading (fines de semana, feriados).
- `adjclose` es crucial para backtesting porque ajusta por splits y dividendos.

---

## 3. v7/finance/quote — Precio en tiempo real

### Endpoint

```
GET https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol1},{symbol2},...
```

**Requiere crumb** (ver sección [Autenticación](#1-autenticación-cookie--crumb)).

### Parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `symbols` | Ticker(s) separados por coma (ej: `AAPL,MSFT,GOOGL`) |
| `crumb` | Token de autenticación (se pasa automático con `yahoo_session()`) |

### Respuesta JSON

```json
{
  "quoteResponse": {
    "result": [
      {
        "language": "en-US",
        "region": "US",
        "quoteType": "EQUITY",
        "typeDisp": "Equity",
        "quoteSourceName": "Nasdaq Real Time Price",
        "triggerable": true,
        "customPriceAlertConfidence": "HIGH",
        "currency": "USD",
        "exchange": "NMS",
        "shortName": "Apple Inc.",
        "longName": "Apple Inc.",
        "messageBoardId": "finmb_24937",
        "exchangeTimezoneName": "America/New_York",
        "exchangeTimezoneShortName": "EDT",
        "gmtOffSetMilliseconds": -14400000,
        "market": "us_market",
        "marketState": "REGULAR",
        "esgPopulated": true,
        "firstTradeDateMilliseconds": 345479400000,
        "priceHint": 2,
        "regularMarketChange": {
          "raw": 2.39,
          "fmt": "2.39"
        },
        "regularMarketChangePercent": {
          "raw": 1.2284,
          "fmt": "1.23%"
        },
        "regularMarketPrice": {
          "raw": 196.89,
          "fmt": "196.89"
        },
        "regularMarketDayHigh": {
          "raw": 197.92,
          "fmt": "197.92"
        },
        "regularMarketDayLow": {
          "raw": 194.81,
          "fmt": "194.81"
        },
        "regularMarketVolume": {
          "raw": 45200000,
          "fmt": "45.2M"
        },
        "regularMarketPreviousClose": {
          "raw": 194.50,
          "fmt": "194.50"
        },
        "regularMarketOpen": {
          "raw": 195.19,
          "fmt": "195.19"
        },
        "averageDailyVolume3Month": {
          "raw": 50300000,
          "fmt": "50.3M"
        },
        "averageDailyVolume10Day": {
          "raw": 42100000,
          "fmt": "42.1M"
        },
        "fiftyTwoWeekLowChange": {
          "raw": 55.68,
          "fmt": "55.68"
        },
        "fiftyTwoWeekLowChangePercent": {
          "raw": 0.3943,
          "fmt": "39.43%"
        },
        "fiftyTwoWeekRange": {
          "raw": "141.21 - 199.62",
          "fmt": "141.21 - 199.62"
        },
        "fiftyTwoWeekHighChange": {
          "raw": -2.73,
          "fmt": "-2.73"
        },
        "fiftyTwoWeekHighChangePercent": {
          "raw": -0.0137,
          "fmt": "-1.37%"
        },
        "fiftyTwoWeekLow": {
          "raw": 141.21,
          "fmt": "141.21"
        },
        "fiftyTwoWeekHigh": {
          "raw": 199.62,
          "fmt": "199.62"
        },
        "dividendDate": 1718323200,
        "earningsTimestamp": 1717459200,
        "earningsTimestampStart": 1717459200,
        "earningsTimestampEnd": 1717459200,
        "earningsCallTimestampStart": 1717466400,
        "earningsCallTimestampEnd": 1717466400,
        "isEarningsDateEstimate": false,
        "trailingAnnualDividendRate": {
          "raw": 1.0,
          "fmt": "1.00"
        },
        "trailingPE": {
          "raw": 29.86,
          "fmt": "29.86"
        },
        "trailingAnnualDividendYield": {
          "raw": 0.0051,
          "fmt": "0.51%"
        },
        "marketCap": {
          "raw": 3020000000000,
          "fmt": "3.02T"
        },
        "tradeable": false
      }
    ],
    "error": null
  }
}
```

### Campos clave del quote

| Campo Ruta | Tipo | Descripción |
|-----------|------|-------------|
| `regularMarketPrice.raw` | float | Precio actual |
| `regularMarketChangePercent.raw` | float | Cambio % (ej: 1.23 = +1.23%) |
| `regularMarketVolume.raw` | int | Volumen del día |
| `regularMarketOpen.raw` | float | Apertura |
| `regularMarketDayHigh.raw` | float | Máximo del día |
| `regularMarketDayLow.raw` | float | Mínimo del día |
| `regularMarketPreviousClose.raw` | float | Cierre anterior |
| `fiftyTwoWeekHigh.raw` | float | Máximo 52 semanas |
| `fiftyTwoWeekLow.raw` | float | Mínimo 52 semanas |
| `marketCap.raw` | int | Capitalización bursátil |
| `trailingPE.raw` | float | P/E ratio trailing |
| `trailingAnnualDividendYield.raw` | float | Dividend yield |
| `trailingAnnualDividendRate.raw` | float | Dividendo anual |
| `dividendDate` | int | Próximo dividendo (Unix timestamp) |
| `earningsTimestamp` | int | Próximo earnings (Unix timestamp) |
| `shortName` | string | Nombre corto |
| `longName` | string | Nombre largo |
| `exchange` | string | Exchange (NMS, NYQ, NASDAQ, etc.) |
| `marketState` | string | `PRE`, `REGULAR`, `POST`, `CLOSED` |
| `currency` | string | Moneda (USD, ARS, etc.) |
| `averageDailyVolume3Month.raw` | int | Volumen promedio 3 meses |

### Notas

- Los campos con `raw` y `fmt` son consistentes en todos los endpoints: `raw` es el valor numérico, `fmt` es el string formateado para mostrar.
- `marketState` es útil para saber si el mercado está abierto.
- `esgPopulated` indica si hay datos ESG disponibles.

---

## 4. v10/finance/quoteSummary — Fundamentos

### Endpoint

```
GET https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules={mod1},{mod2}
```

**Requiere crumb.**

### Módulos disponibles (33 total)

| # | Módulo | Descripción | Tamaño típico |
|---|--------|-------------|:------------:|
| 1 | `assetProfile` | Perfil completo: sector, industria, empleados, descripción, direcciones | Grande |
| 2 | `summaryProfile` | Resumen del perfil (versión corta) | Pequeño |
| 3 | `financialData` | Métricas financieras: EBITDA, revenue, profit margins, ROE, ROA, debt/equity | Mediano |
| 4 | `defaultKeyStatistics` | Estadísticas: beta, market cap, shares outstanding, float, short ratio | Mediano |
| 5 | `incomeStatementHistory` | Estado de resultados (varios años) | Grande |
| 6 | `incomeStatementHistoryQuarterly` | Estado de resultados trimestral | Grande |
| 7 | `balanceSheetHistory` | Balance general (varios años) | Grande |
| 8 | `balanceSheetHistoryQuarterly` | Balance general trimestral | Grande |
| 9 | `cashflowStatementHistory` | Flujo de caja (varios años) | Grande |
| 10 | `cashflowStatementHistoryQuarterly` | Flujo de caja trimestral | Grande |
| 11 | `earnings` | Ganancias históricas por trimestre | Mediano |
| 12 | `earningsHistory` | EPS reportado vs estimado por trimestre | Mediano |
| 13 | `earningsTrend` | Estimados de EPS futuros | Mediano |
| 14 | `recommendationTrend` | Recomendaciones: strong buy, buy, hold, sell por período | Mediano |
| 15 | `upgradeDowngradeHistory` | Historia de cambios de recomendación | Mediano |
| 16 | `insiderTransactions` | Transacciones de insider (compra/venta) | Mediano |
| 17 | `insiderHolders` | Tenedores insider y sus participaciones | Pequeño |
| 18 | `institutionOwnership` | Tenencia de instituciones, cambios, % | Mediano |
| 19 | `fundOwnership` | Tenencia de fondos mutuos | Mediano |
| 20 | `majorDirectHolders` | Mayores tenedores directos | Pequeño |
| 21 | `majorHoldersBreakdown` | % institutional, insider, público, otros | Pequeño |
| 22 | `secFilings` | Últimos SEC filings (10-K, 10-Q, 8-K) | Mediano |
| 23 | `calendarEvents` | Próximos earnings date, dividend date, ex-date | Pequeño |
| 24 | `price` | Información detallada de precio, pre/post market, 52w | Mediano |
| 25 | `quoteType` | Tipo: EQUITY, ETF, MUTUALFUND, INDEX, etc. | Pequeño |
| 26 | `summaryDetail` | Bid, ask, volume, avg volume, yield, beta | Mediano |
| 27 | `symbol` | Símbolo del ticker | Mínimo |
| 28 | `topHoldings` | Top holdings (para ETFs) | Grande (solo ETFs) |
| 29 | `fundProfile` | Perfil del fondo (para ETFs/Mutual Funds) | Grande (solo fondos) |
| 30 | `indexTrend` | Tendencia del índice | Pequeño |
| 31 | `sectorTrend` | Tendencia del sector | Pequeño |
| 32 | `industryTrend` | Tendencia de la industria | Pequeño |
| 33 | `netSharePurchaseActivity` | Actividad neta de recompra de acciones | Mediano |

### Módulos core recomendados

Para un fetch rápido pero completo de cualquier equity:

```
assetProfile,financialData,defaultKeyStatistics,
incomeStatementHistory,balanceSheetHistory,cashflowStatementHistory,
earnings,earningsTrend,recommendationTrend,
calendarEvents,price,summaryDetail
```

### Ejemplo de respuesta (assetProfile)

```json
{
  "quoteSummary": {
    "result": [
      {
        "assetProfile": {
          "address1": "One Apple Park Way",
          "city": "Cupertino",
          "state": "CA",
          "zip": "95014",
          "country": "United States",
          "phone": "14089961010",
          "website": "https://www.apple.com",
          "industry": "Consumer Electronics",
          "industryKey": "consumer-electronics",
          "industryDisp": "Consumer Electronics",
          "sector": "Technology",
          "sectorKey": "technology",
          "sectorDisp": "Technology",
          "longBusinessSummary": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide...",
          "fullTimeEmployees": 161000,
          "companyOfficers": [
            {
              "name": "Mr. Timothy D. Cook",
              "age": 63,
              "title": "CEO & Director",
              "yearBorn": 1961,
              "fiscalYear": 2023,
              "totalPay": {"raw": 63200000, "fmt": "63.2M"}
            }
          ],
          "auditRisk": 7,
          "boardRisk": 3,
          "compensationRisk": 6,
          "shareHolderRightsRisk": 2,
          "overallRisk": 5,
          "governanceEpochDate": 1719792000,
          "compensationAsOfEpochDate": 1704067200,
          "maxAge": 1
        }
      }
    ],
    "error": null
  }
}
```

### financialData

```json
{
  "financialData": {
    "currentPrice": {"raw": 196.89, "fmt": "196.89"},
    "targetHighPrice": {"raw": 250.00, "fmt": "250.00"},
    "targetLowPrice": {"raw": 150.00, "fmt": "150.00"},
    "targetMeanPrice": {"raw": 205.43, "fmt": "205.43"},
    "targetMedianPrice": {"raw": 205.00, "fmt": "205.00"},
    "recommendationMean": {"raw": 1.8, "fmt": "1.80"},
    "recommendationKey": "buy",
    "numberOfAnalystOpinions": {"raw": 42, "fmt": "42"},
    "totalRevenue": {"raw": 391400000000, "fmt": "391.4B"},
    "revenuePerShare": {"raw": 24.95, "fmt": "24.95"},
    "revenueGrowth": {"raw": 0.071, "fmt": "7.1%"},
    "grossProfits": {"raw": 170800000000, "fmt": "170.8B"},
    "grossMargin": {"raw": 0.452, "fmt": "45.2%"},
    "ebitda": {"raw": 130000000000, "fmt": "130B"},
    "ebitdaMargins": {"raw": 0.332, "fmt": "33.2%"},
    "operatingMargin": {"raw": 0.293, "fmt": "29.3%"},
    "profitMargins": {"raw": 0.251, "fmt": "25.1%"},
    "netIncomeToCommon": {"raw": 96990000000, "fmt": "96.99B"},
    "earningsGrowth": {"raw": 0.089, "fmt": "8.9%"},
    "returnOnAssets": {"raw": 0.214, "fmt": "21.4%"},
    "returnOnEquity": {"raw": 1.342, "fmt": "134.2%"},
    "debtToEquity": {"raw": 1.49, "fmt": "149.0%"},
    "quickRatio": {"raw": 0.81, "fmt": "0.81"},
    "currentRatio": {"raw": 0.97, "fmt": "0.97"},
    "totalCash": {"raw": 61100000000, "fmt": "61.1B"},
    "totalDebt": {"raw": 105500000000, "fmt": "105.5B"},
    "totalCashPerShare": {"raw": 3.90, "fmt": "3.90"},
    "earningsQuarterlyGrowth": {"raw": -0.041, "fmt": "-4.1%"},
    "revenuePerEmployee": {"raw": 2430000, "fmt": "2.43M"},
    "freeCashflow": {"raw": 96920000000, "fmt": "96.92B"}
  }
}
```

### Campos útiles por módulo

**defaultKeyStatistics:**

| Campo | Descripción |
|-------|-------------|
| `beta` | Beta (volatilidad vs mercado) |
| `floatShares` | Acciones en float |
| `sharesOutstanding` | Acciones outstanding |
| `sharesShort` | Acciones en corto |
| `shortRatio` | Short ratio (días para cubrir) |
| `heldPercentInstitutions` | % tenencia institucional |
| `heldPercentInsiders` | % tenencia insider |
| `bookValue` | Book value per share |
| `priceToBook` | Price/book ratio |
| `earningsQuarterlyGrowth` | Crecimiento trimestral earnings |
| `netIncomeToCommon` | Net income |
| `trailingEps` | EPS trailing |
| `forwardEps` | EPS forward |
| `pegRatio` | PEG ratio |
| `lastDividendValue` | Último dividendo |
| `lastDividendDate` | Fecha último dividendo |
| `nextFiscalYearEnd` | Fin del próximo año fiscal |
| `mostRecentQuarter` | Último trimestre reportado |

**incomeStatementHistory:**

```json
{
  "incomeStatementHistory": {
    "incomeStatementHistory": [
      {
        "endDate": {"raw": 1704067200, "fmt": "2023-12-31"},
        "totalRevenue": {"raw": 383300000000, "fmt": "383.3B"},
        "costOfRevenue": {"raw": 214100000000, "fmt": "214.1B"},
        "grossProfit": {"raw": 169200000000, "fmt": "169.2B"},
        "operatingIncome": {"raw": 114300000000, "fmt": "114.3B"},
        "netIncome": {"raw": 97000000000, "fmt": "97B"},
        "ebit": {"raw": 114300000000, "fmt": "114.3B"},
        "totalOperatingExpenses": {"raw": 269000000000, "fmt": "269B"}
      }
    ],
    "maxAge": 86400
  }
}
```

---

## 5. v7/finance/options — Cadena de opciones

### Endpoint

```
GET https://query1.finance.yahoo.com/v7/finance/options/{symbol}
GET https://query1.finance.yahoo.com/v7/finance/options/{symbol}?date={unix_timestamp}
```

**Requiere crumb.**

### Respuesta JSON

```json
{
  "optionChain": {
    "result": [
      {
        "underlyingSymbol": "AAPL",
        "expirationDates": [1719878400, 1720569600, 1721260800, ...],
        "strikes": [170.0, 175.0, 180.0, 185.0, 190.0, 195.0, 200.0, ...],
        "hasMiniOptions": false,
        "quote": {
          "shortName": "Apple Inc.",
          "regularMarketPrice": {"raw": 196.89},
          "regularMarketChange": {"raw": 2.39},
          "regularMarketVolume": {"raw": 45200000},
          "fiftyTwoWeekHigh": {"raw": 199.62},
          "fiftyTwoWeekLow": {"raw": 141.21},
          "marketCap": {"raw": 3020000000000}
        },
        "options": [
          {
            "expirationDate": 1719878400,
            "hasMiniOptions": false,
            "calls": [
              {
                "contractSymbol": "AAPL240621C00195000",
                "strike": {"raw": 195.0, "fmt": "195.00"},
                "currency": "USD",
                "lastPrice": {"raw": 4.55, "fmt": "4.55"},
                "change": {"raw": 0.45, "fmt": "0.45"},
                "percentChange": {"raw": 10.97, "fmt": "10.97%"},
                "volume": {"raw": 15234, "fmt": "15.2k"},
                "openInterest": {"raw": 84500, "fmt": "84.5k"},
                "bid": {"raw": 4.50, "fmt": "4.50"},
                "ask": {"raw": 4.60, "fmt": "4.60"},
                "contractSize": "REGULAR",
                "expiration": 1719878400,
                "lastTradeDate": 1717444800,
                "impliedVolatility": {"raw": 0.281, "fmt": "28.1%"},
                "inTheMoney": true
              }
            ],
            "puts": [
              {
                "contractSymbol": "AAPL240621P00195000",
                "strike": {"raw": 195.0, "fmt": "195.00"},
                "currency": "USD",
                "lastPrice": {"raw": 2.85, "fmt": "2.85"},
                "change": {"raw": -0.32, "fmt": "-0.32"},
                "percentChange": {"raw": -10.09, "fmt": "-10.09%"},
                "volume": {"raw": 8900, "fmt": "8.9k"},
                "openInterest": {"raw": 62300, "fmt": "62.3k"},
                "bid": {"raw": 2.80, "fmt": "2.80"},
                "ask": {"raw": 2.90, "fmt": "2.90"},
                "contractSize": "REGULAR",
                "expiration": 1719878400,
                "lastTradeDate": 1717444800,
                "impliedVolatility": {"raw": 0.305, "fmt": "30.5%"},
                "inTheMoney": false
              }
            ]
          }
        ]
      }
    ],
    "error": null
  }
}
```

### Campos de cada opción

| Campo | Descripción |
|-------|-------------|
| `contractSymbol` | Símbolo OCC de la opción |
| `strike` | Strike price |
| `lastPrice` | Último precio tradeado |
| `bid` | Bid actual |
| `ask` | Ask actual |
| `volume` | Volumen del día |
| `openInterest` | Open interest |
| `impliedVolatility` | Volatilidad implícita |
| `inTheMoney` | Si está ITM (boolean) |
| `expiration` | Timestamp de expiración |
| `change` | Cambio en precio |
| `percentChange` | Cambio porcentual |
| `contractSize` | Tamaño del contrato (REGULAR = 100 acciones) |

### Cómo obtener todas las expiraciones

```python
# 1. Obtener fechas de expiración
r = session.get("https://query1.finance.yahoo.com/v7/finance/options/AAPL")
data = r.json()
expirations = data["optionChain"]["result"][0]["expirationDates"]

# 2. Iterar cada fecha
for exp in expirations[:5]:  # primeras 5
    r = session.get(f"https://query1.finance.yahoo.com/v7/finance/options/AAPL?date={exp}")
    data = r.json()
    options = data["optionChain"]["result"][0]["options"][0]
    calls = options["calls"]
    puts = options["puts"]
    print(f"Exp {datetime.fromtimestamp(exp)}: {len(calls)} calls, {len(puts)} puts")
    time.sleep(0.5)
```

> **Nota:** Las opciones fuera de US stocks generalmente no están disponibles. Para GGAL (BCBA), este endpoint puede devolver vacío.

---

## 6. v1/finance/search — Búsqueda y noticias

### Endpoint

```
GET https://query1.finance.yahoo.com/v1/finance/search?q={query}
```

**No requiere autenticación.**

### Parámetros

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `q` | — | Término de búsqueda (requerido) |
| `quotesCount` | 10 | Cantidad de quotes a retornar |
| `newsCount` | 10 | Cantidad de noticias a retornar |
| `enableCb` | false | Incluir commercial banking results |

### Respuesta JSON

```json
{
  "explains": [],
  "count": 5,
  "quotes": [
    {
      "symbol": "AAPL",
      "isYahooFinance": true,
      "exchange": "NMS",
      "exchangeName": "NasdaqGS",
      "typeDisp": "Equity",
      "quoteType": "EQUITY",
      "shortname": "Apple Inc.",
      "longname": "Apple Inc.",
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "isEligibleForCrossBorder": false
    }
  ],
  "news": [
    {
      "uuid": "some-uuid",
      "title": "Apple Hits New All-Time High Ahead of WWDC",
      "publisher": "Bloomberg",
      "link": "https://finance.yahoo.com/news/...",
      "type": "STORY",
      "providerPublishTime": 1717444800,
      "relatedTickers": ["AAPL"],
      "summary": "Apple Inc. shares reached a new all-time high...",
      "thumbnail": {
        "resolutions": [
          {"url": "https://s.yimg.com/...", "width": 200, "height": 200, "tag": "original"}
        ]
      }
    }
  ],
  "timeZoneShortName": "EDT"
}
```

### Notas

- Ideal para **autocompletado** y **búsqueda de tickers** cuando no se sabe el símbolo exacto.
- Las noticias incluyen `thumbnail` con imágenes.
- El campo `typeDisp` ayuda a identificar el tipo: `Equity`, `ETF`, `Mutual Fund`, `Index`, etc.
- Si el ticker no existe, `quotes` viene vacío pero puede haber `news`.

---

## 7. v6/finance/recommendationsbysymbol — Recomendaciones

### Endpoint

```
GET https://query1.finance.yahoo.com/v6/finance/recommendationsbysymbol/{symbol}
```

**Requiere crumb.**

### Respuesta JSON

```json
{
  "finance": {
    "result": [
      {
        "symbol": "AAPL",
        "recommendedSymbols": [
          {"symbol": "MSFT", "score": 0.95},
          {"symbol": "GOOGL", "score": 0.88},
          {"symbol": "AMZN", "score": 0.82},
          {"symbol": "NVDA", "score": 0.79}
        ]
      }
    ],
    "error": null
  }
}
```

Devuelve símbolos **recomendados similares** (no recomendaciones de analistas, eso está en `quoteSummary.recommendationTrend`).

---

## 8. v1/finance/trending — Trending symbols

### Endpoint

```
GET https://query1.finance.yahoo.com/v1/finance/trending/{country}
```

**No requiere autenticación.**

### Parámetros

| Parámetro | Valores |
|-----------|---------|
| `country` | `US`, `AU`, `CA`, `DE`, `HK`, `IN`, `MX`, `MY`, `NZ`, `SG`, `UK`, `VN` |

### Respuesta JSON

```json
{
  "finance": {
    "result": [
      {
        "count": 10,
        "quotes": [
          {"symbol": "AAPL"},
          {"symbol": "NVDA"},
          {"symbol": "TSLA"},
          {"symbol": "MSFT"},
          {"symbol": "AMZN"}
        ],
        "jobTimestamp": 1717444800,
        "startInterval": 1717358400
      }
    ],
    "error": null
  }
}
```

### Notas

- Los trending cambian cada ~15 minutos.
- `US` funciona bien; otros países pueden tener menos datos.

---

## 9. v1/finance/lookup — Lookup de tickers

### Endpoint

```
GET https://query1.finance.yahoo.com/v1/finance/lookup?query={query}&type=equity
```

**No requiere autenticación.**

### Parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `query` | Término de búsqueda |
| `type` | `equity`, `option`, `future`, `currency` |
| `lang` | Idioma (default: en-US) |
| `region` | Región (default: US) |

### Respuesta JSON

```json
{
  "finance": {
    "result": [
      {"symbol": "AAPL", "name": "Apple Inc.", "type": "EQUITY", "exch": "NMS"}
    ],
    "error": null
  }
}
```

---

## 10. v1/finance/screener — Screener

### Endpoint

```
GET https://query1.finance.yahoo.com/v1/finance/screener?scrIds={scrId}&count={count}
```

**Requiere crumb** (a veces).

### Screeners predefinidos comunes

| scrId | Descripción |
|-------|-------------|
| `most_actives` | Más activos |
| `day_gainers` | Mayores ganadores del día |
| `day_losers` | Mayores perdedores del día |
| `undervalued_growth_stocks` | Crecimiento infravalorados |
| `aggressive_small_caps` | Small caps agresivos |
| `portfolio_anchors` | Anclas de portfolio |

### Ejemplo

```python
s = yahoo_session()
r = s.get("https://query1.finance.yahoo.com/v1/finance/screener",
          params={"scrIds": "most_actives", "count": 10})
data = r.json()
for quote in data["finance"]["result"][0]["quotes"]:
    print(quote["symbol"], quote.get("regularMarketPrice"))
```

---

## 11. WebSocket streaming

Yahoo Finance tiene un endpoint WebSocket para datos en tiempo real:

```
wss://streamer.finance.yahoo.com/?version=2
```

### Uso básico

```python
import websocket

def on_message(ws, message):
    data = json.loads(message)
    print(data)

ws = websocket.WebSocketApp("wss://streamer.finance.yahoo.com/?version=2",
                            on_message=on_message)
ws.run_forever()
```

Los mensajes usan **formato Protobuf** — no es straight JSON. Requiere manejo de crumb y firma. Es más complejo que los endpoints REST y **no está recomendado** para uso general. Los endpoints REST con polling cada 20-30 segundos son más estables.

---

## 12. Rate Limiting y Estrategias

### Límites observados

| Límite | Consecuencia |
|--------|-------------|
| ~2 requests/segundo | Límite seguro |
| 3-5 req/s sostenidos | 429 Too Many Requests |
| >10 req/s en ráfaga | IP block temporal (30-60 min) |
| ~2000 req/hora estimado | Límite diario suave |

### Estrategia recomendada

```python
import time
import random

def safe_request(func, *args, retries=3, **kwargs):
    """Wrapper con exponential backoff."""
    for attempt in range(retries):
        try:
            resp = func(*args, **kwargs)
            if resp.status_code == 429:
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited, waiting {wait:.1f}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait)
```

### Rotación de User-Agent

```python
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/17.1",
]

headers = {"User-Agent": random.choice(USER_AGENTS)}
```

### Cacheo de respuestas

Los datos históricos no cambian. Para datos en lote:

```python
import os
import hashlib
import json

CACHE_DIR = ".yf_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def cached_get(url, params, ttl_seconds=3600):
    key = hashlib.md5(f"{url}{json.dumps(params, sort_keys=True)}".encode()).hexdigest()
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    
    if os.path.exists(cache_file):
        age = time.time() - os.path.getmtime(cache_file)
        if age < ttl_seconds:
            with open(cache_file) as f:
                return json.load(f)
    
    resp = requests.get(url, params=params, headers=HEADERS)
    data = resp.json()
    with open(cache_file, "w") as f:
        json.dump(data, f)
    return data
```

---

## 13. Códigos de Error y Troubleshooting

| Error | Causa | Solución |
|-------|-------|----------|
| `401 Unauthorized` | Falta crumb o cookie A3 | Usar `yahoo_session()` |
| `429 Too Many Requests` | Excediste rate limit | Esperar 30-60s, reducir frecuencia |
| `{"finance":{"error":{"code":"Bad Request"}}}` | Crumb inválido/expirado | Regenerar crumb |
| `chart.result` vacío o `null` | Ticker inválido, sin datos en ese rango/interval | Verificar símbolo. Cambiar rango |
| `Quote data missing` | El símbolo no tiene quote pública | Verificar que el ticker existe |
| Conexión rechazada | `query1.finance.yahoo.com` no responde | Fallback a `query2.finance.yahoo.com` |
| Empty JSON `{}` | Rate limit o bloqueo temporal | Esperar y reintentar con exponential backoff |
| `chart.error.code: "Not Found"` | Símbolo no encontrado | Verificar ticker (ej: usar .BA para argentinos) |
| `Python-requests/2.xx` detectado | User-Agent por defecto | Setear User-Agent de navegador |
| SSL Error | Problemas de red/certificado | Reintentar, verificar conectividad |

### Debugging rápido

```python
# Verificar si un ticker existe
r = requests.get(
    "https://query1.finance.yahoo.com/v1/finance/lookup",
    params={"query": "GGAL", "type": "equity"},
    headers=HEADERS
)
print(r.json())

# Verificar crumb
s = requests.Session()
s.headers.update(HEADERS)
s.get("https://fc.yahoo.com")
crumb = s.get("https://query1.finance.yahoo.com/v1/test/getcrumb").text
print(f"Crumb: {crumb}")
```

---

## 14. Tickers Internacionales

Yahoo Finance maneja tickers de todo el mundo con **sufijos de exchange**:

| País/Mercado | Sufijo | Ejemplo |
|-------------|--------|---------|
| Argentina (BCBA) | `.BA` | `GGAL.BA`, `YPFD.BA`, `PAMP.BA` |
| Brasil (Bovespa) | `.SA` | `PETR4.SA`, `VALE3.SA` |
| México (BMV) | `.MX` | `WALMEX.MX`, `CEMEX.CPO.MX` |
| Canadá (TSX) | `.TO` | `SHOP.TO`, `TD.TO` |
| Reino Unido (LSE) | `.L` | `HSBA.L`, `BP.L` |
| Alemania (Xetra) | `.DE` | `SAP.DE`, `DAI.DE` |
| Hong Kong (HKEX) | `.HK` | `0700.HK`, `9988.HK` |
| Japón (TSE) | `.T` | `7203.T`, `9984.T` |
| Australia (ASX) | `.AX` | `CBA.AX`, `BHP.AX` |
| China (Shanghai) | `.SS` | `600519.SS` |
| China (Shenzhen) | `.SZ` | `000858.SZ` |
| India (NSE) | `.NS` | `RELIANCE.NS`, `TCS.NS` |
| India (BSE) | `.BO` | `RELIANCE.BO` |
| ETFs | Sin sufijo | `SPY`, `QQQ`, `ARKK` |
| Crypto | `-XXX` | `BTC-USD`, `ETH-USD`, `DOGE-USD` |
| Forex | `=X` | `EURUSD=X`, `USDBRL=X` |
| Índices | `^` prefix | `^GSPC` (S&P 500), `^IXIC` (NASDAQ), `^BVSP` (Ibovespa) |

### Ejemplo con ticker argentino

```python
# GGAL en la Bolsa de Buenos Aires
r = requests.get(
    "https://query1.finance.yahoo.com/v8/finance/chart/GGAL.BA",
    params={"range": "1y", "interval": "1d"},
    headers=HEADERS
)
print(r.json())
```

> **Importante:** No todos los endpoints funcionan para tickers internacionales. `v7/options` generalmente solo funciona para US stocks. `v10/quoteSummary` funciona para la mayoría de los mercados.

---

## 15. Campos Comunes entre Endpoints

### Formato `raw` / `fmt`

Casi todos los campos numéricos en Yahoo Finance vienen en este formato:

```json
{
  "regularMarketPrice": {
    "raw": 196.89,       # valor numérico para cálculos
    "fmt": "196.89"      # string formateado para mostrar
  }
}
```

Siempre usar `.raw` para operaciones matemáticas y `.fmt` para display.

### Market states

| Valor | Significado |
|-------|-------------|
| `PRE` | Pre-market (antes de la apertura) |
| `REGULAR` | Mercado abierto en horario regular |
| `POST` | Post-market (después del cierre) |
| `CLOSED` | Mercado cerrado |

### Quote types comunes

| quoteType | Descripción |
|-----------|-------------|
| `EQUITY` | Acción común |
| `ETF` | Exchange-Traded Fund |
| `MUTUALFUND` | Fondo mutuo |
| `INDEX` | Índice de mercado |
| `CURRENCY` | Par de divisas |
| `CRYPTOCURRENCY` | Criptomoneda |
| `OPTION` | Opción |
| `FUTURE` | Futuro |
| `BOND` | Bono |

---

## Apéndice: Resumen de URLs rápidas

```
# Sin autenticación
GET https://query1.finance.yahoo.com/v8/finance/chart/{symbol}
GET https://query1.finance.yahoo.com/v1/finance/search
GET https://query1.finance.yahoo.com/v1/finance/trending/{country}
GET https://query1.finance.yahoo.com/v1/finance/lookup
GET https://fc.yahoo.com
GET https://query1.finance.yahoo.com/v1/test/getcrumb

# Requieren crumb (usar yahoo_session())
GET https://query1.finance.yahoo.com/v7/finance/quote
GET https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}
GET https://query1.finance.yahoo.com/v7/finance/options/{symbol}
GET https://query1.finance.yahoo.com/v6/finance/recommendationsbysymbol/{symbol}
GET https://query1.finance.yahoo.com/v1/finance/screener
```

---

*Este documento se basa en ingeniería inversa de la API no oficial de Yahoo Finance.
No hay garantías de disponibilidad o consistencia. Los endpoints pueden cambiar sin aviso.*
