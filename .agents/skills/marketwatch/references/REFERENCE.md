# MarketWatch — Referencia Completa de Endpoints y Datos

## Índice

1. [Quote Page](#1-quote-page)
2. [Company Profile](#2-company-profile)
3. [Income Statement](#3-income-statement)
4. [Balance Sheet](#4-balance-sheet)
5. [Cash Flow Statement](#5-cash-flow-statement)
6. [SEC Filings](#6-sec-filings)
7. [Analyst Estimates](#7-analyst-estimates)
8. [Options Chain](#8-options-chain)
9. [Historical Data](#9-historical-data)
10. [Consideraciones Técnicas](#10-consideraciones-técnicas)

---

## 1. Quote Page

**Endpoint:** `/investing/stock/{TICKER}`

### Campos disponibles

| Dato | Origen | Ejemplo (AAPL) |
|------|--------|----------------|
| Precio actual | `<bg-quote class="value">` | 315.00 |
| Nombre compañía | `<h1 class="company__name">` | Apple Inc. |
| Close | Tabla `table--primary` | $315.20 |
| Chg | Tabla `table--primary` | 8.89 |
| Chg % | Tabla `table--primary` | 2.90% |
| 5 Day | Tabla `c2` | 1.40% |
| 1 Month | Tabla `c2` | 9.63% |
| 3 Month | Tabla `c2` | 20.07% |
| YTD | Tabla `c2` | 15.94% |
| 1 Year | Tabla `c2` | 55.41% |

### Estructura de tablas (class `table--primary`)

| Tabla | Contenido |
|-------|-----------|
| `table--primary.align--right` | Índices globales (FTSE, DAX, CAC...) |
| `table--primary.align--right` (con thead) | **Close / Chg / Chg %** |
| `table--primary.no-heading.c2` | **Performance** (5 Day, 1 Month, 3 Month, YTD, 1 Year) |
| `table--primary.align--right` (Name, Chg %, Market Cap) | Comparables del sector |

### Output JSON (`--quote`)

```json
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "price": "315.00",
  "close": "$315.20",
  "change": "8.89",
  "change_pct": "2.90%",
  "5 Day": "1.40%",
  "1 Month": "9.63%",
  "3 Month": "20.07%",
  "YTD": "15.94%",
  "1 Year": "55.41%"
}
```

---

## 2. Company Profile

**Endpoint:** `/investing/stock/{TICKER}/company-profile`

### Campos disponibles (hasta 29 ratios)

Agrupados en 5 tablas `value-pairs`:

#### Valuación (Table 0)

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| P/E Current | P/E actual | 41.80 |
| P/E Ratio (w/ extraordinary items) | P/E con items extraordinarios | 37.49 |
| P/E Ratio (w/o extraordinary items) | P/E sin items extraordinarios | 34.22 |
| Price to Sales Ratio | Precio/Ventas | 9.21 |
| Price to Book Ratio | Precio/Valor contable | 51.18 |
| Price to Cash Flow Ratio | Precio/Flujo de caja | 34.38 |
| Enterprise Value to EBITDA | EV/EBITDA | 32.06 |
| Enterprise Value to Sales | EV/Ventas | 10.28 |
| Total Debt to Enterprise Value | Deuda total / EV | 0.03 |

#### Eficiencia (Table 1)

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Revenue/Employee | Ingresos por empleado | $2.507M |
| Income Per Employeee | Ganancia por empleado | $674,759 |
| Receivables Turnover | Rotación de cuentas a cobrar | 5.98 |
| Total Asset Turnover | Rotación de activos totales | 1.15 |

#### Liquidez (Table 2)

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Current Ratio | Liquidez corriente | 0.89 |
| Quick Ratio | Prueba ácida | 0.86 |
| Cash Ratio | Liquidez inmediata | 0.33 |

#### Rentabilidad (Table 3)

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Gross Margin | Margen bruto | 46.91% |
| Operating Margin | Margen operativo | 31.97% |
| Pretax Margin | Margen antes de impuestos | 31.89% |
| Net Margin | Margen neto | 26.92% |
| Return on Assets | ROA | 30.93% |
| Return on Equity | ROE | 171.42% |
| Return on Total Capital | ROC | 73.48% |
| Return on Invested Capital | ROIC | 70.63% |

#### Endeudamiento (Table 4)

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Total Debt to Total Equity | D/E total | 152.41 |
| Total Debt to Total Capital | Deuda/Capital total | 60.38 |
| Total Debt to Total Assets | Deuda/Activos | 31.28 |
| Long-Term Debt to Equity | D/E LP | 121.97 |
| Long-Term Debt to Total Capital | Deuda LP/Capital | 48.32 |

### Output JSON (`--profile`)

```json
{
  "P/E Current": "41.80",
  "P/E Ratio (w/ extra...": "37.49",
  "Revenue/Employee": "$2.507M",
  "Gross Margin": "46.91%",
  "ROE": "171.42%",
  "Total Debt to Total Equity": "152.41",
  ...
}
```

---

## 3. Income Statement

**Endpoints:**
- Anual: `/investing/stock/{TICKER}/financials/income`
- Trimestral: `/investing/stock/{TICKER}/financials/income/quarter`

### Estructura de tabla

Clase CSS: `table--overflow`

| Columna | Header | Descripción |
|---------|--------|-------------|
| 0 | ItemItem | Nombre del campo (duplicado, se limpia automáticamente) |
| 1..5 | Año o Fecha | Valores por período (5 columnas) |
| 6 | 5-year trend | Tendencia (vacío en el HTML) |

### Campos completos (57 items)

| # | Nombre | Descripción | Unidad |
|---|--------|-------------|--------|
| 0 | Sales/Revenue | Ingresos totales | $ |
| 1 | Sales Growth | Crecimiento de ingresos | % |
| 2 | Cost of Goods Sold (COGS) incl. D&A | Costo de ventas (con D&A) | $ |
| 3 | COGS Growth | Crecimiento del COGS | % |
| 4 | COGS excluding D&A | COGS sin D&A | $ |
| 5 | Depreciation & Amortization Expense | Depreciación y amortización | $ |
| 6 | Depreciation | Depreciación | $ |
| 7 | Amortization of Intangibles | Amortización de intangibles | $ |
| 8 | Gross Income | Ganancia bruta | $ |
| 9 | Gross Income Growth | Crecimiento ganancia bruta | % |
| 10 | Gross Profit Margin | Margen bruto | % |
| 11 | SG&A Expense | Gastos de venta, generales y adm. | $ |
| 12 | SGA Growth | Crecimiento SG&A | % |
| 13 | Research & Development | I+D | $ |
| 14 | Other SG&A | Otros SG&A | $ |
| 15 | Other Operating Expense | Otros gastos operativos | $ |
| 16 | Unusual Expense | Gastos inusuales | $ |
| 17 | EBIT after Unusual Expense | EBIT después de inusuales | $ |
| 18 | Non Operating Income/Expense | Resultado no operativo | $ |
| 19 | Non-Operating Interest Income | Intereses ganados | $ |
| 20 | Equity in Affiliates (Pretax) | Participación en afiliadas | $ |
| 21 | Interest Expense | Intereses pagados | $ |
| 22 | Interest Expense Growth | Crecimiento intereses | % |
| 23 | Gross Interest Expense | Intereses brutos | $ |
| 24 | Interest Capitalized | Intereses capitalizados | $ |
| 25 | Pretax Income | Resultado antes de impuestos | $ |
| 26 | Pretax Income Growth | Crecimiento pretax | % |
| 27 | Pretax Margin | Margen pretax | % |
| 28 | Income Tax | Impuesto a las ganancias | $ |
| 29 | Income Tax - Current Domestic | Impuesto corriente doméstico | $ |
| 30 | Income Tax - Current Foreign | Impuesto corriente extranjero | $ |
| 31 | Income Tax - Deferred Domestic | Impuesto diferido doméstico | $ |
| 32 | Income Tax - Deferred Foreign | Impuesto diferido extranjero | $ |
| 33 | Income Tax Credits | Créditos impositivos | $ |
| 34 | Equity in Affiliates | Participación en afiliadas (post-tax) | $ |
| 35 | Other After Tax Income (Expense) | Otros ingresos/gastos post-tax | $ |
| 36 | Consolidated Net Income | Resultado neto consolidado | $ |
| 37 | Minority Interest Expense | Interés minoritario | $ |
| 38 | Net Income | Resultado neto | $ |
| 39 | Net Income Growth | Crecimiento neto | % |
| 40 | Net Margin Growth | Margen neto | % |
| 41 | Extraordinaries & Discontinued Operations | Extraordinarios | $ |
| 42 | Extra Items & Gain/Loss Sale Of Assets | Items extraordinarios | $ |
| 43 | Cumulative Effect - Accounting Chg | Cambios contables acumulativos | $ |
| 44 | Discontinued Operations | Operaciones discontinuadas | $ |
| 45 | Net Income After Extraordinaries | Neto después de extraordinarios | $ |
| 46 | Preferred Dividends | Dividendos preferidos | $ |
| 47 | Net Income Available to Common | Neto disponible para comunes | $ |
| 48 | EPS (Basic) | EPS básico | $ |
| 49 | EPS (Basic) Growth | Crecimiento EPS básico | % |
| 50 | Basic Shares Outstanding | Acciones básicas en circulación | # |
| 51 | EPS (Diluted) | EPS diluido | $ |
| 52 | EPS (Diluted) Growth | Crecimiento EPS diluido | % |
| 53 | Diluted Shares Outstanding | Acciones diluidas | # |
| 54 | EBITDA | EBITDA | $ |
| 55 | EBITDA Growth | Crecimiento EBITDA | % |
| 56 | EBITDA Margin | Margen EBITDA | % |

### Ejemplo output (anual)

```json
{
  "income_statement": {
    "annual": [
      {
        "headers": ["Item", "2021", "2022", "2023", "2024", "2025"],
        "rows": [
          ["Sales/Revenue", "365.82B", "394.33B", "383.29B", "391.04B", "416.16B"],
          ["Net Income", "94.68B", "99.8B", "97B", "93.74B", "112.01B"],
          ["EPS (Diluted)", "5.61", "6.11", "6.13", "6.08", "7.47"],
          ...
        ]
      }
    ]
  }
}
```

### Ejemplo output (trimestral)

```json
{
  "income_statement": {
    "quarterly": [ ... ]  // mismos campos, headers = fechas trimestrales
  }
}
```

---

## 4. Balance Sheet

**Endpoints:**
- Anual: `/investing/stock/{TICKER}/financials/balance-sheet`
- Trimestral: `/investing/stock/{TICKER}/financials/balance-sheet/quarter`

### Estructura

El balance sheet tiene **2 tablas** `table--overflow`:

| Tabla | Filas | Contenido |
|-------|-------|-----------|
| Table 0 | 36 | **Activos** (Current + Long-Term Assets) |
| Table 1 | 43 | **Pasivos + Patrimonio** (Liabilities + Equity) |

### Campos — Activos (Table 0)

| # | Nombre | Descripción |
|---|--------|-------------|
| 0 | Cash & Short Term Investments | Efectivo e inversiones de corto plazo |
| 1 | Cash & Short Term Investments Growth | Crecimiento |
| 2 | Cash Only | Efectivo puro |
| 3 | Short-Term Investments | Inversiones de corto plazo |
| 4 | Cash & ST Investments / Total Assets | % sobre activos totales |
| 5 | Total Accounts Receivable | Cuentas a cobrar totales |
| 6 | Total Accounts Receivable Growth | Crecimiento |
| 7 | Accounts Receivables, Net | Cuentas a cobrar netas |
| 8 | Accounts Receivables, Gross | Cuentas a cobrar brutas |
| 9 | Bad Debt/Doubtful Accounts | Incobrables |
| 10 | Other Receivable | Otras cuentas a cobrar |
| 11 | Accounts Receivable Turnover | Rotación de cuentas a cobrar |
| 12 | Inventories | Inventarios |
| 13 | Finished Goods | Productos terminados |
| 14 | Work in Progress | Producción en proceso |
| 15 | Raw Materials | Materias primas |
| 16 | Progress Payments & Other | Pagos a cuenta |
| 17 | Other Current Assets | Otros activos corrientes |
| 18 | Miscellaneous Current Assets | Activos corrientes varios |
| 19 | Total Current Assets | **Total activo corriente** |
| 20 | Net Property, Plant & Equipment | PP&E neto |
| 21 | Property, Plant & Equipment - Gross | PP&E bruto |
| 22 | Buildings | Edificios |
| 23 | Land & Improvements | Terrenos |
| 24 | Computer Software and Equipment | Software y equipos |
| 25 | Other Property, Plant & Equipment | Otros PP&E |
| 26 | Accumulated Depreciation | Depreciación acumulada |
| 27 | Total Investments and Advances | Inversiones totales |
| 28 | Other Long-Term Investments | Otras inversiones LP |
| 29 | Long-Term Note Receivables | Documentos a cobrar LP |
| 30 | Intangible Assets | Activos intangibles |
| 31 | Net Goodwill | Goodwill neto |
| 32 | Net Other Intangibles | Otros intangibles netos |
| 33 | Other Assets | Otros activos |
| 34 | Total Assets | **Total activo** |
| 35 | Total Assets Growth | Crecimiento |

### Campos — Pasivos + Patrimonio (Table 1)

| # | Nombre | Descripción |
|---|--------|-------------|
| 0 | ST Debt & Current Portion LT Debt | Deuda CP + porción corriente deuda LP |
| 1 | Short Term Debt | Deuda de corto plazo |
| 2 | Current Portion of Long Term Debt | Porción corriente deuda LP |
| 3 | Accounts Payable | Cuentas a pagar |
| 4 | Accounts Payable Growth | Crecimiento |
| 5 | Income Tax Payable | Impuesto a las ganancias a pagar |
| 6 | Other Current Liabilities | Otros pasivos corrientes |
| 7 | Dividends Payable | Dividendos a pagar |
| 8 | Accrued Payroll | Remuneraciones devengadas |
| 9 | Miscellaneous Current Liabilities | Pasivos corrientes varios |
| 10 | Total Current Liabilities | **Total pasivo corriente** |
| 11 | Long-Term Debt | Deuda de largo plazo |
| 12 | Long-Term Debt Growth | Crecimiento |
| 13 | Long-Term Debt / Total Equity | Deuda LP / Patrimonio |
| 14 | Total Long-Term Debt | Deuda LP total |
| 15 | Total Long-Term Debt Growth | Crecimiento |
| 16 | Long-Term Debt / Total Capital | Deuda LP / Capital total |
| 17 | Deferred Taxes | Impuestos diferidos |
| 18 | Investment Tax Credit | Crédito fiscal por inversión |
| 19 | Other Liabilities | Otros pasivos |
| 20 | Other Long-Term Liabilities | Otros pasivos LP |
| 21 | Total Liabilities | **Total pasivo** |
| 22 | Total Liabilities / Total Assets | Pasivo / Activo |
| 23 | Preferred Stock (Carrying Value) | Acciones preferidas |
| 24 | Redeemable Preferred Stock | Acciones preferidas rescatables |
| 25 | Preferred Stock Convertible | Acciones preferidas convertibles |
| 26 | Non-Convertible Preferred Stock | Acciones preferidas no convertibles |
| 27 | Preferred Stock - Other | Otras preferidas |
| 28 | Common Stock (Par, Paid In) | Acciones comunes |
| 29 | Additional Paid In Capital | Prima de emisión |
| 30 | Common Stock Par/No Par | Valor nominal |
| 31 | Retained Earnings | Ganancias retenidas |
| 32 | Retained Earnings Growth | Crecimiento |
| 33 | Cumulative Translation Adjustment | Ajuste por conversión |
| 34 | Other Appropriated Reserves | Otras reservas |
| 35 | Treasury Stock | Acciones en tesorería |
| 36 | Other Equity Adjustments | Otros ajustes de patrimonio |
| 37 | Total Shareholders' Equity | **Total patrimonio neto** |
| 38 | Shareholders' Equity Growth | Crecimiento |
| 39 | Shareholders' Equity / Total Assets | Patrimonio / Activo |
| 40 | Total Shareholders' Equity + Minority Interest | Patrimonio + minoritarios |
| 41 | Minority Interest | Interés minoritario |
| 42 | Liabilities & Shareholders' Equity | **Pasivo + Patrimonio** |

---

## 5. Cash Flow Statement

**Endpoint:** `/investing/stock/{TICKER}/financials/cash-flow`

**Nota:** Solo disponible **anual**. El endpoint `/quarter` devuelve datos incompletos.

### Estructura

El cash flow tiene **3 tablas** `table--overflow`:

| Tabla | Filas | Contenido |
|-------|-------|-----------|
| Table 0 | 18 | **Operating Activities** |
| Table 1 | 15 | **Investing Activities** |
| Table 2 | 25 | **Financing Activities + Ratios** |

### Campos — Operating Activities (Table 0)

| # | Nombre | Descripción |
|---|--------|-------------|
| 0 | Net Income before Extraordinaries | Neto antes de extraordinarios |
| 1 | Net Income Growth | Crecimiento |
| 2 | Depreciation, Depletion & Amortization | D&A |
| 3 | Depreciation and Depletion | Depreciación |
| 4 | Amortization of Intangible Assets | Amortización |
| 5 | Deferred Taxes & Investment Tax Credit | Impuestos diferidos |
| 6 | Deferred Taxes | Impuestos diferidos |
| 7 | Investment Tax Credit | Crédito fiscal |
| 8 | Other Funds | Otros fondos |
| 9 | Funds from Operations | Fondos de operaciones |
| 10 | Extraordinaries | Extraordinarios |
| 11 | Changes in Working Capital | Cambios en capital de trabajo |
| 12 | Receivables | Variación cuentas a cobrar |
| 13 | Accounts Payable | Variación cuentas a pagar |
| 14 | Other Assets/Liabilities | Otras variaciones |
| 15 | Net Operating Cash Flow | **FCO neto** |
| 16 | Net Operating Cash Flow Growth | Crecimiento |
| 17 | Net Operating Cash Flow / Sales | FCO / Ventas |

### Campos — Investing Activities (Table 1)

| # | Nombre | Descripción |
|---|--------|-------------|
| 0 | Capital Expenditures | Capex (negativo) |
| 1 | Capital Expenditures Growth | Crecimiento |
| 2 | Capital Expenditures / Sales | Capex / Ventas |
| 3 | Net Assets from Acquisitions | Adquisiciones |
| 4 | Sale of Fixed Assets & Businesses | Venta de activos |
| 5 | Purchase/Sale of Investments | Compra/venta de inversiones |
| 6 | Purchase of Investments | Compra de inversiones |
| 7 | Sale/Maturity of Investments | Venta de inversiones |
| 8 | Other Uses | Otros usos |
| 9 | Other Sources | Otras fuentes |
| 10 | Net Investing Cash Flow | **FCI neto** |
| 11 | Net Investing Cash Flow Growth | Crecimiento |
| 12 | Net Investing Cash Flow / Sales | FCI / Ventas |
| 13 | Other Investing Activities | Otras actividades de inversión |
| 14 | Net Investing Cash Flow - Total | FCI total |

### Campos — Financing Activities (Table 2)

| # | Nombre | Descripción |
|---|--------|-------------|
| 0 | Cash Dividends Paid - Total | Dividendos pagados |
| 1 | Common Dividends | Dividendos comunes |
| 2 | Preferred Dividends | Dividendos preferidos |
| 3 | Change in Capital Stock | Cambio en capital |
| 4 | Repurchase of Common & Preferred Stk | Recompra de acciones |
| 5 | Sale of Common & Preferred Stock | Emisión de acciones |
| 6 | Proceeds from Stock Options | Ejercicio de opciones |
| 7 | Other Proceeds from Sale of Stock | Otras emisiones |
| 8 | Issuance/Reduction of Debt, Net | Emisión/pago de deuda neta |
| 9 | Change in Current Debt | Cambio en deuda CP |
| 10 | Change in Long-Term Debt | Cambio en deuda LP |
| 11 | Issuance of Long-Term Debt | Emisión de deuda LP |
| 12 | Reduction in Long-Term Debt | Pago de deuda LP |
| 13 | Other Funds | Otros fondos |
| 14 | Other Financing Activities | Otras actividades de financiación |
| 15 | Net Financing Cash Flow | **FCF neto** |
| 16 | Net Financing Cash Flow Growth | Crecimiento |
| 17 | Net Financing Cash Flow / Sales | FCF / Ventas |
| 18 | Net Change in Cash | Variación neta de efectivo |
| 19 | Net Change in Cash Growth | Crecimiento |
| 20 | Foreign Exchange Rate Adjustments | Ajustes por tipo de cambio |
| 21 | Free Cash Flow | **Free Cash Flow** |
| 22 | Free Cash Flow Growth | Crecimiento FCF |
| 23 | Free Cash Flow Yield | FCF Yield |
| 24 | Free Cash Flow / Sales | FCF / Ventas |

---

## 6. SEC Filings

**Endpoint:** `/investing/stock/{TICKER}/financials/secfilings`

### Estructura de tabla

| Columna | Header | Descripción |
|---------|--------|-------------|
| 0 | Filing Date | Fecha de presentación |
| 1 | Document Date | Fecha del documento |
| 2 | Type | Tipo de filing (10-K, 10-Q, 8-K, etc.) |
| 3 | Category | Categoría descriptiva |
| 4 | Amended | `*` si es enmienda, vacío si no |

### Tipos de filing comunes

| Tipo | Categoría | Descripción |
|------|-----------|-------------|
| 10-K | Annual Reports | Reporte anual |
| 10-Q | Quarterly Reports | Reporte trimestral |
| 8-K | Special Events | Eventos relevantes |
| DEF 14A | Proxy Statement | Voto por poder |
| SC 13G | Institutional Ownership | Tenencia institucional (>5%) |
| SC 13G/A | Institutional Ownership | Enmienda a SC 13G |
| S-8 | Registration Statement | Registro de valores |

### Ejemplo output

```json
{
  "sec_filings": [
    ["05/01/2026", "03/28/2026", "10-Q", "Quarterly Reports", ""],
    ["04/30/2026", "04/30/2026", "8-K", "Special Events", ""],
    ["04/29/2026", "N/A", "SC 13G", "Institutional Ownership", ""]
  ]
}
```

---

## 7. Analyst Estimates

**Endpoint:** `/investing/stock/{TICKER}/analystestimates`

### Value-Pairs (campos fijos)

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Average Recommendation | Recomendación promedio | Overweight |
| Average Target Price | Precio objetivo promedio | 316.07 |
| Number Of Ratings | Cantidad de analistas | 51 |
| FY Report Date | Año fiscal del reporte | 9/2026 |
| Last Quarter's Earnings | EPS último trimestre | 2.01 |
| Year Ago Earnings | EPS mismo trimestre año anterior | 7.38 |
| Current Quarter's Estimate | EPS estimado trimestre actual | 1.88 |
| Current Year's Estimate | EPS estimado año actual | 8.75 |
| Median PE on CY Estimate | P/E medio sobre estimación CY | N/A |
| Next Fiscal Year Estimate | EPS estimado próximo año fiscal | 9.62 |
| Median PE on Next FY Estimate | P/E medio sobre próx año fiscal | N/A |

### Target Price Range (Table 1)

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| High | Precio objetivo máximo | $400.00 |
| Median | Precio objetivo mediano | $320.00 |
| Low | Precio objetivo mínimo | $215.00 |
| Average | Precio objetivo promedio | $316.07 |
| Current Price | Precio actual | $306.31 |

### EPS Estimates — Tables 2-5

| Tabla | Concepto | Período | Current | 1 Month Ago | 3 Months Ago |
|-------|----------|---------|---------|-------------|--------------|
| Table 2 | FY EPS Estimate | Current Year | $8.75 | $8.69 | $8.48 |
| Table 3 | FY EPS Estimate | Next Year | $9.62 | $9.55 | $9.30 |
| Table 4 | Q EPS Estimate | Next Quarter | $1.88 | $1.87 | $1.72 |
| Table 5 | Q EPS Estimate | Last Quarter | $2.01 | $2.00 | $1.97 |

### Rating Changes (Overflow Table)

| Columna | Header | Descripción |
|---------|--------|-------------|
| 0 | Date | Fecha del cambio |
| 1 | Category | Mantiene, Upgrade, Downgrade, Initiates |
| 2 | Analyst Firm | Nombre del banco/analista |
| 3 | Info | Información adicional |

### Ejemplo output

```json
{
  "analyst_estimates": {
    "Average Recommendation": "Overweight",
    "Average Target Price": "316.07",
    "Number Of Ratings": "51",
    "High": "$400.00",
    "Median": "$320.00",
    "Low": "$215.00",
    "Current": "$2.01",
    "estimates_tables": [
      {
        "headers": ["Date", "Category", "Analyst Firm", "Info"],
        "rows": [
          ["5/26/2026", "Maintains", "B of A Securities", ""],
          ["5/14/2026", "Maintains", "Tigress Financial", ""]
        ]
      }
    ]
  }
}
```

---

## 8. Options Chain

**Endpoint:** `/investing/stock/{TICKER}/options`

### Estructura

Cada tabla `table--overflow` representa una **fecha de expiración**. El header indica la fecha de expiración en el TH que contiene la fecha (ej: `Expires Jun 1, 2026`).

### Columnas por fila (14 valores)

La tabla usa `colspan` para agrupar Calls y Puts. Cada fila contiene:

| Índice | Sección | Columna | Descripción |
|--------|---------|---------|-------------|
| 0 | **Strike** | Strike Price | Precio strike (duplicado, ej: `225.00225.00`) |
| 1 | **Calls** | Call - Last | Último precio operado |
| 2 | | Call - Chg | Cambio |
| 3 | | Call - Bid | Precio de compra |
| 4 | | Call - Ask | Precio de venta |
| 5 | | Call - Vol | Volumen |
| 6 | | Call - Open Int | Interés abierto |
| 7 | **Strike** | Strike Price | Precio strike (segunda aparición, limpio) |
| 8 | **Puts** | Put - Last | Último precio operado |
| 9 | | Put - Chg | Cambio |
| 10 | | Put - Bid | Precio de compra |
| 11 | | Put - Ask | Precio de venta |
| 12 | | Put - Vol | Volumen |
| 13 | | Put - Open Int | Interés abierto |

### Ejemplo de fila (AAPL 225 strike, Jun 1, 2026)

```
['225.00', '82.64', '0.00', '80.00', '82.90', '438', '1,154', 
 '225.00', '0.01', '0.00', '0.00', '0.01', '5', '52']
```

| Strike | Call Last | Call Chg | Call Bid | Call Ask | Call Vol | Call OI | Strike | Put Last | Put Chg | Put Bid | Put Ask | Put Vol | Put OI |
|--------|-----------|----------|----------|----------|----------|---------|--------|----------|---------|---------|---------|---------|--------|
| 225.00 | 82.64 | 0.00 | 80.00 | 82.90 | 438 | 1,154 | 225.00 | 0.01 | 0.00 | 0.00 | 0.01 | 5 | 52 |

### Lo que NO incluye

| Dato | Disponible? |
|------|:-----------:|
| Delta (δ) | ❌ No |
| Gamma (γ) | ❌ No |
| Theta (θ) | ❌ No |
| Vega (ν) | ❌ No |
| Rho (ρ) | ❌ No |
| Implied Volatility (IV) | ❌ No |
| Intrinsic Value | ❌ No |
| Extrinsic Value / Time Value | ❌ No |

### Número de tablas por ticker

| Ticker | Tablas (expiración) | Strikes por tabla |
|--------|---------------------|-------------------|
| AAPL (alta liquidez) | ~9 | 30-109 |
| GGAL (baja liquidez) | ~1-3 | 10-20 |

### Output JSON

```json
{
  "options": [
    {
      "expiration": "Jun 1, 2026",
      "headers": ["Item", "Calls", "Expires Jun 1, 2026", "Puts"],
      "rows": [
        ["225.00", "82.64", "0.00", "80.00", "82.90", "438", "1,154", "225.00", "0.01", "0.00", "0.00", "0.01", "5", "52"],
        ...
      ]
    },
    {
      "expiration": "Jun 3, 2026",
      "headers": [...],
      "rows": [...]
    }
  ]
}
```

---

## 9. Historical Data

**Endpoint:** `/investing/stock/{TICKER}/download-data`

### Estructura

3 tablas `table--overflow`:

| Tabla | Período | Filas | Descripción |
|-------|---------|-------|-------------|
| Table 0 | Diario | 20 | Últimos 20 días hábiles |
| Table 1 | Semanal | 5 | Últimas 5 semanas |
| Table 2 | Mensual | 2 | Últimos 2 meses |

### Columnas

| Columna | Header | Descripción | Ejemplo |
|---------|--------|-------------|---------|
| 0 | Date | Fecha (MM/DD/YYYY, duplicado) | 06/02/2026 |
| 1 | Open | Precio de apertura | $307.46 |
| 2 | High | Precio máximo | $315.45 |
| 3 | Low | Precio mínimo | $306.69 |
| 4 | Close | Precio de cierre | $315.20 |
| 5 | Volume | Volumen operado | 44,058,500 |

### Output JSON

```json
{
  "historical": [
    ["06/02/2026", "$307.46", "$315.45", "$306.69", "$315.20", "44,058,500"],
    ["06/01/2026", "$309.63", "$310.94", "$305.02", "$306.31", "48,849,930"]
  ]
}
```

---

## 10. Consideraciones Técnicas

### Rate Limiting vs Datadome

MarketWatch usa **Datadome** para anti-bot. Tolerancia:

| Delay | Resultado |
|-------|-----------|
| 1s | ❌ 401 después de 1-2 requests |
| 3s | ✅ Funciona, pero puede fallar tras 10+ requests |
| 5s | ✅ ✅ Recomendado para múltiples endpoints |

### Headers requeridos

El scraper ya incluye headers modernos de Chrome 120 con `Sec-Ch-Ua`, `Sec-Fetch-*`, etc. Si hacés requests manuales, necesitás **todos** estos headers o recibís 401.

### Notas sobre financials trimestrales

- Algunos campos vienen como `-` en trimestral porque MarketWatch no desglosa ese nivel de detalle (ej: Depreciation, R&D en quarterly aparecen como `-`)
- Cash Flow **no tiene** datos trimestrales en MarketWatch

### Formato de números

Los valores financieros se presentan en formato humano:
- `365.82B` = 365,820,000,000
- `94.68B` = 94,680,000,000
- `-22.89%` = porcentajes
- `5.67` = EPS en dólares

### Opciones

- No hay Greeks (Delta, Gamma, Theta, Vega, Rho)
- No hay Implied Volatility (IV)
- Las tablas vacías (sin datos) tienen strings vacíos `''` en lugar de valores
- Tickers con baja liquidez (GGAL) pueden tener 1-3 tablas con strikes limitados
