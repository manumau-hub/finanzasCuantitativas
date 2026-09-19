# Macrotrends — Referencia de Endpoints y Campos

Documentación de los endpoints y campos disponibles en Macrotrends para cualquier ticker.

---

## Endpoints

| Recurso | URL | Frecuencia | Períodos |
|---------|-----|------------|----------|
| Income Statement | `/{slug}/financial-statements` | Anual (default) | ~15 años |
| Income Statement (Q) | `/{slug}/financial-statements?freq=Q` | Trimestral | ~60 quarters |
| Balance Sheet | `/{slug}/balance-sheet` | Anual | ~15 años |
| Balance Sheet (Q) | `/{slug}/balance-sheet?freq=Q` | Trimestral | ~60 quarters |
| Cash Flow | `/{slug}/cash-flow` | Anual | ~15 años |
| Financial Ratios | `/{slug}/financial-ratios` | Anual | ~15 años |
| Financial Ratios (Q) | `/{slug}/financial-ratios?freq=Q` | Trimestral | ~60 quarters |
| Employees | `/{slug}/number-of-employees` | Anual | ~15 años |
| Ticker Search | `/assets/php/ticker_search_list.php` | - | Todos los tickers |

---

## Campos — Income Statement

| # | Campo | Descripción |
|---|-------|-------------|
| 0 | Revenue | Ingresos totales |
| 1 | Cost Of Goods Sold | Costo de ventas |
| 2 | Gross Profit | Ganancia bruta |
| 3 | Research And Development Expenses | Gastos en I+D |
| 4 | SG&A Expenses | Gastos de venta, generales y administrativos |
| 5 | Other Operating Income Or Expenses | Otros ingresos/gastos operativos |
| 6 | Operating Expenses | Gastos operativos totales |
| 7 | Operating Income | Resultado operativo (EBIT) |
| 8 | Total Non-Operating Income/Expense | Resultado no operativo |
| 9 | Pre-Tax Income | Resultado antes de impuestos |
| 10 | Income Taxes | Impuesto a las ganancias |
| 11 | Income After Taxes | Resultado después de impuestos |
| 12 | Other Income | Otros ingresos |
| 13 | Income From Continuous Operations | Resultado de operaciones continuas |
| 14 | Income From Discontinued Operations | Resultado de operaciones discontinuadas |
| 15 | Net Income | Resultado neto |
| 16 | EBITDA | EBITDA |
| 17 | EBIT | EBIT |
| 18 | Basic Shares Outstanding | Acciones promedio diluidas |
| 19 | Shares Outstanding | Acciones en circulación |
| 20 | Basic EPS | EPS básico |
| 21 | EPS - Earnings Per Share | EPS diluido |

---

## Campos — Balance Sheet

| # | Campo | Descripción |
|---|-------|-------------|
| 0 | Cash On Hand | Caja y equivalentes |
| 1 | Receivables | Cuentas a cobrar |
| 2 | Inventory | Inventarios |
| 3 | Pre-Paid Expenses | Gastos pagados por adelantado |
| 4 | Other Current Assets | Otros activos corrientes |
| 5 | Total Current Assets | Total activo corriente |
| 6 | Property, Plant, And Equipment | Propiedad, planta y equipo (neto) |
| 7 | Long-Term Investments | Inversiones de largo plazo |
| 8 | Goodwill And Intangible Assets | Goodwill e intangibles |
| 9 | Other Long-Term Assets | Otros activos de largo plazo |
| 10 | Total Long-Term Assets | Total activo no corriente |
| 11 | Total Assets | Total activo |
| 12 | Total Current Liabilities | Total pasivo corriente |
| 13 | Long-Term Debt | Deuda de largo plazo |
| 14 | Other Non-Current Liabilities | Otros pasivos no corrientes |
| 15 | Total Long-Term Liabilities | Total pasivo no corriente |
| 16 | Total Liabilities | Total pasivo |
| 17 | Common Stock Net | Capital social |
| 18 | Retained Earnings (Accumulated Deficit) | Ganancias retenidas |
| 19 | Comprehensive Income And Other | Otro resultado integral |
| 20 | Total Shareholders Equity | Total patrimonio neto |
| 21 | Shareholders Equity | Patrimonio neto (sin minoritarios) |
| 22 | Total Liabilities And Shareholders Equity | Total pasivo + patrimonio |

