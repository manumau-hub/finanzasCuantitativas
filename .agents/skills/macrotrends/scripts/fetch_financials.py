"""
Macrotrends Financial Scraper — Financial statements, ratios, employee count.
15+ years of annual/quarterly data. No API key required.

Uso:
    python fetch_financials.py --ticker NVDA --income
    python fetch_financials.py --ticker AAPL --all
    python fetch_financials.py --ticker MSFT --balance --quarterly
    python fetch_financials.py --ticker NVDA --ratios --quarterly
    python fetch_financials.py --ticker GGAL --employees
    python fetch_financials.py --ticker AAPL --all --output data.json
"""

import argparse
import json
import logging
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

import requests
from bs4 import BeautifulSoup

# ── Config ──────────────────────────────────────────────────────────────────

BASE = "https://www.macrotrends.net"
SEARCH_URL = f"{BASE}/assets/php/ticker_search_list.php"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("macrotrends")

# ── Data models ─────────────────────────────────────────────────────────────

@dataclass
class FinancialData:
    ticker: str
    slug: str
    income_statement: dict = field(default_factory=dict)
    balance_sheet: dict = field(default_factory=dict)
    cash_flow: dict = field(default_factory=dict)
    ratios: dict = field(default_factory=dict)
    employees: list = field(default_factory=list)
    error: Optional[str] = None


# ── Scraper ─────────────────────────────────────────────────────────────────

