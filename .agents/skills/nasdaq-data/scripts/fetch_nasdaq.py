"""
Nasdaq.com Data Fetcher — Internal REST APIs + HTML fallback.
Sin API key. Usa las APIs internas de Nasdaq.com y api.nasdaq.com.

Endpoints disponibles via API REST:
  - info                  Company info, precio real-time, key stats
  - chart                 OHLCV histórico
  - short-interest        Short interest histórico
  - financials            Income Statement, Balance Sheet, Cash Flow, Ratios
  - institutional-holdings Institutional holdings (13F)
  - holdings              ETFs donde el stock es Top 10 Holding
  - etf-holdings          Top 10 Holdings de un ETF
  - company-profile       Descripción, sector, dirección
  - dividends             Dividendos
  - eps                   EPS histórico + upcoming por ticker
  - insider-trades        Insider trading summary + transactions
  - option-chain          Opciones
  - news                  Últimas noticias
  - screener              Screener de acciones
  - screener-etf          Screener de ETFs
  - ipo-calendar          IPO / SPO calendar
  - earnings-calendar     Earnings calendar (EPS estimado, fecha)
  - economic-calendar     Economic calendar: actual vs consensus vs previous
  - dividend-calendar     Dividendos (ex-date, pay-date, rate)
  - splits-calendar       Stock splits

Uso:
    python fetch_nasdaq.py info NVDA
    python fetch_nasdaq.py short-interest GGAL
    python fetch_nasdaq.py chart NVDA --from 2025-01-01 --to 2026-06-04
    python fetch_nasdaq.py financials NVDA
    python fetch_nasdaq.py institutional-holdings NVDA
    python fetch_nasdaq.py holdings NVDA             # ETFs donde NVDA es top 10 holding
    python fetch_nasdaq.py etf-holdings SPY          # Top 10 holdings del ETF SPY
    python fetch_nasdaq.py dividends NVDA
    python fetch_nasdaq.py eps NVDA                  # EPS histórico + upcoming
    python fetch_nasdaq.py insider-trades NVDA       # Insider trading summary + transacciones
    python fetch_nasdaq.py insider-trades NVDA --type all --limit 20
    python fetch_nasdaq.py option-chain NVDA
    python fetch_nasdaq.py news NVDA --limit 5
    python fetch_nasdaq.py screener --exchange nasdaq --limit 10
    python fetch_nasdaq.py screener-etf --limit 5
    python fetch_nasdaq.py ipo-calendar              # IPO calendar global
    python fetch_nasdaq.py ipo-calendar --type spo   # SPO calendar
    python fetch_nasdaq.py ipo-calendar --date 2026-05 --type ipo
    python fetch_nasdaq.py earnings-calendar          # Earnings calendar global
    python fetch_nasdaq.py economic-calendar          # Economic calendar
    python fetch_nasdaq.py economic-calendar --date 2026-06-04
    python fetch_nasdaq.py dividend-calendar          # Dividend calendar
    python fetch_nasdaq.py splits-calendar            # Stock splits calendar
    python fetch_nasdaq.py all NVDA                    # Todo lo disponible
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import requests

log = logging.getLogger("nasdaq")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

API_BASE = "https://api.nasdaq.com"
WWW_BASE = "https://www.nasdaq.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nasdaq.com/",
}
HTML_HEADERS = {**HEADERS, "Accept": "text/html,application/xhtml+xml"}


# ── API Clients ────────────────────────────────────────────────────────────


def _get(url: str, params: dict = None) -> dict:
    """GET request with error handling."""
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def _get_html(url: str) -> str:
    """GET HTML page."""
    r = requests.get(url, headers=HTML_HEADERS, timeout=15)
    r.raise_for_status()
    return r.text


# ── Endpoints ──────────────────────────────────────────────────────────────


def fetch_info(ticker: str) -> dict:
    """Company info, price, key stats."""
    url = f"{API_BASE}/api/quote/{ticker}/info?assetclass=stocks"
    return _get(url)


def fetch_short_interest(ticker: str) -> dict:
    """Short interest history."""
    url = f"{API_BASE}/api/quote/{ticker}/short-interest?assetclass=stocks"
    return _get(url)


def fetch_chart(ticker: str, fromdate: str = None, todate: str = None) -> dict:
    """OHLCV chart data."""
    if not fromdate:
        fromdate = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if not todate:
        todate = datetime.now().strftime("%Y-%m-%d")
    url = f"{API_BASE}/api/quote/{ticker}/chart"
    return _get(url, {"assetclass": "stocks", "fromdate": fromdate, "todate": todate})


def fetch_financials(ticker: str) -> dict:
    """Financial statements: Income, Balance Sheet, Cash Flow, Ratios."""
    url = f"{API_BASE}/api/company/{ticker}/financials"
    return _get(url)


def fetch_institutional_holdings(ticker: str) -> dict:
    """Institutional holdings (13F filings)."""
    url = f"{API_BASE}/api/company/{ticker}/institutional-holdings"
    return _get(url)


def fetch_company_profile(ticker: str) -> dict:
    """Company profile: description, sector, address, phone."""
    url = f"{API_BASE}/api/company/{ticker}/company-profile"
    return _get(url)


def fetch_dividends(ticker: str) -> dict:
    """Dividend data."""
    url = f"{API_BASE}/api/quote/{ticker}/dividends?assetclass=stocks"
    return _get(url)


def fetch_eps(ticker: str) -> dict:
    """EPS historical + upcoming by ticker."""
    url = f"{API_BASE}/api/quote/{ticker}/eps"
    return _get(url)


def fetch_insider_trades(
    ticker: str,
    limit: int = 100,
    type: str = "all",
    sort_column: str = "lastDate",
    sort_order: str = "DESC",
) -> dict:
    """Insider trades: summary (3/12 months) + transaction table."""
    url = f"{API_BASE}/api/company/{ticker}/insider-trades"
    return _get(url, {
        "limit": limit,
        "type": type,
        "sortColumn": sort_column,
        "sortOrder": sort_order,
    })


def fetch_option_chain(ticker: str) -> dict:
    """Options chain."""
    url = f"{API_BASE}/api/quote/{ticker}/option-chain?assetclass=stocks"
    return _get(url)


def fetch_news(ticker: str, limit: int = 10) -> dict:
    """Latest news articles for a ticker."""
    url = f"{WWW_BASE}/api/news/topic/articlebysymbol"
    return _get(url, {"q": f"{ticker}|STOCKS", "offset": 0, "limit": limit})


def fetch_holdings(ticker: str) -> dict:
    """ETFs where this stock is a Top 10 Holding."""
    url = f"{API_BASE}/api/company/{ticker}/holdings?assetclass=stocks"
    return _get(url)


def fetch_etf_holdings(ticker: str) -> dict:
    """Top 10 Holdings of an ETF."""
    url = f"{API_BASE}/api/company/{ticker}/holdings?assetclass=etf"
    return _get(url)


def fetch_screener_etf(limit: int = 25, offset: int = 0) -> dict:
    """ETF screener - list all ETFs."""
    url = f"{API_BASE}/api/screener/etf"
    return _get(url, {"tableonly": "true", "limit": limit, "offset": offset})


def fetch_screener(
    exchange: str = "nasdaq", limit: int = 25, offset: int = 0
) -> dict:
    """Stock screener."""
    url = f"{API_BASE}/api/screener/stocks"
    return _get(
        url,
        {
            "tableonly": "true",
            "limit": limit,
            "offset": offset,
            "exchange": exchange,
        },
    )


# ── Calendars ──────────────────────────────────────────────────────────────


def fetch_ipo_calendar(type: str = None, date: str = None) -> dict:
    """IPO/SPO calendar: upcoming, priced, filed, withdrawn."""
    url = f"{API_BASE}/api/ipo/calendar"
    params = {}
    if type: params['type'] = type
    if date: params['date'] = date
    return _get(url, params)


def fetch_earnings_calendar(date: str = None) -> dict:
    """Earnings calendar with EPS estimates, dates."""
    url = f"{API_BASE}/api/calendar/earnings"
    params = {}
    if date: params['date'] = date
    return _get(url, params)


def fetch_economic_calendar(date: str = None) -> dict:
    """Economic calendar: events, actual vs consensus vs previous."""
    url = f"{API_BASE}/api/calendar/economicevents"
    params = {}
    if date: params['date'] = date
    return _get(url, params)


def fetch_dividend_calendar(date: str = None) -> dict:
    """Dividend calendar."""
    url = f"{API_BASE}/api/calendar/dividends"
    params = {}
    if date: params['date'] = date
    return _get(url, params)


def fetch_splits_calendar() -> dict:
    """Stock splits calendar."""
    url = f"{API_BASE}/api/calendar/splits"
    return _get(url)


# ── CLI ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Nasdaq.com Data Fetcher — REST APIs + HTML fallback"
    )
    parser.add_argument(
        "mode",
        choices=[
            "info",
            "chart",
            "short-interest",
            "financials",
            "institutional-holdings",
            "holdings",
            "etf-holdings",
            "company-profile",
            "dividends",
            "eps",
            "insider-trades",
            "option-chain",
            "news",
            "screener",
            "screener-etf",
            "ipo-calendar",
            "earnings-calendar",
            "economic-calendar",
            "dividend-calendar",
            "splits-calendar",
            "all",
        ],
        help="Datos a obtener",
    )
    parser.add_argument("ticker", nargs="?", help="Ticker symbol (ej: NVDA, GGAL, AAPL)")
    parser.add_argument("--from", dest="fromdate", help="Fecha inicio para chart (YYYY-MM-DD)")
    parser.add_argument("--to", dest="todate", help="Fecha fin para chart (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=10, help="Limite de resultados (default: 10)")
    parser.add_argument("--offset", type=int, default=0, help="Offset para paginacion (default: 0)")
    parser.add_argument(
        "--exchange",
        default="nasdaq",
        help="Exchange para screener (default: nasdaq)",
    )
    parser.add_argument(
        "-o", "--output", help="Guardar output a archivo JSON"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Modo silencioso (solo JSON)"
    )
    parser.add_argument(
        "--type", help="ipo-calendar: ipo|spo | insider-trades: all|buy|sell (default segun contexto)"
    )
    parser.add_argument(
        "--date", help="Fecha para calendarios: YYYY-MM (ipo-calendar) o YYYY-MM-DD (earnings/dividend)"
    )

    args = parser.parse_args()

    if args.quiet:
        log.setLevel(logging.WARNING)

    mode = args.mode
    ticker = args.ticker.upper() if args.ticker else None

    # ── Mode dispatch ──────────────────────────────────────────────────

    result = {}
    try:
        if mode == "info" and ticker:
            result = fetch_info(ticker)
        elif mode == "short-interest" and ticker:
            result = fetch_short_interest(ticker)
        elif mode == "chart" and ticker:
            result = fetch_chart(ticker, args.fromdate, args.todate)
        elif mode == "financials" and ticker:
            result = fetch_financials(ticker)
        elif mode == "institutional-holdings" and ticker:
            result = fetch_institutional_holdings(ticker)
        elif mode == "holdings" and ticker:
            result = fetch_holdings(ticker)
        elif mode == "etf-holdings" and ticker:
            result = fetch_etf_holdings(ticker)
        elif mode == "company-profile" and ticker:
            result = fetch_company_profile(ticker)
        elif mode == "dividends" and ticker:
            result = fetch_dividends(ticker)
        elif mode == "eps" and ticker:
            result = fetch_eps(ticker)
        elif mode == "insider-trades" and ticker:
            t = args.type or "all"
            result = fetch_insider_trades(ticker, limit=args.limit, type=t)
        elif mode == "option-chain" and ticker:
            result = fetch_option_chain(ticker)
        elif mode == "news" and ticker:
            result = fetch_news(ticker, args.limit)
        elif mode == "screener":
            result = fetch_screener(args.exchange, args.limit, args.offset)
        elif mode == "screener-etf":
            result = fetch_screener_etf(args.limit, args.offset)
        elif mode == "ipo-calendar":
            result = fetch_ipo_calendar(type=args.type, date=args.date)
        elif mode == "earnings-calendar":
            result = fetch_earnings_calendar(date=args.date)
        elif mode == "economic-calendar":
            result = fetch_economic_calendar(date=args.date)
        elif mode == "dividend-calendar":
            result = fetch_dividend_calendar(date=args.date)
        elif mode == "splits-calendar":
            result = fetch_splits_calendar()
        elif mode == "all" and ticker:
            result = fetch_all(ticker)
        else:
            parser.print_help()
            sys.exit(1)
    except requests.HTTPError as e:
        log.error(f"HTTP Error: {e}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Error: {e}")
        sys.exit(1)

    # ── Output ─────────────────────────────────────────────────────────

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        log.info(f"Guardado en: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


def fetch_all(ticker: str) -> dict:
    """Fetch all available data for a ticker."""
    log.info(f"Fetching ALL data for {ticker}...")
    result = {"ticker": ticker, "timestamp": datetime.now().isoformat()}

    endpoints = [
        ("info", fetch_info),
        ("short_interest", fetch_short_interest),
        ("holdings", fetch_holdings),
        ("chart", lambda t: fetch_chart(t)),
        ("financials", fetch_financials),
        ("institutional_holdings", fetch_institutional_holdings),
        ("company_profile", fetch_company_profile),
        ("dividends", fetch_dividends),
        ("news", lambda t: fetch_news(t, 5)),
    ]

    for name, func in endpoints:
        try:
            log.info(f"  Fetching {name}...")
            data = func(ticker)
            result[name] = data
            time.sleep(0.3)  # rate limiting
        except Exception as e:
            log.warning(f"  {name}: {e}")
            result[name] = {"error": str(e)}

    return result


if __name__ == "__main__":
    main()
