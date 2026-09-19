# Barchart — Referencia Técnica

Documentación técnica de scraping para agente AI. Detalla campo por campo qué se extrae, de dónde, cómo y qué limitaciones tiene cada endpoint.

---

## Ficha técnica

| Concepto | Respuesta |
|----------|-----------|
| **Método** | Scraping HTML estático + regex. Sin headless browser |
| **Dependencias** | Solo `requests` (Python). Sin bs4, lxml, selenium, playwright |
| **Latencia datos** | Delayed 15-20 min (exchange estándar). Futuros: 10 min |
| **Cobertura** | ~30,000+ símbolos US (NYSE, NASDAQ, AMEX, OTC-US) + futuros, forex, ETFs, índices |
| **ADRs globales** | Sí — GGAL, BABA, SUPV, BMA, etc. listados en NYSE/NASDAQ |
| **Auth** | No requiere. Datos públicos sin login |
| **Rate limit** | Sin límite explícito. Recomendado >= 300ms entre requests |
| **User-Agent** | Requerido (incluido en script). El sitio rechaza requests sin UA |

---

## Disponibilidad campo por campo

### Quote + Fundamentals: `GET /stocks/quotes/{TICKER}`

| # | Campo | Descripción | Tipo | Ejemplo AAPL | Origen en HTML |
|---|-------|-------------|------|-------------|----------------|
| 1 | ticker | Input del usuario | string | AAPL | Argumento CLI |
| 2 | symbol | Símbolo en Barchart | string | AAPL | `data-ng-init` JSON → `symbol` |
| 3 | name | Nombre de la empresa | string | Apple Inc | `data-ng-init` JSON → `symbolName` |
| 4 | lastPrice | Último precio operado | string | 310.26 | `data-ng-init` JSON → `lastPrice` |
| 5 | netChange | Cambio neto en dólares | string | -4.94 | `data-ng-init` JSON → `priceChange` |
| 6 | percentChange | Cambio porcentual | string | -1.57% | `data-ng-init` JSON → `percentChange` |
| 7 | bid | Precio bid actual | string | 313.88 | `data-ng-init` JSON → `bidPrice` |
| 8 | ask | Precio ask actual | string | 313.97 | `data-ng-init` JSON → `askPrice` |
| 9 | exchange | Exchange de cotización | string | NASDAQ | `data-ng-init` JSON → `exchange` |
| 10 | tradeTime | Fecha/hora última operación | string | 06/03/26 | `data-ng-init` JSON → `tradeTime` |
| 11 | marketCap | Market cap en $K | string | 4,629,454,720 | span left/right → "Market Capitalization, $K" |
| 12 | sharesOutstanding | Shares en circulación (en K) | string | 14,687,355 | span left/right → "Shares Outstanding, K" |
| 13 | annualSales | Ventas anuales | string | 416,161 M | span left/right → "Annual Sales, $" |
| 14 | annualIncome | Ingreso neto anual | string | 112,010 M | span left/right → "Annual Income, $" |
| 15 | ebit | EBIT | string | 147,366 M | span left/right → "EBIT $" |
| 16 | ebitda | EBITDA | string | 159,064 M | span left/right → "EBITDA $" |
| 17 | beta | Beta 60 meses | string | 1.09 | span left/right → "60-Month Beta" |
| 18 | priceSales | Price/Sales ratio | string | 10.81 | span left/right → "Price/Sales" |
| 19 | priceCashFlow | Price/Cash Flow ratio | string | 36.59 | span left/right → "Price/Cash Flow" |
| 20 | priceBook | Price/Book ratio | string | 42.25 | span left/right → "Price/Book" |
| 21 | peRatio | Price/Earnings ttm | string | 37.04 | span left/right → "Price/Earnings ttm" |
| 22 | eps | Earnings Per Share ttm | string | 8.27 | span left/right → "Earnings Per Share ttm" |
| 23 | mostRecentEarnings | Último earnings reportado | string | $2.01 on 04/30/26 | span left/right → "Most Recent Earnings" |
| 24 | nextEarningsDate | Próximo earnings date | string | 07/30/26 | span left/right → "Next Earnings Date" |
| 25 | dividend | Dividendo anual + yield fwd | string | 1.08 (0.35%) | span left/right → "Annual Dividend & Yield (Fwd)" |
| 26 | mostRecentDividend | Último dividendo pagado | string | 0.270 on 05/11/26 | span left/right → "Most Recent Dividend" |
| 27 | sector | Sector de la empresa | string | Technology | span left/right → "Sector" |

