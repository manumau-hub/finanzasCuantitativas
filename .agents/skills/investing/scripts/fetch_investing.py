"""
Investing.com Data Fetcher — HTML scrape + sitemap listings.

IMPORTANTE: Investing.com bloquea User-Agents no-browser con Cloudflare.
Este skill usa `curl_cffi` para impersonar Chrome 120 (TLS fingerprint real)
y asi evitar el bot challenge. `requests` puro NO funciona — devuelve el
challenge HTML de Cloudflare en lugar de los datos.

Modos disponibles:
  quote         Cotizacion de equity, commodity, currency, indice, ETF, crypto
                (precio, cambio, last_close, pair_id, OHLC, stats)
  search        Busqueda fuzzy sobre los sitemaps publicos (XML)
  sitemap       Descarga sitemaps individuales con listados de instrumentos
  historical    Historico OHLCV desde la tabla HTML de la pagina
  profile       Datos de empresa / commodity (descripcion, sector, industria)
  financials    Income / Balance / Cash Flow (anual + TTM, ultimos 5 anios)
  ratios        Ratios financieros (margenes, retornos, valuation, etc)
  dividends     Historial de dividendos
  earnings      Earnings history + calendario proximo

Uso:
    python fetch_investing.py quote apple-computer-inc
    python fetch_investing.py quote ypf-sa
    python fetch_investing.py quote gold
    python fetch_investing.py quote eur-usd
    python fetch_investing.py quote us-spx-500
    python fetch_investing.py quote bitcoin

    python fetch_investing.py search GGAL --type equity
    python fetch_investing.py search gold --type commodity
    python fetch_investing.py search ARS --type currency
    python fetch_investing.py search MERVAL --type index

    python fetch_investing.py sitemap equities
    python fetch_investing.py sitemap commodities
    python fetch_investing.py sitemap currencies
    python fetch_investing.py sitemap indices

    python fetch_investing.py historical apple-computer-inc
    python fetch_investing.py historical ypf-sa --pages 5

    python fetch_investing.py profile apple-computer-inc
    python fetch_investing.py financials apple-computer-inc --type income
    python fetch_investing.py financials apple-computer-inc --type balance
    python fetch_investing.py financials apple-computer-inc --type cashflow
    python fetch_investing.py ratios apple-computer-inc
    python fetch_investing.py dividends apple-computer-inc
    python fetch_investing.py earnings apple-computer-inc

    python fetch_investing.py quote apple-computer-inc -o quote.json
    python fetch_investing.py historical ypf-sa -o hist.json
    python fetch_investing.py search GGAL -q
"""
import argparse
import json
import logging
import re
import sys
import time
from datetime import datetime
from html import unescape

import curl_cffi

log = logging.getLogger("investing")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

BASE = "https://www.investing.com"

# Categorias de sitemaps disponibles
# Investing.com usa guion bajo en los archivos paginados: equities_ov_sitemap_2.xml
SITEMAPS = {
    "equities":   ["equities_ov_sitemap.xml"] + [f"equities_ov_sitemap_{i}.xml" for i in range(2, 10)],
    "commodities":["commodities_ov_sitemap.xml"],
    "indices":    ["indices_ov_sitemap.xml", "indices_ov_sitemap_2.xml"],
    "currencies": ["currencies_ov_sitemap.xml", "currencies_ov_sitemap_2.xml"],
    "etfs":       ["etfs_ov_sitemap.xml", "etfs_ov_sitemap_2.xml", "etfs_ov_sitemap_3.xml"],
    "crypto_coins": ["crypto_coins_ov_sitemap.xml"],
    "crypto_pairs": ["crypto_pairs_ov_sitemap.xml", "crypto_pairs_ov_sitemap_2.xml"],
    "rates_bonds":   ["rates-bonds_ov_sitemap.xml", "rates-bonds_ov_sitemap_2.xml"],
    "certificates":  ["certificates_ov_sitemap.xml"],
    "funds":         ["funds_ov_sitemap.xml"] + [f"funds_ov_sitemap_{i}.xml" for i in range(2, 12)],
}

# Tipo path-prefix en la URL
TYPE_PATH = {
    "equities":   "equities",
    "commodities":"commodities",
    "indices":    "indices",
    "currencies": "currencies",
    "etfs":       "etfs",
    "crypto":     "crypto",
}

# Headers minimos — el TLS fingerprint es lo que importa
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}


# ── HTTP helpers ────────────────────────────────────────────────────────────

def make_session():
    """Crea sesion con TLS fingerprint de Chrome 120 (necesario para CF)."""
    return curl_cffi.requests.Session(impersonate="chrome120")


