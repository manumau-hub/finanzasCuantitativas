#!/usr/bin/env python3
"""
Batch fetch de Yahoo Finance con token bucket + ThreadPoolExecutor.

Respeta el rate limit de Yahoo (~2 req/s sostenidos) usando un token bucket
thread-safe. Quote batching: todos los tickers en 1 sola request.

Uso:
    # Test seguro (3 tickers, solo chart, 2 req/s)
    py scripts/batch_fetch.py --tickers AAPL,MSFT,NVDA --chart --rate 2.0

    # Batch completo (quote en 1 request + charts en paralelo)
    py scripts/batch_fetch.py --tickers AAPL,MSFT,NVDA,GOOGL,META,AMZN,TSLA --all --rate 2.0 --workers 4

    # Solo quotes (siempre 1 request, imposible rate-limit)
    py scripts/batch_fetch.py --tickers AAPL,MSFT,NVDA,GOOGL --quote

    # Todo con output a archivo
    py scripts/batch_fetch.py --tickers AAPL,MSFT --all --rate 2.0 --output data/batch.json
"""

import argparse
import functools
import json
import os
import sys
import threading
import time as _time
from concurrent.futures import ThreadPoolExecutor, as_completed

from curl_cffi import requests

BASE = "https://query1.finance.yahoo.com"
FALLBACK = "https://query2.finance.yahoo.com"

# ---------------------------------------------------------------------------
# Token Bucket - thread-safe, con burst
# ---------------------------------------------------------------------------

class TokenBucket:
    """Token bucket rate limiter. Thread-safe.

    Por defecto: 2 tokens/s, max 5 tokens (burst). Esto significa que
    pueden dispararse hasta 5 requests instantaneas, luego se estabiliza
    a 2 req/s. Yahoo tolera esto sin problemas (yfinance no tiene
    rate limiter y manda N requests simultaneas sin throttling).
    """
    def __init__(self, rate: float = 2.0, burst: int = 5):
        self.rate = rate
        self.burst = burst
        self.tokens = float(burst)
        self.last = _time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, block: bool = True):
        """Adquiere 1 token. Bloquea hasta que haya disponible."""
        if block:
            while True:
                needed = self._try_consume()
                if needed <= 0:
                    return
                _time.sleep(min(needed, 0.1))

    def _try_consume(self) -> float:
        """Intenta consumir 1 token. Retorna segundos hasta que haya disponible."""
        with self._lock:
            now = _time.monotonic()
            elapsed = now - self.last
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last = now
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return 0.0
            return (1.0 - self.tokens) / self.rate

# ---------------------------------------------------------------------------
# Sesion + crumb
# ---------------------------------------------------------------------------

class SessionPool:
    """Pool de sesiones curl_cffi con crumb. Thread-safe."""
    def __init__(self, size: int = 2):
        self._sessions = [self._new_session() for _ in range(size)]
        self._counter = 0
        self._lock = threading.Lock()

    @staticmethod
    def _new_session():
        s = requests.Session(impersonate="chrome")
        try:
            s.get("https://fc.yahoo.com", timeout=10)
            crumb = s.get(f"{BASE}/v1/test/getcrumb", timeout=10).text.strip()
            s.params = {"crumb": crumb}
        except Exception:
            s.params = {}
        return s

    def get(self):
        with self._lock:
            s = self._sessions[self._counter % len(self._sessions)]
            self._counter += 1
            return s

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

def fetch_quote(session, tickers):
    """v7/finance/quote - batch de todos los tickers en 1 request."""
    symbols = ",".join(tickers)
    url = f"{BASE}/v7/finance/quote"
    for attempt in range(3):
        resp = session.get(url, params={"symbols": symbols}, timeout=15)
        if resp.status_code == 429:
            _time.sleep(2 ** attempt)
            continue
        resp.raise_for_status()
        return resp.json()
    raise Exception(f"Rate limited after 3 retries: quote batch")


