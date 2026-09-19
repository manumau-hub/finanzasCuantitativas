"""
MarketScreener Client — Scraper de datos financieros gratuitos (S&P Capital IQ)

Extrae earnings transcripts, cotizaciones, perfiles, financials, valuacion,
consenso de analistas, ratings, noticias, insider trading, accionistas y
gobierno corporativo de MarketScreener sin necesidad de API key ni registro.

Uso desde CLI:
    python marketscreener_client.py search AAPL
    python marketscreener_client.py quote AAPL
    python marketscreener_client.py transcript GGAL
    python marketscreener_client.py profile AAPL
    python marketscreener_client.py financials AAPL --statement income
    python marketscreener_client.py valuation AAPL
    python marketscreener_client.py consensus AAPL
    python marketscreener_client.py ratings AAPL
    python marketscreener_client.py news AAPL
    python marketscreener_client.py calendar AAPL

Dependencias: requests, beautifulsoup4
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from curl_cffi import requests
from bs4 import BeautifulSoup, Tag

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

BASE_URL = "https://www.marketscreener.com"

# Headers que imitan un navegador real
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Connection": "keep-alive",
}

# Cookies iniciales tipicas
COOKIES = {
    "accept_cookie": "1",
    "datadome": "1",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("marketscreener")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_session() -> requests.Session:
    """Crea una sesion con headers y cookies de navegador real usando curl_cffi."""
    sess = requests.Session(impersonate="chrome131")
    sess.headers.update(HEADERS)
    sess.cookies.update(COOKIES)
    # Visitar homepage para obtener cookies del sitio
    try:
        sess.get("https://www.marketscreener.com", timeout=30)
    except Exception:
        pass
    return sess


def _rate_limit():
    """Espera al menos 1.5 segundos desde el ultimo request."""
    global LAST_REQUEST
    elapsed = time.time() - LAST_REQUEST
    if elapsed < 1.5:
        time.sleep(1.5 - elapsed)
    LAST_REQUEST = time.time()


def _request(url: str, session: Optional[requests.Session] = None) -> requests.Response:
    """Request con rate limiting y User-Agent."""
    _rate_limit()
    sess = session or _create_session()
    resp = sess.get(url, timeout=30)
    resp.raise_for_status()
    return resp


def _soup(url: str, session: Optional[requests.Session] = None) -> BeautifulSoup:
    """Obtiene HTML y devuelve BeautifulSoup."""
    resp = _request(url, session)
    return BeautifulSoup(resp.text, "html.parser")


def _extract_text(el: Optional[Tag]) -> str:
    """Extrae texto limpio de un tag."""
    if el is None:
        return ""
    return el.get_text(strip=True)


def _find_company_id(ticker: str) -> Tuple[str, str, str]:
    """
    Busca un ticker en MarketScreener y devuelve (company_id, name_slug, full_name).

    Busca en resultados de busqueda y extrae el ID numerico de la URL.
    """
    url = f"{BASE_URL}/search/?q={ticker}"
    soup = _soup(url)

    # Buscar el primer link a /quote/stock/ que contenga el ticker
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/quote/stock/" in href and href.endswith("/"):
            # Extraer ID: /quote/stock/APPLE-INC-4849/ -> 4849
            match = re.search(r"/([A-Za-z0-9-]+)-(\d+)/$", href)
            if match:
                name_slug = match.group(1)
                cid = match.group(2)
                full_name = _extract_text(a)
                # Verificar que el ticker este mencionado cerca
                return cid, name_slug, full_name

    raise ValueError(
        f"No se encontro el ticker '{ticker}' en MarketScreener. "
        "Verifique que el ticker sea correcto."
    )


def _company_url(cid: str, slug: str, page: str = "") -> str:
    """Construye URL base de una company."""
    base = f"{BASE_URL}/quote/stock/{slug}-{cid}/"
    if page:
        return base + page
    return base


def _parse_table_rows(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Parsea tablas HTML del sitio y devuelve lista de filas como dicts.

    Implementacion generica para las tablas de MarketScreener.
    """
    rows = []
    for table in soup.find_all("table"):
        headers = []
        thead = table.find("thead")
        if thead:
            headers = [_extract_text(th) for th in thead.find_all("th")]

        tbody = table.find("tbody")
        if not tbody:
            tbody = table
        for tr in tbody.find_all("tr"):
            cells = [_extract_text(td) for td in tr.find_all("td")]
            if not cells:
                continue
            if headers and len(headers) == len(cells):
                rows.append(dict(zip(headers, cells)))
            else:
                rows.append({f"col_{i}": v for i, v in enumerate(cells)})
    return rows


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class MarketScreenerClient:
    """Cliente para scraping de datos financieros de MarketScreener."""

    def __init__(self, min_delay: float = 1.5):
        self.min_delay = min_delay
        self._last_request = 0.0
        self._session = requests.Session(impersonate="chrome131")
        self._session.headers.update(HEADERS)
        self._session.cookies.update(COOKIES)
        # Inicializar cookies visitando homepage
        try:
            self._session.get(BASE_URL, timeout=30)
        except Exception:
            pass

    def _rate_limit(self):
        elapsed = time.time() - self._last_request
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self._last_request = time.time()

    def _get(self, url: str) -> requests.Response:
        self._rate_limit()
        resp = self._session.get(url, timeout=30)
        resp.raise_for_status()
        return resp

    def _soup(self, url: str) -> BeautifulSoup:
        return BeautifulSoup(self._get(url).text, "html.parser")

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_company(self, query: str) -> List[Dict[str, str]]:
        """
        Busca empresas en MarketScreener por ticker o nombre.

        Returns:
            List[Dict]: cada resultado con 'name', 'ticker', 'exchange', 'type', 'id', 'url'
        """
        url = f"{BASE_URL}/search/?q={query}"
        soup = self._soup(url)
        results = []

        # Tabla de resultados: buscar links a /quote/stock/ en cualquier columna
        for table in soup.find_all("table"):
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 2:
                    continue
                # Buscar link en cualquier columna
                link = None
                for td in tds:
                    a = td.find("a", href=lambda h: h and "/quote/stock/" in h if h else False)
                    if a:
                        link = a
                        break
                if not link:
                    continue
                href = link["href"]
                match = re.search(r"-(\d+)/$", href)
                cid = match.group(1) if match else ""
                name = _extract_text(link)
                # Extraer ticker, exchange, type de las celdas
                ticker = ""
                exchange = ""
                typ = ""
                for td in tds:
                    text = _extract_text(td)
                    if text and text.isupper() and len(text) <= 5 and text != name.upper() and text != name:
                        ticker = text
                        break
                for td in tds:
                    text = _extract_text(td)
                    if text and text not in (name, ticker) and len(text) > 5 and not text.startswith(("$", "+", "-")):
                        if not exchange:
                            exchange = text
                        elif not typ:
                            typ = text
                results.append({
                    "name": name,
                    "ticker": ticker,
                    "exchange": exchange,
                    "type": typ,
                    "id": cid,
                    "url": href,
                })

        return results

    # ------------------------------------------------------------------
    # Resolve ID
    # ------------------------------------------------------------------

    def resolve(self, ticker: str) -> Tuple[str, str, str]:
        """
        Resuelve un ticker a (company_id, name_slug, full_name).

        Ejemplo: resolve("AAPL") -> ("4849", "APPLE-INC", "APPLE INC.")
        """
        results = self.search_company(ticker)
        if not results:
            raise ValueError(f"No se encontro ticker '{ticker}'")

        # Preferir match exacto de ticker
        for r in results:
            if r["ticker"].upper() == ticker.upper():
                return r["id"], r["url"].rstrip("/").split("/")[-1].replace(f"-{r['id']}", ""), r["name"]

        # Usar el primero
        r = results[0]
        return r["id"], r["url"].rstrip("/").split("/")[-1].replace(f"-{r['id']}", ""), r["name"]

    def _ensure_resolved(
        self, ticker: str, cid: Optional[str] = None, slug: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """Devuelve (cid, slug, name). Si faltan, resuelve."""
        if cid and slug:
            return cid, slug, ""
        cid_res, slug_res, name = self.resolve(ticker)
        return cid_res, slug_res, name

    # ------------------------------------------------------------------
    # Quote / Summary
    # ------------------------------------------------------------------

    def get_quote(self, ticker: str, cid: Optional[str] = None, slug: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene cotizacion actual y datos basicos de una empresa.

        Returns:
            Dict con price, change, change_pct, name, ticker, isin, sector, exchange
        """
        cid, slug, name = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug)
        soup = self._soup(url)

        quote: Dict[str, Any] = {
            "ticker": ticker.upper(),
            "name": name,
            "cid": cid,
        }

        # Extraer ISIN del header (esta en ## tags)
        h2_tags = soup.find_all("h2")
        for h2 in h2_tags:
            text = _extract_text(h2)
            if re.match(r"^[A-Z]{2}[A-Z0-9]{10}$", text.strip()):
                quote["isin"] = text.strip()
                break

        # Extraer sector del breadcrumb/sidebar
        sector_link = soup.find("a", href=lambda h: h and "sectors" in h)
        if sector_link:
            quote["sector"] = _extract_text(sector_link)

        # Precio y cambio - buscar en tablas de header
        # El markdown muestra el precio en primera tabla con <sup>USD</sup>
        price_table = soup.find("table")
        if price_table:
            tds = price_table.find_all("td")
            for i, td in enumerate(tds):
                text = _extract_text(td)
                sup = td.find("sup")
                if sup and sup.get_text(strip=True) == "USD":
                    quote["price"] = text.replace("USD", "").strip()
                if text.startswith("+") or text.startswith("-"):
                    if "%" in text:
                        quote["change_pct"] = text
                    elif i > 0 and not quote.get("change"):
                        prev_td = tds[i - 1]
                        quote["change"] = _extract_text(prev_td) + " " + text

        # Intentar extraer de las tablas de resumen mas abajo
        # Buscar por celdas que contengan numeros con formato USD
        for td in soup.find_all("td"):
            text = _extract_text(td)
            sup = td.find("sup")
            if sup and sup.get_text(strip=True) == "USD":
                quote["price"] = text.replace("USD", "").strip()
                # El cambio esta en la celda siguiente
                next_td = td.find_next("td")
                if next_td:
                    change_text = _extract_text(next_td)
                    if change_text and (
                        change_text.startswith("+") or change_text.startswith("-")
                    ):
                        # Puede ser "$X.XX" o "X.XX%"
                        if "%" in change_text:
                            quote["change_pct"] = change_text
                        else:
                            quote["change"] = change_text
                            # Siguiente td podria tener el %
                            next_next = next_td.find_next("td")
                            if next_next:
                                pct = _extract_text(next_next)
                                if "%" in pct:
                                    quote["change_pct"] = pct

        # Buscar en el texto el precio con formato "310.57USD"
        # (a veces el sup rompe el parsing)
        if not quote.get("price"):
            text = soup.get_text()
            # Buscar patron: numero con decimal seguido de USD
            price_match = re.search(r"(\d+[\.,]\d+)\s*USD", text)
            if price_match:
                quote["price"] = price_match.group(1)
                # Buscar cambio cerca
                change_match = re.search(
                    r"([+-]\d+[\.,]\d+)\s*%\s*\|", text
                )
                if change_match:
                    quote["change_pct"] = change_match.group(1) + "%"

        return quote

    # ------------------------------------------------------------------
    # Profile / Company
    # ------------------------------------------------------------------

    def get_profile(self, ticker: str, cid: Optional[str] = None, slug: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene perfil completo de la empresa.

        Returns:
            Dict con name, ticker, isin, sector, industry, description,
            employees, revenue, net_income, website, country, address, phone
        """
        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug, "company/")
        soup = self._soup(url)

        profile: Dict[str, Any] = {
            "ticker": ticker.upper(),
            "cid": cid,
        }

        # Nombre del H1 o del primer H1/h2
        h1 = soup.find("h1")
        if h1:
            profile["name"] = _extract_text(h1).replace("Company ", "").strip()

        # ISIN del H2
        for h2 in soup.find_all("h2"):
            text = _extract_text(h2)
            if re.match(r"^[A-Z]{2}[A-Z0-9]{10}$", text.strip()):
                profile["isin"] = text.strip()

        # Sector del link de sector
        sector_link = soup.find("a", href=lambda h: h and "sectors" in h)
        if sector_link:
            profile["sector"] = _extract_text(sector_link)

        # Business description
        desc_header = soup.find(["h3", "h4"], string=re.compile(r"Business description", re.I))
        if desc_header:
            desc_p = desc_header.find_next("p")
            if desc_p:
                profile["description"] = _extract_text(desc_p)

        # Employees: buscar en el texto "Number of employees:" o "Employees"
        text = soup.get_text()
        emp_match = re.search(r"(?:Number of employees|Employees)[:\s]*([\d,]+)", text)
        if emp_match:
            profile["employees"] = int(emp_match.group(1).replace(",", ""))

        # Address, website, phone desde la seccion "Company details"
        details_header = soup.find(
            ["h3", "h4", "h5"], string=re.compile(r"Company details", re.I)
        )
        if details_header:
            details_div = details_header.find_next(["div", "p"])
            if details_div:
                details_text = details_div.get_text("\n", strip=True)
                # Website (primer http/https)
                web_match = re.search(r"(https?://[^\s\n]+)", details_text)
                if web_match:
                    profile["website"] = web_match.group(1).rstrip(")")
                # Phone: patron +(XXX) XXX-XXXX
                phone_match = re.search(
                    r"(\+?\d[\d\s\-\(\)]{7,})", details_text
                )
                if phone_match:
                    profile["phone"] = phone_match.group(1).strip()

        # Address: primer parrafo antes del telefono
        if details_div:
            lines = details_div.get_text("\n", strip=True).split("\n")
            # Filtrar lineas que no sean website ni phone ni esten vacias
            addr_lines = [
                l
                for l in lines
                if l
                and not l.startswith("http")
                and not l.startswith("+")
                and not l.startswith("(")
            ]
            if addr_lines:
                profile["address"] = ", ".join(addr_lines[:3])

        # Revenue y Net Income de la tabla de ventas (tabla de Sales by Activity)
        for table in soup.find_all("table"):
            ths = table.find_all("th")
            if any("Revenue" in _extract_text(th) for th in ths):
                tds = table.find_all("td")
                values = [_extract_text(td) for td in tds if _extract_text(td)]
                if values:
                    # El ultimo valor es el mas reciente
                    profile["revenue"] = values[-1]

        return profile

    # ------------------------------------------------------------------
    # Financials
    # ------------------------------------------------------------------

    def get_financials(
        self,
        ticker: str,
        statement: str = "income",
        cid: Optional[str] = None,
        slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene estados financieros.

        Args:
            ticker: Ticker de la empresa
            statement: Tipo de estado ('income', 'balance', 'cashflow', 'ratios')

        Returns:
            Dict con los datos financieros por periodo
        """
        page_map = {
            "income": "finances-income-statement/",
            "balance": "finances-balance-sheet/",
            "cashflow": "finances-cash-flow-statement/",
            "ratios": "finances-ratios/",
        }
        page = page_map.get(statement, "finances-income-statement/")

        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug, page)
        soup = self._soup(url)

        result: Dict[str, Any] = {
            "ticker": ticker.upper(),
            "statement": statement,
            "periods": [],
            "data": {},
        }

        # Parsear tablas financieras
        # Las tablas tienen encabezados con años y filas con cuentas
        tables = soup.find_all("table")
        for table in tables:
            rows_data = self._parse_financial_table(table)
            if rows_data and len(rows_data) > 1:
                # Primera fila son headers (años)
                periods = rows_data[0]
                result["periods"] = periods
                for row in rows_data[1:]:
                    if len(row) >= 2:
                        metric = row[0]
                        values = row[1:]
                        result["data"][metric] = dict(zip(periods[1:], values))

        return result

    def _parse_financial_table(self, table: Tag) -> List[List[str]]:
        """Parsea una tabla financiera y devuelve lista de filas."""
        rows = []
        for tr in table.find_all("tr"):
            cells = []
            for tag in tr.find_all(["th", "td"]):
                text = _extract_text(tag)
                cells.append(text)
            if cells:
                rows.append(cells)
        return rows

    # ------------------------------------------------------------------
    # Valuation
    # ------------------------------------------------------------------

    def get_valuation(
        self, ticker: str, cid: Optional[str] = None, slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene ratios de valuacion.

        Returns:
            Dict con pe_ratio, pb_ratio, ev_ebitda, market_cap, dividend_yield, etc.
        """
        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug, "valuation/")
        soup = self._soup(url)

        valuation: Dict[str, Any] = {
            "ticker": ticker.upper(),
        }

        # Parsear la tabla de valuacion principal
        # Buscar la tabla "Company Valuation: ..."
        tables = soup.find_all("table")
        for table in tables:
            rows = self._parse_financial_table(table)
            for row in rows:
                if len(row) >= 2:
                    metric = row[0].strip().lower()
                    # El ultimo valor es el mas reciente (estimado actual)
                    current_val = row[-1] if len(row) > 1 else ""

                    # Normalizar metricas
                    if "capitalization" in metric:
                        valuation["market_cap"] = current_val
                    elif "enterprise value" in metric and "ev" not in valuation:
                        valuation["enterprise_value"] = current_val
                    elif "p/e ratio" in metric or "pe ratio" in metric:
                        valuation["pe_ratio"] = current_val
                    elif "pbr" in metric or "price/book" in metric:
                        valuation["pb_ratio"] = current_val
                    elif "ev / ebitda" in metric:
                        valuation["ev_ebitda"] = current_val
                    elif "ev / sales" in metric or "ev / revenue" in metric:
                        valuation["ev_sales"] = current_val
                    elif "ev / ebit" in metric:
                        valuation["ev_ebit"] = current_val
                    elif "dividend per share" in metric:
                        valuation["dividend_per_share"] = current_val
                    elif "rate of return" in metric or "yield" in metric:
                        valuation["dividend_yield"] = current_val
                    elif "eps" in metric and "revision" not in metric:
                        valuation["eps"] = current_val
                    elif "net sales" in metric or "revenue" in metric:
                        valuation["revenue"] = current_val
                    elif "net income" in metric:
                        valuation["net_income"] = current_val
                    elif "net debt" in metric:
                        valuation["net_debt"] = current_val
                    elif "peg" in metric:
                        valuation["peg_ratio"] = current_val
                    elif "fcf yield" in metric:
                        valuation["fcf_yield"] = current_val
                    elif "ev / fcf" in metric:
                        valuation["ev_fcf"] = current_val

        # Extraer P/E ratio y EV/Sales de las tarjetas de resumen
        # (los que aparecen en la parte superior derecha del summary page)
        text = soup.get_text()

        # Buscar patrones como "P/E ratio 2026 * 33.6x"
        pe_match = re.search(r"P/E ratio\s+(\d{4})\s*\*?\s*([\d.]+)x", text)
        if pe_match and not valuation.get("pe_ratio"):
            valuation["pe_ratio"] = pe_match.group(2) + "x"

        ev_sales_match = re.search(r"EV / Sales\s+(\d{4})\s*\*?\s*([\d.]+)x", text)
        if ev_sales_match and not valuation.get("ev_sales"):
            valuation["ev_sales"] = ev_sales_match.group(2) + "x"

        # Precio max/min 52 semanas
        low_match = re.search(r"52 week\s+low[:\s]*([\d,.]+)", text, re.I)
        if low_match:
            valuation["52w_low"] = low_match.group(1)
        high_match = re.search(r"52 week\s+high[:\s]*([\d,.]+)", text, re.I)
        if high_match:
            valuation["52w_high"] = high_match.group(1)

        return valuation

    # ------------------------------------------------------------------
    # Consensus
    # ------------------------------------------------------------------

    def get_consensus(
        self, ticker: str, cid: Optional[str] = None, slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene consenso de analistas.

        Returns:
            Dict con mean_consensus, num_analysts, target_mean, target_high,
            target_low, buy, hold, sell, etc.
        """
        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug, "consensus/")
        soup = self._soup(url)

        consensus: Dict[str, Any] = {
            "ticker": ticker.upper(),
        }

        # Extraer del texto visible (multi-linea: label y valor en lineas separadas)
        text = soup.get_text("\n", strip=True)

        # Parsear multi-linea: MarketScreener pone label y valor en lineas separadas
        lines = text.split("\n")
        in_consensus = False
        for i, line in enumerate(lines):
            s = line.strip()
            if s == "Analysts' Consensus":
                in_consensus = True
                continue
            if not in_consensus:
                continue
            if any(s.startswith(x) for x in ["Ratings", "Calendar", "Income"]):
                break
            if i + 1 >= len(lines):
                break
            nxt = lines[i + 1].strip()
            if s == "Mean consensus":
                consensus["mean_consensus"] = nxt
            elif s == "Number of Analysts" and nxt.isdigit():
                consensus["num_analysts"] = int(nxt)
            elif s == "Last Close Price":
                consensus["last_close"] = nxt.replace("USD", "").strip()
            elif s == "Average target price":
                consensus["target_mean"] = nxt.replace("USD", "").strip()
            elif s == "Spread / Average Target":
                consensus["spread"] = nxt
            elif s == "High Price Target":
                consensus["target_high"] = nxt.replace("USD", "").strip()
            elif s == "Low Price Target":
                consensus["target_low"] = nxt.replace("USD", "").strip()

        return consensus

    # ------------------------------------------------------------------
    # Ratings (Surperformance)
    # ------------------------------------------------------------------

    def get_ratings(
        self, ticker: str, cid: Optional[str] = None, slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene ratings Surperformance (Trader, Investor, Global, Quality, ESG).

        Returns:
            Dict con trader_rating, investor_rating, global_rating, etc.
        """
        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug, "ratings/")
        soup = self._soup(url)

        ratings: Dict[str, Any] = {
            "ticker": ticker.upper(),
        }

        text = soup.get_text()

        # Buscar las secciones de ratings
        # Trader, Investor, Global, Quality, ESG MSCI
        rating_sections = ["Trader", "Investor", "Global", "Quality"]

        for section in rating_sections:
            # Buscar "Trader 8/10" o "Trader 7.5/10"
            pattern = rf"{re.escape(section)}\s*(\d+[\.,]?\d*)/10"
            match = re.search(pattern, text)
            if match:
                ratings[f"{section.lower()}_rating"] = match.group(1)

        # ESG MSCI rating (CCC a AAA)
        esg_match = re.search(r"ESG MSCI[:\s]*\n*(AAA|AA|A|BBB|BB|B|CCC)", text)
        if esg_match:
            ratings["esg_msci"] = esg_match.group(1)

        return ratings

    # ------------------------------------------------------------------
    # News
    # ------------------------------------------------------------------

    def get_news(
        self, ticker: str, max_items: int = 20, cid: Optional[str] = None, slug: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Obtiene noticias recientes.

        Returns:
            List[Dict] con headline, date, source, url
        """
        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug, "news/")
        soup = self._soup(url)

        news_list = []

        # Las noticias estan en tablas con columnas: fecha, titular, fuente
        for table in soup.find_all("table"):
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 2:
                    continue

                link = tds[1].find("a") if len(tds) > 1 else None
                if not link or not link.get("href"):
                    continue

                headline = _extract_text(link)
                href = link["href"]
                if not href.startswith("http"):
                    href = BASE_URL + href

                date_text = _extract_text(tds[0]) if len(tds) > 0 else ""
                source = _extract_text(tds[2]) if len(tds) > 2 else ""

                news_list.append({
                    "headline": headline,
                    "date": date_text,
                    "source": source.strip(),
                    "url": href,
                })

                if len(news_list) >= max_items:
                    return news_list

        return news_list

    # ------------------------------------------------------------------
    # Transcripts
    # ------------------------------------------------------------------

    def get_transcripts_list(
        self, ticker: str, max_items: int = 10, cid: Optional[str] = None, slug: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Obtiene lista de earnings transcripts disponibles.

        Busca primero en la pagina de transcripts dedicada y luego en la de resumen.

        Returns:
            List[Dict] con title, date, quarter, url
        """
        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        transcripts = []

        # 1. Buscar en la pagina de news-call-transcripts (lista completa)
        try:
            url = _company_url(cid, slug, "news-call-transcripts/")
            soup = self._soup(url)
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/news/transcript-" in href:
                    title = _extract_text(a)
                    full_url = href if href.startswith("http") else BASE_URL + href
                    date_str = ""
                    q_match = re.search(r"Q([1-4])\s+(\d{4})", title)
                    quarter = f"Q{q_match.group(1)} {q_match.group(2)}" if q_match else ""
                    date_match = re.search(r"([A-Z][a-z]+\.?\s+\d+,\s+\d{4})", title)
                    if date_match:
                        date_str = date_match.group(1)
                    transcripts.append({
                        "title": title,
                        "date": date_str,
                        "quarter": quarter,
                        "url": full_url,
                    })
                    if len(transcripts) >= max_items:
                        break
        except Exception:
            pass

        # 2. Si no hay, buscar en la pagina de resumen
        if not transcripts:
            try:
                url = _company_url(cid, slug)
                soup = self._soup(url)
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/news/transcript-" in href:
                        title = _extract_text(a)
                        full_url = href if href.startswith("http") else BASE_URL + href
                        date_match = re.search(r"([A-Z][a-z]+\.?\s+\d+,\s+\d{4})", title)
                        date_str = date_match.group(1) if date_match else ""
                        q_match = re.search(r"Q([1-4])\s+(\d{4})", title)
                        quarter = f"Q{q_match.group(1)} {q_match.group(2)}" if q_match else ""
                        transcripts.append({
                            "title": title,
                            "date": date_str,
                            "quarter": quarter,
                            "url": full_url,
                        })
                        if len(transcripts) >= max_items:
                            break
            except Exception:
                pass

        return transcripts

    def get_transcript(
        self, ticker: str, cid: Optional[str] = None, slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene el ultimo earnings transcript disponible.

        Returns:
            Dict con title, date, participants, prepared_remarks, qa_section
        """
        # Primero obtener lista de transcripts
        transcripts = self.get_transcripts_list(ticker, max_items=1, cid=cid, slug=slug)
        if not transcripts:
            return {
                "ticker": ticker.upper(),
                "error": "No se encontraron transcripts para este ticker",
            }

        latest = transcripts[0]
        return self._fetch_transcript_detail(latest["url"], ticker, latest)

    def get_transcript_by_quarter(
        self, ticker: str, quarter: str, year: str,
        cid: Optional[str] = None, slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene un earnings transcript especifico por quarter y año.

        Args:
            ticker: Ticker de la empresa
            quarter: "Q1", "Q2", "Q3", "Q4"
            year: "2025", "2026", etc.
        """
        transcripts = self.get_transcripts_list(ticker, max_items=50, cid=cid, slug=slug)
        for t in transcripts:
            if quarter in t.get("quarter", "") and year in t.get("quarter", ""):
                return self._fetch_transcript_detail(t["url"], ticker, t)

        return {
            "ticker": ticker.upper(),
            "error": f"No se encontro transcript para {ticker} {quarter} {year}",
        }

    def _fetch_transcript_detail(
        self, url: str, ticker: str, meta: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Parsea el detalle de un transcript desde su pagina.

        El transcript tiene secciones: Operator, Question, Answer
        con participantes listados.
        """
        soup = self._soup(url)
        text = soup.get_text("\n", strip=True)

        result: Dict[str, Any] = {
            "ticker": ticker.upper(),
            "title": meta.get("title", ""),
            "date": meta.get("date", ""),
            "quarter": meta.get("quarter", ""),
            "url": url,
        }

        # Extraer participantes
        participants = []
        # Los participantes aparecen como "Nombre (Compañia)" al inicio del texto
        # Buscar secciones que mencionen "Participants"
        participant_section = re.search(
            r"Participants\s*(.*?)(?=(Operator|Presentation|Prepared|Question))",
            text,
            re.I | re.DOTALL,
        )
        if participant_section:
            p_text = participant_section.group(1)
            # Extraer nombres: lineas con parentesis o cargos
            for line in p_text.split("\n"):
                line = line.strip()
                if line and ("(" in line or "Chief" in line or "CEO" in line or "CFO" in line):
                    participants.append(line)
        else:
            # Fallback: buscar lineas que parezcan nombres de personas
            for line in text.split("\n")[:50]:
                line = line.strip()
                if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+", line) and len(line) < 100:
                    if not any(
                        kw in line.lower()
                        for kw in ["copyright", "market", "stock", "news", "transcript"]
                    ):
                        participants.append(line)

        result["participants"] = participants[:20]

        # Separar prepared remarks y Q&A
        # Buscar secciones "Operator" / "Question" / "Answer"
        sections = re.split(
            r"(Operator|Question|Answer|Presentation)",
            text,
            flags=re.I,
        )

        prepared = ""
        qa = ""

        in_prepared = False
        in_qa = False

        for i, section in enumerate(sections):
            section_lower = section.lower().strip()
            if section_lower in ("operator", "presentation"):
                if i + 1 < len(sections):
                    # El contenido despues de Operator/Presentation al inicio
                    if not prepared and len(sections) > i + 1:
                        prepared = sections[i + 1].strip()
                        in_prepared = True
                        in_qa = False
            elif section_lower in ("question", "answer"):
                in_qa = True
                in_prepared = False
                if i + 1 < len(sections):
                    qa += f"\n[{section.strip()}]: {sections[i + 1].strip()}"

        result["prepared_remarks"] = prepared[:10000] if prepared else ""
        result["qa_section"] = qa[:10000] if qa else ""

        # Si no se pudo separar, intentar metodo alternativo
        if not prepared and not qa:
            # Buscar "Question and Answer" section
            qa_start = re.search(r"(Question and Answer|Q[&/]A|Questions?\s*and\s*Answers?)", text, re.I)
            if qa_start:
                result["prepared_remarks"] = text[: qa_start.start()].strip()[:10000]
                result["qa_section"] = text[qa_start.start():].strip()[:10000]
            else:
                result["full_text"] = text[:15000]

        return result

    # ------------------------------------------------------------------
    # Calendar
    # ------------------------------------------------------------------

    def get_calendar(
        self, ticker: str, cid: Optional[str] = None, slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene calendario corporativo.

        Returns:
            Dict con next_earnings, last_earnings, ex_dividend_date, etc.
        """
        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug, "calendar/")
        soup = self._soup(url)

        calendar: Dict[str, Any] = {
            "ticker": ticker.upper(),
        }

        text = soup.get_text()

        # Buscar fechas de eventos
        event_patterns = [
            ("next_earnings", r"(?:Next|Upcoming)\s+Earnings[:\s]+([A-Za-z]+\s+\d+,?\s*\d*)"),
            ("last_earnings", r"(?:Last|Previous)\s+Earnings[:\s]+([A-Za-z]+\s+\d+,?\s*\d*)"),
            ("ex_dividend_date", r"Ex.dividend\s+date[:\s]+([A-Za-z]+\s+\d+,?\s*\d*)"),
            ("dividend_payment", r"Dividend\s+Payment[:\s]+([A-Za-z]+\s+\d+,?\s*\d*)"),
            ("agm_date", r"(?:AGM|Annual\s+Meeting)[:\s]+([A-Za-z]+\s+\d+,?\s*\d*)"),
        ]

        for key, pattern in event_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                calendar[key] = match.group(1).strip()

        return calendar

    # ------------------------------------------------------------------
    # Insider Trading
    # ------------------------------------------------------------------

    def get_insider_trading(
        self, ticker: str, max_items: int = 20,
        cid: Optional[str] = None, slug: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Obtiene transacciones de insiders.

        Returns:
            List[Dict] con insider_name, position, transaction_type, date, shares, value
        """
        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug, "company-insider-trading/")
        soup = self._soup(url)

        trades = []
        for table in soup.find_all("table"):
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 4:
                    continue

                trade = {
                    "insider_name": _extract_text(tds[0]) if len(tds) > 0 else "",
                    "position": _extract_text(tds[1]) if len(tds) > 1 else "",
                    "transaction_type": _extract_text(tds[2]) if len(tds) > 2 else "",
                    "date": _extract_text(tds[3]) if len(tds) > 3 else "",
                }

                if len(tds) > 4:
                    trade["shares"] = _extract_text(tds[4])
                if len(tds) > 5:
                    trade["price"] = _extract_text(tds[5])
                if len(tds) > 6:
                    trade["value"] = _extract_text(tds[6])

                if trade["insider_name"] and trade["transaction_type"]:
                    trades.append(trade)

                if len(trades) >= max_items:
                    return trades

        return trades

    # ------------------------------------------------------------------
    # Shareholders
    # ------------------------------------------------------------------

    def get_shareholders(
        self, ticker: str, max_items: int = 10,
        cid: Optional[str] = None, slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene principales accionistas.

        Returns:
            Dict con top_shareholders, institutional_pct, etc.
        """
        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug, "company-shareholders/")
        soup = self._soup(url)

        result: Dict[str, Any] = {
            "ticker": ticker.upper(),
            "top_shareholders": [],
        }

        # Buscar tabla de shareholders
        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) >= 3:
                    name = _extract_text(tds[0])
                    pct = _extract_text(tds[2]) if len(tds) > 2 else ""
                    if name and "%" in pct:
                        rows.append({
                            "name": name,
                            "equities": _extract_text(tds[1]) if len(tds) > 1 else "",
                            "percentage": pct,
                        })
            if rows:
                result["top_shareholders"] = rows[:max_items]

        return result

    # ------------------------------------------------------------------
    # Governance
    # ------------------------------------------------------------------

    def get_governance(
        self, ticker: str, cid: Optional[str] = None, slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene informacion de gobierno corporativo.

        Returns:
            Dict con board_members, management, committees
        """
        cid, slug, _ = self._ensure_resolved(ticker, cid, slug)
        url = _company_url(cid, slug, "company-governance/")
        soup = self._soup(url)

        governance: Dict[str, Any] = {
            "ticker": ticker.upper(),
            "board_members": [],
            "management": [],
        }

        # Extraer management y board de las tablas
        current_section = None
        for header in soup.find_all(["h3", "h4", "h5"]):
            header_text = _extract_text(header).lower()
            if "management" in header_text or "executive" in header_text:
                current_section = "management"
            elif "board" in header_text or "director" in header_text:
                current_section = "board"
            else:
                continue

            # La tabla sigue al header
            table = header.find_next("table")
            if table:
                for tr in table.find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) >= 4:
                        member = {
                            "name": _extract_text(tds[0]),
                            "title_desc": _extract_text(tds[1]),
                            "title": _extract_text(tds[2]) if len(tds) > 2 else "",
                            "age": _extract_text(tds[3]) if len(tds) > 3 else "",
                        }
                        if len(tds) > 4:
                            member["since"] = _extract_text(tds[4])
                        if member["name"]:
                            if current_section == "management":
                                governance["management"].append(member)
                            else:
                                governance["board_members"].append(member)

        return governance


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _format_data(data: Any, indent: int = 0) -> str:
    """Formatea datos (dict o list) como texto legible."""
    if isinstance(data, dict):
        return _format_dict(data, indent)
    elif isinstance(data, list):
        prefix = " " * indent
        lines = []
        for i, item in enumerate(data):
            if isinstance(item, dict):
                lines.append(f"{prefix}[{i}]")
                lines.append(_format_dict(item, indent + 2))
            else:
                lines.append(f"{prefix}[{i}] {item}")
        return "\n".join(lines)
    return str(data)


def _format_dict(d: Dict[str, Any], indent: int = 0) -> str:
    """Formatea un dict como texto legible."""
    prefix = " " * indent
    lines = []
    for k, v in d.items():
        if isinstance(v, dict):
            lines.append(f"{prefix}{k}:")
            lines.append(_format_dict(v, indent + 2))
        elif isinstance(v, list):
            lines.append(f"{prefix}{k}:")
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    lines.append(f"{prefix}  [{i}]:")
                    lines.append(_format_dict(item, indent + 4))
                else:
                    lines.append(f"{prefix}  [{i}] {item}")
        else:
            lines.append(f"{prefix}{k}: {v}")
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="MarketScreener Client — Datos financieros gratuitos (scraping)"
    )
    parser.add_argument(
        "command",
        choices=[
            "search", "quote", "profile", "financials", "valuation",
            "consensus", "ratings", "news", "transcript", "transcripts",
            "calendar", "insider", "shareholders", "governance",
        ],
        help="Comando a ejecutar",
    )
    parser.add_argument("ticker", help="Ticker de la empresa (ej: AAPL, GGAL)")
    parser.add_argument(
        "--statement", "-s",
        default="income",
        choices=["income", "balance", "cashflow", "ratios"],
        help="Tipo de estado financiero (default: income)",
    )
    parser.add_argument(
        "--quarter", "-q",
        help="Quarter para transcript (ej: Q1)",
    )
    parser.add_argument(
        "--year", "-y",
        help="Anio para transcript (ej: 2026)",
    )
    parser.add_argument(
        "--max", "-m",
        type=int,
        default=10,
        help="Maximo items a mostrar (default: 10)",
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=1.5,
        help="Delay entre requests en segundos (default: 1.5)",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Salida en formato JSON",
    )

    args = parser.parse_args()

    client = MarketScreenerClient(min_delay=args.delay)

    try:
        if args.command == "search":
            results = client.search_company(args.ticker)
            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                for r in results:
                    print(f"{r['ticker']:10s} | {r['name']:40s} | {r['exchange']:20s} | ID: {r['id']}")
            return

        elif args.command == "quote":
            data = client.get_quote(args.ticker)

        elif args.command == "profile":
            data = client.get_profile(args.ticker)

        elif args.command == "financials":
            data = client.get_financials(args.ticker, statement=args.statement)

        elif args.command == "valuation":
            data = client.get_valuation(args.ticker)

        elif args.command == "consensus":
            data = client.get_consensus(args.ticker)

        elif args.command == "ratings":
            data = client.get_ratings(args.ticker)

        elif args.command == "news":
            data = client.get_news(args.ticker, max_items=args.max)

        elif args.command == "transcripts":
            data = client.get_transcripts_list(args.ticker, max_items=args.max)

        elif args.command == "transcript":
            if args.quarter and args.year:
                data = client.get_transcript_by_quarter(
                    args.ticker, args.quarter, args.year
                )
            else:
                data = client.get_transcript(args.ticker)

        elif args.command == "calendar":
            data = client.get_calendar(args.ticker)

        elif args.command == "insider":
            data = client.get_insider_trading(args.ticker, max_items=args.max)

        elif args.command == "shareholders":
            data = client.get_shareholders(args.ticker, max_items=args.max)

        elif args.command == "governance":
            data = client.get_governance(args.ticker)

        else:
            parser.print_help()
            return

        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        else:
            print(_format_data(data))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
