#!/usr/bin/env python3
"""
Descarga time series desde Alpha Vantage.
Maneja rate limits automáticamente.

Uso:
    python download_timeseries.py --symbol AAPL --output data/
    python download_timeseries.py --symbol IBM --interval weekly --output data/
"""

import argparse
import time
import os
import pandas as pd
from pathlib import Path
import requests

BASE_URL = "https://www.alphavantage.co/query"
RATE_LIMIT_DELAY = 12  # segundos entre requests


def download_timeseries(symbol: str, api_key: str, 
                        function: str = "TIME_SERIES_DAILY",
                        interval: str = None,
                        outputsize: str = "compact") -> pd.DataFrame | None:
    """Descarga time series para un símbolo."""
    params = {
        "function": function,
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": api_key
    }
    
    if interval:
        params["interval"] = interval
    
    try:
        print(f"Descargando {symbol} ({function})...")
        r = requests.get(BASE_URL, params=params, timeout=60)
        data = r.json()
        
        if "Note" in data:
            print(f"⚠️ Rate limit. Esperando {RATE_LIMIT_DELAY}s...")
            time.sleep(RATE_LIMIT_DELAY)
            return None
            
        if "Error Message" in data:
            print(f"❌ Error: {data['Error Message']}")
            return None
        
        # Parsear respuesta según tipo de función
        time_key = None
        for key in data.keys():
            if "Time Series" in key or "Series" in key:
                time_key = key
                break
        
        if not time_key:
            print(f"❌ No se encontró time series en respuesta")
            return None
        
        records = []
        for date, values in data[time_key].items():
            row = {"date": date, "symbol": symbol}
            row.update(values)
            records.append(row)
        
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
        print(f"  ✓ {len(df)} registros")
        return df
        
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Descarga time series desde Alpha Vantage")
    parser.add_argument("--symbol", required=True, help="Símbolo (ej: AAPL)")
    parser.add_argument("--output", default=".", help="Directorio de salida")
    parser.add_argument("--function", default="TIME_SERIES_DAILY",
                        choices=["TIME_SERIES_DAILY", "TIME_SERIES_WEEKLY", 
                                 "TIME_SERIES_MONTHLY", "TIME_SERIES_INTRADAY"])
    parser.add_argument("--interval", default=None,
                        help="Intervalo para INTRADAY (1min, 5min, 15min, 30min, 60min)")
    parser.add_argument("--outputsize", default="compact",
                        help="compact (100 datos) o full (historia completa, premium)")
    parser.add_argument("--apikey", default=os.getenv("ALPHAVANTAGE_API_KEY"),
                        help="API Key")
    args = parser.parse_args()
    
    if not args.apikey:
        print("❌ Error: Se requiere API key")
        return
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = download_timeseries(
        args.symbol, args.apikey, 
        function=args.function,
        interval=args.interval,
        outputsize=args.outputsize
    )
    
    if df is not None:
        out_file = output_dir / f"{args.symbol}_{args.function.lower()}.csv"
        df.to_csv(out_file, index=False)
        print(f"\n✓ Guardado: {out_file}")
        print(df.tail(5).to_string(index=False))


if __name__ == "__main__":
    main()
