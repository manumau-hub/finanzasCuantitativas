"""
CompaniesMarketCap Scraper — Rankings CSV, stock marketcap history, ETF holdings.
Sin API key. Rankings via CSV download, individual pages via HTML parse.

Uso:
    python fetch_cmc.py --rankings                        # Default: marketcap ranking
    python fetch_cmc.py --rankings --metric earnings      # Earnings ranking
    python fetch_cmc.py --rankings --metric revenue       # Revenue ranking
    python fetch_cmc.py --stock NVDA                      # NVDA marketcap history
    python fetch_cmc.py --stock AAPL --output aapl.json
    python fetch_cmc.py --etf SPY --holdings              # SPY ETF holdings
    python fetch_cmc.py --etf VOO --holdings              # VOO holdings
    python fetch_cmc.py --stock AAPL --rankings           # Todo junto
"""

import argparse
import csv
import io
import json
import logging
import re
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

import requests
from bs4 import BeautifulSoup

log = logging.getLogger("cmc")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE = "https://companiesmarketcap.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── Ranking endpoint config ────────────────────────────────────────────────

RANKINGS = {
    "marketcap": {
        "path": "/",
        "csv_column": "marketcap",
        "description": "Market Capitalization",
        "unit": "USD",
    },
    "earnings": {
        "path": "/most-profitable-companies/",
        "csv_column": "earnings_ttm",
        "description": "Earnings (TTM)",
        "unit": "USD",
    },
    "revenue": {
        "path": "/largest-companies-by-revenue/",
        "csv_column": "revenue_ttm",
        "description": "Revenue (TTM)",
        "unit": "USD",
    },
    "employees": {
        "path": "/largest-companies-by-number-of-employees/",
        "csv_column": "employees",
        "description": "Number of Employees",
        "unit": "count",
    },
    "pe_ratio": {
        "path": "/top-companies-by-pe-ratio/",
        "csv_column": "pe_ratio",
        "description": "P/E Ratio",
        "unit": "ratio",
    },
    "operating_margin": {
        "path": "/top-companies-by-operating-margin/",
        "csv_column": "operating_margin_ttm",
        "description": "Operating Margin (TTM)",
        "unit": "percentage",
    },
    "total_assets": {
        "path": "/top-companies-by-total-assets/",
        "csv_column": "total_assets",
        "description": "Total Assets",
        "unit": "USD",
    },
    "net_assets": {
        "path": "/top-companies-by-net-assets/",
        "csv_column": "net_assets",
        "description": "Net Assets",
        "unit": "USD",
    },
    "liabilities": {
        "path": "/companies-with-the-highest-liabilities/",
        "csv_column": "total_liabilities",
        "description": "Total Liabilities",
        "unit": "USD",
    },
    "debt": {
        "path": "/companies-with-the-highest-debt/",
        "csv_column": "total_debt",
        "description": "Total Debt",
        "unit": "USD",
    },
    "cash": {
        "path": "/companies-with-the-highest-cash-on-hand/",
        "csv_column": "cash_on_hand",
        "description": "Cash on Hand",
        "unit": "USD",
    },
    "pb_ratio": {
        "path": "/companies-with-lowest-pb-ratio/",
        "csv_column": "pb_ratio",
        "description": "Price/Book Ratio",
        "unit": "ratio",
    },
    "etfs": {
        "path": "/etfs/largest-etfs-by-marketcap/",
        "csv_column": "marketcap",
        "description": "ETF Market Capitalization",
        "unit": "USD",
    },
}


# ── Scraper ─────────────────────────────────────────────────────────────────