**JSON `data-ng-init`** — atributo HTML que contiene JSON con quote data:
```html
<div data-ng-controller="symbolHeaderCtrl" 
     data-ng-init='init({"symbol":"AAPL","symbolName":"Apple Inc","lastPrice":"310.26",...})'>
```

**Spans left/right** — estructura HTML de los fundamentals:
```html
<li>
  <span class="left">Market Capitalization, $K</span>
  <span class="right">4,629,454,720</span>
</li>
```

---

### Insider Summary: `GET /stocks/quotes/{TICKER}/insider-trades`

| # | Campo | Descripción | Tipo | Ejemplo AAPL | Origen |
|---|-------|-------------|------|-------------|--------|
| 28 | summaryLast3M.buys | Transacciones de compra (3 meses) | int | 0 | Texto visible "Last 3 Months: X Buys" |
| 29 | summaryLast3M.buyShares | Acciones compradas (3 meses) | int | 0 | Texto visible "Y Shares" |
| 30 | summaryLast3M.sells | Transacciones de venta (3 meses) | int | 6 | Texto visible "Z Sells" |
| 31 | summaryLast3M.sellShares | Acciones vendidas (3 meses) | int | 397759 | Texto visible "W Shares" |

**Extracción:** El texto visible en la página es:
```
Last 3 Months: 0 Buys, 0 Shares; 6 Sells, 397,759 Shares
```

Se usa regex sobre el HTML con tags removidos (texto plano).

**Nota:** Solo el summary de 3 meses está disponible. Las transacciones detalladas (fecha, insider, precio) son render AngularJS.

---

### Analyst Ratings: `GET /stocks/quotes/{TICKER}/analyst-ratings`

| # | Campo | Descripción | Tipo | Ejemplo AAPL | Origen |
|---|-------|-------------|------|-------------|--------|
| 32 | current.rating | Rating actual | string | Moderate Buy | Texto plano post "Current" |
| 33 | current.value | Valor numérico (1-5) | float | 4.12 | Texto plano post rating |
| 34 | current.analysts | Cantidad de analistas | int | 42 | Texto plano "Based on N analysts" |
| 35 | 1_mth_ago.rating | Rating 1 mes atrás | string | Moderate Buy | Ídem |
| 36 | 1_mth_ago.value | Valor 1 mes atrás | float | 4.12 | Ídem |
| 37 | 1_mth_ago.analysts | Analistas 1 mes atrás | int | 42 | Ídem |
| 38 | 2_mths_ago.rating | Rating 2 meses atrás | string | Moderate Buy | Ídem |
| 39 | 2_mths_ago.value | Valor 2 meses atrás | float | 4.07 | Ídem |
| 40 | 2_mths_ago.analysts | Analistas 2 meses atrás | int | 42 | Ídem |
| 41 | 3_mths_ago.rating | Rating 3 meses atrás | string | Moderate Buy | Ídem |
| 42 | 3_mths_ago.value | Valor 3 meses atrás | float | 4.07 | Ídem |
| 43 | 3_mths_ago.analysts | Analistas 3 meses atrás | int | 42 | Ídem |

**Escala de ratings:**

| Rating | Valor |
|--------|:-----:|
| Strong Buy | 5 |
| Moderate Buy | 4 |
| Hold | 3 |
| Moderate Sell | 2 |
| Strong Sell | 1 |

**Extracción:** Patrón en texto plano:
```
Current\nModerate Buy\n4.12\nBased on\n42\nanalysts
```

**No disponible en HTML estático:**
- Price targets (High/Mean/Low) — render AngularJS
- Ratings breakdown (Strong Buy N, Hold N...) — render AngularJS

---

### Earnings Estimates: `GET /stocks/quotes/{TICKER}/earnings-estimates`

