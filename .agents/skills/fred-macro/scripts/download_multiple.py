"""
FRED Batch Downloader — Descarga batches predefinidos de series FRED.

Uso:
    py download_multiple.py --api-key TU_API_KEY
    py download_multiple.py --api-key KEY --category interest-rates --output-dir data/fred
    py download_multiple.py --api-key KEY --all --format parquet
    py download_multiple.py --api-key KEY --custom GDP,UNRATE,FEDFUNDS,CPIAUCSL --start 2015-01-01
"""

import argparse
import logging
import os
import sys
from datetime import datetime

import pandas as pd

# ── Config ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fred-batch")

# ── Categorías predefinidas ─────────────────────────────────────────────────

CATEGORIES = {
    "gdp": {
        "name": "Producto Interno Bruto",
        "series": ["GDP", "GDPC1", "GDPPOT", "A191RL1Q225SBEA", "GPDI", "A939RX0Q048SBEA"],
    },
    "inflation-cpi": {
        "name": "Inflación (CPI)",
        "series": [
            "CPIAUCSL",
            "CPILFESL",
            "CPIENGSL",
            "CPIFABSL",
            "CPITRNSL",
            "CUSR0000SAD",
        ],
    },
    "inflation-pce": {
        "name": "Inflación (PCE)",
        "series": ["PCE", "PCEC96", "PCECTPI", "PCEPILFE"],
    },
    "interest-rates": {
        "name": "Tasas de Interés",
        "series": [
            "FEDFUNDS",
            "DFF",
            "SOFR",
            "PRIME",
            "DGS1MO",
            "DGS3MO",
            "DGS6MO",
            "DGS1",
            "DGS2",
            "DGS3",
            "DGS5",
            "DGS7",
            "DGS10",
            "DGS20",
            "DGS30",
        ],
    },
    "spreads": {
        "name": "Spreads de Tasas",
        "series": ["T10Y2Y", "T10Y3M", "BAA10Y", "AAA10Y", "T5YIE", "T10YIE"],
    },
    "employment": {
        "name": "Empleo",
        "series": [
            "UNRATE",
            "PAYEMS",
            "CIVPART",
            "EMRATIO",
            "U6RATE",
            "AWHMAN",
            "CES0500000003",
            "JTSJOL",
            "JTSQUR",
            "ICSA",
        ],
    },
    "money-supply": {
        "name": "Oferta Monetaria",
        "series": ["M1SL", "M2SL", "M2V", "M1V", "BOGMBASE", "WRESBAL", "TOTBKCR"],
    },
    "financial-markets": {
        "name": "Mercados Financieros",
        "series": [
            "VIXCLS",
            "SP500",
            "NASDAQCOM",
            "DJIA",
            "WILL5000PR",
            "DEXUSEU",
            "DEXJPUS",
            "DTWEXBGS",
        ],
    },
    "housing": {
        "name": "Vivienda",
        "series": [
            "HOUST",
            "HOUST1F",
            "HOUST5F",
            "PERMIT",
            "CSUSHPISA",
            "MORTGAGE30US",
            "MORTGAGE15US",
        ],
    },
    "consumer": {
        "name": "Consumo",
        "series": [
            "TOTALSA",
            "PCDG",
            "PCND",
            "PCESV",
            "PSAVERT",
            "UMCSENT",
        ],
    },
    "industry": {
        "name": "Industria",
        "series": [
            "INDPRO",
            "CAPUTL",
            "TCU",
            "IPMAN",
            "BUSINV",
        ],
    },
    "government": {
        "name": "Gobierno",
        "series": [
            "GFDEBTN",
            "FYFSD",
            "FGEXPND",
            "FGRECPT",
            "MTSDS133FMS",
        ],
    },
    "trade": {
        "name": "Comercio Exterior",
        "series": ["BOPGSTB", "BOPCAT", "IMPGS", "EXPGS"],
    },
    "recession-indicators": {
        "name": "Indicadores de Recesión",
        "series": [
            "USREC",
            "STLFSI",
            "NFCI",
            "TEDRATE",
            "DFII10",
            "EXPINF1YR",
            "EXPINF10YR",
        ],
    },
}

ALL_SERIES = sorted(set(s for cat in CATEGORIES.values() for s in cat["series"]))


def fetch_fred_series(series_id, api_key, start, end):
    """Descarga una serie FRED y retorna Series de pandas."""
    import requests

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start,
        "observation_end": end,
        "sort_order": "asc",
    }
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    obs = data.get("observations", [])

    records = []
    for o in obs:
        if o["value"] != ".":
            records.append({"date": o["date"], series_id: float(o["value"])})

    if not records:
        return pd.Series(name=series_id, dtype=float)

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")[series_id]


# ── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="FRED Batch Downloader — Descarga batches de series.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Categorías disponibles: {', '.join(CATEGORIES.keys())}