def fetch_chart(session, ticker, range_="1y", interval="1d", events="div,splits"):
    """v8/finance/chart - OHLCV historico. No requiere crumb."""
    params = {"range": range_, "interval": interval, "events": events}
    for attempt in range(3):
        resp = session.get(f"{BASE}/v8/finance/chart/{ticker}",
                           params=params, timeout=15)
        if resp.status_code == 429:
            _time.sleep(2 ** attempt)
            continue
        resp.raise_for_status()
        return resp.json()
    raise Exception(f"Rate limited after 3 retries: chart {ticker}")


def fetch_quote_summary(session, ticker, modules):
    """v10/finance/quoteSummary - fundamentos."""
    url = f"{BASE}/v10/finance/quoteSummary/{ticker}"
    params = {"modules": ",".join(modules)}
    for attempt in range(3):
        resp = session.get(url, params=params, timeout=15)
        if resp.status_code == 429:
            _time.sleep(2 ** attempt)
            continue
        resp.raise_for_status()
        return resp.json()
    raise Exception(f"Rate limited after 3 retries: summary {ticker}")


def fetch_options(session, ticker):
    """v7/finance/options - cadena de opciones."""
    for attempt in range(3):
        resp = session.get(f"{BASE}/v7/finance/options/{ticker}", timeout=15)
        if resp.status_code == 429:
            _time.sleep(2 ** attempt)
            continue
        resp.raise_for_status()
        return resp.json()
    raise Exception(f"Rate limited after 3 retries: options {ticker}")


def fetch_search(ticker):
    """v1/finance/search - busqueda + noticias. Sin crumb."""
    url = f"{BASE}/v1/finance/search"
    params = {"q": ticker, "quotesCount": 3, "newsCount": 5}
    resp = requests.get(url, params=params, impersonate="chrome", timeout=15)
    resp.raise_for_status()
    return resp.json()

# ---------------------------------------------------------------------------
# Worker - procesa un ticker individual (chart, summary, options)
# ---------------------------------------------------------------------------

CORE_MODULES = [
    "assetProfile", "financialData", "defaultKeyStatistics",
    "incomeStatementHistory", "balanceSheetHistory", "cashflowStatementHistory",
    "earnings", "earningsTrend", "recommendationTrend",
    "calendarEvents", "price", "summaryDetail"
]

