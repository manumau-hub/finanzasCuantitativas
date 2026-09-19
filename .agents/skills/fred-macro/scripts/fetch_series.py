"""
FRED Series Fetcher — Descarga datos macroeconómicos de la Reserva Federal.

Uso:
    py fetch_series.py --series GDP,UNRATE,FEDFUNDS --api-key TU_API_KEY
    py fetch_series.py --series CPIAUCSL --start 2020-01-01 --end 2025-12-31 --output cpi.csv
    py fetch_series.py --series DGS10 --frequency d --units chg --output 10y_changes.parquet
    py fetch_series.py --series M2SL --plot
    py fetch_series.py --api-key TU_API_KEY --series-list (lista todas las series disponibles)
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import requests

# ── Config ──────────────────────────────────────────────────────────────────

BASE_URL = "https://api.stlouisfed.org/fred"
DEFAULT_START = "2000-01-01"
DEFAULT_END = datetime.now().strftime("%Y-%m-%d")
REQUEST_DELAY = 1.0  # segundos entre requests (120 req/min ≈ 0.5s, pero usamos 1s por seguridad)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fred")


# ── FRED Client ─────────────────────────────────────────────────────────────


class FredClient:
    """Cliente para la API de FRED."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self._last_request = 0.0

    def _rate_limit(self):
        """Rate limiting simple: asegura pausa entre requests."""
        elapsed = time.time() - self._last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self._last_request = time.time()

    def _get(self, endpoint: str, params: dict) -> dict:
        """Request genérico a la API de FRED."""
        self._rate_limit()
        url = f"{BASE_URL}/{endpoint}"
        params["api_key"] = self.api_key
        params["file_type"] = "json"
        try:
            r = self.session.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            if r.status_code == 429:
                log.error("Rate limit excedido (429). Esperá 60s y reintentá.")
            elif r.status_code == 400:
                try:
                    err = r.json()
                    log.error(f"Error 400: {err.get('error_message', 'Bad Request')}")
                except Exception:
                    log.error(f"Error 400: {r.text[:200]}")
            elif r.status_code == 404:
                log.error(f"Serie no encontrada (404). Revisá el series_id.")
            else:
                log.error(f"HTTP {r.status_code}: {e}")
            raise

    # ── Métodos públicos ─────────────────────────────────────────────────

    def fetch_series(
        self,
        series_id: str,
        start: str = DEFAULT_START,
        end: str = DEFAULT_END,
        units: str = "lin",
        frequency: Optional[str] = None,
        agg_method: str = "avg",
        limit: int = 100000,
    ) -> pd.DataFrame:
        """
        Descarga observaciones de una serie FRED.

        Args:
            series_id: ID de la serie (ej: 'GDP', 'UNRATE')
            start: Fecha inicio YYYY-MM-DD
            end: Fecha fin YYYY-MM-DD
            units: 'lin', 'chg', 'ch1', 'pch', 'pc1', 'pca', 'log'
            frequency: 'd', 'w', 'bw', 'm', 'q', 'sa', 'a' (opcional)
            agg_method: 'avg', 'sum', 'eop'
            limit: Máx observaciones (default 100000)

        Returns:
            DataFrame con índice de fechas y columna 'value'
        """
        params = {
            "series_id": series_id.upper(),
            "observation_start": start,
            "observation_end": end,
            "units": units,
            "aggregation_method": agg_method,
            "sort_order": "asc",
            "limit": limit,
        }
        if frequency:
            params["frequency"] = frequency

        log.info(f"Descargando {series_id} ({start} → {end})...")
        data = self._get("series/observations", params)
        records = data.get("observations", [])

        if not records:
            log.warning(f"Sin datos para {series_id}")
            return pd.DataFrame()

        # Armar DataFrame (solo date + value)
        df = pd.DataFrame(records)
        df = df[["date", "value"]]
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])
        df = df.set_index("date").sort_index()
        df.index.name = "date"
        df = df.rename(columns={"value": series_id.upper()})

        log.info(f"  → {len(df)} observaciones ({df.index[0].date()} → {df.index[-1].date()})")
        return df

    def fetch_multiple(
        self,
        series_ids: list,
        start: str = DEFAULT_START,
        end: str = DEFAULT_END,
        units: str = "lin",
        frequency: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Descarga múltiples series y las combina en un solo DataFrame.

        Args:
            series_ids: Lista de IDs de series
            start, end, units, frequency: igual que fetch_series

        Returns:
            DataFrame con columnas por serie, alineadas por fecha
        """
        dfs = []
        for sid in series_ids:
            df = self.fetch_series(sid, start, end, units, frequency)
            if not df.empty:
                dfs.append(df)
        if not dfs:
            return pd.DataFrame()
        result = pd.concat(dfs, axis=1, sort=True)
        log.info(f"Total combinado: {result.shape[0]} filas × {result.shape[1]} columnas")
        return result

    def get_metadata(self, series_id: str) -> dict:
        """Obtiene metadatos de una serie."""
        data = self._get("series", {"series_id": series_id.upper()})
        series_list = data.get("seriess", [])
        return series_list[0] if series_list else {}

    def search_series(
        self,
        query: str,
        search_type: str = "full_text",
        limit: int = 50,
        order_by: str = "popularity",
    ) -> list:
        """Busca series por texto."""
        params = {
            "search_text": query,
            "search_type": search_type,
            "limit": limit,
            "order_by": order_by,
            "sort_order": "desc",
        }
        data = self._get("series/search", params)
        return data.get("seriess", [])

    def get_series_in_category(self, category_id: int, limit: int = 100) -> list:
        """Lista series dentro de una categoría."""
        params = {"category_id": category_id, "limit": limit}
        data = self._get("category/series", params)
        return data.get("seriess", [])

    def get_categories(self, series_id: str) -> list:
        """Obtiene categorías de una serie."""
        data = self._get("series/categories", {"series_id": series_id.upper()})
        return data.get("categories", [])


# ── Output ──────────────────────────────────────────────────────────────────


def save_output(df: pd.DataFrame, filepath: str):
    """Guarda DataFrame en CSV, JSON o Parquet según extensión."""
    ext = os.path.splitext(filepath)[1].lower()
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    if ext == ".csv":
        df.to_csv(filepath)
        log.info(f"Guardado CSV: {filepath} ({os.path.getsize(filepath):,} bytes)")
    elif ext == ".json":
        df.reset_index().to_json(filepath, orient="records", date_format="iso", indent=2)
        log.info(f"Guardado JSON: {filepath}")
    elif ext == ".parquet":
        try:
            df.to_parquet(filepath, compression="zstd")
            log.info(f"Guardado Parquet: {filepath} ({os.path.getsize(filepath):,} bytes)")
        except ImportError:
            csv_fallback = filepath.replace(".parquet", ".csv")
            log.warning(f"pyarrow/fastparquet no disponible. Guardando como CSV: {csv_fallback}")
            df.to_csv(csv_fallback)
    else:
        df.to_csv(filepath + ".csv")
        log.info(f"Extensión no reconocida. Guardado como CSV: {filepath}.csv")


def plot_series(df: pd.DataFrame, title: str = "FRED Series"):
    """Grafica las series del DataFrame."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        log.warning("matplotlib no instalado. No se puede graficar.")
        return

    if df.empty:
        log.warning("DataFrame vacío, nada que graficar.")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    df.plot(ax=ax, title=title, grid=True)
    plt.tight_layout()
    plt.show()
    log.info("Gráfico mostrado.")


# ── CLI ─────────────────────────────────────────────────────────────────────


def print_series_info(series_list: list, title: str = "Series encontradas"):
    """Imprime lista de series en formato tabla."""
    if not series_list:
        print(f"\n  No se encontraron series.")
        return
    print(f"\n  {title}: {len(series_list)}")
    print(f"  {'ID':<15} {'Popularidad':<12} {'Frecuencia':<12} {'Título'}")
    print(f"  {'-'*15} {'-'*12} {'-'*12} {'-'*60}")
    for s in series_list:
        pop = s.get("popularity", "N/A")
        freq = s.get("frequency_short", "?")
        title_txt = s.get("title", "")[:60]
        print(f"  {s['id']:<15} {pop:<12} {freq:<12} {title_txt}")


def main():
    parser = argparse.ArgumentParser(
        description="FRED Data Fetcher — Descarga datos macroeconómicos de la Fed.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  py fetch_series.py --series GDP,UNRATE --api-key KEY
  py fetch_series.py --series CPIAUCSL --start 2020-01-01 --end 2025-12-31 -o cpi.csv
  py fetch_series.py --series DGS10 --frequency d --units chg -o 10y.parquet
  py fetch_series.py --series M2SL --plot
  py fetch_series.py --search "inflation" --limit 20
  py fetch_series.py --category 32995 --limit 50
  py fetch_series.py --metadata FEDFUNDS
        """,
    )

    # API Key
    parser.add_argument(
        "--api-key",
        default=os.getenv("FRED_API_KEY", ""),
        help="FRED API key (o setear FRED_API_KEY env var)",
    )

    # Fetch
    parser.add_argument(
        "--series",
        help="Series IDs separadas por coma (ej: GDP,UNRATE,FEDFUNDS)",
    )
    parser.add_argument("--start", default=DEFAULT_START, help="Fecha inicio YYYY-MM-DD")
    parser.add_argument("--end", default=DEFAULT_END, help="Fecha fin YYYY-MM-DD")
    parser.add_argument(
        "--units",
        default="lin",
        choices=["lin", "chg", "ch1", "pch", "pc1", "pca", "log"],
        help="Transformación de unidades",
    )
    parser.add_argument(
        "--frequency",
        choices=["d", "w", "bw", "m", "q", "sa", "a"],
        help="Frecuencia objetivo (opcional)",
    )

    # Output
    parser.add_argument("-o", "--output", help="Archivo de salida (.csv, .json, .parquet)")
    parser.add_argument("--plot", action="store_true", help="Graficar las series")

    # Metadata y búsqueda
    parser.add_argument("--metadata", help="Obtener metadatos de una serie")
    parser.add_argument(
        "--search",
        help="Buscar series por texto",
    )
    parser.add_argument("--limit", type=int, default=20, help="Límite de resultados de búsqueda")
    parser.add_argument(
        "--category",
        type=int,
        help="Listar series de una categoría (ej: 32995 = tasas de interés)",
    )

    args = parser.parse_args()

    # ── API Key ────────────────────────────────────────────────────────
    api_key = args.api_key
    if not api_key:
        log.error(
            "API Key no encontrada. Usá --api-key o setea FRED_API_KEY env var.\n"
            "  Obtener: https://fred.stlouisfed.org/docs/api/api_key.html"
        )
        sys.exit(1)

    client = FredClient(api_key)

    # ── Solo metadatos ─────────────────────────────────────────────────
    if args.metadata:
        meta = client.get_metadata(args.metadata)
        if meta:
            print(f"\n  ── Metadatos: {meta['id']} ──")
            for k, v in meta.items():
                print(f"    {k}: {v}")
        else:
            log.error(f"Serie '{args.metadata}' no encontrada.")
        return

    # ── Búsqueda ────────────────────────────────────────────────────────
    if args.search:
        results = client.search_series(args.search, limit=args.limit)
        print_series_info(results, f'Resultados para "{args.search}"')
        return

    # ── Categoría ──────────────────────────────────────────────────────
    if args.category:
        results = client.get_series_in_category(args.category, limit=args.limit)
        print_series_info(results, f"Series en categoría {args.category}")
        return

    # ── Fetch ───────────────────────────────────────────────────────────
    if not args.series:
        parser.print_help()
        print("\n\n⚠️  Usá --series o --search o --category o --metadata")
        sys.exit(1)

    series_ids = [s.strip().upper() for s in args.series.split(",")]
    if not series_ids:
        log.error("No se especificaron series.")
        sys.exit(1)

    df = client.fetch_multiple(series_ids, args.start, args.end, args.units, args.frequency)

    if df.empty:
        log.warning("No se obtuvieron datos.")
        sys.exit(1)

    # Estadísticas básicas
    print(f"\n  == Resumen ==")
    print(f"  Periodo: {df.index[0].date()} -> {df.index[-1].date()}")
    print(f"  Observaciones: {len(df)}")
    print(f"  Series: {', '.join(df.columns)}")

    stats = df.describe().round(4)
    print(f"\n  Estadisticas:\n{stats.to_string()}")

    # Guardar
    if args.output:
        save_output(df, args.output)
    else:
        # Default CSV
        default_name = f"fred_{'_'.join(series_ids[:3])}_{args.start}_{args.end}.csv"
        default_name = default_name.replace("-", "")
        save_output(df, default_name)

    # Graficar
    if args.plot:
        plot_series(df, f"FRED: {', '.join(series_ids)}")


if __name__ == "__main__":
    main()
