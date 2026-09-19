#!/usr/bin/env python3
"""
Fetch financial statements estructurados desde SEC EDGAR (XBRL JSON API).

Usa secfi para obtener CIK + requests directos a la API JSON de la SEC.
Descarga income statement, balance sheet, cash flow en formato estructurado.

Uso:
    python fetch_financials.py --ticker AAPL --all
    python fetch_financials.py --ticker MSFT --income
    python fetch_financials.py --ticker NVDA --balance --cashflow
    python fetch_financials.py --ticker AAPL --all --output data/aapl
    python fetch_financials.py --ticker AAPL --all --all-concepts --output data/aapl_full
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

# Intentar importar secfi; si no está, mostrar error
try:
    import secfi
except ImportError:
    print("ERROR: secfi no instalado. Ejecutar: pip install secfi")
    sys.exit(1)

HEADERS = {"User-Agent": "osojuanferpity@xmail.com"}

# =========================================================================
# Conceptos US-GAAP organizados por estado financiero
# =========================================================================

INCOME_CONCEPTS = [
    "Revenues",
    "CostOfRevenue",
    "GrossProfit",
    "ResearchAndDevelopmentExpense",
    "SellingGeneralAndAdministrativeExpense",
    "OperatingExpenses",
    "OperatingIncomeLoss",
    "NonoperatingIncomeExpense",
    "InterestExpense",
    "InterestIncomeExpenseNonoperatingNet",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxes",
    "IncomeTaxExpenseBenefit",
    "IncomeLossFromContinuingOperationsAfterTax",
    "NetIncomeLoss",
    "NetIncomeLossAvailableToCommonStockholdersBasic",
    "PreferredStockDividendsAndOtherAdjustments",
    "EarningsPerShareBasic",
    "EarningsPerShareDiluted",
    "WeightedAverageNumberOfSharesOutstandingBasic",
    "WeightedAverageNumberOfSharesDilutedOutstanding",
]

BALANCE_CONCEPTS = [
    "Assets",
    "AssetsCurrent",
    "CashAndCashEquivalentsAtCarryingValue",
    "ShortTermInvestments",
    "AvailableForSaleSecuritiesCurrent",
    "AccountsReceivableNetCurrent",
    "InventoryNet",
    "PrepaidExpenseAndOtherAssetsCurrent",
    "OtherAssetsCurrent",
    "PropertyPlantAndEquipmentNet",
    "OperatingLeaseRightOfUseAsset",
    "Goodwill",
    "IntangibleAssetsNetExcludingGoodwill",
    "LongTermInvestments",
    "DeferredIncomeTaxAssetsNet",
    "OtherNoncurrentAssets",
    "Liabilities",
    "LiabilitiesCurrent",
    "AccountsPayableCurrent",
    "AccruedLiabilitiesCurrent",
    "ContractWithCustomerLiabilityCurrent",
    "DebtCurrent",
    "LongTermDebtNoncurrent",
    "OperatingLeaseLiabilityNoncurrent",
    "DeferredIncomeTaxLiabilitiesNet",
    "OtherNoncurrentLiabilities",
    "StockholdersEquity",
    "CommonStockValue",
    "AdditionalPaidInCapital",
    "RetainedEarningsAccumulatedDeficit",
    "AccumulatedOtherComprehensiveIncomeLossNetOfTax",
    "TreasuryStockValue",
]

CASHFLOW_CONCEPTS = [
    "NetCashProvidedByUsedInOperatingActivities",
    "AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivities",
    "DepreciationDepletionAndAmortization",
    "ShareBasedCompensation",
    "DeferredIncomeTaxExpenseBenefit",
    "IncreaseDecreaseInAccountsReceivable",
    "IncreaseDecreaseInInventories",
    "IncreaseDecreaseInAccountsPayable",
    "IncreaseDecreaseInOtherOperatingAssets",
    "IncreaseDecreaseInOtherOperatingLiabilities",
    "NetCashProvidedByUsedInInvestingActivities",
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "ProceedsFromSaleOfPropertyPlantAndEquipment",
    "PaymentsToAcquireBusinessesNetOfCashAcquired",
    "PaymentsToAcquireInvestments",
    "ProceedsFromSaleOfInvestments",
    "NetCashProvidedByUsedInFinancingActivities",
    "ProceedsFromIssuanceOfDebt",
    "RepaymentsOfDebt",
    "ProceedsFromIssuanceOfCommonStock",
    "PaymentsOfDividends",
    "PaymentsForRepurchaseOfCommonStock",
    "CashAndCashEquivalentsPeriodIncreaseDecrease",
    "InterestPaid",
    "IncomeTaxesPaid",
]

ALL_CONCEPTS = INCOME_CONCEPTS + BALANCE_CONCEPTS + CASHFLOW_CONCEPTS

# =========================================================================
# IFRS ↔ US-GAAP mapping
# Empresas extranjeras (20-F) usan ifrs-full con nombres de concepto distintos.
# =========================================================================

IFRS_MAP = {
    # Income Statement
    "Revenues": ["RevenueAndOperatingIncome", "Revenue", "RevenueFromInterest"],
    "CostOfRevenue": ["CostOfGoodsAndServicesSold", "CostOfGoodsSold", "FeeAndCommissionExpense"],
    "GrossProfit": ["GrossProfit"],
    "ResearchAndDevelopmentExpense": ["ResearchAndDevelopmentExpense"],
    "SellingGeneralAndAdministrativeExpense": ["AdministrativeExpense", "SellingGeneralAndAdministrativeExpense"],
    "OperatingExpenses": ["OperatingExpense", "OperatingCosts"],
    "OperatingIncomeLoss": ["ProfitLossFromOperatingActivities", "OperatingIncomeLoss"],
    "NonoperatingIncomeExpense": ["NonoperatingIncomeExpense"],
    "InterestExpense": ["InterestExpense"],
    "InterestIncomeExpenseNonoperatingNet": ["InterestRevenueExpense"],
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxes": ["ProfitLossBeforeTax"],
    "IncomeTaxExpenseBenefit": ["IncomeTaxExpenseContinuingOperations", "IncomeTaxExpenseBenefit"],
    "IncomeLossFromContinuingOperationsAfterTax": ["ProfitLossFromContinuingOperations"],
    "NetIncomeLoss": ["ProfitLoss", "NetIncomeLoss"],
    "NetIncomeLossAvailableToCommonStockholdersBasic": ["ProfitLossAttributableToOwnersOfParent", "ProfitLossAttributableToOrdinaryEquityHoldersOfParentEntity"],
    "PreferredStockDividendsAndOtherAdjustments": ["PreferredStockDividendsAndOtherAdjustments"],
    "EarningsPerShareBasic": ["BasicEarningsLossPerShare", "EarningsPerShareBasic"],
    "EarningsPerShareDiluted": ["DilutedEarningsLossPerShare", "EarningsPerShareDiluted"],
    "WeightedAverageNumberOfSharesOutstandingBasic": ["WeightedAverageShares", "WeightedAverageNumberOfSharesOutstandingBasic"],
    "WeightedAverageNumberOfSharesDilutedOutstanding": ["WeightedAverageSharesDiluted", "WeightedAverageNumberOfSharesDilutedOutstanding"],
    # Balance Sheet
    "Assets": ["Assets"],
    "AssetsCurrent": ["AssetsCurrent"],
    "CashAndCashEquivalentsAtCarryingValue": ["CashAndCashEquivalents", "Cash"],
    "ShortTermInvestments": ["ShortTermInvestments"],
    "AvailableForSaleSecuritiesCurrent": ["AvailableForSaleSecuritiesCurrent"],
    "AccountsReceivableNetCurrent": ["AccountsReceivableNetCurrent", "TradeAccountsReceivable"],
    "InventoryNet": ["InventoryNet", "Inventories"],
    "PrepaidExpenseAndOtherAssetsCurrent": ["PrepaidExpenseAndOtherAssetsCurrent"],
    "OtherAssetsCurrent": ["OtherFinancialAssets", "OtherNonfinancialAssets", "OtherAssetsCurrent"],
    "PropertyPlantAndEquipmentNet": ["PropertyPlantAndEquipment", "PropertyPlantAndEquipmentNet"],
    "OperatingLeaseRightOfUseAsset": ["RightofUseAssets", "OperatingLeaseRightOfUseAsset"],
    "Goodwill": ["Goodwill"],
    "IntangibleAssetsNetExcludingGoodwill": ["IntangibleAssets", "IntangibleAssetsNetExcludingGoodwill"],
    "LongTermInvestments": ["LongTermInvestments", "InvestmentAccountedForUsingEquityMethod"],
    "DeferredIncomeTaxAssetsNet": ["DeferredTaxAssets", "DeferredIncomeTaxAssetsNet"],
    "OtherNoncurrentAssets": ["OtherNoncurrentAssets"],
    "Liabilities": ["Liabilities"],
    "LiabilitiesCurrent": ["LiabilitiesCurrent"],
    "AccountsPayableCurrent": ["AccountsPayableCurrent", "TradeAccountsPayable"],
    "AccruedLiabilitiesCurrent": ["AccruedLiabilitiesCurrent"],
    "ContractWithCustomerLiabilityCurrent": ["ContractWithCustomerLiabilityCurrent"],
    "DebtCurrent": ["DebtCurrent", "BorrowingsCurrent"],
    "LongTermDebtNoncurrent": ["LongTermDebtNoncurrent", "BorrowingsNoncurrent"],
    "OperatingLeaseLiabilityNoncurrent": ["LeaseLiabilities", "OperatingLeaseLiabilityNoncurrent"],
    "DeferredIncomeTaxLiabilitiesNet": ["DeferredTaxLiabilities", "DeferredIncomeTaxLiabilitiesNet"],
    "OtherNoncurrentLiabilities": ["OtherNoncurrentLiabilities"],
    "StockholdersEquity": ["Equity", "StockholdersEquity"],
    "CommonStockValue": ["IssuedCapital", "CommonStockValue"],
    "AdditionalPaidInCapital": ["AdditionalPaidInCapital"],
    "RetainedEarningsAccumulatedDeficit": ["RetainedEarnings", "RetainedEarningsAccumulatedDeficit"],
    "AccumulatedOtherComprehensiveIncomeLossNetOfTax": ["AccumulatedOtherComprehensiveIncome", "AccumulatedOtherComprehensiveIncomeLossNetOfTax"],
    "TreasuryStockValue": ["TreasuryStockValue"],
    # Cash Flow
    "NetCashProvidedByUsedInOperatingActivities": ["CashFlowsFromUsedInOperatingActivities"],
    "AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivities": ["AdjustmentsForReconcileProfitLoss"],
    "DepreciationDepletionAndAmortization": ["DepreciationAmortisationAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLoss", "DepreciationDepletionAndAmortization"],
    "ShareBasedCompensation": ["ShareBasedCompensation", "ShareBasedPaymentArrangementExpense"],
    "DeferredIncomeTaxExpenseBenefit": ["DeferredTaxExpenseIncome", "DeferredIncomeTaxExpenseBenefit"],
    "IncreaseDecreaseInAccountsReceivable": ["AdjustmentsForDecreaseIncreaseInTradeAccountsReceivable"],
    "IncreaseDecreaseInInventories": ["AdjustmentsForDecreaseIncreaseInInventories"],
    "IncreaseDecreaseInAccountsPayable": ["AdjustmentsForIncreaseDecreaseInTradeAccountsPayable"],
    "IncreaseDecreaseInOtherOperatingAssets": ["AdjustmentsForDecreaseIncreaseInOtherCurrentAssets", "AdjustmentsForDecreaseIncreaseInOtherFinancialAssets"],
    "IncreaseDecreaseInOtherOperatingLiabilities": ["AdjustmentsForIncreaseDecreaseInOtherCurrentLiabilities"],
    "NetCashProvidedByUsedInInvestingActivities": ["CashFlowsFromUsedInInvestingActivities"],
    "PaymentsToAcquirePropertyPlantAndEquipment": ["PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets", "PaymentsToAcquirePropertyPlantAndEquipment"],
    "ProceedsFromSaleOfPropertyPlantAndEquipment": ["ProceedsFromDisposalsOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets", "ProceedsFromSaleOfPropertyPlantAndEquipment"],
    "PaymentsToAcquireBusinessesNetOfCashAcquired": ["PaymentsToAcquireBusinessesNetOfCashAcquired"],
    "PaymentsToAcquireInvestments": ["PaymentsToAcquireInvestments", "PurchaseOfInterestsInInvestmentsAccountedForUsingEquityMethod"],
    "ProceedsFromSaleOfInvestments": ["ProceedsFromSaleOfInvestments", "ProceedsFromSalesOfInvestmentsAccountedForUsingEquityMethod"],
    "NetCashProvidedByUsedInFinancingActivities": ["CashFlowsFromUsedInFinancingActivities"],
    "ProceedsFromIssuanceOfDebt": ["ProceedsFromIssuanceOfDebt", "ProceedsFromBorrowings"],
    "RepaymentsOfDebt": ["RepaymentsOfDebt", "RepaymentsOfBorrowings"],
    "ProceedsFromIssuanceOfCommonStock": ["ProceedsFromIssuingShares", "ProceedsFromIssuanceOfCommonStock"],
    "PaymentsOfDividends": ["DividendsPaidClassifiedAsFinancingActivities", "PaymentsOfDividends"],
    "PaymentsForRepurchaseOfCommonStock": ["PaymentsForRepurchaseOfCommonStock", "PurchaseOfTreasuryShares"],
    "CashAndCashEquivalentsPeriodIncreaseDecrease": ["IncreaseDecreaseInCashAndCashEquivalents"],
    "InterestPaid": ["InterestPaidClassifiedAsOperatingActivities"],
    "IncomeTaxesPaid": ["IncomeTaxesPaidRefundClassifiedAsOperatingActivities", "IncomeTaxesPaidRefund"],
}

def resolve_concept(gaap_data, us_gaap_name, taxonomy):
    """
    Busca un concepto por nombre US-GAAP.
    Si taxonomy es ifrs-full, prueba el mapping IFRS.
    """
    if taxonomy == "us-gaap":
        return extract_concept(gaap_data, us_gaap_name)

    # IFRS: probar nombres alternativos
    alt_names = IFRS_MAP.get(us_gaap_name, [])
    for alt in alt_names:
        result = extract_concept(gaap_data, alt)
        if result:
            return result
    return None

# =========================================================================
# Funciones core
# =========================================================================


def get_cik(ticker):
    """Obtiene CIK de 10 dígitos para un ticker usando secfi."""
    ciks = secfi.getCiks()
    try:
        return ciks.loc[ticker.upper()].cik
    except KeyError:
        print(f"ERROR: Ticker '{ticker}' no encontrado en SEC")
        sys.exit(1)


def fetch_company_facts(cik):
    """Fetch de companyfacts JSON desde SEC EDGAR."""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    print(f"  Fetching company facts (CIK {cik})...", end=" ", flush=True)
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    print(f"OK ({len(json.dumps(data)) // 1024} KB)")
    return data


def extract_concept(gaap_data, concept_name):
    """Extrae entries de un concepto US-GAAP de companyfacts."""
    concept = gaap_data.get(concept_name, {})
    units_data = concept.get("units", {})
    # Buscar en USD, shares, etc.
    for unit_key, entries in units_data.items():
        if entries:
            label = concept.get("label", concept_name)
            description = concept.get("description", "")
            return {
                "concept": concept_name,
                "label": label,
                "description": description,
                "unit": unit_key,
                "entries": entries,
            }
    return None


def filter_annual(entries):
    """Filtra solo entries anuales (fp==FY) y ordena por fy descendente."""
    annual = [e for e in entries if e.get("fp") == "FY"]
    return sorted(annual, key=lambda x: x.get("fy", 0), reverse=True)


def filter_quarterly(entries):
    """Filtra entries trimestrales (fp==Q1,Q2,Q3,Q4) y ordena por end."""
    q = [e for e in entries if e.get("fp", "").startswith("Q")]
    return sorted(q, key=lambda x: x.get("end", ""), reverse=True)


# =========================================================================
# Output
# =========================================================================


def save_json(data, filepath):
    """Guarda datos como JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    size_kb = os.path.getsize(filepath) / 1024
    print(f"  Guardado: {filepath} ({size_kb:.0f} KB)")