| # | Campo | Descripción | Ejemplo GGAL Current Qtr | Origen |
|---|-------|-------------|-------------------------|--------|
| 44 | Average Earnings Estimate | EPS estimado promedio | $0.82 | Tabla HTML |
| 45 | Number of Estimates | Analistas que estiman | 3 | Tabla HTML |
| 46 | High Estimate | EPS estimado más optimista | $1.02 | Tabla HTML |
| 47 | Low Estimate | EPS estimado más pesimista | $0.69 | Tabla HTML |
| 48 | Prior Year | EPS año anterior mismo período | $0.94 | Tabla HTML |
| 49 | Growth Rate Est. (yoy) | Crecimiento vs año anterior | -12.77% | Tabla HTML |

**Columnas de la tabla (4 períodos):**
1. Current Qtr (MM/YYYY) — trimestre actual
2. Next Qtr (MM/YYYY) — próximo trimestre
3. Fiscal Yr (MM/YYYY) — año fiscal actual
4. Fiscal Yr (MM/YYYY) — año fiscal siguiente

**Extracción:** Se busca la tabla HTML que contiene "Average Earnings Estimate", se extraen las filas `<tr>` con `<td>`, y para cada fila se toma el label (primera celda) y los valores (celdas 2-5).

**Ejemplo tabla real GGAL:**
```
Average Earnings Estimate: $0.82 | $1.11 | $3.69 | $6.42
Number of Estimates: 3 | 2 | 3 | 3
High Estimate: $1.02 | $1.30 | $4.45 | $8.12
Low Estimate: $0.69 | $0.92 | $3.29 | $5.21
Prior Year: $0.94 | $0.08 | N/A | $3.69
Growth Rate Est. (yoy): -12.77% | +1,287.50% | -99.63% | +73.98%
```

**Nota:** El label puede contener texto extra (ej: "Growth Rate Est. (year over year) Growth Rate Est. (yoy)"). Se deja como viene del HTML.

---

### Financial Summary: `GET /stocks/quotes/{TICKER}/financial-summary/{annual|quarterly}`

| # | Campo | Descripción | Ejemplo GGAL (annual 2025) | Origen |
|---|-------|-------------|---------------------------|--------|
| 50 | incomeStatement.periods | Períodos (5 años/trimestres) | ["12-2025","12-2024","12-2023","12-2022","12-2021"] | JSON `data-content` |
| 51 | incomeStatement.series.Sales | Ventas por período | [10559375000, 11641250000, ...] | JSON `data-content` |
| 52 | incomeStatement.series.Net Income | Ingreso neto por período | [170020000, 1790999999, ...] | JSON `data-content` |
| 53 | balanceSheet.periods | Períodos (5 años/trimestres) | ["12-2025","12-2024",...] | JSON `data-content` |
| 54 | balanceSheet.series.Assets | Total activos por período | [36535558594, 35769531250, ...] | JSON `data-content` |
| 55 | balanceSheet.series.Liabilities | Total pasivos por período | [30329687500, 29101367188, ...] | JSON `data-content` |
| 56 | cashFlow.periods | Períodos (5 años/trimestres) | ["12-2025","12-2024",...] | JSON `data-content` |
| 57 | cashFlow.series.Cash | Operating cash flow por período | [-1284339965, 3853060059, ...] | JSON `data-content` |
| 58 | cashFlow.series.Net Cash Flow | Net cash flow por período | [423520000, 320470000, ...] | JSON `data-content` |

**Extracción:** El JSON está embebido en atributos HTML `data-content` con HTML entities:
```html
<div data-content="{&quot;series&quot;:[...],&quot;period&quot;:[...],...}">
```

Se decodifican `&quot;` → `"` y se parsea como JSON. La clasificación en incomeStatement / balanceSheet / cashFlow se hace por los nombres de las series.

**Valores formateados en el output:**
- ≥ 1e9 → $XB (billones)
- ≥ 1e6 → $XM (millones)
- ≥ 1e3 → $XK (miles)
- < 1e3 → $X (unidades)

**Períodos:**
- Annual: `MM-YYYY` (ej: "12-2025" = año fiscal terminado Dic 2025)
- Quarterly: `MM-YYYY` (ej: "03-2026" = trimestre terminado Mar 2026)

