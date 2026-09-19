# Nasdaq Data — Referencia Completa

## Indice
1. [Resumen de Endpoints](#1-resumen-de-endpoints)
2. [Info — Cotizacion y Datos de Empresa](#2-info--cotizacion-y-datos-de-empresa)
3. [Short Interest](#3-short-interest)
4. [Chart — OHLCV Historico](#4-chart--ohlcv-historico)
5. [Financials — Estados Financieros](#5-financials--estados-financieros)
6. [Institutional Holdings — Tenencias 13F](#6-institutional-holdings--tenencias-13f)
7. [Holdings — ETFs donde el Stock es Top 10](#7-holdings--etfs-donde-el-stock-es-top-10)
8. [ETF Holdings — Top 10 Holdings de un ETF](#8-etf-holdings--top-10-holdings-de-un-etf)
9. [Company Profile — Perfil de Empresa](#9-company-profile--perfil-de-empresa)
10. [Dividends — Dividendos](#10-dividends--dividendos)
11. [EPS — Earnings Per Share por Ticker](#11-eps--earnings-per-share-por-ticker)
12. [Insider Trades — Actividad de Insiders](#12-insider-trades--actividad-de-insiders)
13. [Option Chain — Cadena de Opciones](#13-option-chain--cadena-de-opciones)
14. [News — Noticias](#14-news--noticias)
15. [Screener — Buscador de Acciones](#15-screener--buscador-de-acciones)
16. [Screener ETFs — Buscador de ETFs](#16-screener-etfs--buscador-de-etfs)
17. [IPO Calendar](#17-ipo-calendar)
18. [Earnings Calendar](#18-earnings-calendar)
19. [Dividend Calendar](#19-dividend-calendar)
20. [Splits Calendar](#20-splits-calendar)
21. [Economic Calendar](#21-economic-calendar)
22. [All — Fetch Combinado](#22-all--fetch-combinado)
23. [Consideraciones Tecnicas](#23-consideraciones-tecnicas)
24. [Endpoints No Disponibles](#24-endpoints-no-disponibles)

---

## 1. Resumen de Endpoints

| Modo | Endpoint Interno | Metodo | AssetClass | Output |
|------|-----------------|--------|------------|--------|
| `info` | `/api/quote/{ticker}/info` | GET | `stocks` | JSON ~3KB |
| `short-interest` | `/api/quote/{ticker}/short-interest` | GET | `stocks` | JSON ~8KB |
| `chart` | `/api/quote/{ticker}/chart` | GET | `stocks` | JSON ~40KB |
| `financials` | `/api/company/{ticker}/financials` | GET | - | JSON ~10KB |
| `institutional-holdings` | `/api/company/{ticker}/institutional-holdings` | GET | - | JSON ~5KB |
| `holdings` | `/api/company/{ticker}/holdings` | GET | `stocks` | JSON ~1KB |
| `etf-holdings` | `/api/company/{ticker}/holdings` | GET | `etf` | JSON ~1KB |
| `company-profile` | `/api/company/{ticker}/company-profile` | GET | - | JSON ~1KB |
| `dividends` | `/api/quote/{ticker}/dividends` | GET | `stocks` | JSON ~2KB |
| `eps` | `/api/quote/{ticker}/eps` | GET | - | JSON ~1KB |
| `insider-trades` | `/api/company/{ticker}/insider-trades` | GET | - | JSON ~5KB |
| `option-chain` | `/api/quote/{ticker}/option-chain` | GET | `stocks` | JSON ~30KB+ |
| `news` | `/api/news/topic/articlebysymbol` | GET | - | JSON ~7KB |
| `screener` | `/api/screener/stocks` | GET | - | JSON variable |
| `screener-etf` | `/api/screener/etf` | GET | - | JSON variable |
| `ipo-calendar` | `/api/ipo/calendar` | GET | - | JSON ~2KB |
| `earnings-calendar` | `/api/calendar/earnings` | GET | - | JSON ~10KB |
| `economic-calendar` | `/api/calendar/economicevents` | GET | - | JSON ~8KB |
| `dividend-calendar` | `/api/calendar/dividends` | GET | - | JSON ~15KB |
| `splits-calendar` | `/api/calendar/splits` | GET | - | JSON ~3KB |

**Base URLs:**
- API principal: `https://api.nasdaq.com`
- News API: `https://www.nasdaq.com`

**Headers requeridos:**
```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nasdaq.com/",
}
```

**Estructura comun de respuesta:**
```json
{
  "data": { ... },
  "message": null,
  "status": {
    "rCode": 200,
    "bCodeMessage": null,
    "developerMessage": null
  }
}
```

---

## 2. Info — Cotizacion y Datos de Empresa

**Endpoint:** `GET /api/quote/{ticker}/info?assetclass=stocks`

Endpoint principal que devuelve la cotizacion actual, datos de mercado y estadisticas clave.

### Campos del response

```json
{
  "data": {
    "symbol": "NVDA",
    "companyName": "NVIDIA Corporation Common Stock",
    "stockType": "Common Stock",
    "exchange": "NASDAQ-GS",
    "isNasdaqListed": true,
    "isNasdaq100": true,
    "isHeld": false,
    "primaryData": {
      "lastSalePrice": "$214.75",
      "netChange": "-8.07",
      "percentageChange": "-3.62%",
      "deltaIndicator": "down",
      "lastTradeTimestamp": "Jun 3, 2026",
      "isRealTime": false,
      "bidPrice": "N/A",
      "askPrice": "N/A",
      "bidSize": "N/A",
      "askSize": "N/A",
      "volume": "160,910,801",
      "currency": null
    },
    "secondaryData": null,
    "marketStatus": "Closed",
    "assetClass": "STOCKS",
    "keyStats": {
      "fiftyTwoWeekHighLow": {
        "label": "52 Week Range:",
        "value": "137.95 - 236.54"
      },
      "dayrange": {
        "label": "High/Low:",
        "value": "NA"
      }
    },
    "notifications": []
  }
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `symbol` | string | Ticker |
| `companyName` | string | Nombre completo de la empresa |
| `stockType` | string | Tipo de accion (Common Stock, ADR, ETF) |
| `exchange` | string | Exchange (NASDAQ-GS, NASDAQ-CM, NYSE) |
| `isNasdaqListed` | bool | Si esta listado en Nasdaq |
| `isNasdaq100` | bool | Si es componente del Nasdaq-100 |
| `primaryData.lastSalePrice` | string | Ultimo precio (formateado con $) |
| `primaryData.netChange` | string | Cambio neto en USD |
| `primaryData.percentageChange` | string | Cambio porcentual |
| `primaryData.deltaIndicator` | string | `up` / `down` / `unchanged` |
| `primaryData.volume` | string | Volumen (formateado con comas) |
| `marketStatus` | string | `Open`, `Closed`, `Pre-market`, `After-hours` |
| `keyStats.fiftyTwoWeekHighLow` | object | Rango de 52 semanas |

### Coverage

| Tipo | Coverage |
|------|----------|
| Stocks Nasdaq | Todas las listadas en Nasdaq |
| Stocks NYSE | Si, via `?assetclass=stocks` |
| ETFs | Si, cambiar `?assetclass=etf` |
| ADRs | Si (ej: GGAL) |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py info GGAL
python scripts/fetch_nasdaq.py info AAPL -q
```

---

## 3. Short Interest

**Endpoint:** `GET /api/quote/{ticker}/short-interest?assetclass=stocks`

Devuelve el historico de short interest (posiciones cortas) con datos quincenales.

### Campos del response

```json
{
  "data": {
    "symbol": "nvda",
    "shortInterestTable": {
      "headers": {
        "settlementDate": "Settlement Date",
        "interest": "Short Interest",
        "avgDailyShareVolume": "Avg. Daily Share Volume",
        "daysToCover": "Days to Cover"
      },
      "rows": [
        {
          "settlementDate": "05/15/2026",
          "interest": "296,966,425",
          "avgDailyShareVolume": "152,806,421",
          "daysToCover": 1.943416
        }
      ]
    }
  }
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `settlementDate` | string | Fecha de liquidacion (MM/DD/YYYY) |
| `interest` | string | Short Interest (acciones en corto) |
| `avgDailyShareVolume` | string | Volumen diario promedio |
| `daysToCover` | float | Dias para cubrir (short interest / volumen diario) |

### Coverage temporal

| Ticker | Periodo | Registros |
|--------|---------|-----------|
| NVDA | Jul 2024 - May 2026 | ~46 registros (2 anos) |
| GGAL | Jun 2025 - May 2026 | ~23 registros (1 ano) |
| AAPL | Similar | ~46 registros |

### Interpretacion

- **Days to Cover alto** (>10): Mucha presion bajista, posible short squeeze
- **Days to Cover bajo** (<2): Poca presion bajista
- **Short Interest creciente**: Mas apostadores bajistas

### Ejemplo

```bash
python scripts/fetch_nasdaq.py short-interest GGAL
python scripts/fetch_nasdaq.py short-interest NVDA -o nvda_short.json
```

---

## 4. Chart — OHLCV Historico

**Endpoint:** `GET /api/quote/{ticker}/chart?assetclass=stocks&fromdate=YYYY-MM-DD&todate=YYYY-MM-DD`

Devuelve datos OHLCV historicos para graficar.

### Parametros

| Parametro | Requerido | Default | Descripcion |
|-----------|-----------|---------|-------------|
| `assetclass` | Si | - | `stocks` |
| `fromdate` | No | 1 ano atras | Fecha inicio (YYYY-MM-DD) |
| `todate` | No | Hoy | Fecha fin (YYYY-MM-DD) |

### Campos del response

```json
{
  "data": {
    "symbol": "NVDA",
    "company": "NVIDIA Corporation Common Stock",
    "timeAsOf": "Jun 3, 2026",
    "isNasdaq100": true,
    "lastSalePrice": "$214.75",
    "netChange": "-8.07",
    "percentageChange": "-3.62%",
    "deltaIndicator": "up",
    "previousClose": "$222.82",
    "chart": [
      {
        "z": {
          "high": "138.12",
          "low": "135.4",
          "open": "135.49",
          "close": "137.38",
          "volume": "53889998",
          "date": "06/03/2025",
          "unixTime": 1748980800000,
          "change": "1.89",
          "changePercent": "1.4",
          "label": "Jun 3"
        }
      }
    ]
  }
}
```

### Campos del chart

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `z.date` | string | Fecha (MM/DD/YYYY) |
| `z.open` | string | Precio de apertura |
| `z.high` | string | Maximo del dia |
| `z.low` | string | Minimo del dia |
| `z.close` | string | Precio de cierre |
| `z.volume` | string | Volumen |
| `z.unixTime` | int | Timestamp Unix (ms) |
| `z.change` | string | Cambio neto |
| `z.changePercent` | string | Cambio porcentual |

### Coverage

| Ticker | Periodo maximo | Bars |
|--------|---------------|------|
| NVDA | ~1 ano | ~251 (trading days) |
| GGAL | ~1 ano | ~251 |
| Cualquier | 1 ano por defecto | Variable |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py chart NVDA --from 2025-01-01 --to 2026-06-04
python scripts/fetch_nasdaq.py chart GGAL --from 2025-06-01 --to 2026-06-01
```

---

## 5. Financials — Estados Financieros

**Endpoint:** `GET /api/company/{ticker}/financials`

Devuelve 4 tablas financieras principales:

### Tabs disponibles

| Tab | Descripcion |
|-----|-------------|
| `incomeStatementTable` | Estado de resultados |
| `balanceSheetTable` | Balance general |
| `cashFlowTable` | Flujo de efectivo |
| `financialRatiosTable` | Ratios financieros |

### Income Statement

```json
{
  "data": {
    "symbol": "NVDA",
    "incomeStatementTable": {
      "asOf": null,
      "headers": {
        "value1": "Period Ending:",
        "value2": "1/25/2026",
        "value3": "1/26/2025",
        "value4": "1/28/2024",
        "value5": "1/29/2023"
      },
      "rows": [
        {
          "value1": "Total Revenue",
          "value2": "$215,938,000",
          "value3": "$130,497,000",
          "value4": "$60,922,000",
          "value5": "$26,974,000"
        },
        {
          "value1": "Cost of Revenue",
          "value2": "$65,625,000",
          "value3": "$40,892,000",
          "value4": "$18,512,000",
          "value5": "$11,618,000"
        },
        {
          "value1": "Gross Profit",
          "value2": "$150,313,000",
          "value3": "$89,605,000",
          "value4": "$42,410,000",
          "value5": "$15,356,000"
        }
      ]
    }
  }
}
```

### Balance Sheet

Headers similares. Rows incluyen:
- Total Assets, Total Liabilities, Total Equity
- Cash & Cash Equivalents
- Long-term Debt
- Goodwill, Intangible Assets
- Accounts Receivable, Inventory

### Cash Flow

Headers similares. Rows incluyen:
- Net Income
- Operating Activities, Investing Activities, Financing Activities
- Free Cash Flow
- Capital Expenditure

### Financial Ratios

Headers: value1 (nombre), value2...valueN (periodos).
- Profit Margin, Operating Margin
- Return on Assets (ROA), Return on Equity (ROE)
- Current Ratio, Quick Ratio
- Debt to Equity
- Inventory Turnover

### Coverage

| Ticker | Periodos |
|--------|----------|
| NVDA | 4 periodos (2023-2026) |
| AAPL | 4 periodos |
| GGAL | 4 periodos |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py financials NVDA
python scripts/fetch_nasdaq.py financials MSFT -o msft_fin.json
```

---

## 6. Institutional Holdings — Tenencias 13F

**Endpoint:** `GET /api/company/{ticker}/institutional-holdings`

Devuelve las tenencias institucionales reportadas en formularios 13F.

### Campos del response

```json
{
  "data": {
    "ownershipSummary": null,
    "activePositions": null,
    "newSoldOutPositions": null,
    "holdingsTransactions": {
      "totalRecords": "6245",
      "institutionalHolders": " Institutional Holders",
      "sharesHeld": " Total Shares Held",
      "table": {
        "asOf": null,
        "headers": {
          "ownerName": "Owner Name",
          "date": "Date",
          "sharesHeld": "Shares Held",
          "change": "Change",
          "percentHeld": "% Held"
        },
        "rows": [
          {
            "ownerName": "Vanguard Group Inc",
            "date": "03/31/2026",
            "sharesHeld": "209,640,142",
            "change": "1,906,564",
            "percentHeld": "8.54"
          }
        ]
      }
    }
  }
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `ownerName` | string | Nombre de la institucion |
| `date` | string | Fecha del reporte 13F |
| `sharesHeld` | string | Cantidad de acciones poseidas |
| `change` | string | Cambio respecto al trimestre anterior |
| `percentHeld` | string | Porcentaje del total de acciones |

### Coverage

| Ticker | Institutional Holders |
|--------|---------------------|
| NVDA | ~6,245 transacciones |
| AAPL | ~7,000+ |
| GGAL | ~161 holders |
| META | ~5,531 holders |

### Notas

- Los datos se actualizan dentro de los 45 dias posteriores al cierre del trimestre
- Incluye compras, ventas, nuevas posiciones y cierres
- Solo instituciones con >$100M AUM estan obligadas a reportar

### Ejemplo

```bash
python scripts/fetch_nasdaq.py institutional-holdings NVDA
python scripts/fetch_nasdaq.py institutional-holdings GGAL
```

---

## 7. Holdings — ETFs donde el Stock es Top 10

**Endpoint:** `GET /api/company/{ticker}/holdings?assetclass=stocks`

Devuelve los ETFs que tienen al stock como Top 10 Holding. Es la respuesta directa a "en qué ETFs está este stock?".

### Campos del response

```json
{
  "data": {
    "heading": "ETFs with NVDA as a Top 10 Holding*",
    "holdings": {
      "asOf": null,
      "headers": {
        "symbol": "Symbol",
        "weighting": "% Weighting",
        "priceChange100Day": "100 Day Price Change (%)"
      },
      "rows": [
        {
          "symbol": "NVDW",
          "companyname": "Roundhill NVDA WeeklyPay ETF",
          "weighting": "20.6%",
          "priceChange100Day": "-0.14 (-0.33%)",
          "highlight": false,
          "isPositivePriceChange": false
        },
        {
          "symbol": "VGT",
          "companyname": "Vanguard Information Tech ETF",
          "weighting": "18.59%",
          "priceChange100Day": "+30.01 (+31.34%)",
          "highlight": false,
          "isPositivePriceChange": true
        }
      ]
    },
    "nasdaqheading": "Nasdaq Listed ETFs where NVDA is a top 10 holding*",
    "nasdaqHoldings": {
      "asOf": null,
      "headers": null,
      "rows": null
    }
  }
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `symbol` | string | Ticker del ETF |
| `companyname` | string | Nombre del ETF |
| `weighting` | string | Ponderacion en el portfolio del ETF |
| `priceChange100Day` | string | Cambio del ETF en 100 dias |
| `highlight` | bool | Destacado (ETF tematico/nicho) |
| `isPositivePriceChange` | bool | Cambio positivo en 100d |

### Coverage

| Ticker | ETFs encontrados | Ejemplos |
|--------|-----------------|----------|
| **NVDA** | 5 ETFs | NVDW (20.6%), USXF (20.37%), VGT (18.59%) |
| **AAPL** | 5 ETFs | AAPW (19.83%), GXPT (17.62%), VGT (14.81%) |
| **GGAL** | 1 ETF | ARGT - Global X MSCI Argentina ETF (6.3%) |
| **MSFT** | 5 ETFs | MSFW (31.6%), GXPT (12.73%), MSFU (12.54%) |
| **SPY** | 5 ETFs | DHSB (103%), VEGA (40.95%), GAL (28.63%) |

### Notas

- `weighting` >100% es posible (ETFs apalancados o inversos)
- `highlight: true` indica ETFs tematicos directamente vinculados al stock
- El campo `nasdaqHoldings` son ETFs listados en Nasdaq donde el stock es top 10 (suele ser null)

### Ejemplo

```bash
python scripts/fetch_nasdaq.py holdings NVDA
python scripts/fetch_nasdaq.py holdings GGAL
```

---

## 8. ETF Holdings — Top 10 Holdings de un ETF

**Endpoint:** `GET /api/company/{ticker}/holdings?assetclass=etf`

Devuelve el Top 10 de holdings de un ETF. Es el inverso del endpoint anterior.

### Campos del response

```json
{
  "data": {
    "heading": "Top 10 Holdings of SPY",
    "holdings": {
      "asOf": null,
      "headers": {
        "symbol": "Symbol",
        "weighting": "% Holdings"
      },
      "rows": [
        {
          "symbol": "NVDA",
          "companyname": "NVIDIA Corporation Common Stock",
          "weighting": "8.36%",
          "priceChange100Day": null,
          "highlight": false,
          "isPositivePriceChange": false
        },
        {
          "symbol": "AAPL",
          "companyname": "Apple Inc. Common Stock",
          "weighting": "6.89%",
          "priceChange100Day": null,
          "highlight": false,
          "isPositivePriceChange": false
        }
      ]
    }
  }
}
```

### Campos clave

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `symbol` | string | Ticker del holding |
| `companyname` | string | Nombre de la empresa |
| `weighting` | string | Ponderacion dentro del ETF |
| `priceChange100Day` | string/null | Cambio del holding en 100d |

### Coverage

| ETF | Holdings | Top holdings |
|-----|----------|-------------|
| **SPY** | 10 | NVDA 8.36%, AAPL 6.89%, MSFT 5.24% |
| **QQQ** | 10 | NVDA 8.64%, AAPL 7.12%, MSFT 5.1% |
| **IVV** | 9 | NVDA 8.34%, AAPL 7%, MSFT 4.87% |
| **VOO** | 10 | NVDA 7.84%, AAPL 6.44%, MSFT 4.89% |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py etf-holdings SPY
python scripts/fetch_nasdaq.py etf-holdings QQQ
python scripts/fetch_nasdaq.py etf-holdings ARGT
```

---

## 9. Company Profile — Perfil de Empresa

**Endpoint:** `GET /api/company/{ticker}/company-profile`

Devuelve informacion basica de la empresa.

### Campos del response

```json
{
  "data": {
    "ModuleTitle": { "label": "Module Title", "value": "Company Description" },
    "CompanyName": { "label": "Company Name", "value": "NVIDIA Corporation" },
    "Symbol": { "label": "Symbol", "value": "NVDA" },
    "Address": {
      "label": "Address",
      "value": "2788 SAN TOMAS EXPRESSWAY, SANTA CLARA, California, 95051, United States"
    },
    "Phone": { "label": "Phone", "value": "+1 408 - 486-2000" },
    "Industry": { "label": "Industry", "value": "Semiconductors" },
    "Sector": { "label": "Sector", "value": "Technology" },
    "Region": { "label": "Region", "value": "North America" },
    "CompanyDescription": {
      "label": "Company Description",
      "value": "NVIDIA Corporation provides graphics, compute and networking solutions..."
    },
    "CompanyUrl": { "label": "Company URL", "value": "http://www.nvidia.com" },
    "CEO": { "label": "CEO", "value": "Jensen Huang" },
    "Employees": { "label": "Employees", "value": "36000" }
  }
}
```

### Ejemplo

```bash
python scripts/fetch_nasdaq.py company-profile AAPL
```

---

## 10. Dividends — Dividendos

**Endpoint:** `GET /api/quote/{ticker}/dividends?assetclass=stocks`

### Campos del response

```json
{
  "data": {
    "dividendHeaderValues": {
      "amount": "Amount",
      "frequency": "Frequency",
      "yield": "Yield",
      "payDate": "Pay Date",
      "exDate": "Ex Date"
    },
    "exDividendDate": { "label": "Ex/Efective Date", "value": "06/05/2026" },
    "dividendPaymentDate": { "label": "Dividend Payment Date", "value": "06/19/2026" },
    "yield": { "label": "Yield", "value": "0.93%" },
    "annualizedDividend": { "label": "Annualized Dividend", "value": "$2.04" },
    "frequency": { "label": "Frequency", "value": "Quarterly" },
    "amount": { "label": "Amount", "value": "$0.51" },
    "history": {
      "asOf": null,
      "headers": {
        "exDate": "Ex/Eff Date",
        "type": "Type",
        "amount": "Amount",
        "paymentDate": "Payment Date"
      },
      "rows": [
        {
          "exDate": "06/05/2026",
          "type": "Cash",
          "amount": "$0.51",
          "paymentDate": "06/19/2026"
        }
      ]
    }
  }
}
```

### Campos clave

| Campo | Descripcion |
|-------|-------------|
| `exDividendDate` | Fecha ex-dividendo |
| `dividendPaymentDate` | Fecha de pago |
| `yield` | Dividend yield anual |
| `annualizedDividend` | Dividendo anualizado por accion |
| `frequency` | Frecuencia (Quarterly, Monthly, Annual) |
| `amount` | Ultimo monto del dividendo |
| `history.rows` | Historial de dividendos |

### Coverage

| Ticker | Historial |
|--------|-----------|
| NVDA | ~4 anos de historial |
| AAPL | ~10+ anos |
| GGAL | ~8+ anos (paga dividendos) |

### Nota

Empresas que no pagan dividendos devuelven `data: null`.

### Ejemplo

```bash
python scripts/fetch_nasdaq.py dividends NVDA
```

---

## 11. EPS — Earnings Per Share por Ticker

**Endpoint:** `GET /api/quote/{ticker}/eps`

EPS histórico y estimaciones futuras por ticker.

### Campos del response

```json
{
  "data": {
    "symbol": "nvda",
    "earningsPerShare": [
      {
        "type": "PreviousQuarter",
        "period": "Apr 2026",
        "consensus": 1.7,
        "earnings": 1.87
      },
      {
        "type": "UpcomingQuarter",
        "period": "Jul 2026",
        "consensus": 1.88,
        "earnings": 0.0
      }
    ]
  }
}
```

### Campos clave

| Campo | Descripcion |
|-------|-------------|
| `type` | `PreviousQuarter` (historico) o `UpcomingQuarter` (estimado) |
| `period` | Periodo fiscal (ej: `Apr 2026`, `Jul 2026`) |
| `consensus` | EPS estimado por consenso de analistas |
| `earnings` | EPS real reportado (0.0 si es estimado futuro) |

### Coverage

| Ticker | Periodos |
|--------|----------|
| NVDA | 8 quarters: 4 historicos + 4 upcoming |
| GGAL | Similar |
| AAPL | Similar |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py eps NVDA
python scripts/fetch_nasdaq.py eps GGAL -q
```

---

## 12. Insider Trades — Actividad de Insiders

**Endpoint:** `GET /api/company/{ticker}/insider-trades?limit=N&type=all&sortColumn=lastDate&sortOrder=DESC`

Resumen de actividad de insiders (3 y 12 meses) + tabla detallada de transacciones.

### Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `limit` | 100 | Cantidad de transacciones |
| `type` | `all` | `all`, `buy`, `sell` |
| `sortColumn` | `lastDate` | Columna de ordenamiento |
| `sortOrder` | `DESC` | `ASC` o `DESC` |

### Campos del response

```json
{
  "data": {
    "title": null,
    "numberOfTrades": {
      "headers": { "insiderTrade": "Insider Trade", "months3": "3 Months", "months12": "12 Months" },
      "rows": [
        { "insiderTrade": "Number of Open Market Buys", "months3": "5", "months12": "23" },
        { "insiderTrade": "Number of Sells", "months3": "17", "months12": "190" },
        { "insiderTrade": "Total Insider Trades", "months3": "22", "months12": "213" }
      ]
    },
    "numberOfSharesTraded": {
      "rows": [
        { "insiderTrade": "Number of Shares Bought", "months3": "59,150,794", "months12": "70,154,889" },
        { "insiderTrade": "Number of Shares Sold", "months3": "60,595,682", "months12": "128,299,660" },
        { "insiderTrade": "Net Activity", "months3": "(1,444,888)", "months12": "(58,144,771)" }
      ]
    },
    "transactionTable": {
      "totalRecords": "363",
      "table": {
        "headers": {
          "insider": "Insider",
          "relation": "Relation",
          "lastDate": "Last Date",
          "transactionType": "Transaction",
          "ownType": "Owner Type",
          "sharesTraded": "Shares Traded",
          "lastPrice": "Price",
          "sharesHeld": "Shares Held"
        },
        "rows": [
          {
            "insider": "DABIRI JOHN",
            "relation": "Director",
            "lastDate": "5/27/2026",
            "transactionType": "Automatic Sell",
            "ownType": "Direct",
            "sharesTraded": "2",
            "lastPrice": "0",
            "sharesHeld": "33,770"
          }
        ]
      }
    }
  }
}
```

### Campos clave

| Tabla | Descripcion |
|-------|-------------|
| `numberOfTrades` | Conteo de compras, ventas y totales en 3/12 meses |
| `numberOfSharesTraded` | Shares comprados, vendidos, neto en 3/12 meses |
| `transactionTable` | Transacciones detalladas con insider, rol, fecha, tipo, precio |

### Transaction table fields

| Campo | Descripcion |
|-------|-------------|
| `insider` | Nombre del insider |
| `relation` | Relacion (Director, Officer, 10% Owner) |
| `lastDate` | Fecha de la transaccion |
| `transactionType` | Tipo (Automatic Sell, Open Market Purchase, etc.) |
| `ownType` | Tipo de propiedad (Direct, Indirect) |
| `sharesTraded` | Cantidad de acciones |
| `lastPrice` | Precio |
| `sharesHeld` | Acciones poseidas despues del trade |
| `totalRecords` | Total de transacciones disponibles |

### Net Activity

`Net Activity` en `numberOfSharesTraded` muestra:
- **Positivo**: Mas compras que ventas (alcista)
- **Negativo**: Mas ventas que compras (bajista)
- Parentesis = negativo

### Ejemplo

```bash
python scripts/fetch_nasdaq.py insider-trades NVDA
python scripts/fetch_nasdaq.py insider-trades NVDA --type buy
python scripts/fetch_nasdaq.py insider-trades NVDA --type sell --limit 10
python scripts/fetch_nasdaq.py insider-trades GGAL -q
```

---

## 13. Option Chain — Cadena de Opciones

**Endpoint:** `GET /api/quote/{ticker}/option-chain?assetclass=stocks`

Devuelve la cadena completa de opciones con calls y puts.

### Campos del response

```json
{
  "data": {
    "totalRecord": 962,
    "lastTrade": "LAST TRADE: $214.75 (AS OF JUN 3, 2026)",
    "filterlist": [...],
    "table": {
      "asOf": null,
      "headers": {
        "expiryDate": "Exp. Date",
        "c_Last": "Last",
        "c_Change": "Change",
        "c_Bid": "Bid",
        "c_Ask": "Ask",
        "c_Volume": "Volume",
        "c_Openinterest": "Open Int.",
        "strike": "Strike",
        "p_Last": "Last",
        "p_Change": "Change",
        "p_Bid": "Bid",
        "p_Ask": "Ask",
        "p_Volume": "Volume",
        "p_Openinterest": "Open Int."
      },
      "rows": [
        {
          "expirygroup": "June 5, 2026",
          "expiryDate": "06/05/2026",
          "c_Last": "N/A",
          "c_Change": "N/A",
          "c_Bid": "N/A",
          "c_Ask": "N/A",
          "c_Volume": "N/A",
          "c_Openinterest": "N/A",
          "strike": "214.00",
          "p_Last": "N/A",
          "p_Change": "N/A",
          "p_Bid": "N/A",
          "p_Ask": "N/A",
          "p_Volume": "N/A",
          "p_Openinterest": "N/A"
        }
      ]
    }
  }
}
```

### Prefijos de columnas

| Prefijo | Tipo |
|---------|------|
| `c_` | Call |
| `p_` | Put |

### Campos clave por opcion

| Campo | Descripcion |
|-------|-------------|
| `expiryDate` | Fecha de vencimiento |
| `strike` | Precio strike |
| `c_Last` | Ultimo precio de la call |
| `c_Bid` | Bid de la call |
| `c_Ask` | Ask de la call |
| `c_Volume` | Volumen de la call |
| `c_Openinterest` | Open interest de la call |
| `p_Last`, `p_Bid`, `p_Ask`, etc. | Equivalentes para puts |

### Coverage

| Ticker | Opciones |
|--------|----------|
| NVDA | ~962 registros |
| AAPL | Similar |
| GGAL | Similar (si tiene opciones listadas) |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py option-chain NVDA
```

---

## 14. News — Noticias

**Endpoint:** `GET /api/news/topic/articlebysymbol?q={ticker}|STOCKS&offset=0&limit=N`

Devuelve las ultimas noticias relacionadas con un ticker.

### Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `q` | - | `{ticker}|STOCKS` (formato requerido) |
| `offset` | 0 | Paginacion |
| `limit` | 10 | Maximo de resultados |

### Campos del response

```json
{
  "data": {
    "totalrecords": 500,
    "rows": [
      {
        "title": "Nvidia (NVDA) Stock Has Made Early Investors a Fortune...",
        "description": "Key PointsNvidia is a dominant force in semiconductors.",
        "created": "Jun 4, 2026",
        "ago": "1 hour ago",
        "publisher": "The Motley Fool",
        "primarysymbol": "nvda",
        "url": "/articles/nvidia-nvda-stock-has-made-early-investors-fortune...",
        "id": 27713111,
        "primarytopic": "Markets|4006",
        "related_symbols": ["nvda|stocks"]
      }
    ]
  }
}
```

### Campos clave

| Campo | Descripcion |
|-------|-------------|
| `title` | Titulo de la noticia |
| `description` | Descripcion breve |
| `created` | Fecha de publicacion |
| `ago` | Tiempo desde publicacion |
| `publisher` | Fuente/editor |
| `url` | URL relativa en nasdaq.com |
| `primarysymbol` | Ticker principal de la noticia |
| `related_symbols` | Tickers relacionados |

### Coverage

| Ticker | Noticias disponibles |
|--------|---------------------|
| NVDA | ~500 (maximo) |
| AAPL | ~500 |
| GGAL | ~500 |
| Cualquier | Depende de la cobertura |

### URL completa de noticias

La URL relativa en `url` se completa con `https://www.nasdaq.com`:
```
https://www.nasdaq.com/articles/nvidia-nvda-stock-has-made-early-investors-fortune...
```

### Ejemplo

```bash
python scripts/fetch_nasdaq.py news NVDA --limit 5
python scripts/fetch_nasdaq.py news GGAL --limit 3 -q
```

---

## 15. Screener — Buscador de Acciones

**Endpoint:** `GET /api/screener/stocks?tableonly=true&limit=N&offset=0&exchange=X`

Devuelve un listado de acciones con datos de cotizacion.

### Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `tableonly` | `true` | Solo tabla (sin filtros) |
| `limit` | 25 | Cantidad de resultados |
| `offset` | 0 | Paginacion |
| `exchange` | `nasdaq` | `nasdaq`, `nyse`, `amex` |

### Campos del response

```json
{
  "data": {
    "table": {
      "headers": {
        "symbol": "Symbol",
        "name": "Name",
        "lastsale": "Last Sale",
        "netchange": "Net Change",
        "pctchange": "% Change",
        "marketCap": "Market Cap"
      },
      "rows": [
        {
          "symbol": "NVDA",
          "name": "NVIDIA Corporation Common Stock",
          "lastsale": "$214.75",
          "netchange": "-8.07",
          "pctchange": "-3.622%",
          "marketCap": "5.581T",
          "url": "/market-activity/stocks/nvda"
        }
      ]
    },
    "totalrecords": 3513
  }
}
```

### Paginacion

Para obtener mas de 25 resultados, incrementar `offset` en pasos de 25:

```python
# Pagina 1
/screener/stocks?tableonly=true&limit=25&offset=0&exchange=nasdaq
# Pagina 2
/screener/stocks?tableonly=true&limit=25&offset=25&exchange=nasdaq
```

### Ejemplo

```bash
python scripts/fetch_nasdaq.py screener --exchange nasdaq --limit 10
python scripts/fetch_nasdaq.py screener --exchange nyse --limit 50 --offset 100
```

---

## 16. Screener ETFs — Buscador de ETFs

**Endpoint:** `GET /api/screener/etf?tableonly=true&limit=N&offset=0`

Devuelve un listado de ETFs con datos de cotizacion y rendimiento anual.

### Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `tableonly` | `true` | Solo tabla (sin filtros) |
| `limit` | 25 | Cantidad de resultados |
| `offset` | 0 | Paginacion |

### Campos del response

```json
{
  "data": {
    "records": {
      "totalrecords": 4551,
      "data": {
        "headers": {
          "symbol": "SYMBOL",
          "companyName": "NAME",
          "lastSalePrice": "LAST PRICE",
          "percentageChange": "% CHANGE",
          "oneYearPercentagechange": "1 yr % CHANGE"
        },
        "rows": [
          {
            "symbol": "AIVI",
            "companyName": "WisdomTree International AI Enhanced Value Fund",
            "lastSalePrice": "$56.8056",
            "netChange": "-0.3804",
            "percentageChange": "-0.67%",
            "oneYearPercentage": "17.83%",
            "deltaIndicator": "down"
          }
        ]
      }
    }
  }
}
```

### Campos clave

| Campo | Descripcion |
|-------|-------------|
| `symbol` | Ticker del ETF |
| `companyName` | Nombre del ETF |
| `lastSalePrice` | Ultimo precio |
| `netChange` | Cambio neto |
| `percentageChange` | Cambio porcentual diario |
| `oneYearPercentage` | Rendimiento a 1 ano |
| `deltaIndicator` | `up` / `down` |

### Coverage

| Metrica | Valor |
|---------|-------|
| Total ETFs | 4,551 |
| Paginacion | 25 por default |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py screener-etf --limit 5
python scripts/fetch_nasdaq.py screener-etf --limit 100 --offset 200
```

---

## 17. IPO Calendar

**Endpoint:** `GET /api/ipo/calendar`

Calendario IPO con secciones: upcoming, priced, filed y withdrawn.

### Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `date` | current | Mes en formato `YYYY-MM` (ej: `2026-06`) |

### Campos del response

```json
{
  "data": {
    "priced": { "asOf": null, "headers": null, "rows": null },
    "upcoming": {
      "upcomingTable": {
        "asOf": null,
        "headers": {
          "proposedTickerSymbol": "Symbol",
          "companyName": "Company Name",
          "proposedExchange": "Exchange/ Market",
          "proposedSharePrice": "Price",
          "sharesOffered": "Shares",
          "expectedPriceDate": "Expected IPO Date",
          "dollarValueOfSharesOffered": "Offer Amount"
        },
        "rows": [
          {
            "dealID": "1386521-118069",
            "proposedTickerSymbol": "FRBT",
            "companyName": "Forbright, Inc.",
            "proposedExchange": "NASDAQ Global Select",
            "proposedSharePrice": "18.00-20.00",
            "sharesOffered": "7,900,000",
            "expectedPriceDate": "6/11/2026",
            "dollarValueOfSharesOffered": "$181,700,000"
          }
        ]
      }
    },
    "filed": { "rows": [...] },
    "withdrawn": { "rows": [...] },
    "month": "6",
    "year": "2026",
    "totalResults": "1"
  }
}
```

### Secciones

| Seccion | Descripcion |
|---------|-------------|
| `upcoming` | IPOs proximas (con fecha, precio, exchange) |
| `priced` | IPOs ya priceadas en el periodo |
| `filed` | IPOs presentadas (filing) |
| `withdrawn` | IPOs retiradas |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py ipo-calendar
python scripts/fetch_nasdaq.py ipo-calendar -q
```

---

## 18. Earnings Calendar

**Endpoint:** `GET /api/calendar/earnings`

Calendario de earnings con estimaciones de EPS, horario y market cap.

### Campos del response

```json
{
  "data": {
    "asOf": "Thu, Jun 4, 2026",
    "headers": {
      "time": "Time",
      "symbol": "Symbol",
      "name": "Company Name",
      "marketCap": "Market Cap",
      "fiscalQuarterEnding": "Fiscal Quarter Ending",
      "epsForecast": "Consensus EPS* Forecast",
      "noOfEsts": "# of Ests",
      "lastYearRptDt": "Last Year's Report Date",
      "lastYearEPS": "Last year's EPS*"
    },
    "rows": [
      {
        "time": "time-pre-market",
        "symbol": "CIEN",
        "name": "Ciena Corporation",
        "marketCap": "$88,656,813,729",
        "fiscalQuarterEnding": "Apr/2026",
        "epsForecast": "$1.20",
        "noOfEsts": "8",
        "lastYearRptDt": "6/05/2025",
        "lastYearEPS": "$0.16"
      }
    ]
  }
}
```

### Campos clave

| Campo | Descripcion |
|-------|-------------|
| `time` | `time-pre-market`, `time-after-hours`, `time-not-supplied` |
| `symbol` | Ticker |
| `name` | Nombre de la empresa |
| `marketCap` | Market cap |
| `fiscalQuarterEnding` | Trimestre fiscal |
| `epsForecast` | EPS estimado consenso |
| `noOfEsts` | Numero de estimaciones de analistas |
| `lastYearRptDt` | Fecha del reporte del año anterior |
| `lastYearEPS` | EPS del año anterior |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py earnings-calendar
python scripts/fetch_nasdaq.py earnings-calendar -q
```

---

## 19. Dividend Calendar

**Endpoint:** `GET /api/calendar/dividends`

Calendario de dividendos con fechas ex-date, pay-date, record-date, y montos.

### Campos del response

```json
{
  "data": {
    "calendar": {
      "asOf": "Thu, Jun 4, 2026",
      "headers": {
        "symbol": "Symbol",
        "companyName": "Name",
        "dividend_Ex_Date": "Ex-Dividend Date",
        "payment_Date": "Payment Date",
        "record_Date": "Record Date",
        "dividend_Rate": "Dividend",
        "indicated_Annual_Dividend": "Historical Annual Dividend",
        "announcement_Date": "Announcement Date"
      },
      "rows": [
        {
          "companyName": "Exelon Corporation Common Stock",
          "symbol": "EXC",
          "dividend_Ex_Date": "6/04/2026",
          "payment_Date": "6/15/2026",
          "record_Date": "6/04/2026",
          "dividend_Rate": 0.42,
          "indicated_Annual_Dividend": 1.68,
          "announcement_Date": "4/28/2026"
        }
      ]
    },
    "timeframe": { ... }
  }
}
```

### Campos clave

| Campo | Descripcion |
|-------|-------------|
| `symbol` | Ticker |
| `companyName` | Nombre de la empresa |
| `dividend_Ex_Date` | Fecha ex-dividendo |
| `payment_Date` | Fecha de pago |
| `record_Date` | Fecha de registro |
| `dividend_Rate` | Monto del dividendo (float) |
| `indicated_Annual_Dividend` | Dividendo anualizado (float) |
| `announcement_Date` | Fecha de anuncio |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py dividend-calendar
python scripts/fetch_nasdaq.py dividend-calendar -q
```

---

## 20. Splits Calendar

**Endpoint:** `GET /api/calendar/splits`

Calendario de stock splits con ratio y fecha efectiva.

### Campos del response

```json
{
  "data": {
    "asOf": "Wed, Jun 3, 2026",
    "headers": {
      "symbol": "SYMBOL",
      "name": "COMPANY",
      "ratio": "RATIO",
      "executionDate": "EFFECTIVE DATE"
    },
    "rows": [
      {
        "symbol": "SMERY",
        "name": "Siemens Energy AG",
        "ratio": "5 : 1",
        "executionDate": "6/22/2026"
      },
      {
        "symbol": "CCBC",
        "name": "Chino Commercial Bancorp",
        "ratio": "6 : 5",
        "executionDate": "6/18/2026"
      }
    ]
  }
}
```

### Campos clave

| Campo | Descripcion |
|-------|-------------|
| `symbol` | Ticker |
| `name` | Nombre de la empresa |
| `ratio` | Ratio del split (ej: `5 : 1`, `1 : 40`) |
| `executionDate` | Fecha efectiva del split |

### Interpretacion del ratio

| Ratio | Significado |
|-------|-------------|
| `5 : 1` | Reverse split: 5 acciones viejas = 1 nueva |
| `6 : 5` | Forward split: 6 acciones nuevas por cada 5 viejas |
| `1 : 40` | Reverse split fuerte: 40 acciones viejas = 1 nueva |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py splits-calendar
python scripts/fetch_nasdaq.py splits-calendar -q
```

---

## 21. Economic Calendar

**Endpoint:** `GET /api/calendar/economicevents?date=YYYY-MM-DD`

Calendario de eventos economicos con valor actual, consenso y anterior.

### Parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `date` | today | Fecha en formato `YYYY-MM-DD` |

### Campos del response

```json
{
  "data": {
    "date": "2026-06-04",
    "events": [
      {
        "dateTime": "2026-06-04T11:00:00",
        "eventName": "Jobless Claims",
        "eventType": "Weekly",
        "previous": "229K",
        "consensus": "227K",
        "actual": "225K",
        "unit": "K",
        "importance": "high",
        "impact": "decrease",
        "description": "Initial Jobless Claims",
        "source": "Department of Labor"
      },
      {
        "dateTime": "2026-06-04T11:00:00",
        "eventName": "Continuing Claims",
        "eventType": "Weekly",
        "previous": "1,793K",
        "consensus": "1,790K",
        "actual": "1,787K",
        "unit": "K",
        "importance": "medium",
        "impact": "decrease",
        "description": "Continuing Jobless Claims",
        "source": "Department of Labor"
      }
    ]
  }
}
```

### Campos clave

| Campo | Descripcion |
|-------|-------------|
| `dateTime` | Fecha y hora del evento |
| `eventName` | Nombre del evento |
| `eventType` | Tipo (Weekly, Monthly, Quarterly) |
| `previous` | Valor anterior |
| `consensus` | Estimacion de consenso |
| `actual` | Valor actual (cuando se publica) |
| `unit` | Unidad (%, K, B, etc.) |
| `importance` | `high`, `medium`, `low` |
| `impact` | `increase`, `decrease`, `unchanged` |
| `description` | Descripcion del evento |
| `source` | Fuente de datos |

### Interpretacion

| Importancia | Significado |
|-------------|-------------|
| `high` | Evento mayor (Fed, NFP, CPI, GDP) |
| `medium` | Evento intermedio (claims, durable goods) |
| `low` | Evento menor |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py economic-calendar
python scripts/fetch_nasdaq.py economic-calendar --date 2026-06-04
python scripts/fetch_nasdaq.py economic-calendar -q
```

---

## 22. All — Fetch Combinado

El modo `all` ejecuta todos los endpoints disponibles secuencialmente con rate limiting de 0.3s entre requests.

### Output

```json
{
  "ticker": "GGAL",
  "timestamp": "2026-06-04T07:20:52",
  "info": { ... },
  "short_interest": { ... },
  "chart": { ... },
  "financials": { ... },
  "institutional_holdings": { ... },
  "company_profile": { ... },
  "dividends": { ... },
  "news": { ... }
}
```

### Tiempo estimado

| Ticker | Tiempo | Tamaño output |
|--------|--------|---------------|
| GGAL | ~25s | ~77KB |
| NVDA | ~25s | ~100KB+ |

### Ejemplo

```bash
python scripts/fetch_nasdaq.py all NVDA -o nvda_completo.json
python scripts/fetch_nasdaq.py all GGAL -q
```

---

## 23. Consideraciones Tecnicas

### Rate Limiting

La API de Nasdaq no tiene rate limiting documentado, pero por experiencia:

| Comportamiento | Consecuencia |
|---------------|--------------|
| 1 req/0.3s | ✅ Seguro |
| 1 req/0.1s | ⚠️ Posibles errores 429 |
| Multiples requests simultaneos | ❌ Riesgo de baneo temporal |

### Manejo de errores

El status de cada response incluye:

```json
{
  "status": {
    "rCode": 200,
    "bCodeMessage": null
  }
}
```

| rCode | Significado |
|-------|-------------|
| 200 | OK |
| 400 | Bad request (parametros faltantes) |
| 404 | Endpoint no encontrado / ticker no soportado |
| 429 | Rate limit excedido |

### Tickers internacionales

Nasdaq.com cubre principalmente empresas listadas en bolsas de EE.UU.:
- **NASDAQ**: NVDA, AAPL, MSFT, GOOG, AMZN, META
- **NYSE**: BRK.B, JPM, V, JNJ, WMT
- **AMEX**: SLV, GLD, etc.

No cubre tickers de mercados internacionales directamente (ej: `GGAL.BA` no funciona, usar `GGAL` para el ADR).

### Formato de valores

- Precios: `"$214.75"` (string con $)
- Cambios: `"-8.07"` (string)
- Volumen: `"160,910,801"` (string con comas)
- Market Cap: `"5.581T"` (string con sufijo T/B/M)
- Fechas: `"MM/DD/YYYY"` (string)
- Porcentajes: `"-3.62%"` (string)

### Headers requeridos

Siempre incluir:
- `User-Agent` de navegador moderno
- `Accept: application/json`
- `Referer: https://www.nasdaq.com/`

Sin estos headers, algunos endpoints pueden devolver 403/404.

---

## 24. Endpoints No Disponibles

Los siguientes datos de Nasdaq.com **no tienen endpoint JSON interno** identificado:

| Seccion | URL | Alternativa |
|---------|-----|-------------|
| **Holiday Schedule** | `/market-activity/stock-market-holiday-schedule` | Sin API interna detectada |
| **ETF Detail (AUM, desc, fees)** | No disponible en Nasdaq.com | Usar skill `companiesmarketcap --etf TICKER` |

Para estos casos, se recomienda:
1. **ETF Detail**: Usar el skill `companiesmarketcap` (endpoint `--etf TICKER`)
