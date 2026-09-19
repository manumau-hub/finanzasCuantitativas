"""
INDEC Argentina Data Fetcher — API Series de Tiempo del Estado Argentino.

API oficial publica sin auth ni API key, mantenida por Datos Argentina.
Agrupa series del INDEC + BCRA + Ministerio de Economia + otros organismos.

Total: ~4250 series con datos macro, financieros y sociales de Argentina.

Endpoints expuestos:
  /series    — Fetch de datos por IDs (endpoint principal)
  /search    — Buscador full-text de series
  /dump      — Descarga completa del catalogo (pesado)
  /validate  — Valida una query antes de ejecutarla

Modos CLI disponibles:

  CONSULTA DIRECTA:
    series IDS              Fetch series por ID(s) — el modo mas potente
    search QUERY            Busca series por keywords
    validate IDS            Valida que un ID sea correcto

  ATAJOS POR INDICADOR (usan series_groups.json):
    ipc                     IPC Nacional variacion mensual
    ipc-completo            IPC + nucleo + regulados + categorias
    emae                    EMAE nivel general (original + desestacionalizado)
    salarios                RIPTE + SMVM + haber jubilatorio
    comercio                Exportaciones totales (M/T/A)
    construccion            ISAC nivel general
    dolar                   Tipo de cambio BNA vendedor
    reservas                Reservas internacionales BCRA
    snapshot                Snapshot macro Argentina (IPC + EMAE + dolar + reservas + RIPTE)

  CATALOGOS LOCALES (sin HTTP):
    catalog                 Catalogo curado de series IDs principales
    groups                  Bundles pre-armados de series
    sources                 Organismos publicadores
    modes                   Representation modes disponibles
    aggregations            Collapse aggregations disponibles

  COMBINADO:
    all                     Snapshot completo macro (combina varios atajos)

Uso:
    py fetch_indec.py series "145.3_INGNACUAL_DICI_M_38" --last 12
    py fetch_indec.py series "145.3_INGNACUAL_DICI_M_38,158.1_REPTE_0_0_5" --start 2024-01-01
    py fetch_indec.py search "pobreza" --limit 20
    py fetch_indec.py ipc --last 12
    py fetch_indec.py emae --start 2024-01-01
    py fetch_indec.py salarios -o salarios.json
    py fetch_indec.py snapshot
    py fetch_indec.py series "<ID>" --mode percent_change_a_year_ago    # YoY %
    py fetch_indec.py series "<ID>" --collapse year --aggregation sum   # acumulado anual

Atajos para transformaciones (representation_mode):
    --mode value                                    # default
    --mode percent_change                           # var % periodo a periodo
    --mode percent_change_a_year_ago                # var % YoY (inflacion interanual)
    --mode percent_change_since_beginning_of_year   # var % YTD (inflacion acumulada)
    --mode change                                   # diff absoluta
    --mode change_a_year_ago                        # diff absoluta YoY

Atajos para agregacion temporal (collapse + collapse_aggregation):
    --collapse day | week | month | quarter | semester | year
    --aggregation avg | sum | end_of_period | min | max

Output:
    Por default: JSON normalizado a stdout.
    -o file.json: guarda a archivo.
    -q: modo silencioso (sin logs INFO).
    --format csv: pide CSV en lugar de JSON.
    --raw: response raw sin normalizar.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

log = logging.getLogger("indec")
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

# ── Configuracion ──────────────────────────────────────────────────────────

BASE_URL = "https://apis.datos.gob.ar/series/api"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# Limites de la API
MAX_LIMIT_PER_REQUEST = 1000      # Max datapoints por serie en una llamada
DEFAULT_LIMIT = 1000

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


# ── HTTP helpers ───────────────────────────────────────────────────────────


def _get(path: str, params: dict, timeout: int = 30, as_json: bool = True) -> Any:
    """GET con error handling."""
    url = f"{BASE_URL}/{path}"
    log.info(f"GET {url} params={params}")
    r = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json() if as_json else r.text


# ── Normalizacion del response ─────────────────────────────────────────────


def normalize_series_response(raw: dict) -> dict:
    """Convierte el response del endpoint /series a un dict mas usable.

    Input:
      {
        "data": [["2026-04-01", 0.0258], ["2026-05-01", ...]],
        "count": 121,
        "meta": [
          {"frequency": "month", "start_date": "...", "end_date": "..."},
          {"catalog": {...}, "dataset": {...}, "distribution": {...}, "field": {...}}
        ],
        "params": {...}
      }

    Output (con metadata legible y data parseable):
      {
        "count": 121,
        "frequency": "month",
        "start_date": "...",
        "end_date": "...",
        "series": [
          {
            "id": "145.3_INGNACUAL_DICI_M_38",
            "description": "...",
            "units": "Variacion intermensual",
            "frequency": "...",
            "dataset_title": "...",
            "source": "Instituto Nacional de Estadistica y Censos (INDEC)",
            "data": [{"date": "2026-04-01", "value": 0.0258}, ...]
          }
        ]
      }
    """
    if not isinstance(raw, dict) or "data" not in raw:
        return raw

    data_raw = raw.get("data", [])
    meta = raw.get("meta", [])
    count = raw.get("count", len(data_raw))

    # meta[0] tiene info global (frecuencia, start_date, end_date)
    global_meta = meta[0] if meta else {}

    # meta[1:] tiene info de cada serie (en multi-serie hay multiples entries)
    series_metas = meta[1:] if len(meta) > 1 else []

    # data_raw es columnar: cada row = [date, value_serie_1, value_serie_2, ...]
    n_series = len(series_metas) if series_metas else 1

    series_out = []
    for i, sm in enumerate(series_metas):
        field = sm.get("field", {})
        dataset = sm.get("dataset", {})
        distribution = sm.get("distribution", {})

        # Extraer los datos de esta serie de las filas
        ts_data = []
        for row in data_raw:
            if not isinstance(row, list) or len(row) < 2:
                continue
            date = row[0]
            value = row[i + 1] if len(row) > i + 1 else None
            ts_data.append({"date": date, "value": value})

        series_out.append({
            "id": field.get("id"),
            "description": field.get("description"),
            "units": field.get("units"),
            "representation_mode": field.get("representation_mode"),
            "representation_mode_units": field.get("representation_mode_units"),
            "frequency": field.get("frequency"),
            "dataset_title": dataset.get("title"),
            "source": dataset.get("source"),
            "issued": dataset.get("issued"),
            "distribution_url": distribution.get("downloadURL"),
            "data": ts_data,
        })

    return {
        "count": count,
        "frequency": global_meta.get("frequency"),
        "start_date": global_meta.get("start_date"),
        "end_date": global_meta.get("end_date"),
        "n_series": len(series_out),
        "series": series_out,
    }


# ── Endpoints ──────────────────────────────────────────────────────────────


def fetch_series(
    ids: str | list[str],
    start_date: str | None = None,
    end_date: str | None = None,
    representation_mode: str | None = None,
    collapse: str | None = None,
    collapse_aggregation: str | None = None,
    limit: int = DEFAULT_LIMIT,
    start: int = 0,
    last: int | None = None,
    sort: str = "asc",
    metadata: str = "simple",
    format_: str = "json",
    raw: bool = False,
) -> dict | str:
    """Fetch de series por ID(s) via /series.

    Args:
        ids: ID o lista de IDs separados por coma (string) o list.
        start_date, end_date: rango YYYY-MM-DD.
        representation_mode: value | change | percent_change | percent_change_a_year_ago |
                             change_since_beginning_of_year | percent_change_since_beginning_of_year.
        collapse: day | week | month | quarter | semester | year.
        collapse_aggregation: avg | sum | end_of_period | min | max (default avg).
        limit: max datapoints por serie (max 1000).
        start: offset para paginacion.
        last: si se pasa, devuelve los ultimos N valores (override de start).
        sort: asc | desc.
        metadata: none | only | simple | full.
        format_: json | csv.
        raw: si True, devuelve response sin normalizar.
    """
    if isinstance(ids, list):
        ids = ",".join(ids)

    params: dict[str, Any] = {
        "ids": ids,
        "format": format_,
        "metadata": metadata,
    }
    if start_date: params["start_date"] = start_date
    if end_date: params["end_date"] = end_date
    if representation_mode: params["representation_mode"] = representation_mode
    if collapse: params["collapse"] = collapse
    if collapse_aggregation: params["collapse_aggregation"] = collapse_aggregation
    # Caveat de la API: `last` NO se puede combinar con `sort`, `start`, `limit`.
    # Si el usuario pasa `last`, ignorar los otros 3.
    if last is not None:
        params["last"] = last
    else:
        if limit: params["limit"] = min(limit, MAX_LIMIT_PER_REQUEST)
        if start: params["start"] = start
        if sort: params["sort"] = sort

    response = _get("series", params, as_json=(format_ == "json"))

    if raw or format_ != "json":
        return response
    return normalize_series_response(response)


def search_series(query: str, limit: int = 10, offset: int = 0) -> dict:
    """Busca series por keywords full-text.

    Returns:
        dict con `data` (lista de matches) y `meta` (counts).
    """
    return _get("search", {"q": query, "limit": limit, "offset": offset})


def validate_ids(ids: str | list[str]) -> dict:
    """Valida que un ID o lista de IDs sea correcta sin fetchear datos."""
    if isinstance(ids, list):
        ids = ",".join(ids)
    return _get("validate", {"ids": ids})


def dump_full(format_: str = "json") -> dict | str:
    """Descarga el catalogo completo de series (PESADO — varios MB).

    Args:
        format_: json | csv.
    """
    log.warning("dump_full() descarga TODO el catalogo. Esto puede tardar.")
    return _get("dump", {"format": format_}, timeout=120, as_json=(format_ == "json"))


# ── Atajos por indicador (usando series_groups.json) ───────────────────────


def _shortcut(group_name: str, **kwargs) -> dict:
    """Helper para los atajos de los indicadores. Combina IDs del grupo."""
    groups = load_asset("series_groups.json") or {}
    group = groups.get(group_name)
    if not group:
        raise ValueError(f"Grupo '{group_name}' no encontrado en series_groups.json")
    ids = group["ids"]
    log.info(f"Atajo '{group_name}': {len(ids)} IDs ({group.get('descripcion', '')[:60]})")
    return fetch_series(ids, **kwargs)


def ipc(**kwargs) -> dict:
    """IPC Nacional — variacion mensual."""
    return _shortcut("ipc_basico", **kwargs)


def ipc_completo(**kwargs) -> dict:
    """IPC + nucleo + regulados + categorias."""
    return _shortcut("ipc_completo", **kwargs)


def emae(**kwargs) -> dict:
    """EMAE nivel general (original + desestacionalizado)."""
    return _shortcut("emae_basico", **kwargs)


def salarios(**kwargs) -> dict:
    """Indicadores salariales."""
    return _shortcut("salarios", **kwargs)


def comercio(**kwargs) -> dict:
    """Exportaciones totales."""
    return _shortcut("comercio_exterior", **kwargs)


def construccion(**kwargs) -> dict:
    """ISAC nivel general."""
    return _shortcut("construccion", **kwargs)


def dolar(**kwargs) -> dict:
    """Tipo de cambio BNA."""
    return _shortcut("tipo_cambio_bcra", **kwargs)


def reservas(**kwargs) -> dict:
    """Reservas internacionales BCRA."""
    return _shortcut("reservas", **kwargs)


def snapshot(**kwargs) -> dict:
    """Snapshot rapido macro Argentina."""
    return _shortcut("snapshot_basico", **kwargs)


# ── Catalogos locales (sin HTTP) ───────────────────────────────────────────


def show_catalog() -> dict:
    """Catalogo curado de series IDs principales."""
    return load_asset("known_series_ids.json")


def show_groups() -> dict:
    """Bundles pre-armados."""
    return load_asset("series_groups.json")


def show_sources() -> dict:
    """Organismos publicadores."""
    return load_asset("data_sources.json")


def show_modes() -> dict:
    """Representation modes disponibles."""
    return load_asset("representation_modes.json")


def show_aggregations() -> dict:
    """Collapse aggregations disponibles."""
    return load_asset("collapse_aggregations.json")


# ── Mode ALL ───────────────────────────────────────────────────────────────


def fetch_all(last: int = 12, **kwargs) -> dict:
    """Snapshot macro completo: combina IPC + EMAE + salarios + dolar + reservas + construccion + comercio."""
    log.info("Fetching ALL macro snapshot...")
    result: dict[str, Any] = {"timestamp": datetime.now().isoformat()}
    indicators = [
        ("ipc", ipc),
        ("emae", emae),
        ("salarios", salarios),
        ("dolar", dolar),
        ("reservas", reservas),
        ("construccion", construccion),
        ("comercio", comercio),
    ]
    for name, fn in indicators:
        try:
            log.info(f"  {name}...")
            result[name] = fn(last=last, **kwargs)
            time.sleep(0.3)
        except Exception as e:
            log.warning(f"  {name}: {e}")
            result[name] = {"error": str(e)}
    return result


# ── CLI ────────────────────────────────────────────────────────────────────


MODES = [
    # Consulta directa
    "series", "search", "validate", "dump",
    # Atajos por indicador
    "ipc", "ipc-completo", "emae", "salarios", "comercio", "construccion",
    "dolar", "reservas", "snapshot",
    # Catalogos locales
    "catalog", "groups", "sources", "modes", "aggregations",
    # Combinado
    "all",
]


def main():
    parser = argparse.ArgumentParser(
        description="INDEC Argentina Data Fetcher — API Series de Tiempo oficial"
    )
    parser.add_argument("mode", choices=MODES, help="Modo de operacion")
    parser.add_argument("arg", nargs="?", help="Argumento principal (IDs o query segun modo)")

    # Filtros temporales
    parser.add_argument("--start", "--start-date", dest="start_date",
                        help="Fecha desde YYYY-MM-DD")
    parser.add_argument("--end", "--end-date", dest="end_date",
                        help="Fecha hasta YYYY-MM-DD")
    parser.add_argument("--last", type=int, help="Devolver los ultimos N valores")

    # Transformaciones
    parser.add_argument("--mode", "--representation-mode", dest="representation_mode",
                        choices=["value", "change", "percent_change",
                                 "percent_change_a_year_ago",
                                 "change_since_beginning_of_year",
                                 "percent_change_since_beginning_of_year"],
                        help="Representation mode (transformacion). Ver `modes` para detalles.")
    parser.add_argument("--collapse",
                        choices=["day", "week", "month", "quarter", "semester", "year"],
                        help="Agregacion temporal a otra frecuencia")
    parser.add_argument("--aggregation", "--collapse-aggregation", dest="collapse_aggregation",
                        choices=["avg", "sum", "end_of_period", "min", "max"],
                        help="Modo de agregacion para collapse (default: avg)")

    # Paginacion
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help=f"Max datapoints por serie (max {MAX_LIMIT_PER_REQUEST}, default {DEFAULT_LIMIT})")
    parser.add_argument("--offset", dest="start", type=int, default=0,
                        help="Offset para paginacion")

    # Sort, metadata, format
    parser.add_argument("--sort", choices=["asc", "desc"], default="asc")
    parser.add_argument("--metadata", choices=["none", "only", "simple", "full"],
                        default="simple", help="Nivel de metadata en el response (default: simple)")
    parser.add_argument("--format", dest="format_", choices=["json", "csv"], default="json")

    # Output
    parser.add_argument("--raw", action="store_true",
                        help="Devolver response raw (sin normalizar a dict)")
    parser.add_argument("-o", "--output", help="Guardar a archivo")
    parser.add_argument("-q", "--quiet", action="store_true", help="Modo silencioso")

    args = parser.parse_args()
    if args.quiet:
        log.setLevel(logging.WARNING)

    # Common kwargs para fetch_series y atajos
    common_kwargs = {
        "start_date": args.start_date,
        "end_date": args.end_date,
        "representation_mode": args.representation_mode,
        "collapse": args.collapse,
        "collapse_aggregation": args.collapse_aggregation,
        "limit": args.limit,
        "start": args.start,
        "last": args.last,
        "sort": args.sort,
        "metadata": args.metadata,
        "format_": args.format_,
        "raw": args.raw,
    }

    try:
        m = args.mode

        if m == "series":
            if not args.arg:
                log.error("Modo 'series' requiere ID(s). Ej: 145.3_INGNACUAL_DICI_M_38")
                sys.exit(1)
            result = fetch_series(args.arg, **common_kwargs)
        elif m == "search":
            if not args.arg:
                log.error("Modo 'search' requiere QUERY")
                sys.exit(1)
            result = search_series(args.arg, limit=args.limit, offset=args.start)
        elif m == "validate":
            if not args.arg:
                log.error("Modo 'validate' requiere ID(s)")
                sys.exit(1)
            result = validate_ids(args.arg)
        elif m == "dump":
            result = dump_full(format_=args.format_)
        # Atajos
        elif m == "ipc":
            result = ipc(**common_kwargs)
        elif m == "ipc-completo":
            result = ipc_completo(**common_kwargs)
        elif m == "emae":
            result = emae(**common_kwargs)
        elif m == "salarios":
            result = salarios(**common_kwargs)
        elif m == "comercio":
            result = comercio(**common_kwargs)
        elif m == "construccion":
            result = construccion(**common_kwargs)
        elif m == "dolar":
            result = dolar(**common_kwargs)
        elif m == "reservas":
            result = reservas(**common_kwargs)
        elif m == "snapshot":
            result = snapshot(**common_kwargs)
        # Catalogos locales
        elif m == "catalog":
            result = show_catalog()
        elif m == "groups":
            result = show_groups()
        elif m == "sources":
            result = show_sources()
        elif m == "modes":
            result = show_modes()
        elif m == "aggregations":
            result = show_aggregations()
        # Combinado
        elif m == "all":
            result = fetch_all(last=args.last or 12, **{k: v for k, v in common_kwargs.items() if k != "last"})
        else:
            parser.print_help()
            sys.exit(1)
    except requests.HTTPError as e:
        log.error(f"HTTP Error: {e}")
        if e.response is not None:
            log.error(f"Body: {e.response.text[:500]}")
        log.error("Si el ID parece valido y igual falla, ver references/LIMITATIONS_TROUBLESHOOTING.md")
        sys.exit(1)
    except Exception as e:
        log.error(f"Error: {e}")
        sys.exit(1)

    # Output
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


if __name__ == "__main__":
    main()
