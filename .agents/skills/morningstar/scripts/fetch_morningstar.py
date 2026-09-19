"""
Morningstar Screener Data Fetcher — API JSON publica (no auth, sin WAF).

Accede a un endpoint interno de Morningstar usado por su UI web para el
screener de acciones. El endpoint se descubrio por ingenieria inversa
mirando que XHR hace la web. Devuelve la base de datos completa de un
mercado/exchange con 28 campos (precio, market cap, ratios, retornos
1d/1w/1m/3m/6m/12m/36m/60m/120m, deuda, dividend yield, sector,
industria, etc.) en formato JSON.

Solo el endpoint /security/screener es accesible sin auth. Otros
endpoints de Morningstar (api-global.morningstar.com, global.morningstar.com,
lt.morningstar.com) requieren resolver AWS WAF challenge (ver SKILL.md).

Modos disponibles:
  info        Info del script, universes soportados, campos disponibles
  search      Buscar tickers por nombre en uno o varios universes
  screener    Descarga masiva de uno o varios universes (toda la DB)
  download    Alias de screener
  fields      Lista los 28 securityDataPoints disponibles

Uso:
    python fetch_morningstar.py info
    python fetch_morningstar.py fields
    python fetch_morningstar.py search Apple --universe XNAS
    python fetch_morningstar.py search Apple --universe XNAS XFRA XBUE
    python fetch_morningstar.py screener --universe XBUE
    python fetch_morningstar.py screener --universe XNAS XLON
    python fetch_morningstar.py download --universe XBUE --output argentina.csv
    python fetch_morningstar.py download --country AR --output ar_data.json
    python fetch_morningstar.py search AAPL --universe XNAS --limit 5 -q
"""
import argparse
import csv
import json
import logging
import sys
import time
import warnings
from collections import OrderedDict
from datetime import datetime, timezone

import requests

# Silenciar DeprecationWarning de datetime.utcnow()
warnings.filterwarnings("ignore", category=DeprecationWarning)

log = logging.getLogger("morningstar")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# Token universal descubierto por ingenieria inversa (mismo en todos los
# sub-dominios tools.morningstar.* que no tienen WAF)
TOKEN = "klr5zyak8x"

# Sub-dominios tools.morningstar.* que NO tienen WAF
# Todos funcionan con el mismo TOKEN
DOMAINS = [
    "https://tools.morningstar.co.uk",
    "https://tools.morningstar.de",
    "https://tools.morningstar.it",
    "https://tools.morningstar.fr",
    "https://tools.morningstar.es",
]
DEFAULT_DOMAIN = DOMAINS[0]

# Los 28 securityDataPoints del screener (extraidos del notebook del usuario
# y validados contra la respuesta del API)
DATA_POINTS = [
    # Identificacion
    "Ticker",
    "Name",
    "PerformanceId",
    "Universe",
    # Precio y tamano
    "ClosePrice",
    "MarketCap",
    "MarketCountryName",
    # Categoria
    "SectorName",
    "IndustryName",
    "EquityStyleBox",
    "QuantitativeStarRating",
    # Ratios de valuacion
    "PERatio",
    "PEGRatio",
    "DividendYield",
    # Ratios financieros
    "DebtEquityRatio",
    "NetMargin",
    "EBTMarginYear1",
    "ROATTM",
    "ROETTM",
    "ROEYear1",
    "ROICYear1",
    # Crecimiento
    "EPSGrowth3YYear1",
    "RevenueGrowth3Y",
    # Retornos
    "ReturnD1",
    "ReturnW1",
    "ReturnM0",
    "ReturnM1",
    "ReturnM3",
    "ReturnM6",
    "ReturnM12",
    "ReturnM36",
    "ReturnM60",
    "ReturnM120",
]

