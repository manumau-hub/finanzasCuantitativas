#!/usr/bin/env python3
"""
Descarga quotes de múltiples símbolos desde Alpha Vantage.
Maneja rate limits automáticamente.

Uso:
    python download_quotes.py --symbols AAPL,GOOGL,MSFT --output data/
    python download_quotes.py --symbols AAPL --apikey TU_KEY --output data/
"""

import argparse
import time
import os
import pandas as pd
from pathlib import Path
import requests

BASE_URL = "https://www.alphavantage.co/query"
RATE_LIMIT_DELAY = 12  # segundos entre requests (5 req/min free tier)


def get_quote(symbol: str, api_key: str) -> dict | None:
    """Obtiene quote de un símbolo."""
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": api_key
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=30)
        data = r.json()
        
        if "Note" in data:  # Rate limit
            print(f"⚠️ Rate limit alcanzado. Esperando...")
            return None
        if "Error Message" in data:
            print(f"❌ Error para {symbol}: {data['Error Message']}")
            return None
            
        return data.get("Global Quote", {})
    except Exception as e:
        print(f"❌ Excepción para {symbol}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Descarga quotes desde Alpha Vantage")
    parser.add_argument("--symbols", required=True, help="Símbolos separados por coma")
    parser.add_argument("--output", default=".", help="Directorio de salida")
    parser.add_argument("--apikey", default=os.getenv("ALPHAVANTAGE_API_KEY"),
                        help="API Key (o ALPHAVANTAGE_API_KEY env var)")
    args = parser.parse_args()
    
    if not args.apikey:
        print("❌ Error: Se requiere API key. Usá --apikey o ALPHAVANTAGE_API_KEY")
        return
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    symbols = [s.strip() for s in args.symbols.split(",")]
    quotes = []
    
    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{len(symbols)}] Obteniendo {symbol}...")
        quote = get_quote(symbol, args.apikey)
        
        if quote:
            quotes.append({"symbol": symbol, **quote})
            print(f"  ✓ {symbol}: ${quote.get('05. price', 'N/A')}")
        else:
            print(f"  ⚠️ Saltando {symbol} por rate limit")
        
        # Rate limit: 5 requests por minuto
        if i < len(symbols) - 1:
            print(f"  ⏳ Esperando {RATE_LIMIT_DELAY}s...")
            time.sleep(RATE_LIMIT_DELAY)
    
    if quotes:
        df = pd.DataFrame(quotes)
        out_file = output_dir / "quotes.csv"
        df.to_csv(out_file, index=False)
        print(f"\n✓ Guardado: {out_file}")
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
