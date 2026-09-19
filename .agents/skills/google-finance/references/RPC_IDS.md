# RPC IDs — Catalogo Detallado

> Lista exhaustiva de los **RPC IDs** que se pueden invocar via el endpoint
> `batchexecute` de Google Finance. Cada RPC retorna un shape diferente —
> aca documentamos args, output, ejemplos y caveats.

**Endpoint comun:** `POST https://www.google.com/finance/beta/_/FinHubUi/data/batchexecute?rpcids={RPC_ID}`

> ⚠️ **Estos RPC IDs son INTERNOS de Google y pueden cambiar sin aviso.**
> Si una llamada empieza a fallar con HTTP 400 o devolver `null`, ver
> [`LIMITATIONS_TROUBLESHOOTING.md`](./LIMITATIONS_TROUBLESHOOTING.md)
> seccion "Re-derivar mappings desde el HTML".

---

## Indice

1. [Tabla resumen](#1-tabla-resumen)
2. [hgueg — Indices globales](#2-hgueg--indices-globales)
3. [vNewwe — Sectors heatmap](#3-vnewwe--sectors-heatmap)
4. [gCvqoe — Quote basico](#4-gcvqoe--quote-basico)
5. [JL8oKc — Descripcion empresa](#5-jl8okc--descripcion-empresa)
6. [SICF5d — Peers / related stocks](#6-sicf5d--peers--related-stocks)
7. [YTM9q — Analyst recommendations](#7-ytm9q--analyst-recommendations)
8. [XxQsbd — Earnings history](#8-xxqsbd--earnings-history)
9. [dlNq8b — Quote enriquecido](#9-dlnq8b--quote-enriquecido)
10. [c2u4wc — OHLC (4 variantes)](#10-c2u4wc--ohlc-4-variantes)
11. [gXxkFd — Ratings tecnicos](#11-gxxkfd--ratings-tecnicos)
12. [Pr8h2e — Financials masivos](#12-pr8h2e--financials-masivos)
13. [kA4MVd — News (2 variantes)](#13-ka4mvd--news-2-variantes)
14. [RPCs desconocidos](#14-rpcs-desconocidos)

---

## 1. Tabla resumen

| RPC ID | Modo CLI | Args template | Necesita simbolo | Output size |
|--------|----------|---------------|:---:|:---:|
| `hgueg` | `indices` | `[1]` | ❌ | ~10 KB |
| `vNewwe` | `sectors` | `[null, [null, 1]]` | ❌ | ~6 KB |
| `gCvqoe` | `quote` | `[[[null, [TKR, EX]]], 1]` | ✅ | ~0.5 KB |
| `JL8oKc` | `description` | `[[[null, [TKR, EX]]]]` | ✅ | ~1 KB |
| `SICF5d` | `peers` | `[[null, [TKR, EX]], 4]` | ✅ | ~3 KB |
| `YTM9q` | `analysts` | `[[null, [TKR, EX]]]` | ✅ | ~3 KB |
| `XxQsbd` | `earnings` | `[[[null, [TKR, EX]]], 1]` | ✅ | ~3 KB |
| `dlNq8b` | `quote-full` | `[[[null, [TKR, EX]]], 1, 1, 1]` | ✅ | ~4 KB |
| `c2u4wc` (1) | `intraday-1min` | `[[[null, [TKR, EX]]], 1]` | ✅ | ~30 KB |
| `c2u4wc` (2) | `intraday-5min` | `[[[null, [TKR, EX]]], 1, null×5, 1]` | ✅ | ~5 KB |
| `c2u4wc` (3) | `daily` | `[[[null, [TKR, EX]]], 3]` | ✅ | ~2.5 KB |
| `c2u4wc` (4) | `daily-6m` | `[[[null, [TKR, EX]]], 4]` | ✅ | ~13 KB |
| `gXxkFd` | `technicals` | `[[TKR, EX]]` | ✅ | ~0.2 KB |
| `Pr8h2e` | `financials` | `[[[null, [TKR, EX]]]]` | ✅ | ~22 KB |
| `kA4MVd` (global) | `news-related` | `[2, 12, [[null, [TKR, EX]]]]` | ✅ | ~14 KB |
| `kA4MVd` (symbol) | `news` | `[5, 12, [[null, [TKR, EX]]]]` | ✅ | ~2 KB |

> Catalogo JSON estructurado: [`../assets/rpc_ids.json`](../assets/rpc_ids.json).

---

## 2. hgueg — Indices globales

**Funcion:** Devuelve los indices globales del mercado (Dow, S&P, NASDAQ, Russell, VIX, DAX, FTSE, Nikkei, Hang Seng, IBEX, CAC, etc) con su quote actual.

### Args

```python
args = [1]
```

> El `1` parece controlar el preset de region. Otros valores no testeados.

### Output (abreviado)

```json
[[[1, [
  [null, [["/m/0cqyw", [".DJI","INDEXDJX"], "Dow Jones Industrial Average", 1, null,
          [51561.93, 874.86, 1.7260, 2,2,2], null, 50687.07, ...]], "Dow Jones"],
  [null, [[..., [".INX","INDEXSP"], "S&P 500", 1, null, [7584.31, ...]]], "S&P 500"],
  [null, [[..., [".IXIC","INDEXNASDAQ"], "Nasdaq Composite", ...]], "Nasdaq"],
  ...
]]]]
```

Estructura: `[[region_id, [[null, quote_array, friendly_name], ...]]]`.

### Indices verificados en el response

`Dow Jones Industrial Average`, `S&P 500`, `Nasdaq Composite`, `Russell 2000`,
`VIX`, `DAX`, `FTSE 100`, `Nikkei 225`, `Hang Seng`, `IBEX 35`, `CAC 40`,
`STOXX 600`, etc.

---

## 3. vNewwe — Sectors heatmap

**Funcion:** Equity sectors heatmap (Health Care, Energy, Tech, etc) con performance %.

### Args

```python
args = [None, [None, 1]]
```

### Output (abreviado)

```json
[[["sectors", ["/g/1q52g4typ", ...10 ids...], "Equity sectors",
  [
    [[null, ["SXDP", "INDEXSTOXX"]], null, 1068.27, "/g/1q52g4typ", 1068.27, 1100, 1098.84,
     2, 31.73, 2, 2.97, 2, null, "SXDP:INDEXSTOXX", "Health Care", 1067.11, ...],
    ...
  ]
]]]
```

### Sectores tipicos

`Health Care`, `Energy`, `Information Technology`, `Financials`,
`Consumer Discretionary`, `Industrials`, `Materials`, `Real Estate`,
`Utilities`, `Communication Services`.

---

## 4. gCvqoe — Quote basico

**Funcion:** Quote actual del simbolo: precio, change, prev_close, currency, market hours, timezone.

### Args

```python
args = [[[None, ["GGAL", "NASDAQ"]]], 1]
# Tambien acepta multiples simbolos: [[[None, ["A","NASDAQ"]],[None,["B","NYSE"]]], 1]
```

### Output

```json
[[[
  "/m/0clbgbw",                                              // freebase_id
  ["GGAL", "NASDAQ"],                                        // ticker_pair
  "Grupo Financiero Galicia SA",                             // company_name
  0,                                                          // unknown_flag
  "USD",                                                      // currency
  [48.62, 0.2899971, 0.60003537, 2, 2, 2],                  // [price, change, change_pct, prec...]
  null,                                                       // unknown
  48.33,                                                      // previous_close
  "#b87040",                                                  // color_hex
  "US",                                                       // country
  "/m/03p28tt",                                              // industry_freebase_id
  [1780619400],                                              // last_update_unix
  "America/New_York",                                        // timezone
  -14400,                                                     // tz_offset_seconds
  "/m/0clbgbw",                                              // freebase_id_dup
  null,
  [48.62, 0, 0, 2, 2, 2],                                   // after_hours_data
  [1780603201],                                              // market_open_unix
  [1780617660],                                              // market_close_unix
  [[1, [2026,6,4,9,30,...], [2026,6,4,16,...]]],            // market_session
  null,
  "GGAL:NASDAQ",                                             // ticker_pair_string
  0, null, null, null, false                                 // misc flags
]]]
```

> Layouts detallados en
> [`../assets/chunk_layouts.json`](../assets/chunk_layouts.json) clave
> `quote_array`.

### Ejemplo cliente Python

```python
data = call_batchexecute("gCvqoe", [[[None, ["GGAL", "NASDAQ"]]], 1])
quote_row = data[0][0]
price = quote_row[5][0]
change_pct = quote_row[5][2]
prev_close = quote_row[7]
print(f"{quote_row[2]}: ${price:.2f} ({change_pct:+.2f}%) prev: ${prev_close:.2f}")
# → Grupo Financiero Galicia SA: $48.62 (+0.60%) prev: $48.33
```

---

## 5. JL8oKc — Descripcion empresa

**Funcion:** Descripcion + address + employees + market cap + ratios + URLs + 52-week range.

### Args

```python
args = [[[None, ["GGAL", "NASDAQ"]]]]
```

### Output (estructura)

```json
[[[
  "/m/0clbgbw",                              // freebase_id
  "Galicia Financial Group",                 // short_name
  "Grupo Financiero Galicia S.A. is a ...",  // description text (~500-2000 chars)
  ["Buenos Aires", "Buenos Aires", "Argentina", "AR", "TTE. GRAL. JUAN D PERON 456"],
                                              // address [city, region, country_full, country_code, street]
  [1905],                                    // founded_year
  null,
  10032,                                     // employees
  6868153427.116013,                         // market_cap
  48.33,                                     // previous_close
  48.25,                                     // open
  49.62,                                     // day_high
  48.25,                                     // day_low
  62.3919,                                   // year_high
  25.89,                                     // year_low
  729353,                                    // volume
  "USD",                                     // currency
  126.878914, 1.2811806,                     // ratios (PE / earnings_growth, orden variable)
  1311218,                                   // shares_outstanding (variable position)
  0.3832, 1.2808,                           // dividend_yield / other
  134277200,                                 // shares
  "http://www.gfgsa.com/",                   // website_url
  "USD",                                     // currency_dup
  ...
  "https://en.wikipedia.org/wiki/...",       // wikipedia_url (cerca del final)
]]]
```

> ⚠️ Los indices 16-21 (PE, EPS, dividend yield, shares) pueden estar
> en **orden distinto** segun el tipo de empresa. Validar empiricamente
> para cada caso.

---

## 6. SICF5d — Peers / related stocks

**Funcion:** Lista de empresas similares (peers) basadas en el simbolo.

### Args

```python
args = [[None, ["GGAL", "NASDAQ"]], 4]  # N=4 peers
# Mayor N retorna mas peers (probar 10, 20)
```

### Output

```json
[[
  [quote_array_peer1],
  [quote_array_peer2],
  ...
]]
```

Cada peer es un quote_array completo igual al de `gCvqoe`.

### Peers tipicos de GGAL

`Banco BBVA Argentina (BBAR:NYSE)`, `Pampa Energia (PAM:NYSE)`,
`Banco Macro (BMA:NYSE)`, `YPF`, `IRSA`, etc.

---

## 7. YTM9q — Analyst recommendations

**Funcion:** Recomendaciones de analistas (resumen + opiniones individuales con firma, target, fecha).

### Args

```python
args = [[None, ["GGAL", "NASDAQ"]]]
```

### Output (2 secciones)

```json
[
  // [0]: Summary header
  ["Grupo Financiero Galicia SA", "USD",
   49,       // price_target_average
   49,       // price_target_high
   49,       // price_target_low
   1.39,     // upside_pct
   2,        // num_analysts
   "Buy",    // consensus_rating
   1, 0, 1, null, 2  // strong_buy / buy / hold / sell / strong_sell counts
  ],
  // [1]: Lista de opiniones individuales
  [
    ["opinion_id", "Analyst Name", "Goldman Sachs", "Hold", "03/06/2026",
     "https://...", "thumbnail.jpg", analyst_5y_return, analyst_avg_return,
     analyst_success_rate, ..., "title", "Author Name", ...,
     target_price, target_change, "USD", target_price, ..., "USD", "slug",
     "ISO_date", "Maintained", 0, 0],
    ...
  ]
]
```

> Layouts detallados en
> [`../assets/chunk_layouts.json`](../assets/chunk_layouts.json) keys
> `analyst_summary_YTM9q` y `analyst_opinion`.

---

## 8. XxQsbd — Earnings history

**Funcion:** Earnings history multi-periodo (años + trimestres) con EPS reportado, revenue, etc.

### Args

```python
args = [[[None, ["GGAL", "NASDAQ"]]], 1]
```

### Output

```json
[[
  ["/m/0clbgbw", ["GGAL","NASDAQ"], "Grupo Financiero Galicia SA",
   2022, 4,           // year, quarter (4 = full year)
   null, null, null, null,
   [null,...,451235000,null,null,...,"USD",[2022,12,31]],  // earnings data
   0, null, 0],
  ["...", "GGAL/NASDAQ", "...", 2026, 2,  // 2026 Q2 forecast/actual
   ...],
  ...
]]
```

Cada row es `[freebase_id, [TKR, EX], 'Name', YEAR, QUARTER, ..., earnings_data_array, ...]`.

---

## 9. dlNq8b — Quote enriquecido

**Funcion:** Quote full con industry, market cap explicito, volume, y mini-cards de peers.

### Args

```python
args = [[[None, ["GGAL", "NASDAQ"]]], 1, 1, 1]
```

### Output

```json
[[[
  [null, ["GGAL","NASDAQ"]],
  null,
  48.25,                              // open
  "/m/0clbgbw",
  48.25,                              // open dup
  49.62,                              // day_high
  48.62,                              // close
  2,
  0.2899971,                          // change_abs
  2,
  0.60003537,                         // change_pct
  2,
  "USD",
  "GGAL:NASDAQ",
  "Grupo Financiero Galicia SA",
  48.33,                              // previous_close
  6868153427.116013,                  // market_cap (precision completa)
  729353,                             // volume
  "Bank",                             // industry_short_name
  [quote_array_completo],             // quote array tipo gCvqoe
  ...
]]]
```

---

## 10. c2u4wc — OHLC (4 variantes)

**Funcion:** Series OHLC historicas. **Las 4 variantes usan el MISMO RPC** (`c2u4wc`) pero con args diferentes.

### Variante 1 — Intraday 1-min del dia actual

```python
args = [[[None, ["GGAL", "NASDAQ"]]], 1]
```

Output: ~30 KB. Cada bar es `[timestamp_array, close_change_array, volume]`.

```json
[[[["GGAL","NASDAQ"], "/m/0clbgbw", "USD",
   [[[1, [market_open_ts], [market_close_ts]],
     [
       [[2026,6,4,9,30,...,[-14400]], [48.7, 0.37, 0.0077, 2,2,4], 2200],
       [[2026,6,4,9,31,...,[-14400]], [48.32, -0.01, -0.000207, 2,4,5], 1200],
       ...
     ]
    ]]
  ]]]
```

> ⚠️ Cada bar solo tiene **close + change**, NO open/high/low por minuto.

### Variante 2 — Intraday 5-min con OHLC explicito

```python
args = [[[None, ["GGAL", "NASDAQ"]]], 1, None, None, None, None, None, 1]
```

Output: ~5 KB. Cada bar tiene `[open, close, high, low, ISO_ts, volume]`.

```json
[[[["GGAL","NASDAQ"], "/m/0clbgbw", "USD",
   [[[1, [market_open_ts], [market_close_ts]], null,
     [
       [48.25, 48.25, 48.25, 48.25, "2026-06-04T09:30:00-04:00", 1839],
       [48.43, 48.36, 48.43, 48.28, "2026-06-04T09:35:00-04:00", 1771],
       ...
     ]
    ]]
  ]]]
```

### Variante 3 — Daily ultimo mes

```python
args = [[[None, ["GGAL", "NASDAQ"]]], 3]
```

Output: ~2.5 KB con ~22 dias habiles. Mismo shape que variante 1 pero por dia.

### Variante 4 — Daily ultimos ~6 meses

```python
args = [[[None, ["GGAL", "NASDAQ"]]], 4]
```

Output: ~13 KB con ~130 dias habiles.

> ⚠️ Otros valores del segundo arg (5, 6, etc.) pueden retornar mas o
> menos historico — no testeado exhaustivamente. Para historico real
> largo (>6m) usar otros providers (Yahoo Finance, Alpha Vantage).

---

## 11. gXxkFd — Ratings tecnicos

**Funcion:** Ratings tecnicos del simbolo (analogo a Recommend.* de TradingView).

### Args

```python
args = [["GGAL", "NASDAQ"]]
```

### Output

```json
[null, null,
  [["GGAL","NASDAQ"],
   0, 1, 0, 0,                                 // flags binarios
   0.4459, 0.4325, 0.1216,                     // bull / bear / neutral scores [0-1]
   32.43,                                       // RSI value
   1.5, 0,
   0.7692307692307692                          // volume_score [0-1]
  ]
]
```

> ⚠️ Los nombres de campos (`bull_score`, `bear_score`, etc.) son
> **INFERIDOS** del comportamiento, NO de doc oficial. Para mostrar al
> usuario una etiqueta como STRONG_BUY/BUY/NEUTRAL/SELL, considerar
> usar el rating de TradingView en su lugar (mas confiable).

---

## 12. Pr8h2e — Financials masivos

**Funcion:** Financials COMPLETOS multi-period: income statement + balance sheet + cash flow.

### Args

```python
args = [[[None, ["GGAL", "NASDAQ"]]]]
```

### Output

~22 KB. Array anidado por periodos × lineas financieras.

```json
[[[[
  [2026, 1,    // year, quarter
   [1622881521000,    // revenue
    66488440000,      // operating income
    41.39,            // operating margin %
    4.1,              // ...
    28838217000,      // net income
    -3755720644000,   // ... varios fields
    ...
    "ARS",            // currency (NATIVA — no USD si la empresa no es US)
    [2026, 3, 31]     // period_end_date
   ],
   0, null, 0
  ],
  [1902798868000, ...]  // siguiente periodo
  ...
]]]]
```

> ⚠️ El layout de los campos financieros NO esta completamente
> documentado. Tiene ~40 campos por periodo. Para mostrar al usuario,
> recomendado parsear solo los primeros campos (revenue, op income,
> net income, margins) y dejar el resto raw.
>
> Para financials estructurados con keys, considerar **SEC EDGAR** (skill
> `sec-data`) para empresas US o **Macrotrends** (skill `macrotrends`)
> para historico global.

---

## 13. kA4MVd — News (2 variantes)

**Funcion:** News headlines. **2 variantes con el mismo RPC** segun el primer arg.

### Variante 1 — News globales del mercado (con related symbols)

```python
args = [2, 12, [[None, ["GGAL", "NASDAQ"]]]]
# 2 = tipo "global", 12 = limit
```

Output: ~14 KB con news mundiales. Cada item incluye `relatedSymbols[]`
con quote_arrays de los simbolos mencionados.

### Variante 2 — News especificas del simbolo

```python
args = [5, 12, [[None, ["GGAL", "NASDAQ"]]]]
# 5 = tipo "symbol-specific", 12 = limit
```

Output: ~2 KB con solo news que mencionan al simbolo.

### Shape de cada item de news

```json
[
  "https://...",                          // url
  "Headline title",                       // title
  "Reuters",                              // source
  "https://encrypted-tbn1.gstatic...",    // thumbnail_url
  1780628639,                             // published_unix
  false,                                  // is_premium
  false,                                  // unknown_flag
  "https://encrypted-tbn1.gstatic.com/faviconV2?url=...", // favicon
  [related_quote_arrays],                 // solo en variante 1 (global)
  ["/m/freebase_id", ...],                // related freebase ids
  "news_internal_id",
  null,
  340, 148,                               // thumbnail_width, _height
  1780578842                              // second_timestamp
]
```

---

## 14. RPCs desconocidos

Estos 2 RPCs aparecen en la pagina HTML pero retornan vacio cuando los
invocamos con args `[]`. Probable que necesiten args especificos no
descubiertos.

| RPC ID | Status |
|--------|--------|
| `RiQiSd` | UNKNOWN — devuelve `[]` con args vacios. |
| `X12h2b` | UNKNOWN — idem. |

Si necesitas esta data, capturar request real con DevTools del browser
y replicar los args.

---

## Apendice: como descubrir nuevos RPCs

Para descubrir RPCs nuevos (ej: para una pagina de markets, watchlist,
calendar, etc):

1. Abrir DevTools del browser en la pagina objetivo.
2. Filtrar Network por `batchexecute`.
3. Cada request POST trae el `rpcids=XXX` en query string y el `f.req`
   en el body con la estructura `[[["RPC_ID", "args_serialized", null, "generic"]]]`.
4. Replicar en Python pasando los mismos `f.req` + cookies.
5. Documentar en `assets/rpc_ids.json`.

Otra opcion: inspeccionar el HTML de la pagina y buscar:

```javascript
'ds:N' : {id:'XXXXX', request:[...]}
```

Esos `XXXXX` son los RPC IDs y los `request` son los args.