# Todos los universe codes descubiertos (54 con data, junio 2026)
UNIVERSES = OrderedDict([
    # === Americas - US ===
    ("XNYS",  {"name": "NYSE",                      "exchange": "New York Stock Exchange",     "country": "United States",  "currency": "USD", "lang": "en-US", "count": 2343}),
    ("XNAS",  {"name": "Nasdaq",                    "exchange": "Nasdaq",                      "country": "United States",  "currency": "USD", "lang": "en-US", "count": 3741}),
    ("ARCX",  {"name": "NYSE Arca",                 "exchange": "NYSE Arca",                   "country": "United States",  "currency": "USD", "lang": "en-US", "count": 3}),
    ("XASE",  {"name": "NYSE American",             "exchange": "NYSE American",               "country": "United States",  "currency": "USD", "lang": "en-US", "count": 267}),
    # === Americas - Canada ===
    ("XTSE",  {"name": "TSX",                       "exchange": "Toronto Stock Exchange",      "country": "Canada",         "currency": "CAD", "lang": "en-CA", "count": 1123}),
    ("XTSX",  {"name": "TSXV",                      "exchange": "TSX Venture Exchange",        "country": "Canada",         "currency": "CAD", "lang": "en-CA", "count": 1728}),
    # === Americas - LatAm ===
    ("XMEX",  {"name": "BMV",                       "exchange": "Bolsa Mexicana de Valores",   "country": "Mexico",         "currency": "MXN", "lang": "es-MX", "count": 2233}),
    ("BVMF",  {"name": "B3",                        "exchange": "B3 (Brasil Bolsa Balcao)",    "country": "Brasil",         "currency": "BRL", "lang": "pt-BR", "count": 2070}),
    ("XBUE",  {"name": "BCBA",                      "exchange": "Bolsas y Mercados Argentinos","country": "Argentina",      "currency": "ARS", "lang": "es-AR", "count": 469}),
    # === Europe - UK ===
    ("XLON",  {"name": "LSE",                       "exchange": "London Stock Exchange",       "country": "United Kingdom", "currency": "GBP", "lang": "en-GB", "count": 1333}),
    # === Europe - Eurozona ===
    ("XPAR",  {"name": "EPA",                       "exchange": "Euronext Paris",              "country": "France",         "currency": "EUR", "lang": "fr-FR", "count": 728}),
    ("XAMS",  {"name": "AMS",                       "exchange": "Euronext Amsterdam",          "country": "Netherlands",    "currency": "EUR", "lang": "nl-NL", "count": 123}),
    ("XBRU",  {"name": "BRU",                       "exchange": "Euronext Brussels",           "country": "Belgium",        "currency": "EUR", "lang": "nl-BE", "count": 140}),
    ("XLIS",  {"name": "LIS",                       "exchange": "Euronext Lisbon",             "country": "Portugal",       "currency": "EUR", "lang": "pt-PT", "count": 49}),
    ("XDUB",  {"name": "DUB",                       "exchange": "Euronext Dublin",             "country": "Ireland",        "currency": "EUR", "lang": "en-IE", "count": 44}),
    ("XETR",  {"name": "XETRA",                     "exchange": "Xetra (Deutsche Borse)",      "country": "Germany",        "currency": "EUR", "lang": "de-DE", "count": 1048}),
    ("XFRA",  {"name": "FRA",                       "exchange": "Frankfurt (Tradegate)",       "country": "Germany",        "currency": "EUR", "lang": "de-DE", "count": 14082}),
    ("XSTU",  {"name": "STU",                       "exchange": "Stuttgart",                   "country": "Germany",        "currency": "EUR", "lang": "de-DE", "count": 9971}),
    ("XMUN",  {"name": "MUN",                       "exchange": "Munich",                      "country": "Germany",        "currency": "EUR", "lang": "de-DE", "count": 8425}),
    ("XHAM",  {"name": "HAM",                       "exchange": "Hamburg",                     "country": "Germany",        "currency": "EUR", "lang": "de-DE", "count": 3596}),
    ("XDUS",  {"name": "DUS",                       "exchange": "Dusseldorf",                  "country": "Germany",        "currency": "EUR", "lang": "de-DE", "count": 8297}),
    ("XBER",  {"name": "BER",                       "exchange": "Berlin",                      "country": "Germany",        "currency": "EUR", "lang": "de-DE", "count": 256}),
    ("XHAN",  {"name": "HAN",                       "exchange": "Hanover",                     "country": "Germany",        "currency": "EUR", "lang": "de-DE", "count": 1436}),
    ("XMIL",  {"name": "MIL",                       "exchange": "Borsa Italiana (Milan)",      "country": "Italy",          "currency": "EUR", "lang": "it-IT", "count": 1411}),
    ("XMAD",  {"name": "MAD",                       "exchange": "BME (Madrid)",                "country": "Spain",          "currency": "EUR", "lang": "es-ES", "count": 291}),
    ("XMCE",  {"name": "MCE",                       "exchange": "Mercado Continuo (Madrid)",   "country": "Spain",          "currency": "EUR", "lang": "es-ES", "count": 291}),
    ("XHEL",  {"name": "HEL",                       "exchange": "Helsinki",                    "country": "Finland",        "currency": "EUR", "lang": "fi-FI", "count": 194}),
    ("XATH",  {"name": "ATH",                       "exchange": "Athens",                      "country": "Greece",         "currency": "EUR", "lang": "el-GR", "count": 149}),
    # === Europe - Otros ===
    ("XSWX",  {"name": "SIX",                       "exchange": "Swiss Exchange",              "country": "Switzerland",    "currency": "CHF", "lang": "de-CH", "count": 507}),
    ("XCSE",  {"name": "CPH",                       "exchange": "Copenhagen (Nasdaq Nordic)",  "country": "Denmark",        "currency": "DKK", "lang": "da-DK", "count": 146}),
    ("XOSL",  {"name": "OSL",                       "exchange": "Oslo (Euronext)",             "country": "Norway",         "currency": "NOK", "lang": "no-NO", "count": 296}),
    ("XSTO",  {"name": "STO",                       "exchange": "Stockholm (Nasdaq Nordic)",   "country": "Sweden",         "currency": "SEK", "lang": "sv-SE", "count": 930}),
    ("XICE",  {"name": "ICE",                       "exchange": "Iceland (Nasdaq Nordic)",    "country": "Iceland",        "currency": "ISK", "lang": "is-IS", "count": 31}),
    ("XTAL",  {"name": "TAL",                       "exchange": "Tallinn (Nasdaq Baltic)",    "country": "Estonia",        "currency": "EUR", "lang": "et-EE", "count": 35}),
    ("XWAR",  {"name": "WSE",                       "exchange": "Warsaw",                      "country": "Poland",         "currency": "PLN", "lang": "pl-PL", "count": 797}),
    ("XIST",  {"name": "BIST",                      "exchange": "Borsa Istanbul",              "country": "Turkey",         "currency": "TRY", "lang": "tr-TR", "count": 607}),
    # === Asia ===
    ("XTKS",  {"name": "TSE",                       "exchange": "Tokyo Stock Exchange",        "country": "Japan",          "currency": "JPY", "lang": "ja-JP", "count": 3989}),
    ("XSHG",  {"name": "SSE",                       "exchange": "Shanghai",                    "country": "China",          "currency": "CNY", "lang": "zh-CN", "count": 2365}),
    ("XSHE",  {"name": "SZSE",                      "exchange": "Shenzhen",                    "country": "China",          "currency": "CNY", "lang": "zh-CN", "count": 2934}),
    ("XHKG",  {"name": "HKEX",                      "exchange": "Hong Kong",                   "country": "Hong Kong",      "currency": "HKD", "lang": "zh-HK", "count": 2757}),
    ("XSES",  {"name": "SGX",                       "exchange": "Singapore",                   "country": "Singapore",      "currency": "SGD", "lang": "en-SG", "count": 642}),
    ("XKRX",  {"name": "KRX",                       "exchange": "Korea Exchange",              "country": "South Korea",    "currency": "KRW", "lang": "ko-KR", "count": 2877}),
    ("XBOM",  {"name": "BSE",                       "exchange": "Bombay (BSE)",                "country": "India",          "currency": "INR", "lang": "en-IN", "count": 5192}),
    ("XNSE",  {"name": "NSE",                       "exchange": "NSE India",                   "country": "India",          "currency": "INR", "lang": "en-IN", "count": 3018}),
    ("XTAI",  {"name": "TWSE",                      "exchange": "Taiwan",                      "country": "Taiwan",         "currency": "TWD", "lang": "zh-TW", "count": 1127}),
    ("XBKK",  {"name": "SET",                       "exchange": "Bangkok",                     "country": "Thailand",       "currency": "THB", "lang": "th-TH", "count": 2719}),
    ("XKLS",  {"name": "BURSA",                     "exchange": "Bursa Malaysia",              "country": "Malaysia",       "currency": "MYR", "lang": "ms-MY", "count": 1142}),
    ("XIDX",  {"name": "IDX",                       "exchange": "Jakarta",                     "country": "Indonesia",      "currency": "IDR", "lang": "id-ID", "count": 961}),
    ("XPHS",  {"name": "PSE",                       "exchange": "Philippines",                 "country": "Philippines",    "currency": "PHP", "lang": "en-PH", "count": 361}),
    # === Oceania ===
    ("XASX",  {"name": "ASX",                       "exchange": "Australian Securities Exch.", "country": "Australia",      "currency": "AUD", "lang": "en-AU", "count": 1814}),
    ("XNZE",  {"name": "NZX",                       "exchange": "New Zealand Exchange",        "country": "New Zealand",    "currency": "NZD", "lang": "en-NZ", "count": 127}),
    # === Middle East & Africa ===
    ("XTAE",  {"name": "TASE",                      "exchange": "Tel Aviv",                    "country": "Israel",         "currency": "ILS", "lang": "he-IL", "count": 546}),
    ("XJSE",  {"name": "JSE",                       "exchange": "Johannesburg",                "country": "South Africa",   "currency": "ZAR", "lang": "en-ZA", "count": 332}),
])