---

## Campos — Cash Flow

| # | Campo | Descripción |
|---|-------|-------------|
| 0 | Net Income/Loss | Resultado neto |
| 1 | Total Depreciation And Amortization - Cash Flow | Depreciación y amortización |
| 2 | Other Non-Cash Items | Otros ajustes no monetarios |
| 3 | Total Non-Cash Items | Total ajustes no monetarios |
| 4 | Change In Accounts Receivable | Variación en cuentas a cobrar |
| 5 | Change In Inventories | Variación en inventarios |
| 6 | Change In Accounts Payable | Variación en cuentas a pagar |
| 7 | Change In Assets/Liabilities | Otras variaciones en activos/pasivos |
| 8 | Total Change In Working Capital | Variación total en capital de trabajo |
| 9 | Cash From Operating Activities | Flujo de efectivo operativo |
| 10 | Net Property, Plant, And Equipment | Capex (inversión en PP&E) |
| 11 | Net Acquisitions | Adquisiciones netas |
| 12 | Net Investment Purchases And Sales | Compras/ventas de inversiones |
| 13 | Other Investing Activities | Otras actividades de inversión |
| 14 | Net Cash From Investing Activities | Flujo de efectivo de inversión |
| 15 | Total Debt Issued | Emisión de deuda |
| 16 | Total Debt Repaid | Pago de deuda |
| 17 | Issuance Of Common Stock | Emisión de acciones |
| 18 | Repurchase Of Common Stock | Recompra de acciones |
| 19 | Issuance And Repayment Of Other Securities | Otras emisiones/amortizaciones |
| 20 | Common Dividends Paid | Dividendos pagados |
| 21 | Other Financing Activities | Otras actividades de financiación |
| 22 | Net Cash From Financing Activities | Flujo de efectivo de financiación |
| 23 | Foreign Exchange Rate Adjustments | Ajustes por tipo de cambio |
| 24 | Net Cash Flow From Discontinued Operations | Flujo de operaciones discontinuadas |
| 25 | Net Change In Cash | Variación neta de efectivo |
| 26 | Cash At Beginning Of Period | Efectivo al inicio del período |
| 27 | Cash At End Of Period | Efectivo al final del período |
| 28 | Free Cash Flow | Flujo de caja libre |

---

## Campos — Ratios Financieros

| # | Campo | Descripción |
|---|-------|-------------|
| 0 | Current Ratio | Liquidez corriente |
| 1 | Long-term Debt / Capital | Deuda LP / Capital total |
| 2 | Debt/Equity Ratio | Deuda / Patrimonio |
| 3 | Gross Margin | Margen bruto (%) |
| 4 | Operating Margin | Margen operativo (%) |
| 5 | EBIT Margin | Margen EBIT (%) |
| 6 | EBITDA Margin | Margen EBITDA (%) |
| 7 | Pre-Tax Profit Margin | Margen antes de impuestos (%) |
| 8 | Net Profit Margin | Margen neto (%) |
| 9 | Asset Turnover | Rotación de activos |
| 10 | Inventory Turnover Ratio | Rotación de inventarios |
| 11 | Receiveable Turnover | Rotación de cuentas a cobrar |
| 12 | Days Sales In Receivables | Días de cobranza |
| 13 | ROE - Return On Equity | ROE (%) |
| 14 | Return On Tangible Equity | ROE tangible (%) |
| 15 | ROA - Return On Assets | ROA (%) |
| 16 | ROI - Return On Investment | ROI (%) |
| 17 | Book Value Per Share | Valor contable por acción |
| 18 | Operating Cash Flow Per Share | FCO por acción |
| 19 | Free Cash Flow Per Share | FCF por acción |

---

## Notas

- **Cash Flow trimestral**: Macrotrends solo muestra data anual de cash flow. El parámetro `?freq=Q` no está disponible.
- **Employee count**: Los datos están en formato HTML `<table>`, no en JSON embebido.
- **Valores vacíos**: Algunos campos pueden retornar strings vacíos `""` si no hay datos para ese período.
- **Formato numérico**: Los valores vienen como strings con formato humano (ej: `"42,000"` para employees). Los statements financieros vienen como números float.
