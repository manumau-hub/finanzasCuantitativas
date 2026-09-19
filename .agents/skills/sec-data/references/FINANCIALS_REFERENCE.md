# SEC EDGAR Structured Financial Data — Reference Completa

> Documentación de la API JSON de XBRL Facts de la SEC y conceptos US-GAAP
> para financial statements estructurados (income statement, balance sheet, cash flow).
>
> Basado en la API pública de SEC EDGAR: https://www.sec.gov/edgar/sec-api-documentation

---

## Índice

1. [SEC EDGAR JSON API](#1-sec-edgar-json-api)
2. [Estructura del JSON de Company Facts](#2-estructura-del-json-de-company-facts)
3. [Company Concept (histórico por concepto)](#3-company-concept-histórico-por-concepto)
4. [Income Statement — Conceptos US-GAAP](#4-income-statement--conceptos-us-gaap)
5. [Balance Sheet — Conceptos US-GAAP](#5-balance-sheet--conceptos-us-gaap)
6. [Cash Flow Statement — Conceptos US-GAAP](#6-cash-flow-statement--conceptos-us-gaap)
7. [Financial Ratios y Métricas Derivadas](#7-financial-ratios-y-métricas-derivadas)
8. [Taxonomías: us-gaap, ifrs-full, dei](#8-taxonomías-us-gaap-ifrs-full-dei)
9. [Tickers Internacionales y IFRS](#9-tickers-internacionales-y-ifrs)
10. [IFRS ↔ US-GAAP Concept Mapping](#10-ifrs--us-gaap-concept-mapping)
11. [Rate Limiting y Buenas Prácticas](#11-rate-limiting-y-buenas-practicas)
12. [Errores y Troubleshooting](#12-errores-y-troubleshooting)
13. [Apéndice A: Lista completa de conceptos core](#13-apéndice-a-lista-completa-de-conceptos-core)
14. [Apéndice B: Schema de la respuesta JSON](#14-apéndice-b-schema-de-la-respuesta-json)

---

## 1. SEC EDGAR JSON API

La SEC expone dos endpoints REST para datos financieros estructurados XBRL:

### 1.1 Company Facts

```
GET https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json
```

**Headers requeridos:**
```http
User-Agent: nombreapellido@email.com (obligatorio, email real)
Accept: application/json
```

**Parámetros:**
- `CIK` — Central Index Key de 10 dígitos (ej: `0000320193` para Apple)

**Returns:** Todos los facts XBRL reportados por la empresa, organizados por taxonomía y concepto.

### 1.2 Company Concept

```
GET https://data.sec.gov/api/xbrl/companyconcept/CIK{CIK}/us-gaap/{concept}.json
```

**Returns:** Todos los valores reportados para un concepto específico a lo largo del tiempo.

### 1.3 Cómo obtener el CIK

Usando `secfi`:

```python
import secfi
ciks = secfi.getCiks()
cik = ciks.loc["AAPL"].cik  # "0000320193"
```

O directamente desde la SEC:

```python
import requests
r = requests.get("https://www.sec.gov/files/company_tickers.json",
                 headers={"User-Agent": "email@domain.com"})
ciks = pd.DataFrame(r.json()).T.set_index("ticker")
ciks["cik"] = ciks["cik_str"].astype(str).str.zfill(10)
```

---

## 2. Estructura del JSON de Company Facts

```json
{
  "cik": 320193,
  "entityName": "Apple Inc.",
  "facts": {
    "dei": {
      "EntityCommonStockSharesOutstanding": {
        "label": "Entity Common Stock, Shares Outstanding",
        "description": "Indicates number of shares...",
        "units": {
          "shares": [
            {
              "val": 15550000,
              "accn": "0000320193-23-000106",
              "fy": 2023,
              "fp": "FY",
              "form": "10-K",
              "filed": "2023-11-03",
              "frame": "CY2023Q4",
              "end": "2023-09-30"
            }
          ]
        }
      }
    },
    "us-gaap": {
      "Revenues": {
        "label": "Revenues",
        "description": "Amount of revenue recognized from goods sold, services rendered...",
        "units": {
          "USD": [
            {
              "val": 394328000000,
              "accn": "0000320193-23-000106",
              "fy": 2023,
              "fp": "FY",
              "form": "10-K",
              "filed": "2023-11-03",
              "frame": "CY2023",
              "end": "2023-09-30",
              "start": "2022-10-01"
            }
          ]
        }
      },
      "NetIncomeLoss": { ... },
      "Assets": { ... },
      "StockholdersEquity": { ... }
    }
  }
}
```

### Campos de cada fact (entry)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `val` | number | Valor numérico del fact |
| `accn` | string | Accession number del filing |
| `fy` | int | Fiscal year |
| `fp` | string | Fiscal period: `FY`, `Q1`, `Q2`, `Q3`, `Q4` |
| `form` | string | Form type: `10-K`, `10-Q`, `8-K`, etc. |
| `filed` | date | Fecha de filing |
| `frame` | string | Período calendario (ej: `CY2023`, `CY2023Q4`) |
| `end` | date | Fecha de fin del período |
| `start` | date | Fecha de inicio del período (solo para state of affairs) |

---

## 3. Company Concept (histórico por concepto)

### Endpoint

```
GET https://data.sec.gov/api/xbrl/companyconcept/CIK{CIK}/us-gaap/{ConceptName}.json
```

### Ejemplo

```python
import requests
HEADERS = {"User-Agent": "email@domain.com"}

url = "https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/Revenues.json"
r = requests.get(url, headers=HEADERS)
data = r.json()

# data["entityName"] -> "Apple Inc."
# data["cik"] -> 320193
# data["taxonomy"] -> "us-gaap"
# data["concept"] -> "Releases"
# data["units"]["USD"] -> [{val, accn, fy, fp, form, filed, frame, end, start}, ...]

for entry in data["units"]["USD"]:
    if entry["fp"] == "FY":  # solo anual
        print(entry["fy"], entry["val"])
```

### Diferencia entre Company Facts y Company Concept

| Aspecto | Company Facts | Company Concept |
|---------|---------------|-----------------|
| Data | Todos los facts (todos los conceptos) | Un concepto específico |
| Tamaño | Grande (puede ser >50MB) | Pequeño |
| Ideal para | Una sola empresa, full análisis | Series históricas de una métrica |

---

## 4. Income Statement — Conceptos US-GAAP

Conceptos para construir un **income statement** completo.

### Core (esenciales)

| Concepto US-GAAP | Etiqueta | Descripción |
|------------------|----------|-------------|
| `Revenues` | Revenue | Ingresos totales |
| `CostOfRevenue` | Cost of Revenue | Costo de los ingresos |
| `GrossProfit` | Gross Profit | Ganancia bruta = Revenue - CostOfRevenue |
| `ResearchAndDevelopmentExpense` | R&D Expense | Gastos de I+D |
| `SellingGeneralAndAdministrativeExpense` | SG&A Expense | Gastos de venta, generales y administrativos |
| `OperatingExpenses` | Operating Expenses | Total gastos operativos |
| `OperatingIncomeLoss` | Operating Income (EBIT) | Resultado operativo |
| `NonoperatingIncomeExpense` | Non-operating Income | Ingresos/gastos no operativos |
| `InterestIncomeExpenseNonoperatingNet` | Interest Income/Expense | Intereses netos no operativos |
| `IncomeLossFromContinuingOperationsBeforeIncomeTaxes` | Pretax Income | Resultado antes de impuestos |
| `IncomeTaxExpenseBenefit` | Income Tax Expense | Impuesto a las ganancias |
| `IncomeLossFromContinuingOperationsAfterTax` | After-tax Income | Resultado después de impuestos |
| `NetIncomeLoss` | Net Income | Resultado neto |
| `EarningsPerShareBasic` | EPS Basic | Ganancia por acción básica |
| `EarningsPerShareDiluted` | EPS Diluted | Ganancia por acción diluida |
| `WeightedAverageNumberOfSharesOutstandingBasic` | Shares Basic | Acciones promedio básicas |
| `WeightedAverageNumberOfSharesDilutedOutstanding` | Shares Diluted | Acciones promedio diluidas |

### Adicionales (desglose)

| Concepto | Descripción |
|----------|-------------|
| `RevenueFromContractWithCustomerExcludingAssessedTax` | Revenue detallado (ASC 606) |
| `CostOfGoodsAndServicesSold` | Costo de ventas detallado |
| `CostOfGoodsSold` | Costo de mercadería vendida |
| `GrossProfitFromContractsWithCustomers` | Gross profit detallado |
| `SalesRevenueNet` | Revenue neto de ventas |
| `ServiceRevenue` | Revenue de servicios |
| `ProductRevenue` | Revenue de productos |
| `OperatingIncomeLossBeforeInterestExpense` | EBIT antes de intereses |
| `InterestExpense` | Gastos de intereses |
| `InterestIncomeOperating` | Ingresos por intereses operativos |
| `OtherNonoperatingIncomeExpense` | Otros ingresos/gastos no operativos |
| `IncomeTaxExpenseBenefitContinuingOperations` | Impuesto detallado |
| `NetIncomeLossAvailableToCommonStockholdersBasic` | Net income atribuible a comunes |
| `ParticipatingSecuritiesDistributedAndUndistributedEarningsLossBasic` | EPS ajustado |

### Estructura típica de Income Statement

```
Revenue (Revenues)
  - Product Revenue (ProductRevenue)
  - Service Revenue (ServiceRevenue)
= Gross Profit (GrossProfit)
  - R&D (ResearchAndDevelopmentExpense)
  - SG&A (SellingGeneralAndAdministrativeExpense)
= Operating Income (OperatingIncomeLoss) / EBIT
  - Interest Expense (InterestExpense)
  + Other Income (NonoperatingIncomeExpense)
= Pretax Income (IncomeLossFromContinuingOperationsBeforeIncomeTaxes)
  - Tax (IncomeTaxExpenseBenefit)
= Net Income (NetIncomeLoss)
  - Preferred Dividends
= Net Income to Common
  EPS Basic (EarningsPerShareBasic)
  EPS Diluted (EarningsPerShareDiluted)
```

---

## 5. Balance Sheet — Conceptos US-GAAP

### Assets (Activos)

| Concepto | Descripción |
|----------|-------------|
| `Assets` | Activos totales |
| `AssetsCurrent` | Activo corriente |
| `CashAndCashEquivalentsAtCarryingValue` | Caja y equivalentes |
| `ShortTermInvestments` | Inversiones temporarias |
| `AvailableForSaleSecuritiesCurrent` | Valores negociables |
| `AccountsReceivableNetCurrent` | Cuentas a cobrar netas |
| `InventoryNet` | Inventario neto |
| `PrepaidExpenseAndOtherAssetsCurrent` | Gastos pagados por adelantado |
| `OtherAssetsCurrent` | Otros activos corrientes |
| `PropertyPlantAndEquipmentNet` | Propiedad, planta y equipo neto (PP&E) |
| `OperatingLeaseRightOfUseAsset` | Activo por derecho de uso (operating lease) |
| `Goodwill` | Goodwill (llave de negocio) |
| `IntangibleAssetsNetExcludingGoodwill` | Activos intangibles netos |
| `LongTermInvestments` | Inversiones a largo plazo |
| `DeferredIncomeTaxAssetsNet` | Activo por impuesto diferido |
| `OtherNoncurrentAssets` | Otros activos no corrientes |

### Liabilities (Pasivos)

| Concepto | Descripción |
|----------|-------------|
| `Liabilities` | Pasivos totales |
| `LiabilitiesCurrent` | Pasivo corriente |
| `AccountsPayableCurrent` | Cuentas a pagar |
| `AccruedLiabilitiesCurrent` | Pasivos acumulados |
| `ContractWithCustomerLiabilityCurrent` | Pasivo por contrato con cliente |
| `DebtCurrent` | Deuda corriente |
| `LongTermDebtNoncurrent` | Deuda a largo plazo |
| `OperatingLeaseLiabilityNoncurrent` | Pasivo por leasing operativo |
| `DeferredIncomeTaxLiabilitiesNet` | Pasivo por impuesto diferido |
| `OtherNoncurrentLiabilities` | Otros pasivos no corrientes |

### Equity (Patrimonio Neto)

| Concepto | Descripción |
|----------|-------------|
| `StockholdersEquity` | Patrimonio neto total |
| `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` | PN incluyendo no controlantes |
| `CommonStockValue` | Capital social (acciones comunes) |
| `AdditionalPaidInCapital` | Prima de emisión |
| `RetainedEarningsAccumulatedDeficit` | Ganancias retenidas |
| `AccumulatedOtherComprehensiveIncomeLossNetOfTax` | ORI acumulado |
| `TreasuryStockValue` | Acciones en tesorería |

### Estructura típica de Balance Sheet

```
ASSETS
  Current Assets:
    Cash (CashAndCashEquivalentsAtCarryingValue)
    Short-term Investments (ShortTermInvestments)
    Receivables (AccountsReceivableNetCurrent)
    Inventory (InventoryNet)
    Other Current Assets
  Total Current Assets (AssetsCurrent)
  
  Non-current Assets:
    PP&E (PropertyPlantAndEquipmentNet)
    Goodwill (Goodwill)
    Intangibles (IntangibleAssetsNetExcludingGoodwill)
    Other Non-current Assets
  TOTAL ASSETS (Assets)

LIABILITIES
  Current Liabilities:
    Accounts Payable (AccountsPayableCurrent)
    Accrued Liabilities
    Short-term Debt (DebtCurrent)
  Total Current Liabilities (LiabilitiesCurrent)
  
  Non-current Liabilities:
    Long-term Debt (LongTermDebtNoncurrent)
    Deferred Tax Liabilities
    Other Non-current Liabilities
  TOTAL LIABILITIES (Liabilities)

EQUITY
  Common Stock (CommonStockValue)
  Additional Paid-in Capital (AdditionalPaidInCapital)
  Retained Earnings (RetainedEarningsAccumulatedDeficit)
  Treasury Stock (TreasuryStockValue)
  TOTAL EQUITY (StockholdersEquity)

TOTAL LIABILITIES + EQUITY = TOTAL ASSETS
```

---

## 6. Cash Flow Statement — Conceptos US-GAAP

### Operating Activities

| Concepto | Descripción |
|----------|-------------|
| `NetCashProvidedByUsedInOperatingActivities` | Flujo de caja neto de operación |
| `DepreciationDepletionAndAmortization` | Depreciación y amortización |
| `ShareBasedCompensation` | Compensación basada en acciones |
| `DeferredIncomeTaxExpenseBenefit` | Impuesto diferido |
| `IncreaseDecreaseInAccountsReceivable` | Cambio en cuentas a cobrar |
| `IncreaseDecreaseInInventories` | Cambio en inventarios |
| `IncreaseDecreaseInAccountsPayable` | Cambio en cuentas a pagar |
| `IncreaseDecreaseInOtherOperatingAssets` | Cambio en otros activos operativos |
| `IncreaseDecreaseInOtherOperatingLiabilities` | Cambio en otros pasivos operativos |
| `AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivities` | Ajustes totales |

### Investing Activities

| Concepto | Descripción |
|----------|-------------|
| `NetCashProvidedByUsedInInvestingActivities` | Flujo de caja neto de inversión |
| `PaymentsToAcquirePropertyPlantAndEquipment` | CAPEX (compras de PP&E) |
| `PaymentsToAcquireBusinessesNetOfCashAcquired` | Adquisiciones de negocios |
| `ProceedsFromSaleOfPropertyPlantAndEquipment` | Ventas de PP&E |
| `PaymentsToAcquireInvestments` | Compras de inversiones |
| `ProceedsFromSaleOfInvestments` | Ventas de inversiones |
| `ProceedsFromMaturitiesPrepaymentsAndCallsOfInvestments` | Vencimiento de inversiones |

### Financing Activities

| Concepto | Descripción |
|----------|-------------|
| `NetCashProvidedByUsedInFinancingActivities` | Flujo de caja neto de financiación |
| `ProceedsFromIssuanceOfDebt` | Emisión de deuda |
| `RepaymentsOfDebt` | Pago de deuda |
| `ProceedsFromIssuanceOfCommonStock` | Emisión de acciones |
| `PaymentsOfDividends` | Pago de dividendos |
| `PaymentsForRepurchaseOfCommonStock` | Recompra de acciones |
| `ProceedsFromIssuanceOfPreferredStock` | Emisión de acciones preferidas |

### Summary

| Concepto | Descripción |
|----------|-------------|
| `CashAndCashEquivalentsPeriodIncreaseDecrease` | Cambio neto en efectivo |
| `CashAndCashEquivalentsAtCarryingValue` | Efectivo final |
| `InterestPaid` | Intereses pagados (GAAP) |
| `IncomeTaxesPaid` | Impuestos pagados (GAAP) |

### Free Cash Flow (derivado)

FCF no es un concepto US-GAAP directo. Se calcula:

```
FCF = NetCashProvidedByUsedInOperatingActivities - PaymentsToAcquirePropertyPlantAndEquipment
```

O alternativamente:

```
FCF = NetCashProvidedByUsedInOperatingActivities - CapitalExpenditure
```

---

## 7. Financial Ratios y Métricas Derivadas

Estos ratios se calculan a partir de los conceptos US-GAAP. No existen como facts directos.

### Profitability Ratios

| Ratio | Fórmula | Conceptos |
|-------|---------|-----------|
| Gross Margin | `GrossProfit / Revenues` | GrossProfit, Revenues |
| Operating Margin | `OperatingIncomeLoss / Revenues` | OperatingIncomeLoss, Revenues |
| Net Margin | `NetIncomeLoss / Revenues` | NetIncomeLoss, Revenues |
| ROA | `NetIncomeLoss / Assets` | NetIncomeLoss, Assets |
| ROE | `NetIncomeLoss / StockholdersEquity` | NetIncomeLoss, StockholdersEquity |
| EBITDA | `OperatingIncomeLoss + DepreciationAmortization` | OperatingIncomeLoss, DepreciationDepletionAndAmortization |

### Liquidity Ratios

| Ratio | Fórmula |
|-------|---------|
| Current Ratio | `AssetsCurrent / LiabilitiesCurrent` |
| Quick Ratio | `(AssetsCurrent - InventoryNet) / LiabilitiesCurrent` |

### Leverage Ratios

| Ratio | Fórmula |
|-------|---------|
| Debt-to-Equity | `(DebtCurrent + LongTermDebtNoncurrent) / StockholdersEquity` |
| Debt-to-Assets | `(DebtCurrent + LongTermDebtNoncurrent) / Assets` |

### Valuation Ratios

| Ratio | Fórmula |
|-------|---------|
| P/E | `Price / EarningsPerShareBasic` (price desde Yahoo Finance) |
| P/B | `Price / (StockholdersEquity / Shares)` |
| Dividend Yield | `Dividend / Price` |

---

## 8. Taxonomías: us-gaap, ifrs-full, dei

La SEC organiza los facts en taxonomías (namespaces):

| Taxonomía | Descripción |
|-----------|-------------|
| `us-gaap` | US Generally Accepted Accounting Principles — la más común para empresas US |
| `ifrs-full` | International Financial Reporting Standards — empresas extranjeras que reportan en IFRS |
| `dei` | Document and Entity Information — metadata del filing (fechas, shares, nombre) |
| `srt` | SEC Reporting Taxonomy — conceptos adicionales (rangos de mercado, etc.) |
| `invest` | Investment management taxonomy |
| `country` | Países |
| `currency` | Monedas |
| `exch` | Exchanges |

### Cómo determinar qué taxonomía usar

```python
data = r.json()
facts = data["facts"]
print(list(facts.keys()))  # ['dei', 'us-gaap'] o ['dei', 'ifrs-full']

if "us-gaap" in facts:
    gaap = facts["us-gaap"]
elif "ifrs-full" in facts:
    gaap = facts["ifrs-full"]
```

### Diferencias clave: US-GAAP vs IFRS

| Aspecto | us-gaap | ifrs-full |
|---------|---------|-----------|
| Empresas | US companies | Foreign private issuers |
| Conceptos | `Revenues`, `NetIncomeLoss` | `Revenue`, `ProfitLoss` |
| Formularios | 10-K, 10-Q | 20-F, 6-K |
| Moneda | USD | Moneda local (puede variar) |

Ejemplo de respuesta IFRS:

```json
{
  "ifrs-full": {
    "Revenue": {
      "label": "Revenue",
      "units": { "USD": [...] }
    },
    "ProfitLoss": {
      "label": "Profit (loss)",
      "units": { "USD": [...] }
    }
  }
}
```

---

## 9. Tickers Internacionales y IFRS

### Empresas que usan IFRS

Las empresas extranjeras listadas en US suelen reportar en IFRS usando el formulario 20-F.

**Ejemplo:**
- `GGAL.BA` → Banco Galicia. Es argentina, reporta en la BCBA. **No presenta 10-K** en SEC (no está listada en US).
- `BABA` → Alibaba. China, listada en NYSE. Reporta en IFRS (20-F).
- `SAP` → SAP. Alemana, listada en NYSE. Reporta en IFRS (20-F).
- `Spotify` → SPOT. Sueca. Reporta en IFRS.

### Cómo verificar

```python
# Ver qué forms tiene una empresa en SEC
filings = secfi.getFils("BABA")
print(filings["form"].value_counts())
# 20-F, 6-K, etc.
```

---

## 10. IFRS ↔ US-GAAP Concept Mapping

El script `fetch_financials.py` incluye un diccionario `IFRS_MAP` que mapea automáticamente conceptos US-GAAP
a sus equivalentes IFRS (`ifrs-full`). Esto permite que el mismo script funcione tanto para empresas US (AAPL, MSFT)
como para empresas extranjeras (GGAL, BABA, SAP) sin cambios de configuración.

### Income Statement — IFRS mapping

| US-GAAP | IFRS (ifrs-full) |
|---------|-----------------|
| `Revenues` | `RevenueAndOperatingIncome`, `Revenue`, `RevenueFromInterest` |
| `CostOfRevenue` | `CostOfGoodsAndServicesSold`, `CostOfGoodsSold`, `FeeAndCommissionExpense` |
| `GrossProfit` | `GrossProfit` |
| `ResearchAndDevelopmentExpense` | `ResearchAndDevelopmentExpense` |
| `SellingGeneralAndAdministrativeExpense` | `AdministrativeExpense`, `SellingGeneralAndAdministrativeExpense` |
| `OperatingExpenses` | `OperatingExpense`, `OperatingCosts` |
| `OperatingIncomeLoss` | `ProfitLossFromOperatingActivities`, `OperatingIncomeLoss` |
| `NonoperatingIncomeExpense` | `NonoperatingIncomeExpense` |
| `InterestExpense` | `InterestExpense` |
| `InterestIncomeExpenseNonoperatingNet` | `InterestRevenueExpense` |
| `IncomeLossFromContinuingOperationsBeforeIncomeTaxes` | `ProfitLossBeforeTax` |
| `IncomeTaxExpenseBenefit` | `IncomeTaxExpenseContinuingOperations`, `IncomeTaxExpenseBenefit` |
| `IncomeLossFromContinuingOperationsAfterTax` | `ProfitLossFromContinuingOperations` |
| `NetIncomeLoss` | `ProfitLoss`, `NetIncomeLoss` |
| `NetIncomeLossAvailableToCommonStockholdersBasic` | `ProfitLossAttributableToOwnersOfParent`, `ProfitLossAttributableToOrdinaryEquityHoldersOfParentEntity` |
| `PreferredStockDividendsAndOtherAdjustments` | `PreferredStockDividendsAndOtherAdjustments` |
| `EarningsPerShareBasic` | `BasicEarningsLossPerShare`, `EarningsPerShareBasic` |
| `EarningsPerShareDiluted` | `DilutedEarningsLossPerShare`, `EarningsPerShareDiluted` |
| `WeightedAverageNumberOfSharesOutstandingBasic` | `WeightedAverageShares`, `WeightedAverageNumberOfSharesOutstandingBasic` |
| `WeightedAverageNumberOfSharesDilutedOutstanding` | `WeightedAverageSharesDiluted` |

### Balance Sheet — IFRS mapping

| US-GAAP | IFRS (ifrs-full) |
|---------|-----------------|
| `Assets` | `Assets` |
| `AssetsCurrent` | `AssetsCurrent` |
| `CashAndCashEquivalentsAtCarryingValue` | `CashAndCashEquivalents`, `Cash` |
| `ShortTermInvestments` | `ShortTermInvestments` |
| `AvailableForSaleSecuritiesCurrent` | `AvailableForSaleSecuritiesCurrent` |
| `AccountsReceivableNetCurrent` | `AccountsReceivableNetCurrent`, `TradeAccountsReceivable` |
| `InventoryNet` | `InventoryNet`, `Inventories` |
| `PropertyPlantAndEquipmentNet` | `PropertyPlantAndEquipment`, `PropertyPlantAndEquipmentNet` |
| `OperatingLeaseRightOfUseAsset` | `RightofUseAssets`, `OperatingLeaseRightOfUseAsset` |
| `Goodwill` | `Goodwill` |
| `IntangibleAssetsNetExcludingGoodwill` | `IntangibleAssets`, `IntangibleAssetsNetExcludingGoodwill` |
| `LongTermInvestments` | `LongTermInvestments`, `InvestmentAccountedForUsingEquityMethod` |
| `DeferredIncomeTaxAssetsNet` | `DeferredTaxAssets`, `DeferredIncomeTaxAssetsNet` |
| `Liabilities` | `Liabilities` |
| `LiabilitiesCurrent` | `LiabilitiesCurrent` |
| `AccountsPayableCurrent` | `AccountsPayableCurrent`, `TradeAccountsPayable` |
| `DebtCurrent` | `DebtCurrent`, `BorrowingsCurrent` |
| `LongTermDebtNoncurrent` | `LongTermDebtNoncurrent`, `BorrowingsNoncurrent` |
| `OperatingLeaseLiabilityNoncurrent` | `LeaseLiabilities`, `OperatingLeaseLiabilityNoncurrent` |
| `DeferredIncomeTaxLiabilitiesNet` | `DeferredTaxLiabilities`, `DeferredIncomeTaxLiabilitiesNet` |
| `StockholdersEquity` | `Equity`, `StockholdersEquity` |
| `CommonStockValue` | `IssuedCapital`, `CommonStockValue` |
| `RetainedEarningsAccumulatedDeficit` | `RetainedEarnings`, `RetainedEarningsAccumulatedDeficit` |
| `AccumulatedOtherComprehensiveIncomeLossNetOfTax` | `AccumulatedOtherComprehensiveIncome` |

### Cash Flow — IFRS mapping

| US-GAAP | IFRS (ifrs-full) |
|---------|-----------------|
| `NetCashProvidedByUsedInOperatingActivities` | `CashFlowsFromUsedInOperatingActivities` |
| `AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivities` | `AdjustmentsForReconcileProfitLoss` |
| `DepreciationDepletionAndAmortization` | `DepreciationAmortisationAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLoss` |
| `ShareBasedCompensation` | `ShareBasedCompensation`, `ShareBasedPaymentArrangementExpense` |
| `DeferredIncomeTaxExpenseBenefit` | `DeferredTaxExpenseIncome`, `DeferredIncomeTaxExpenseBenefit` |
| `NetCashProvidedByUsedInInvestingActivities` | `CashFlowsFromUsedInInvestingActivities` |
| `PaymentsToAcquirePropertyPlantAndEquipment` | `PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets` |
| `ProceedsFromSaleOfPropertyPlantAndEquipment` | `ProceedsFromDisposalsOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets` |
| `ProceedsFromSaleOfInvestments` | `ProceedsFromSaleOfInvestments`, `ProceedsFromSalesOfInvestmentsAccountedForUsingEquityMethod` |
| `NetCashProvidedByUsedInFinancingActivities` | `CashFlowsFromUsedInFinancingActivities` |
| `PaymentsOfDividends` | `DividendsPaidClassifiedAsFinancingActivities`, `PaymentsOfDividends` |
| `PaymentsForRepurchaseOfCommonStock` | `PaymentsForRepurchaseOfCommonStock`, `PurchaseOfTreasuryShares` |
| `CashAndCashEquivalentsPeriodIncreaseDecrease` | `IncreaseDecreaseInCashAndCashEquivalents` |
| `IncomeTaxesPaid` | `IncomeTaxesPaidRefundClassifiedAsOperatingActivities`, `IncomeTaxesPaidRefund` |

### Ejemplo práctico: GGAL (IFRS) vs AAPL (US-GAAP)

```bash
# US-GAAP
python scripts/fetch_financials.py --ticker AAPL --all  # 55 conceptos

# IFRS (mapping automatico)
python scripts/fetch_financials.py --ticker GGAL --all  # 40 conceptos
```

El script detecta automaticamente si la empresa usa `us-gaap` o `ifrs-full` y aplica el mapping correspondiente.

---

## 11. Rate Limiting y Buenas Practicas

### Límites

| Límite | Detalle |
|--------|---------|
| Requests | ~10 req/s (recomendado) |
| Sin API key | Público, requiere User-Agent |
| Tamaño response | Puede ser >50MB (companyfacts de AAPL) |
| Cacheo | **Recomendado** — los datos históricos no cambian |

### Estrategia de cacheo

```python
import os
import json
import hashlib
import requests

CACHE_DIR = ".sec_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def cached_fetch(url, headers, ttl=86400):
    key = hashlib.md5(url.encode()).hexdigest()
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    
    if os.path.exists(cache_file) and time.time() - os.path.getmtime(cache_file) < ttl:
        with open(cache_file) as f:
            return json.load(f)
    
    r = requests.get(url, headers=headers)
    data = r.json()
    with open(cache_file, "w") as f:
        json.dump(data, f)
    return data
```

### User-Agent

La SEC **bloquea requests sin User-Agent**. Usar un email real:

```python
# BUENO
HEADERS = {"User-Agent": "juan.perez@gmail.com"}

# MALO (403 Forbidden)
HEADERS = {"User-Agent": "python-requests/2.32"}
```

---

## 12. Errores y Troubleshooting

| Error | Causa | Solución |
|-------|-------|----------|
| `403 Forbidden` | User-Agent inválido o ausente | Usar email real |
| `404 Not Found` | CIK incorrecto | Verificar con `secfi.getCiks()` |
| `KeyError: 'us-gaap'` | Empresa reporta en IFRS | Usar `ifrs-full` |
| `ConnectionError` | Red/rate limit | Reintentar con backoff |
| JSON vacío `{}` | CIK no encontrado en SEC EDGAR | Verificar que el ticker esté en SEC |
| `ParseError` | JSON corrupto o truncado | Re-descargar |
| `ValueError: val no encontrado` | Concepto no reportado por la empresa | Verificar con `list(data.keys())` |

### Debugging rápido

```python
import requests
import secfi

cik = secfi.getCiks().loc["AAPL"].cik
url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
r = requests.get(url, headers={"User-Agent": "test@test.com"})
print(r.status_code, r.headers.get("content-type", ""))
if r.status_code == 200:
    data = r.json()
    print("Entity:", data["entityName"])
    print("Taxonomies:", list(data["facts"].keys()))
    print("US-GAAP concepts:", len(data["facts"].get("us-gaap", [])))
```

---

## 12. Apéndice A: Lista completa de conceptos core

### Income Statement (20 conceptos)

```
Revenues
CostOfRevenue
GrossProfit
ResearchAndDevelopmentExpense
SellingGeneralAndAdministrativeExpense
OperatingExpenses
OperatingIncomeLoss
NonoperatingIncomeExpense
InterestExpense
InterestIncomeExpenseNonoperatingNet
IncomeLossFromContinuingOperationsBeforeIncomeTaxes
IncomeTaxExpenseBenefit
IncomeLossFromContinuingOperationsAfterTax
NetIncomeLoss
NetIncomeLossAvailableToCommonStockholdersBasic
PreferredStockDividendsAndOtherAdjustments
EarningsPerShareBasic
EarningsPerShareDiluted
WeightedAverageNumberOfSharesOutstandingBasic
WeightedAverageNumberOfSharesDilutedOutstanding
```

### Balance Sheet (30 conceptos)

```
Assets
AssetsCurrent
CashAndCashEquivalentsAtCarryingValue
ShortTermInvestments
AvailableForSaleSecuritiesCurrent
AccountsReceivableNetCurrent
InventoryNet
InventoryFinishedGoodsNetOfReserves
PrepaidExpenseAndOtherAssetsCurrent
OtherAssetsCurrent
PropertyPlantAndEquipmentNet
OperatingLeaseRightOfUseAsset
Goodwill
IntangibleAssetsNetExcludingGoodwill
LongTermInvestments
DeferredIncomeTaxAssetsNet
OtherNoncurrentAssets
Liabilities
LiabilitiesCurrent
AccountsPayableCurrent
AccruedLiabilitiesCurrent
ContractWithCustomerLiabilityCurrent
DebtCurrent
LongTermDebtNoncurrent
OperatingLeaseLiabilityNoncurrent
DeferredIncomeTaxLiabilitiesNet
OtherNoncurrentLiabilities
StockholdersEquity
CommonStockValue
AdditionalPaidInCapital
RetainedEarningsAccumulatedDeficit
AccumulatedOtherComprehensiveIncomeLossNetOfTax
TreasuryStockValue
```

### Cash Flow (20 conceptos)

```
NetCashProvidedByUsedInOperatingActivities
AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivities
DepreciationDepletionAndAmortization
ShareBasedCompensation
DeferredIncomeTaxExpenseBenefit
IncreaseDecreaseInAccountsReceivable
IncreaseDecreaseInInventories
IncreaseDecreaseInAccountsPayable
IncreaseDecreaseInOtherOperatingAssets
IncreaseDecreaseInOtherOperatingLiabilities
NetCashProvidedByUsedInInvestingActivities
PaymentsToAcquirePropertyPlantAndEquipment
ProceedsFromSaleOfPropertyPlantAndEquipment
PaymentsToAcquireBusinessesNetOfCashAcquired
PaymentsToAcquireInvestments
ProceedsFromSaleOfInvestments
NetCashProvidedByUsedInFinancingActivities
ProceedsFromIssuanceOfDebt
RepaymentsOfDebt
ProceedsFromIssuanceOfCommonStock
PaymentsOfDividends
PaymentsForRepurchaseOfCommonStock
CashAndCashEquivalentsPeriodIncreaseDecrease
InterestPaid
IncomeTaxesPaid
```

---

## 14. Apéndice B: Schema de la respuesta JSON

### Company Facts Response

```json
{
  "cik": int,
  "entityName": string,
  "facts": {
    "{taxonomy}": {
      "{conceptName}": {
        "label": string,
        "description": string,
        "units": {
          "{unitName}": [
            {
              "val": number,
              "accn": string,
              "fy": int,
              "fp": string,
              "form": string,
              "filed": string (date),
              "frame": string,
              "end": string (date),
              "start": string (date, optional)
            }
          ]
        }
      }
    }
  }
}
```

### Company Concept Response

```json
{
  "cik": int,
  "entityName": string,
  "taxonomy": string,
  "concept": string,
  "units": {
    "{unitName}": [
      {
        "val": number,
        "accn": string,
        "fy": int,
        "fp": string,
        "form": string,
        "filed": string (date),
        "frame": string,
        "end": string (date),
        "start": string (date, optional)
      }
    ]
  }
}
```

---

*Documentación basada en la SEC EDGAR API pública (https://www.sec.gov/edgar/sec-api-documentation).*
*Los conceptos US-GAAP están sujetos a cambios según actualizaciones de FASB.*