def worker(ticker, args, bucket, session_pool):
    """Procesa todos los endpoints requeridos para UN ticker."""
    result = {"ticker": ticker, "ok": {}, "error": {}}
    session = session_pool.get()

    if args.chart:
        try:
            bucket.acquire()
            data = fetch_chart(session, ticker, args.range, args.interval)
            n_bars = len(data.get("chart", {}).get("result", [{}])[0].get("timestamp", []))
            result["ok"]["chart"] = {"bars": n_bars}
        except Exception as e:
            result["error"]["chart"] = str(e)

    if args.fundamentals:
        try:
            bucket.acquire()
            data = fetch_quote_summary(session, ticker, args.modules or CORE_MODULES)
            result["ok"]["fundamentals"] = True
        except Exception as e:
            result["error"]["fundamentals"] = str(e)

    if args.options:
        try:
            bucket.acquire()
            data = fetch_options(session, ticker)
            opt_res = data.get("optionChain", {}).get("result", [{}])[0]
            n_exp = len(opt_res.get("expirationDates", []))
            result["ok"]["options"] = {"expirations": n_exp}
        except Exception as e:
            result["error"]["options"] = str(e)

    if args.search:
        try:
            data = fetch_search(ticker)
            n_news = len(data.get("news", []))
            result["ok"]["search"] = {"news": n_news}
        except Exception as e:
            result["error"]["search"] = str(e)

    return result

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Batch fetch Yahoo Finance con rate limiting + paralelismo."
    )
    parser.add_argument("--tickers", "-t", required=True,
                        help="Tickers separados por coma, ej: AAPL,MSFT,NVDA")
    parser.add_argument("--output", "-o", default=None,
                        help="Archivo JSON de salida")
    parser.add_argument("--rate", type=float, default=2.0,
                        help="Tokens/segundo del rate limiter (default: 2.0)")
    parser.add_argument("--burst", type=int, default=5,
                        help="Max tokens acumulables (default: 5)")
    parser.add_argument("--workers", "-w", type=int, default=4,
                        help="Max workers en ThreadPoolExecutor (default: 4)")
    parser.add_argument("--range", default="1y",
                        help="Rango del chart: 1d..max (default: 1y)")
    parser.add_argument("--interval", default="1d",
                        help="Intervalo del chart (default: 1d)")
    parser.add_argument("--modules", default=None,
                        help="Modulos de quoteSummary separados por coma")

    # Que endpoints ejecutar
    parser.add_argument("--all", action="store_true",
                        help="Todos los endpoints")
    parser.add_argument("--chart", action="store_true",
                        help="Incluir historico OHLCV")
    parser.add_argument("--quote", action="store_true",
                        help="Incluir quote batch (todos los tickers en 1 request)")
    parser.add_argument("--fundamentals", action="store_true",
                        help="Incluir fundamentals (1 req por ticker)")
    parser.add_argument("--options", action="store_true",
                        help="Incluir opciones (1 req por ticker)")
    parser.add_argument("--search", action="store_true",
                        help="Incluir busqueda + noticias (1 req por ticker)")

    args = parser.parse_args()

    if args.all:
        args.chart = True
        args.quote = True
        args.fundamentals = True
        args.options = True
        args.search = True

    tickers = [t.strip().upper() for t in args.tickers.split(",")]

    if args.modules:
        args.modules = [m.strip() for m in args.modules.split(",")]
    else:
        args.modules = CORE_MODULES

    bucket = TokenBucket(rate=args.rate, burst=args.burst)
    session_pool = SessionPool(size=min(args.workers, 4))

    output = {
        "meta": {
            "tickers": tickers,
            "rate": args.rate,
            "burst": args.burst,
            "workers": args.workers,
            "timestamp": _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime()),
            "note": "Datos obtenidos de la API no oficial de Yahoo Finance."
        },
        "quote": None,
        "tickers": {},
        "summary": {
            "total": len(tickers),
            "ok": 0,
            "errors": 0
        }
    }

    # --- Fase 1: Quote batch (1 request para TODOS los tickers) ---
    if args.quote:
        print(f">> Quote batch ({len(tickers)} tickers)...")
        try:
            session = session_pool.get()
            data = fetch_quote(session, tickers)
            output["quote"] = data
            results = data.get("quoteResponse", {}).get("result", [])
            for q in results:
                sym = q.get("symbol", "?")
                p = q.get("regularMarketPrice", "N/A")
                chg = q.get("regularMarketChangePercent", 0)
                print(f"   {sym}: ${p} ({chg:+.2f}%)")
            output["summary"]["quotes_ok"] = len(results)
        except Exception as e:
            print(f"   ERR quote batch: {e}")
            output["summary"]["quote_error"] = str(e)

    # --- Fase 2: Paralelo por ticker (chart, fundamentals, options) ---
    endpoints_after_quote = sum([args.chart, args.fundamentals, args.options, args.search])
    if endpoints_after_quote == 0:
        pass  # solo quote
    else:
        print(f">> Procesando {len(tickers)} tickers con {args.workers} workers, rate={args.rate} req/s...")
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(worker, t, args, bucket, session_pool): t
                for t in tickers
            }
            for future in as_completed(futures):
                t = futures[future]
                try:
                    result = future.result()
                    output["tickers"][t] = result
                    n_ok = len(result["ok"])
                    n_err = len(result["error"])
                    if n_err > 0:
                        output["summary"]["errors"] += 1
                        print(f"   {t}: {n_ok} ok, {n_err} errors")
                    else:
                        output["summary"]["ok"] += 1
                        print(f"   {t}: {n_ok} ok")
                except Exception as e:
                    output["tickers"][t] = {"ticker": t, "error": str(e)}
                    output["summary"]["errors"] += 1
                    print(f"   {t}: EXCEPTION {e}")

    # --- Output ---
    outpath = args.output or f"batch_{len(tickers)}t.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    size_kb = os.path.getsize(outpath) / 1024
    print(f"\nGuardado: {outpath} ({size_kb:.0f} KB)")
    print(f"Tickers: {output['summary']['ok']} ok / {output['summary']['errors']} errors")


if __name__ == "__main__":
    main()
