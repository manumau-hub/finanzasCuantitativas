#!/usr/bin/env python3
"""
Descarga option contracts desde Alpaca Data API.

Uso:
    python download_options.py --symbol AAPL --output data/
    python download_options.py --symbol AAPL --exp-days 90 --output data/
    python download_options.py --symbol AAPL --strike-min 100 --strike-max 200 --output data/
"""

import argparse
import os
import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import requests

CONTRACTS_URL = "https://data.alpaca.markets/v2/options/contracts"
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


def download_option_contracts(symbol: str, 
                              exp_min: str = None,
                              exp_max: str = None,
                              strike_min: float = None,
                              strike_max: float = None,
                              option_type: str = None) -> pd.DataFrame:
    """Descarga contracts de opciones para un símbolo."""
    
    params = {
        "underlying_symbols": symbol,
        "limit": 1000
    }
    
    if exp_min:
        params["expiration_date_gte"] = exp_min
    if exp_max:
        params["expiration_date_lte"] = exp_max
    if strike_min is not None:
        params["strike_price_gte"] = strike_min
    if strike_max is not None:
        params["strike_price_lte"] = strike_max
    if option_type:
        params["type"] = option_type
    
    print(f"  Descargando contracts para {symbol}...")
    
    r = requests.get(CONTRACTS_URL, headers=get_headers(), params=params, timeout=60)
    
    if r.status_code == 429:
        print(f"  ⚠️ Rate limit. Esperando 60s...")
        time.sleep(60)
        r = requests.get(CONTRACTS_URL, headers=get_headers(), params=params, timeout=60)
    
    if r.status_code != 200:
        print(f"  ❌ Error {r.status_code}: {r.text[:200]}")
        return None
    
    data = r.json()
    contracts = data.get("option_contracts", [])
    
    if not contracts:
        print(f"  ⚠️ No se encontraron contracts")
        return None
    
    # Parsear contratos
    df = pd.DataFrame([{
        "id": c.get("id"),
        "symbol": c.get("symbol"),
        "underlying": c.get("underlying_symbol"),
        "expiration": c.get("expiration_date"),
        "type": c.get("type"),  # call o put
        "style": c.get("style"),  # american o european
        "strike": float(c.get("strike_price", 0)),
        "size": int(c.get("size", 100)),
        "open_interest": int(c.get("open_interest") or 0),
        "close_price": float(c.get("close_price") or 0),
        "close_price_date": c.get("close_price_date"),
        "status": c.get("status"),
        "tradable": c.get("tradable"),
        "root_symbol": c.get("root_symbol"),
    } for c in contracts])
    
    df["expiration"] = pd.to_datetime(df["expiration"])
    df = df.sort_values(["expiration", "strike", "type"])
    
    return df


def main():
    parser = argparse.ArgumentParser(description="Descarga option contracts desde Alpaca")
    parser.add_argument("--symbol", required=True, help="Símbolo subyacente (ej: AAPL)")
    parser.add_argument("--exp-days", type=int, default=90, 
                        help="Días hacia adelante para buscar expiraciones")
    parser.add_argument("--strike-min", type=float, help="Strike mínimo")
    parser.add_argument("--strike-max", type=float, help="Strike máximo")
    parser.add_argument("--type", choices=["call", "put"], help="Tipo de opción")
    parser.add_argument("--output", default=".", help="Directorio de salida")
    args = parser.parse_args()
    
    # Calcular fechas de expiración
    exp_min = datetime.now().strftime("%Y-%m-%d")
    exp_max = (datetime.now() + timedelta(days=args.exp_days)).strftime("%Y-%m-%d")
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Buscando options para {args.symbol}")
    print(f"Expiraciones: {exp_min} a {exp_max}")
    if args.strike_min:
        print(f"Strikes: ${args.strike_min} a ${args.strike_max}")
    print()
    
    df = download_option_contracts(
        args.symbol,
        exp_min=exp_min,
        exp_max=exp_max,
        strike_min=args.strike_min,
        strike_max=args.strike_max,
        option_type=args.type
    )
    
    if df is not None and len(df) > 0:
        out_file = output_dir / f"{args.symbol}_options.csv"
        df.to_csv(out_file, index=False)
        print(f"\n✓ {len(df)} contracts guardados: {out_file}")
        
        # Resumen
        print(f"\nResumen:")
        print(f"  Calls: {len(df[df['type']=='call'])}")
        print(f"  Puts: {len(df[df['type']=='put'])}")
        print(f"  Expiraciones: {df['expiration'].nunique()}")
        print(f"  Rango strikes: ${df['strike'].min():.2f} - ${df['strike'].max():.2f}")
        
        # Muestra
        print(f"\nPrimeras 5 calls:")
        print(df[df['type']=='call'].head().to_string(index=False))
    else:
        print("\n⚠️ No se encontraron opciones")


if __name__ == "__main__":
    main()