def save_csv(rows, filepath):
    """Guarda rows como CSV."""
    if not rows:
        print(f"  Sin datos para {filepath}")
        return
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Guardado: {filepath} ({len(rows)} filas)")


# =========================================================================
# Main
# =========================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Fetch financial statements estructurados desde SEC EDGAR. "
        "Usa secfi para CIK + API JSON de la SEC."
    )
    parser.add_argument("--ticker", "-t", required=True, help="Ticker (ej: AAPL, MSFT, NVDA)")
    parser.add_argument("--output", "-o", default=None, help="Prefijo de archivos de salida")

    parser.add_argument("--all", action="store_true", help="Fetch de income + balance + cashflow")
    parser.add_argument("--income", action="store_true", help="Income statement")
    parser.add_argument("--balance", action="store_true", help="Balance sheet")
    parser.add_argument("--cashflow", action="store_true", help="Cash flow statement")
    parser.add_argument("--all-concepts", action="store_true", help="Todos los conceptos disponibles")
    parser.add_argument("--annual", action="store_true", default=True, help="Solo datos anuales (default)")
    parser.add_argument("--quarterly", action="store_true", help="Incluir datos trimestrales")
    parser.add_argument("--quiet", "-q", action="store_true", help="Sin salida detallada")

    args = parser.parse_args()

    if not any([args.all, args.income, args.balance, args.cashflow]):
        args.all = True

    ticker = args.ticker.upper()
    output_prefix = args.output or f"{ticker}_financials"

    log = print if not args.quiet else lambda *a, **kw: None

    # 1. Obtener CIK
    log(f">> Obteniendo CIK para {ticker}...")
    cik = get_cik(ticker)
    log(f"  CIK: {cik}")
    log(f"  Entity: {secfi.getCiks().loc[ticker].title}")

    # 2. Fetch company facts
    log("")
    data = fetch_company_facts(cik)
    entity_name = data.get("entityName", ticker)

    # 3. Determinar taxonomía
    facts = data.get("facts", {})
    if "us-gaap" in facts:
        gaap = facts["us-gaap"]
        taxonomy = "us-gaap"
    elif "ifrs-full" in facts:
        gaap = facts["ifrs-full"]
        taxonomy = "ifrs-full"
        log(f"\n>> Usando taxonomia: {taxonomy} (IFRS)")
    else:
        print(f"ERROR: No se encontraron datos financieros (us-gaap ni ifrs-full)")
        print(f"  Taxonomias disponibles: {list(facts.keys())}")
        sys.exit(1)

    # 4. Determinar qué conceptos extraer
    concepts_to_fetch = []
    statement_types = []

    if args.all or args.income:
        concepts_to_fetch += INCOME_CONCEPTS
        statement_types.append("income")
    if args.all or args.balance:
        concepts_to_fetch += BALANCE_CONCEPTS
        statement_types.append("balance")
    if args.all or args.cashflow:
        concepts_to_fetch += CASHFLOW_CONCEPTS
        statement_types.append("cashflow")
    if args.all_concepts:
        # Agregar todos los conceptos disponibles en la taxonomía
        available = list(gaap.keys())
        for c in available:
            if c not in concepts_to_fetch:
                concepts_to_fetch.append(c)

    # 5. Extraer datos
    log(f"\n>> Extrayendo {len(concepts_to_fetch)} conceptos de {taxonomy}...")
    extracted = []

    for concept_name in concepts_to_fetch:
        result = resolve_concept(gaap, concept_name, taxonomy)
        if result and result["entries"]:
            # Filtrar anual
            if args.annual and not args.quarterly:
                result["entries"] = filter_annual(result["entries"])
            elif args.quarterly:
                result["entries"] = filter_quarterly(result["entries"])

            if result["entries"]:
                extracted.append(result)

    log(f"  {len(extracted)} conceptos con datos")

    # 6. Guardar resultados

    # 6a. JSON completo (por statement)
    result_data = {
        "ticker": ticker,
        "cik": cik,
        "entityName": entity_name,
        "taxonomy": taxonomy,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "concepts": {},
    }

    for r in extracted:
        result_data["concepts"][r["concept"]] = {
            "label": r["label"],
            "unit": r["unit"],
            "entries": r["entries"],
        }

    # Guardar JSON completo
    json_path = f"{output_prefix}.json"
    save_json(result_data, json_path)

    # 6b. CSV tabular (aplanado)
    csv_rows = []
    for r in extracted:
        for entry in r["entries"]:
            csv_rows.append({
                "ticker": ticker,
                "concept": r["concept"],
                "label": r["label"],
                "unit": r["unit"],
                "val": entry.get("val", ""),
                "fy": entry.get("fy", ""),
                "fp": entry.get("fp", ""),
                "form": entry.get("form", ""),
                "filed": entry.get("filed", ""),
                "end": entry.get("end", ""),
                "start": entry.get("start", ""),
                "accn": entry.get("accn", ""),
            })

    csv_path = f"{output_prefix}.csv"
    save_csv(csv_rows, csv_path)

    # 6c. CSV por año (matriz concepto x año)
    if args.annual:
        # Obtener todos los años únicos
        years = sorted(set(
            e["fy"]
            for r in extracted
            for e in r["entries"]
            if e.get("fp") == "FY" and e.get("fy")
        ), reverse=True)

        # Por cada statement type
        concept_map = {
            "income": INCOME_CONCEPTS,
            "balance": BALANCE_CONCEPTS,
            "cashflow": CASHFLOW_CONCEPTS,
        }

        for stype in statement_types:
            stype_concepts = concept_map[stype]
            matrix = []
            for cname in stype_concepts:
                found = [r for r in extracted if r["concept"] == cname]
                if not found:
                    continue
                entries_by_fy = {e["fy"]: e["val"] for e in found[0]["entries"] if e.get("fp") == "FY"}
                row = {"concept": cname}
                for y in years:
                    row[str(y)] = entries_by_fy.get(y, "")
                matrix.append(row)

            if matrix:
                stype_path = f"{output_prefix}_{stype}_annual.csv"
                cols = ["concept"] + [str(y) for y in years]
                with open(stype_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=cols)
                    writer.writeheader()
                    writer.writerows(matrix)
                print(f"  Guardado: {stype_path} ({len(matrix)} conceptos x {len(years)} anios)")

    # 7. Resumen
    log(f"\n{'='*50}")
    log(f"Ticker: {ticker} ({entity_name})")
    log(f"Taxonomia: {taxonomy}")
    log(f"Conceptos extraidos: {len(extracted)}")
    log(f"Total entries: {len(csv_rows)}")
    log(f"Archivos generados: {output_prefix}.json, {output_prefix}.csv")

    # Resumen de algunos conceptos clave
    log(f"\n>> Ultimo año disponible:")
    display_keys = ["Revenues", "NetIncomeLoss", "GrossProfit", "OperatingIncomeLoss"]
    if taxonomy == "ifrs-full":
        display_keys = ["Revenues", "NetIncomeLoss", "ProfitLossFromOperatingActivities"]
    for key in display_keys:
        found = [r for r in extracted if r["concept"] == key]
        if not found and taxonomy == "ifrs-full":
            # Try to find the IFRS name
            alt_names = IFRS_MAP.get(key, [])
            for alt in alt_names:
                found = [r for r in extracted if r["concept"] == alt]
                if found:
                    key = alt
                    break
        if found and found[0]["entries"]:
            latest = found[0]["entries"][0]
            log(f"  {key}: {latest.get('val', 'N/A')} ({latest.get('fy', 'N/A')})")

    # 9. Calcular FCF si hay datos
    if taxonomy == "us-gaap":
        op_cf_name = "NetCashProvidedByUsedInOperatingActivities"
        capex_name = "PaymentsToAcquirePropertyPlantAndEquipment"
    else:
        op_cf_name = "CashFlowsFromUsedInOperatingActivities"
        capex_name = "PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets"

    op_cf = next((r for r in extracted if r["concept"] == op_cf_name), None)
    capex = next((r for r in extracted if r["concept"] == capex_name), None)

    if op_cf and capex:
        log(f"\n>> Free Cash Flow (FCF) estimado:")
        op_by_fy = {e["fy"]: e["val"] for e in op_cf["entries"] if e.get("fp") == "FY"}
        capex_by_fy = {e["fy"]: e["val"] for e in capex["entries"] if e.get("fp") == "FY"}
        for fy in sorted(op_by_fy.keys(), reverse=True)[:5]:
            ocf = op_by_fy.get(fy, 0)
            cpx = abs(capex_by_fy.get(fy, 0))
            fcf = ocf - cpx
            log(f"  {fy}: FCF = {ocf} - {cpx} = {fcf}")


if __name__ == "__main__":
    main()
