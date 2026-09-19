#!/usr/bin/env python3
"""
Descarga historical crypto bars desde Alpaca Data API.
NO requiere API keys.

Uso:
    python download_crypto_bars.py --symbols BTC/USD,ETH/USD --days 90 --output data/
    python download_crypto_bars.py --symbols BTC/USD --timeframe 1H --days 30 --output data/
"""

import argparse
import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import requests

DATA_URL = "https://data.alpaca.markets/v2/stocks/crypto/bars"

MIN_REQUEST_INTERVAL = 0.5


def download_crypto_bars(symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
    """Descarga crypto bars con paginación."""
    all_bars = []
    page_token = None
    
    while True:
        params = {
            "symbols": symbol,
            "timeframe": timeframe,
            "start": start,
            "end": end,
            "limit": 10000
        }
        if page_token:
            params["page_token"] = page_token
        
        print(f"  Descargando {symbol} (page: {page_token[:20] if page_token else 'None'}...)")
        
        r = requests.get(DATA_URL, params=params, timeout=60)
        
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
        
        page_token = data.get("next_page_token")
        if not page_token:
            break
        
        time.sleep(MIN_REQUEST_INTERVAL)
    
    return pd.DataFrame(all_bars)


def main():
    parser = argparse.ArgumentParser(description="Descarga crypto bars desde Alpaca")
    parser.add_argument("--symbols", required=True, help="Símbolos separados por coma (ej: BTC/USD,ETH/USD)")
    parser.add_argument("--days", type=int, default=90, help="Días de historia")
    parser.add_argument("--timeframe", default="1Day", 
                        help="Timeframe: 1Min, 5Min, 15Min, 1Hour, 1Day, 1Week")
    parser.add_argument("--start", default=None, help="Fecha inicio (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="Fecha fin (YYYY-MM-DD)")
    parser.add_argument("--output", default=".", help="Directorio de salida")
    args = parser.parse_args()
    
    end_date = args.end or datetime.now().strftime("%Y-%m-%d")
    start_date = args.start or (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    symbols = [s.strip() for s in args.symbols.split(",")]
    
    print(f"Descargando {args.timeframe} crypto bars para {len(symbols)} símbolos")
    print(f"Periodo: {start_date} a {end_date}")
    print()
    
    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{len(symbols)}] {symbol}")
        
        df = download_crypto_bars(symbol, args.timeframe, start_date, end_date)
        
        if df is not None and len(df) > 0:
            df["timestamp"] = pd.to_datetime(df["t"])
            df = df.set_index("timestamp").sort_index()
            
            safe_name = symbol.replace("/", "_")
            out_file = output_dir / f"{safe_name}_{args.timeframe}.csv"
            df.to_csv(out_file)
            print(f"  ✓ {len(df)} bars guardados: {out_file}")
        else:
            print(f"  ⚠️ Sin datos")
        
        if i < len(symbols) - 1:
            time.sleep(MIN_REQUEST_INTERVAL)
    
    print(f"\n✓ Completado")


if __name__ == "__main__":
    main()