# Mapping pais -> universe codes (principales)
COUNTRY_TO_UNIVERSES = {
    "US": ["XNYS", "XNAS", "ARCX", "XASE"],
    "CA": ["XTSE", "XTSX"],
    "MX": ["XMEX"],
    "BR": ["BVMF"],
    "AR": ["XBUE"],
    "GB": ["XLON"],
    "FR": ["XPAR"],
    "NL": ["XAMS"],
    "BE": ["XBRU"],
    "PT": ["XLIS"],
    "IE": ["XDUB"],
    "DE": ["XETR", "XFRA", "XSTU", "XMUN", "XHAM", "XDUS", "XBER", "XHAN"],
    "IT": ["XMIL"],
    "ES": ["XMAD", "XMCE"],
    "FI": ["XHEL"],
    "GR": ["XATH"],
    "CH": ["XSWX"],
    "DK": ["XCSE"],
    "NO": ["XOSL"],
    "SE": ["XSTO"],
    "IS": ["XICE"],
    "EE": ["XTAL"],
    "PL": ["XWAR"],
    "TR": ["XIST"],
    "JP": ["XTKS"],
    "CN": ["XSHG", "XSHE"],
    "HK": ["XHKG"],
    "SG": ["XSES"],
    "KR": ["XKRX"],
    "IN": ["XBOM", "XNSE"],
    "TW": ["XTAI"],
    "TH": ["XBKK"],
    "MY": ["XKLS"],
    "ID": ["XIDX"],
    "PH": ["XPHS"],
    "AU": ["XASX"],
    "NZ": ["XNZE"],
    "IL": ["XTAE"],
    "ZA": ["XJSE"],
}