def get(s, path, retries=3, sleep=2.0):
    """GET con retries y backoff. Devuelve texto o None si todos fallan.
    Cloudflare bloquea agresivamente: usar `sleep` >= 2.0 entre requests."""
    url = path if path.startswith("http") else f"{BASE}{path}"
    for i in range(retries):
        time.sleep(sleep)
        try:
            r = s.get(url, headers=DEFAULT_HEADERS, timeout=25, allow_redirects=True)
        except Exception as e:
            log.warning(f"  request error {i+1}/{retries}: {e}")
            continue
        if r.status_code == 200 and "Just a moment" not in r.text[:500]:
            return r
        if r.status_code == 429:
            log.warning(f"  429 rate-limit (intento {i+1}/{retries}), esperando...")
            time.sleep(10 + i*5)
            continue
        if r.status_code == 403:
            log.warning(f"  403 forbidden (intento {i+1}/{retries})")
            time.sleep(5 + i*3)
            continue
        if r.status_code == 404:
            return r
        log.warning(f"  status={r.status_code} intento {i+1}/{retries}")
    return None


# ── Quote / Profile / Financials ────────────────────────────────────────────

def detect_type(slug, hint=None):
    """Detecta el tipo probando cada path. Devuelve (type, url) o (None, None).
    `hint` permite forzar el orden de busqueda (e.g. ["equities", "commodities"]).
    Las categorias mas comunes primero (commodities, currencies, indices) son
    menos rate-limited que /equities/.
    """
    order = hint or ["commodities", "currencies", "indices", "etfs", "crypto", "equities"]
    for t in order:
        if t not in TYPE_PATH: continue
        path = f"/{TYPE_PATH[t]}/{slug}"
        s_local = make_session()
        r = get(s_local, path, retries=1, sleep=1.0)
        if r and r.status_code == 200 and 'class="html"' in r.text[:500]:
            return t, path
        if r and r.status_code == 403:
            log.debug(f"  403 en {path} (rate-limit o bloqueo)")
            time.sleep(2)
    return None, None


def parse_quote(html):
    """Extrae datos de cotizacion de la pagina HTML de investing.com."""
    out = {}
    # precio
    m = re.search(r'data-test="instrument-price-last"[^>]*>([0-9.,]+)<', html)
    if m: out["last"] = m.group(1)
    # JSON embebido
    m = re.search(r'"last"\s*:\s*([\d.]+)', html)
    if m: out["last_raw"] = float(m.group(1))
    m = re.search(r'"last_close"\s*:\s*([\d.]+)', html)
    if m: out["last_close"] = float(m.group(1))
    m = re.search(r'"change"\s*:\s*"?(-?[\d.]+)"?', html)
    if m: out["change"] = float(m.group(1))
    m = re.search(r'"change_pct"\s*:\s*"?(-?[\d.]+)"?', html)
    if m: out["change_pct"] = float(m.group(1))
    m = re.search(r'"bid"\s*:\s*([\d.]+)', html)
    if m: out["bid"] = float(m.group(1))
    m = re.search(r'"ask"\s*:\s*([\d.]+)', html)
    if m: out["ask"] = float(m.group(1))
    m = re.search(r'"open"\s*:\s*([\d.]+)', html)
    if m: out["open"] = float(m.group(1))
    m = re.search(r'"high"\s*:\s*([\d.]+)', html)
    if m: out["high"] = float(m.group(1))
    m = re.search(r'"low"\s*:\s*([\d.]+)', html)
    if m: out["low"] = float(m.group(1))
    m = re.search(r'"volume"\s*:\s*"?(\d+)"?', html)
    if m: out["volume"] = int(m.group(1))
    m = re.search(r'"avg_volume"\s*:\s*"?(\d+)"?', html)
    if m: out["avg_volume"] = int(m.group(1))
    m = re.search(r'"prev_close"\s*:\s*([\d.]+)', html)
    if m: out["prev_close"] = float(m.group(1))
    m = re.search(r'"pair_id"\s*:\s*(\d+)', html)
    if m: out["pair_id"] = int(m.group(1))
    m = re.search(r'"name"\s*:\s*"([^"]+)"\s*,\s*"symbol"\s*:\s*"([^"]+)"', html)
    if m: out["name"], out["symbol"] = m.group(1), m.group(2)
    m = re.search(r'"currency"\s*:\s*"([^"]+)"', html)
    if m: out["currency"] = m.group(1)
    m = re.search(r'"exchange"\s*:\s*"([^"]+)"', html)
    if m: out["exchange"] = m.group(1)
    m = re.search(r'"country"\s*:\s*"([^"]+)"', html)
    if m: out["country"] = m.group(1)
    m = re.search(r'"updated_time"\s*:\s*"?(\d+)"?', html)
    if m: out["updated_epoch"] = int(m.group(1))
    m = re.search(r'"timezone"\s*:\s*"([^"]+)"', html)
    if m: out["timezone"] = m.group(1)
    # title
    m = re.search(r'<title>([^<]+)</title>', html)
    if m: out["page_title"] = unescape(m.group(1))
    return out


