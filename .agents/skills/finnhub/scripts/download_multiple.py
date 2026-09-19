"""
Finnhub Batch Downloader — Descarga batches de datos por categoria (todos endpoints gratuitos).

Uso:
    py download_multiple.py --api-key TU_API_KEY --category quotes --symbols AAPL,MSFT,GOOGL
    py download_multiple.py --api-key TU_API_KEY --category profile --symbols AAPL,MSFT
    py download_multiple.py --api-key TU_API_KEY --category all --symbols AAPL,MSFT,GOOGL,NVDA,TSLA,META
    py download_multiple.py --api-key TU_API_KEY --category news --symbols AAPL --days 30
    py download_multiple.py --api-key TU_API_KEY --category candles --symbols AAPL --format parquet
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("finnhub-batch")

BASE_URL = "https://finnhub.io/api/v1"
REQUEST_DELAY = 1.1

_LAST_REQUEST = 0.0


def _rate_limit():
    global _LAST_REQUEST
    elapsed = time.time() - _LAST_REQUEST
    if elapsed < REQUEST_DELAY:
        time.sleep(REQUEST_DELAY - elapsed)
    _LAST_REQUEST = time.time()


def call_api(endpoint, params, api_key):
    """Llama a Finnhub API con rate limiting."""
    _rate_limit()
    params["token"] = api_key
    url = f"{BASE_URL}/{endpoint}"
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


# ── Categorias de descarga ──────────────────────────────────────────────────

CATEGORIES = {
    "quote": {
        "name": "Cotizaciones en tiempo real",
        "endpoint": "quote",
        "params": lambda sym: {"symbol": sym},
        "parser": lambda data, sym: {
            "symbol": sym,
            "price": data.get("c"),
            "change": data.get("d"),
            "change_pct": data.get("dp"),
            "high": data.get("h"),
            "low": data.get("l"),
            "open": data.get("o"),
            "prev_close": data.get("pc"),
        },
        "free": True,
    },
    "profile": {
        "name": "Perfil de empresa v2",
        "endpoint": "stock/profile2",
        "params": lambda sym: {"symbol": sym},
        "parser": lambda data, sym: data,
        "free": True,
    },
    "peers": {
        "name": "Empresas similares",
        "endpoint": "stock/peers",
        "params": lambda sym: {"symbol": sym},
        "parser": lambda data, sym: {"symbol": sym, "peers": data},
        "free": True,
    },
    "metric": {
        "name": "Metricas financieras",
        "endpoint": "stock/metric",
        "params": lambda sym: {"symbol": sym, "metric": "all"},
        "parser": lambda data, sym: {"symbol": sym, **data.get("metric", {})},
        "free": True,
    },
    "earnings": {
        "name": "Earnings historicos",
        "endpoint": "stock/earnings",
        "params": lambda sym: {"symbol": sym, "limit": 8},
        "parser": lambda data, sym: {"symbol": sym, "earnings": data},
        "free": True,
    },
    "recommendation": {
        "name": "Recomendaciones de analistas",
        "endpoint": "stock/recommendation",
        "params": lambda sym: {"symbol": sym},
        "parser": lambda data, sym: {"symbol": sym, "recommendations": data},
        "free": True,
    },
    "price-target": {
        "name": "Price targets",
        "endpoint": "stock/price-target",
        "params": lambda sym: {"symbol": sym},
        "parser": lambda data, sym: {"symbol": sym, **data},
        "free": True,
    },
    "financials": {
        "name": "Estados financieros (Income)",
        "endpoint": "stock/financials",
        "params": lambda sym: {"symbol": sym, "statement": "ic", "freq": "annual"},
        "parser": lambda data, sym: {"symbol": sym, "financials": data.get("financials", [])},
        "free": True,
    },
    "balance-sheet": {
        "name": "Balance Sheet",
        "endpoint": "stock/financials",
        "params": lambda sym: {"symbol": sym, "statement": "bs", "freq": "annual"},
        "parser": lambda data, sym: {"symbol": sym, "financials": data.get("financials", [])},
        "free": True,
    },
    "cash-flow": {
        "name": "Cash Flow",
        "endpoint": "stock/financials",
        "params": lambda sym: {"symbol": sym, "statement": "cf", "freq": "annual"},
        "parser": lambda data, sym: {"symbol": sym, "financials": data.get("financials", [])},
        "free": True,
    },
    "dividends": {
        "name": "Dividendos",
        "endpoint": "stock/dividend",
        "params": lambda sym: {"symbol": sym, "from": "2020-01-01", "to": datetime.now().strftime("%Y-%m-%d")},
        "parser": lambda data, sym: {"symbol": sym, "dividends": data},
        "free": True,
    },
    "splits": {
        "name": "Splits",
        "endpoint": "stock/split",
        "params": lambda sym: {"symbol": sym, "from": "2020-01-01", "to": datetime.now().strftime("%Y-%m-%d")},
        "parser": lambda data, sym: {"symbol": sym, "splits": data},
        "free": True,
    },
}

CANDLE_CATEGORY = {
    "candles": {
        "name": "Velas OHLCV Diarias",
        "description": "Usa --days para controlar cuantos dias",
        "free": True,
    }
}


def fetch_candles(symbol, api_key, days=90):
    """Descarga velas OHLCV diarias."""
    to_ts = int(time.time())
    from_ts = to_ts - (days * 86400)
    data = call_api("stock/candle", {
        "symbol": symbol, "resolution": "D",
        "from": from_ts, "to": to_ts,
    }, api_key)
    return {"symbol": symbol, "days": days, **data}


def fetch_news(symbol, api_key, days=7):
    """Descarga noticias de empresa."""
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    data = call_api("company-news", {
        "symbol": symbol, "from": from_date, "to": to_date,
    }, api_key)
    return {"symbol": symbol, "from": from_date, "to": to_date, "articles": data[:20]}


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Finnhub Batch Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Categorias disponibles ({len(CATEGORIES)}):
  {', '.join(CATEGORIES.keys())}
  candles, news

Ejemplos:
  py download_multiple.py --api-key KEY --category quote --symbols AAPL,MSFT
  py download_multiple.py --api-key KEY --category candles --symbols AAPL,MSFT --days 30
  py download_multiple.py --api-key KEY --category all --symbols AAPL,MSFT,GOOGL,NVDA
  py download_multiple.py --api-key KEY --category news --symbols AAPL --days 7
        """,
    )
    parser.add_argument("--api-key", default=os.getenv("FINNHUB_API_KEY", ""),
                        help="Finnhub API key (o FINNHUB_API_KEY env var)")
    parser.add_argument("--category", required=True,
                        help=f"Categoria a descargar ({', '.join(list(CATEGORIES.keys()) + ['all', 'candles', 'news'])})")
    parser.add_argument("--symbols", required=True, help="Simbolos separados por coma")
    parser.add_argument("--days", type=int, default=90, help="Dias (para candles, news)")
    parser.add_argument("-o", "--output", help="Archivo de salida JSON (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output JSON a stdout")

    args = parser.parse_args()
    api_key = args.api_key

    if not api_key:
        log.error("API Key no encontrada. Usa --api-key o setea FINNHUB_API_KEY.")
        sys.exit(1)

    symbols = [s.strip().upper() for s in args.symbols.split(",")]
    categories_to_run = list(CATEGORIES.keys()) if args.category == "all" else [args.category]

    results = {}

    for cat in categories_to_run:
        if cat in CATEGORIES:
            info = CATEGORIES[cat]
            log.info(f"[{cat}] {info['name']} ({len(symbols)} simbolos)")

            cat_results = []
            for sym in symbols:
                try:
                    data = call_api(info["endpoint"], info["params"](sym), api_key)
                    parsed = info["parser"](data, sym)
                    cat_results.append(parsed)
                    log.info(f"  [+] {sym}: OK")
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 403:
                        log.warning(f"  [-] {sym}: Premium (requiere plan pago)")
                    else:
                        log.warning(f"  [-] {sym}: Error {e}")
                except Exception as e:
                    log.error(f"  [X] {sym}: {e}")

            if cat_results:
                results[cat] = cat_results
                log.info(f"  -> {len(cat_results)}/{len(symbols)} obtenidos")

        elif cat == "candles":
            log.info(f"[candles] Velas OHLCV ({args.days} dias, {len(symbols)} simbolos)")
            cat_results = []
            for sym in symbols:
                try:
                    data = fetch_candles(sym, api_key, args.days)
                    cat_results.append(data)
                    count = len(data.get("c", []))
                    log.info(f"  [+] {sym}: {count} velas")
                except Exception as e:
                    log.error(f"  [X] {sym}: {e}")
            if cat_results:
                results["candles"] = cat_results

        elif cat == "news":
            log.info(f"[news] Noticias de empresa ({args.days} dias, {len(symbols)} simbolos)")
            cat_results = []
            for sym in symbols:
                try:
                    data = fetch_news(sym, api_key, args.days)
                    count = len(data.get("articles", []))
                    cat_results.append(data)
                    log.info(f"  [+] {sym}: {count} articulos")
                except Exception as e:
                    log.error(f"  [X] {sym}: {e}")
            if cat_results:
                results["news"] = cat_results

        else:
            log.error(f"Categoria desconocida: {cat}")

    # Output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        size = os.path.getsize(args.output)
        log.info(f"Guardado: {args.output} ({size:,} bytes)")
    elif args.json or True:
        print(json.dumps(results, indent=2, default=str))

    # Resumen
    total_cats = len(results)
    total_items = sum(len(v) if isinstance(v, list) else 1 for v in results.values())
    print(f"\n=== Resumen ===", file=sys.stderr)
    print(f"  Categorias: {total_cats}", file=sys.stderr)
    print(f"  Total items: {total_items}", file=sys.stderr)


if __name__ == "__main__":
    main()
