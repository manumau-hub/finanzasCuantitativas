"""
FRED Series Search — Busca, filtra y explora series FRED.

Uso:
    py search_series.py --api-key TU_API_KEY --search "inflation" --limit 30
    py search_series.py --search "GDP" --search-type series_id --limit 10
    py search_series.py --category 32995 --limit 100
    py search_series.py --category 32995 --output-ids > tasas_ids.txt
    py search_series.py --metadata FEDFUNDS
    py search_series.py --api-key KEY --tags "monthly;inflation"
    py search_series.py --api-key KEY --output-catalog
"""

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fred-search")

BASE_URL = "https://api.stlouisfed.org/fred"
REQUEST_DELAY = 0.6

_LAST_REQUEST = 0.0
import time


def _rate_limit():
    global _LAST_REQUEST
    elapsed = time.time() - _LAST_REQUEST
    if elapsed < REQUEST_DELAY:
        time.sleep(REQUEST_DELAY - elapsed)
    _LAST_REQUEST = time.time()


def fred_get(endpoint: str, params: dict, api_key: str) -> dict:
    """Request a FRED API con rate limiting."""
    _rate_limit()
    params["api_key"] = api_key
    params["file_type"] = "json"
    url = f"{BASE_URL}/{endpoint}"
    try:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        if r.status_code == 429:
            log.error("Rate limit excedido. Esperá 60s.")
        else:
            log.error(f"HTTP {r.status_code}: {e}")
        raise


# ── Print helpers ───────────────────────────────────────────────────────────


def print_table(series_list: list, max_rows: int = 100):
    """Imprime series como tabla formateada."""
    if not series_list:
        print("  (sin resultados)")
        return

    print(f"\n  {'ID':<15} {'Pop':<6} {'Freq':<6} {'Inicio':<12} {'Titulo'}")
    print(f"  {'-'*15} {'-'*6} {'-'*6} {'-'*12} {'-'*60}")

    for s in series_list[:max_rows]:
        sid = s.get("id", "?")
        pop = s.get("popularity", "?")
        freq = s.get("frequency_short", "?")
        obs_start = s.get("observation_start", "?")
        title = s.get("title", "?")[:60]
        print(f"  {sid:<15} {pop:<6} {freq:<6} {obs_start:<12} {title}")

    if len(series_list) > max_rows:
        print(f"  ... y {len(series_list) - max_rows} más (usá --limit para ampliar)")


# ── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="FRED Series Search — Busca y explora series macro.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  py search_series.py --api-key KEY --search "inflation"
  py search_series.py --api-key KEY --search "GDP" --search-type series_id
  py search_series.py --api-key KEY --category 32995 --limit 50
  py search_series.py --api-key KEY --metadata FEDFUNDS
  py search_series.py --api-key KEY --tags "monthly;inflation" --limit 30
  py search_series.py --api-key KEY --output-catalog > catalogo_fred.csv
        """,
    )

    parser.add_argument(
        "--api-key",
        default=os.getenv("FRED_API_KEY", ""),
        help="FRED API key (o FRED_API_KEY env var)",
    )
    parser.add_argument("--search", help="Texto de búsqueda")
    parser.add_argument(
        "--search-type",
        default="full_text",
        choices=["full_text", "series_id"],
        help="Tipo de búsqueda (default: full_text)",
    )
    parser.add_argument("--category", type=int, help="ID de categoría para listar series")
    parser.add_argument("--metadata", help="Obtener metadatos de una serie")
    parser.add_argument(
        "--tags",
        help="Filtrar por tags (separados por punto y coma, ej: 'monthly;inflation')",
    )
    parser.add_argument("--limit", type=int, default=30, help="Límite resultados (default: 30, max: 1000)")
    parser.add_argument(
        "--output-catalog",
        action="store_true",
        help="Genera catálogo CSV de series populares por categoría",
    )
    parser.add_argument("--json", action="store_true", help="Output en JSON")

    args = parser.parse_args()

    api_key = args.api_key
    if not api_key:
        log.error(
            "API Key no encontrada. Usá --api-key o setea FRED_API_KEY.\n"
            "  Obtener: https://fred.stlouisfed.org/docs/api/api_key.html"
        )
        sys.exit(1)

    # ── Metadata ────────────────────────────────────────────────────────
    if args.metadata:
        data = fred_get("series", {"series_id": args.metadata.upper()}, api_key)
        series = data.get("seriess", [])
        if not series:
            log.error(f"Serie '{args.metadata}' no encontrada.")
            sys.exit(1)

        meta = series[0]
        if args.json:
            print(json.dumps(meta, indent=2))
        else:
            print(f"\n  == Metadatos: {meta['id']} ==")
            for k, v in meta.items():
                print(f"    {k}: {v}")
        return

    # ── Busqueda por texto ──────────────────────────────────────────────
    if args.search:
        params = {
            "search_text": args.search,
            "search_type": args.search_type,
            "limit": min(args.limit, 1000),
            "order_by": "popularity",
            "sort_order": "desc",
        }
        if args.tags:
            params["tag_names"] = args.tags

        data = fred_get("series/search", params, api_key)
        results = data.get("seriess", [])

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f'\n  Resultados para "{args.search}": {len(results)} series')
            print_table(results)
        return

    # ── Categoria ──────────────────────────────────────────────────────
    if args.category:
        params = {
            "category_id": args.category,
            "limit": min(args.limit, 1000),
        }
        data = fred_get("category/series", params, api_key)
        results = data.get("seriess", [])

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n  Series en categoria {args.category}: {len(results)}")
            print_table(results)
        return

    # ── Tags ────────────────────────────────────────────────────────────
    if args.tags:
        params = {
            "tag_names": args.tags,
            "limit": min(args.limit, 1000),
            "order_by": "popularity",
            "sort_order": "desc",
        }
        data = fred_get("tags/series", params, api_key)
        results = data.get("seriess", [])

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f'\n  Series con tags "{args.tags}": {len(results)}')
            print_table(results)
        return

    # ── Catálogo completo ──────────────────────────────────────────────
    if args.output_catalog:
        categories = {
            32991: "Population_Employment_Labor",
            32992: "National_Income_Product_Accounts",
            32993: "CPI",
            32994: "PPI",
            32995: "Interest_Rates",
            32996: "Money_Banking_Finance",
            33000: "US_Regional",
        }
        print("series_id,title,frequency,units,popularity,category")
        for cat_id, cat_name in categories.items():
            params = {"category_id": cat_id, "limit": 500}
            try:
                data = fred_get("category/series", params, api_key)
                for s in data.get("seriess", []):
                    print(f'{s["id"]},"{s["title"]}",{s.get("frequency_short","?")},{s.get("units_short","?")},{s.get("popularity","?")},{cat_name}')
            except Exception as e:
                log.warning(f"Categoría {cat_id}: {e}")
        return

    # ── Sin argumentos ─────────────────────────────────────────────────
    parser.print_help()
    print("\n\n⚠️  Usá --search, --category, --metadata, --tags o --output-catalog")


if __name__ == "__main__":
    main()
