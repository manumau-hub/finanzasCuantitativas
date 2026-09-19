"""
MarketWatch Scraper — Quote, financials, SEC filings, analyst estimates, options, historical data.

Uso:
    python fetch_marketwatch.py --ticker AAPL --quote
    python fetch_marketwatch.py --ticker GGAL --all
    python fetch_marketwatch.py --ticker AAPL --income --balance --cashflow
    python fetch_marketwatch.py --ticker MSFT --income --quarterly
    python fetch_marketwatch.py --ticker NVDA --historical
    python fetch_marketwatch.py --ticker AAPL --options
    python fetch_marketwatch.py --ticker AAPL --analyst
    python fetch_marketwatch.py --ticker AAPL --sec-filings
    python fetch_marketwatch.py --ticker AAPL --all --output aapl.json
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

log = logging.getLogger("marketwatch")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE = "https://www.marketwatch.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
}


# ── Data models ─────────────────────────────────────────────────────────────

@dataclass
class MarketWatchData:
    ticker: str
    quote: dict = field(default_factory=dict)
    profile: dict = field(default_factory=dict)
    income_statement: dict = field(default_factory=dict)
    balance_sheet: dict = field(default_factory=dict)
    cash_flow: dict = field(default_factory=dict)
    sec_filings: list = field(default_factory=list)
    analyst_estimates: dict = field(default_factory=dict)
    options: list = field(default_factory=list)
    historical: list = field(default_factory=list)
    error: Optional[str] = None


# ── Scraper ─────────────────────────────────────────────────────────────────

class MarketWatchScraper:
    """Scraper for MarketWatch."""

    def __init__(self, delay: float = 3.0):
        self.delay = delay

    def _session(self):
        """Create a fresh session with full browser headers."""
        s = requests.Session()
        s.headers.update(HEADERS)
        return s

    def _request(self, url: str) -> str:
        """Fetch page with rate limiting and fresh session."""
        time.sleep(self.delay)
        s = self._session()
        resp = s.get(url, timeout=30)
        if resp.status_code == 401:
            raise PermissionError(
                f"401 Unauthorized — MarketWatch bloqueó la request. "
                f"Probá aumentar --delay o esperar unos minutos."
            )
        resp.raise_for_status()
        return resp.text

    # ── Table parsers ───────────────────────────────────────────────────

    def _parse_overflow_table(self, table) -> dict:
        """Parse a table--overflow into {header_periods: [rows]}.
        
        MarketWatch financial tables have structure:
        - Header row: ['ItemItem', '2021', '2022', ...] (headers repeat)
        - Data rows: ['ItemNameItemName', 'val1', 'val2', ...]
        """
        result = {}
        thead = table.find("thead")
        if not thead:
            return result
        
        headers = [c.get_text(strip=True) for c in thead.find_all("th")]
        # Clean headers: "ItemItem" -> "Item"
        if headers:
            clean_first = self._clean_field(headers[0])
            if clean_first in ("item", ""):
                headers[0] = "Item"
        
        # Parse tbody rows
        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]
        
        data_rows = []
        for row in rows:
            cells = row.find_all("td")
            vals = [c.get_text(strip=True) for c in cells]
            if vals:
                # Clean first cell (item name is duplicated)
                vals[0] = self._clean_field(vals[0])
                data_rows.append(vals)
        
        return {
            "headers": headers,
            "rows": data_rows,
        }

    def _parse_value_pairs(self, table) -> dict:
        """Parse a value-pairs table (label/value rows)."""
        result = {}
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if label and value:
                    result[label] = value
        return result

    @staticmethod
    def _clean_field(name: str) -> str:
        """Clean duplicated field names like 'ItemItem' -> 'Item'."""
        if len(name) >= 2 and name[:len(name)//2] == name[len(name)//2:]:
            return name[:len(name)//2]
        return name

    # ── Page scrapers ───────────────────────────────────────────────────

    def _scrape_quote(self, soup: BeautifulSoup, ticker: str) -> dict:
        """Extract quote data from the main page."""
        data = {"ticker": ticker.upper()}
        
        # Company name
        h1 = soup.find("h1", class_="company__name")
        if h1:
            data["company_name"] = h1.get_text(strip=True)
        
        # Price from bg-quote or span.value
        price_el = soup.find("bg-quote", class_="value")
        if not price_el:
            price_el = soup.find("span", class_="value")
        if price_el:
            data["price"] = price_el.get_text(strip=True)
        
        # Change from the quote table (table--primary with Close header)
        tables = soup.find_all("table", class_="table--primary")
        for table in tables:
            thead = table.find("thead")
            if not thead:
                continue
            headers = [c.get_text(strip=True) for c in thead.find_all(["th", "td"])]
            if "Close" in headers:
                tbody = table.find("tbody")
                if tbody:
                    cells = tbody.find_all("td")
                    if len(cells) >= 3:
                        data["close"] = cells[0].get_text(strip=True)
                        data["change"] = cells[1].get_text(strip=True)
                        data["change_pct"] = cells[2].get_text(strip=True)
                break
        
        # Performance data
        perf_tables = soup.find_all("table", class_=re.compile(r"table--primary.*c2"))
        for table in perf_tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    data[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
        
        return data

    def _scrape_profile(self, soup: BeautifulSoup) -> dict:
        """Extract company profile data."""
        data = {}
        vp_tables = soup.find_all("table", class_="value-pairs")
        for table in vp_tables:
            pairs = self._parse_value_pairs(table)
            data.update(pairs)
        
        # Also look for sector/industry
        sectors = soup.find_all("span", class_=re.compile("sector|industry"))
        for s in sectors:
            label = s.get("class", [""])[0]
            data[label] = s.get_text(strip=True)
        
        return data

    def _scrape_financials(self, soup: BeautifulSoup, stmt_type: str, freq: str) -> list:
        """Extract financial statements data."""
        tables = soup.find_all("table", class_="table--overflow")
        results = []
        
        for table in tables:
            header_row = table.find("thead")
            if not header_row:
                continue
            headers = [c.get_text(strip=True) for c in header_row.find_all("th")]
            
            # Determine if this is a financial data table (not a sidebar)
            if not headers or headers[0] not in ("ItemItem", "Item"):
                # Check for 'Item' in any form
                if not any("Item" in h for h in headers[:2]):
                    # Check if first header is empty (sidebar tables)
                    if not headers[0]:
                        continue
            
            parsed = self._parse_overflow_table(table)
            if parsed["rows"]:
                results.append(parsed)
        
        return results

    def _scrape_sec_filings(self, soup: BeautifulSoup) -> list:
        """Extract SEC filings."""
        tables = soup.find_all("table", class_="table--overflow")
        for table in tables:
            header_row = table.find("thead")
            if not header_row:
                continue
            headers = [c.get_text(strip=True) for c in header_row.find_all("th")]
            if any("Filing Date" in h for h in headers):
                parsed = self._parse_overflow_table(table)
                return parsed.get("rows", [])
        return []

    def _scrape_analyst(self, soup: BeautifulSoup) -> dict:
        """Extract analyst estimates."""
        data = {}
        
        # Value-pairs tables: recommendation, target price, etc.
        vp_tables = soup.find_all("table", class_="value-pairs")
        for table in vp_tables:
            pairs = self._parse_value_pairs(table)
            data.update(pairs)
        
        # Overflow tables: estimates data
        overflow_tables = soup.find_all("table", class_="table--overflow")
        estimates = []
        for table in overflow_tables:
            parsed = self._parse_overflow_table(table)
            if parsed["rows"]:
                estimates.append(parsed)
        
        if estimates:
            data["estimates_tables"] = estimates
        
        return data

    def _scrape_options(self, soup: BeautifulSoup) -> list:
        """Extract options chain data."""
        options_data = []
        tables = soup.find_all("table", class_="table--overflow")
        
        for table in tables:
            header_row = table.find("thead")
            if not header_row:
                continue
            headers = [c.get_text(strip=True) for c in header_row.find_all("th")]
            
            # Options tables have "Calls" and "Puts" in headers or a strike price header
            if any("Calls" in h for h in headers) or any("Put" in h for h in headers):
                parsed = self._parse_overflow_table(table)
                
                # Extract expiration from header
                expiration = ""
                for h in headers:
                    m = re.search(r"Expires (.+)", h)
                    if m:
                        expiration = m.group(1)
                        break
                
                options_data.append({
                    "expiration": expiration,
                    "headers": parsed["headers"],
                    "rows": parsed["rows"],
                })
        
        return options_data

    def _scrape_historical(self, soup: BeautifulSoup) -> list:
        """Extract historical price data."""
        tables = soup.find_all("table", class_="table--overflow")
        
        for table in tables:
            header_row = table.find("thead")
            if not header_row:
                continue
            headers = [c.get_text(strip=True) for c in header_row.find_all("th")]
            
            if any(h in headers for h in ["Date", "Open", "High", "Low", "Close"]):
                parsed = self._parse_overflow_table(table)
                return parsed.get("rows", [])
        
        return []

    # ── Main fetch ─────────────────────────────────────────────────────

    def fetch_all(self, ticker: str,
                  quote: bool = False,
                  profile: bool = False,
                  income: bool = False,
                  balance: bool = False,
                  cashflow: bool = False,
                  sec_filings: bool = False,
                  analyst: bool = False,
                  options: bool = False,
                  historical: bool = False,
                  quarterly: bool = False) -> MarketWatchData:
        """Fetch selected MarketWatch data for a ticker."""
        result = MarketWatchData(ticker=ticker.upper())
        t = ticker.upper()
        
        freq_path = "/quarter" if quarterly else ""
        freq_label = "quarterly" if quarterly else "annual"
        
        # ── Quote page ──────────────────────────────────────────────
        if quote:
            log.info("Fetching quote page...")
            html = self._request(f"{BASE}/investing/stock/{t}")
            soup = BeautifulSoup(html, "html.parser")
            result.quote = self._scrape_quote(soup, t)
        
        # ── Company Profile ─────────────────────────────────────────
        if profile:
            log.info("Fetching company profile...")
            html = self._request(f"{BASE}/investing/stock/{t}/company-profile")
            soup = BeautifulSoup(html, "html.parser")
            result.profile = self._scrape_profile(soup)
        
        # ── Income Statement ────────────────────────────────────────
        if income:
            log.info("Fetching income statement (%s)...", freq_label)
            html = self._request(f"{BASE}/investing/stock/{t}/financials/income{freq_path}")
            soup = BeautifulSoup(html, "html.parser")
            tables = self._scrape_financials(soup, "income", freq_label)
            result.income_statement[freq_label] = tables
        
        # ── Balance Sheet ───────────────────────────────────────────
        if balance:
            log.info("Fetching balance sheet (%s)...", freq_label)
            html = self._request(f"{BASE}/investing/stock/{t}/financials/balance-sheet{freq_path}")
            soup = BeautifulSoup(html, "html.parser")
            tables = self._scrape_financials(soup, "balance_sheet", freq_label)
            result.balance_sheet[freq_label] = tables
        
        # ── Cash Flow ───────────────────────────────────────────────
        if cashflow:
            log.info("Fetching cash flow (%s)...", freq_label)
            html = self._request(f"{BASE}/investing/stock/{t}/financials/cash-flow{freq_path}")
            soup = BeautifulSoup(html, "html.parser")
            tables = self._scrape_financials(soup, "cash_flow", freq_label)
            result.cash_flow[freq_label] = tables
        
        # ── SEC Filings ─────────────────────────────────────────────
        if sec_filings:
            log.info("Fetching SEC filings...")
            html = self._request(f"{BASE}/investing/stock/{t}/financials/secfilings")
            soup = BeautifulSoup(html, "html.parser")
            result.sec_filings = self._scrape_sec_filings(soup)
        
        # ── Analyst Estimates ───────────────────────────────────────
        if analyst:
            log.info("Fetching analyst estimates...")
            html = self._request(f"{BASE}/investing/stock/{t}/analystestimates")
            soup = BeautifulSoup(html, "html.parser")
            result.analyst_estimates = self._scrape_analyst(soup)
        
        # ── Options ─────────────────────────────────────────────────
        if options:
            log.info("Fetching options chain...")
            html = self._request(f"{BASE}/investing/stock/{t}/options")
            soup = BeautifulSoup(html, "html.parser")
            result.options = self._scrape_options(soup)
        
        # ── Historical Data ─────────────────────────────────────────
        if historical:
            log.info("Fetching historical data...")
            html = self._request(f"{BASE}/investing/stock/{t}/download-data")
            soup = BeautifulSoup(html, "html.parser")
            result.historical = self._scrape_historical(soup)
        
        return result


# ── CLI ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="MarketWatch Scraper — quotes, financials, SEC filings, analyst estimates, options, historical"
    )
    parser.add_argument("--ticker", "-t", required=True, help="Ticker, ej: AAPL, MSFT, NVDA, GGAL")
    parser.add_argument("--output", "-o", default=None, help="Archivo JSON de salida")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay entre requests (default: 3.0s)")
    parser.add_argument("--quarterly", action="store_true", help="Frecuencia trimestral para financials")
    parser.add_argument("--quiet", "-q", action="store_true", help="Modo silencioso")

    # Data type flags
    parser.add_argument("--quote", action="store_true", help="Quote data (precio, cambio, performance)")
    parser.add_argument("--profile", action="store_true", help="Company profile (ratios, sector)")
    parser.add_argument("--income", action="store_true", help="Income statement")
    parser.add_argument("--balance", action="store_true", help="Balance sheet")
    parser.add_argument("--cashflow", action="store_true", help="Cash flow statement")
    parser.add_argument("--financials", action="store_true", help="Todos los financials (income + balance + cashflow)")
    parser.add_argument("--sec-filings", action="store_true", help="SEC filings")
    parser.add_argument("--analyst", action="store_true", help="Analyst estimates")
    parser.add_argument("--options", action="store_true", help="Options chain")
    parser.add_argument("--historical", action="store_true", help="Historical OHLCV data")
    parser.add_argument("--all", action="store_true", help="Todo lo disponible")

    return parser.parse_args()


def print_summary(data: MarketWatchData):
    """Print human-readable summary."""
    print(f"\n=============== {data.ticker} ===============")
    
    if data.quote:
        q = data.quote
        print(f"\nQuote:")
        print(f"  Company: {q.get('company_name', '-')}")
        print(f"  Price: {q.get('price', q.get('close', '-'))}")
        print(f"  Change: {q.get('change', '-')} ({q.get('change_pct', '-')})")
        for k in ("5 Day", "1 Month", "YTD"):
            if k in q:
                print(f"  {k}: {q[k]}")
    
    if data.profile:
        print(f"\nProfile: {len(data.profile)} fields")
        for k in ("P/E Current", "P/E Ratio (w/ extraordinary items)", 
                   "Revenue/Employee", "Employees"):
            if k in data.profile:
                print(f"  {k}: {data.profile[k]}")
    
    for name, stmt, label in [
        ("Income Statement", data.income_statement, "income"),
        ("Balance Sheet", data.balance_sheet, "balance"),
        ("Cash Flow", data.cash_flow, "cash flow"),
    ]:
        if stmt:
            for freq, tables in stmt.items():
                total_rows = sum(len(t.get("rows", [])) for t in tables)
                print(f"\n{name} ({freq}): {len(tables)} tables, {total_rows} rows")
    
    if data.sec_filings:
        print(f"\nSEC Filings: {len(data.sec_filings)} entries")
        for f in data.sec_filings[:3]:
            print(f"  {f}")
    
    if data.analyst_estimates:
        ae = data.analyst_estimates
        print(f"\nAnalyst Estimates: {len(ae)} fields")
        for k in ("Average Recommendation", "Average Target Price",
                   "High", "Median", "Low"):
            if k in ae:
                print(f"  {k}: {ae[k]}")
    
    if data.options:
        print(f"\nOptions: {len(data.options)} expiration dates")
        for opt in data.options:
            print(f"  {opt['expiration']}: {len(opt['rows'])} strikes")
    
    if data.historical:
        print(f"\nHistorical: {len(data.historical)} trading days")
        if data.historical:
            print(f"  Latest: {data.historical[0]}")
            print(f"  Oldest: {data.historical[-1]}")


def main():
    args = parse_args()
    if args.quiet:
        log.setLevel(logging.WARNING)
    
    if args.all:
        args.quote = args.profile = args.financials = True
        args.sec_filings = args.analyst = args.options = args.historical = True
    if args.financials:
        args.income = args.balance = args.cashflow = True
    
    if not any([args.quote, args.profile, args.income, args.balance, args.cashflow,
                args.sec_filings, args.analyst, args.options, args.historical]):
        log.error("No data flags specified. Use --quote, --profile, --income, --balance, --cashflow, --sec-filings, --analyst, --options, --historical, or --all")
        sys.exit(1)
    
    try:
        scraper = MarketWatchScraper(delay=args.delay)
        data = scraper.fetch_all(
            ticker=args.ticker,
            quote=args.quote,
            profile=args.profile,
            income=args.income,
            balance=args.balance,
            cashflow=args.cashflow,
            sec_filings=args.sec_filings,
            analyst=args.analyst,
            options=args.options,
            historical=args.historical,
            quarterly=args.quarterly,
        )
    except PermissionError as e:
        log.error(e)
        sys.exit(1)
    except requests.RequestException as e:
        log.error("Network error: %s", e)
        sys.exit(1)
    
    # Build output dict
    output = {
        "ticker": data.ticker,
        "quote": data.quote,
        "profile": data.profile,
        "income_statement": data.income_statement,
        "balance_sheet": data.balance_sheet,
        "cash_flow": data.cash_flow,
        "sec_filings": data.sec_filings,
        "analyst_estimates": data.analyst_estimates,
        "options": data.options,
        "historical": data.historical,
    }
    output_str = json.dumps(output, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        log.info("Output guardado en %s", args.output)
    else:
        print(output_str)
    
    if not args.quiet:
        print_summary(data)


if __name__ == "__main__":
    main()