**Ejemplo real GGAL annual:**
```
incomeStatement: Sales = $10.56B | $11.64B | $24.99B | $9.99B | $5.11B
incomeStatement: Net Income = $170.02M | $1.79B | $1.28B | $374.52M | $326.49M
balanceSheet: Assets = $36.54B | $35.77B | $38.82B | $25.96B | $17.62B
balanceSheet: Liabilities = $30.33B | $29.10B | $31.16B | $21.27B | $14.42B
cashFlow: Cash (Operating) = $-1.28B | $3.85B | $6.34B | $4.47B | $2.97B
cashFlow: Net Cash Flow = $423.52M | $320.47M | $-3.28B | $588.02M | $736.72M
```

**Nota:** Los growth rates (Sales Growth %, Net Income Growth %) no están en el JSON — los calcula AngularJS.

---

### Income Statement Detail: `GET /stocks/quotes/{TICKER}/income-statement/{quarterly|annual}`

| # | Campo | Descripción | Ejemplo GGAL 09-2025 | Origen |
|---|-------|-------------|---------------------|--------|
| 59 | period | 'quarterly' o 'annual' | quarterly | Argumento CLI |
| 60 | periods | Lista de períodos | ["09-2025","03-2025","12-2024","09-2024","06-2024"] | Header de tabla HTML |
| 61 | rows[].label | Nombre de la línea | Interest Income | Primera celda del `<tr>` |
| 62 | rows[].values | Valores por período | ["N/A","1,590,672","7,624,088","1,444,576","N/A"] | Celdas 2-N del `<tr>` |

**Filas disponibles (GGAL ejemplo real, ~17):**
- Interest Income, Interest Expense, Interest Income (Net of Interest Expense)
- Non-Interest Income, Sales, Credit Losses Provision
- Non Interest Expenses, Pre-tax Income, Income Tax, Other Income
- Net Income, EPS Basic Continuous Ops, EPS Basic Total Ops
- EPS Diluted Continuous Ops, EPS Diluted Total Ops
- EPS Diluted Before Non-Recurring Items, EBITDA(a)

**Extracción:** Se busca el primer `<table>` en el HTML y se parsean todas las filas `<tr>` con `<td>`. La primera fila contiene los períodos (headers). Las filas subsiguientes contienen label + values.

**Decodificación aplicada:**
- `&#039;` → `'` (apóstrofe)
- `&amp;` → `&`
- `&nbsp;` → espacio

**Formato de valores:**
- Numéricos con separador de miles: `1,590,672`
- `$` prefijo en Net Income y EBITDA: `$-70,168`
- `N/A` para datos no disponibles
- Valores negativos con signo `-`: `-139,097`

**Nota:** Las filas disponibles varían según el tipo de empresa (bancos vs tech vs industriales). Barchart muestra las líneas relevantes para cada sector.

---

### Balance Sheet Detail: `GET /stocks/quotes/{TICKER}/balance-sheet/{quarterly|annual}`

| # | Campo | Descripción | Ejemplo GGAL 09-2025 | Origen |
|---|-------|-------------|---------------------|--------|
| 63 | period | 'quarterly' o 'annual' | quarterly | Argumento CLI |
| 64 | periods | Lista de períodos | ["09-2025","03-2025","12-2024","09-2024","06-2024"] | Header de tabla HTML |
| 65 | rows[].label | Nombre de la línea | Cash & Cash Equivalents | Primera celda del `<tr>` |
| 66 | rows[].values | Valores por período | ["6,955,327","5,545,430","7,419,325","7,422,673","2,853,684"] | Celdas 2-N del `<tr>` |

**Filas disponibles (GGAL ejemplo real, ~23):**
- Assets: Cash & Cash Equivalents, Federal Funds Sold, Securities And Investments, Loans Gross, Allowance For Loan Losses, PPE Net, Intangibles, Other assets, Total Assets
- Liabilities: Total deposits, Federal Funds Purchased, Long Term Debt, Other liabilities, Total Liabilities
- Shareholders' Equity: Shares Outstanding (annual), Common Shares, Additional Paid Capital, Retained earnings, Other shareholders' equity, TOTAL, Total Liabilities And Equity

