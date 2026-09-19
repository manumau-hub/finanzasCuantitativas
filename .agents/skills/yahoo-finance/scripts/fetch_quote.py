"""
Fetch quote + fundamentals de Yahoo Finance usando la API v7/v10 directa.
Sin dependencia de yfinance — solo requests + cookie/crumb.

Uso:
    python fetch_quote.py --tickers AAPL,MSFT --output data/
    python fetch_quote.py --tickers AAPL --modules assetProfile,financialData --json
"""

import argparse
import json
import os
import sys
import time

import requests


BASE = "https://query1.finance.yahoo.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def yahoo_session():
    """Create requests.Session with cookie A3 and crumb."""
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get("https://fc.yahoo.com", timeout=10)
    crumb_resp = s.get(f"{BASE}/v1/test/getcrumb", timeout=10)
    crumb = crumb_resp.text.strip()
    s.params = {"crumb": crumb}
    return s


def fetch_quote(session, tickers):
    """Fetch real-time quote via v7/quote."""
    symbols = ",".join(tickers)
    url = f"{BASE}/v7/finance/quote"
    resp = session.get(url, params={"symbols": symbols})
    resp.raise_for_status()
    return resp.json()


def fetch_quote_summary(session, ticker, modules):
    """Fetch fundamentals via v10/quoteSummary."""
    url = f"{BASE}/v10/finance/quoteSummary/{ticker}"
    resp = session.get(url, params={"modules": ",".join(modules)})
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Fetch quote + fundamentals de Yahoo Finance")
    parser.add_argument("--tickers", required=True, help="Tickers separados por coma, ej: AAPL,MSFT")
    parser.add_argument("--modules", default="assetProfile,financialData,defaultKeyStatistics",
                        help="Módulos de quoteSummary separados por coma")
    parser.add_argument("--output", default="data", help="Directorio de salida")
    parser.add_argument("--json", action="store_true", help="Output a JSON en stdout")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay entre requests (segundos)")

    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)

    tickers = [t.strip().upper() for t in args.tickers.split(",")]
    modules = [m.strip() for m in args.modules.split(",")]

    print("→ Obteniendo sesión con crumb...")
    session = yahoo_session()

    # 1. Quote rápido
    print(f"→ Fetching quote para {', '.join(tickers)}...")
    try:
        quote_data = fetch_quote(session, tickers)
        if args.json:
            print(json.dumps(quote_data, indent=2))
        else:
            outfile = os.path.join(args.output, "quotes.json")
            with open(outfile, "w", encoding="utf-8") as f:
                json.dump(quote_data, f, indent=2)
            print(f"  ✓ quotes.json guardado en {outfile}")

            # Mostrar resumen
            for q in quote_data.get("quoteResponse", {}).get("result", []):
                print(f"  {q['symbol']}: ${q.get('regularMarketPrice', 'N/A')} "
                      f"({q.get('regularMarketChangePercent', 0):.2f}%) "
                      f"vol={q.get('regularMarketVolume', 'N/A')}")
    except Exception as e:
        print(f"  ✗ Error en quote: {e}")

    time.sleep(args.delay)

    # 2. QuoteSummary (fundamentals) por ticker
    for ticker in tickers:
        print(f"\n→ Fetching fundamentals para {ticker}...")
        try:
            summary = fetch_quote_summary(session, ticker, modules)
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                outfile = os.path.join(args.output, f"{ticker}_fundamentals.json")
                with open(outfile, "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2)
                print(f"  ✓ {ticker}_fundamentals.json guardado")

                # Mostrar resumen si hay financialData
                result = summary.get("quoteSummary", {}).get("result", [{}])[0]
                fin = result.get("financialData", {})
                if fin:
                    print(f"  Revenue: {fin.get('totalRevenue', {}).get('raw', 'N/A')}")
                    print(f"  EBITDA: {fin.get('ebitda', {}).get('raw', 'N/A')}")
                    print(f"  Profit Margin: {fin.get('profitMargins', {}).get('fmt', 'N/A')}")
        except Exception as e:
            print(f"  ✗ Error en {ticker}: {e}")

        time.sleep(args.delay)


if __name__ == "__main__":
    main()
