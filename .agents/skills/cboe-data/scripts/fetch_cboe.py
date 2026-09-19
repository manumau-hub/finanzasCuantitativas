"""
CBOE.com Data Fetcher — Public REST APIs.
Sin API key, sin autenticacion.

Endpoints disponibles via API REST:
  - quote                Cotizacion delayed de indices y stocks (VIX, SPX, AAPL, GGAL, etc.)
  - historical           Datos historicos: annual high/low, HV e IV a 30/60/90 dias
  - intraday             Chart intraday 1-min con volumen de opciones (calls/puts)
  - futures              Cadena de futuros (VX, VXM, VA, IBHY, IBIG, IEMD)
  - products             Todos los productos tradables en CBOE
  - lookup               Busqueda de simbolos (ticker + company name)
  - summary              Resumen de mercado equities CBOE (volumen por mercado y tape)
  - most-active          Top 10 mas activos por mercado (equities)
  - options-summary      Resumen de mercado opciones CBOE (volumen por exchange)
  - options-most-active  Top N opciones mas activas (calls/puts por categoria)
  - options-chain        Cadena de opciones completa con greeks (stocks y ETFs)
  - options-directory    Instrumentos listados con opciones (directorio por exchange)
  - futures-products     Productos futuros tradables en CBOE

Uso:
    python fetch_cboe.py quote _VIX
    python fetch_cboe.py quote _SPX
    python fetch_cboe.py quote GGAL
    python fetch_cboe.py quote AAPL
    python fetch_cboe.py historical _VIX
    python fetch_cboe.py historical GGAL
    python fetch_cboe.py intraday _VIX
    python fetch_cboe.py intraday _SPX
    python fetch_cboe.py intraday GGAL
    python fetch_cboe.py futures VX
    python fetch_cboe.py futures VXM
    python fetch_cboe.py futures VA
    python fetch_cboe.py futures IBHY
    python fetch_cboe.py futures IBIG
    python fetch_cboe.py products
    python fetch_cboe.py lookup
    python fetch_cboe.py summary
    python fetch_cboe.py most-active --market bzx
    python fetch_cboe.py most-active --market edgx
    python fetch_cboe.py options-summary
    python fetch_cboe.py options-most-active
    python fetch_cboe.py options-most-active --limit 25
    python fetch_cboe.py options-most-active --limit 50
    python fetch_cboe.py options-chain GGAL
    python fetch_cboe.py options-chain AAPL
    python fetch_cboe.py options-directory
    python fetch_cboe.py options-directory --exchange cboe --sid G
    python fetch_cboe.py options-directory --exchange edgx
    python fetch_cboe.py futures-products
    python fetch_cboe.py all _VIX
"""

import argparse
import json
import logging
import re
import sys
import time
from datetime import datetime

import requests

log = logging.getLogger("cboe")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

CDN_BASE = "https://cdn.cboe.com/api/global/delayed_quotes"
API_BASE = "https://www-api.cboe.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


# ── API Client ─────────────────────────────────────────────────────────────


def _get(url: str, params: dict = None) -> dict:
    """GET request with error handling."""
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


# ── Endpoints ──────────────────────────────────────────────────────────────


def fetch_quote(symbol: str) -> dict:
    """Cotizacion delayed de un indice o stock en CBOE.

    Funciona tanto para indices (con prefijo _) como para stocks.
    Indices: _VIX, _SPX, _RUT, _OEX, _DJX, _XSP, _CBTX, _MBTX, _MXEF, _MXEA
    Stocks: GGAL, AAPL, TSLA, SPY, QQQ, NVDA, etc.

    Args:
        symbol: Simbolo (ej: _VIX, _SPX, GGAL, AAPL)
    """
    url = f"{CDN_BASE}/quotes/{symbol}.json"
    return _get(url)


def fetch_historical(symbol: str) -> dict:
    """Datos historicos anuales: precio high/low, HV e IV a 30/60/90 dias.

    Funciona tanto para indices (con prefijo _) como para stocks.

    Args:
        symbol: Simbolo (ej: _VIX, _SPX, GGAL, AAPL)
    """
    url = f"{CDN_BASE}/historical_data/{symbol}.json"
    return _get(url)


def fetch_intraday(symbol: str) -> dict:
    """Chart intraday 1-min con volumen de opciones.

    Funciona tanto para indices (con prefijo _) como para stocks.

    Args:
        symbol: Simbolo (ej: _VIX, _SPX, GGAL, AAPL)
    """
    url = f"{CDN_BASE}/charts/intraday/{symbol}.json"
    return _get(url)


def fetch_futures(symbol: str) -> dict:
    """Cadena de futuros para un simbolo.

    Args:
        symbol: VX, VXM, VA, IBHY, IBIG, IEMD
    """
    url = f"{API_BASE}/us/futures/api/data/"
    return _get(url, {"symbol": symbol})


