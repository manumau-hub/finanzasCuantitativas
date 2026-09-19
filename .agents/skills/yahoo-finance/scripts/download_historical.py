"""
Descargar datos históricos OHLCV de Yahoo Finance usando la API v8/chart directa.
Sin dependencia de yfinance — solo requests.

Uso:
    python download_historical.py --tickers AAPL,MSFT --range 1y --interval 1d --output data/
    python download_historical.py --tickers AAPL --period1 1672531200 --period2 1704067200 --interval 1d
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime, timezone

import requests


BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_chart(ticker, period1=None, period2=None, range_=None, interval="1d", events="div,splits"):
    """Fetch raw JSON from v8/chart endpoint."""
    params = {"interval": interval}
    if range_:
        params["range"] = range_
    else:
        if period1:
            params["period1"] = period1
        if period2:
            params["period2"] = period2 or int(time.time())
    if events:
        params["events"] = events

    url = f"{BASE_URL}/{ticker}"
    resp = requests.get(url, params=params, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def parse_chart(data, ticker):
    """Parse JSON de v8/chart a lista de dicts planos."""
    try:
        result = data["chart"]["result"][0]
    except (KeyError, IndexError, TypeError):
        print(f"  ⚠ Sin datos para {ticker}")
        return []

    timestamps = result.get("timestamp", [])
    quotes = result.get("indicators", {}).get("quote", [{}])[0]
    adjclose = result.get("indicators", {}).get("adjclose", [{}])[0]
    events = result.get("events", {})

    rows = []
    for i, ts in enumerate(timestamps):
        row = {
            "ticker": ticker,
            "date": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d"),
            "open": _get(quotes, "open", i),
            "high": _get(quotes, "high", i),
            "low": _get(quotes, "low", i),
            "close": _get(quotes, "close", i),
            "volume": _get(quotes, "volume", i),
            "adjclose": _get(adjclose, "adjclose", i),
        }
        rows.append(row)

    # Agregar dividendos como filas separadas
    if events and "dividends" in events:
        for ts_str, div in events["dividends"].items():
            rows.append({
                "ticker": ticker,
                "date": datetime.fromtimestamp(int(ts_str), tz=timezone.utc).strftime("%Y-%m-%d"),
                "dividend": div.get("amount"),
            })

    return rows


def _get(obj, key, idx):
    """Get value safely from a list at index."""
    try:
        val = obj[key][idx]
        return val if val is not None else ""
    except (IndexError, KeyError, TypeError):
        return ""


def save_csv(rows, output_path, ticker):
    """Save rows to CSV file."""
    if not rows:
        print(f"  ⚠ No hay datos para guardar para {ticker}")
        return

    filename = os.path.join(output_path, f"{ticker}_historical.csv")
    fieldnames = rows[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ {filename} — {len(rows)} filas")


def main():
    parser = argparse.ArgumentParser(description="Descargar históricos OHLCV de Yahoo Finance")
    parser.add_argument("--tickers", required=True, help="Tickers separados por coma, ej: AAPL,MSFT")
    parser.add_argument("--range", default="1mo", help="Rango: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max")
    parser.add_argument("--interval", default="1d", help="Intervalo: 1m, 5m, 15m, 1h, 1d, 1wk, 1mo")
    parser.add_argument("--period1", type=int, help="Timestamp Unix inicio (alternativo a --range)")
    parser.add_argument("--period2", type=int, help="Timestamp Unix fin (alternativo a --range)")
    parser.add_argument("--output", default="data", help="Directorio de salida")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay entre requests (segundos)")

    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)

    tickers = [t.strip().upper() for t in args.tickers.split(",")]

    for ticker in tickers:
        print(f"→ Descargando {ticker} ...")
        try:
            data = fetch_chart(
                ticker,
                period1=args.period1,
                period2=args.period2,
                range_=args.range,
                interval=args.interval,
            )
            rows = parse_chart(data, ticker)
            save_csv(rows, args.output, ticker)
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error en {ticker}: {e}")
        except Exception as e:
            print(f"  ✗ Error inesperado en {ticker}: {e}")

        time.sleep(args.delay)


if __name__ == "__main__":
    main()
