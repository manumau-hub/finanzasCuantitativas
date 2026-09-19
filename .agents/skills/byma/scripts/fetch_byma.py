"""
BYMA Data Fetcher — Bolsas y Mercados Argentinos (open.bymadata.com.ar).

API publica de market data de BYMA. Sin API key, sin autenticacion.
SSL: el cert SSL de BYMA no es validable por bundles standard de Python,
por lo que se usa verify=False (ver SKILL.md). La data es publica.

Endpoints disponibles:

  PANELES (POST):
    - panel leading-equity    Panel lideres: 20 acciones x 2 settlements (40 items)
    - panel cedears           CEDEARs (~1143 unicos, 2000 items con settlement)
    - panel public-bonds      Bonos publicos soberanos + LECAPs/BONCAPs (1018 items)
    - panel on                Obligaciones negociables corporativas (2117 items)
    - panel cauciones         Cauciones por fecha+plazo (133 items)
    - panel senebi-on         ON segmento SENEBI (3160 items, paginado)
    - panel options           Opciones (429 items, con strike, OI, etc.)

  HISTORICOS (GET):
    - historico <SYM>         Historico OHLCV diario de un instrumento
                              Formato simbolo: "TICKER 24HS" (ej: "GGAL 24HS")
                              Bonds USD: "AL30D 24HS"; CCL: "AL30C 24HS"
    - indice <COD>            Historico de un indice de BYMA (M=MERVAL, G=BURCAP)

  FICHA TECNICA (POST):
    - bond-info <TICKER>      Ficha tecnica de un bono/LECAP/BONCAP/ON:
                              forma de amortizacion, intereses, ISIN, ley,
                              emisor, fechas, monto nominal/residual, etc.

Uso:
    py fetch_byma.py panel leading-equity
    py fetch_byma.py panel leading-equity --t0     # solo CI (settlementType=1)
    py fetch_byma.py panel leading-equity --t1     # solo 24hs (settlementType=2)
    py fetch_byma.py panel cedears
    py fetch_byma.py panel public-bonds            # paginado total 1018
    py fetch_byma.py panel public-bonds --all      # trae todos en una llamada
    py fetch_byma.py panel on
    py fetch_byma.py panel cauciones
    py fetch_byma.py panel senebi-on
    py fetch_byma.py panel options
    py fetch_byma.py historico "GGAL 24HS"
    py fetch_byma.py historico "AL30 24HS"
    py fetch_byma.py historico "AL30D 24HS" --desde 2024-05-15 --hasta 2026-06-05
    py fetch_byma.py historico "AAPL 24HS"
    py fetch_byma.py indice M                      # MERVAL
    py fetch_byma.py indice G                      # BURCAP
    py fetch_byma.py indice M --desde 2025-01-01 --hasta 2026-06-05
    py fetch_byma.py bond-info AE38                # Ficha tecnica AE38
    py fetch_byma.py bond-info AL30                # Ficha tecnica AL30
    py fetch_byma.py bond-info TY30P               # Ficha tecnica BONCAP TY30P
    py fetch_byma.py all                           # snapshot todos los paneles
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Any

import requests
import urllib3

# BYMA usa cert SSL no validable por bundles standard de Python.
# La data es publica, sin credenciales. Disable warnings (autorizado).
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger("byma")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

BASE = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# ── Constantes ─────────────────────────────────────────────────────────────

# Paneles soportados (POST). Key = nombre interno usado en CLI, value = path API.
PANELS = {
    "leading-equity": "leading-equity",
    "cedears": "cedears",
    "public-bonds": "public-bonds",
    "on": "negociable-obligations",
    "cauciones": "cauciones",
    "senebi-on": "senebi-obligaciones-negociables",
    "options": "options",
}

# Paneles que devuelven `{content, data, ...}` (paginados).
# El resto devuelve una lista directa.
PAGED_PANELS = {"leading-equity", "public-bonds", "senebi-on"}

# Indices verificados con datos consistentes:
#   M = MERVAL (~3.0-3.2M actual)
#   G = BURCAP (~135M actual)
# Otros codigos (A, B, V) son aceptados pero devuelven todos ceros.
INDICES_CONOCIDOS = {
    "M": "S&P MERVAL",
    "G": "BURCAP",
}

# Resoluciones soportadas. Para indices, todas devuelven el mismo dataset
# (resolution parece ignorado en index-historical-series).
# Para historical-series de instrumentos: D, W, M tienen efecto real.
RESOLUTIONS = ["D", "W", "M"]


# ── HTTP helpers ───────────────────────────────────────────────────────────


def _post(path: str, payload: dict | None = None) -> Any:
    """POST request. BYMA usa verify=False por su cert SSL no estandar."""
    r = requests.post(
        f"{BASE}/{path}",
        headers=HEADERS,
        json=payload or {},
        timeout=30,
        verify=False,
    )
    r.raise_for_status()
    return r.json()


def _get(path: str, params: dict) -> Any:
    """GET request con verify=False."""
    r = requests.get(
        f"{BASE}/{path}",
        headers=HEADERS,
        params=params,
        timeout=30,
        verify=False,
    )
    r.raise_for_status()
    return r.json()


def _date_to_unix(date_str: str | None, default_days_ago: int = 30) -> int:
    """Convierte 'YYYY-MM-DD' a unix timestamp (segundos UTC)."""
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    return int(time.time()) - default_days_ago * 86400


# ── Paneles ────────────────────────────────────────────────────────────────


def fetch_panel(
    panel: str,
    page: int = 1,
    page_size: int = 200,
    t0: bool = False,
    t1: bool = False,
    fetch_all: bool = False,
) -> Any:
    """Fetch generico de paneles (POST endpoints).

    Args:
        panel: nombre interno del panel (ver PANELS dict).
        page: numero de pagina (1-indexed). NOTA: la API ignora este parametro
              en la version actual — siempre retorna pagina 1. Workaround: usar
              `fetch_all=True` o `page_size` grande.
        page_size: items por pagina. Default 200. Maximo observado: 5000+.
        t0: si True, filtra solo settlementType=1 (CI).
        t1: si True, filtra solo settlementType=2 (24hs).
        fetch_all: si True, fuerza page_size=5000 para traer todo en una sola llamada.

    Returns:
        Para PAGED_PANELS: dict con keys `content`, `data`, `empty`, `upgrade`.
        Para el resto: list directa de items.
    """
    if panel not in PANELS:
        raise ValueError(f"Panel invalido. Validos: {list(PANELS)}")
    path = PANELS[panel]
    payload: dict[str, Any] = {}
    if fetch_all:
        payload["page_size"] = 5000
    else:
        payload["page"] = page
        payload["page_size"] = page_size
    if t0:
        payload["T0"] = True
    if t1:
        payload["T1"] = True
    return _post(path, payload)


# ── Historicos ─────────────────────────────────────────────────────────────


def fetch_historico(
    symbol: str,
    desde: str | None = None,
    hasta: str | None = None,
    resolution: str = "D",
) -> dict:
    """Historico OHLCV diario/semanal/mensual de un instrumento.

    Formato del simbolo: `{TICKER} 24HS`. Ejemplos validos:
        "GGAL 24HS"   — acciones
        "AAPL 24HS"   — CEDEARs ARS
        "AAPLD 24HS"  — CEDEARs USD
        "AL30 24HS"   — bonos ARS
        "AL30D 24HS"  — bonos USD
        "AL30C 24HS"  — bonos CCL
        "TY30P 24HS"  — LECAPs/BONCAPs

    NOTA: el sufijo "CI" no funciona en historicos (retorna 400). Solo 24HS.
    Cualquier ticker sin sufijo retorna 400.

    Args:
        symbol: simbolo completo con " 24HS".
        desde: fecha desde YYYY-MM-DD (default: 30 dias atras).
        hasta: fecha hasta YYYY-MM-DD (default: hoy).
        resolution: D (diario), W (semanal), M (mensual). Default D.

    Returns:
        dict con keys `s` (status), `t[]` (timestamps unix), `o[]`, `h[]`,
        `l[]`, `c[]`, `v[]` (OHLCV arrays sincronizados por indice).
    """
    if resolution not in RESOLUTIONS:
        log.warning(f"Resolution {resolution!r} no estandar; pueden esperarse resultados extraños")
    from_ts = _date_to_unix(desde, default_days_ago=30)
    to_ts = _date_to_unix(hasta, default_days_ago=0)
    return _get("chart/historical-series/history", {
        "symbol": symbol,
        "resolution": resolution,
        "from": from_ts,
        "to": to_ts,
    })


def fetch_indice(
    symbol: str,
    desde: str | None = None,
    hasta: str | None = None,
    resolution: str = "D",
) -> dict:
    """Historico de un indice BYMA.

    Indices verificados con datos:
        M = S&P MERVAL
        G = BURCAP

    Otros codigos (A, B, V, etc.) son aceptados por la API pero retornan
    series con todos ceros — probablemente indices deprecated o sin
    publicacion historica.

    Args:
        symbol: codigo de letra del indice (M, G, etc.).
        desde, hasta: rango YYYY-MM-DD (default: ultimos 30 dias).
        resolution: D/W/M (default D). NOTA: en indices la API ignora este
                    parametro y siempre devuelve diario.

    Returns:
        dict con la misma estructura que `fetch_historico`.
    """
    from_ts = _date_to_unix(desde, default_days_ago=30)
    to_ts = _date_to_unix(hasta, default_days_ago=0)
    return _get("chart/index-historical-series/history", {
        "symbol": symbol,
        "resolution": resolution,
        "from": from_ts,
        "to": to_ts,
    })


# ── Ficha tecnica de bonos / ONs ───────────────────────────────────────────


def fetch_bond_info(symbol: str) -> dict:
    """Ficha tecnica de un bono / LECAP / BONCAP / ON.

    Devuelve TODA la info estatica del instrumento: ley aplicable, forma
    de amortizacion (texto), fechas de emision/vencimiento, ISIN, moneda,
    monto nominal/residual, descripcion de intereses, emisor, tipo de
    garantia, denominacion minima.

    El campo mas importante para finanzas es **`formaAmortizacion`**, que
    describe en texto plano el cronograma de amortizacion (ej: "22 cuotas
    semestrales iguales el 9 de enero y el 9 de julio de cada año desde
    julio 2027 hasta enero 2038"). `interes` describe el esquema de cupones
    (paso a paso para step-up).

    Args:
        symbol: ticker del bono SIN sufijo de settlement.
                Ejemplos: "AE38", "AL30", "GD30", "AE38C", "AE38D",
                "BPOA7", "TY30P", "TZX26", "S237Q", "SBC1C".
                Tambien funciona con variantes por moneda (C, D).
                Para acciones devuelve data vacia.

    Returns:
        dict con keys:
        - `content`: pagination (page_number, page_count, page_size, total_elements_count)
        - `data[0]`: ficha tecnica con keys:
            - `ley`: jurisdiccion (Nacional, Extranjera, etc.)
            - `formaAmortizacion`: TEXTO con cronograma de amortizacion
            - `denominacionMinima`: denominacion minima de emision
            - `fechaVencimiento`: ISO datetime
            - `tipoGarantia`: Comun, etc.
            - `fechaEmision`: ISO datetime
            - `fechaDevenganIntereses`: fecha inicio devengo
            - `codigoIsin`: codigo ISIN
            - `tipoEspecie`: Titulos Publicos, etc.
            - `default`: estado de default
            - `tipoObligacion`: clasificacion regulatoria
            - `montoNominal`: monto nominal emitido
            - `denominacion`: nombre oficial completo
            - `insType`: BOND
            - `paisLey`: pais de la ley aplicable
            - `moneda`: Dolares, Pesos, etc.
            - `montoResidual`: monto residual actual
            - `interes`: TEXTO con esquema de cupones
            - `emisor`: emisor (Gobierno Nacional, Provincia, Corporativo)
        - `empty`: bool
    """
    return _post("bnown/fichatecnica/especies/general", {"symbol": symbol})


# ── Mode ALL ───────────────────────────────────────────────────────────────


def fetch_all() -> dict:
    """Snapshot de TODOS los paneles + indice MERVAL + BURCAP."""
    log.info("Fetching ALL BYMA snapshots...")
    result: dict[str, Any] = {"timestamp": datetime.now().isoformat()}

    for name in PANELS:
        try:
            log.info(f"  Panel {name}...")
            result[f"panel_{name}"] = fetch_panel(name, fetch_all=True)
            time.sleep(0.3)
        except Exception as e:
            log.warning(f"  {name}: {e}")
            result[f"panel_{name}"] = {"error": str(e)}

    for code in INDICES_CONOCIDOS:
        try:
            log.info(f"  Indice {code} ({INDICES_CONOCIDOS[code]})...")
            result[f"indice_{code}"] = fetch_indice(code)
            time.sleep(0.3)
        except Exception as e:
            log.warning(f"  indice {code}: {e}")
            result[f"indice_{code}"] = {"error": str(e)}

    return result


# ── CLI ────────────────────────────────────────────────────────────────────


MODES = ["panel", "historico", "indice", "bond-info", "all"]


def main():
    parser = argparse.ArgumentParser(
        description="BYMA Data Fetcher — Bolsas y Mercados Argentinos"
    )
    parser.add_argument("mode", choices=MODES, help="Modo")
    parser.add_argument(
        "arg", nargs="?",
        help="Argumento: panel name | symbol | indice code"
    )
    parser.add_argument(
        "--page", type=int, default=1,
        help="Pagina (1-indexed). NOTA: ignorada por la API — usar --all"
    )
    parser.add_argument(
        "--page-size", type=int, default=200,
        help="Items por pagina (default: 200; usar grande para 'all')"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Trae todo de una sola llamada (page_size=5000)"
    )
    parser.add_argument(
        "--t0", action="store_true",
        help="Solo settlementType=1 (CI/Contado Inmediato)"
    )
    parser.add_argument(
        "--t1", action="store_true",
        help="Solo settlementType=2 (24hs)"
    )
    parser.add_argument("--desde", help="Fecha desde YYYY-MM-DD (historicos)")
    parser.add_argument("--hasta", help="Fecha hasta YYYY-MM-DD (historicos)")
    parser.add_argument(
        "--resolution", default="D",
        help="Resolucion historico: D, W, M (default: D)"
    )
    parser.add_argument("-o", "--output", help="Guardar a archivo JSON")
    parser.add_argument("-q", "--quiet", action="store_true", help="Modo silencioso")

    args = parser.parse_args()
    if args.quiet:
        log.setLevel(logging.WARNING)

    try:
        if args.mode == "panel":
            if not args.arg:
                log.error(f"Modo 'panel' requiere nombre. Validos: {list(PANELS)}")
                sys.exit(1)
            result = fetch_panel(
                args.arg, page=args.page, page_size=args.page_size,
                t0=args.t0, t1=args.t1, fetch_all=args.all,
            )
        elif args.mode == "historico":
            if not args.arg:
                log.error("Modo 'historico' requiere simbolo (ej: 'GGAL 24HS')")
                sys.exit(1)
            result = fetch_historico(
                args.arg, desde=args.desde, hasta=args.hasta,
                resolution=args.resolution,
            )
        elif args.mode == "indice":
            if not args.arg:
                log.error(f"Modo 'indice' requiere codigo. Conocidos: {INDICES_CONOCIDOS}")
                sys.exit(1)
            result = fetch_indice(
                args.arg.upper(), desde=args.desde, hasta=args.hasta,
                resolution=args.resolution,
            )
        elif args.mode == "bond-info":
            if not args.arg:
                log.error("Modo 'bond-info' requiere ticker (ej: 'AE38', 'AL30', 'TY30P')")
                sys.exit(1)
            result = fetch_bond_info(args.arg.upper())
        elif args.mode == "all":
            result = fetch_all()
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

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        log.info(f"Guardado: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
