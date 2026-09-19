"""
Fundamental analysis ratios (Class 8 of the indicators taxonomy).

These functions do NOT download data. They accept DataFrames in standard
formats and return metrics. The DataFrames are typically fetched from
one of the following skills in the Gauss314 Skills Repository
(https://github.com/gauss314/skills):

  - sec-data        : structured XBRL financial statements (15+ years)
  - marketwatch     : income, balance, cash flow + analyst data
  - investing       : 81K+ equities fundamentals
  - macrotrends     : 20+ ratios, 15+ years of financial history
  - barchart        : detailed financials + analyst estimates
  - yahoo-finance   : free financial summary modules
  - nasdaq-data     : institutional holdings (13F) + insider trading
  - simplywallst    : snowflake scores + valuation
  - finviz          : fundamental snapshot
  - earningswhispers: full earnings call transcripts
  - marketscreener  : company profile + top shareholders

The functions below are designed to be called on DataFrames that have at
least the line items the formulas need.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Income statement
# ---------------------------------------------------------------------------

def income_metrics(df_income):
    """Compute standard profitability margins from an income statement.

    Expects df_income with at least: revenue, gross_profit, operating_income,
    net_income, ebit (or ebitda). Missing fields are ignored.

    Returns dict with: gross_margin, operating_margin, net_margin, ebitda_margin.
    """
    def _get(df, *keys):
        for k in keys:
            if k in df.index:
                v = df.loc[k]
                return v.iloc[0] if hasattr(v, 'iloc') else v
        return np.nan

    revenue = _get(df_income, 'revenue', 'totalRevenue', 'Total Revenue')
    gross = _get(df_income, 'gross_profit', 'grossProfit', 'Gross Profit')
    op_inc = _get(df_income, 'operating_income', 'operatingIncome', 'Operating Income')
    ebit = _get(df_income, 'ebit', 'EBIT')
    ebitda = _get(df_income, 'ebitda', 'EBITDA')
    net_inc = _get(df_income, 'net_income', 'netIncome', 'Net Income')

    out = {}
    if revenue and not np.isnan(revenue) and revenue != 0:
        if not np.isnan(gross):
            out['gross_margin'] = float(gross / revenue)
        if not np.isnan(op_inc):
            out['operating_margin'] = float(op_inc / revenue)
        if not np.isnan(net_inc):
            out['net_margin'] = float(net_inc / revenue)
        if not np.isnan(ebitda):
            out['ebitda_margin'] = float(ebitda / revenue)
        if not np.isnan(ebit) and not np.isnan(ebitda):
            out['da_to_ebitda'] = float((ebitda - ebit) / ebitda)
    return out


# ---------------------------------------------------------------------------
# Balance sheet
# ---------------------------------------------------------------------------

def balance_metrics(df_balance):
    """Solvency, leverage and liquidity metrics from balance sheet.

    Expects at least: total_assets, total_equity, total_debt, current_assets,
    current_liabilities, inventory, working_capital, cash.
    """
    def _get(df, *keys):
        for k in keys:
            if k in df.index:
                v = df.loc[k]
                return v.iloc[0] if hasattr(v, 'iloc') else v
        return np.nan

    assets = _get(df_balance, 'total_assets', 'totalAssets', 'Total Assets')
    equity = _get(df_balance, 'total_equity', 'totalEquity', 'Total Equity')
    debt = _get(df_balance, 'total_debt', 'totalDebt', 'Total Debt')
    ca = _get(df_balance, 'current_assets', 'currentAssets', 'Current Assets')
    cl = _get(df_balance, 'current_liabilities', 'currentLiabilities', 'Current Liabilities')
    inv = _get(df_balance, 'inventory', 'Inventory')
    cash = _get(df_balance, 'cash', 'Cash')
    wc = _get(df_balance, 'working_capital', 'workingCapital', 'Working Capital')

    out = {}
    if not np.isnan(equity) and equity != 0 and not np.isnan(debt):
        out['debt_to_equity'] = float(debt / equity)
    if not np.isnan(assets) and assets != 0 and not np.isnan(debt):
        out['debt_to_assets'] = float(debt / assets)
    if not np.isnan(ca) and not np.isnan(cl) and cl != 0:
        out['current_ratio'] = float(ca / cl)
        if not np.isnan(inv):
            out['quick_ratio'] = float((ca - inv) / cl)
    if not np.isnan(cash) and not np.isnan(cl) and cl != 0:
        out['cash_ratio'] = float(cash / cl)
    if not np.isnan(wc):
        out['working_capital'] = float(wc)
    return out


# ---------------------------------------------------------------------------
# Cash flow
# ---------------------------------------------------------------------------

def cashflow_metrics(df_cashflow):
    """Cash flow quality and conversion metrics.

    Expects at least: operating_cashflow, capital_expenditures, free_cashflow.
    """
    def _get(df, *keys):
        for k in keys:
            if k in df.index:
                v = df.loc[k]
                return v.iloc[0] if hasattr(v, 'iloc') else v
        return np.nan

    cfo = _get(df_cashflow, 'operating_cashflow', 'operatingCashflow', 'Operating Cashflow')
    capex = _get(df_cashflow, 'capital_expenditures', 'capitalExpenditures', 'Capital Expenditures')
    fcf = _get(df_cashflow, 'free_cashflow', 'freeCashflow', 'Free Cashflow')
    revenue = _get(df_cashflow, 'revenue', 'totalRevenue', 'Total Revenue')
    net_inc = _get(df_cashflow, 'net_income', 'netIncome', 'Net Income')

    out = {}
    if not np.isnan(cfo) and not np.isnan(capex):
        out['fcf_calc'] = float(cfo - capex)
    if not np.isnan(fcf):
        out['fcf_reported'] = float(fcf)
    if not np.isnan(cfo) and not np.isnan(revenue) and revenue != 0:
        out['cfo_to_revenue'] = float(cfo / revenue)
    if not np.isnan(cfo) and not np.isnan(net_inc) and net_inc != 0:
        out['cfo_to_net_income'] = float(cfo / net_inc)
    return out


# ---------------------------------------------------------------------------
# Valuation
# ---------------------------------------------------------------------------

def valuation_metrics(market_cap, df_income, df_balance, share_price=None, shares_out=None):
    """P/E, P/B, P/S, EV/EBITDA.

    Parameters
    ----------
    market_cap : float
        Current market capitalization.
    df_income, df_balance : DataFrames
        As in income_metrics() and balance_metrics().
    share_price, shares_out : float, optional
        If provided, EV can be computed more precisely.
    """
    def _get(df, *keys):
        for k in keys:
            if k in df.index:
                v = df.loc[k]
                return v.iloc[0] if hasattr(v, 'iloc') else v
        return np.nan

    net_inc = _get(df_income, 'net_income', 'netIncome', 'Net Income')
    revenue = _get(df_income, 'revenue', 'totalRevenue', 'Total Revenue')
    ebitda = _get(df_income, 'ebitda', 'EBITDA')
    equity = _get(df_balance, 'total_equity', 'totalEquity', 'Total Equity')
    debt = _get(df_balance, 'total_debt', 'totalDebt', 'Total Debt')
    cash = _get(df_balance, 'cash', 'Cash')

    out = {'market_cap': float(market_cap)}
    if not np.isnan(net_inc) and net_inc > 0:
        out['pe'] = float(market_cap / net_inc)
    if not np.isnan(equity) and equity > 0:
        out['pb'] = float(market_cap / equity)
    if not np.isnan(revenue) and revenue > 0:
        out['ps'] = float(market_cap / revenue)
    if not np.isnan(debt) and not np.isnan(cash) and not np.isnan(ebitda) and ebitda > 0:
        ev = market_cap + debt - cash
        out['ev'] = float(ev)
        out['ev_ebitda'] = float(ev / ebitda)
    if not np.isnan(ebitda) and not np.isnan(net_inc) and net_inc > 0:
        out['ev_earnings'] = float((market_cap + (debt if not np.isnan(debt) else 0) - (cash if not np.isnan(cash) else 0)) / net_inc)
    return out


# ---------------------------------------------------------------------------
# Profitability (ROE, ROA, ROIC)
# ---------------------------------------------------------------------------

def roe_roa(df_income, df_balance):
    """Return on Equity, Return on Assets, Return on Invested Capital."""
    def _get(df, *keys):
        for k in keys:
            if k in df.index:
                v = df.loc[k]
                return v.iloc[0] if hasattr(v, 'iloc') else v
        return np.nan

    ni = _get(df_income, 'net_income', 'netIncome', 'Net Income')
    assets = _get(df_balance, 'total_assets', 'totalAssets', 'Total Assets')
    equity = _get(df_balance, 'total_equity', 'totalEquity', 'Total Equity')
    debt = _get(df_balance, 'total_debt', 'totalDebt', 'Total Debt')
    ebit = _get(df_income, 'ebit', 'EBIT')
    tax_rate = _get(df_income, 'tax_rate', 'taxRate')

    out = {}
    if not np.isnan(ni) and not np.isnan(equity) and equity != 0:
        out['roe'] = float(ni / equity)
    if not np.isnan(ni) and not np.isnan(assets) and assets != 0:
        out['roa'] = float(ni / assets)
    if not np.isnan(ebit) and not np.isnan(debt) and not np.isnan(equity):
        inv = debt + equity
        if inv != 0:
            tr = tax_rate if not np.isnan(tax_rate) else 0.21
            nopat = ebit * (1 - tr)
            out['roic'] = float(nopat / inv)
    return out


# ---------------------------------------------------------------------------
# DuPont decomposition
# ---------------------------------------------------------------------------

def dupont(df_income, df_balance):
    """DuPont decomposition of ROE into tax × interest × margin × turnover × leverage.

    ROE = (NI/EBT) * (EBT/EBIT) * (EBIT/Revenue) * (Revenue/Assets) * (Assets/Equity)
    """
    def _get(df, *keys):
        for k in keys:
            if k in df.index:
                v = df.loc[k]
                return v.iloc[0] if hasattr(v, 'iloc') else v
        return np.nan

    ni = _get(df_income, 'net_income', 'netIncome', 'Net Income')
    ebt = _get(df_income, 'income_before_tax', 'incomeBeforeTax', 'Income Before Tax')
    ebit = _get(df_income, 'ebit', 'EBIT')
    revenue = _get(df_income, 'revenue', 'totalRevenue', 'Total Revenue')
    assets = _get(df_balance, 'total_assets', 'totalAssets', 'Total Assets')
    equity = _get(df_balance, 'total_equity', 'totalEquity', 'Total Equity')

    out = {}
    if all(not np.isnan(x) and x != 0 for x in [ni, ebt]):
        out['tax_burden'] = float(ni / ebt)
    if all(not np.isnan(x) and x != 0 for x in [ebt, ebit]):
        out['interest_burden'] = float(ebt / ebit)
    if all(not np.isnan(x) and x != 0 for x in [ebit, revenue]):
        out['operating_margin'] = float(ebit / revenue)
    if all(not np.isnan(x) and x != 0 for x in [revenue, assets]):
        out['asset_turnover'] = float(revenue / assets)
    if all(not np.isnan(x) and x != 0 for x in [assets, equity]):
        out['leverage'] = float(assets / equity)
    if all(not np.isnan(x) and x != 0 for x in [ni, equity]):
        components = [out.get(k, 1.0) for k in
                      ['tax_burden', 'interest_burden', 'operating_margin',
                       'asset_turnover', 'leverage']]
        out['roe_check'] = float(np.prod(components))
        out['roe_direct'] = float(ni / equity)
    return out


# ---------------------------------------------------------------------------
# Altman Z-Score
# ---------------------------------------------------------------------------

def altman_z(df_income, df_balance, market_cap, total_liabilities, retained_earnings=None):
    """Altman Z-Score for bankruptcy prediction (public firms).

    Z = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
    A = Working Capital / Total Assets
    B = Retained Earnings / Total Assets
    C = EBIT / Total Assets
    D = Market Cap / Total Liabilities
    E = Sales / Total Assets

    Interpretation: Z > 2.99 safe, 1.81 < Z < 2.99 grey zone, Z < 1.81 distress.
    """
    def _get(df, *keys):
        for k in keys:
            if k in df.index:
                v = df.loc[k]
                return v.iloc[0] if hasattr(v, 'iloc') else v
        return np.nan

    assets = _get(df_balance, 'total_assets', 'totalAssets', 'Total Assets')
    wc = _get(df_balance, 'working_capital', 'workingCapital', 'Working Capital')
    re = retained_earnings if retained_earnings is not None else _get(df_balance, 'retained_earnings', 'retainedEarnings', 'Retained Earnings')
    ebit = _get(df_income, 'ebit', 'EBIT')
    sales = _get(df_income, 'revenue', 'totalRevenue', 'Total Revenue')

    if any(np.isnan(x) or x == 0 for x in [assets, total_liabilities, market_cap]):
        return {'z': np.nan, 'interpretation': 'insufficient data'}
    A = wc / assets if not np.isnan(wc) else 0
    B = re / assets if not np.isnan(re) else 0
    C = ebit / assets if not np.isnan(ebit) else 0
    D = market_cap / total_liabilities
    E = sales / assets if not np.isnan(sales) else 0
    z = 1.2 * A + 1.4 * B + 3.3 * C + 0.6 * D + 1.0 * E
    if z > 2.99:
        interp = 'safe'
    elif z > 1.81:
        interp = 'grey zone'
    else:
        interp = 'distress'
    return {'z': float(z), 'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'interpretation': interp}


# ---------------------------------------------------------------------------
# Piotroski F-Score
# ---------------------------------------------------------------------------

def piotroski(df_income_curr, df_balance_curr, df_cashflow_curr,
              df_income_prev, df_balance_prev, df_cashflow_prev):
    """Piotroski F-Score (9-criterion fundamental quality score).

    9 binary criteria, total score 0-9. Higher = stronger fundamentals.
      Profitability (4): NI>0, CFO>0, ROA improved, CFO>NI
      Leverage/Liquidity (3): debt down, current ratio up, shares not diluted
      Operating efficiency (2): gross margin up, asset turnover up
    """
    def _get(df, *keys):
        for k in keys:
            if k in df.index:
                v = df.loc[k]
                return v.iloc[0] if hasattr(v, 'iloc') else v
        return np.nan

    score = 0
    breakdown = {}

    ni = _get(df_income_curr, 'net_income', 'netIncome', 'Net Income')
    breakdown['ni_positive'] = int(not np.isnan(ni) and ni > 0)
    score += breakdown['ni_positive']

    cfo = _get(df_cashflow_curr, 'operating_cashflow', 'operatingCashflow', 'Operating Cashflow')
    breakdown['cfo_positive'] = int(not np.isnan(cfo) and cfo > 0)
    score += breakdown['cfo_positive']

    assets = _get(df_balance_curr, 'total_assets', 'totalAssets', 'Total Assets')
    ni_prev = _get(df_income_prev, 'net_income', 'netIncome', 'Net Income')
    assets_prev = _get(df_balance_prev, 'total_assets', 'totalAssets', 'Total Assets')
    if all(not np.isnan(x) and x != 0 for x in [assets_prev, assets, ni, ni_prev]):
        roa_curr = ni / assets
        roa_prev = ni_prev / assets_prev
        breakdown['roa_improved'] = int(roa_curr > roa_prev)
    else:
        breakdown['roa_improved'] = 0
    score += breakdown['roa_improved']

    if all(not np.isnan(x) for x in [cfo, ni]):
        breakdown['cfo_exceeds_ni'] = int(cfo > ni)
    else:
        breakdown['cfo_exceeds_ni'] = 0
    score += breakdown['cfo_exceeds_ni']

    debt = _get(df_balance_curr, 'total_debt', 'totalDebt', 'Total Debt')
    debt_prev = _get(df_balance_prev, 'total_debt', 'totalDebt', 'Total Debt')
    if all(not np.isnan(x) for x in [debt, debt_prev]) and assets != 0 and assets_prev != 0:
        breakdown['debt_down'] = int((debt / assets) < (debt_prev / assets_prev))
    else:
        breakdown['debt_down'] = 0
    score += breakdown['debt_down']

    ca = _get(df_balance_curr, 'current_assets', 'currentAssets', 'Current Assets')
    cl = _get(df_balance_curr, 'current_liabilities', 'currentLiabilities', 'Current Liabilities')
    ca_prev = _get(df_balance_prev, 'current_assets', 'currentAssets', 'Current Assets')
    cl_prev = _get(df_balance_prev, 'current_liabilities', 'currentLiabilities', 'Current Liabilities')
    if all(not np.isnan(x) and x != 0 for x in [cl, cl_prev]):
        breakdown['current_ratio_up'] = int((ca / cl) > (ca_prev / cl_prev))
    else:
        breakdown['current_ratio_up'] = 0
    score += breakdown['current_ratio_up']

    shares = _get(df_balance_curr, 'shares_outstanding', 'sharesOutstanding', 'Shares Outstanding')
    shares_prev = _get(df_balance_prev, 'shares_outstanding', 'sharesOutstanding', 'Shares Outstanding')
    if all(not np.isnan(x) and x > 0 for x in [shares, shares_prev]):
        breakdown['no_dilution'] = int(shares <= shares_prev)
    else:
        breakdown['no_dilution'] = 0
    score += breakdown['no_dilution']

    gross = _get(df_income_curr, 'gross_profit', 'grossProfit', 'Gross Profit')
    revenue = _get(df_income_curr, 'revenue', 'totalRevenue', 'Total Revenue')
    gross_prev = _get(df_income_prev, 'gross_profit', 'grossProfit', 'Gross Profit')
    revenue_prev = _get(df_income_prev, 'revenue', 'totalRevenue', 'Total Revenue')
    if all(not np.isnan(x) and x != 0 for x in [revenue, revenue_prev, gross, gross_prev]):
        breakdown['gross_margin_up'] = int((gross / revenue) > (gross_prev / revenue_prev))
    else:
        breakdown['gross_margin_up'] = 0
    score += breakdown['gross_margin_up']

    if all(not np.isnan(x) and x != 0 for x in [revenue, assets, revenue_prev, assets_prev]):
        at_curr = revenue / assets
        at_prev = revenue_prev / assets_prev
        breakdown['asset_turnover_up'] = int(at_curr > at_prev)
    else:
        breakdown['asset_turnover_up'] = 0
    score += breakdown['asset_turnover_up']

    return {'f_score': score, 'breakdown': breakdown, 'max': 9}