def fetch_products() -> dict:
    """Lista de todos los productos tradables en CBOE."""
    url = f"{API_BASE}/tradable_products/data/"
    return _get(url)


def fetch_symbol_lookup(market: str = "bzx") -> dict:
    """Busqueda de simbolos: lista completa de tickers con company name.

    Args:
        market: Mercado (bzx, edgx, etc.)
    """
    url = f"https://ww2.cboe.com/us/equities/market_statistics/book_viewer_2/symbol_lookup_data/"
    return _get(url, {"mkt": market})


def fetch_market_summary() -> dict:
    """Resumen de mercado CBOE: volumen por mercado (BZX, BYX, EDGX, EDGA) y tape (A, B, C)."""
    url = f"{API_BASE}/us/equities/market_statistics/summary_lite/market/data/"
    return _get(url)


def fetch_most_active(market: str = "bzx") -> dict:
    """Top 10 mas activos por mercado (equities).

    Args:
        market: Mercado (bzx, byx, edgx, edga)
    """
    url = f"{API_BASE}/us/equities/market_statistics/most_active/data/10/"
    return _get(url, {"mkts": market})


# Valores de limit aceptados por la API de opciones most-active.
# Cualquier otro valor es ignorado y la API devuelve 25 (default).
OPTIONS_MOST_ACTIVE_LIMITS = [10, 25, 50, 100]

# Categorias devueltas por la API: all, index, equity.
OPTIONS_MOST_ACTIVE_CATEGORIES = ["all", "index", "equity"]


def fetch_options_summary() -> dict:
    """Resumen de mercado opciones CBOE: volumen por exchange (Cboe Options, C2, EDGX, BZX)."""
    url = f"{API_BASE}/us/options/market_statistics/summary_lite/market/data/"
    return _get(url)


def fetch_options_most_active(limit: int = 25) -> dict:
    """Top N opciones mas activas por volumen (calls y puts separados).

    Devuelve 3 categorias: all, index, equity. Cada categoria contiene arrays
    de calls y puts con symbol, expires, strike y volume.

    Args:
        limit: Cantidad de resultados por categoria. Solo se aceptan 10, 25, 50, 100.
               Cualquier otro valor sera ignorado por la API (devuelve 25).
    """
    url = f"{API_BASE}/us/options/market_statistics/most_active/data/"
    params = {"mkt": "cone"}
    if limit in OPTIONS_MOST_ACTIVE_LIMITS:
        params["limit"] = limit
    return _get(url, params)


def fetch_futures_products() -> dict:
    """Lista de productos futuros tradables en CBOE (VX, VXM, VA, IBHY, IBIG, etc.)."""
    url = f"{API_BASE}/us/futures/api/tradable_future_products_data/"
    return _get(url)


def parse_option_ticker(ticker: str) -> dict | None:
    """Decodifica un ticker de opcion CBOE en sus componentes.

    Formato: ROOT + YYMMDD + C/P + 8-digit strike (x1000)
    Ejemplo: GGAL260618C00030000 -> root=GGAL, expiry=2026-06-18, type=call, strike=30.0

    Returns:
        dict con keys: root, expiry, type, strike. None si no match.
    """
    m = re.match(r'^(.+?)(\d{6})([CP])(\d{8})$', ticker)
    if not m:
        return None
    root = m.group(1)
    yymmdd = m.group(2)
    cp = m.group(3)
    strike = int(m.group(4)) / 1000
    expiry = f"20{yymmdd[:2]}-{yymmdd[2:4]}-{yymmdd[4:6]}"
    return {"root": root, "expiry": expiry, "type": "call" if cp == "C" else "put", "strike": strike}


def fetch_options_chain(symbol: str) -> dict:
    """Cadena de opciones completa con greeks para un stock o ETF.

    Devuelve el quote del simbolo + la cadena completa de opciones (calls y puts)
    con bid, ask, iv, delta, gamma, theta, vega, rho, theo, volume, open_interest.
    Funciona para stocks y ETFs (no para indices con prefijo _).

    El ticker de cada opcion sigue el formato ROOT + YYMMDD + C/P + strike*1000.
    Usar parse_option_ticker() para decodificarlo.

    Args:
        symbol: Simbolo del stock/ETF (ej: GGAL, AAPL, BMA, SPY)
    """
    url = f"{CDN_BASE}/options/{symbol}.json"
    return _get(url)


# Exchanges disponibles para options-directory.
OPTIONS_DIRECTORY_EXCHANGES = ["cboe", "edgx"]