Ejemplos:
  py download_multiple.py --api-key KEY
  py download_multiple.py --api-key KEY --category interest-rates
  py download_multiple.py --api-key KEY --all --format parquet
  py download_multiple.py --api-key KEY --custom GDP,UNRATE,FEDFUNDS -o data.gzip
        """,
    )

    parser.add_argument(
        "--api-key",
        default=os.getenv("FRED_API_KEY", ""),
        help="FRED API key (o FRED_API_KEY env var)",
    )
    parser.add_argument(
        "--category",
        choices=list(CATEGORIES.keys()) + ["all"],
        help="Categoría predefinida a descargar",
    )
    parser.add_argument("--all", action="store_true", help="Descargar TODAS las categorías")
    parser.add_argument(
        "--custom",
        help="Lista custom de series separadas por coma (ej: GDP,UNRATE,FEDFUNDS)",
    )

    parser.add_argument(
        "--start",
        default="2000-01-01",
        help="Fecha inicio YYYY-MM-DD (default: 2000-01-01)",
    )
    parser.add_argument(
        "--end",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Fecha fin YYYY-MM-DD (default: hoy)",
    )

    parser.add_argument(
        "--output-dir",
        default="fred_data",
        help="Directorio de salida (default: fred_data)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "parquet"],
        default="csv",
        help="Formato de archivo (default: csv)",
    )

    args = parser.parse_args()

    api_key = args.api_key
    if not api_key:
        log.error(
            "API Key no encontrada. Usá --api-key o setea FRED_API_KEY.\n"
            "  Obtener: https://fred.stlouisfed.org/docs/api/api_key.html"
        )
        sys.exit(1)

    # Determinar qué series descargar
    series_to_download = {}

    if args.custom:
        series_list = [s.strip().upper() for s in args.custom.split(",")]
        series_to_download["custom"] = {"name": "Custom", "series": series_list}

    elif args.all:
        for cat_key, cat_info in CATEGORIES.items():
            series_to_download[cat_key] = cat_info

    elif args.category:
        if args.category == "all":
            series_to_download = CATEGORIES
        else:
            series_to_download[args.category] = CATEGORIES[args.category]
    else:
        series_to_download = CATEGORIES

    os.makedirs(args.output_dir, exist_ok=True)

    total_series = sum(len(info["series"]) for info in series_to_download.values())

    log.info(f"Descargando {total_series} series de {len(series_to_download)} categorias...")
    log.info(f"Periodo: {args.start} -> {args.end}")
    log.info(f"Formato: {args.format}")
    log.info(f"Directorio: {args.output_dir}")
    print()

    all_data = {}

    for cat_key, cat_info in series_to_download.items():
        series_list = cat_info["series"]
        cat_name = cat_info["name"]

        log.info(f"[{cat_key}] {cat_name} ({len(series_list)} series)")

        cat_data = {}
        for sid in series_list:
            try:
                s = fetch_fred_series(sid, api_key, args.start, args.end)
                if not s.empty:
                    cat_data[sid] = s
                    log.info(f"  [+] {sid}: {len(s)} obs")
                else:
                    log.warning(f"  [-] {sid}: sin datos")
            except Exception as e:
                log.error(f"  [X] {sid}: {e}")

        if cat_data:
            df = pd.DataFrame(cat_data)
            df = df.sort_index()

            ext = f".{args.format}"
            fname = f"fred_{cat_key}_{args.start}_{args.end}{ext}"
            fname = fname.replace("-", "")
            fpath = os.path.join(args.output_dir, fname)

            if args.format == "csv":
                df.to_csv(fpath)
            else:
                try:
                    df.to_parquet(fpath, compression="zstd")
                except ImportError:
                    csv_fallback = fpath.replace(".parquet", ".csv")
                    log.warning(f"pyarrow/fastparquet no disponible. Guardando como CSV: {csv_fallback}")
                    df.to_csv(csv_fallback)
                    fpath = csv_fallback

            fsize = os.path.getsize(fpath)
            log.info(f"  [*] Guardado: {fpath} ({fsize:,} bytes, {df.shape[0]} filas x {df.shape[1]} cols)")
            print()

            all_data[cat_key] = df

    # Resumen final
    print(f"\n  == Resumen Final ==")
    print(f"  Categorias descargadas: {len(all_data)}")
    print(f"  Series totales: {sum(df.shape[1] for df in all_data.values())}")
    print(f"  Directorio: {args.output_dir}")

    # Combinar todo si hay multiples categorias
    if len(all_data) > 1 and series_to_download:
        combined = []
        for df in all_data.values():
            combined.append(df)
        mega_df = pd.concat(combined, axis=1)
        # Eliminar columnas duplicadas
        mega_df = mega_df.loc[:, ~mega_df.columns.duplicated()]

        ext = f".{args.format}"
        mega_fname = f"fred_all_{args.start}_{args.end}{ext}".replace("-", "")
        mega_path = os.path.join(args.output_dir, mega_fname)

        if args.format == "csv":
            mega_df.to_csv(mega_path)
        else:
            try:
                mega_df.to_parquet(mega_path, compression="zstd")
            except ImportError:
                csv_fallback = mega_path.replace(".parquet", ".csv")
                log.warning(f"pyarrow no disponible. Guardando como CSV: {csv_fallback}")
                mega_df.to_csv(csv_fallback)
                mega_path = csv_fallback

        mega_size = os.path.getsize(mega_path)
        log.info(f"\n  [+] Mega archivo combinado: {mega_path}")
        log.info(f"      {mega_df.shape[0]} filas x {mega_df.shape[1]} columnas, {mega_size:,} bytes")


if __name__ == "__main__":
    main()