class CMScraper:
    """Scraper for CompaniesMarketCap."""

    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self._name_cache = {}  # ticker -> name

    def _session(self):
        s = requests.Session()
        s.headers.update(HEADERS)
        return s

    def _request(self, url: str) -> str:
        time.sleep(self.delay)
        resp = self._session().get(url, timeout=30)
        resp.raise_for_status()
        return resp.text

    # ── Name resolver (ticker -> slug) ────────────────────────────────

    def _resolve_slug(self, ticker: str) -> tuple:
        """Resolve a ticker to (name, slug) using the ranking CSVs."""
        if ticker in self._name_cache:
            name = self._name_cache[ticker]
            return name, self._name_to_slug(name)

        # Try main marketcap CSV
        txt = self._request(f"{BASE}/?download=csv")
        reader = csv.DictReader(io.StringIO(txt))
        for row in reader:
            sym = row.get("Symbol", "").strip()
            name = row.get("Name", "").strip()
            if sym:
                self._name_cache[sym] = name
                if sym == ticker:
                    return name, self._name_to_slug(name)

        # Try ETF CSV (SPY, VOO, etc. are only in ETF rankings)
        txt = self._request(f"{BASE}/etfs/largest-etfs-by-marketcap/?download=csv")
        reader = csv.DictReader(io.StringIO(txt))
        for row in reader:
            sym = row.get("Symbol", "").strip()
            name = row.get("Name", "").strip()
            if sym:
                self._name_cache[sym] = name
                if sym == ticker:
                    return name, self._name_to_slug(name)

        return ticker, ticker.lower()

    @staticmethod
    def _name_to_slug(name: str) -> str:
        """Convert company name to URL slug."""
        slug = name.lower()
        slug = slug.replace(" & ", "-").replace(" &", "-").replace("& ", "-")
        slug = slug.replace("&", "")  # S&P -> sp, AT&T -> att
        slug = slug.replace(",", "").replace("(", "").replace(")", "")
        slug = slug.replace("'", "").replace(".", "")
        slug = slug.replace(" ", "-")
        slug = re.sub(r"-+", "-", slug).strip("-")
        return slug

    # ── Rankings (CSV) ───────────────────────────────────────────────

    def fetch_ranking(self, metric: str = "marketcap", limit: int = 0) -> dict:
        """Fetch a ranking CSV.

        Returns:
            {
                "metric": "marketcap",
                "description": "Market Capitalization",
                "total_rows": 10852,
                "data": [ { "rank": 1, "name": "NVIDIA", "symbol": "NVDA", ... }, ... ]
            }
        """
        if metric not in RANKINGS:
            raise ValueError(f"Unknown metric '{metric}'. Options: {', '.join(RANKINGS.keys())}")

        cfg = RANKINGS[metric]
        url = f"{BASE}{cfg['path']}?download=csv"
        log.info("Fetching %s ranking: %s", metric, url)

        txt = self._request(url)
        reader = csv.DictReader(io.StringIO(txt))
        rows = list(reader)
        total = len(rows)

        if limit > 0:
            rows = rows[:limit]

        # Parse numeric values and clean up
        data = []
        for row in rows:
            entry = {
                "rank": int(row.get("Rank", 0)) if row.get("Rank", "").strip().isdigit() else None,
                "name": row.get("Name", "").strip(),
                "symbol": row.get("Symbol", "").strip(),
                "price_usd": self._parse_number(row.get("price (USD)", "")),
                "country": row.get("country", "").strip(),
            }
            value = row.get(cfg["csv_column"], "").strip()
            entry["value"] = self._parse_number(value)
            data.append(entry)

        return {
            "metric": metric,
            "description": cfg["description"],
            "unit": cfg["unit"],
            "total_rows": total,
            "data": data,
        }

    # ── Stock marketcap history ──────────────────────────────────────

    def fetch_stock(self, ticker: str) -> dict:
        """Fetch stock marketcap history and metadata.

        Returns:
            {
                "ticker": "NVDA",
                "name": "NVIDIA",
                "slug": "nvidia",
                "marketcap_history": [ { "year": "2026", "marketcap": "$5.396 T", "change": "16.34%" }, ... ],
                "similar_companies": [ { "name": "...", "marketcap": "...", "diff": "...", "country": "..." }, ... ]
            }
        """
        name, slug = self._resolve_slug(ticker)
        url = f"{BASE}/{slug}/marketcap/"
        log.info("Fetching stock page: %s (%s)", ticker, url)

        html = self._request(url)
        soup = BeautifulSoup(html, "html.parser")

        result = {
            "ticker": ticker.upper(),
            "name": name,
            "slug": slug,
            "marketcap_history": [],
            "similar_companies": [],
        }

        # Historical marketcap table
        tables = soup.find_all("table")
        for table in tables:
            thead = table.find("thead")
            if not thead:
                continue
            headers = [c.get_text(strip=True) for c in thead.find_all("th")]
            tbody = table.find("tbody")
            rows = tbody.find_all("tr") if tbody else []

            if "Year" in headers:
                for row in rows:
                    cells = [c.get_text(strip=True) for c in row.find_all("td")]
                    if len(cells) >= 3:
                        result["marketcap_history"].append({
                            "year": cells[0],
                            "marketcap": cells[1],
                            "change": cells[2],
                        })

            elif "Country" in headers or any("Country" in h for h in headers):
                for row in rows:
                    cells = [c.get_text(strip=True) for c in row.find_all("td")]
                    if len(cells) >= 4:
                        # The name cell has ticker concatenated: "MicrosoftMSFT"
                        name_raw = cells[0]
                        result["similar_companies"].append({
                            "name": name_raw,
                            "marketcap": cells[1],
                            "diff": cells[2],
                            "country": cells[3],
                        })

        return result

    # ── ETF holdings ─────────────────────────────────────────────────

    def fetch_etf_holdings(self, ticker: str) -> dict:
        """Fetch ETF holdings."""
        name, slug = self._resolve_slug(ticker)
        url = f"{BASE}/{slug}/holdings/"
        log.info("Fetching ETF holdings: %s (%s)", ticker, url)

        html = self._request(url)
        soup = BeautifulSoup(html, "html.parser")

        result = {
            "ticker": ticker.upper(),
            "name": name,
            "slug": slug,
            "holdings": [],
        }

        tables = soup.find_all("table")
        for table in tables:
            thead = table.find("thead")
            if not thead:
                continue
            headers = [c.get_text(strip=True) for c in thead.find_all("th")]
            tbody = table.find("tbody")
            rows = tbody.find_all("tr") if tbody else []

            if "Weight" in headers or "Ticker" in headers:
                for row in rows:
                    cells = [c.get_text(strip=True) for c in row.find_all("td")]
                    if len(cells) >= 4:
                        result["holdings"].append({
                            "weight_pct": cells[0],
                            "name": cells[1],
                            "ticker": cells[2],
                            "shares_held": self._parse_number(cells[3]),
                        })

        return result

    # ── ETF summary ──────────────────────────────────────────────────

    def fetch_etf_summary(self, ticker: str) -> dict:
        """Fetch ETF summary from the main page."""
        name, slug = self._resolve_slug(ticker)
        url = f"{BASE}/{slug}/"
        log.info("Fetching ETF page: %s (%s)", ticker, url)

        html = self._request(url)
        soup = BeautifulSoup(html, "html.parser")

        result = {
            "ticker": ticker.upper(),
            "name": name,
            "slug": slug,
        }

        h1 = soup.find("h1")
        if h1:
            result["title"] = h1.get_text(strip=True)

        return result

    # ── Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _parse_number(s: str):
        """Parse a number string like '5396923154432' or empty string."""
        s = s.strip()
        if not s:
            return None
        try:
            # Remove commas for integer parsing
            clean = s.replace(",", "")
            if "." in clean:
                return float(clean)
            return int(clean)
        except ValueError:
            return s


