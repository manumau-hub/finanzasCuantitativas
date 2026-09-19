"""
Barchart — Extrae quotes y fundamentals de barchart.com

Sin bs4, sin lxml, sin API key. Solo pip install requests.

Uso:
    py fetch_barchart.py AAPL
    py fetch_barchart.py AAPL,MSFT,GGAL
    py fetch_barchart.py AAPL -o aapl.json
    py fetch_barchart.py AAPL -q
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
}
BASE = "https://www.barchart.com"
DELAY = 0.3


def log(msg: str):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", file=sys.stderr)


def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    time.sleep(DELAY)
    return r.text


def scrape_quote(ticker: str) -> Dict[str, Any]:
    """Scrapea quote + fundamentals."""
    html = fetch(f"{BASE}/stocks/quotes/{ticker}")
    data: Dict[str, Any] = {"ticker": ticker.upper()}

    # 1. JSON embedido en data-ng-init (price data)
    m = re.search(r"data-ng-init='init\(\s*({.+?})\s*\)'", html)
    if m:
        try:
            q = json.loads(m.group(1))
            data["symbol"] = q.get("symbol")
            data["name"] = q.get("symbolName")
            data["lastPrice"] = q.get("lastPrice")
            data["netChange"] = q.get("priceChange")
            data["percentChange"] = q.get("percentChange")
            data["bid"] = q.get("bidPrice")
            data["ask"] = q.get("askPrice")
            data["exchange"] = q.get("exchange")
            data["tradeTime"] = q.get("tradeTime")
        except json.JSONDecodeError:
            pass

    # 2. Fundamentals de <span class="left"> / <span class="right">
    pairs = re.findall(
        r'<span class="left">([^<]+)</span>\s*<span class="right[^"]*">\s*([^<]+?)\s*</span>',
        html,
    )
    FUND_MAP = {
        "market capitalization": "marketCap",
        "shares outstanding": "sharesOutstanding",
        "annual sales": "annualSales",
        "annual income": "annualIncome",
        "ebitda": "ebitda",
        "ebit": "ebit",
        "price/earnings ttm": "peRatio",
        "earnings per share ttm": "eps",
        "60-month beta": "beta",
        "price/sales": "priceSales",
        "price/book": "priceBook",
        "price/cash flow": "priceCashFlow",
        "annual dividend": "dividend",
        "most recent dividend": "mostRecentDividend",
        "most recent earnings": "mostRecentEarnings",
        "next earnings date": "nextEarningsDate",
    }
    for label, value in pairs:
        lbl = label.strip().lower()
        val = value.strip()
        for key, target in FUND_MAP.items():
            if key in lbl:
                data[target] = val
                break
        if lbl == "sector" or lbl.startswith("sector"):
            data["sector"] = val

    return data


def scrape_insider(ticker: str) -> Dict[str, Any]:
    """Insider trades summary (ultimos 3 meses)."""
    html = fetch(f"{BASE}/stocks/quotes/{ticker}/insider-trades")
    data: Dict[str, Any] = {}
    m = re.search(
        r"Last\s*3\s*Months.*?(\d[\d,]*)\s*Buys.*?(\d[\d,]*)\s*Shares.*?(\d[\d,]*)\s*Sells.*?(\d[\d,]*)",
        html, re.IGNORECASE | re.DOTALL,
    )
    if m:
        data["summaryLast3M"] = {
            "buys": int(m.group(1).replace(",", "")),
            "buyShares": int(m.group(2).replace(",", "")),
            "sells": int(m.group(3).replace(",", "")),
            "sellShares": int(m.group(4).replace(",", "")),
        }
    return data


def scrape_earnings_estimates(ticker: str) -> Dict[str, Any]:
    """Earnings estimates: estimaciones de EPS por periodo."""
    html = fetch(f"{BASE}/stocks/quotes/{ticker}/earnings-estimates")
    data: Dict[str, Any] = {}

    # Buscar tabla de estimaciones (está como HTML plano, no Angular)
    idx = html.find('Average Earnings Estimate')
    if idx < 0:
        return data

    start = html.rfind('<table', 0, idx)
    end = html.find('</table>', idx)
    if start < 0 or end < 0:
        return data

    table_html = html[start:end + 8]

    # Extraer columnas (periodos) del header
    col_headers = []
    for m in re.finditer(r'<th[^>]*>(.*?)</th>', table_html, re.DOTALL):
        h = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if h and ('Qtr' in h or 'Fiscal' in h or 'Year' in h):
            col_headers.append(h)

    # Extraer filas
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
    for row_html in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
        if not cells:
            continue
        label = re.sub(r'<[^>]+>', '', cells[0]).strip()
        if not label or label == '' or len(label) > 60:
            continue

        values = []
        for c in cells[1:]:
            v = re.sub(r'<[^>]+>', '', c).strip()
            if v:
                values.append(v)

        if values:
            data[label] = values

    return data


def scrape_analysts(ticker: str) -> Dict[str, Any]:
    """Analyst ratings: rating actual, valor, cantidad analistas, historico."""
    html = fetch(f"{BASE}/stocks/quotes/{ticker}/analyst-ratings")
    text = re.sub(r'<[^>]+>', '\n', html)
    data: Dict[str, Any] = {}

    periods = ['Current', '1 Mth Ago', '2 Mths Ago', '3 Mths Ago']
    for period in periods:
        m = re.search(
            rf'{re.escape(period)}\s*\n\s*(Strong Buy|Moderate Buy|Buy|Hold|Moderate Sell|Sell|Strong Sell)\s*\n\s*([\d.]+)\s*\n\s*Based on\s*\n\s*(\d+)',
            text, re.IGNORECASE
        )
        if m:
            key = period.lower().replace(' ', '_')
            data[key] = {
                "rating": m.group(1),
                "value": float(m.group(2)),
                "analysts": int(m.group(3)),
            }

    return data


def scrape_financial_summary(ticker: str, period: str = "annual") -> Dict[str, Any]:
    """Financial summary: income statement, balance sheet, cash flow.

    Args:
        ticker: Symbol del ticker
        period: "annual" o "quarterly"

    Returns:
        Dict con secciones (incomeStatement, balanceSheet, cashFlow)
        cada una con series y periodos.
    """
    html = fetch(f"{BASE}/stocks/quotes/{ticker}/financial-summary/{period}")
    data: Dict[str, Any] = {"period": period}

    # Buscar data-content con JSON de financial charts
    for m in re.finditer(r'data-content="({[^"]+})"', html):
        raw = m.group(1).replace('&quot;', '"').replace('&#x2F;', '/')
        try:
            d = json.loads(raw)
            series = d.get('series', [])
            periods = d.get('period', [])
            text = d.get('text', '')

            section_data: Dict[str, Any] = {
                "periods": periods,
                "text": text,
                "series": {},
            }
            for s in series:
                section_data["series"][s["name"]] = s["data"]

            # Clasificar segun los nombres de las series
            names = [s["name"] for s in series]
            names_str = " ".join(names)

            if "Sales" in names_str or "Income" in names_str:
                data["incomeStatement"] = section_data
            elif "Assets" in names_str or "Liabilities" in names_str:
                data["balanceSheet"] = section_data
            elif "Cash" in names_str or "Net Cash" in names_str:
                data["cashFlow"] = section_data

        except json.JSONDecodeError:
            pass

    return data


def _parse_financial_table(html: str) -> tuple:
    """Parse HTML financial table into (periods, rows).

    Returns:
        (list_of_periods, list_of_dicts_with_label_and_values)
    """
    html_clean = html.replace('&#039;', "'").replace('&amp;', '&').replace('&nbsp;', ' ')

    table_match = re.search(r'<table[^>]*>(.*?)</table>', html_clean, re.DOTALL)
    if not table_match:
        return [], []

    table_html = table_match.group(1)
    rows_raw = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
    if not rows_raw:
        return [], []

    periods = []
    data_rows = []

    for i, row_html in enumerate(rows_raw):
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row_html, re.DOTALL)
        if not cells:
            continue

        clean = []
        for c in cells:
            text = re.sub(r'<[^>]+>', '', c).strip()
            text = re.sub(r'\s+', ' ', text).strip()
            clean.append(text)

        if i == 0:
            # Header row — skip first cell (label column header)
            periods = [c for c in clean if c]
        else:
            lbl = clean[0] if clean else ''
            vals = clean[1:] if len(clean) > 1 else []
            if lbl and lbl not in ('', ' ', ' '):
                data_rows.append({'label': lbl, 'values': vals})

    return periods, data_rows


def scrape_income_statement(ticker: str, period: str = "quarterly") -> Dict[str, Any]:
    """Detailed income statement from HTML table.

    Args:
        ticker: Symbol del ticker
        period: "quarterly" o "annual"

    Returns:
        Dict con period, periods (lista) y rows (lista de label+values)
    """
    url = f"{BASE}/stocks/quotes/{ticker}/income-statement/{period}"
    html = fetch(url)
    periods, rows = _parse_financial_table(html)
    return {
        "period": period,
        "periods": periods,
        "rows": rows,
    }


def scrape_balance_sheet(ticker: str, period: str = "quarterly") -> Dict[str, Any]:
    """Detailed balance sheet from HTML table.

    Args:
        ticker: Symbol del ticker
        period: "quarterly" o "annual"

    Returns:
        Dict con period, periods (lista) y rows (lista de label+values)
    """
    url = f"{BASE}/stocks/quotes/{ticker}/balance-sheet/{period}"
    html = fetch(url)
    periods, rows = _parse_financial_table(html)
    return {
        "period": period,
        "periods": periods,
        "rows": rows,
    }


def scrape_cash_flow(ticker: str, period: str = "quarterly") -> Dict[str, Any]:
    """Detailed cash flow statement from HTML table.

    Args:
        ticker: Symbol del ticker
        period: "quarterly" o "annual"

    Returns:
        Dict con period, periods (lista) y rows (lista de label+values)
    """
    url = f"{BASE}/stocks/quotes/{ticker}/cash-flow/{period}"
    html = fetch(url)
    periods, rows = _parse_financial_table(html)
    return {
        "period": period,
        "periods": periods,
        "rows": rows,
    }


def scrape_profile(ticker: str) -> Dict[str, Any]:
    """Company profile: company info + key statistics tables.

    Extracts:
    - Company info: name, address, website, employees, phone, fax, sector, industries, description
    - Key statistics tables: overview, financials, growth, per-share info, ratios, dividends
    """
    html = fetch(f"{BASE}/stocks/quotes/{ticker}/profile")
    data: Dict[str, Any] = {}

    # --- Company Info ---
    company = {}

    # Name from data-ng-init or title
    m = re.search(r"data-ng-init='init\(\s*({.+?})\s*\)'", html)
    if m:
        try:
            q = json.loads(m.group(1))
            company["name"] = q.get("symbolName")
        except json.JSONDecodeError:
            pass

    # Address, website, employees, phone, fax from text-block divs
    # Find the Company Info section
    idx = html.find('Company Info</h3>')
    if idx > 0:
        company_block = html[idx:idx+3000]

        # Address lines: look for <span> text after the name
        spans = re.findall(r'<span>([^<]+)</span>', company_block)
        addr_lines = []
        for sp in spans:
            s = sp.strip()
            if s.startswith('Employees:'):
                company["employees"] = s.replace('Employees:', '').strip()
            elif s.startswith('P:'):
                company["phone"] = s.replace('P:', '').strip()
            elif s.startswith('F:'):
                company["fax"] = s.replace('F:', '').strip()
            elif s and not s.startswith('<') and not s.startswith('www'):
                addr_lines.append(s)

        if addr_lines:
            company["address"] = ' '.join(addr_lines)

        # Website
        mw = re.search(r'href="(https?://[^"]+)"[^>]*>([^<]+)</a>', company_block)
        if mw:
            company["website"] = mw.group(1)

        # Sector
        ms = re.search(r'Sector:</h4>\s*<p>(?:<a[^>]*>)?([^<]+)(?:</a>)?\s*</p>', company_block)
        if ms:
            company["sector"] = ms.group(1).strip()

        # Industry grouping
        industries = re.findall(r'href="[^"]*quoteSectors=[^"]*">\s*([^<]+)\s*</a>', company_block)
        if industries:
            company["industries"] = [i.strip() for i in industries]

        # Description
        md = re.search(r'Description:</h4>\s*<p>([^<]+)</p>', company_block)
        if md:
            company["description"] = md.group(1).strip()

    data["company"] = company

    # --- Key Statistics Tables ---
    tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)
    table_names = [
        "overview",
        "financials",
        "growth",
        "perShareInfo",
        "ratios",
        "dividendHistory",
    ]

    for i, t_html in enumerate(tables):
        if i >= len(table_names):
            break
        rows_raw = re.findall(r'<tr[^>]*>(.*?)</tr>', t_html, re.DOTALL)
        rows = []
        for row_html in rows_raw:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row_html, re.DOTALL)
            if len(cells) < 2:
                continue
            label = re.sub(r'<[^>]+>', '', cells[0]).strip()
            label = label.replace('&amp;', '&').replace('&nbsp;', ' ').strip()
            value = re.sub(r'<[^>]+>', '', cells[1]).strip()
            if label:
                rows.append({"label": label, "value": value})
        if rows:
            data[table_names[i]] = rows

    return data


def main():
    p = argparse.ArgumentParser(description="Barchart scraper")
    p.add_argument("ticker", nargs="?", help="Ticker(s) separados por coma")
    p.add_argument("--insider", action="store_true", help="Incluir insider summary")
    p.add_argument("--analysts", action="store_true", help="Incluir analyst ratings")
    p.add_argument("--estimates", action="store_true", help="Incluir earnings estimates")
    p.add_argument("--financials", type=str, nargs="?", const="annual", choices=["annual", "quarterly"],
                   help="Financial summary: annual o quarterly (default: annual)")
    p.add_argument("--income", type=str, nargs="?", const="quarterly", choices=["annual", "quarterly"],
                   help="Income statement detail (default: quarterly)")
    p.add_argument("--balance", type=str, nargs="?", const="quarterly", choices=["annual", "quarterly"],
                   help="Balance sheet detail (default: quarterly)")
    p.add_argument("--cashflow", type=str, nargs="?", const="quarterly", choices=["annual", "quarterly"],
                   help="Cash flow detail (default: quarterly)")
    p.add_argument("--profile", action="store_true", help="Incluir company profile")
    p.add_argument("--output", "-o", type=str, help="Guardar JSON")
    p.add_argument("--quiet", "-q", action="store_true", help="Output JSON a stdout")
    args = p.parse_args()

    if not args.ticker:
        p.print_help()
        sys.exit(1)

    results: Dict[str, Any] = {}

    for ticker in [t.strip().upper() for t in args.ticker.split(",")]:
        log(f"Fetching {ticker}...")

        # Quote + fundamentals (siempre)
        quote = scrape_quote(ticker)
        results[ticker] = {"quote": quote}

        # Insider (opcional)
        if args.insider:
            results[ticker]["insider"] = scrape_insider(ticker)

        # Analysts (opcional)
        if args.analysts:
            results[ticker]["analysts"] = scrape_analysts(ticker)

        # Earnings estimates (opcional)
        if args.estimates:
            results[ticker]["earningsEstimates"] = scrape_earnings_estimates(ticker)

        # Financial summary (opcional)
        if args.financials:
            results[ticker]["financialSummary"] = scrape_financial_summary(ticker, args.financials)

        # Income statement detail (opcional)
        if args.income:
            results[ticker]["incomeStatement"] = scrape_income_statement(ticker, args.income)

        # Balance sheet detail (opcional)
        if args.balance:
            results[ticker]["balanceSheet"] = scrape_balance_sheet(ticker, args.balance)

        # Cash flow detail (opcional)
        if args.cashflow:
            results[ticker]["cashFlow"] = scrape_cash_flow(ticker, args.cashflow)

        # Profile (opcional)
        if args.profile:
            results[ticker]["profile"] = scrape_profile(ticker)

    # Output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        log(f"Guardado: {args.output}")
    elif args.quiet:
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
    else:
        for ticker, data in results.items():
            print(f"\n=== {ticker} ===")
            for k, v in data.get("quote", {}).items():
                if v is not None and v != "":
                    print(f"  {k}: {v}")
            if "insider" in data:
                print(f"\n  --- insider ---")
                print(f"  {data['insider']}")
            if "analysts" in data:
                print(f"\n  --- analysts ---")
                for period, info in data["analysts"].items():
                    print(f"  {period}: {info['rating']} ({info['value']}) - {info['analysts']} analysts")
            if "earningsEstimates" in data:
                print(f"\n  --- earnings estimates ---")
                for label, values in data["earningsEstimates"].items():
                    print(f"  {label}: {' | '.join(values)}")
            if "financialSummary" in data:
                fs = data["financialSummary"]
                print(f"\n  --- financial summary ({fs.get('period', '?')}) ---")
                for section in ["incomeStatement", "balanceSheet", "cashFlow"]:
                    sec = fs.get(section)
                    if sec:
                        periods = sec.get("periods", [])
                        print(f"\n  {section}:")
                        print(f"    Periods: {' | '.join(periods)}")
                        for name, values in sec.get("series", {}).items():
                            formatted = []
                            for v in values:
                                if isinstance(v, (int, float)):
                                    if abs(v) >= 1e9:
                                        formatted.append(f"${v/1e9:.2f}B")
                                    elif abs(v) >= 1e6:
                                        formatted.append(f"${v/1e6:.2f}M")
                                    elif abs(v) >= 1e3:
                                        formatted.append(f"${v/1e3:.2f}K")
                                    else:
                                        formatted.append(f"${v:.2f}")
                                else:
                                    formatted.append(str(v))
                            print(f"    {name}: {' | '.join(formatted)}")

            if "incomeStatement" in data:
                inc = data["incomeStatement"]
                print(f"\n  --- income statement detail ({inc.get('period', '?')}) ---")
                print(f"    Periods: {' | '.join(inc.get('periods', []))}")
                for row in inc.get("rows", []):
                    vals = ' | '.join(row["values"])
                    print(f"    {row['label']}: {vals}")

            if "balanceSheet" in data:
                bs = data["balanceSheet"]
                print(f"\n  --- balance sheet detail ({bs.get('period', '?')}) ---")
                print(f"    Periods: {' | '.join(bs.get('periods', []))}")
                for row in bs.get("rows", []):
                    vals = ' | '.join(row["values"])
                    print(f"    {row['label']}: {vals}")

            if "cashFlow" in data:
                cf = data["cashFlow"]
                print(f"\n  --- cash flow detail ({cf.get('period', '?')}) ---")
                print(f"    Periods: {' | '.join(cf.get('periods', []))}")
                for row in cf.get("rows", []):
                    vals = ' | '.join(row["values"])
                    print(f"    {row['label']}: {vals}")

            if "profile" in data:
                prof = data["profile"]
                company = prof.get("company", {})
                print(f"\n  --- profile ---")
                if company.get("name"):
                    print(f"    Name: {company['name']}")
                if company.get("address"):
                    print(f"    Address: {company['address']}")
                if company.get("website"):
                    print(f"    Website: {company['website']}")
                if company.get("employees"):
                    print(f"    Employees: {company['employees']}")
                if company.get("phone"):
                    print(f"    Phone: {company['phone']}")
                if company.get("fax"):
                    print(f"    Fax: {company['fax']}")
                if company.get("sector"):
                    print(f"    Sector: {company['sector']}")
                if company.get("industries"):
                    print(f"    Industries: {', '.join(company['industries'])}")
                if company.get("description"):
                    desc = company['description'][:200]
                    print(f"    Description: {desc}...")
                for section in ["overview", "financials", "growth", "perShareInfo", "ratios"]:
                    rows = prof.get(section, [])
                    if rows:
                        print(f"\n    --- {section} ---")
                        for row in rows:
                            print(f"      {row['label']}: {row['value']}")
                div_rows = prof.get("dividendHistory", [])
                if div_rows:
                    print(f"\n    --- dividendHistory ---")
                    for row in div_rows[:5]:
                        print(f"      {row['label']}: {row['value']}")
                    if len(div_rows) > 5:
                        print(f"      ... ({len(div_rows) - 5} more entries)")


if __name__ == "__main__":
    main()
