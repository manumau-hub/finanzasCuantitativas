---
name: barchart
description: "Quotes, fundamentals, insider, analyst ratings, earnings estimates, financial summary, income/balance/cashflow detail y company profile (delayed 15-20min). 30K+ stocks US y ADRs globales. Sin API key."
license: MIT
---

# Barchart Scraper

Extrae datos de [Barchart](https://www.barchart.com/) mediante **scraping HTML**. Sin bs4, sin lxml, sin API key.

---

## ⚠️ Datos clave

| Concepto | Respuesta |
|----------|-----------|
| **Tipo de datos** | Quotes + fundamentals + insider + analyst ratings + earnings estimates + financial summary + income/balance/cashflow detail + company profile |
| **Latencia** | ❌ **Delayed 15-20 min** (exchange delay estándar). Futuros: 10 min. No es tiempo real |
| **Cobertura** | ~**30,000+ símbolos US**: NYSE, NASDAQ, AMEX, OTC-US. ADRs globales incluidos (GGAL, BABA, SUPV, etc.) |
| **Requiere registro/API key** | No |
| **Dependencias** | Solo `pip install requests` |
| **Método** | Scraping de HTML estático. Barchart usa AngularJS — datos renderizados client-side **no disponibles** |

---

## Instalación

```bash
pip install requests
```

---

## Scripts

| Script | Descripción |
|--------|-------------|
| `fetch_barchart.py` | Scraper: quote + fundamentals + insider + analysts + earnings estimates + income/balance/cashflow detail + company profile |

---

## Uso rápido

```bash
# Quote + fundamentals (27 campos) — sin flags extra
py fetch_barchart.py AAPL
py fetch_barchart.py AAPL,MSFT,GGAL         # Multi-ticker

# Insider summary (--insider)
py fetch_barchart.py AAPL --insider

# Analyst ratings (--analysts)
py fetch_barchart.py AAPL --analysts

# Earnings estimates (--estimates)
py fetch_barchart.py AAPL --estimates

# Financial summary annual (--financials)
py fetch_barchart.py GGAL --financials

# Financial summary quarterly (--financials quarterly)
py fetch_barchart.py GGAL --financials quarterly

# Income statement detail (--income)
py fetch_barchart.py GGAL --income                    # trimestral (default)
py fetch_barchart.py GGAL --income annual

# Balance sheet detail (--balance)
py fetch_barchart.py GGAL --balance                    # trimestral (default)
py fetch_barchart.py GGAL --balance annual

# Cash flow detail (--cashflow)
py fetch_barchart.py GGAL --cashflow                   # trimestral (default)
py fetch_barchart.py GGAL --cashflow annual

# Company profile (--profile)
py fetch_barchart.py GGAL --profile

# Combinar flags
py fetch_barchart.py GGAL --insider --analysts --estimates --income --balance --cashflow

# Output
py fetch_barchart.py AAPL -o aapl.json      # Guardar JSON
py fetch_barchart.py AAPL -q                # JSON a stdout
```

---

## Output real por flag

### `py fetch_barchart.py AAPL` (quote + fundamentals)

```
  ticker: AAPL
  symbol: AAPL
  name: Apple Inc
  lastPrice: 310.26
  netChange: -4.94
  percentChange: -1.57%
  bid: 313.88
  ask: 313.97
  exchange: NASDAQ
  tradeTime: 06/03/26
  marketCap: 4,629,454,720          # en $K (dividir /1000)
  sharesOutstanding: 14,687,355      # en K
  annualSales: 416,161 M
  annualIncome: 112,010 M
  ebit: 147,366 M
  ebitda: 159,064 M
  beta: 1.09
  priceSales: 10.81
  priceCashFlow: 36.59
  priceBook: 42.25
  peRatio: 37.04
  eps: 8.27
  mostRecentEarnings: $2.01 on 04/30/26
  nextEarningsDate: 07/30/26
  dividend: 1.08 (0.35%)             # monto anual + yield
  mostRecentDividend: 0.270 on 05/11/26
```

### `py fetch_barchart.py GGAL` (mismos campos para ADR)

```
  ticker: GGAL
  symbol: GGAL
  name: Grupo Fin Galicia ADR
  lastPrice: 48.33
  netChange: -2.00
  percentChange: -3.97%
  bid: 47.15 / ask: 49.99
  exchange: NASDAQ
  marketCap: 8,084,256 $K
  sharesOutstanding: 160,625 K
  annualSales: 10,559 M
  annualIncome: 170,020 K            # utilidad negativa
  ebit: -1,178 M
  ebitda: -934 M
  beta: 1.32
  priceSales: 0.78
  priceBook: 1.37
  peRatio: 0.00
  eps: 2.27
  dividend: 4.86 (9.50%)
  nextEarningsDate: 08/25/26
```

### `--insider` (agrega)

```
  --- insider ---
  summaryLast3M:
    buys: 0
    buyShares: 0
    sells: 6
    sellShares: 397759
```

**Qué significa:** Últimos 3 meses hubo 0 compras y 6 ventas por 397,759 acciones por parte de insiders de la compañía.

### `--analysts` (agrega)

```
  --- analysts ---
  current:     Moderate Buy (4.12) - 42 analysts
  1_mth_ago:   Moderate Buy (4.12) - 42 analysts
  2_mths_ago:  Moderate Buy (4.07) - 42 analysts
  3_mths_ago:  Moderate Buy (4.07) - 42 analysts
```

**Qué significa:** Rating actual = Moderate Buy con valor 4.12/5 basado en 42 analistas. La escala va de 1 (Strong Sell) a 5 (Strong Buy). Se muestra también el histórico de los últimos 3 meses.

### `--estimates` (agrega)

```
  --- earnings estimates ---
  Average Earnings Estimate: $0.82 | $1.11 | $3.69 | $6.42
  Number of Estimates: 3 | 2 | 3 | 3
  High Estimate: $1.02 | $1.30 | $4.45 | $8.12
  Low Estimate: $0.69 | $0.92 | $3.29 | $5.21
  Prior Year: $0.94 | $0.08 | N/A | $3.69
  Growth Rate Est. (yoy): -12.77% | +1,287.50% | -99.63% | +73.98%
```

**Columnas de la tabla:** Current Qtr (06/2026) | Next Qtr (09/2026) | Fiscal Yr (12/2026) | Fiscal Yr (12/2027)

**Qué significa:**
- Average Earnings Estimate = estimación de EPS promedio de los analistas
- Number of Estimates = cuántos analistas dieron estimación para ese período
- High/Low Estimate = estimación más optimista y más pesimista
- Prior Year = EPS reportado en el mismo período del año anterior
- Growth Rate Est. = crecimiento estimado vs año anterior

### `--financials` annual (agrega)

```
  --- financial summary (annual) ---

  incomeStatement:
    Periods: 12-2025 | 12-2024 | 12-2023 | 12-2022 | 12-2021
    Sales: $10.56B | $11.64B | $24.99B | $9.99B | $5.11B
    Net Income: $170.02M | $1.79B | $1.28B | $374.52M | $326.49M

  balanceSheet:
    Periods: 12-2025 | 12-2024 | 12-2023 | 12-2022 | 12-2021
    Assets: $36.54B | $35.77B | $38.82B | $25.96B | $17.62B
    Liabilities: $30.33B | $29.10B | $31.16B | $21.27B | $14.42B

  cashFlow:
    Periods: 12-2025 | 12-2024 | 12-2023 | 12-2022 | 12-2021
    Cash (Operating): $-1.28B | $3.85B | $6.34B | $4.47B | $2.97B
    Net Cash Flow: $423.52M | $320.47M | $-3.28B | $588.02M | $736.72M
```

**Qué significa:** Income statement con Sales y Net Income de los últimos 5 años, Balance Sheet con Assets y Liabilities, Cash Flow con Operating Cash Flow y Net Cash Flow. Cada valor está formateado en B (billones) o M (millones). Los períodos son `MM-YYYY`. 

### `--financials quarterly` (agrega)

```
  --- financial summary (quarterly) ---

  incomeStatement:
    Periods: 03-2026 | 09-2025 | 06-2025 | 03-2025 | 12-2024
    Sales: $672.00M | $409.98M | $2.24B | $2.18B | $8.58B
    Net Income: $46.54M | $-70.17M | $150.71M | $146.32M | $846.01M

  balanceSheet:
    Periods: 03-2026 | 09-2025 | 06-2025 | 03-2025 | 12-2024
    Assets: $31.61B | $36.54B | $33.60B | $31.33B | $35.77B
    Liabilities: $25.60B | $30.33B | $27.92B | $25.26B | $29.10B

  cashFlow:
    Periods: 03-2026 | 09-2025 | 06-2025 | 03-2025 | 12-2024
    Cash (Operating): $-1.28B | $-966.19M | $3.85B | $5.32B | $0.00
    Net Cash Flow: $423.52M | $-1.16B | $320.47M | $1.14B | $0.00
```

**Qué significa:** Mismos campos que annual pero para los últimos 5 trimestres en lugar de años.

### `--income quarterly` (agrega income statement detallado)

```
  --- income statement detail (quarterly) ---
    Periods: 09-2025 | 03-2025 | 12-2024 | 09-2024 | 06-2024
    Interest Income: N/A | 1,590,672 | 7,624,088 | 1,444,576 | N/A
    Interest Expense: 0 | 628,468 | 2,797,842 | 606,029 | 0
    Interest Income (Net of Interest Expense): 996,333 | 962,204 | 1,774,389 | 838,547 | 1,400,136
    Non-Interest Income: 409,984 | 589,955 | 959,292 | 576,923 | 526,451
    Sales: 1,406,317 | 1,552,158 | 2,997,404 | 1,415,470 | 1,926,588
    Credit Losses Provision: N/A | N/A | N/A | N/A | 160,058
    Non Interest Expenses: 1,545,414 | 1,340,467 | 2,005,786 | 1,132,053 | 1,074,184
    Pre-tax Income: -139,097 | 211,692 | 991,619 | 283,417 | 692,346
    Income Tax: -68,924 | 65,327 | 145,681 | 98,683 | 242,396
    Other Income: -139,097 | 840,160 | 3,789,461 | 889,446 | 692,346
    Net Income: $-70,168 | $146,321 | $846,011 | $184,766 | $449,884
    EPS Basic Continuous Ops: -0.44 | 0.92 | 4.62 | 1.25 | 3.05
    EPS Basic Total Ops: -0.44 | 0.92 | 5.67 | 1.25 | 3.05
    EPS Diluted Continuous Ops: -0.44 | 0.92 | 4.62 | 1.25 | 3.05
    EPS Diluted Total Ops: -0.44 | 0.92 | 5.67 | 1.25 | 3.05
    EPS Diluted Before Non-Recurring Items: 0.08 | 0.96 | N/A | N/A | N/A
    EBITDA(a): $N/A | $N/A | $N/A | $N/A | $N/A
```

Con `--income annual` cambian los períodos a `12-YYYY` y los valores son anuales.

### `--balance quarterly` (agrega balance sheet detallado)

```
  --- balance sheet detail (quarterly) ---
    Periods: 09-2025 | 03-2025 | 12-2024 | 09-2024 | 06-2024
    Assets:
    Cash & Cash Equivalents: 6,955,327 | 5,545,430 | 7,419,325 | 7,422,673 | 2,853,684
    Securities And Investments: 676,711 | 6,598,840 | 8,225,726 | 6,138,255 | 1,748,708
    Loans Gross: 17,647,550 | 15,687,540 | 16,561,370 | 10,078,030 | 7,070,364
    PPE Net: 936,089 | 989,632 | 1,095,073 | 810,412 | 720,216
    Total Assets: $33,596,770 | $31,332,270 | $35,769,780 | $25,272,940 | $19,191,830
    Total deposits: 19,632,510 | 17,298,760 | 20,497,760 | 15,073,540 | 9,613,379
    Long Term Debt: N/A | 1,421,175 | 1,110,457 | 507,279 | N/A
    Total Liabilities: $27,922,710 | $25,256,920 | $29,099,660 | $20,389,730 | $15,007,280
    Retained earnings: N/A | 558,626 | 464,154 | -172,847 | N/A
    Total Liabilities And Equity: $33,596,766 | $31,332,267 | $35,769,779 | $25,272,935 | $19,191,833
```

### `--cashflow quarterly` (agrega cash flow detallado)

```
  --- cash flow detail (quarterly) ---
    Periods: 09-2025 | 03-2025 | 12-2024 | 09-2024 | 06-2024
    Net Income: N/A | 211,692 | 2,432,345 | 1,610,563 | N/A
    Depreciation Amortization: N/A | 55,824 | 206,874 | 125,586 | N/A
    Operating Cash Flow: $N/A | $-966,190 | $3,853,060 | $5,324,640 | $N/A
    Investing Cash Flow: $N/A | $-65,007 | $951,697 | $-142,836 | $N/A
    Financing Cash Flow: $N/A | $147,569 | $454,877 | $-490,960 | $N/A
    End Cash Position: N/A | 6,077,983 | 8,147,057 | 8,384,714 | N/A
    Net Cash Flow: $N/A | $-1,158,989 | $320,472 | $1,140,003 | $N/A
    Free Cash Flow: 0 | -1,056,768 | 3,616,886 | 5,176,481 | 0
```

### `--profile` (agrega company profile + key statistics)

```
  --- profile ---
    Name: Grupo Fin Galicia ADR
    Address: TTE. GRAL. JUAN D. PERON 430 25TH FLOOR BUENOS AIRES C1 CP1038AAJ ARG
    Website: http://www.gfgsa.com
    Employees: 10,079
    Phone: 54-11-4343-7528
    Fax: 114-331-9183
    Sector: Finance
    Industries: SIC-6029 Commercial Banks, NEC, Banks - Foreign, Indices Nasdaq Composite
    Description: Grupo Financiero Galicia SA. is involved in the Financial Services Industry...

    --- overview ---
      Market Capitalization, $K: 8,084,256
      Enterprise Value, $K: 2,012,866
      Shares Outstanding, K: 160,625
      Float, K: 160,625
      % Float: 100.00%
      Short Interest, K: 6,552
      Short Float: 4.08%
      Days to Cover: 6.72
      Short Volume Ratio: 0.53
      % of Institutional Shareholders: 0.00%

    --- financials ---
      Annual Sales, $: 10,559 M
      Annual Net Income, $: 170,020 K
      Last Quarter Sales, $: 672,000 K
      Last Quarter Net Income, $: 46,540 K
      EBIT, $: -1,178 M
      EBITDA, $: -934,100 K

    --- growth ---
      1-Year Return: -14.61%
      3-Year Return: 226.33%
      5-Year Return: 387.69%
      5-Year Revenue Growth: 141.77%
      5-Year Earnings Growth: -100.00%
      5-Year Dividend Growth: 2,725.00%

    --- perShareInfo ---
      Most Recent Earnings: 0.29 on 05/26/26
      Next Earnings Date: 08/25/26
      Earnings Per Share ttm: 2.27
      EPS Growth vs. Prev Year: -69.79%
      Annual Dividend & Yield (Paid): 2.16 (4.28%)
      Annual Dividend & Yield (Fwd): 4.86 (9.50%)
      Most Recent Dividend: 0.405 on 05/11/26
      Next Ex-Dividends Date: 05/11/26
      Dividend Payable Date: 05/29/26
      Dividend Payout Ratio: 51.43%

    --- ratios ---
      Price/Earnings ttm: 0.00
      Price/Earnings forward: 13.85
      Price/Earnings to Growth: 0.36
      Return-on-Equity %: 0.00%
      Return-on-Assets %: 0.00%
      Profit Margin %: 1.61%
      Debt/Equity: 0.00
      Price/Sales: 0.78
      Price/Cash Flow: 19.86
      Price/Book: 1.37
      Book Value/Share: 37.43
      Interest Coverage: -1.21
      60-Month Beta: 1.32

    --- dividendHistory ---
      Date: Value
      05/11/26: $0.4050
      05/04/26: $0.1640
      03/30/26: $0.1600
      ... (12+ entries)
```

---

## Lo que trae cada flag (resumen)

### `py fetch_barchart.py TICKER` — Siempre: 27 campos de quote + fundamentals

| # | Campo | Descripción | Ejemplo AAPL | Nota |
|---|-------|-------------|-------------|------|
| 1 | ticker | Input del usuario | AAPL | |
| 2 | symbol | Símbolo en Barchart | AAPL | |
| 3 | name | Nombre de la empresa | Apple Inc | |
| 4 | lastPrice | Último precio | 310.26 | Delayed 15-20 min |
| 5 | netChange | Cambio neto en $ | -4.94 | |
| 6 | percentChange | Cambio porcentual | -1.57% | |
| 7 | bid | Bid price actual | 313.88 | |
| 8 | ask | Ask price actual | 313.97 | |
| 9 | exchange | Exchange donde cotiza | NASDAQ | |
| 10 | tradeTime | Hora de última operación | 06/03/26 | |
| 11 | marketCap | Market cap en $K | 4,629,454,720 | Dividir /1000 para $ |
| 12 | sharesOutstanding | Shares en circulación K | 14,687,355 | En miles |
| 13 | annualSales | Ventas anuales | 416,161 M | M = millones |
| 14 | annualIncome | Ingreso neto anual | 112,010 M | |
| 15 | ebit | EBIT | 147,366 M | |
| 16 | ebitda | EBITDA | 159,064 M | |
| 17 | beta | Beta 60 meses | 1.09 | |
| 18 | priceSales | Price/Sales ratio | 10.81 | |
| 19 | priceCashFlow | Price/Cash Flow ratio | 36.59 | |
| 20 | priceBook | Price/Book ratio | 42.25 | |
| 21 | peRatio | Price/Earnings ttm | 37.04 | |
| 22 | eps | Earnings Per Share ttm | 8.27 | |
| 23 | mostRecentEarnings | Último earnings reportado | $2.01 on 04/30/26 | |
| 24 | nextEarningsDate | Próximo earnings date | 07/30/26 | |
| 25 | dividend | Dividendo anual + yield | 1.08 (0.35%) | |
| 26 | mostRecentDividend | Último dividendo pagado | 0.270 on 05/11/26 | |
| 27 | sector | Sector de la empresa | Technology | |

### `--insider` agrega: 4 campos

| # | Campo | Descripción | Ejemplo AAPL |
|---|-------|-------------|-------------|
| 28 | summaryLast3M.buys | Cantidad de transacciones de compra por insiders (3 meses) | 0 |
| 29 | summaryLast3M.buyShares | Acciones compradas por insiders | 0 |
| 30 | summaryLast3M.sells | Cantidad de transacciones de venta | 6 |
| 31 | summaryLast3M.sellShares | Acciones vendidas por insiders | 397,759 |

### `--analysts` agrega: 4 períodos × 3 campos = 12 campos

| Período | Campos | Ejemplo AAPL |
|---------|--------|-------------|
| **current** | rating (texto), value (1-5), analysts (#) | Moderate Buy, 4.12, 42 |
| **1_mth_ago** | rating, value, analysts | Moderate Buy, 4.12, 42 |
| **2_mths_ago** | rating, value, analysts | Moderate Buy, 4.07, 42 |
| **3_mths_ago** | rating, value, analysts | Moderate Buy, 4.07, 42 |

### `--estimates` agrega: 5+ filas × 4 períodos

| Fila | Descripción | Ejemplo GGAL Current Qtr |
|------|-------------|-------------------------|
| Average Earnings Estimate | EPS estimado promedio | $0.82 |
| Number of Estimates | Cantidad de analistas que estiman | 3 |
| High Estimate | EPS estimado más optimista | $1.02 |
| Low Estimate | EPS estimado más pesimista | $0.69 |
| Prior Year | EPS del año anterior en mismo período | $0.94 |
| Growth Rate Est. | Crecimiento estimado vs año anterior | -12.77% |

---

## Lo que NO trae el script

Toda esta data se renderiza con AngularJS y **no está disponible en el HTML estático**. Hay que usar un headless browser (Playwright, Selenium, etc.).

| Página | Datos no disponibles |
|--------|---------------------|
| `/stocks/quotes/{TICKER}/financial-summary` | **Solo income/balance/cash flow están disponibles** con `--financials`. Growth rates (%) no están |
| `/stocks/quotes/{TICKER}/options` | Options chain |
| `/stocks/quotes/{TICKER}/technical-analysis` | RSI, Stochastic, ATR, ADX, Moving Averages, Volatility |
| `/stocks/quotes/{TICKER}/analyst-ratings` | Price targets (High/Mean/Low), Ratings breakdown (cantidad por categoría) |
| `/stocks/quotes/{TICKER}/insider-trades` | Transacciones detalladas (solo summary disponible) |
| `/stocks/quotes/{TICKER}/related-etfs` | **Tabla de ETFs relacionados** (symbol, name, weight) — todo AngularJS |
| `/stocks/signals/top-bottom/top` | Screener / Top lists |

---

## Cómo funciona — endpoints

### Quote + fundamentals
```
GET https://www.barchart.com/stocks/quotes/{TICKER}
```
1. Extrae JSON del atributo `data-ng-init='init({...})'` (symbol, lastPrice, bid/ask, exchange, tradeTime)
2. Extrae pares `<span class="left">Label</span>` + `<span class="right">Value</span>` para fundamentals

### Insider
```
GET https://www.barchart.com/stocks/quotes/{TICKER}/insider-trades
```
- Extrae resumen de texto plano: "Last 3 Months: X Buys, Y Shares; Z Sells, W Shares"

### Analyst ratings
```
GET https://www.barchart.com/stocks/quotes/{TICKER}/analyst-ratings
```
- Extrae de texto plano el patrón: `{Período}\n{Rating}\n{Valor}\nBased on\n{Cantidad}`

### Earnings estimates
```
GET https://www.barchart.com/stocks/quotes/{TICKER}/earnings-estimates
```
- Extrae tabla HTML de estimaciones de EPS

### Financial summary
```
GET https://www.barchart.com/stocks/quotes/{TICKER}/financial-summary/{annual|quarterly}
```
- Extrae JSON del atributo `data-content` con Income Statement (Sales, Net Income), Balance Sheet (Assets, Liabilities) y Cash Flow (Operating Cash Flow, Net Cash Flow) para 5 períodos

### Income statement detail
```
GET https://www.barchart.com/stocks/quotes/{TICKER}/income-statement/{quarterly|annual}
```
- Extrae tabla HTML con Income Statement detallado: Interest Income/Expense, Sales, Net Income, EPS (Basic/Diluted), EBITDA y más (~17 filas)

### Balance sheet detail
```
GET https://www.barchart.com/stocks/quotes/{TICKER}/balance-sheet/{quarterly|annual}
```
- Extrae tabla HTML con Balance Sheet detallado: Cash, Securities, Loans, Total Assets/Liabilities, Shareholders' Equity y más (~23 filas)

### Cash flow detail
```
GET https://www.barchart.com/stocks/quotes/{TICKER}/cash-flow/{quarterly|annual}
```
- Extrae tabla HTML con Cash Flow detallado: Operating, Investing, Financing Cash Flow, Free Cash Flow, Net Cash Flow, End Cash Position y más (~27 filas)

### Company profile
```
GET https://www.barchart.com/stocks/quotes/{TICKER}/profile
```
- Extrae company info desde la sección Company Info (address, website, employees, phone, fax, sector, industries, description)
- Extrae 6 tablas de key statistics: overview (enterprise value, float, short interest), financials (last quarter data), growth (returns, CAGR), per-share info (EPS growth, payout ratio, ex-div date), ratios (P/E forward, PEG, ROE, ROA, profit margin, book value/share), dividend history

---

## Flags del script

| Flag | Descripción | Endpoint |
|------|-------------|----------|
| `TICKER` | Ticker(s) separados por coma (ej: `AAPL,MSFT,GGAL`) | Siempre |
| `--insider` | Resumen de insider trading últimos 3 meses | `/insider-trades` |
| `--analysts` | Analyst ratings actual + histórico 3 meses | `/analyst-ratings` |
| `--estimates` | Earnings estimates (4 períodos) | `/earnings-estimates` |
| `--financials` | Financial summary anual (default) | `/financial-summary/annual` |
| `--financials quarterly` | Financial summary trimestral | `/financial-summary/quarterly` |
| `--income` | Income statement detallado trimestral (default) | `/income-statement/quarterly` |
| `--income annual` | Income statement detallado anual | `/income-statement/annual` |
| `--balance` | Balance sheet detallado trimestral (default) | `/balance-sheet/quarterly` |
| `--balance annual` | Balance sheet detallado anual | `/balance-sheet/annual` |
| `--cashflow` | Cash flow detallado trimestral (default) | `/cash-flow/quarterly` |
| `--cashflow annual` | Cash flow detallado anual | `/cash-flow/annual` |
| `--profile` | Company profile + key statistics | `/profile` |
| `--output` / `-o` | Guarda output en archivo JSON | - |
| `--quiet` / `-q` | Output solo JSON a stdout (modo pipe) | - |

Se pueden combinar: `py fetch_barchart.py AAPL --insider --analysts --estimates --financials --income --balance --cashflow -o aapl_full.json`

---

## Notas técnicas

- **marketCap** está en **$K** (miles). AAPL = 4,629,454,720 → $4.6T
- **sharesOutstanding** está en **K** (miles)
- **annualSales/Income** usan sufijos: `M` = millions, `K` = thousands
- Los datos son **delayed 15-20 min** vs mercado en vivo
- Cubre **ADRs globales** (GGAL, SUPV, BABA, etc.) listados en NYSE/NASDAQ
- **User-Agent** de navegador requerido (ya incluido en el script)
- **Rate limit:** ~300ms entre requests (configurable en el script)

---

## Estructura del skill

```
skills/barchart/
├── SKILL.md                       # Este archivo — documentación principal
├── references/
│   └── REFERENCE.md               # Referencia técnica detallada
├── scripts/
│   └── fetch_barchart.py          # Script principal (sin dependencias extra)
└── assets/
```

---

> **📖 Referencia técnica:** [references/REFERENCE.md](./references/REFERENCE.md) — tabla campo por campo, detalle de extracción, notas técnicas
