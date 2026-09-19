"""
Google Finance Data Fetcher — APIs publicas internas sin auth.

Google Finance NO tiene API publica oficial. Pero su SPA expone un endpoint
RPC (Remote Procedure Call) llamado `batchexecute` que retorna JSON
estructurado para cualquier simbolo. SIN api key, SIN autenticacion.

Endpoint base: POST https://www.google.com/finance/beta/_/FinHubUi/data/batchexecute

Modos disponibles:

  POR SIMBOLO (requieren ticker tipo "GGAL:NASDAQ" o "GGAL:BCBA"):
    - quote SYM            Quote basico (precio, change, currency, market hours)
    - quote-full SYM       Quote enriquecido (market cap, volume, industry)
    - description SYM      Descripcion + address + employees + ratios + URLs
    - peers SYM            Related stocks / peers
    - analysts SYM         Analyst recommendations + opinions individuales
    - earnings SYM         Earnings history (year + quarter)
    - technicals SYM       Ratings tecnicos
    - financials SYM       Financials masivos multi-period (income/balance/cashflow)
    - intraday-1min SYM    OHLC 1-min del dia actual (~30 KB)
    - intraday-5min SYM    OHLC 5-min con OHLC explicito (~5 KB)
    - daily SYM            OHLC diario ultimo mes (~22 dias)
    - daily-6m SYM         OHLC diario ultimos ~6 meses
    - news SYM             News especificas del simbolo
    - news-related SYM     News globales (con related symbols del query)

  GLOBALES (sin simbolo):
    - indices              Indices globales: Dow, S&P, NASDAQ, VIX, DAX, FTSE...
    - sectors              Sectors equity heatmap

  CATALOGOS LOCALES (sin HTTP):
    - rpcs                 Listar RPCs disponibles con sus args templates
    - layouts              Listar layouts de los arrays anidados
    - cookies              Mostrar cookies de bypass consent

  COMBINADO:
    - all SYM              Combina quote + description + analysts + financials + daily + news

Uso:
    py fetch_gfinance.py quote GGAL:NASDAQ
    py fetch_gfinance.py quote GGAL:BCBA
    py fetch_gfinance.py quote-full AAPL:NASDAQ
    py fetch_gfinance.py description AAPL:NASDAQ
    py fetch_gfinance.py peers GGAL:NASDAQ
    py fetch_gfinance.py analysts NASDAQ:NVDA      # tambien acepta EXCHANGE:TICKER
    py fetch_gfinance.py earnings AAPL:NASDAQ
    py fetch_gfinance.py technicals GGAL:NASDAQ
    py fetch_gfinance.py financials AAPL:NASDAQ
    py fetch_gfinance.py intraday-1min GGAL:NASDAQ
    py fetch_gfinance.py intraday-5min AAPL:NASDAQ
    py fetch_gfinance.py daily GGAL:NASDAQ
    py fetch_gfinance.py daily-6m AAPL:NASDAQ
    py fetch_gfinance.py news GGAL:NASDAQ
    py fetch_gfinance.py news-related GGAL:NASDAQ

    py fetch_gfinance.py indices
    py fetch_gfinance.py sectors

    py fetch_gfinance.py rpcs                       # catalogo local
    py fetch_gfinance.py layouts                    # catalogo local
    py fetch_gfinance.py cookies                    # mostrar cookies bypass

    py fetch_gfinance.py all GGAL:NASDAQ
    py fetch_gfinance.py all GGAL:NASDAQ -o ggal_full.json

    py fetch_gfinance.py quote GGAL:NASDAQ --raw   # NO normalizar response
    py fetch_gfinance.py quote GGAL:NASDAQ -q      # silencioso

⚠️  WARNING: Esta API NO esta documentada y puede cambiar sin aviso.
Si fallan llamadas, revisar references/LIMITATIONS_TROUBLESHOOTING.md.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

log = logging.getLogger("gfinance")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# Forzar UTF-8 en Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, Exception):
    pass

# ── Hosts y configuracion ──────────────────────────────────────────────────

BATCH_URL = "https://www.google.com/finance/beta/_/FinHubUi/data/batchexecute"
WEB_BASE = "https://www.google.com/finance/beta"
BL_VERSION = "boq_finhub-uiserver_20260531.09_p2"  # del HTML — puede cambiar

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "X-Same-Domain": "1",
    "Origin": "https://www.google.com",
}

# Cookies de bypass del consent screen (ver assets/consent_cookies.json)
COOKIES = {
    "CONSENT": "PENDING+999",
    "SOCS": "CAESHAgBEhJnd3NfMjAyNTAxMjMtMF9SQzMaAmVuIAEaBgiAvLW8Bg",
}

# Assets locales
SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"


def load_asset(name: str) -> Any:
    fp = ASSETS_DIR / name
    if not fp.exists():
        log.warning(f"Asset no encontrado: {fp}")
        return None
    with open(fp, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Parser del protocolo wrb.fr ────────────────────────────────────────────


def parse_wrbfr(text: str) -> list[tuple[str, Any]]:
    """Parse del response format wrb.fr de Google.

    Estructura:
      )]}'
      <size>
      [["wrb.fr","<rpcId>","<JSON_serialized_array>",null,null,null,"generic"], ...]
      <size>
      [...mas entries...]

    Returns:
        Lista de (rpc_id, parsed_data). data ya viene parseado con doble json.loads.
    """
    if not text.startswith(")]}'"):
        # Algunos errores no traen este prefix
        return []
    body = text[4:].strip()
    results = []
    for line in body.split("\n"):
        line = line.strip()
        if not line or line.isdigit():
            continue
        try:
            arr = json.loads(line)
        except json.JSONDecodeError:
            continue
        for item in arr:
            if (
                isinstance(item, list) and len(item) >= 3
                and item[0] == "wrb.fr"
                and isinstance(item[1], str)
                and item[2]
            ):
                rpc_id = item[1]
                try:
                    parsed = json.loads(item[2])
                except json.JSONDecodeError:
                    parsed = item[2]
                results.append((rpc_id, parsed))
    return results


# ── Call generico al batchexecute ──────────────────────────────────────────


def call_batchexecute(rpc_id: str, args: list, sym_pair: tuple[str, str] | None = None,
                     raw: bool = False) -> Any:
    """Hace un POST al batchexecute con un RPC.

    Args:
        rpc_id: ID del RPC (gCvqoe, hgueg, etc).
        args: argumentos del RPC (se serializa a JSON).
        sym_pair: tupla (TICKER, EXCHANGE) — usado solo para el Referer.
        raw: si True, retorna el response parseado raw; si False, el array de data del RPC.

    Returns:
        Si raw=False: el array de data del primer match wrb.fr (o None si error).
        Si raw=True: list de (rpc_id, data) — util si pasaste multiple RPCs.

    Raises:
        requests.HTTPError si el endpoint retorna != 200.
    """
    rpc_args_json = json.dumps(args, separators=(",", ":"))
    f_req = json.dumps([[[rpc_id, rpc_args_json, None, "generic"]]], separators=(",", ":"))

    params = {
        "rpcids": rpc_id,
        "source-path": (
            f"/finance/quote/{sym_pair[0]}:{sym_pair[1]}" if sym_pair
            else "/finance"
        ),
        "f.sid": "-1",
        "bl": BL_VERSION,
        "hl": "en",
        "_reqid": "1",
        "rt": "c",
    }
    headers = {
        **HEADERS,
        "Referer": (
            f"https://www.google.com/finance/quote/{sym_pair[0]}:{sym_pair[1]}" if sym_pair
            else "https://www.google.com/finance"
        ),
    }

    log.info(f"POST batchexecute rpcid={rpc_id}, args={args}")
    r = requests.post(
        BATCH_URL, params=params, data={"f.req": f_req},
        headers=headers, cookies=COOKIES, timeout=30,
    )
    r.raise_for_status()

    parsed = parse_wrbfr(r.text)
    if not parsed:
        log.warning(f"  Response sin wrb.fr (size={len(r.text)})")
        return None

    if raw:
        return parsed

    # Buscar el match del rpc_id que pediste
    for rid, data in parsed:
        if rid == rpc_id:
            return data
    # Si no matchea exact, devolver el primero
    return parsed[0][1]


# ── Helper: parsear "TICKER:EXCHANGE" o "EXCHANGE:TICKER" ──────────────────


def parse_symbol(sym_str: str) -> tuple[str, str]:
    """Parse 'GGAL:NASDAQ' o 'NASDAQ:GGAL' a (TICKER, EXCHANGE).

    Heuristica: el exchange es el componente que matchea una lista conocida.
    Si no se puede determinar, asume formato TICKER:EXCHANGE (lo mas comun
    en Google Finance).
    """
    if ":" not in sym_str:
        raise ValueError(f"Simbolo invalido: {sym_str!r}. Esperado TICKER:EXCHANGE (ej: GGAL:NASDAQ)")
    parts = sym_str.split(":", 1)
    a, b = parts[0].upper(), parts[1].upper()
    KNOWN_EXCHANGES = {
        "NASDAQ", "NYSE", "AMEX", "BCBA", "BYMA", "BME", "BMV", "BMFBOVESPA",
        "XETR", "FWB", "LSE", "EURONEXT", "MIL", "SIX", "TSE", "JPX", "HKEX",
        "SSE", "SZSE", "KRX", "NSE", "BSE", "ASX", "INDEXDJX", "INDEXSP",
        "INDEXNASDAQ", "INDEXRUSSELL", "INDEXCBOE", "INDEXDB", "INDEXFTSE",
        "INDEXNIKKEI", "INDEXHSI", "INDEXMADRID", "INDEXBOM",
    }
    if b in KNOWN_EXCHANGES:
        return (a, b)
    if a in KNOWN_EXCHANGES:
        return (b, a)  # flip: el usuario paso EXCHANGE:TICKER
    # Default: asumir TICKER:EXCHANGE (formato standard)
    return (a, b)


# ── Modos especificos ──────────────────────────────────────────────────────


def quote(sym: str) -> Any:
    """Quote basico."""
    pair = parse_symbol(sym)
    return call_batchexecute("gCvqoe", [[[None, list(pair)]], 1], pair)


def quote_full(sym: str) -> Any:
    """Quote enriquecido (industry + market cap + volume)."""
    pair = parse_symbol(sym)
    return call_batchexecute("dlNq8b", [[[None, list(pair)]], 1, 1, 1], pair)


def description(sym: str) -> Any:
    """Descripcion + address + employees + ratios + URLs."""
    pair = parse_symbol(sym)
    return call_batchexecute("JL8oKc", [[[None, list(pair)]]], pair)


def peers(sym: str, count: int = 4) -> Any:
    """Related stocks / peers (4 default)."""
    pair = parse_symbol(sym)
    return call_batchexecute("SICF5d", [[None, list(pair)], count], pair)


def analysts(sym: str) -> Any:
    """Analyst recommendations + opinions."""
    pair = parse_symbol(sym)
    return call_batchexecute("YTM9q", [[None, list(pair)]], pair)


def earnings(sym: str) -> Any:
    """Earnings history (year + quarter)."""
    pair = parse_symbol(sym)
    return call_batchexecute("XxQsbd", [[[None, list(pair)]], 1], pair)


def technicals(sym: str) -> Any:
    """Ratings tecnicos."""
    pair = parse_symbol(sym)
    return call_batchexecute("gXxkFd", [list(pair)], pair)


def financials(sym: str) -> Any:
    """Financials masivos (income/balance/cashflow multi-period)."""
    pair = parse_symbol(sym)
    return call_batchexecute("Pr8h2e", [[[None, list(pair)]]], pair)


def intraday_1min(sym: str) -> Any:
    """OHLC 1-min del dia actual."""
    pair = parse_symbol(sym)
    return call_batchexecute("c2u4wc", [[[None, list(pair)]], 1], pair)


def intraday_5min(sym: str) -> Any:
    """OHLC 5-min con OHLC explicito."""
    pair = parse_symbol(sym)
    return call_batchexecute(
        "c2u4wc",
        [[[None, list(pair)]], 1, None, None, None, None, None, 1],
        pair,
    )


def daily(sym: str) -> Any:
    """OHLC diario ultimo mes."""
    pair = parse_symbol(sym)
    return call_batchexecute("c2u4wc", [[[None, list(pair)]], 3], pair)


def daily_6m(sym: str) -> Any:
    """OHLC diario ultimos ~6 meses."""
    pair = parse_symbol(sym)
    return call_batchexecute("c2u4wc", [[[None, list(pair)]], 4], pair)


def news(sym: str) -> Any:
    """News especificas del simbolo."""
    pair = parse_symbol(sym)
    return call_batchexecute("kA4MVd", [5, 12, [[None, list(pair)]]], pair)


def news_related(sym: str) -> Any:
    """News globales del mercado (con related symbols del query)."""
    pair = parse_symbol(sym)
    return call_batchexecute("kA4MVd", [2, 12, [[None, list(pair)]]], pair)


def indices() -> Any:
    """Indices globales (sin simbolo)."""
    return call_batchexecute("hgueg", [1])


def sectors() -> Any:
    """Sectors equity heatmap (sin simbolo)."""
    return call_batchexecute("vNewwe", [None, [None, 1]])


# ── Catalogos locales ──────────────────────────────────────────────────────


def list_rpcs() -> Any:
    return load_asset("rpc_ids.json")


def list_layouts() -> Any:
    return load_asset("chunk_layouts.json")


def list_cookies() -> Any:
    return load_asset("consent_cookies.json")


# ── Mode ALL ───────────────────────────────────────────────────────────────


def fetch_all(sym: str) -> dict:
    """Combina los modos mas utiles en un solo dict."""
    log.info(f"Fetching ALL data for {sym}...")
    result: dict[str, Any] = {
        "symbol": sym,
        "timestamp": datetime.now().isoformat(),
    }
    actions = [
        ("quote", quote),
        ("description", description),
        ("analysts", analysts),
        ("financials", financials),
        ("daily", daily),
        ("news", news),
    ]
    for name, fn in actions:
        try:
            log.info(f"  {name}...")
            result[name] = fn(sym)
            time.sleep(0.3)
        except Exception as e:
            log.warning(f"  {name}: {e}")
            result[name] = {"error": str(e)}
    return result


# ── CLI ────────────────────────────────────────────────────────────────────


MODES = [
    # Por simbolo
    "quote", "quote-full", "description", "peers", "analysts", "earnings",
    "technicals", "financials",
    "intraday-1min", "intraday-5min", "daily", "daily-6m",
    "news", "news-related",
    # Globales
    "indices", "sectors",
    # Catalogos
    "rpcs", "layouts", "cookies",
    # Combinado
    "all",
]


def main():
    parser = argparse.ArgumentParser(
        description="Google Finance Data Fetcher — APIs publicas internas sin auth"
    )
    parser.add_argument("mode", choices=MODES, help="Modo de operacion")
    parser.add_argument("sym", nargs="?", help="Simbolo TICKER:EXCHANGE (ej: GGAL:NASDAQ)")
    parser.add_argument(
        "--peers-count", type=int, default=4,
        help="Cantidad de peers para `peers` (default: 4)"
    )
    parser.add_argument(
        "--raw", action="store_true",
        help="Devolver response raw (sin extraer del array wrb.fr)"
    )
    parser.add_argument("-o", "--output", help="Guardar a archivo JSON")
    parser.add_argument("-q", "--quiet", action="store_true", help="Modo silencioso")

    args = parser.parse_args()
    if args.quiet:
        log.setLevel(logging.WARNING)

    try:
        m = args.mode

        # Modos que requieren simbolo
        sym_modes = {
            "quote", "quote-full", "description", "peers", "analysts",
            "earnings", "technicals", "financials",
            "intraday-1min", "intraday-5min", "daily", "daily-6m",
            "news", "news-related", "all",
        }
        if m in sym_modes:
            if not args.sym:
                log.error(f"Modo '{m}' requiere simbolo TICKER:EXCHANGE (ej: GGAL:NASDAQ)")
                sys.exit(1)

        if m == "quote":
            result = quote(args.sym)
        elif m == "quote-full":
            result = quote_full(args.sym)
        elif m == "description":
            result = description(args.sym)
        elif m == "peers":
            result = peers(args.sym, count=args.peers_count)
        elif m == "analysts":
            result = analysts(args.sym)
        elif m == "earnings":
            result = earnings(args.sym)
        elif m == "technicals":
            result = technicals(args.sym)
        elif m == "financials":
            result = financials(args.sym)
        elif m == "intraday-1min":
            result = intraday_1min(args.sym)
        elif m == "intraday-5min":
            result = intraday_5min(args.sym)
        elif m == "daily":
            result = daily(args.sym)
        elif m == "daily-6m":
            result = daily_6m(args.sym)
        elif m == "news":
            result = news(args.sym)
        elif m == "news-related":
            result = news_related(args.sym)
        elif m == "indices":
            result = indices()
        elif m == "sectors":
            result = sectors()
        elif m == "rpcs":
            result = list_rpcs()
        elif m == "layouts":
            result = list_layouts()
        elif m == "cookies":
            result = list_cookies()
        elif m == "all":
            result = fetch_all(args.sym)
        else:
            parser.print_help()
            sys.exit(1)
    except requests.HTTPError as e:
        log.error(f"HTTP Error: {e}")
        if e.response is not None:
            log.error(f"Body: {e.response.text[:500]}")
        log.error("Si el endpoint deja de funcionar, ver references/LIMITATIONS_TROUBLESHOOTING.md")
        sys.exit(1)
    except Exception as e:
        log.error(f"Error: {e}")
        sys.exit(1)

    # ── Output ─────────────────────────────────────────────────────────
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        log.info(f"Guardado: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
