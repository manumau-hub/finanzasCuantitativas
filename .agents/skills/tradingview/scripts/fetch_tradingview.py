"""
TradingView Data Fetcher — APIs publicas internas sin auth.

TradingView no tiene API publica oficial, pero sus apps web exponen varias APIs
internas accesibles SIN auth y SIN API key. Este script las consolida en una
CLI con ~15 modos.

Endpoints disponibles:

  QUOTE / SCANNER (POST scanner.tradingview.com/{market}/scan):
    - quote SYM            Quote basico (15 columnas)
    - quote-extended SYM   Quote con indicadores + valuacion (~30 columnas)
    - technicals SYM       Solo indicadores tecnicos (RSI, MACD, EMAs, ratings)
    - pivots SYM           Pivots mensuales (Classic, Fibonacci, Camarilla, Woodie, DeMark)
    - financials SYM       Balance + income + cashflow + ratios (~35 columnas)
    - earnings SYM         Earnings pasados + forecast proximo
    - targets SYM          Price targets + analyst recommendations
    - performance SYM      Performance returns (W/1M/3M/6M/Y/YTD/5Y/All)
    - dividends SYM        Historico + yield + payout ratio
    - ownership SYM        Float + institutional + insiders + short interest

  SCANNING / SCREENING (POST scanner.tradingview.com/{market}/scan):
    - screen               Screener con filtros + sort + pagination
    - country COUNTRY      Stocks de un pais especifico (e.g. Argentina)
    - sector SECTOR        Stocks de un sector (Finance, Technology, etc.)
    - market MARKET        Listar stocks de un mercado completo

  SYMBOL SEARCH (GET symbol-search.tradingview.com/symbol_search/v3/):
    - search QUERY         Busqueda con ISIN/CUSIP/CIK/logoid/etc

  NEWS (GET news-headlines.tradingview.com/v2/headlines):
    - news SYM             Headlines por simbolo
    - news-global          Headlines globales del mercado
    - story STORY_PATH     Fetch body completo de una noticia (HTML)

  HTML SCRAPING (GET es.tradingview.com/symbols/{ex}-{sym}/{path}/):
    - subpage SYM PATH     Fetch HTML de cualquier subpage + extrae prs.init-data JSON

  CATALOGOS LOCALES (sin HTTP):
    - columns [grupo]      Listar columnas disponibles (o un grupo concreto)
    - groups               Listar grupos de columnas pre-armados
    - markets              Listar mercados validos

  COMBINADO:
    - all SYM              Combina quote + technicals + financials + earnings +
                           targets + news en 1 dict (6 requests)

Uso:
    py fetch_tradingview.py quote NASDAQ:GGAL
    py fetch_tradingview.py quote-extended NASDAQ:AAPL
    py fetch_tradingview.py technicals NASDAQ:GGAL
    py fetch_tradingview.py pivots NASDAQ:AAPL
    py fetch_tradingview.py financials NASDAQ:GGAL
    py fetch_tradingview.py earnings NYSE:JPM
    py fetch_tradingview.py targets NASDAQ:NVDA
    py fetch_tradingview.py performance NYSE:JPM
    py fetch_tradingview.py dividends NYSE:KO
    py fetch_tradingview.py ownership NASDAQ:NVDA

    py fetch_tradingview.py screen --filter '[["sector","equal","Finance"],["market_cap_basic","greater",100000000000]]' --sort market_cap_basic:desc --limit 10
    py fetch_tradingview.py country Argentina --limit 30
    py fetch_tradingview.py sector Finance --market global --limit 20
    py fetch_tradingview.py market crypto --limit 20

    py fetch_tradingview.py search "GGAL"
    py fetch_tradingview.py search "Apple" --type stocks --exchange NASDAQ
    py fetch_tradingview.py search "BTC" --type crypto

    py fetch_tradingview.py news NASDAQ:GGAL
    py fetch_tradingview.py news NASDAQ:AAPL --lang en
    py fetch_tradingview.py news-global
    py fetch_tradingview.py story /news/DJN_DN20260604009289:0/

    py fetch_tradingview.py subpage NASDAQ:GGAL technicals
    py fetch_tradingview.py subpage NASDAQ:GGAL financials-income-statement

    py fetch_tradingview.py columns                      # todas
    py fetch_tradingview.py columns technicals           # grupo concreto
    py fetch_tradingview.py groups
    py fetch_tradingview.py markets

    py fetch_tradingview.py all NASDAQ:GGAL              # 6 requests combinadas
    py fetch_tradingview.py all NASDAQ:GGAL -o ggal_full.json

    py fetch_tradingview.py quote NASDAQ:GGAL --columns "name,close,RSI,MACD.macd"  # custom
    py fetch_tradingview.py quote NASDAQ:GGAL --market global                       # cambiar market
    py fetch_tradingview.py quote BCBA:GGAL --market argentina                      # arg local
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

log = logging.getLogger("tradingview")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# Forzar UTF-8 en stdout en Windows (la consola cp1252 falla con noticias en
# ingles que tienen caracteres como apostrofes curvos, em-dashes, etc.).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, Exception):
    pass

# ── Hosts ──────────────────────────────────────────────────────────────────

SCANNER_HOST = "https://scanner.tradingview.com"
SYMBOL_SEARCH_HOST = "https://symbol-search.tradingview.com"
NEWS_HOST = "https://news-headlines.tradingview.com"
WEB_HOST = "https://es.tradingview.com"
LOGO_HOST = "https://s3-symbol-logo.tradingview.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Origin": "https://es.tradingview.com",
    "Referer": "https://es.tradingview.com/",
}

# ── Assets locales ─────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"


def load_asset(name: str) -> Any:
    """Carga un JSON del directorio assets/."""
    fp = ASSETS_DIR / name
    if not fp.exists():
        log.warning(f"Asset no encontrado: {fp}")
        return None
    with open(fp, "r", encoding="utf-8") as f:
        return json.load(f)


# Cache los assets al cargar el modulo
_column_groups: dict | None = None
_markets: dict | None = None
_scanner_columns: dict | None = None
_recommend_ratings: dict | None = None


def column_groups() -> dict:
    global _column_groups
    if _column_groups is None:
        _column_groups = load_asset("column_groups.json") or {}
    return _column_groups


def markets() -> dict:
    global _markets
    if _markets is None:
        _markets = load_asset("markets.json") or {}
    return _markets


def scanner_columns() -> dict:
    global _scanner_columns
    if _scanner_columns is None:
        _scanner_columns = load_asset("scanner_columns.json") or {}
    return _scanner_columns


def recommend_ratings() -> dict:
    global _recommend_ratings
    if _recommend_ratings is None:
        _recommend_ratings = load_asset("recommend_ratings.json") or {}
    return _recommend_ratings


# ── HTTP helpers ───────────────────────────────────────────────────────────


def _post(url: str, payload: dict, timeout: int = 30) -> Any:
    """POST con error handling. La API del Scanner siempre devuelve JSON."""
    r = requests.post(url, json=payload, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _get(url: str, params: dict | None = None, timeout: int = 30, as_json: bool = True) -> Any:
    """GET con error handling."""
    r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.json() if as_json else r.text


def _normalize_scanner_response(raw: dict, columns: list[str]) -> dict:
    """Convierte el response columnar del Scanner a dicts por simbolo.

    Input:  {"totalCount": 1, "data": [{"s": "NASDAQ:GGAL", "d": [val0, val1, ...]}]}
    Output: {"totalCount": 1, "data": [{"symbol": "NASDAQ:GGAL", "name": val0, ...}]}
    """
    if not isinstance(raw, dict):
        return raw
    if "data" not in raw:
        return raw
    out_data = []
    for row in raw.get("data", []):
        record: dict[str, Any] = {"symbol": row.get("s")}
        d = row.get("d", []) or []
        for col, val in zip(columns, d):
            record[col] = val
        out_data.append(record)
    return {"totalCount": raw.get("totalCount"), "data": out_data}


# ── Scanner API ────────────────────────────────────────────────────────────


def scanner_scan(
    symbols: list[str] | None = None,
    columns: list[str] | None = None,
    filter_: list[dict] | None = None,
    market: str = "global",
    range_: tuple[int, int] = (0, 100),
    sort: dict | None = None,
    options: dict | None = None,
) -> dict:
    """POST /{market}/scan — el endpoint mas potente de TradingView.

    Args:
        symbols: lista de tickers tipo "NASDAQ:AAPL". Si esta dado, se ignora filter_.
        columns: lista de nombres de columnas. Ver assets/scanner_columns.json.
        filter_: filtros tipo [{"left": "sector", "operation": "equal", "right": "Finance"}].
                 Ver references/SCANNER_FILTERS.md.
        market: mercado (global, america, argentina, brazil, spain, etc).
                Ver assets/markets.json.
        range_: tuple (offset, limit_offset_from). Default (0, 100) = primeros 100.
        sort: {"sortBy": "market_cap_basic", "sortOrder": "desc"}.
        options: {"lang": "en"} u otros opcionales.

    Returns:
        dict {"totalCount": N, "data": [...]} con data normalizada a dicts
        por simbolo (no columnar).
    """
    if columns is None:
        columns = column_groups().get("quote_basic", ["name", "close"])
    payload: dict[str, Any] = {
        "columns": columns,
        "range": list(range_),
    }
    if symbols:
        payload["symbols"] = {"tickers": symbols}
    if filter_:
        payload["filter"] = filter_
    elif "symbols" not in payload:
        payload["filter"] = []
    if sort:
        payload["sort"] = sort
    if options:
        payload["options"] = options

    url = f"{SCANNER_HOST}/{market}/scan"
    log.info(f"POST {url} (cols={len(columns)}, market={market}, range={range_})")
    raw = _post(url, payload)
    return _normalize_scanner_response(raw, columns)


def quote(symbol: str, columns: list[str] | None = None, market: str = "global") -> dict:
    """Quote basico de un simbolo."""
    cols = columns or column_groups()["quote_basic"]
    return scanner_scan(symbols=[symbol], columns=cols, market=market, range_=(0, 1))


def quote_extended(symbol: str, market: str = "global") -> dict:
    """Quote con ~30 columnas: indicadores + valuacion."""
    return scanner_scan(
        symbols=[symbol], columns=column_groups()["quote_extended"],
        market=market, range_=(0, 1),
    )


def technicals(symbol: str, market: str = "global") -> dict:
    """Indicadores tecnicos: RSI, MACD, EMAs, SMAs, ratings."""
    return scanner_scan(
        symbols=[symbol], columns=column_groups()["technicals"],
        market=market, range_=(0, 1),
    )


def pivots(symbol: str, market: str = "global") -> dict:
    """Pivots mensuales (Classic, Fibonacci, Camarilla, Woodie, DeMark)."""
    return scanner_scan(
        symbols=[symbol], columns=column_groups()["pivots"],
        market=market, range_=(0, 1),
    )


def financials(symbol: str, market: str = "global") -> dict:
    """Balance + income + cashflow + ratios."""
    return scanner_scan(
        symbols=[symbol], columns=column_groups()["financials"],
        market=market, range_=(0, 1),
    )


def earnings(symbol: str, market: str = "global") -> dict:
    """Earnings pasados + forecast."""
    return scanner_scan(
        symbols=[symbol], columns=column_groups()["earnings"],
        market=market, range_=(0, 1),
    )


def targets(symbol: str, market: str = "global") -> dict:
    """Price targets + analyst recommendations."""
    return scanner_scan(
        symbols=[symbol], columns=column_groups()["targets"],
        market=market, range_=(0, 1),
    )


def performance(symbol: str, market: str = "global") -> dict:
    """Performance returns (W/1M/3M/6M/Y/YTD/5Y/All) + volatility + beta."""
    return scanner_scan(
        symbols=[symbol], columns=column_groups()["performance"],
        market=market, range_=(0, 1),
    )


def dividends(symbol: str, market: str = "global") -> dict:
    """Dividend yield + DPS + payout ratio + crecimiento."""
    return scanner_scan(
        symbols=[symbol], columns=column_groups()["dividends"],
        market=market, range_=(0, 1),
    )


def ownership(symbol: str, market: str = "global") -> dict:
    """Float + institutional + insiders + short interest."""
    return scanner_scan(
        symbols=[symbol], columns=column_groups()["ownership"],
        market=market, range_=(0, 1),
    )


def screen(
    filter_: list[dict],
    market: str = "global",
    columns: list[str] | None = None,
    sort: dict | None = None,
    limit: int = 30,
    offset: int = 0,
) -> dict:
    """Screener generico con filtros + sort + paginacion."""
    cols = columns or column_groups()["quote_basic"]
    return scanner_scan(
        columns=cols, filter_=filter_, market=market,
        range_=(offset, offset + limit), sort=sort,
    )


def by_country(country: str, market: str = "global", limit: int = 30) -> dict:
    """Stocks de un pais (Argentina, Brazil, USA, Spain, etc)."""
    return screen(
        filter_=[{"left": "country", "operation": "equal", "right": country}],
        market=market, limit=limit,
        sort={"sortBy": "market_cap_basic", "sortOrder": "desc"},
    )


def by_sector(sector: str, market: str = "global", limit: int = 30) -> dict:
    """Stocks de un sector."""
    return screen(
        filter_=[{"left": "sector", "operation": "equal", "right": sector}],
        market=market, limit=limit,
        sort={"sortBy": "market_cap_basic", "sortOrder": "desc"},
    )


def list_market(market: str = "global", limit: int = 30) -> dict:
    """Listar stocks de un mercado completo (sin filtros)."""
    return scanner_scan(
        columns=column_groups()["quote_basic"],
        filter_=[], market=market,
        range_=(0, limit),
        sort={"sortBy": "market_cap_basic", "sortOrder": "desc"},
    )


# ── Symbol Search API ──────────────────────────────────────────────────────


SYMBOL_SEARCH_TYPES = ["stocks", "funds", "futures", "forex", "crypto", "indices", "bonds", "economic", "options"]


def symbol_search(
    query: str,
    search_type: str | None = None,
    exchange: str | None = None,
    lang: str = "en",
    domain: str = "production",
    hl: int = 1,
) -> dict:
    """GET /symbol_search/v3/?text={query}.

    Args:
        query: texto a buscar (ticker, ISIN, CUSIP, nombre empresa).
        search_type: stocks | funds | futures | forex | crypto | indices | bonds | economic | options.
        exchange: filtrar por exchange (NASDAQ, NYSE, BCBA, BME, etc.).
        lang: idioma del response (en, es, etc.).
        domain: production (default).
        hl: 1 = highlight matches en description.

    Returns:
        dict {"symbols_remaining": N, "symbols": [...]} con symbol, description,
        type, exchange, isin, cusip, cik_code, currency_code, logoid, etc.
    """
    url = f"{SYMBOL_SEARCH_HOST}/symbol_search/v3/"
    params: dict[str, Any] = {"text": query, "hl": hl, "lang": lang, "domain": domain}
    if search_type:
        params["search_type"] = search_type
    if exchange:
        params["exchange"] = exchange
    return _get(url, params=params)


# ── News API ───────────────────────────────────────────────────────────────


def news_by_symbol(symbol: str, lang: str = "en") -> dict:
    """GET /v2/headlines?symbol={symbol}.

    Returns:
        dict con `items[]`. Cada item: id, title, provider, source, published,
        urgency, link, relatedSymbols, storyPath.
    """
    return _get(
        f"{NEWS_HOST}/v2/headlines",
        params={"symbol": symbol, "client": "web", "lang": lang},
    )


def news_global(lang: str = "en") -> dict:
    """GET /v2/headlines sin symbol (devuelve hasta 200 headlines globales)."""
    return _get(
        f"{NEWS_HOST}/v2/headlines",
        params={"client": "web", "lang": lang},
    )


def news_story(story_path: str) -> dict:
    """Fetch del cuerpo de una noticia individual via su storyPath.

    El endpoint API directo (news-headlines.tradingview.com/v2/story?id=X)
    retorna 400. Workaround: scrapear https://es.tradingview.com{storyPath}.

    Args:
        story_path: el `storyPath` que viene en `items[].storyPath` de news_by_symbol.

    Returns:
        dict con `url`, `html`, y extraccion best-effort de `title` y `body`.
    """
    if not story_path.startswith("/"):
        story_path = "/" + story_path
    url = f"{WEB_HOST}{story_path}"
    html = _get(url, as_json=False)
    # Best-effort extract de title + body
    title_m = re.search(r'<title>([^<]+)</title>', html)
    # Body suele estar en <div data-name="news-content">  o similar
    body_m = re.search(r'<article[^>]*>(.+?)</article>', html, re.DOTALL)
    if not body_m:
        body_m = re.search(r'data-name="news-content"[^>]*>(.+?)</div>\s*</div>', html, re.DOTALL)
    body_text = None
    if body_m:
        # Strip HTML tags
        raw = body_m.group(1)
        body_text = re.sub(r'<[^>]+>', ' ', raw)
        body_text = re.sub(r'\s+', ' ', body_text).strip()
    return {
        "url": url,
        "title": title_m.group(1).strip() if title_m else None,
        "body": body_text,
        "html_size": len(html),
    }


# ── HTML scraping helpers (prs.init-data+json) ──────────────────────────────


def fetch_subpage(symbol: str, subpath: str = "") -> dict:
    """GET https://es.tradingview.com/symbols/{EX}-{SYM}/{subpath}/.

    Extrae el HTML + todos los bloques `<script type="application/prs.init-data+json">`
    en una lista deserializada.

    Args:
        symbol: ticker tipo "NASDAQ:GGAL" o "BCBA:GGAL".
        subpath: subpage como "technicals", "financials-overview", "forecast",
                 "ideas", "options-chain", "seasonals", "bonds", "etfs",
                 "financials-income-statement", "financials-balance-sheet",
                 "financials-cash-flow", "financials-statistics-and-ratios",
                 "financials-dividends", "financials-revenue", "financials-earnings",
                 "minds". String vacio = pagina base.

    Returns:
        dict con `url`, `html_size`, `prs_blocks` (list de dicts deserializados),
        `tabs` (lista de subpages descubiertas).
    """
    # Convertir "NASDAQ:GGAL" -> "NASDAQ-GGAL"
    sym_path = symbol.replace(":", "-")
    sub = subpath.strip("/") + "/" if subpath else ""
    url = f"{WEB_HOST}/symbols/{sym_path}/{sub}"
    log.info(f"GET {url}")
    html = _get(url, as_json=False, timeout=30)
    blocks = []
    for m in re.finditer(
        r'<script[^>]*type="application/prs\.init-data\+json"[^>]*>(.+?)</script>',
        html, re.DOTALL,
    ):
        try:
            blocks.append(json.loads(m.group(1).strip()))
        except json.JSONDecodeError:
            pass
    tabs = sorted(set(re.findall(rf'href="(/symbols/{sym_path}/[a-z-]+/?)"', html)))
    return {
        "url": url,
        "html_size": len(html),
        "prs_blocks": blocks,
        "tabs": tabs,
    }


# ── Mode ALL ───────────────────────────────────────────────────────────────


def fetch_all(symbol: str, market: str = "global") -> dict:
    """Combina quote_extended + technicals + financials + earnings + targets + news.

    6 requests secuenciales con sleep(0.3) entre cada uno.
    """
    log.info(f"Fetching ALL for {symbol}...")
    result: dict[str, Any] = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
    }
    actions: list[tuple[str, Any]] = [
        ("quote_extended", lambda: quote_extended(symbol, market)),
        ("technicals", lambda: technicals(symbol, market)),
        ("financials", lambda: financials(symbol, market)),
        ("earnings", lambda: earnings(symbol, market)),
        ("targets", lambda: targets(symbol, market)),
        ("news", lambda: news_by_symbol(symbol)),
    ]
    for name, fn in actions:
        try:
            log.info(f"  {name}...")
            result[name] = fn()
            time.sleep(0.3)
        except Exception as e:
            log.warning(f"  {name}: {e}")
            result[name] = {"error": str(e)}
    # Apply rating buckets a los Recommend.* si estan en quote_extended
    try:
        rec_all = result["quote_extended"]["data"][0].get("Recommend.All")
        if rec_all is not None:
            result["_rating_label"] = recommend_label(rec_all)
    except Exception:
        pass
    return result


def recommend_label(value: float) -> str | None:
    """Convierte un valor de Recommend.* en su etiqueta humana."""
    if value is None:
        return None
    for b in recommend_ratings().get("buckets", []):
        if b["min"] <= value <= b["max"]:
            return b["label"]
    return None


# ── Catalogos locales (sin HTTP) ───────────────────────────────────────────


def list_columns(group: str | None = None) -> dict:
    """Listar columnas disponibles (todas las del scanner o un grupo concreto)."""
    if group:
        cols = column_groups().get(group)
        if cols is None:
            return {"error": f"Grupo '{group}' no existe", "available_groups": list(column_groups().keys())}
        return {"group": group, "columns": cols, "count": len(cols)}
    # Sin grupo: devolver TODAS las columnas conocidas con sus descripciones
    return scanner_columns()


def list_groups() -> dict:
    """Listar grupos de columnas pre-armados."""
    cg = column_groups()
    return {k: {"count": len(v), "first_5": v[:5]} for k, v in cg.items() if not k.startswith("_")}


def list_markets() -> dict:
    """Listar mercados validos para POST /{market}/scan."""
    return markets()


# ── CLI ────────────────────────────────────────────────────────────────────


MODES = [
    # Scanner por simbolo
    "quote", "quote-extended", "technicals", "pivots", "financials",
    "earnings", "targets", "performance", "dividends", "ownership",
    # Scanner masivo
    "screen", "country", "sector", "market",
    # Search
    "search",
    # News
    "news", "news-global", "story",
    # HTML
    "subpage",
    # Catalogos
    "columns", "groups", "markets",
    # Combinado
    "all",
]


def main():
    parser = argparse.ArgumentParser(
        description="TradingView Data Fetcher — APIs publicas internas sin auth"
    )
    parser.add_argument("mode", choices=MODES, help="Modo de operacion")
    parser.add_argument(
        "args", nargs="*",
        help="Argumentos posicionales segun el modo"
    )
    parser.add_argument(
        "--market", default="global",
        help="Mercado del Scanner (default: global). Ver `markets`."
    )
    parser.add_argument(
        "--columns", default=None,
        help="Lista de columnas custom separadas por comas (override del grupo del modo)"
    )
    parser.add_argument(
        "--filter", default=None,
        help='Filtro JSON para `screen`. Ej: \'[["sector","equal","Finance"]]\''
    )
    parser.add_argument(
        "--sort", default=None,
        help="Sort para `screen`. Ej: `market_cap_basic:desc`"
    )
    parser.add_argument(
        "--limit", type=int, default=30,
        help="Limite de resultados (default: 30)"
    )
    parser.add_argument(
        "--offset", type=int, default=0,
        help="Offset para paginacion (default: 0)"
    )
    parser.add_argument(
        "--type", default=None,
        help="search_type para `search`: stocks | funds | futures | forex | crypto | indices | bonds | options"
    )
    parser.add_argument(
        "--exchange", default=None,
        help="Exchange filter para `search`: NASDAQ | NYSE | BCBA | BME | etc"
    )
    parser.add_argument(
        "--lang", default="en",
        help="Idioma para news y search (default: en)"
    )
    parser.add_argument("-o", "--output", help="Guardar a archivo JSON")
    parser.add_argument("-q", "--quiet", action="store_true", help="Modo silencioso")

    args = parser.parse_args()
    if args.quiet:
        log.setLevel(logging.WARNING)

    custom_cols: list[str] | None = None
    if args.columns:
        custom_cols = [c.strip() for c in args.columns.split(",") if c.strip()]

    sort_dict: dict | None = None
    if args.sort:
        if ":" in args.sort:
            field, order = args.sort.split(":", 1)
            sort_dict = {"sortBy": field, "sortOrder": order}
        else:
            sort_dict = {"sortBy": args.sort, "sortOrder": "desc"}

    filter_list: list[dict] | None = None
    if args.filter:
        raw = json.loads(args.filter)
        # Aceptar lista de [left, op, right] o lista de dicts
        if raw and isinstance(raw[0], list):
            filter_list = [
                {"left": x[0], "operation": x[1], "right": x[2]} for x in raw
            ]
        else:
            filter_list = raw

    try:
        m = args.mode
        pos = args.args

        if m == "quote":
            _need(pos, 1, m, "SYMBOL (ej: NASDAQ:GGAL)")
            result = quote(pos[0], columns=custom_cols, market=args.market)
        elif m == "quote-extended":
            _need(pos, 1, m, "SYMBOL")
            result = quote_extended(pos[0], market=args.market)
        elif m == "technicals":
            _need(pos, 1, m, "SYMBOL")
            result = technicals(pos[0], market=args.market)
        elif m == "pivots":
            _need(pos, 1, m, "SYMBOL")
            result = pivots(pos[0], market=args.market)
        elif m == "financials":
            _need(pos, 1, m, "SYMBOL")
            result = financials(pos[0], market=args.market)
        elif m == "earnings":
            _need(pos, 1, m, "SYMBOL")
            result = earnings(pos[0], market=args.market)
        elif m == "targets":
            _need(pos, 1, m, "SYMBOL")
            result = targets(pos[0], market=args.market)
        elif m == "performance":
            _need(pos, 1, m, "SYMBOL")
            result = performance(pos[0], market=args.market)
        elif m == "dividends":
            _need(pos, 1, m, "SYMBOL")
            result = dividends(pos[0], market=args.market)
        elif m == "ownership":
            _need(pos, 1, m, "SYMBOL")
            result = ownership(pos[0], market=args.market)
        elif m == "screen":
            if not filter_list:
                log.error("screen requiere --filter JSON. Ver references/SCANNER_FILTERS.md")
                sys.exit(1)
            result = screen(
                filter_=filter_list, market=args.market, columns=custom_cols,
                sort=sort_dict, limit=args.limit, offset=args.offset,
            )
        elif m == "country":
            _need(pos, 1, m, "COUNTRY (ej: Argentina)")
            result = by_country(pos[0], market=args.market, limit=args.limit)
        elif m == "sector":
            _need(pos, 1, m, "SECTOR (ej: Finance)")
            result = by_sector(pos[0], market=args.market, limit=args.limit)
        elif m == "market":
            mk = pos[0] if pos else args.market
            result = list_market(market=mk, limit=args.limit)
        elif m == "search":
            _need(pos, 1, m, "QUERY")
            result = symbol_search(
                " ".join(pos), search_type=args.type, exchange=args.exchange, lang=args.lang,
            )
        elif m == "news":
            _need(pos, 1, m, "SYMBOL")
            result = news_by_symbol(pos[0], lang=args.lang)
        elif m == "news-global":
            result = news_global(lang=args.lang)
        elif m == "story":
            _need(pos, 1, m, "STORY_PATH (ej: /news/DJN_DN...:0/)")
            result = news_story(pos[0])
        elif m == "subpage":
            _need(pos, 1, m, "SYMBOL [SUBPATH]")
            sym = pos[0]
            subpath = pos[1] if len(pos) > 1 else ""
            result = fetch_subpage(sym, subpath)
        elif m == "columns":
            group = pos[0] if pos else None
            result = list_columns(group)
        elif m == "groups":
            result = list_groups()
        elif m == "markets":
            result = list_markets()
        elif m == "all":
            _need(pos, 1, m, "SYMBOL")
            result = fetch_all(pos[0], market=args.market)
        else:
            parser.print_help()
            sys.exit(1)
    except requests.HTTPError as e:
        log.error(f"HTTP Error: {e}")
        if e.response is not None:
            log.error(f"Body: {e.response.text[:500]}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Error: {e}")
        sys.exit(1)

    # ── Output ─────────────────────────────────────────────────────────
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            if isinstance(result, str):
                f.write(result)
            else:
                json.dump(result, f, indent=2, ensure_ascii=False)
        log.info(f"Guardado: {args.output}")
    else:
        if isinstance(result, str):
            print(result)
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))


def _need(args_list: list, n: int, mode: str, msg: str):
    if len(args_list) < n:
        log.error(f"Modo '{mode}' requiere: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