**Nota:** Estructura muy similar para todos los tickers. Las filas de "Assets:", "Liabilities:" y "Shareholders' Equity:" son separadores visuales que se mantienen como labels en el output.

---

### Cash Flow Detail: `GET /stocks/quotes/{TICKER}/cash-flow/{quarterly|annual}`

| # | Campo | Descripción | Ejemplo GGAL 09-2025 | Origen |
|---|-------|-------------|---------------------|--------|
| 67 | period | 'quarterly' o 'annual' | quarterly | Argumento CLI |
| 68 | periods | Lista de períodos | ["09-2025","03-2025","12-2024","09-2024","06-2024"] | Header de tabla HTML |
| 69 | rows[].label | Nombre de la línea | Operating Cash Flow | Primera celda del `<tr>` |
| 70 | rows[].values | Valores por período | ["$N/A","$-966,190","$3,853,060","$5,324,640","$N/A"] | Celdas 2-N del `<tr>` |

**Filas disponibles (GGAL ejemplo real, ~27):**
- Cash Flows From Operating Activities: Net Income, Depreciation Amortization, Other Working Capital, Loans, Other Operating Activity, Operating Cash Flow
- Cash Flows From Investing Activities: PPE Investments, Net Acquisitions, Other Investing Activity, Investing Cash Flow
- Cash Flows From Financing Activities: Change In Short Term Borrowing (annual), Debt Issued, Debt Repayment, Common Stock Issued, Dividend Paid, Other Financing Activity, Financing Cash Flow
- Exchange Rate Effect, Beginning Cash Position, End Cash Position, Net Cash Flow
- Free Cash Flow: Operating Cash Flow, Capital Expenditure, Free Cash Flow

**Nota:** Algunas filas como "Change In Short Term Borrowing" solo aparecen en la versión annual. Las filas de separación ("Cash Flows From Operating Activities:", etc.) se mantienen como labels en el output.

---

### Company Profile: `GET /stocks/quotes/{TICKER}/profile`

**Campos extraídos:**

#### Company Info (sección principal)

| # | Campo | Descripción | Ejemplo GGAL |
|---|-------|-------------|-------------|
| 70 | profile.company.name | Nombre de la empresa | Grupo Fin Galicia ADR |
| 71 | profile.company.address | Dirección completa | TTE. GRAL. JUAN D. PERON 430 25TH FLOOR BUENOS AIRES C1 CP1038AAJ ARG |
| 72 | profile.company.website | Sitio web | http://www.gfgsa.com |
| 73 | profile.company.employees | Número de empleados | 10,079 |
| 74 | profile.company.phone | Teléfono | 54-11-4343-7528 |
| 75 | profile.company.fax | Fax | 114-331-9183 |
| 76 | profile.company.sector | Sector | Finance |
| 77 | profile.company.industries | Lista de industrias/clasificaciones | ["SIC-6029 Commercial Banks, NEC", "Banks - Foreign", "Indices Nasdaq Composite"] |
| 78 | profile.company.description | Descripción de la empresa | Grupo Financiero Galicia SA... |

#### Overview Table

| # | Campo | Descripción | Ejemplo GGAL |
|---|-------|-------------|-------------|
| 79 | overview.Market Capitalization, $K | Market cap en $K | 8,084,256 |
| 80 | overview.Enterprise Value, $K | Enterprise value en $K | 2,012,866 |
| 81 | overview.Shares Outstanding, K | Shares en miles | 160,625 |
| 82 | overview.Float, K | Float en miles | 160,625 |
| 83 | overview.% Float | % del float | 100.00% |
| 84 | overview.Short Interest, K | Short interest en miles | 6,552 |
| 85 | overview.Short Float | % short del float | 4.08% |
| 86 | overview.Days to Cover | Días para cubrir | 6.72 |
| 87 | overview.Short Volume Ratio | Ratio de short volume | 0.53 |
| 88 | overview.% of Institutional Shareholders | % institucional | 0.00% |

#### Financials Table