class MacrotrendsScraper:
    """Scraper for Macrotrends financial data."""

    def __init__(self, delay: float = 3.0):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.delay = delay

    def _request(self, url: str) -> requests.Response:
        """Make HTTP request with rate limiting."""
        time.sleep(self.delay)
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return resp

    # ── Ticker search ───────────────────────────────────────────────────

    def _search_ticker(self, ticker: str) -> Optional[str]:
        """Search for ticker slug via macrotrends search endpoint."""
        try:
            resp = self._request(SEARCH_URL)
            data = resp.json()
            for item in data:
                if item.get("s", "").upper().startswith(ticker.upper() + "/"):
                    return item["s"].split("/")[1]
            # Fallback: try lowercase ticker as slug
            return ticker.lower()
        except Exception as e:
            log.warning("Search failed for %s: %s. Trying lowercase slug.", ticker, e)
            return ticker.lower()

    # ── JSON data extraction (statements, ratios) ───────────────────────

    def _fetch_json_data(self, ticker: str, slug: str, endpoint: str, freq: str = "") -> dict:
        """
        Extract data from macrotrends pages that embed `var originalData = [...]`.
        Returns dict of {field_name: {period: value}}.
        """
        freq_param = f"?freq={freq}" if freq else ""
        url = f"{BASE}/stocks/charts/{ticker}/{slug}/{endpoint}{freq_param}"
        log.info("Fetching %s", url)

        try:
            resp = self._request(url)
            soup = BeautifulSoup(resp.text, "html.parser")

            for script in soup.find_all("script"):
                if script.string and "originalData" in script.string:
                    match = re.search(r"var originalData = (\[.*?\]);", script.string, re.DOTALL)
                    if match:
                        raw = json.loads(match.group(1))
                        result = {}
                        for item in raw:
                            field = re.sub(r"<[^>]+>", "", item["field_name"]).strip()
                            values = {
                                k: v for k, v in item.items()
                                if k not in ("field_name", "popup_icon")
                            }
                            result[field] = values
                        log.info("  -> %d fields, %d periods", len(result),
                                 len(next(iter(result.values()))))
                        return result

            log.warning("  -> No originalData found in %s", url)
            return {}

        except requests.HTTPError as e:
            if e.response.status_code == 429:
                log.error("  -> 429 Rate Limited. Increase --delay.")
            else:
                log.error("  -> HTTP %s: %s", e.response.status_code, url)
            return {}
        except Exception as e:
            log.error("  -> Error: %s", e)
            return {}

    # ── HTML table data extraction (employees) ──────────────────────────

    def _fetch_employees(self, ticker: str, slug: str) -> list:
        """Extract employee count from HTML historical_data_table."""
        url = f"{BASE}/stocks/charts/{ticker}/{slug}/number-of-employees"
        log.info("Fetching %s", url)

        try:
            resp = self._request(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table", class_="historical_data_table")
            if not table:
                log.warning("  -> No employee table found")
                return []

            rows = table.find_all("tr")
            result = []
            for row in rows[1:]:  # skip header
                cells = row.find_all("td")
                if len(cells) >= 2:
                    year = cells[0].get_text(strip=True)
                    count = cells[1].get_text(strip=True)
                    # Parse number from "42,000" format
                    count_num = count.replace(",", "")
                    try:
                        count_num = int(count_num)
                    except ValueError:
                        pass
                    result.append({"year": year, "employees": count_num})

            log.info("  -> %d years of employee data", len(result))
            return result

        except requests.HTTPError as e:
            if e.response.status_code == 429:
                log.error("  -> 429 Rate Limited.")
            else:
                log.error("  -> HTTP %s: %s", e.response.status_code, url)
            return []
        except Exception as e:
            log.error("  -> Error: %s", e)
            return []

    # ── Main fetch ─────────────────────────────────────────────────────

    def fetch_all(self, ticker: str, slug: Optional[str] = None,
                  statements: bool = False, balance: bool = False,
                  cashflow: bool = False, ratios: bool = False,
                  employees: bool = False, quarterly: bool = False) -> FinancialData:
        """Fetch selected financial data for a ticker."""
        # Resolve slug
        if not slug:
            slug = self._search_ticker(ticker)
            log.info("Resolved slug for %s: %s", ticker, slug)

        result = FinancialData(ticker=ticker, slug=slug)
        freq = "Q" if quarterly else ""
        freq_label = "quarterly" if quarterly else "annual"

        # Income Statement
        if statements:
            log.info("--- Income Statement (%s) ---", freq_label)
            if not quarterly:
                result.income_statement["annual"] = self._fetch_json_data(
                    ticker, slug, "financial-statements"
                )
            else:
                result.income_statement["quarterly"] = self._fetch_json_data(
                    ticker, slug, "financial-statements", freq="Q"
                )

        # Balance Sheet
        if balance:
            log.info("--- Balance Sheet (%s) ---", freq_label)
            if not quarterly:
                result.balance_sheet["annual"] = self._fetch_json_data(
                    ticker, slug, "balance-sheet"
                )
            else:
                result.balance_sheet["quarterly"] = self._fetch_json_data(
                    ticker, slug, "balance-sheet", freq="Q"
                )

        # Cash Flow (only annual available on macrotrends)
        if cashflow:
            log.info("--- Cash Flow (annual only) ---")
            result.cash_flow["annual"] = self._fetch_json_data(
                ticker, slug, "cash-flow"
            )
            if quarterly:
                log.info("  (Note: Cash flow quarterly not available on macrotrends)")

        # Ratios
        if ratios:
            log.info("--- Ratios (%s) ---", freq_label)
            if not quarterly:
                result.ratios["annual"] = self._fetch_json_data(
                    ticker, slug, "financial-ratios"
                )
            else:
                result.ratios["quarterly"] = self._fetch_json_data(
                    ticker, slug, "financial-ratios", freq="Q"
                )

        # Employees
        if employees:
            log.info("--- Employees ---")
            result.employees = self._fetch_employees(ticker, slug)

        return result


# ── CLI ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Macrotrends Financial Scraper — statements, ratios, employees"
    )
    parser.add_argument("--ticker", "-t", required=True,
                        help="Ticker, ej: AAPL, MSFT, NVDA, GGAL")
    parser.add_argument("--slug", default=None,
                        help="Slug manual (si el search no funciona)")
    parser.add_argument("--output", "-o", default=None,
                        help="Archivo JSON de salida (default: stdout)")
    parser.add_argument("--delay", type=float, default=3.0,
                        help="Delay entre requests en segundos (default: 3.0)")
    parser.add_argument("--quarterly", action="store_true",
                        help="Usar frecuencia trimestral")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Modo silencioso")

    # Data type flags
    parser.add_argument("--income", action="store_true", help="Income Statement")
    parser.add_argument("--balance", action="store_true", help="Balance Sheet")
    parser.add_argument("--cashflow", action="store_true", help="Cash Flow")
    parser.add_argument("--ratios", action="store_true", help="Financial Ratios")
    parser.add_argument("--employees", action="store_true", help="Employee Count")
    parser.add_argument("--all", action="store_true", help="Todo lo disponible")

    return parser.parse_args()


