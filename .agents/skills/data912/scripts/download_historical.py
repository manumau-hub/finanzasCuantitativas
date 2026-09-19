#!/usr/bin/env python3
"""
Descarga datos históricos del mercado argentino desde data912.com
y los guarda como CSV.

Uso:
    python download_historical.py --type stocks --tickers GGAL,PAMP,YPFD --output data/
    python download_historical.py --type cedears --tickers AAPL,GOOGL --output data/
    python download_historical.py --type bonds --tickers AL30,GD30 --output data/
    python download_historical.py --type all --tickers GGAL,AL30,AAPL --output data/
"""

import argparse
import time
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

BASE_URL = "https://data912.com"
RATE_LIMIT_DELAY = 0.5  # segundos entre requests (para 120 req/min)

ENDPOINTS = {
    "stocks": "/historical/stocks/{ticker}",
    "cedears": "/historical/cedears/{ticker}",
    "bonds": "/historical/bonds/{ticker}",
}


def download_ticker(ticker: str, endpoint_template: str) -> tuple[str, pd.DataFrame | None]:
    """Descarga datos de un ticker específico."""
    url = f"{BASE_URL}{endpoint_template.format(ticker=ticker)}"
    try:
        print(f"Descargando {ticker}...")
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            df = pd.DataFrame(r.json())
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df = df.set_index("date").sort_index()
            return ticker, df
        else:
            print(f"Error {r.status_code} para {ticker}")
            return ticker, None
    except Exception as e:
        print(f"Excepción para {ticker}: {e}")
        return ticker, None


def download_all(tickers: list[str], endpoint_template: str, output_dir: Path, prefix: str):
    """Descarga todos los tickers y guarda CSV combinado + individuales."""
    dfs = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(download_ticker, t, endpoint_template): t 
            for t in tickers
        }
        for future in as_completed(futures):
            ticker, df = future.result()
            if df is not None:
                df_copy = df.copy()
                df_copy["ticker"] = ticker
                dfs.append(df_copy)
                
                # Guardar individual
                out_file = output_dir / f"{prefix}_{ticker}.csv"
                df_copy.reset_index().to_csv(out_file, index=False)
                print(f"  Guardado: {out_file}")
            
            time.sleep(RATE_LIMIT_DELAY)
    
    if dfs:
        combined = pd.concat(dfs)
        combined = combined.reset_index()
        out_file = output_dir / f"{prefix}_all.csv"
        combined.to_csv(out_file, index=False)
        print(f"\nGuardado combinado: {out_file}")


def main():
    parser = argparse.ArgumentParser(description="Descarga datos históricos de data912.com")
    parser.add_argument("--type", required=True, choices=["stocks", "cedears", "bonds", "all"],
                        help="Tipo de activo")
    parser.add_argument("--tickers", required=True, help="Ticker(s) separados por coma (o 'all')")
    parser.add_argument("--output", default=".", help="Directorio de salida")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.type == "all":
        # Descargar todos los tipos para los tickers dados
        for t in ["stocks", "cedears", "bonds"]:
            tickers = [x.strip() for x in args.tickers.split(",")]
            download_all(tickers, ENDPOINTS[t], output_dir, t)
    else:
        tickers = [x.strip() for x in args.tickers.split(",")]
        download_all(tickers, ENDPOINTS[args.type], output_dir, args.type)
    
    print("\n✓ Descarga completada")


if __name__ == "__main__":
    main()
