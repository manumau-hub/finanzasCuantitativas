"""
SimplyWallSt API Client — Snowflake scores, company data, screener.

API interna de simplywall.st descubierta por reverse engineering.
Sin Cloudflare (en /api/), sin API key, sin registro.

Uso:
    # PRIMERO: Descargar snapshot completo (1 vez, ~3 min)
    python fetch_sws.py --download-snapshot

    # Luego: búsquedas instantáneas via snapshot
    python fetch_sws.py --ticker GGAL
    python fetch_sws.py --ticker GGAL --full
    python fetch_sws.py --ticker GGAL,BMA --score

    # Otras ops
    python fetch_sws.py --search "Galicia"
    python fetch_sws.py --list-tickers --country AR
    python fetch_sws.py --grid --size 10
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import re
import sys
import time
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# ── Config ─────────────────────────────────────────────────────────────────
BASE = "https://simplywall.st"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
}

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
SNAPSHOT_PATTERN = re.compile(r"\d{2}-\d{2}-\d{2}-ticker-snapshot\.csv$")

DEFAULT_RULES = [
    ["order_by", "market_cap", "desc"],
    ["grid_visible_flag", "=", True],
    ["primary_flag", "=", True],
    ["is_fund", "=", False],
]

INCLUDES_ALL = [
    "info",
    "score",
    "analysis",
    "analysis.extended",
    "analysis.extended.raw_data",
    "analysis.extended.raw_data.insider_transactions",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("sws")


# ── Helpers ────────────────────────────────────────────────────────────────

def sanitize(val: Any) -> str:
    """Convertir valor a string seguro."""
    if val is None:
        return ""
    if isinstance(val, (int, float)):
        return str(val)
    return str(val)


# ── Client ─────────────────────────────────────────────────────────────────
class SWSClient:
    """Cliente para la API interna de SimplyWallSt."""

    def __init__(self, delay: float = 0.3):
        self.delay = delay
        self.sess = requests.Session()
        self.sess.headers.update(HEADERS)
        try:
            self.sess.get(BASE, timeout=10)
        except Exception:
            pass

    def _rate_limit(self):
        time.sleep(self.delay)

    def grid_filter(
        self,
        offset: int = 0,
        size: int = 100,
        rules: Optional[List] = None,
        include: str = "info,score,grid",
    ) -> Dict:
        """POST al grid/filter API."""
        size = min(size, 100)  # server max
        if rules is None:
            rules = DEFAULT_RULES

        url = f"{BASE}/api/grid/filter?include={include}"
        payload = {
            "id": "0",
            "no_result_if_limit": False,
            "offset": offset,
            "size": size,
            "state": "read",
            "rules": json.dumps(rules),
        }
        log.debug("POST grid_filter offset=%d size=%d", offset, size)
        resp = self.sess.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        self._rate_limit()
        return resp.json()

    def grid_filter_exchange(
        self, exchange: str, offset: int = 0, size: int = 100, include: str = "info,score,grid"
    ) -> Tuple[List[Dict], int]:
        """Empresas de un exchange específico."""
        rules = [
            ["order_by", "market_cap", "desc"],
            ["exchange_symbol", "=", exchange],
            ["primary_flag", "=", True],
        ]
        try:
            data = self.grid_filter(offset=offset, size=size, rules=rules, include=include)
            return data.get("data", []), data.get("meta", {}).get("total_records", 0)
        except Exception as e:
            log.warning("Error fetching exchange %s offset %d: %s", exchange, offset, e)
            return [], 0

    # ── Snapshot completo (particionado por exchange) ────────────────

    def download_full_snapshot(self) -> List[Dict]:
        """Descargar TODOS los tickers disponibles (>54K).

        Estrategia:
          1. Top 10K vía query default (para extraer exchanges)
          2. Por cada exchange, fetch ALL companies
          3. Dedup por unique_symbol
        """
        seen: Dict[str, Dict] = OrderedDict()
        total_requests = 0

        # ── Fase 1: Top 10K ──
        log.info("=" * 50)
        log.info("FASE 1: Top 10K (default query)")
        log.info("=" * 50)
        for offset in range(0, 10000, 100):
            try:
                data = self.grid_filter(offset=offset, size=100)
                for c in data.get("data", []):
                    key = c.get("unique_symbol") or c.get("canonical_url") or str(id(c))
                    if key not in seen:
                        seen[key] = c
                total_requests += 1
                if offset % 1000 == 0:
                    log.info("  offset %d/10000 | unique: %d", offset, len(seen))
            except Exception as e:
                log.warning("  Error at offset %d: %s", offset, e)
                break

        log.info("FASE 1 done: %d unique companies (%d requests)", len(seen), total_requests)

        # ── Fase 2: Extraer exchanges ──
        exchanges = sorted({sanitize(c.get("exchange_symbol", "")) for c in seen.values() if c.get("exchange_symbol")})
        # Filtrar exchanges que parezcan inválidos (muy cortos o numéricos)
        exchanges = [e for e in exchanges if len(e) >= 2 and not e.isdigit()]
        log.info("FASE 2: %d exchanges extraídos", len(exchanges))

        # ── Fase 3: Por exchange, obtener resto ──
        log.info("=" * 50)
        log.info("FASE 3: Fetch por exchange (%d exchanges)", len(exchanges))
        log.info("=" * 50)
        for idx, ex in enumerate(exchanges):
            count_before = len(seen)

            # Paginar hasta obtener todas las companies de este exchange
            ex_offset = 0
            while True:
                companies, total = self.grid_filter_exchange(ex, offset=ex_offset, size=100)
                total_requests += 1
                if not companies:
                    break
                for c in companies:
                    key = c.get("unique_symbol") or c.get("canonical_url") or str(id(c))
                    if key not in seen:
                        seen[key] = c
                ex_offset += len(companies)
                if ex_offset >= total or len(companies) < 100:
                    break

            new_count = len(seen) - count_before
            if new_count > 0:
                log.info("  [%d/%d] %-12s -> +%d (total: %d)", idx + 1, len(exchanges), ex, new_count, len(seen))

        log.info("=" * 50)
        log.info("SNAPSHOT COMPLETE: %d companies (%d requests)", len(seen), total_requests)
        log.info("=" * 50)
        return list(seen.values())

    # ── Listado paginado (limitado a 10K) ──

    def list_companies(self, max_results: int = 1000, page_size: int = 100) -> List[Dict]:
        """Top N companies (limitado a 10K por el server)."""
        all_cos: List[Dict] = []
        for offset in range(0, min(max_results, 10000), min(page_size, 100)):
            try:
                data = self.grid_filter(offset=offset, size=min(page_size, 100))
                chunk = data.get("data", [])
                if not chunk:
                    break
                all_cos.extend(chunk)
            except Exception:
                break
        return all_cos[:max_results]

    # ── Company Detail ───────────────────────────────────────────────

    def company_detail(self, canonical_url: str, includes: Optional[List[str]] = None) -> Dict:
        if includes is None:
            includes = INCLUDES_ALL
        url = f"{BASE}/api/company{canonical_url}"
        params = {"include": ",".join(includes), "version": "2.0"}
        log.debug("GET company detail: %s", canonical_url)
        resp = self.sess.get(url, params=params, timeout=30)
        resp.raise_for_status()
        self._rate_limit()
        return resp.json().get("data", resp.json())

    # ── Search / Resolve ticker ──

    def find_company(
        self,
        ticker: Optional[str] = None,
        name: Optional[str] = None,
        snapshot: Optional[Dict[str, Dict]] = None,
        max_pages: int = 50,
    ) -> Optional[Dict]:
        """Buscar por ticker o nombre. Usa snapshot si disponible."""
        # Snapshot lookup (instantáneo)
        if ticker and snapshot:
            row = snapshot.get(ticker.upper())
            if row:
                log.info("Found %s in snapshot", ticker)
                return {
                    "ticker_symbol": row.get("ticker_symbol", ticker),
                    "name": row.get("name", ""),
                    "exchange_symbol": row.get("exchange_symbol", ""),
                    "canonical_url": row.get("canonical_url", ""),
                    "unique_symbol": row.get("unique_symbol", ""),
                    "info": {"data": {
                        "country": row.get("country", ""),
                        "industry": {"name": row.get("industry", "")},
                        "employees": row.get("employees", ""),
                        "year_founded": row.get("year_founded", ""),
                    }},
                    "score": {"data": {
                        "value": row.get("score_value", ""),
                        "income": row.get("score_income", ""),
                        "health": row.get("score_health", ""),
                        "past": row.get("score_past", ""),
                        "future": row.get("score_future", ""),
                        "management": row.get("score_management", ""),
                        "total": row.get("score_total", ""),
                    }},
                }

        # Grid iteration (lento pero sin snapshot)
        log.info("Searching grid (no snapshot match)...")
        pages = 0
        for offset in range(0, max_pages * 100, 100):
            try:
                data = self.grid_filter(offset=offset, size=100, include="info,score")
            except Exception:
                break
            companies = data.get("data", [])
            if not companies:
                break
            pages += 1
            for c in companies:
                ts = sanitize(c.get("ticker_symbol", ""))
                cn = sanitize(c.get("name", ""))
                if ticker and ts.upper() == ticker.upper():
                    log.info("Found %s at offset %d", ticker, offset)
                    return c
                if name and name.lower() in cn.lower():
                    log.info("Found '%s' at offset %d", name, offset)
                    return c
        log.warning("Company not found: ticker=%s name=%s", ticker, name)
        return None

    def fetch_by_ticker(self, ticker: str, includes: Optional[List[str]] = None,
                        snapshot: Optional[Dict[str, Dict]] = None) -> Dict:
        company = self.find_company(ticker=ticker, snapshot=snapshot)
        if not company:
            raise ValueError(f"Company not found for ticker: {ticker}")
        canonical_url = company.get("canonical_url")
        if not canonical_url:
            raise ValueError(f"No canonical_url for ticker: {ticker}")
        log.info("Fetching detail: %s", canonical_url)
        return self.company_detail(canonical_url, includes=includes)


# ── Snapshot Manager ────────────────────────────────────────────────────────

SNAPSHOT_FIELDS = [
    "ticker_symbol", "name", "exchange_symbol", "canonical_url", "unique_symbol",
    "country", "industry", "employees", "year_founded",
    "score_value", "score_income", "score_health", "score_past", "score_future",
    "score_management", "score_total",
    "share_price", "market_cap", "pe_ratio", "pb_ratio",
]


def make_snapshot_rows(companies: List[Dict]) -> List[Dict]:
    """Convert raw API companies to flat snapshot rows."""
    rows = []
    for c in companies:
        info = c.get("info", {}).get("data", {})
        score = c.get("score", {}).get("data", {})
        grid = c.get("grid", {}).get("data", {})
        rows.append({
            "ticker_symbol": sanitize(c.get("ticker_symbol", "")),
            "name": sanitize(c.get("name", "")),
            "exchange_symbol": sanitize(c.get("exchange_symbol", "")),
            "canonical_url": sanitize(c.get("canonical_url", "")),
            "unique_symbol": sanitize(c.get("unique_symbol", "")),
            "country": sanitize(info.get("country", "")),
            "industry": sanitize((info.get("industry") or {}).get("name", "")),
            "employees": sanitize(info.get("employees", "")),
            "year_founded": sanitize(info.get("year_founded", "")),
            "score_value": sanitize(score.get("value", "")),
            "score_income": sanitize(score.get("income", "")),
            "score_health": sanitize(score.get("health", "")),
            "score_past": sanitize(score.get("past", "")),
            "score_future": sanitize(score.get("future", "")),
            "score_management": sanitize(score.get("management", "")),
            "score_total": sanitize(score.get("total", "")),
            "share_price": sanitize(grid.get("share_price", "")),
            "market_cap": sanitize(grid.get("market_cap", "")),
            "pe_ratio": sanitize(grid.get("pe", "")),
            "pb_ratio": sanitize(grid.get("pb", "")),
        })
    return rows


def load_snapshot(path: str) -> Dict[str, Dict]:
    """CSV -> dict ticker -> row."""
    result: Dict[str, Dict] = {}
    p = Path(path)
    if not p.exists():
        log.warning("Snapshot not found: %s", path)
        return result
    with open(p, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ticker = row.get("ticker_symbol", "").strip().upper()
            if ticker:
                result[ticker] = row
    log.info("Snapshot loaded: %s (%d tickers)", p.name, len(result))
    return result


def find_latest_snapshot() -> Optional[Path]:
    if not ASSETS_DIR.exists():
        return None
    snaps = sorted(
        [f for f in ASSETS_DIR.iterdir() if f.is_file() and SNAPSHOT_PATTERN.match(f.name)],
        reverse=True,
    )
    return snaps[0] if snaps else None


def auto_load_snapshot() -> Dict[str, Dict]:
    latest = find_latest_snapshot()
    return load_snapshot(str(latest)) if latest else {}


# ── Formateo ───────────────────────────────────────────────────────────────

def flatten_company_data(data: Dict) -> Dict:
    flat = {}
    for key in ["id", "company_id", "name", "slug", "exchange_symbol",
                 "ticker_symbol", "unique_symbol", "isin_symbol",
                 "canonical_url", "primary_canonical_url"]:
        flat[key] = sanitize(data.get(key))

    info = data.get("info", {}).get("data", {})
    if info:
        flat.update({
            "description": info.get("description"),
            "industry": (info.get("industry") or {}).get("name"),
            "country": info.get("country"),
            "currency": info.get("currency"),
            "status": info.get("status"),
            "employees": info.get("employees"),
            "year_founded": info.get("year_founded"),
            "ceo_name": (info.get("ceo") or {}).get("name"),
            "legal_name": info.get("legal_name"),
            "url": info.get("url"),
        })

    score = data.get("score", {}).get("data", {})
    if score:
        flat.update({
            "score_value": score.get("value"),
            "score_income": score.get("income"),
            "score_health": score.get("health"),
            "score_past": score.get("past"),
            "score_future": score.get("future"),
            "score_management": score.get("management"),
            "score_total": score.get("total"),
            "score_sentence": score.get("sentence"),
        })

    analysis = data.get("analysis", {}).get("data", {})
    if analysis:
        flat.update({
            "share_price": analysis.get("share_price"),
            "market_cap": analysis.get("market_cap"),
            "pe_ratio": analysis.get("pe"),
            "pb_ratio": analysis.get("pb"),
            "peg_ratio": analysis.get("peg"),
            "roe": analysis.get("roe"),
            "roa": analysis.get("roa"),
            "eps": analysis.get("eps"),
            "debt_equity": analysis.get("debt_equity"),
            "dividend_current": (analysis.get("dividend") or {}).get("current"),
            "dividend_future": (analysis.get("dividend") or {}).get("future"),
            "growth_1y": (analysis.get("future") or {}).get("growth_1y"),
            "growth_3y": (analysis.get("future") or {}).get("growth_3y"),
            "past_growth_1y": (analysis.get("past") or {}).get("growth_1y"),
            "past_growth_5y": (analysis.get("past") or {}).get("growth_5y"),
            "analyst_count": analysis.get("analyst_count"),
        })

    grid = data.get("grid", {}).get("data", {})
    if grid:
        flat.update({
            "grid_share_price": grid.get("share_price"),
            "grid_market_cap": grid.get("market_cap"),
            "grid_pe": grid.get("pe"),
            "grid_pb": grid.get("pb"),
            "grid_price_to_sales": grid.get("price_to_sales"),
            "grid_analyst_count": grid.get("analyst_count"),
            "grid_return_1d": grid.get("return_1d"),
            "grid_return_7d": grid.get("return_7d"),
            "grid_return_1yr": grid.get("return_1yr_abs"),
            "grid_price_target": grid.get("price_target"),
            "grid_growth_3y": grid.get("growth_3y"),
            "grid_dividend_yield": grid.get("dividend_yield"),
        })
    return flat


def print_summary(data, mode="full"):
    if mode == "score":
        score = data.get("score", {}).get("data", {}) or data.get("grid", {}).get("data", {})
        if score:
            print(f"\n  Snowflake Scores: {score.get('sentence', 'N/A')}")
            print(f"     {'Value':>6s} {'Income':>6s} {'Health':>6s} {'Past':>6s} {'Future':>6s} {'Mgmt':>6s} {'Total':>6s}")
            print(f"     {sanitize(score.get('value','-')):>6s} {sanitize(score.get('income','-')):>6s} "
                  f"{sanitize(score.get('health','-')):>6s} {sanitize(score.get('past','-')):>6s} "
                  f"{sanitize(score.get('future','-')):>6s} {sanitize(score.get('management','-')):>6s} "
                  f"{sanitize(score.get('total','-')):>6s}")
    elif mode == "info":
        info = data.get("info", {}).get("data", {}) or data
        name = data.get("name", info.get("legal_name", ""))
        ticker = data.get("ticker_symbol", "")
        print(f"\n  {name} ({ticker})")
        print(f"  {'-'*40}")
        print(f"  Industry:  {(info.get('industry') or {}).get('name', 'N/A')}")
        print(f"  Country:   {info.get('country', 'N/A')}")
        print(f"  Currency:  {info.get('currency', 'N/A')}")
        print(f"  Founded:   {info.get('year_founded', 'N/A')}")
        print(f"  Employees: {info.get('employees', 'N/A')}")
        print(f"  CEO:       {(info.get('ceo') or {}).get('name', 'N/A')}")
        print(f"  Status:    {info.get('status', 'N/A')}")
        print(f"  Website:   {info.get('url', 'N/A')}")
        print(f"  ISIN:      {data.get('isin_symbol', 'N/A')}")
    elif mode == "analysis":
        a = data.get("analysis", {}).get("data", {}) or data
        name = data.get("name", "")
        ticker = data.get("ticker_symbol", "")
        print(f"\n  {name} ({ticker}) - Key Metrics")
        print(f"  {'-'*50}")
        print(f"  Price:       {a.get('share_price', 'N/A')}")
        print(f"  Market Cap:  {a.get('market_cap', 'N/A')}")
        print(f"  P/E:         {a.get('pe', 'N/A')}")
        print(f"  P/B:         {a.get('pb', 'N/A')}")
        print(f"  PEG:         {a.get('peg', 'N/A')}")
        print(f"  ROE:         {a.get('roe', 'N/A')}")
        print(f"  ROA:         {a.get('roa', 'N/A')}")
        print(f"  EPS:         {a.get('eps', 'N/A')}")
        print(f"  D/E:         {a.get('debt_equity', 'N/A')}")
        print(f"  Analysts:    {a.get('analyst_count', 'N/A')}")
        div = a.get("dividend", {})
        if div:
            print(f"  Div Current: {div.get('current', 'N/A')}")
            print(f"  Div Future:  {div.get('future', 'N/A')}")
        fut = a.get("future", {})
        if fut:
            print(f"  Growth 1y:   {fut.get('growth_1y', 'N/A')}%")
            print(f"  Growth 3y:   {fut.get('growth_3y', 'N/A')}%")
        past = a.get("past", {})
        if past:
            print(f"  Past 1y:     {past.get('growth_1y', 'N/A')}%")
            print(f"  Past 5y:     {past.get('growth_5y', 'N/A')}%")
    elif mode == "grid":
        for c in data:
            s = c.get("score", {}).get("data", {})
            g = c.get("grid", {}).get("data", {})
            print(f"  {sanitize(c.get('ticker_symbol','?')):10s} {sanitize(c.get('name','?')):30s} "
                  f"{sanitize(c.get('exchange_symbol','?')):12s} Score:{s.get('total','-'):>2s}  "
                  f"Price:{sanitize(g.get('share_price','?')):>8}")
    elif mode == "tickers":
        hdr = f"  {'Ticker':12s} {'Name':35s} {'Exchange':12s} {'Country':8s} {'Industry':20s} {'Score':6s}"
        print(f"\n{hdr}")
        print(f"  {'-'*len(hdr)}")
        for c in data:
            i = c.get("info", {}).get("data", {})
            s = c.get("score", {}).get("data", {})
            print(f"  {sanitize(c.get('ticker_symbol','?')):12s} {sanitize(c.get('name','?')):35s} "
                  f"{sanitize(c.get('exchange_symbol','?')):12s} "
                  f"{sanitize(i.get('country','?')):8s} {sanitize((i.get('industry') or {}).get('name','?')):20s} "
                  f"{sanitize(s.get('total','-')):>6s}")
    else:
        name = data.get("name", "")
        ticker = data.get("ticker_symbol", "")
        print(f"\n  {name} ({ticker})")
        print(f"  {'='*50}")
        info = data.get("info", {}).get("data", {})
        if info:
            print(f"  Industry: {(info.get('industry') or {}).get('name','N/A')}  |  "
                  f"Country: {info.get('country','N/A')}  |  "
                  f"Employees: {info.get('employees','N/A')}")
        score = data.get("score", {}).get("data", {})
        if score:
            print(f"  Scores: V={score.get('value')} I={score.get('income')} H={score.get('health')} "
                  f"P={score.get('past')} F={score.get('future')} M={score.get('management')} "
                  f"Total={score.get('total')}")
            print(f"  {score.get('sentence', '')}")
        analysis = data.get("analysis", {}).get("data", {})
        if analysis:
            print(f"  Price: {analysis.get('share_price','?')}  |  MC: {analysis.get('market_cap','?')}  |  "
                  f"P/E: {analysis.get('pe','?')}  |  P/B: {analysis.get('pb','?')}")


def write_csv(filepath: str, data: List[Dict], fieldnames: Optional[List[str]] = None):
    if not data:
        log.warning("No data to write to CSV")
        return
    if not fieldnames:
        fieldnames = list(data[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(data)
    log.info("CSV written: %s (%d rows)", filepath, len(data))


# ── CLI ────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="SimplyWallSt - Snowflake scores, company data, screener",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ejemplos:\n  python fetch_sws.py --ticker GGAL\n  python fetch_sws.py --download-snapshot\n  python fetch_sws.py --ticker GGAL,BMA --score",
    )
    tg = p.add_argument_group("Target")
    tg.add_argument("--ticker", "-t", type=str, help="Ticker(s) separados por coma")
    tg.add_argument("--search", "-s", type=str, help="Buscar por nombre")

    dd = p.add_argument_group("Data selection")
    dd.add_argument("--full", action="store_true", help="Todos los includes")
    dd.add_argument("--score", action="store_true", help="Solo scores")
    dd.add_argument("--info", action="store_true", help="Solo info corporativa")
    dd.add_argument("--analysis", action="store_true", help="Solo metrics")
    dd.add_argument("--extended", action="store_true", help="Incluir data extendida")
    dd.add_argument("--raw-data", action="store_true", help="Incluir raw data financiera")

    gg = p.add_argument_group("Grid / List")
    gg.add_argument("--grid", action="store_true", help="Listar via grid/filter")
    gg.add_argument("--list-tickers", action="store_true", help="Listar tickers")
    gg.add_argument("--country", type=str, help="Filtrar por pais (client-side)")
    gg.add_argument("--size", type=int, default=24, help="Page size (default: 24)")
    gg.add_argument("--limit", type=int, default=0, help="Max resultados (0=sin limite)")

    sg = p.add_argument_group("Snapshot")
    sg.add_argument("--download-snapshot", action="store_true",
                    help="Descargar snapshot COMPLETO (54K+ stocks) a assets/")
    sg.add_argument("--snapshot", type=str, default=None,
                    help="Ruta al CSV de snapshot (default: auto en assets/)")

    oo = p.add_argument_group("Output")
    oo.add_argument("--output", "-o", type=str, help="Archivo de salida")
    oo.add_argument("--csv", action="store_true", help="Output CSV")
    oo.add_argument("--quiet", "-q", action="store_true", help="Silencioso")

    cc = p.add_argument_group("Config")
    cc.add_argument("--delay", type=float, default=0.3, help="Delay entre requests (default: 0.3s)")
    return p.parse_args()


def build_includes(args) -> List[str]:
    if args.full:
        return INCLUDES_ALL
    inc = []
    if args.info:
        inc.append("info")
    if args.score:
        inc.append("score")
    if args.analysis or args.extended or args.raw_data:
        inc.append("analysis")
        if args.extended:
            inc.append("analysis.extended")
        if args.raw_data:
            inc.append("analysis.extended.raw_data")
            inc.append("analysis.extended.raw_data.insider_transactions")
    return inc or ["info", "score", "analysis"]


def filter_by_country(companies: List[Dict], country: str) -> List[Dict]:
    ctry = country.upper()
    return [c for c in companies
            if (c.get("info", {}).get("data", {}) or {}).get("country", "").upper() == ctry]


def main():
    args = parse_args()
    if args.quiet:
        log.setLevel(logging.WARNING)

    has_action = any([args.ticker, args.search, args.grid, args.list_tickers, args.download_snapshot])
    if not has_action:
        print("[ERROR] Especifica --ticker, --search, --grid, --list-tickers o --download-snapshot")
        sys.exit(1)

    try:
        client = SWSClient(delay=args.delay)

        # ── Download Snapshot ──
        if args.download_snapshot:
            all_companies = client.download_full_snapshot()
            rows = make_snapshot_rows(all_companies)
            ASSETS_DIR.mkdir(parents=True, exist_ok=True)
            fname = f"{datetime.now().strftime('%y-%m-%d')}-ticker-snapshot.csv"
            outpath = args.output or str(ASSETS_DIR / fname)
            write_csv(outpath, rows, fieldnames=SNAPSHOT_FIELDS)
            print(f"\nSnapshot saved: {outpath}")
            print(f"Total tickers: {len(rows)}")
            return

        # ── Load snapshot ──
        snapshot = None
        if args.snapshot:
            snapshot = load_snapshot(args.snapshot)
        elif args.ticker or args.search:
            snapshot = auto_load_snapshot()
            if snapshot:
                latest = find_latest_snapshot()
                print(f"Using snapshot: {latest.name} ({len(snapshot)} tickers)")

        results = {}

        # ── Grid / List tickers ──
        if args.grid or args.list_tickers:
            user_limit = args.limit if args.limit > 0 else None
            if args.country:
                log.info("Fetching grid (country filter active)...")
                companies_all = client.list_companies(max_results=5000)
                companies = filter_by_country(companies_all, args.country)
                if user_limit:
                    companies = companies[:user_limit]
                log.info("Filtered to %d companies in '%s'", len(companies), args.country)
            else:
                mx = user_limit if user_limit else (1000 if args.grid else 500)
                log.info("Fetching %d companies from grid...", mx)
                companies = client.list_companies(max_results=mx, page_size=min(args.size, 100))
            if args.list_tickers:
                results["tickers"] = companies
                if not args.quiet:
                    print_summary(companies, "tickers")
                    print(f"\n  Total: {len(companies)} tickers")
            else:
                results["grid"] = companies
                if not args.quiet:
                    print_summary(companies, "grid")

        # ── Search ──
        elif args.search:
            log.info("Searching for '%s'...", args.search)
            company = client.find_company(name=args.search, snapshot=snapshot)
            if not company:
                print(f"[ERROR] No company found matching '{args.search}'")
                sys.exit(1)
            includes = build_includes(args)
            detail = client.company_detail(company["canonical_url"], includes=includes)
            results["data"] = detail
            if not args.quiet:
                print_summary(detail)

        # ── Ticker ──
        elif args.ticker:
            tickers = [t.strip().upper() for t in args.ticker.split(",")]
            includes = build_includes(args)
            for i, ticker in enumerate(tickers):
                log.info("Fetching %s (%d/%d)...", ticker, i + 1, len(tickers))
                try:
                    detail = client.fetch_by_ticker(ticker, includes=includes, snapshot=snapshot)
                    results[ticker] = detail
                    if not args.quiet:
                        if len(tickers) > 1:
                            print(f"\n{'='*60}")
                        if args.score:
                            print_summary(detail, "score")
                        elif args.info:
                            print_summary(detail, "info")
                        elif args.analysis:
                            print_summary(detail, "analysis")
                        else:
                            print_summary(detail, "full")
                except ValueError as e:
                    log.error("  X %s", e)
                    results[ticker] = {"error": str(e)}
                except Exception as e:
                    log.error("  X Error: %s", e)
                    results[ticker] = {"error": str(e)}

        # ── Output ──
        if args.output:
            fp = args.output
            ext = os.path.splitext(fp)[1].lower()
            if args.csv or ext == ".csv":
                if args.list_tickers:
                    write_csv(fp, [flatten_company_data(c) for c in results.get("tickers", [])])
                elif args.grid:
                    write_csv(fp, [flatten_company_data(c) for c in results.get("grid", [])])
                else:
                    flat = []
                    for t, d in results.items():
                        if isinstance(d, dict) and "error" not in d:
                            r = flatten_company_data(d)
                            r["_ticker"] = t
                            flat.append(r)
                    write_csv(fp, flat)
            else:
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                log.info("JSON written: %s", fp)
        elif args.quiet and not args.grid and not args.list_tickers:
            print(json.dumps(results, indent=2, ensure_ascii=False))

    except requests.RequestException as e:
        log.error("Network error: %s", e)
        sys.exit(1)
    except Exception as e:
        log.error("Error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
