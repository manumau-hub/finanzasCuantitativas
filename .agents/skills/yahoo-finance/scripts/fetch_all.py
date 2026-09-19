#!/usr/bin/env python3
"""
Fetch integral de Yahoo Finance: histórico, quote, fundamentals, opciones, búsqueda y noticias.
Usa requests HTTP directos — sin yfinance ni wrappers.

Uso:
    # Todo lo disponible para un ticker
    python fetch_all.py --ticker AAPL --all

    # Solo histórico con rango personalizado
    python fetch_all.py --ticker MSFT --chart --range 5y --interval 1wk

    # Histórico por timestamps Unix
    python fetch_all.py --ticker TSLA --chart --period1 1609459200 --period2 1704067200

    # Solo quote + fundamentals con módulos específicos
    python fetch_all.py --ticker NVDA --quote --fundamentals --modules financialData,assetProfile

    # Todo + opciones para varios tickers (uno por vez)
    python fetch_all.py --ticker AAPL --all --output data/aapl.json
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

BASE = "https://query1.finance.yahoo.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =========================================================================
# Sesión con autenticación
# =========================================================================

def yahoo_session():
    """Crea una requests.Session con cookie A3 y crumb para endpoints auth."""
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get("https://fc.yahoo.com", timeout=10)
    crumb = s.get(f"{BASE}/v1/test/getcrumb", timeout=10).text.strip()
    s.params = {"crumb": crumb}
    return s


# =========================================================================
# Endpoints
# =========================================================================

def fetch_chart(ticker, range_="1mo", interval="1d", events="div,splits",
                period1=None, period2=None, include_prepost=False):
    """
    v8/finance/chart — Históricos OHLCV.
    No requiere autenticación, sólo User-Agent.
    """
    params = {"interval": interval}
    if range_:
        params["range"] = range_
    if period1:
        params["period1"] = period1
        if period2:
            params["period2"] = period2
        else:
            params["period2"] = int(time.time())
    if events:
        params["events"] = events
    if include_prepost:
        params["includePrePost"] = "true"

    r = requests.get(f"{BASE}/v8/finance/chart/{ticker}",
                     params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def fetch_quote(session, ticker):
    """
    v7/finance/quote — Precio en tiempo real y métricas básicas.
    Requiere crumb.
    """
    r = session.get(f"{BASE}/v7/finance/quote",
                    params={"symbols": ticker}, timeout=15)
    r.raise_for_status()
    return r.json()


def fetch_quote_summary(session, ticker, modules):
    """
    v10/finance/quoteSummary/{ticker} — Fundamentos y datos profundos.
    Requiere crumb.
    """
    r = session.get(
        f"{BASE}/v10/finance/quoteSummary/{ticker}",
        params={"modules": ",".join(modules)},
        timeout=15
    )
    r.raise_for_status()
    return r.json()


def fetch_options(session, ticker, expiration_date=None):
    """
    v7/finance/options/{ticker} — Cadena de opciones.
    Requiere crumb.
    expiration_date: timestamp Unix opcional para una fecha específica.
    """
    url = f"{BASE}/v7/finance/options/{ticker}"
    params = {}
    if expiration_date:
        params["date"] = expiration_date
    r = session.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def fetch_search(ticker, quotes_count=3, news_count=5):
    """
    v1/finance/search — Búsqueda + noticias.
    No requiere autenticación.
    """
    r = requests.get(
        f"{BASE}/v1/finance/search",
        params={"q": ticker, "quotesCount": quotes_count, "newsCount": news_count},
        headers=HEADERS, timeout=15
    )
    r.raise_for_status()
    return r.json()


def fetch_recommendations(session, ticker):
    """
    v6/finance/recommendationsbysymbol/{ticker} — Recomendaciones de analistas.
    Requiere crumb.
    """
    r = session.get(f"{BASE}/v6/finance/recommendationsbysymbol/{ticker}", timeout=15)
    r.raise_for_status()
    return r.json()


def fetch_trending(session=None, country="US"):
    """
    v1/finance/trending/{country} — Trending symbols.
    No requiere autenticación.
    """
    r = requests.get(f"{BASE}/v1/finance/trending/{country}",
                     headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


# =========================================================================
# Módulos disponibles para quoteSummary
# =========================================================================

ALL_MODULES = [
    "assetProfile",              # Perfil de la empresa completo
    "summaryProfile",            # Resumen del perfil
    "financialData",             # Métricas financieras clave
    "defaultKeyStatistics",      # Estadísticas clave (beta, shares, etc.)
    "incomeStatementHistory",    # Estado de resultados histórico
    "incomeStatementHistoryQuarterly",  # Estado de resultados trimestral
    "balanceSheetHistory",       # Balance general histórico
    "balanceSheetHistoryQuarterly",     # Balance general trimestral
    "cashflowStatementHistory",  # Flujo de caja histórico
    "cashflowStatementHistoryQuarterly", # Flujo de caja trimestral
    "earnings",                  # Ganancias históricas
    "earningsHistory",           # Historia de earnings vs estimados
    "earningsTrend",             # Tendencia de earnings
    "recommendationTrend",       # Recomendaciones de analistas
    "upgradeDowngradeHistory",   # Historia de upgrades/downgrades
    "insiderTransactions",       # Transacciones de insider
    "insiderHolders",            # Tenedores insider
    "institutionOwnership",      # Tenencia institucional
    "fundOwnership",             # Tenencia de fondos mutuos
    "majorDirectHolders",        # Mayores tenedores directos
    "majorHoldersBreakdown",     # Desglose de tenedores (%, institutional, insider)
    "secFilings",                # SEC filings
    "calendarEvents",            # Próximos eventos
    "price",                     # Información detallada de precio
    "quoteType",                 # Tipo de instrumento
    "summaryDetail",             # Detalle resumido
    "symbol",                    # Símbolo
    "topHoldings",               # Top holdings (ETFs)
    "fundProfile",               # Perfil del fondo (ETFs)
    "indexTrend",                # Tendencia del índice
    "sectorTrend",               # Tendencia del sector
    "industryTrend",             # Tendencia de la industria
    "netSharePurchaseActivity",  # Actividad neta de recompra
    "esgScore",                  # Score ESG (si disponible)
]

# Módulos esenciales para un fetch rápido
CORE_MODULES = [
    "assetProfile", "financialData", "defaultKeyStatistics",
    "incomeStatementHistory", "balanceSheetHistory", "cashflowStatementHistory",
    "earnings", "earningsTrend", "recommendationTrend",
    "calendarEvents", "price", "summaryDetail"
]


# =========================================================================
# Main
# =========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Fetch integral de Yahoo Finance. Usa requests HTTP directos (sin yfinance)."
    )
    parser.add_argument("--ticker", "-t", required=True,
                        help="Ticker a consultar (ej: AAPL, MSFT, GGAL)")
    parser.add_argument("--output", "-o", default=None,
                        help="Archivo JSON de salida (default: <ticker>_fetch.json)")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Delay entre requests en segundos (default: 0.5)")

    # Qué endpoints ejecutar
    parser.add_argument("--all", action="store_true",
                        help="Fetch de todo lo disponible (chart + quote + all fundamentals + options + search)")
    parser.add_argument("--chart", action="store_true",
                        help="Incluir histórico OHLCV")
    parser.add_argument("--quote", action="store_true",
                        help="Incluir quote en tiempo real")
    parser.add_argument("--fundamentals", action="store_true",
                        help="Incluir fundamentals (quoteSummary)")
    parser.add_argument("--options", action="store_true",
                        help="Incluir cadena de opciones")
    parser.add_argument("--search", action="store_true",
                        help="Incluir búsqueda y noticias")
    parser.add_argument("--recommendations", action="store_true",
                        help="Incluir recomendaciones de analistas")
    parser.add_argument("--trending", action="store_true",
                        help="Incluir trending symbols")

    # Parámetros para chart
    parser.add_argument("--range", default="1y",
                        help="Rango del histórico: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
    parser.add_argument("--interval", default="1d",
                        help="Intervalo: 1m, 2m, 5m, 15m, 30m, 60m, 1h, 1d, 1wk, 1mo")
    parser.add_argument("--period1", type=int, default=None,
                        help="Timestamp Unix inicio (alternativo a --range)")
    parser.add_argument("--period2", type=int, default=None,
                        help="Timestamp Unix fin (alternativo a --range)")

    # Parámetros para fundamentals
    parser.add_argument("--modules", default=None,
                        help="Módulos de quoteSummary separados por coma (default: core)")
    parser.add_argument("--all-modules", action="store_true",
                        help="Fetch de TODOS los módulos de quoteSummary (~33 módulos)")

    # Consola
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Sin salida en consola (sólo errores)")

    args = parser.parse_args()

    # Si --all, habilitar todo
    if args.all:
        args.chart = True
        args.quote = True
        args.fundamentals = True
        args.options = True
        args.search = True
        args.recommendations = True

    ticker = args.ticker.upper()
    results = {
        "ticker": ticker,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {},
        "meta": {
            "note": "Datos obtenidos de la API no oficial de Yahoo Finance. Sin garantías."
        }
    }
    errors = []
    log = [] if args.quiet else print

    def log_msg(msg):
        if not args.quiet:
            print(msg)

    session = None  # lazy init

    # ------ CHART ------
    if args.chart:
        log_msg(f">> Chart ({args.range}, {args.interval})...")
        try:
            data = fetch_chart(ticker, range_=args.range, interval=args.interval,
                               period1=args.period1, period2=args.period2)
            results["endpoints"]["chart"] = data
            n = len(data.get("chart", {}).get("result", [{}])[0].get("timestamp", []))
            log_msg(f"  OK {n} bars")
        except Exception as e:
            errors.append(f"chart: {e}")
            log_msg(f"  ERR {e}")
        time.sleep(args.delay)

    # ------ QUOTE ------
    if args.quote:
        log_msg(">> Quote...")
        try:
            if session is None:
                session = yahoo_session()
            data = fetch_quote(session, ticker)
            results["endpoints"]["quote"] = data
            q = data.get("quoteResponse", {}).get("result", [{}])[0]
            p = q.get("regularMarketPrice", "N/A")
            chg = q.get("regularMarketChangePercent", 0)
            log_msg(f"  OK Price: ${p} ({chg:.2f}%)")
        except Exception as e:
            errors.append(f"quote: {e}")
            log_msg(f"  ERR {e}")
        time.sleep(args.delay)

    # ------ FUNDAMENTALS ------
    if args.fundamentals:
        if args.all_modules:
            modules = ALL_MODULES
        elif args.modules:
            modules = [m.strip() for m in args.modules.split(",")]
        else:
            modules = CORE_MODULES
        log_msg(f">> Fundamentals ({len(modules)} módulos)...")
        try:
            if session is None:
                session = yahoo_session()
            data = fetch_quote_summary(session, ticker, modules)
            results["endpoints"]["quoteSummary"] = data
            fin = data.get("quoteSummary", {}).get("result", [{}])[0]
            profile = fin.get("assetProfile", {})
            summary = profile.get("longBusinessSummary", "N/A")[:100]
            log_msg(f"  OK Company: {summary}...")
            fd = fin.get("financialData", {})
            log_msg(f"    Revenue: {fd.get('totalRevenue',{}).get('fmt','N/A')}  "
                    f"EBITDA: {fd.get('ebitda',{}).get('fmt','N/A')}  "
                    f"PE: {fd.get('trailingPE',{}).get('fmt','N/A')}")
        except Exception as e:
            errors.append(f"fundamentals: {e}")
            log_msg(f"  ERR {e}")
        time.sleep(args.delay)

    # ------ OPTIONS ------
    if args.options:
        log_msg(">> Options...")
        try:
            if session is None:
                session = yahoo_session()
            data = fetch_options(session, ticker)
            results["endpoints"]["options"] = data
            opt_res = data.get("optionChain", {}).get("result", [{}])[0]
            exp = len(opt_res.get("expirationDates", []))
            opts = opt_res.get("options", [])
            nc = len(opts[0].get("calls", [])) if opts else 0
            np_ = len(opts[0].get("puts", [])) if opts else 0
            log_msg(f"  OK {exp} expiration dates, {nc} calls, {np_} puts")
        except Exception as e:
            errors.append(f"options: {e}")
            log_msg(f"  ERR {e}")
        time.sleep(args.delay)

    # ------ SEARCH ------
    if args.search:
        log_msg(">> Search + News...")
        try:
            data = fetch_search(ticker)
            results["endpoints"]["search"] = data
            nn = len(data.get("news", []))
            log_msg(f"  OK {nn} news items")
        except Exception as e:
            errors.append(f"search: {e}")
            log_msg(f"  ERR {e}")
        time.sleep(args.delay)

    # ------ RECOMMENDATIONS ------
    if args.recommendations:
        log_msg(">> Recommendations...")
        try:
            if session is None:
                session = yahoo_session()
            data = fetch_recommendations(session, ticker)
            results["endpoints"]["recommendations"] = data
            log_msg("  OK")
        except Exception as e:
            errors.append(f"recommendations: {e}")
            log_msg(f"  ERR {e}")
        time.sleep(args.delay)

    # ------ TRENDING ------
    if args.trending:
        log_msg(">> Trending...")
        try:
            data = fetch_trending()
            results["endpoints"]["trending"] = data
            nq = len(data.get("finance", {}).get("result", [{}])[0].get("quotes", []))
            log_msg(f"  OK {nq} trending symbols")
        except Exception as e:
            errors.append(f"trending: {e}")
            log_msg(f"  ERR {e}")
        time.sleep(args.delay)

    # ====== GUARDAR ======
    results["errors"] = errors
    results["endpoints_count"] = len(results["endpoints"])

    if args.output:
        outpath = args.output
    else:
        outpath = f"{ticker}_fetch.json"

    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    size_kb = os.path.getsize(outpath) / 1024
    log_msg(f"\n{'='*50}")
    log_msg(f"Guardado en: {outpath}")
    log_msg(f"Endpoints exitosos: {results['endpoints_count']}/{len(errors) + results['endpoints_count']}")
    if errors:
        log_msg(f"Errores ({len(errors)}):")
        for e in errors:
            log_msg(f"  - {e}")
    log_msg(f"Tamano: {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
