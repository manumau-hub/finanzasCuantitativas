#!/usr/bin/env python3
"""
Descarga historical stock bars desde Alpaca Data API.
Maneja paginación automáticamente.

Uso:
    python download_stock_bars.py --symbols AAPL,GOOGL,MSFT --days 365 --output data/
    python download_stock_bars.py --symbols AAPL --timeframe 1H --days 30 --output data/
"""

import argparse
import os
import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import requests

# Base URLs
DATA_URL = "https://data.alpaca.markets/v2/stocks/bars"

# Rate limit: 200 req/min free tier = 1 request cada 0.3s mínimo
MIN_REQUEST_INTERVAL = 0.5


def get_headers():
    """Obtiene headers de autenticación."""
    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")
    
    if not api_key or not secret_key:
        raise ValueError("Se requieren APCA_API_KEY_ID y APCA_API_SECRET_KEY")
    
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key
    }


def download_bars(symbol: str, timeframe: str, start: str, end: str, 
                 feed: str = "iex") -> pd.DataFrame:
    """Descarga bars para un símbolo con paginación."""
    all_bars = []
    page_token = None
    
    while True:
        params = {
            "symbols": symbol,
            "timeframe": timeframe,
            "start": start,
            "end": end,
            "limit": 10000,
            "feed": feed
        }
        if page_token:
            params["page_token"] = page_token
        
        print(f"  Descargando {symbol} (page token: {page_token[:20] if page_token else 'None'}...)")
        
        r = requests.get(DATA_URL, headers=get_headers(), params=params, timeout=60)
        
        if r.status_code == 429:
            print(f"  ⚠️ Rate limit. Esperando 60s...")
            time.sleep(60)
            continue
        elif r.status_code != 200:
            print(f"  ❌ Error {r.status_code}: {r.text[:200]}")
            break
        
        data = r.json()
        bars = data.get("bars", {}).get(symbol, [])
        
        if not bars:
            break
        
        all_bars.extend(bars)
        
        # Siguiente página
        page_token = data.get("next_page_token")
        if not page_token:
            break
        
        time.sleep(MIN_REQUEST_INTERVAL)
    
    return pd.DataFrame(all_bars)


def main():
    parser = argparse.ArgumentParser(description="Descarga stock bars desde Alpaca")
    parser.add_argument("--symbols", required=True, help="Símbolos separados por coma")
    parser.add_argument("--days", type=int, default=365, help="Días de historia")
    parser.add_argument("--timeframe", default="1Day", 
                        help="Timeframe: 1Min, 5Min, 15Min, 1Hour, 1Day, 1Week")
    parser.add_argument("--start", default=None, help="Fecha inicio (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="Fecha fin (YYYY-MM-DD)")
    parser.add_argument("--feed", default="iex", choices=["iex", "sip", "boats"],
                        help="Feed de datos (iex=free, sip/boats=paid)")
    parser.add_argument("--output", default=".", help="Directorio de salida")
    args = parser.parse_args()
    
    # Calcular fechas si no se especifican
    end_date = args.end or datetime.now().strftime("%Y-%m-%d")
    start_date = args.start or (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    symbols = [s.strip() for s in args.symbols.split(",")]
    
    print(f"Descargando {args.timeframe} bars para {len(symbols)} símbolos")
    print(f"Periodo: {start_date} a {end_date}")
    print(f"Feed: {args.feed}")
    print()
    
    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{len(symbols)}] {symbol}")
        
        df = download_bars(symbol, args.timeframe, start_date, end_date, args.feed)
        
        if df is not None and len(df) > 0:
            df["timestamp"] = pd.to_datetime(df["t"])
            df = df.set_index("timestamp").sort_index()
            
            out_file = output_dir / f"{symbol}_{args.timeframe}.csv"
            df.to_csv(out_file)
            print(f"  ✓ {len(df)} bars guardados: {out_file}")
        else:
            print(f"  ⚠️ Sin datos")
        
        if i < len(symbols) - 1:
            time.sleep(MIN_REQUEST_INTERVAL)
    
    print(f"\n✓ Completado")


if __name__ == "__main__":
    main()