| # | Campo | Descripción | Ejemplo GGAL |
|---|-------|-------------|-------------|
| 89 | financials.Annual Sales, $ | Ventas anuales (último fiscal year) | 10,559 M |
| 90 | financials.Annual Net Income, $ | Net income anual | 170,020 K |
| 91 | financials.Last Quarter Sales, $ | Ventas último trimestre | 672,000 K |
| 92 | financials.Last Quarter Net Income, $ | Net income último trimestre | 46,540 K |
| 93 | financials.EBIT, $ | EBIT | -1,178 M |
| 94 | financials.EBITDA, $ | EBITDA | -934,100 K |

#### Growth Table

| # | Campo | Descripción | Ejemplo GGAL |
|---|-------|-------------|-------------|
| 95 | growth.1-Year Return | Retorno 1 año | -14.61% |
| 96 | growth.3-Year Return | Retorno 3 años | 226.33% |
| 97 | growth.5-Year Return | Retorno 5 años | 387.69% |
| 98 | growth.5-Year Revenue Growth | CAGR revenue 5 años | 141.77% |
| 99 | growth.5-Year Earnings Growth | CAGR earnings 5 años | -100.00% |
| 100 | growth.5-Year Dividend Growth | CAGR dividendo 5 años | 2,725.00% |

#### Per-Share Info Table

| # | Campo | Descripción | Ejemplo GGAL |
|---|-------|-------------|-------------|
| 101 | perShareInfo.Most Recent Earnings | Último EPS reportado + fecha | 0.29 on 05/26/26 |
| 102 | perShareInfo.Next Earnings Date | Próxima fecha de earnings | 08/25/26 |
| 103 | perShareInfo.Earnings Per Share ttm | EPS ttm | 2.27 |
| 104 | perShareInfo.EPS Growth vs. Prev Year | Crecimiento EPS vs año anterior | -69.79% |
| 105 | perShareInfo.Annual Dividend & Yield (Paid) | Dividendo anual pagado + yield | 2.16 (4.28%) |
| 106 | perShareInfo.Annual Dividend & Yield (Fwd) | Dividendo anual forward + yield | 4.86 (9.50%) |
| 107 | perShareInfo.Most Recent Dividend | Último dividendo + fecha | 0.405 on 05/11/26 |
| 108 | perShareInfo.Next Ex-Dividends Date | Próxima fecha ex-dividendo | 05/11/26 |
| 109 | perShareInfo.Dividend Payable Date | Fecha de pago del dividendo | 05/29/26 |
| 110 | perShareInfo.Dividend Payout Ratio | Payout ratio en % | 51.43% |

#### Ratios Table

| # | Campo | Descripción | Ejemplo GGAL |
|---|-------|-------------|-------------|
| 111 | ratios.Price/Earnings ttm | P/E ttm | 0.00 |
| 112 | ratios.Price/Earnings forward | P/E forward | 13.85 |
| 113 | ratios.Price/Earnings to Growth | PEG ratio | 0.36 |
| 114 | ratios.Return-on-Equity % | ROE | 0.00% |
| 115 | ratios.Return-on-Assets % | ROA | 0.00% |
| 116 | ratios.Profit Margin % | Profit margin | 1.61% |
| 117 | ratios.Debt/Equity | Debt/Equity | 0.00 |
| 118 | ratios.Price/Sales | Price/Sales | 0.78 |
| 119 | ratios.Price/Cash Flow | Price/Cash Flow | 19.86 |
| 120 | ratios.Price/Book | Price/Book | 1.37 |
| 121 | ratios.Book Value/Share | Book value por acción | 37.43 |
| 122 | ratios.Interest Coverage | Interest coverage | -1.21 |
| 123 | ratios.60-Month Beta | Beta 60 meses | 1.32 |

#### Dividend History Table

| # | Campo | Descripción | Ejemplo GGAL |
|---|-------|-------------|-------------|
| 124 | dividendHistory[].label | Fecha del dividendo | 05/11/26 |
| 125 | dividendHistory[].value | Monto del dividendo | $0.4050 |

**Nota:** El dividend history puede tener 5-20+ entries dependiendo del ticker.