def fetch_quote(s, slug, slug_type=None):
    """Cotizacion de un instrumento. Auto-detecta tipo si no se pasa."""
    if slug_type:
        path = f"/{TYPE_PATH[slug_type]}/{slug}"
    else:
        slug_type, path = detect_type(slug)
        if not path:
            return {"error": f"slug '{slug}' no encontrado en ningun sitemap"}
    log.info(f"  GET {path}")
    r = get(s, path, sleep=0.5)
    if not r or r.status_code != 200:
        return {"error": f"no se pudo obtener {path}"}
    out = parse_quote(r.text)
    out["slug"] = slug
    out["type"] = slug_type
    out["url"] = f"{BASE}{path}"
    return out


# ── Sitemap ────────────────────────────────────────────────────────────────

def fetch_sitemap(s, category):
    """Descarga todos los XML de un sitemap y devuelve URLs."""
    if category not in SITEMAPS:
        return {"error": f"categoria invalida. Opciones: {list(SITEMAPS.keys())}"}
    files = SITEMAPS[category]
    urls = []
    for fn in files:
        path = f"/{fn}"
        r = get(s, path, sleep=0.3)
        if not r or r.status_code != 200:
            log.warning(f"  skip {fn}: status={r.status_code if r else 'None'}")
            continue
        n = len(re.findall(r'<loc>', r.text))
        log.info(f"  {fn}: {n} URLs")
        urls.extend(re.findall(r'<loc>([^<]+)</loc>', r.text))
    return {"category": category, "count": len(urls), "urls": urls}


# ── Search ─────────────────────────────────────────────────────────────────

def search_sitemap(s, query, category=None, limit=20):
    """Busqueda fuzzy sobre los sitemaps. Si no se pasa categoria, prueba todas."""
    cats = [category] if category else ["equities", "commodities", "indices", "currencies", "etfs", "crypto_pairs"]
    q = query.lower()
    results = []
    for cat in cats:
        sm = fetch_sitemap(s, cat)
        if "urls" not in sm: continue
        for url in sm["urls"]:
            if q in url.lower():
                slug = url.rstrip("/").split("/")[-1]
                results.append({"category": cat, "slug": slug, "url": url})
                if len(results) >= limit: break
        if len(results) >= limit: break
    return {"query": query, "count": len(results), "results": results}


# ── Historical ─────────────────────────────────────────────────────────────

def parse_historical(html):
    """Extrae filas OHLCV de la tabla HTML de la pagina -historical-data."""
    rows = re.findall(r'<tr[^>]+class="[^"]*hist[^"]*"[^>]*>(.+?)</tr>', html, re.S)
    out = []
    for r in rows:
        tds = re.findall(r'<td[^>]*>(.+?)</td>', r, re.S)
        if len(tds) < 6: continue
        cells = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', td)).strip() for td in tds]
        out.append({
            "date": cells[0],
            "price": cells[1],
            "open": cells[2],
            "high": cells[3],
            "low": cells[4],
            "vol": cells[5],
            "change_pct": cells[6] if len(cells) > 6 else None,
        })
    return out


def fetch_historical(s, slug, pages=1, slug_type=None):
    """Historico desde la tabla HTML. `pages` indica paginacion."""
    if not slug_type:
        slug_type, base_path = detect_type(slug)
        if not base_path:
            return {"error": f"slug '{slug}' no encontrado"}
    else:
        base_path = f"/{TYPE_PATH[slug_type]}/{slug}"

    all_rows = []
    for p in range(1, pages + 1):
        path = f"{base_path}-historical-data" if p == 1 else f"{base_path}-historical-data/{p}"
        log.info(f"  GET {path}")
        r = get(s, path, sleep=0.5)
        if not r or r.status_code != 200:
            return {"error": f"no se pudo obtener {path}", "partial": all_rows}
        rows = parse_historical(r.text)
        if not rows:
            log.warning(f"  sin filas en {path}")
            break
        all_rows.extend(rows)
        time.sleep(0.5)
    return {"slug": slug, "type": slug_type, "count": len(all_rows), "rows": all_rows}