# ── HTTP ────────────────────────────────────────────────────────────────────

def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return s


def get(s, path, params=None, retries=3, sleep=1.0):
    """GET al sub-dominio que funcione (probar varios)."""
    last_error = None
    for domain in DOMAINS:
        url = f"{domain}{path}"
        for i in range(retries):
            try:
                r = s.get(url, params=params, timeout=30, allow_redirects=True)
            except Exception as e:
                last_error = e
                log.warning(f"  network error en {domain}: {e}")
                time.sleep(sleep)
                continue
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                # este dominio no tiene el endpoint, probar el siguiente
                last_error = f"{domain} 404"
                break
            log.warning(f"  {domain} intento {i+1}/{retries}: status={r.status_code}")
            time.sleep(sleep)
        time.sleep(0.3)
    raise RuntimeError(f"ningun dominio respondio OK. Last error: {last_error}")


# ── Modos ───────────────────────────────────────────────────────────────────

def cmd_info(args):
    """Imprime info del script, dominios, token, numero de universes."""
    out = {
        "name": "morningstar",
        "endpoint": "/api/rest.svc/klr5zyak8x/security/screener",
        "domains": DOMAINS,
        "default_domain": DEFAULT_DOMAIN,
        "token": TOKEN,
        "token_note": "Universal, mismo en todos los sub-dominios",
        "universe_count": len(UNIVERSES),
        "data_points_count": len(DATA_POINTS),
        "total_listings": sum(u["count"] for u in UNIVERSES.values()),
        "countries": len(COUNTRY_TO_UNIVERSES),
    }
    print(json.dumps(out, indent=2))
    print()
    print("Ejecuta 'python fetch_morningstar.py fields' para ver los 28 campos")
    print("Ejecuta 'python fetch_morningstar.py help' para ver los comandos")
    return out


