# SimplyWallSt API Reference

Documentación detallada de la API interna de SimplyWallSt descubierta mediante reverse engineering.

---

## Descubrimiento

SimplyWallSt expone una API REST interna bajo `https://simplywall.st/api/` que su frontend Next.js consume directamente. A diferencia del sitio público (protegido por Cloudflare), **los endpoints `/api/` NO tienen Cloudflare** y responden con JSON puro.

El backend interno corre en `http://api.prod.sws.tools/` (visible en errores 404).

---

## Endpoints

### 1. Company List — Grid/Filter

Obtiene listado de empresas con scores, info y grid metrics.

```
POST https://simplywall.st/api/grid/filter?include=info,score,grid
```

**Headers:**
```
Content-Type: application/json
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

**Request Body:**
```json
{
  "id": "0",
  "no_result_if_limit": false,
  "offset": 0,
  "size": 24,
  "state": "read",
  "rules": "[[\"order_by\",\"market_cap\",\"desc\"],[\"value_score\",\">=\",0],[\"dividends_score\",\">=\",0],[\"future_performance_score\",\">=\",0],[\"health_score\",\">=\",0],[\"past_performance_score\",\">=\",0],[\"grid_visible_flag\",\"=\",true],[\"market_cap\",\"is_not_null\"],[\"primary_flag\",\"=\",true],[\"is_fund\",\"=\",false]]"
}
```

**Response:**
```json
{
  "data": [
    {
      "id": 32307,
      "company_id": "08830E11-EECD-4A85-982D-B0AE1DFD6F7A",
      "trading_item_id": 2635154,
      "name": "NVIDIA",
      "slug": "nvidia",
      "exchange_symbol": "NasdaqGS",
      "ticker_symbol": "NVDA",
      "unique_symbol": "NasdaqGS:NVDA",
      "primary_ticker": true,
      "last_updated": 1780358400000,
      "canonical_url": "/stocks/us/semiconductors/nasdaq-nvda/nvidia",
      "primary_canonical_url": "/stocks/us/semiconductors/nasdaq-nvda/nvidia",
      "is_searchable": true,
      "isin_symbol": "US67066G1040",
      "info": { ... },
      "score": { ... },
      "grid": { ... }
    }
  ],
  "meta": { "total_records": 120000 }
}
```

#### Parámetros del Body

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Siempre "0" |
| `offset` | int | Paginación offset |
| `size` | int | Tamaño de página (max ~100) |
| `state` | string | Siempre "read" |
| `rules` | string | JSON stringified array de reglas |
| `no_result_if_limit` | bool | false para obtener resultados parciales |

#### Reglas (rules) disponibles

| Operador | Campo | Valor |
|----------|-------|-------|
| `order_by` | `market_cap`, `value_score`, `dividends_score`, etc. | `asc`/`desc` |
| `>=` | `value_score`, `dividends_score`, `future_performance_score`, `health_score`, `past_performance_score` | 0-6 |
| `=` | `grid_visible_flag` | `true` |
| `=` | `primary_flag` | `true` |
| `=` | `is_fund` | `false` |
| `is_not_null` | `market_cap` | (sin valor) |

> **Nota:** No se puede filtrar por `country` o `ticker_symbol` directamente. El filtrado por país se hace client-side.

#### Grid Data Fields

| Campo | Descripción | Ejemplo (GGAL) |
|-------|-------------|-----------------|
| `year_founded` | Año de fundación | 1905 |
| `description` | Descripción corta | "A financial service holding company..." |
| `share_price` | Precio actual | 7585.0 |
| `market_cap` | Market cap | 8.6T |
| `pe` | P/E ratio | 176.68 |
| `pb` | P/B ratio | 1.42 |
| `price_to_sales` | Price/Sales | - |
| `analyst_count` | N° de analistas | 7 |
| `return_1d` | Retorno 1 día | -0.0069 |
| `return_7d` | Retorno 7 días | 0.037 |
| `return_1yr_abs` | Retorno 1 año | 0.578 |
| `price_target` | Precio objetivo | 296.81 |
| `growth_3y` | Crecimiento 3 años | 0.212 |
| `net_income_growth_annual` | Crecimiento net income anual | 0.212 |
| `revenue_growth_annual` | Crecimiento revenue anual | 0.241 |
| `dividend_yield` | Dividend yield | 0.0045 |

---

### 2. Company Detail

Obtiene data detallada de una empresa específica.

```
GET https://simplywall.st/api/company{canonical_url}
```

**Parámetros Query:**
```
include=info,score,analysis,analysis.extended,analysis.extended.raw_data,analysis.extended.raw_data.insider_transactions
version=2.0
```

**Ejemplo URL:**
```
GET https://simplywall.st/api/company/stocks/ar/banks/base-ggal/grupo-financiero-galicia-shares?include=info,score,analysis&version=2.0
```

**Response Structure:**
```json
{
  "data": {
    "id": 1532718,
    "company_id": "392D0D4E-FEE1-4F68-82E8-8D41C0EE5D31",
    "name": "Grupo Financiero Galicia",
    "slug": "grupo-financiero-galicia",
    "exchange_symbol": "BASE",
    "ticker_symbol": "GGAL",
    "unique_symbol": "BASE:GGAL",
    "canonical_url": "/stocks/ar/banks/base-ggal/grupo-financiero-galicia-shares",
    "isin_symbol": "ARP495251018",
    "info": { ... },
    "score": { ... },
    "analysis": { ... }
  }
}
```

---

## Includes Detallados

### `info` — Corporate Profile

```json
{
  "info": {
    "data": {
      "id": "392D0D4E-FEE1-4F68-82E8-8D41C0EE5D31",
      "description": "A financial service holding company...",
      "warning_type": 0,
      "industry": {
        "name": "Banks",
        "primary_id": 7010000,
        "secondary_id": 7011000,
        "tertiary_id": 7012000
      },
      "fund": false,
      "status": "Operating",
      "currency": "ARS",
      "country": "AR",
      "employees": 10032,
      "address": "Teniente General Juan D. PerOn 430, Buenos Aires...",
      "year_founded": 1905,
      "url": "www.gfgsa.com",
      "logo_url": "/api/company/image/BMV:GGAL N/logo",
      "has_logo": true,
      "ceo": {
        "name": "Fabian Enrique Kon",
        "age": null,
        "url": "/api/person/image/681523495"
      },
      "legal_name": "Grupo Financiero Galicia S.A."
    }
  }
}
```

**Campos:**
- `description` — Descripción de la empresa
- `industry` — Objeto con `name`, `primary_id`, `secondary_id`, `tertiary_id`
- `fund` — Booleano, si es un fondo
- `status` — "Operating", etc.
- `currency` — Moneda de cotización (ARS, USD, etc.)
- `country` — Código ISO país (AR, US, etc.)
- `employees` — Cantidad de empleados
- `year_founded` — Año de fundación
- `ceo` — Objeto con `name`, `age`, `url`

---

### `score` — Snowflake Scores

```json
{
  "score": {
    "data": {
      "value": 0,
      "income": 0,
      "health": 4,
      "past": 1,
      "future": 5,
      "management": 0,
      "misc": 0,
      "total": 12,
      "sentence": "High growth potential with adequate balance sheet."
    }
  }
}
```

**Interpretación de scores (0-6):**

| Score | Rango | Significado |
|-------|-------|-------------|
| `value` | 0-6 | Valuación (descuento vs fair value) |
| `income` | 0-6 | Rentabilidad (dividendos, buybacks) |
| `health` | 0-6 | Salud financiera (balance sheet) |
| `past` | 0-6 | Performance pasada (5yr returns) |
| `future` | 0-6 | Potencial de crecimiento futuro |
| `management` | 0-6 | Calidad del management |
| `total` | 0-36 | Score total |
| `sentence` | string | Frase resumen del análisis |

**Rango de total: 0-36** (suma de los 6 scores individuales, cada uno 0-6)

---

### `analysis` — Key Metrics

```json
{
  "analysis": {
    "data": {
      "id": "392D0D4E-FEE1-4F68-82E8-8D41C0EE5D31",
      "share_price": 7585.0,
      "market_cap": 8602.51672118156,
      "intrinsic_discount": -55.61,
      "pe": 176.68,
      "pb": 1.42,
      "peg": 4.64,
      "preferred_multiple": "pb",
      "preferred_multiple_reason": "isProfitableAbovePeThreshold",
      "preferred_relative_multiple_average_peer_value": 1.31,
      "justified_preferred_multiple_ratio": null,
      "roe": 0.803,
      "roa": 0.153,
      "eps": 42.93,
      "debt_equity": 0.779,
      "dividend": {
        "current": 0,
        "future": 3.81,
        "upcoming": false,
        "ex_date": null
      },
      "future": {
        "growth_1y": 11.30,
        "growth_3y": 29.64,
        "roe_1y": 16.20,
        "roe_3y": 17.37
      },
      "past": {
        "growth_1y": -96.54,
        "growth_5y": 40.69
      },
      "analyst_count": 7,
      "insider_buying": null,
      "show_new_valuation": true,
      "show_analyst_price_target": true
    }
  }
}
```

**Campos principales:**

| Campo | Descripción | Unidad |
|-------|-------------|--------|
| `share_price` | Precio actual | Moneda local |
| `market_cap` | Market capitalization | Moneda local (billions?) |
| `intrinsic_discount` | Descuento respecto a fair value | % (negativo = sobrevaluado) |
| `pe` | Price/Earnings ratio | ratio |
| `pb` | Price/Book ratio | ratio |
| `peg` | PEG ratio | ratio |
| `roe` | Return on Equity | decimal (0.803 = 80.3%) |
| `roa` | Return on Assets | decimal |
| `eps` | Earnings Per Share | moneda local |
| `debt_equity` | Debt to Equity | ratio |
| `analyst_count` | N° de analistas cubriendo | entero |
| `insider_buying` | Insider buying activity | null o detalle |

**Dividend:**

| Campo | Descripción |
|-------|-------------|
| `current` | Current dividend yield (0 = no paga) |
| `future` | Future/projected dividend yield |
| `upcoming` | Próximo pago programado |
| `ex_date` | Fecha ex-dividendo (timestamp ms) |

**Future:**

| Campo | Descripción |
|-------|-------------|
| `growth_1y` | Crecimiento EPS proyectado 1 año (%) |
| `growth_3y` | Crecimiento EPS proyectado 3 años (%) |
| `roe_1y` | ROE proyectado 1 año (%) |
| `roe_3y` | ROE proyectado 3 años (%) |

**Past:**

| Campo | Descripción |
|-------|-------------|
| `growth_1y` | Crecimiento earnings 1 año (%) |
| `growth_5y` | Crecimiento earnings 5 años (%) |

---

### `analysis.extended` — Extended Data

```json
{
  "analysis": {
    "extended": {
      "data": {
        "analysis": {
          "dividend": {
            "dividend_yield": 0,
            "dividend_yield_future": 0.0381,
            "dividend_paying_years": 0,
            "payout_ratio": 0,
            "payout_ratio_3y": 0.3105,
            "historical_dividend_yield": {
              "1455235200000": 0.00272,
              "1461888000000": 0.00284,
              ...
            },
            "historical_dividend_payments": {
              "1455235200000": 0.1154,
              ...
              "1683072000000": 26.4462,
              "1780358400000": 0
            },
            "merged_future_dividends_per_share": {
              "1780358400000": 0,
              "1798675200000": 81.28,
              "1830211200000": 262.85,
              "1861833600000": 453.64
            },
            "merged_future_yield": {
              "1780358400000": 0,
              "1798675200000": 0.0107,
              "1830211200000": 0.0347,
              "1861833600000": 0.0598
            },
            "buyback_yield": 0.001045,
            "total_shareholder_yield": 0.001045,
            "payout_ratio_median_3yr": 0.0843,
            "dividend_payments_ltm": 326.09,
            "payout_ratio_history": {
              "1435622400000": 0.02687,
              ...
            },
            "dividend_currency_iso": "ARS"
          },
          "future": {
            "return_on_equity_1y": 0.162,
            "return_on_equity_3y": 0.174,
            "earnings_per_share_growth_1y": 11.30,
            "earnings_per_share_growth_3y": 29.64,
            "earnings_per_share_1y": 528.10,
            "earnings_per_share_2y": 1075.90,
            "earnings_per_share_3y": 1744.20
          }
        }
      }
    }
  }
}
```

**Campos de dividendos extendidos:**

| Campo | Descripción |
|-------|-------------|
| `dividend_yield` | Dividend yield actual |
| `dividend_yield_future` | Dividend yield futuro proyectado |
| `dividend_paying_years` | Años pagando dividendos |
| `payout_ratio` | Payout ratio actual |
| `payout_ratio_3y` | Payout ratio promedio 3 años |
| `historical_dividend_yield` | Mapa timestamp → yield histórico |
| `historical_dividend_payments` | Mapa timestamp → pago histórico |
| `merged_future_dividends_per_share` | Dividendos futuros por acción proyectados |
| `merged_future_yield` | Yield futuro proyectado |
| `buyback_yield` | Buyback yield |
| `total_shareholder_yield` | Total shareholder yield (dividend + buyback) |
| `payout_ratio_median_3yr` | Payout ratio mediano 3 años |
| `dividend_payments_ltm` | Dividendos últimos 12 meses |
| `payout_ratio_history` | Mapa timestamp → payout ratio histórico |
| `dividend_currency_iso` | Moneda de dividendos (ARS, USD) |

**Nota sobre timestamps:** Las claves son timestamps UNIX en milisegundos. Convertir con:
- Python: `datetime.fromtimestamp(ts / 1000)`

---

### `analysis.extended.raw_data` — Raw Financial Data

Incluye arrays de datos financieros históricos. Estructura general:

```json
{
  "analysis": {
    "extended": {
      "raw_data": {
        "data": {
          "balance_sheets": [ ... ],
          "income_statements": [ ... ],
          "cash_flow_statements": [ ... ],
          "financial_ratios": [ ... ],
          "insider_transactions": [ ... ]
        }
      }
    }
  }
}
```

Contiene data numérica de financial statements para cálculos personalizados.

---

## Flujo de trabajo típico

### 1. Obtener listado de empresas
```python
POST /api/grid/filter?include=info,score,grid
```
→ Obtener `canonical_url` de cada empresa

### 2. Obtener detalle de una empresa
```python
GET /api/company{canonical_url}?include=info,score,analysis,analysis.extended
```
→ Obtener toda la data disponible

### 3. Construir URL desde ticker
1. Buscar ticker en grid/filter (iterate pages)
2. Extraer `canonical_url`
3. Llamar company detail

---

## Consideraciones técnicas

### Rate Limiting
- Sin límite explícito observado
- Recomendado: 300-500ms entre requests
- El backend (`api.prod.sws.tools`) puede tener protecciones

### Actualización de datos
- `last_updated` es timestamp en ms
- Precios se actualizan daily (cierre)
- Scores se recalculan periódicamente

### Monedas
- Los precios están en la moneda local del exchange (ARS para BASE)
- Market cap también en moneda local
- Dividend currency puede diferir

### Manejo de errores

| Código | Significado |
|--------|-------------|
| 200 | OK |
| 400 | Invalid rule o bad request |
| 404 | Company no encontrada o ruta inválida |
| 405 | Method not allowed (usar POST para grid) |
| 500 | Error interno |

---

## Coverage de tickers

SimplyWallSt cubre **120,000+ stocks** en **90+ mercados globales**. Ejemplos por región:

| Región | Exchange | Ejemplos |
|--------|----------|----------|
| Argentina | BASE (BCBA) | GGAL, BMA, SUPV, YPFD, TXAR, CEpu, COME, PAMP, TRAN, EDN, etc. |
| US | NasdaqGS, NYSE, AMEX | AAPL, MSFT, NVDA, AMZN, GOOGL, SPY, etc. |
| Europa | LSE, XETRA, Euronext | SHEL, BP, SAP, AIR, etc. |
| Asia | TSE, HKE, SSE | TM, 7203.T, 9984.T, etc. |

### Exchange Symbols comunes

| Símbolo | Exchange |
|---------|----------|
| `BASE` | Bolsa de Buenos Aires (BCBA) |
| `NasdaqGS` | NASDAQ Global Select |
| `NYSE` | New York Stock Exchange |
| `LSE` | London Stock Exchange |
| `XETRA` | Deutsche Börse Xetra |
| `TSE` | Tokyo Stock Exchange |
| `HKE` | Hong Kong Exchange |

---

## Limitaciones conocidas

1. **Grid/filter** no soporta filtrado por ticker o país — solo los campos en rules
2. **News endpoint** existe pero devuelve `[]` para la mayoría de tickers
3. **Search endpoint** (`/api/search`) no existe (404)
4. **Peers endpoint** (`/api/company/.../peers`) requiere company_id, no canonical_url
5. **Narratives endpoint** (`/api/narratives/`) no tiene ruta
6. `api.simplywall.st` está protegido por Cloudflare — usar `simplywall.st/api/`
7. No hay data histórica de precios OHLC — solo snapshot actual

---

## Exchange → Country Mapping

Todos los **106 exchanges** cubiertos por SimplyWallSt según snapshot `26-06-04` (78,454 listings).

| Exchange | País | Listings | Mercado |
|----------|------|---------:|---------|
| `ADX` | AE | 117 | Abu Dhabi Securities Exchange |
| `AIM` | GB | 832 | AIM (London Stock Exchange) |
| `ASE` | GR | 172 | Athens Stock Exchange |
| `ASX` | AU | 2,527 | Australian Securities Exchange |
| `ATSE` | GR | 165 | Athens Stock Exchange (ATHEX) |
| `BASE` | AR | 84 | Bolsa de Buenos Aires (BCBA) |
| `BATS` | US | 1,575 | BATS Exchange |
| `BATS-CHIXE` | GB | 14 | BATS Europe / CHI-X |
| `BAX` | BH | 41 | Bahrain Bourse |
| `BDB` | DE | 9 | Baden-Württembergische Wertpapierbörse |
| `BDL` | BD | 44 | Bondholders (Bangladesh) |
| `BDM` | DE | 9 | Börse Düsseldorf |
| `BELEX` | RS | 134 | Belgrade Stock Exchange |
| `BIT` | IT | 760 | Borsa Italiana |
| `BME` | ES | 1,514 | Bolsas y Mercados Españoles |
| `BMV` | MX | 209 | Bolsa Mexicana de Valores |
| `BOVESPA` | BR | 1,120 | B3 (Brasil) |
| `BRSE` | CH | 22 | Bern Stock Exchange |
| `BRVM` | CI | 46 | Bourse Régionale des Valeurs Mobilières |
| `BSE` | IN | 3,833 | BSE India (antes Bombay SE) |
| `BSSE` | BS | 19 | Bahamas Securities Exchange |
| `BUL` | BG | 257 | Bulgarian Stock Exchange |
| `BUSE` | HU | 88 | Budapest Stock Exchange |
| `BVB` | RO | 331 | Bucharest Stock Exchange |
| `BVC` | CO | 72 | Bolsa de Valores de Colombia |
| `BVL` | PE | 121 | Bolsa de Valores de Lima |
| `BVMT` | TN | 84 | Bourse des Valeurs Mobilières de Tunis |
| `CASE` | EG | 233 | Egyptian Exchange (EGX) |
| `CBSE` | CY | 80 | Cyprus Stock Exchange |
| `CCSE` | HR | 41 | Zagreb Stock Exchange |
| `CNSX` | CA | 841 | Canadian Securities Exchange |
| `COSE` | MU | 292 | Stock Exchange of Mauritius |
| `CPSE` | DK | 675 | Copenhagen Stock Exchange |
| `CSE` | LK | 88 | Colombo Stock Exchange (Sri Lanka) |
| `DAR` | TZ | 22 | Dar es Salaam Stock Exchange |
| `DB` | DE | 716 | Deutsche Börse (Frankfurt) |
| `DFM` | AE | 58 | Dubai Financial Market |
| `DSE` | BD | 395 | Dhaka Stock Exchange |
| `DSM` | QA | 57 | Qatar Stock Exchange |
| `DUSE` | DE | 90 | Börse Stuttgart |
| `ENXTAM` | NL | 285 | Euronext Amsterdam |
| `ENXTBR` | BE | 209 | Euronext Brussels |
| `ENXTLS` | PT | 60 | Euronext Lisbon |
| `ENXTPA` | FR | 1,147 | Euronext Paris |
| `GHSE` | GH | 33 | Ghana Stock Exchange |
| `HLSE` | FI | 201 | Helsinki Stock Exchange |
| `HMSE` | DE | 122 | Börse Hamburg |
| `HNX` | VN | 357 | Hanoi Stock Exchange |
| `HOSE` | VN | 462 | Ho Chi Minh Stock Exchange |
| `IBSE` | IE | 624 | Irish Stock Exchange |
| `ICSE` | IS | 30 | Iceland Stock Exchange |
| `IDX` | ID | 985 | Indonesia Stock Exchange |
| `ISE` | IT | 29 | Italian Stock Exchange (MTA) |
| `JSE` | ZA | 417 | Johannesburg Stock Exchange |
| `KASE` | PK | 521 | Pakistan Stock Exchange |
| `KLSE` | MY | 1,172 | Bursa Malaysia |
| `KOSDAQ` | KR | 1,997 | KOSDAQ (Korea) |
| `KOSE` | KR | 2,075 | Korea Exchange (KOSPI) |
| `KWSE` | KW | 159 | Boursa Kuwait |
| `LJSE` | SI | 61 | Ljubljana Stock Exchange |
| `LSE` | GB | 1,963 | London Stock Exchange |
| `LUSE` | LU | 24 | Luxembourg Stock Exchange |
| `MAL` | MT | 15 | Malta Stock Exchange |
| `MISX` | RU | 212 | Moscow Exchange (MOEX) |
| `MSM` | OM | 118 | Muscat Securities Market |
| `MTSE` | MX | 36 | Mexican Stock Exchange (BIVA) |
| `MUSE` | MU | 103 | Stock Exchange of Mauritius |
| `NASE` | NA | 62 | Namibian Stock Exchange |
| `NGSE` | NG | 167 | Nigerian Exchange Group |
| `NSE` | KE | 71 | Nairobi Securities Exchange |
| `NSEI` | IN | 2,241 | National Stock Exchange of India |
| `NSEL` | IN | 29 | National Stock Exchange (India SME) |
| `NYSE` | US | 2,574 | New York Stock Exchange |
| `NYSEAM` | US | 297 | NYSE American |
| `NZSE` | NZ | 173 | New Zealand Stock Exchange |
| `NasdaqCM` | US | 1,854 | NASDAQ Capital Market |
| `NasdaqGM` | US | 2,304 | NASDAQ Global Market |
| `NasdaqGS` | US | 1,532 | NASDAQ Global Select |
| `OB` | NO | 368 | Oslo Børs |
| `OM` | SE | 852 | OMX Nordic (Stockholm) |
| `OTCNO` | US | 41 | OTC Markets (No quota) |
| `OTCPK` | US | 6,138 | OTC Markets Pink |
| `PSE` | PH | 281 | Philippine Stock Exchange |
| `SASE` | SA | 414 | Saudi Stock Exchange (Tadawul) |
| `SEHK` | HK | 3,019 | Hong Kong Stock Exchange |
| `SEP` | SE | 30 | Spotlight Stock Market (Suecia) |
| `SET` | TH | 993 | Stock Exchange of Thailand |
| `SGX` | SG | 446 | Singapore Exchange |
| `SHSE` | CN | 3,293 | Shanghai Stock Exchange |
| `SNSE` | CL | 689 | Bolsa de Santiago (Chile) |
| `SWX` | CH | 552 | SIX Swiss Exchange |
| `SZSE` | CN | 3,723 | Shenzhen Stock Exchange |
| `TASE` | IL | 1,029 | Tel Aviv Stock Exchange |
| `TLSE` | EE | 37 | Tallinn Stock Exchange (Baltic) |
| `TPEX` | TW | 1,430 | Taipei Exchange (GreTai) |
| `TSE` | JP | 4,693 | Tokyo Stock Exchange |
| `TSX` | CA | 2,381 | Toronto Stock Exchange |
| `TSXV` | CA | 1,999 | TSX Venture Exchange |
| `TTSE` | TT | 26 | Trinidad and Tobago Stock Exchange |
| `TWSE` | TW | 1,292 | Taiwan Stock Exchange |
| `UGSE` | UG | 11 | Uganda Securities Exchange |
| `WBAG` | AT | 87 | Wiener Börse (Vienna) |
| `WSE` | PL | 849 | Warsaw Stock Exchange |
| `XTRA` | DE | 1,135 | Xetra (Deutsche Börse) |
| `ZGSE` | HR | 97 | Zagreb Stock Exchange |
| `ZMSE` | ZM | 41 | Lusaka Stock Exchange (Zambia) |

> **Nota:** Los counts son del snapshot `26-06-04`. Los valores pueden variar ligeramente en snapshots posteriores.

---

## Comparación con otras fuentes

| Feature | SimplyWallSt | Yahoo Finance | MarketScreener |
|---------|-------------|---------------|----------------|
| Snowflake scores | ✅ Único | ❌ | ❌ |
| Dividend history | ✅ 19+ años | ✅ | ✅ |
| Insider transactions | ✅ | ✅ | ✅ |
| Financial statements | ✅ Raw data | ✅ | ✅ |
| Price target | ✅ Consensus | ✅ | ✅ |
| Cloudflare | ⚠️ Solo web, API no | ✅ No | ✅ No |
| API key | ❌ No necesita | ❌ No necesita | ❌ No necesita |
| Cobertura | 120K stocks | Global | 20K+ stocks |
| Rate limit | ~300ms | ~1s (crumb) | ~1.5s |

---

## Changelog de descubrimiento

| Fecha | Descubrimiento |
|------|----------------|
| 2026-06-03 | Endpoint `/api/company{canonical_url}` funciona sin Cloudflare |
| 2026-06-03 | Endpoint `/api/grid/filter` con rules JSON permite listar empresas |
| 2026-06-03 | Includes: info, score, analysis, analysis.extended, analysis.extended.raw_data |
| 2026-06-03 | Grid rules no soportan filtro por country o ticker |