def print_summary(data: FinancialData):
    """Print a human-readable summary of fetched data."""
    print(f"\n=============== {data.ticker} ({data.slug}) ===============")

    # Income
    for freq_key in ("annual", "quarterly"):
        if freq_key in data.income_statement:
            d = data.income_statement[freq_key]
            periods = list(next(iter(d.values())).keys()) if d else []
            print(f"\nIncome Statement ({freq_key}): {len(d)} fields, {len(periods)} periods")
            if periods:
                print(f"  Periods: {periods[0]} to {periods[-1]}")
            for fname in ("Revenue", "Net Income", "EBITDA", "EPS - Earnings Per Share"):
                if fname in d:
                    vals = list(d[fname].values())
                    print(f"  {fname}: {vals[0]} ({periods[0]}) ... {vals[-1]} ({periods[-1]})")

    # Balance
    for freq_key in ("annual", "quarterly"):
        if freq_key in data.balance_sheet:
            d = data.balance_sheet[freq_key]
            periods = list(next(iter(d.values())).keys()) if d else []
            print(f"\nBalance Sheet ({freq_key}): {len(d)} fields, {len(periods)} periods")
            for fname in ("Cash On Hand", "Total Assets", "Total Liabilities",
                          "Total Shareholders Equity"):
                if fname in d:
                    vals = list(d[fname].values())
                    print(f"  {fname}: {vals[0]} ({periods[0]})")

    # Cash Flow
    if "annual" in data.cash_flow:
        d = data.cash_flow["annual"]
        periods = list(next(iter(d.values())).keys()) if d else []
        print(f"\nCash Flow (annual): {len(d)} fields, {len(periods)} periods")
        for fname in ("Free Cash Flow", "Cash From Operating Activities",
                       "Net Cash From Investing Activities"):
            if fname in d:
                vals = list(d[fname].values())
                print(f"  {fname}: {vals[0]} ({periods[0]})")

    # Ratios
    for freq_key in ("annual", "quarterly"):
        if freq_key in data.ratios:
            d = data.ratios[freq_key]
            periods = list(next(iter(d.values())).keys()) if d else []
            print(f"\nRatios ({freq_key}): {len(d)} ratios, {len(periods)} periods")
            for fname in ("Current Ratio", "ROE - Return On Equity", "Net Profit Margin"):
                if fname in d:
                    vals = list(d[fname].values())
                    print(f"  {fname}: {vals[0]} ({periods[0]})")

    # Employees
    if data.employees:
        print(f"\nEmployees: {len(data.employees)} years")
        for e in data.employees[:5]:
            val = e['employees']
            if isinstance(val, int):
                print(f"  {e['year']}: {val:,}")
            else:
                print(f"  {e['year']}: {val}")
        if len(data.employees) > 5:
            print(f"  ... +{len(data.employees) - 5} more years")

    if data.error:
        print(f"\nX Error: {data.error}")


def main():
    args = parse_args()
    if args.quiet:
        log.setLevel(logging.WARNING)

    # Determine what to fetch
    if args.all:
        args.income = args.balance = args.cashflow = args.ratios = args.employees = True

    if not any([args.income, args.balance, args.cashflow, args.ratios, args.employees]):
        log.error("No data flags specified. Use --income, --balance, --cashflow, --ratios, --employees, or --all")
        sys.exit(1)

    scraper = MacrotrendsScraper(delay=args.delay)
    data = scraper.fetch_all(
        ticker=args.ticker,
        slug=args.slug,
        statements=args.income,
        balance=args.balance,
        cashflow=args.cashflow,
        ratios=args.ratios,
        employees=args.employees,
        quarterly=args.quarterly,
    )

    # Output
    output = {
        "ticker": data.ticker,
        "slug": data.slug,
        "income_statement": data.income_statement,
        "balance_sheet": data.balance_sheet,
        "cash_flow": data.cash_flow,
        "ratios": data.ratios,
        "employees": data.employees,
    }
    output_str = json.dumps(output, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        log.info("Output guardado en %s", args.output)
    else:
        print(output_str)

    # Summary
    if not args.quiet:
        print_summary(data)


if __name__ == "__main__":
    main()