def cmd_fields(args):
    """Imprime los 28 securityDataPoints con descripcion."""
    info = {
        "ClosePrice":          "Precio de cierre (en la currency del universe)",
        "MarketCap":           "Capitalizacion de mercado",
        "MarketCountryName":   "Pais del instrumento",
        "SectorName":          "Sector (11 sectores posibles)",
        "IndustryName":        "Industria (~145 industrias posibles)",
        "EquityStyleBox":      "Matriz 1-9 (1=Large Value, 9=Small Growth)",
        "QuantitativeStarRating": "Rating cuantitativo Morningstar (1-5 estrellas)",
        "PERatio":             "Price-to-Earnings (TTM)",
        "PEGRatio":            "Price/Earnings to Growth",
        "DividendYield":       "Dividend yield (%)",
        "DebtEquityRatio":     "Deuda / Equity",
        "NetMargin":           "Margen neto (%)",
        "EBTMarginYear1":      "EBT margin ultimo ano fiscal (%)",
        "ROATTM":              "Return on Assets (TTM, %)",
        "ROETTM":              "Return on Equity (TTM, %)",
        "ROEYear1":            "Return on Equity ultimo ano fiscal (%)",
        "ROICYear1":           "Return on Invested Capital (%)",
        "EPSGrowth3YYear1":    "EPS growth 3Y anualizado (%)",
        "RevenueGrowth3Y":     "Revenue growth 3Y anualizado (%)",
        "ReturnD1":            "Retorno 1 dia (%)",
        "ReturnW1":            "Retorno 1 semana (%)",
        "ReturnM0":            "Retorno mes actual (MTD, %)",
        "ReturnM1":            "Retorno 1 mes (%)",
        "ReturnM3":            "Retorno 3 meses (%)",
        "ReturnM6":            "Retorno 6 meses (%)",
        "ReturnM12":           "Retorno 12 meses (%)",
        "ReturnM36":           "Retorno 36 meses / 3Y (%)",
        "ReturnM60":           "Retorno 60 meses / 5Y (%)",
        "ReturnM120":          "Retorno 120 meses / 10Y (%)",
    }
    print(f"Total: {len(info)} securityDataPoints")
    print()
    print(f"{'Campo':<28} {'Descripcion'}")
    print("-" * 80)
    for k, v in info.items():
        print(f"{k:<28} {v}")
    return info


def resolve_universes(args):
    """Resuelve la lista de universes a partir de --universe, --country, --all."""
    codes = []
    if getattr(args, "all", False):
        codes = list(UNIVERSES.keys())
    if getattr(args, "universe", None):
        for u in args.universe:
            u = u.upper()
            if u in UNIVERSES:
                codes.append(u)
            else:
                log.warning(f"  universe {u!r} no reconocido, ignorando")
    if getattr(args, "country", None):
        for c in args.country:
            c = c.upper()
            if c in COUNTRY_TO_UNIVERSES:
                for u in COUNTRY_TO_UNIVERSES[c]:
                    if u not in codes:
                        codes.append(u)
            else:
                log.warning(f"  pais {c!r} no reconocido, ignorando")
    if not codes:
        log.error("Especifica --universe, --country o --all")
        sys.exit(1)
    return codes


def fetch_universe(s, univ_code, fields=None, term=None, page_size=50000):
    """Descarga TODOS los listings de un universe.
    Por default usa languageId=en-GB (devuelve nombres de sectores/industrias
    en ingles sin problemas de encoding). Para obtener el nombre local del
    pais, usar lang='local' (puede tener problemas de encoding en UTF-8)."""
    meta = UNIVERSES[univ_code]
    fields = fields or DATA_POINTS
    log.info(f"  downloading {univ_code} ({meta['name']}, {meta['country']}) - {meta['count']} expected")
    params = {
        "page": 1,
        "pageSize": page_size,
        "outputType": "json",
        "version": 1,
        # en-GB devuelve sectores/industrias en ingles (sin problemas de encoding)
        # La moneda y el nombre del pais ya vienen en el JSON en formato ingles
        "languageId": "en-GB",
        "currencyId": meta["currency"],
        "universeIds": f"E0EXG${univ_code}",
        "securityDataPoints": "|".join(fields),
        "sortOrder": "Name asc",
        "filters": "",
        "term": term or "",
        "subUniverseId": "",
    }
    r = get(s, f"/api/rest.svc/{TOKEN}/security/screener", params=params)
    d = r.json()
    rows = d.get("rows", [])
    log.info(f"  {univ_code}: received {len(rows)} rows")
    return rows


