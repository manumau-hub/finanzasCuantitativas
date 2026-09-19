# CompaniesMarketCap — Referencia Completa

## Índice
1. [Resumen de Endpoints](#1-resumen-de-endpoints)
2. [Rankings (CSV)](#2-rankings-csv)
3. [Stock — Marketcap Histórico](#3-stock--marketcap-histórico)
4. [ETF — Holdings](#4-etf--holdings)
5. [Resolución Ticker → Slug](#5-resolución-ticker--slug)
6. [Consideraciones Técnicas](#6-consideraciones-técnicas)
7. [Catálogo Completo de Rankings](#7-catálogo-completo-de-rankings)

---

## 1. Resumen de Endpoints

| Modo | Flag | Endpoint | Método | Output |
|------|------|----------|--------|--------|
| Ranking | `--rankings --metric X` | `/?download=csv` | CSV | 10,852 filas |
| Stock history | `--stock TICKER` | `/{slug}/marketcap/` | HTML table | ~28-31 años |
| ETF holdings | `--etf TICKER --holdings` | `/{slug}/holdings/` | HTML table | ~505 filas |

---

## 2. Rankings (CSV)

### Mecanismo

Todas las páginas de ranking de CompaniesMarketCap soportan `?download=csv` que devuelve un archivo CSV con headers consistentes. **No requiere API key**, no requiere parsear HTML.

### Headers comunes

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `Rank` | int | Posición en el ranking |
| `Name` | string | Nombre de la compañía |
| `Symbol` | string | Ticker (ej: NVDA, 1398.HK, 2222.SR) |
| `{metric_column}` | int/float | Valor de la métrica específica |
| `price (USD)` | float | Precio de la acción en USD |
| `country` | string | País de domicilio |

### Métricas disponibles (`--metric`)

| Flag | CSV Column | Descripción | Unidad |
|------|-----------|-------------|--------|
| `marketcap` (default) | `marketcap` | Market Capitalization | USD |
| `earnings` | `earnings_ttm` | Earnings (Trailing 12 Months) | USD |
| `revenue` | `revenue_ttm` | Revenue (TTM) | USD |
| `employees` | `employees` | Number of Employees | count |
| `pe_ratio` | `pe_ratio` | Price/Earnings Ratio | ratio |
| `operating_margin` | `operating_margin_ttm` | Operating Margin (TTM) | % |
| `total_assets` | `total_assets` | Total Assets | USD |
| `net_assets` | `net_assets` | Net Assets | USD |
| `liabilities` | `total_liabilities` | Total Liabilities | USD |
| `debt` | `total_debt` | Total Debt | USD |
| `cash` | `cash_on_hand` | Cash on Hand | USD |
| `pb_ratio` | `pb_ratio` | Price/Book Ratio | ratio |
| `etfs` | `marketcap` | ETF Market Cap | USD |

### Cantidad de datos

| Métrica | Filas | Coverage |
|---------|-------|----------|
| Todos los rankings stock | ~10,852 | Empresas de +50 países |
| ETFs | ~3,638 | ETFs globales |

### Ejemplo output

```json
{
  "metric": "earnings",
  "description": "Earnings (TTM)",
  "unit": "USD",
  "total_rows": 10852,
  "data": [
    {
      "rank": 1,
      "name": "Alphabet (Google)",
      "symbol": "GOOG",
      "price_usd": 358.39,
      "country": "United States",
      "value": 195684000000
    }
  ]
}
```

---

## 3. Stock — Marketcap Histórico

**Endpoint:** `/{slug}/marketcap/`

### Datos extraídos

#### Marketcap History Table

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| year | Año fiscal | 2026 |
| marketcap | Market cap formateado | "$5.396 T" |
| change | Cambio porcentual anual | "16.34%" |

Cobertura temporal:
- **NVDA:** 28 años (1999–2026)
- **AAPL:** 31 años (1996–2026)
- **GGAL:** 12 años (2014–2026)

#### Similar Companies

Compañías comparables con: `name`, `marketcap`, `diff`, `country`.

### Ejemplo output

```json
{
  "ticker": "NVDA",
  "name": "NVIDIA",
  "slug": "nvidia",
  "marketcap_history": [
    { "year": "2026", "marketcap": "$5.396 T", "change": "16.34%" },
    { "year": "2025", "marketcap": "$4.638 T", "change": "41.05%" }
  ],
  "similar_companies": [...]
}
```

---

## 4. ETF — Holdings

**Endpoint:** `/{slug}/holdings/`

### Datos extraídos

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| weight_pct | Peso en el ETF | "8.36%" |
| name | Nombre de la compañía | "NVIDIA CORP" |
| ticker | Ticker del holding | "NVDA" |
| shares_held | Cantidad de acciones | 292323382 |

### Cobertura

| ETF | Holdings |
|-----|----------|
| SPY | ~505 |
| IVV | ~505 |
| Otros | Varía según el ETF |

### Ejemplo output

```json
{
  "etf_holdings": {
    "ticker": "SPY",
    "name": "SPDR S&P 500 ETF",
    "slug": "spdr-sp-500-etf",
    "holdings": [
      {
        "weight_pct": "8.36%",
        "name": "NVIDIA CORP",
        "ticker": "NVDA",
        "shares_held": 292323382
      }
    ]
  }
}
```

---

## 5. Resolución Ticker → Slug

El scraper resuelve automáticamente el slug a partir del nombre en el CSV.

### Algoritmo de slug

```
name.lower()
  .replace(" & ", "-").replace(" &", "-").replace("& ", "-")
  .replace("&", "")         # "S&P" → "sp"
  .replace(",", "").replace("(", "").replace(")", "")
  .replace("'", "").replace(".", "")
  .replace(" ", "-")
  -> slug
```

### Ejemplos de resolución

| Ticker | Nombre en CSV | Slug generado | Status |
|--------|---------------|---------------|--------|
| NVDA | NVIDIA | `nvidia` | ✅ 200 |
| AAPL | Apple | `apple` | ✅ 200 |
| GOOG | Alphabet (Google) | `alphabet-google` | ✅ 200 |
| GGAL | Galicia Financial Group | `galicia-financial-group` | ✅ 200 |
| BRK-B | Berkshire Hathaway | `berkshire-hathaway` | ✅ 200 |
| SPY | SPDR S&P 500 ETF | `spdr-sp-500-etf` | ✅ 200 |
| VOO | Vanguard S&P 500 ETF | `vanguard-s-p-500-etf` | ✅ 200 |

### Orden de resolución

1. Primero busca el ticker en el **marketcap CSV** (stocks, ~10,852 empresas)
2. Si no lo encuentra, busca en el **ETF CSV** (ETFs, ~3,638)
3. Si no está en ninguno, usa el ticker en minúsculas como slug (puede fallar)

---

## 6. Consideraciones Técnicas

### Rate Limiting

| Delay | Resultado |
|-------|-----------|
| <1s | ❌ Riesgo de bloqueo |
| 2s | ✅ Recomendado |
| 3s+ | ✅ Ideal para múltiples requests |

### Cache de nombres

El scraper cachea los nombres de los CSVs en `_name_cache` para no tener que descargarlos repetidamente. Cada ejecución independiente descarga los CSVs la primera vez que se necesita.

### Formato de valores numéricos

- Los CSVs devuelven números en formato raw: `5396923154432`, `222.82`
- El scraper parsea a `int` o `float` automáticamente
- Strings vacíos se devuelven como `null`
- Holdings grandes usan notación científica en el CSV: `2.92323382E8` se parsean como float

### Coverage geográfico

Los rankings incluyen empresas de **50+ países**, con tickers en formato local:
- `1398.HK` → Hong Kong
- `2222.SR` → Saudi Arabia
- `601288.SS` → Shanghai
- `7718.T` → Tokyo
- `ARG.AX` → Australia

---

## 7. Catálogo Completo de Rankings

| # | Métrica | Path | CSV Column | Descripción |
|---|---------|------|------------|-------------|
| 1 | `marketcap` | `/` | `marketcap` | Market Capitalization global |
| 2 | `earnings` | `/most-profitable-companies/` | `earnings_ttm` | Earnings (TTM) |
| 3 | `revenue` | `/largest-companies-by-revenue/` | `revenue_ttm` | Revenue (TTM) |
| 4 | `employees` | `/largest-companies-by-number-of-employees/` | `employees` | Employee count |
| 5 | `pe_ratio` | `/top-companies-by-pe-ratio/` | `pe_ratio` | P/E ratio |
| 6 | `operating_margin` | `/top-companies-by-operating-margin/` | `operating_margin_ttm` | Operating margin (%) |
| 7 | `total_assets` | `/top-companies-by-total-assets/` | `total_assets` | Total assets |
| 8 | `net_assets` | `/top-companies-by-net-assets/` | `net_assets` | Net assets |
| 9 | `liabilities` | `/companies-with-the-highest-liabilities/` | `total_liabilities` | Total liabilities |
| 10 | `debt` | `/companies-with-the-highest-debt/` | `total_debt` | Total debt |
| 11 | `cash` | `/companies-with-the-highest-cash-on-hand/` | `cash_on_hand` | Cash on hand |
| 12 | `pb_ratio` | `/companies-with-lowest-pb-ratio/` | `pb_ratio` | Price/Book ratio |
| 13 | `etfs` | `/etfs/largest-etfs-by-marketcap/` | `marketcap` | ETF market caps |