# ── CLI ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="CompaniesMarketCap — Rankings, stock history, ETF holdings"
    )
    parser.add_argument("--delay", type=float, default=2.0, help="Delay entre requests (default: 2.0s)")
    parser.add_argument("--output", "-o", default=None, help="Archivo JSON de salida")
    parser.add_argument("--quiet", "-q", action="store_true", help="Modo silencioso")
    parser.add_argument("--limit", type=int, default=0, help="Limitar filas en rankings (default: todas)")

    # Modes
    parser.add_argument("--rankings", action="store_true", help="Fetch ranking list")
    parser.add_argument("--metric", default="marketcap",
                        help=f"Métrica del ranking. Opciones: {', '.join(RANKINGS.keys())}")
    parser.add_argument("--stock", "-s", type=str, help="Ticker de stock para marketcap histórico")
    parser.add_argument("--etf", "-e", type=str, help="Ticker de ETF")
    parser.add_argument("--holdings", action="store_true", help="ETF holdings (con --etf)")

    return parser.parse_args()


def print_summary(data, mode):
    """Print human-readable summary."""
    if mode == "ranking":
        print(f"\nRanking: {data['description']} ({data['metric']})")
        print(f"Total companies: {data['total_rows']:,}")
        print(f"Showing: {len(data['data'])} rows")
        for row in data["data"][:10]:
            val_str = f"{row['value']:,}" if isinstance(row['value'], (int, float)) and row['value'] else str(row['value'] or '-')
            print(f"  #{row['rank']:5d} {row['symbol']:10s} {row['name'][:30]:30s} {val_str:>20s}")

    elif mode == "stock":
        print(f"\nStock: {data['name']} ({data['ticker']})")
        print(f"Marketcap history: {len(data['marketcap_history'])} years")
        for h in data["marketcap_history"][:8]:
            print(f"  {h['year']}: {h['marketcap']} ({h['change']})")
        if len(data['marketcap_history']) > 8:
            print(f"  ... +{len(data['marketcap_history'])-8} more years")

    elif mode == "holdings":
        print(f"\nETF: {data['name']} ({data['ticker']})")
        print(f"Holdings: {len(data['holdings'])} positions")
        for h in data['holdings'][:5]:
            print(f"  {h['weight_pct']:>6s} {h['ticker']:10s} {h['name'][:30]:30s}")
        if len(data['holdings']) > 5:
            print(f"  ... +{len(data['holdings'])-5} more")


def main():
    args = parse_args()
    if args.quiet:
        log.setLevel(logging.WARNING)

    if not any([args.rankings, args.stock, args.etf]):
        args.rankings = True  # default

    try:
        scraper = CMScraper(delay=args.delay)
        outputs = {}

        if args.rankings:
            data = scraper.fetch_ranking(metric=args.metric, limit=args.limit)
            outputs["ranking"] = data
            if not args.quiet:
                print_summary(data, "ranking")

        if args.stock:
            data = scraper.fetch_stock(args.stock)
            outputs["stock"] = data
            if not args.quiet:
                print_summary(data, "stock")

        if args.etf:
            if args.holdings:
                data = scraper.fetch_etf_holdings(args.etf)
                outputs["etf_holdings"] = data
            else:
                data = scraper.fetch_etf_summary(args.etf)
                outputs["etf"] = data
            if not args.quiet and not args.holdings:
                print(f"\nETF: {data['name']} ({data['ticker']})")
            elif not args.quiet:
                print_summary(data, "holdings")

        output_str = json.dumps(outputs, indent=2, ensure_ascii=False)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_str)
            log.info("Output guardado en %s", args.output)
        else:
            print(output_str)

    except requests.RequestException as e:
        log.error("Network error: %s", e)
        sys.exit(1)
    except Exception as e:
        log.error("Error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