def fetch_options_directory(exchange: str = "cboe", sid: str = None, dt: str = None) -> dict:
    """Directorio de instrumentos listados con opciones en CBOE.

    Devuelve la lista de todos los stocks/ETFs/indices que tienen opciones listadas,
    con el nombre de la empresa, el market maker asignado y el post/station.

    Args:
        exchange: Exchange de opciones. 'cboe' (Cboe Options) o 'edgx' (EDGX Options).
        sid: Filtro por letra inicial del company_name (A-Z). Sin sid devuelve todos (~5,500).
        dt: Fecha en formato YYYY-MM-DD. Sin dt usa la fecha mas reciente disponible.
    """
    if exchange == "edgx":
        url = f"{API_BASE}/us/options/symboldir/edgx-equity-index-options/data/"
    else:
        url = f"{API_BASE}/us/options/symboldir/equity-index-options/data/"
    params = {}
    if dt:
        params["dt"] = dt
    if sid:
        params["sid"] = sid.upper()
    return _get(url, params if params else None)


# ── CLI ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="CBOE.com Data Fetcher — Public REST APIs"
    )
    parser.add_argument(
        "mode",
        choices=["quote", "historical", "intraday", "futures", "products", "lookup", "summary",
                 "most-active", "options-summary", "options-most-active", "options-chain",
                 "options-directory", "futures-products", "all"],
        help="Datos a obtener",
    )
    parser.add_argument(
        "symbol",
        nargs="?",
        help="Simbolo (ej: _VIX, _SPX, VX para futuros)",
    )
    parser.add_argument(
        "-o", "--output", help="Guardar output a archivo JSON"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Modo silencioso (solo JSON)"
    )
    parser.add_argument(
        "--market", default="bzx",
        help="Mercado para most-active o lookup (default: bzx). Valores: bzx, byx, edgx, edga"
    )
    parser.add_argument(
        "--limit", type=int, default=25,
        help="Resultados por categoria para options-most-active (default: 25). Solo acepta: 10, 25, 50, 100"
    )
    parser.add_argument(
        "--exchange", default="cboe",
        help="Exchange para options-directory (default: cboe). Valores: cboe, edgx"
    )
    parser.add_argument(
        "--sid", default=None,
        help="Letra inicial del company_name para options-directory (A-Z). Sin filtro devuelve todos"
    )
    parser.add_argument(
        "--date", default=None,
        help="Fecha para options-directory (YYYY-MM-DD). Sin fecha usa la mas reciente"
    )

    args = parser.parse_args()

    if args.quiet:
        log.setLevel(logging.WARNING)

    mode = args.mode
    symbol = args.symbol.upper() if args.symbol else None

    # ── Validacion ─────────────────────────────────────────────────────

    if mode in ("quote", "historical", "intraday", "futures", "options-chain") and not symbol:
        log.error(f"Modo '{mode}' requiere un simbolo")
        sys.exit(1)

    # ── Mode dispatch ──────────────────────────────────────────────────

    result = {}
    try:
        if mode == "quote" and symbol:
            result = fetch_quote(symbol)
        elif mode == "historical" and symbol:
            result = fetch_historical(symbol)
        elif mode == "intraday" and symbol:
            result = fetch_intraday(symbol)
        elif mode == "futures" and symbol:
            result = fetch_futures(symbol)
        elif mode == "products":
            result = fetch_products()
        elif mode == "lookup":
            result = fetch_symbol_lookup(market=args.market)
        elif mode == "summary":
            result = fetch_market_summary()
        elif mode == "most-active":
            result = fetch_most_active(market=args.market)
        elif mode == "options-summary":
            result = fetch_options_summary()
        elif mode == "options-most-active":
            result = fetch_options_most_active(limit=args.limit)
        elif mode == "options-chain" and symbol:
            result = fetch_options_chain(symbol)
        elif mode == "options-directory":
            result = fetch_options_directory(exchange=args.exchange, sid=args.sid, dt=args.date)
        elif mode == "futures-products":
            result = fetch_futures_products()
        elif mode == "all" and symbol:
            result = fetch_all(symbol)
        else:
            parser.print_help()
            sys.exit(1)
    except requests.HTTPError as e:
        log.error(f"HTTP Error: {e}")
        if e.response.status_code == 403:
            log.error(f"El simbolo '{symbol}' no esta disponible en este endpoint.")
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


def fetch_all(symbol: str) -> dict:
    """Fetch all available data for a symbol."""
    log.info(f"Fetching ALL data for {symbol}...")
    result = {"symbol": symbol, "timestamp": datetime.now().isoformat()}

    # Siempre intentamos quote, historical e intraday
    endpoints = [
        ("quote", fetch_quote),
        ("historical", fetch_historical),
        ("intraday", fetch_intraday),
    ]

    # Si el simbolo es un futuro conocido, traemos tambien futuros
    futures_symbols = {"VX", "VXM", "VA", "IBHY", "IBIG", "IEMD"}
    clean_symbol = symbol.lstrip("_")
    if clean_symbol in futures_symbols:
        endpoints.append(("futures", lambda s: fetch_futures(clean_symbol)))

    for name, func in endpoints:
        try:
            log.info(f"  Fetching {name}...")
            data = func(symbol)
            result[name] = data
            time.sleep(0.5)
        except Exception as e:
            log.warning(f"  {name}: {e}")
            result[name] = {"error": str(e)}

    return result


if __name__ == "__main__":
    main()