**Extracción:** Se parsea la sección "Company Info" del HTML usando regex sobre texto plano (address, website, employees, sector, industries, description). Las 6 tablas de key statistics se parsean extrayendo pares `<tr>` → `<td>` label/value.

---

## Lo que NO se puede extraer (AngularJS)

Por cada página de Barchart, estos datos se renderizan client-side y **no están en el HTML estático**:

| Página | Datos no disponibles |
|--------|---------------------|
| `/stocks/quotes/{TICKER}` | Day High/Low, Open, Previous Close, Volume, Avg Volume, 52W High/Low, Weighted Alpha, Relative Strength |
| `/stocks/quotes/{TICKER}/financial-summary` | **Income/balance/cash flow SÍ disponibles** via `--financials`. Growth rates (%) y detalle por línea no |
| `/stocks/quotes/{TICKER}/options` | Options chain (calls/puts con strikes, Greeks) |
| `/stocks/quotes/{TICKER}/technical-analysis` | RSI, Stochastic, ATR, ADX, Moving Averages, Historic Volatility |
| `/stocks/quotes/{TICKER}/analyst-ratings` | Price targets (High/Mean/Low), Ratings breakdown (Strong Buy N, Hold N...) |
| `/stocks/quotes/{TICKER}/insider-trades` | Transacciones detalladas (fecha, insider, precio, cantidad) — solo summary disponible |
| `/stocks/quotes/{TICKER}/earnings-estimates` | Revenue estimates, tabla Reported vs Estimate histórica |
| `/stocks/quotes/{TICKER}/related-etfs` | Tabla de ETFs relacionados (symbol, name, weight, weightInEtf) — todo AngularJS |
| `/stocks/signals/top-bottom/top` | Screener / Top lists completos |

---

## Notas técnicas

### Multi-ticker
El script acepta múltiples tickers separados por coma: `AAPL,MSFT,GGAL`. Cada ticker hace requests separados.

### marketCap y sharesOutstanding
- `marketCap` está en **$K** (miles de dólares). AAPL = 4,629,454,720 → $4.6 trillones
- `sharesOutstanding` está en **K** (miles de acciones)
- Para convertir: valor_real = marketCap * 1000

### Sufijos numéricos
- `M` = millions (millones)
- `K` = thousands (miles)
- `B` = billions (miles de millones) — aunque en Barchart los valores grandes aparecen sin sufijo

### Dividend
El campo `dividend` contiene tanto el monto anual como el yield: `1.08 (0.35%)`. Hay que parsear si se necesita cada valor por separado.

### Datos negativos
EBIT/EBITDA pueden ser negativos (GGAL muestra EBITDA = -934 M). El script los captura como string.

### Rate limiting
No hay límite explícito pero por cortesía y estabilidad el script tiene un delay de 300ms entre requests.

### Encoding
El HTML puede contener `&amp;` en lugar de `&` (ej: "Annual Dividend & Yield"). Los strings se dejan como vienen.

---

## Changelog de descubrimiento

| Fecha | Descubrimiento |
|-------|----------------|
| 2026-06-04 | Scraping vía `data-ng-init` JSON para quotes |
| 2026-06-04 | Spans left/right para fundamentals |
| 2026-06-04 | Insider summary (3 meses) desde texto plano |
| 2026-06-04 | Analyst ratings: rating actual + histórico desde texto plano |
| 2026-06-04 | Earnings estimates: tabla HTML con 4 períodos de EPS estimado |
| 2026-06-04 | Financial summary (annual + quarterly): Income Statement, Balance Sheet, Cash Flow desde JSON en `data-content` |
| 2026-06-04 | Income Statement Detail (quarterly + annual): 17+ filas desde tabla HTML |
| 2026-06-04 | Balance Sheet Detail (quarterly + annual): 23+ filas desde tabla HTML |
| 2026-06-04 | Cash Flow Detail (quarterly + annual): 27+ filas desde tabla HTML |
| 2026-06-04 | Internal API investigation: `/proxies/core-api/v1/quotes/get`, `API_URL=/api/v1`, auth con XSRF-TOKEN |
| 2026-06-04 | Company Profile desde `/profile`: company info (address, employees, sector, description) + 6 tabs key statistics + dividend history |