# ── Profile ────────────────────────────────────────────────────────────────

def fetch_profile(s, slug, slug_type=None):
    """Datos de la empresa / commodity desde /-company-profile."""
    if not slug_type:
        slug_type, _ = detect_type(slug)
    if not slug_type:
        return {"error": f"slug '{slug}' no encontrado"}
    prefix = TYPE_PATH[slug_type]
    path = f"/{prefix}/{slug}-company-profile"
    log.info(f"  GET {path}")
    r = get(s, path, sleep=0.5)
    if not r or r.status_code != 200:
        return {"error": f"no se pudo obtener {path}"}
    html = r.text
    out = {"slug": slug, "type": slug_type, "url": f"{BASE}{path}"}
    # description
    m = re.search(r'<meta name="description" content="([^"]+)"', html)
    if m: out["description"] = unescape(m.group(1))
    # industry/sector/country suelen estar en tablas de pares (label, value)
    pairs = re.findall(r'>([A-Z][A-Za-z ]{2,40})</[a-z][^>]*>\s*<[a-z][^>]*>([^<]{1,100})<', html)
    for label, value in pairs:
        l = label.strip()
        v = value.strip()
        if not v or len(v) > 200: continue
        kl = l.lower()
        if "sector" in kl: out["sector"] = v
        elif "industry" in kl: out["industry"] = v
        elif "country" in kl: out["country"] = v
        elif "employees" in kl: out["employees"] = v
        elif "headquarters" in kl or "headquarter" in kl: out["headquarters"] = v
        elif "founded" in kl or "ipo" in kl: out["founded"] = v
        elif "website" in kl: out["website"] = v
        elif "ceo" in kl: out["ceo"] = v
    # name y symbol
    m = re.search(r'"name":"([^"]+)"\s*,\s*"symbol":"([^"]+)"', html)
    if m: out["name"], out["symbol"] = m.group(1), m.group(2)
    return out


# ── Financials ─────────────────────────────────────────────────────────────

FINANCIAL_TYPES = {
    "income":    "-income-statement",
    "balance":   "-balance-sheet",
    "cashflow":  "-cash-flow",
    "ratios":    "-ratios",
}

def fetch_financials(s, slug, ftype="income", slug_type=None):
    """Income / Balance / Cash Flow / Ratios. Devuelve dict con los rows parseados."""
    if ftype not in FINANCIAL_TYPES:
        return {"error": f"ftype invalido. Opciones: {list(FINANCIAL_TYPES.keys())}"}
    if not slug_type:
        slug_type, _ = detect_type(slug)
    if not slug_type:
        return {"error": f"slug '{slug}' no encontrado"}
    prefix = TYPE_PATH[slug_type]
    suffix = FINANCIAL_TYPES[ftype]
    path = f"/{prefix}/{slug}{suffix}"
    log.info(f"  GET {path}")
    r = get(s, path, sleep=0.5)
    if not r or r.status_code != 200:
        return {"error": f"no se pudo obtener {path}"}
    html = r.text
    out = {"slug": slug, "type": slug_type, "ftype": ftype, "url": f"{BASE}{path}"}
    # la tabla tiene thead con periodos (TTM, 2024, 2023, ...) y tbody con filas
    # periodo headers
    headers = re.findall(r'<th[^>]+scope="col"[^>]*>\s*<span[^>]*>([^<]+)</span>', html)
    if not headers:
        # alternativa
        headers = re.findall(r'<th[^>]*>([A-Za-z0-9/]{1,20})</th>', html)
    out["periods"] = headers[:25]
    # filas: <tr> con <td label> + <td values>
    trs = re.findall(r'<tr[^>]*>(.+?)</tr>', html, re.S)
    rows = []
    for tr in trs:
        tds = re.findall(r'<td[^>]*>(.+?)</td>', tr, re.S)
        if len(tds) < 2: continue
        cells = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', td)).strip() for td in tds]
        label = cells[0]
        if not label or len(label) > 100: continue
        rows.append({"label": label, "values": cells[1:26]})
    out["count"] = len(rows)
    out["rows"] = rows
    return out


# ── Dividends ──────────────────────────────────────────────────────────────

