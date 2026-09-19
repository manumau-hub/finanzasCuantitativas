"""
MAE.com.ar Data Fetcher — Mercado Abierto Electronico de Argentina.

API publica de market data del MAE (https://www.mae.com.ar). Sin API key,
sin autenticacion. Todos los datos son delayed (cierre del dia anterior
o tiempo real con delay de mercado).

Endpoints disponibles:

  RESUMENES (intraday + historial intradia del titulo lider):
    - resumen RF       Top 10 titulos publicos renta fija (LECAPs, BONCAPs, etc.)
    - resumen CAU      Top cauciones (CAARS, CAUSD por plazo)
    - resumen FOR      Top monedas FOREX (US$, EUR, etc.)
    - resumen DDF      Top contratos futuro dolar (Dolar Diferido a Fix)

  DATOS DE MERCADO (todos los titulos negociados hoy):
    - datos RF         Todas las cotizaciones del dia de renta fija (~289 lineas)
    - datos CAU        Todas las cauciones del dia
    - datos FOR        Todas las cotizaciones FOREX

  VOLUMEN:
    - volumen ARS      Volumen por categoria (Renta Fija TRD, FOREX, etc.) en pesos
    - volumen USD      Mismo en dolares

  MAPA (prospectos por segmento/plazo/moneda):
    - mapa             Mapa de titulos por segmento, plazo y moneda

  INSTITUCIONAL:
    - comunicados      Comunicados del MAE
    - licitaciones     Calendario de licitaciones (proximas + actuales)
    - licitaciones-estado  Licitaciones filtradas por estado (A/F/C/S/P)

  CURVAS RENTA FIJA:
    - flujo-fondos H   Flujo fondos cotizaciones bonos hard dollar (AE38, AL30, etc.)
    - flujo-fondos B   Flujo fondos cotizaciones BOPREALes

  HISTORICOS:
    - hist-rf          Historico renta fija por rango de fechas (grid + chart)
    - hist-forex       Historico FOREX por rango de fechas
    - hist-forex-vol   Historico volumen operado FOREX
    - hist-cau         Historico cauciones por rango
    - hist-cau-vt      Cauciones: serie de volumen y tasas por titulo+plazo
    - hist-repo        Historico repo por rango
    - repo-fecha       Volumen repo y tasa promedio ponderada por fecha

  INDICES:
    - indice-ars       Indice ARS-MAE actual (PBO + PPN intradia)
    - indice-ars-hist  Serie historica del Indice ARS-MAE (PPN diario)

Uso:
    py fetch_mae.py resumen RF
    py fetch_mae.py resumen CAU
    py fetch_mae.py resumen FOR
    py fetch_mae.py resumen DDF
    py fetch_mae.py datos RF
    py fetch_mae.py datos CAU
    py fetch_mae.py datos FOR
    py fetch_mae.py volumen ARS
    py fetch_mae.py volumen USD
    py fetch_mae.py mapa --segmento BT --plazo 001 --moneda '$'
    py fetch_mae.py comunicados
    py fetch_mae.py comunicados --desde 2026-05-05 --hasta 2026-06-05
    py fetch_mae.py licitaciones
    py fetch_mae.py licitaciones-estado --estado A --desde 2026-05-05 --hasta 2026-06-05
    py fetch_mae.py flujo-fondos H
    py fetch_mae.py flujo-fondos B
    py fetch_mae.py hist-rf --desde 2026-05-05 --hasta 2026-06-04
    py fetch_mae.py hist-forex --desde 2026-05-05 --hasta 2026-06-05
    py fetch_mae.py hist-forex-vol --desde 2026-05-05 --hasta 2026-06-05
    py fetch_mae.py hist-cau --desde 2026-05-05 --hasta 2026-06-05
    py fetch_mae.py hist-cau-vt --titulo CAARS --plazo 001 --desde 2026-05-05 --hasta 2026-06-05
    py fetch_mae.py hist-repo --desde 2026-05-05 --hasta 2026-06-05
    py fetch_mae.py repo-fecha --desde 2026-05-05 --hasta 2026-06-05
    py fetch_mae.py indice-ars
    py fetch_mae.py indice-ars-hist --desde 2026-05-05 --hasta 2026-06-05
    py fetch_mae.py all
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import urllib.parse
from datetime import datetime
from typing import Any, Optional

import requests

log = logging.getLogger("mae")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

BASE = "https://api.marketdata.mae.com.ar/api"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# ── Constantes ─────────────────────────────────────────────────────────────

# Resumenes disponibles (verificados ✅; cualquier otro retorna 400).
RESUMEN_TIPOS = ["RF", "CAU", "FOR", "DDF"]

# Datos de mercado disponibles (verificados ✅; DDF retorna 500, otros 400).
DATOS_TIPOS = ["RF", "CAU", "FOR"]

# Monedas para /volumen-categoria. ARS y USD verificados.
VOLUMEN_MONEDAS = ["ARS", "USD"]

# Letras para /emisiones/flujofondoscotiz. Solo B (BOPREAL) y H (Hard dollar)
# tienen datos; el resto retorna lista vacia. C retorna 500.
FLUJO_FONDOS_LETRAS = ["B", "H"]

# Estados validos para /licitacionesporestado/Todos.
# Verificados: A (Activa), F (Finalizada), C (Cancelada), S (Suspendida?), P (Programada).
# Invalidos: M, X, N, I, T, "Todos", "TODOS".
LICITACION_ESTADOS = {
    "A": "Activa",
    "F": "Finalizada",
    "C": "Cancelada",
    "S": "Suspendida",
    "P": "Programada",
}

# Segmentos verificados para /mercado/mapa (response no varia con segmento,
# pero la API acepta cualquiera de estos).
MAPA_SEGMENTOS = ["BT", "PPT", "PT", "BL", "TX", "RV", "EX"]

# Monedas validas para /mercado/mapa.
MAPA_MONEDAS = ["$", "D", "C"]


# ── HTTP Client ────────────────────────────────────────────────────────────


def _get(url: str, params: dict | None = None) -> Any:
    """GET request con error handling."""
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _build_otitulo(d: dict) -> str:
    """Codifica un dict como query param `oTitulo=` en JSON URL-encoded."""
    return urllib.parse.quote(json.dumps(d, separators=(",", ":")))


# ── Resumenes ──────────────────────────────────────────────────────────────


def fetch_resumen(tipo: str) -> list:
    """Resumen intradia del top 10 titulos por categoria.

    Cada item incluye un mini-grafico intradia (`datosGrafico`) con la serie de
    precios y volumenes ejecutados durante la rueda. Util para snapshot rapido
    de los titulos lideres de la categoria.

    Args:
        tipo: RF (renta fija), CAU (cauciones), FOR (forex), DDF (dolar futuro).

    Returns:
        list de dicts con keys: ticker, tipoEmision, descripcion, plazo,
        fechaLiquidacion, moneda, segmento, variacion, ultimo, cantidad,
        monto, datosGrafico {ultimoHoy, variacionPerc, precios[], volumenes[]}.
    """
    if tipo not in RESUMEN_TIPOS:
        raise ValueError(f"Tipo invalido. Validos: {RESUMEN_TIPOS}")
    return _get(f"{BASE}/mercado/resumen/{tipo}")


# ── Datos de mercado ────────────────────────────────────────────────────────


def fetch_datos(tipo: str) -> list:
    """Datos completos de mercado del dia para una categoria.

    Devuelve TODAS las cotizaciones de la rueda (no solo el top 10 como
    `resumen`). Para RF puede devolver ~289 lineas (cada titulo x plazo x moneda).

    Args:
        tipo: RF (renta fija), CAU (cauciones), FOR (forex).
              DDF no esta soportado (retorna 500).

    Returns:
        list de dicts con keys: ticker, tipoEmision, fechaLiquidacion,
        volumen, monto, descripcion, plazo, codigoPlazo, segmento, codigoSegmento,
        moneda, variacion, ultimo, ultimaTasa, cierreAnterior, minimo, maximo,
        openInterest, precioCierre, precioApertura.
    """
    if tipo not in DATOS_TIPOS:
        raise ValueError(f"Tipo invalido. Validos: {DATOS_TIPOS}")
    return _get(f"{BASE}/mercado/datos/{tipo}")


# ── Volumen por categoria ───────────────────────────────────────────────────


def fetch_volumen(moneda: str = "ARS") -> list:
    """Volumen del dia por categoria de mercado (Renta Fija TRD, FOREX, etc.).

    Agrupa el volumen en `grupos`: Contado (Renta Fija TRD / PPT) y Monedas
    (FOREX). Incluye share porcentual de cada categoria dentro de su grupo.

    Args:
        moneda: ARS (pesos) o USD (dolares).

    Returns:
        list de dicts con keys: nombre, descripcion, volumen, share, grupo,
        moneda, orden.
    """
    if moneda not in VOLUMEN_MONEDAS:
        raise ValueError(f"Moneda invalida. Validas: {VOLUMEN_MONEDAS}")
    return _get(f"{BASE}/mercado/volumen-categoria/{moneda}")


# ── Mapa de titulos por segmento/plazo/moneda ───────────────────────────────


def fetch_mapa(segmento: str = "BT", plazo: str = "001", moneda: str = "$") -> dict:
    """Mapa de titulos cotizando por segmento, plazo y moneda.

    Devuelve un dict con keys por moneda ($, D, C) y para cada moneda dos listas:
    `Privados` y `Publicos`. Los items son cotizaciones del segmento/plazo
    especificado.

    Args:
        segmento: BT (Bilateral TRD), PPT, PT, BL, TX, RV, EX, etc.
        plazo: Codigo de plazo: "000" (CI), "001" (24hs), "002" (48hs), etc.
        moneda: "$" (pesos), "D" (dolar MEP/CCL?), "C" (cable?). El response
                siempre devuelve las 3, pero el filtro por moneda condiciona
                cuales tienen contenido.

    Returns:
        dict con keys "$", "D", "C", cada una conteniendo dicts con
        "Privados" y "Publicos" como listas de cotizaciones.
    """
    q = _build_otitulo({"segmento": segmento, "plazo": plazo, "moneda": moneda})
    return _get(f"{BASE}/mercado/mapa?oTitulo={q}")


# ── Institucional ───────────────────────────────────────────────────────────


def fetch_comunicados(desde: str | None = None, hasta: str | None = None) -> list:
    """Comunicados institucionales del MAE.

    Sin filtro: devuelve los ultimos 60 comunicados.
    Con filtro de fechas: aplica filtrado server-side.

    Args:
        desde: Fecha desde en formato YYYY-MM-DD (opcional).
        hasta: Fecha hasta en formato YYYY-MM-DD (opcional).

    Returns:
        list de dicts con keys: id, fecha, numero, titulo, tipo, archivos[].
        Cada archivo tiene `nombre` y `url` (PDF en SharePoint).
    """
    url = f"{BASE}/institucional/comunicados"
    if desde or hasta:
        q = _build_otitulo({"fechaDesde": desde or "", "fechaHasta": hasta or ""})
        url += f"?oTitulo={q}"
    return _get(url)


def fetch_licitaciones() -> dict:
    """Calendario de licitaciones primarias proximas + activas.

    Equivale al endpoint `/mercado/repo/tasas` (mismo response).

    Returns:
        dict con keys: timeZone, events[]. Cada evento tiene id, title,
        start, end (fechas en UTC ISO8601).
    """
    return _get(f"{BASE}/mercado/licitaciones")


def fetch_licitaciones_estado(estado: str = "A", desde: str | None = None,
                              hasta: str | None = None) -> list:
    """Licitaciones detalladas filtradas por estado y rango de fechas.

    Devuelve mucha mas info que `licitaciones` (calendario): emisor, industria,
    monto a licitar, modalidad, colocadores, monto adjudicado, valor de corte,
    duration, comentarios, plazos, archivos.

    Args:
        estado: A (Activa), F (Finalizada), C (Cancelada), S (Suspendida),
                P (Programada). Otros valores retornan 400.
        desde: Fecha desde YYYY-MM-DD.
        hasta: Fecha hasta YYYY-MM-DD.

    Returns:
        list de dicts con keys: fechaInicio, fechaFin, fechaLiquidacion,
        fechaVencimiento, titulo, emisor, industria, moneda, montoaLicitar,
        rueda, modalidad, liquidador, estado, tipo, colocador, observaciones,
        monto_Adjudicado, sistema_Adjudicacion, valor_Corte, duration, id,
        comentario, fechaModificacion, plazoEspecie, archivos[].
    """
    if estado not in LICITACION_ESTADOS:
        raise ValueError(f"Estado invalido. Validos: {list(LICITACION_ESTADOS)}")
    q = _build_otitulo({
        "estado": estado,
        "fechaDesde": desde or "",
        "fechaHasta": hasta or "",
    })
    return _get(f"{BASE}/mercado/licitacionesporestado/Todos?oTitulo={q}")


# ── Flujo de fondos para curvas de renta fija ───────────────────────────────


def fetch_flujo_fondos(letra: str) -> list:
    """Flujo de fondos teorico de bonos cotizantes para construir curva TIR/MD.

    Devuelve, para cada bono de la letra, su precio actual, TIR, MD y
    el flujo de fondos completo (cashflow, renta, amortizacion por fecha).

    Args:
        letra: B (BOPREAL serie 1: BPOB7, BPOD7, BPOC7), H (bonos hard dollar
               step-up: AE38, etc.). Otras letras retornan lista vacia.

    Returns:
        list de dicts con keys: especie, numeroCuponActual, renta, amortizacion,
        amasR, moneda, descripcion, precio, tir, md, detalle[].
        `detalle` es la lista de cashflows futuros: fechaPago, vr, vrCartera,
        cashFlow, renta, amortizacion, amasR.
    """
    return _get(f"{BASE}/emisiones/flujofondoscotiz/{letra}")


# ── Historicos por rango de fechas ──────────────────────────────────────────


def fetch_historico_rf(desde: str, hasta: str) -> dict:
    """Historico de renta fija agrupado por dia.

    Args:
        desde: Fecha desde YYYY-MM-DD.
        hasta: Fecha hasta YYYY-MM-DD.

    Returns:
        dict con keys `grid` y `chart`. `grid` es lista por fecha con
        volumen total y `details` (lista de todas las operaciones del dia).
    """
    q = _build_otitulo({"fechaDesde": desde, "fechaHasta": hasta})
    return _get(f"{BASE}/mercado/titulo/historicorentafija?oTitulo={q}")


def fetch_historico_forex(desde: str, hasta: str) -> list:
    """Historico FOREX agrupado por dia.

    Args:
        desde, hasta: YYYY-MM-DD.

    Returns:
        list de dicts con keys: fecha, cantidad, volumen, details[].
    """
    q = _build_otitulo({"fechaDesde": desde, "fechaHasta": hasta})
    return _get(f"{BASE}/mercado/titulo/historicoforex?oTitulo={q}")


def fetch_historico_forex_volumen(desde: str, hasta: str) -> list:
    """Solo volumen total FOREX por dia (sin detalle).

    Args:
        desde, hasta: YYYY-MM-DD.

    Returns:
        list de dicts con keys: fecha, volumen, cant_Millones.
    """
    q = _build_otitulo({"fechaDesde": desde, "fechaHasta": hasta})
    return _get(f"{BASE}/mercado/titulo/historicoforex/volumenoperado?oTitulo={q}")


def fetch_historico_cauciones(desde: str, hasta: str) -> list:
    """Historico de cauciones agrupado por dia.

    Args:
        desde, hasta: YYYY-MM-DD.

    Returns:
        list de dicts con keys: fecha, volumen, details[] (cotizaciones).
    """
    q = _build_otitulo({"fechaDesde": desde, "fechaHasta": hasta})
    return _get(f"{BASE}/mercado/titulo/historicocauciones?oTitulo={q}")


def fetch_cauciones_volumen_tasas(titulo: str, plazo: str, desde: str, hasta: str) -> dict:
    """Series temporales de tasa y volumen de una caucion especifica.

    Args:
        titulo: CAARS (caucion pesos), CAUSD (caucion dolar), o CAU (todos).
        plazo: "001" (1 dia), "007" (7 dias), etc.
        desde, hasta: YYYY-MM-DD.

    Returns:
        dict con keys: tasa[], volumen[]. Cada item: {time: unix_ts, value: float}.
    """
    q = _build_otitulo({
        "codTitulo": titulo, "plazo": plazo,
        "fechaDesde": desde, "fechaHasta": hasta,
    })
    return _get(f"{BASE}/mercado/cauciones/valorescierre/volumentasas?oTitulo={q}")


def fetch_historico_repo(desde: str, hasta: str) -> list:
    """Historico REPO agrupado por dia con detalle por rueda (REPO, REPX, SIMU).

    Args:
        desde, hasta: YYYY-MM-DD.

    Returns:
        list de dicts: fecha, volumen, details[] (cotizaciones por rueda).
        Cada detail incluye: rueda, moneda, tasaApertura, ultimaTasa,
        tasaMaximo, tasaMinimo, cierreAyer, cantidad, volumen, tasaPP,
        variacion, cantOperaciones, plazo, segmento.
    """
    q = _build_otitulo({"fechaDesde": desde, "fechaHasta": hasta})
    return _get(f"{BASE}/mercado/titulo/historicorepo?oTitulo={q}")


def fetch_repo_titulos_fecha(desde: str, hasta: str, unit: str = "USD") -> list:
    """Volumen REPO y tasa promedio ponderada por fecha (sin detalle por rueda).

    Nota: el parametro `unit` NO afecta el response (todos los valores
    retornan iguales). Se mantiene por compatibilidad con la API.

    Args:
        desde, hasta: YYYY-MM-DD.
        unit: USD (default). Ignorado por la API.

    Returns:
        list de dicts: fecha, volumen, details {plazo, volumen, tPP, tPPnBCRA}.
    """
    q = _build_otitulo({
        "fechaDesde": desde, "fechaHasta": hasta, "unit": unit,
    })
    return _get(f"{BASE}/mercado/repo/titulosfecha?oTitulo={q}")


# ── Indices ─────────────────────────────────────────────────────────────────


def fetch_indice_ars() -> list:
    """Indice ARS-MAE actual: PBO + PPN intradia (snapshot horario).

    Devuelve los ultimos 10 puntos intradia con tipo PBO (precio base operativo)
    y PPN (precio promedio ponderado).

    Returns:
        list de dicts con keys: fecha, tipo (PBO|PPN), valor, valorNuevo.
    """
    return _get(f"{BASE}/mercado/indiceARS")


def fetch_indice_ars_historico(desde: str, hasta: str) -> list:
    """Serie historica diaria del indice ARS-MAE (PPN al cierre).

    Args:
        desde, hasta: YYYY-MM-DD.

    Returns:
        list de dicts con keys: id, fecha, valor, valorNuevo.
    """
    q = _build_otitulo({"fechaDesde": desde, "fechaHasta": hasta})
    return _get(f"{BASE}/mercado/titulo/indicearsmae/historico?oTitulo={q}")


# ── Mode ALL ────────────────────────────────────────────────────────────────


def fetch_all() -> dict:
    """Fetch de TODOS los snapshots de mercado actuales (sin historicos)."""
    log.info("Fetching ALL market snapshots...")
    result = {"timestamp": datetime.now().isoformat()}

    snapshots: list[tuple[str, Any]] = [
        ("resumen_RF", lambda: fetch_resumen("RF")),
        ("resumen_CAU", lambda: fetch_resumen("CAU")),
        ("resumen_FOR", lambda: fetch_resumen("FOR")),
        ("resumen_DDF", lambda: fetch_resumen("DDF")),
        ("datos_RF", lambda: fetch_datos("RF")),
        ("datos_CAU", lambda: fetch_datos("CAU")),
        ("datos_FOR", lambda: fetch_datos("FOR")),
        ("volumen_ARS", lambda: fetch_volumen("ARS")),
        ("volumen_USD", lambda: fetch_volumen("USD")),
        ("comunicados", fetch_comunicados),
        ("licitaciones", fetch_licitaciones),
        ("indice_ars", fetch_indice_ars),
        ("flujo_fondos_B", lambda: fetch_flujo_fondos("B")),
        ("flujo_fondos_H", lambda: fetch_flujo_fondos("H")),
    ]
    for name, fn in snapshots:
        try:
            log.info(f"  Fetching {name}...")
            result[name] = fn()
            time.sleep(0.3)
        except Exception as e:
            log.warning(f"  {name}: {e}")
            result[name] = {"error": str(e)}
    return result


# ── CLI ─────────────────────────────────────────────────────────────────────


MODES = [
    "resumen", "datos", "volumen", "mapa",
    "comunicados", "licitaciones", "licitaciones-estado",
    "flujo-fondos",
    "hist-rf", "hist-forex", "hist-forex-vol", "hist-cau", "hist-cau-vt",
    "hist-repo", "repo-fecha",
    "indice-ars", "indice-ars-hist",
    "all",
]


def main():
    parser = argparse.ArgumentParser(
        description="MAE.com.ar Data Fetcher — Mercado Abierto Electronico de Argentina"
    )
    parser.add_argument("mode", choices=MODES, help="Modo de operacion")
    parser.add_argument(
        "arg", nargs="?",
        help="Argumento posicional segun el modo (tipo, moneda, letra, etc.)"
    )
    parser.add_argument("--desde", help="Fecha desde YYYY-MM-DD")
    parser.add_argument("--hasta", help="Fecha hasta YYYY-MM-DD")
    parser.add_argument(
        "--segmento", default="BT",
        help="Segmento para mapa (default: BT). Valores: BT, PPT, PT, BL, TX, RV, EX"
    )
    parser.add_argument(
        "--plazo", default="001",
        help="Plazo (default: 001). Ej: 000 (CI), 001 (24hs), 002 (48hs), 007 (7d)"
    )
    parser.add_argument(
        "--moneda", default="$",
        help="Moneda para mapa (default: $). Valores: $, D, C"
    )
    parser.add_argument(
        "--estado", default="A",
        help="Estado licitacion para licitaciones-estado (default: A). "
             "Valores: A (Activa), F (Finalizada), C (Cancelada), S (Suspendida), P (Programada)"
    )
    parser.add_argument(
        "--titulo", default="CAARS",
        help="Ticker para hist-cau-vt (default: CAARS). Valores: CAARS, CAUSD, CAU"
    )
    parser.add_argument(
        "--unit", default="USD",
        help="Unit para repo-fecha (default: USD). Nota: la API ignora este parametro."
    )
    parser.add_argument("-o", "--output", help="Guardar output a archivo JSON")
    parser.add_argument("-q", "--quiet", action="store_true", help="Modo silencioso")

    args = parser.parse_args()
    if args.quiet:
        log.setLevel(logging.WARNING)

    mode = args.mode
    pos = (args.arg or "").upper() if args.arg else None

    # ── Dispatch ──────────────────────────────────────────────────────
    try:
        if mode == "resumen":
            if not pos:
                log.error(f"Modo 'resumen' requiere tipo. Validos: {RESUMEN_TIPOS}")
                sys.exit(1)
            result = fetch_resumen(pos)
        elif mode == "datos":
            if not pos:
                log.error(f"Modo 'datos' requiere tipo. Validos: {DATOS_TIPOS}")
                sys.exit(1)
            result = fetch_datos(pos)
        elif mode == "volumen":
            moneda = pos or "ARS"
            result = fetch_volumen(moneda)
        elif mode == "mapa":
            result = fetch_mapa(args.segmento, args.plazo, args.moneda)
        elif mode == "comunicados":
            result = fetch_comunicados(args.desde, args.hasta)
        elif mode == "licitaciones":
            result = fetch_licitaciones()
        elif mode == "licitaciones-estado":
            if not args.desde or not args.hasta:
                log.error("Modo 'licitaciones-estado' requiere --desde y --hasta")
                sys.exit(1)
            result = fetch_licitaciones_estado(args.estado, args.desde, args.hasta)
        elif mode == "flujo-fondos":
            if not pos:
                log.error(f"Modo 'flujo-fondos' requiere letra. Validas: {FLUJO_FONDOS_LETRAS}")
                sys.exit(1)
            result = fetch_flujo_fondos(pos)
        elif mode == "hist-rf":
            if not args.desde or not args.hasta:
                log.error("Modo 'hist-rf' requiere --desde y --hasta")
                sys.exit(1)
            result = fetch_historico_rf(args.desde, args.hasta)
        elif mode == "hist-forex":
            if not args.desde or not args.hasta:
                log.error("Modo 'hist-forex' requiere --desde y --hasta")
                sys.exit(1)
            result = fetch_historico_forex(args.desde, args.hasta)
        elif mode == "hist-forex-vol":
            if not args.desde or not args.hasta:
                log.error("Modo 'hist-forex-vol' requiere --desde y --hasta")
                sys.exit(1)
            result = fetch_historico_forex_volumen(args.desde, args.hasta)
        elif mode == "hist-cau":
            if not args.desde or not args.hasta:
                log.error("Modo 'hist-cau' requiere --desde y --hasta")
                sys.exit(1)
            result = fetch_historico_cauciones(args.desde, args.hasta)
        elif mode == "hist-cau-vt":
            if not args.desde or not args.hasta:
                log.error("Modo 'hist-cau-vt' requiere --desde y --hasta")
                sys.exit(1)
            result = fetch_cauciones_volumen_tasas(
                args.titulo, args.plazo, args.desde, args.hasta
            )
        elif mode == "hist-repo":
            if not args.desde or not args.hasta:
                log.error("Modo 'hist-repo' requiere --desde y --hasta")
                sys.exit(1)
            result = fetch_historico_repo(args.desde, args.hasta)
        elif mode == "repo-fecha":
            if not args.desde or not args.hasta:
                log.error("Modo 'repo-fecha' requiere --desde y --hasta")
                sys.exit(1)
            result = fetch_repo_titulos_fecha(args.desde, args.hasta, args.unit)
        elif mode == "indice-ars":
            result = fetch_indice_ars()
        elif mode == "indice-ars-hist":
            if not args.desde or not args.hasta:
                log.error("Modo 'indice-ars-hist' requiere --desde y --hasta")
                sys.exit(1)
            result = fetch_indice_ars_historico(args.desde, args.hasta)
        elif mode == "all":
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

    # ── Output ─────────────────────────────────────────────────────────
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        log.info(f"Guardado en: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