def cmd_search(args):
    """Busca tickers por nombre en uno o varios universes."""
    s = make_session()
    codes = resolve_universes(args)
    query = args.query
    out = OrderedDict()
    out["_meta"] = {
        "query": query,
        "fields": ["Ticker", "PerformanceId", "Name", "ClosePrice", "MarketCap", "MarketCountryName"],
        "universe_count": len(codes),
        "universe_codes": codes,
    }
    out["results"] = []
    for code in codes:
        rows = fetch_universe(s, code, term=query, page_size=200, fields=[
            "Ticker", "PerformanceId", "Name", "ClosePrice", "MarketCap", "MarketCountryName", "SectorName", "IndustryName",
        ])
        for row in rows:
            row["_universe_code"] = code
            row["_universe_name"] = UNIVERSES[code]["name"]
            out["results"].append(row)
    out["_meta"]["total_results"] = len(out["results"])
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return out


def cmd_screener(args):
    """Descarga masiva de uno o varios universes."""
    s = make_session()
    codes = resolve_universes(args)
    fields = args.fields or DATA_POINTS
    out = OrderedDict()
    out["_meta"] = {
        "endpoint": "/security/screener",
        "universe_count": len(codes),
        "field_count": len(fields),
        "fields": fields,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    out["universes"] = OrderedDict()
    total = 0
    for code in codes:
        try:
            rows = fetch_universe(s, code, fields=args.fields or DATA_POINTS)
            meta = UNIVERSES[code]
            out["universes"][code] = {
                "name": meta["name"],
                "exchange": meta["exchange"],
                "country": meta["country"],
                "currency": meta["currency"],
                "count": len(rows),
                "rows": rows,
            }
            total += len(rows)
        except Exception as e:
            log.error(f"  {code}: ERROR {e}")
            out["universes"][code] = {"error": str(e)}
        time.sleep(0.5)
    out["_meta"]["total_rows"] = total
    return out


def write_output(out, path, fmt=None):
    """Guarda el output a JSON o CSV segun extension."""
    if not path:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    fmt = fmt or path.rsplit(".", 1)[-1].lower()
    if fmt == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2, default=str)
        log.info(f"  guardado en {path} (JSON)")
    elif fmt == "csv":
        # CSV flat: una fila por (universe, asset)
        # Recolectar todos los fieldnames primero para evitar el error
        # "dict contains fields not in fieldnames"
        all_rows = []
        if "universes" in out:
            for code, u in out["universes"].items():
                if "rows" not in u: continue
                for row in u["rows"]:
                    all_rows.append({"_universe_code": code, **row})
        elif "results" in out:
            for row in out["results"]:
                all_rows.append(row)
        if not all_rows:
            log.warning("  no hay filas para escribir")
            return
        all_fieldnames = []
        for row in all_rows:
            for k in row.keys():
                if k not in all_fieldnames:
                    all_fieldnames.append(k)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_fieldnames, extrasaction="ignore", restval="")
            writer.writeheader()
            for row in all_rows:
                writer.writerow(row)
        log.info(f"  guardado en {path} (CSV, {len(all_rows)} filas, {len(all_fieldnames)} columnas)")
    else:
        log.error(f"formato desconocido: {fmt}")


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Morningstar Screener (endpoint JSON, no auth)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("mode", choices=["info", "fields", "search", "screener", "download"],
                    help="Modo de operacion (download = alias de screener)")
    ap.add_argument("query", nargs="?", help="Termino de busqueda (solo para search)")

    ap.add_argument("--universe", "-u", nargs="+",
                    help=f"Universe code(s) ({', '.join(list(UNIVERSES.keys())[:8])}, ...). Sin prefijo E0EXG$")
    ap.add_argument("--country", "-c", nargs="+",
                    help=f"Codigo de pais ISO ({', '.join(list(COUNTRY_TO_UNIVERSES.keys()))})")
    ap.add_argument("--all", action="store_true", help="Todos los universes (54)")
    ap.add_argument("--fields", "-f", nargs="+", help=f"Campos especificos a descargar (default: los {len(DATA_POINTS)})")
    ap.add_argument("--output", "-o", help="Guardar a archivo (.json o .csv)")
    ap.add_argument("-q", "--quiet", action="store_true", help="Solo JSON, sin logs")

    args = ap.parse_args()

    if args.quiet:
        logging.getLogger("morningstar").setLevel(logging.WARNING)

    if args.mode == "info":
        cmd_info(args)
        return
    if args.mode == "fields":
        cmd_fields(args)
        return
    if args.mode in ("screener", "download"):
        out = cmd_screener(args)
        write_output(out, args.output)
        return
    if args.mode == "search":
        if not args.query:
            log.error("'search' requiere un termino de busqueda")
            sys.exit(1)
        out = cmd_search(args)
        write_output(out, args.output)
        return


if __name__ == "__main__":
    main()