def fetch_dividends(s, slug, slug_type=None):
    """Historial de dividendos."""
    if not slug_type:
        slug_type, _ = detect_type(slug)
    if not slug_type:
        return {"error": f"slug '{slug}' no encontrado"}
    prefix = TYPE_PATH[slug_type]
    path = f"/{prefix}/{slug}-dividends"
    log.info(f"  GET {path}")
    r = get(s, path, sleep=0.5)
    if not r or r.status_code != 200:
        return {"error": f"no se pudo obtener {path}"}
    html = r.text
    out = {"slug": slug, "type": slug_type, "url": f"{BASE}{path}"}
    rows = re.findall(r'<tr[^>]+class="[^"]*hist[^"]*"[^>]*>(.+?)</tr>', html, re.S)
    divs = []
    for tr in rows:
        tds = re.findall(r'<td[^>]*>(.+?)</td>', tr, re.S)
        if len(tds) < 3: continue
        cells = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', td)).strip() for td in tds]
        divs.append(cells)
    out["count"] = len(divs)
    out["rows"] = divs
    return out


# ── Earnings ───────────────────────────────────────────────────────────────

def fetch_earnings(s, slug, slug_type=None):
    """Earnings history + calendario."""
    if not slug_type:
        slug_type, _ = detect_type(slug)
    if not slug_type:
        return {"error": f"slug '{slug}' no encontrado"}
    prefix = TYPE_PATH[slug_type]
    path = f"/{prefix}/{slug}-earnings"
    log.info(f"  GET {path}")
    r = get(s, path, sleep=0.5)
    if not r or r.status_code != 200:
        return {"error": f"no se pudo obtener {path}"}
    html = r.text
    out = {"slug": slug, "type": slug_type, "url": f"{BASE}{path}"}
    # buscar EPS rows en la tabla
    trs = re.findall(r'<tr[^>]+class="[^"]*hist[^"]*"[^>]*>(.+?)</tr>', html, re.S)
    earnings = []
    for tr in trs:
        tds = re.findall(r'<td[^>]*>(.+?)</td>', tr, re.S)
        if len(tds) < 3: continue
        cells = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', td)).strip() for td in tds]
        earnings.append(cells)
    out["count"] = len(earnings)
    out["rows"] = earnings
    return out


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Investing.com data fetcher (HTML scrape)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("mode", choices=[
        "quote", "search", "sitemap", "historical",
        "profile", "financials", "ratios", "dividends", "earnings",
    ], help="Modo de operacion")
    ap.add_argument("target", nargs="?", help="Slug del instrumento (quote/historical/profile/...) o query de busqueda")
    ap.add_argument("--type", choices=list(TYPE_PATH.keys()),
                    help="Tipo de instrumento (auto-detectado si se omite). "
                         "Opciones: " + ", ".join(TYPE_PATH.keys()))
    ap.add_argument("--category", choices=list(SITEMAPS.keys()),
                    help="Categoria de sitemap (search/sitemap). "
                         "Opciones: " + ", ".join(SITEMAPS.keys()))
    ap.add_argument("--ftype", choices=list(FINANCIAL_TYPES.keys()), default="income",
                    help="Tipo de financial (income/balance/cashflow)")
    ap.add_argument("--pages", type=int, default=1,
                    help="Cantidad de paginas de historico (default: 1 = ~23 dias)")
    ap.add_argument("--limit", type=int, default=20, help="Limite de resultados de search (default: 20)")
    ap.add_argument("-o", "--output", help="Guardar output a archivo JSON")
    ap.add_argument("-q", "--quiet", action="store_true", help="Solo JSON (sin logs)")

    args = ap.parse_args()

    if args.quiet:
        logging.getLogger("investing").setLevel(logging.WARNING)

    s = make_session()

    if args.mode == "quote":
        out = fetch_quote(s, args.target, args.type)
    elif args.mode == "search":
        out = search_sitemap(s, args.target, args.category, args.limit)
    elif args.mode == "sitemap":
        out = fetch_sitemap(s, args.target) if args.target else fetch_sitemap(s, args.category)
    elif args.mode == "historical":
        out = fetch_historical(s, args.target, args.pages, args.type)
    elif args.mode == "profile":
        out = fetch_profile(s, args.target, args.type)
    elif args.mode == "financials":
        out = fetch_financials(s, args.target, args.ftype, args.type)
    elif args.mode == "ratios":
        out = fetch_financials(s, args.target, "ratios", args.type)
    elif args.mode == "dividends":
        out = fetch_dividends(s, args.target, args.type)
    elif args.mode == "earnings":
        out = fetch_earnings(s, args.target, args.type)
    else:
        ap.error(f"modo desconocido: {args.mode}")

    out["_fetched_at"] = datetime.utcnow().isoformat() + "Z"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        log.info(f"  guardado en {args.output}")
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
