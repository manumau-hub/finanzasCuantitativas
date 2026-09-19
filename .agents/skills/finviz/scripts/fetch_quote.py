"""
Finviz Quote Scraper — Extrae datos fundamentales, técnicos, noticias e insider trading.

Uso:
    python fetch_quote.py --ticker AAPL
    python fetch_quote.py --ticker AAPL,MSFT --output data.json
    python fetch_quote.py --ticker NVDA --fields fundamentals --news-headlines 10
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

BASE_URL = "https://finviz.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("finviz")


# ── Data models ─────────────────────────────────────────────────────────────

@dataclass
class FinvizQuote:
    ticker: str
    fundamentals: dict = field(default_factory=dict)
    technicians: dict = field(default_factory=dict)
    news: list = field(default_factory=list)
    insider_trading: list = field(default_factory=list)
    error: Optional[str] = None


# ── Scraper ─────────────────────────────────────────────────────────────────

class FinvizScraper:
    """Scraper for Finviz quote pages."""

    def __init__(self, delay: float = 2.0):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.delay = delay

    def _request(self, url: str, params: dict = None) -> requests.Response:
        """Make HTTP request with rate limiting."""
        time.sleep(self.delay)
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp

    # ── Quote page ──────────────────────────────────────────────────────

    def fetch_quote(self, ticker: str, news_count: int = 5) -> FinvizQuote:
        """Fetch all data from finviz.com/quote.ashx for a ticker."""
        quote = FinvizQuote(ticker=ticker)
        url = f"{BASE_URL}/quote.ashx"
        params = {"t": ticker.upper()}

        try:
            resp = self._request(url, params=params)
            soup = BeautifulSoup(resp.text, "html.parser")

            # 1. Fundamentals + Technicians table
            self._parse_snapshot_table(soup, quote)

            # 2. News headlines
            quote.news = self._parse_news(soup, news_count)

            # 3. Insider trading table
            quote.insider_trading = self._parse_insider_trading(soup)

        except requests.RequestException as e:
            quote.error = f"HTTP error: {e}"
            log.error("Error fetching %s: %s", ticker, e)
        except Exception as e:
            quote.error = f"Parse error: {e}"
            log.error("Error parsing %s: %s", ticker, e)

        return quote

    def _parse_snapshot_table(self, soup: BeautifulSoup, quote: FinvizQuote) -> None:
        """
        Parse the main snapshot table with fundamentals and technicals.
        Finviz uses a table with class 'snapshot-table2'.
        Each row has: label | value | label | value | label | value
        """
        table = soup.find("table", class_="snapshot-table2")
        if not table:
            log.warning("Snapshot table not found (structure may have changed)")
            return

        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            # Each row has 6 cells: label1, value1, label2, value2, label3, value3
            for i in range(0, len(cells), 2):
                if i + 1 >= len(cells):
                    break
                label = cells[i].get_text(strip=True)
                value = cells[i + 1].get_text(strip=True)
                if not label or not value:
                    continue

                # Classify as fundamental or technical
                technical_fields = {
                    "RSI (14)", "SMA 20", "SMA 50", "SMA 200",
                    "MACD", "ATR", "BB", "Volatility", "Beta",
                    "20-day", "50-day", "200-day", "Perf Week",
                    "Perf Month", "Perf Quarter", "Perf Half Y",
                    "Perf Year", "Perf YTD", "Change",
                }
                if label in technical_fields:
                    quote.technicians[label] = value
                else:
                    quote.fundamentals[label] = value

        log.info(
            "Parsed %d fundamentals, %d technicians",
            len(quote.fundamentals),
            len(quote.technicians),
        )

    def _parse_news(self, soup: BeautifulSoup, count: int) -> list[dict]:
        """Parse news headlines from the quote page."""
        news = []
        news_table = soup.find("table", class_="fullview-news-outer")
        if not news_table:
            return news

        rows = news_table.find_all("tr")
        for row in rows[:count]:
            try:
                link = row.find("a")
                if not link:
                    continue
                title = link.get_text(strip=True)
                url = link.get("href", "")
                # Date/time is in the first <td>
                date_td = row.find("td")
                date = date_td.get_text(strip=True) if date_td else ""
                news.append({"title": title, "url": url, "date": date})
            except Exception as e:
                log.debug("Error parsing news row: %s", e)

        return news

    def _parse_insider_trading(self, soup: BeautifulSoup) -> list[dict]:
        """Parse insider trading table."""
        insider = []
        # Insider trading is in a table with class 'body-table' or similar
        # It's usually in a section with 'Insider Trading' heading
        tables = soup.find_all("table", class_="body-table")
        for table in tables:
            # Check if this is the insider trading table by looking at headers
            header = table.find("tr")
            if not header:
                continue
            header_text = header.get_text(" ", strip=True)
            if "Insider Trading" in header_text or any(
                h in header_text for h in [" insider ", "trade", "shares"]
            ):
                rows = table.find_all("tr")[1:]  # skip header
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 6:
                        insider.append({
                            "trader": cols[0].get_text(strip=True),
                            "relationship": cols[1].get_text(strip=True),
                            "date": cols[2].get_text(strip=True),
                            "transaction": cols[3].get_text(strip=True),
                            "cost": cols[4].get_text(strip=True),
                            "shares": cols[5].get_text(strip=True),
                        })
        return insider


# ── CLI ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Finviz Quote Scraper — fundamental data, technicals, news, insider trading"
    )
    parser.add_argument(
        "--ticker", "-t",
        required=True,
        help="Ticker(s) separados por coma, ej: AAPL o AAPL,MSFT,GOOGL",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Archivo JSON de salida (default: stdout)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay entre requests en segundos (default: 2.0)",
    )
    parser.add_argument(
        "--news-headlines",
        type=int,
        default=5,
        help="Número de headlines de noticias a extraer (default: 5)",
    )
    parser.add_argument(
        "--fields",
        choices=["all", "fundamentals", "technicals", "news", "insider"],
        default="all",
        help="Qué campos extraer (default: all)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Modo silencioso (solo output JSON)",
    )
    return parser.parse_args()


def filter_quote(quote: FinvizQuote, fields: str) -> dict:
    """Filter quote data based on --fields."""
    data = {"ticker": quote.ticker}
    if quote.error:
        data["error"] = quote.error
        return data

    if fields in ("all", "fundamentals"):
        data["fundamentals"] = quote.fundamentals
    if fields in ("all", "technicals"):
        data["technicals"] = quote.technicians
    if fields in ("all", "news"):
        data["news"] = quote.news
    if fields in ("all", "insider"):
        data["insider_trading"] = quote.insider_trading

    return data


def main():
    args = parse_args()
    if not args.quiet:
        log.setLevel(logging.INFO)

    tickers = [t.strip().upper() for t in args.ticker.split(",")]
    scraper = FinvizScraper(delay=args.delay)

    results = []
    for ticker in tickers:
        if not args.quiet:
            log.info("Fetching %s...", ticker)
        quote = scraper.fetch_quote(ticker, news_count=args.news_headlines)
        filtered = filter_quote(quote, args.fields)
        results.append(filtered)

        if not args.quiet and not quote.error:
            print(f"\n=============== {ticker} ===============")
            if quote.fundamentals:
                print("Fundamentals:")
                for k, v in list(quote.fundamentals.items())[:10]:
                    print(f"  {k:20s} {v}")
                if len(quote.fundamentals) > 10:
                    print(f"  ... and {len(quote.fundamentals) - 10} more fields")
            if quote.technicians:
                print("\nTechnicals:")
                for k, v in list(quote.technicians.items())[:8]:
                    print(f"  {k:20s} {v}")
            if quote.news:
                print(f"\nNews (top {args.news_headlines}):")
                for n in quote.news[:3]:
                    print(f"  - {n['date']} -- {n['title'][:80]}")
            if quote.insider_trading:
                print(f"\nInsider Trades: {len(quote.insider_trading)} transactions")
            if quote.error:
                print(f"\nX Error: {quote.error}")

    output = results if len(results) > 1 else results[0]
    output_str = json.dumps(output, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        if not args.quiet:
            log.info("Output guardado en %s", args.output)
    else:
        print(output_str)


if __name__ == "__main__":
    main()
