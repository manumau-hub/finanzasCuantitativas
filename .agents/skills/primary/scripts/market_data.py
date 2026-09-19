#!/usr/bin/env python3
"""
Market data de Primary API: snapshot en tiempo real y trades históricos.

Uso:
    python scripts/market_data.py --user USER --password PASS --symbol DLR/JUN26
    python scripts/market_data.py --user USER --password PASS --symbol DLR/JUN26 --entries BI,OF,LA
    python scripts/market_data.py --user USER --password PASS --symbol DLR/JUN26 --historical --date 2026-06-05
"""

import argparse
import json
import os
import sys

import requests

BASE_URL = "https://api.remarkets.primary.com.ar"


def get_token(user, password):
    r = requests.post(
        f"{BASE_URL}/auth/getToken",
        headers={"X-Username": user, "X-Password": password},
    )
    if r.status_code != 200:
        print(f"Error de autenticación: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.headers["X-Auth-Token"]


MD_ENTRIES = {
    "BI": "Bids (ofertas de compra)",
    "OF": "Offers (ofertas de venta)",
    "LA": "Last (último precio operado)",
    "OP": "Opening Price (apertura)",
    "CL": "Closing Price (cierre anterior)",
    "SE": "Settlement (ajuste, solo futuros)",
    "HI": "High Price (máximo rueda)",
    "LO": "Low Price (mínimo rueda)",
    "TV": "Trade Volume (volumen contratos)",
    "OI": "Open Interest (interés abierto)",
    "IV": "Index Value (solo índices)",
    "EV": "Effective Volume (solo BYMA)",
    "NV": "Nominal Volume (solo BYMA)",
    "ACP": "Auction Price (cierre corriente)",
}


def market_data_snapshot(headers, symbol, entries="BI,OF,LA,OP,CL,SE,OI", depth=1):
    r = requests.get(
        f"{BASE_URL}/rest/marketdata/get",
        headers=headers,
        params={
            "marketId": "ROFX",
            "symbol": symbol,
            "entries": entries,
            "depth": depth,
        },
    )
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        print(f"Error: {data}", file=sys.stderr)
        return
    md = data.get("marketData", {})
    depth_returned = data.get("depth", 1)
    print(f"\nMarket Data: {symbol}  (depth={depth_returned})")
    print("=" * 60)
    for entry_name, entry_val in md.items():
        label = MD_ENTRIES.get(entry_name, entry_name)
        if entry_val is None:
            print(f"  {entry_name:<4} {label:<40}: —")
        elif isinstance(entry_val, list):
            print(f"  {entry_name:<4} {label:<40}:")
            for level in entry_val:
                print(f"         price={level.get('price', '?')}  size={level.get('size', '?')}")
        elif isinstance(entry_val, dict):
            px = entry_val.get("price")
            sz = entry_val.get("size")
            dt = entry_val.get("date")
            print(f"  {entry_name:<4} {label:<40}: price={px}  size={sz}  date={dt}")
        else:
            print(f"  {entry_name:<4} {label:<40}: {entry_val}")


def historical_trades(headers, symbol, date_from=None, date_to=None, date=None,
                      external=False, environment="REMARKETS"):
    params = {"marketId": "ROFX", "symbol": symbol, "environment": environment}
    if date:
        params["date"] = date
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    if external:
        params["external"] = "true"
    r = requests.get(
        f"{BASE_URL}/rest/data/getTrades",
        headers=headers,
        params=params,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        print(f"Error: {data}", file=sys.stderr)
        return
    trades = data.get("trades", [])
    if not trades:
        print("No hay trades para el período solicitado.")
        return
    print(f"\nTrades históricos: {symbol}  ({len(trades)} operaciones)")
    print("=" * 70)
    print(f"{'Fecha/Hora':<26} {'Precio':<10} {'Cantidad':<10}")
    print("-" * 70)
    for t in trades:
        print(f"{t['datetime']:<26} {t['price']:<10} {t['size']:<10}")
    if trades:
        prices = [t["price"] for t in trades]
        print("-" * 70)
        print(f"  Apertura: {prices[0]}  |  Cierre: {prices[-1]}")
        print(f"  Máximo: {max(prices)}  |  Mínimo: {min(prices)}")
        print(f"  Total operado: {sum(t['size'] for t in trades)} contratos")


def main():
    parser = argparse.ArgumentParser(description="Market data de Primary API")
    parser.add_argument("--user", default=os.getenv("PRIMARY_USER"), help="Usuario (o env PRIMARY_USER)")
    parser.add_argument("--password", default=os.getenv("PRIMARY_PASSWORD"), help="Contraseña (o env PRIMARY_PASSWORD)")
    parser.add_argument("--symbol", default="DLR/JUN26", help="Símbolo del instrumento (default: DLR/JUN26)")
    parser.add_argument("--entries", default="BI,OF,LA,OP,CL,SE,OI", help="Entries de MD (default: todas)")
    parser.add_argument("--depth", type=int, default=1, help="Profundidad del book (default: 1)")
    parser.add_argument("--historical", action="store_true", help="Modo histórico (trades)")
    parser.add_argument("--date", help="Fecha específica (YYYY-MM-DD)")
    parser.add_argument("--date-from", help="Fecha desde (YYYY-MM-DD)")
    parser.add_argument("--date-to", help="Fecha hasta (YYYY-MM-DD)")
    parser.add_argument("--external", action="store_true", help="Instrumento de mercado externo a Matba Rofex")
    parser.add_argument("--environment", default="REMARKETS", help="Entorno (default: REMARKETS)")
    parser.add_argument("--list-entries", action="store_true", help="Listar entries disponibles y salir")
    args = parser.parse_args()

    if args.list_entries:
        print("Entries disponibles para market data:")
        for code, desc in MD_ENTRIES.items():
            print(f"  {code:<4} - {desc}")
        return

    if not args.user or not args.password:
        parser.print_help()
        print("\nERROR: Se requieren --user y --password (o env PRIMARY_USER, PRIMARY_PASSWORD)")
        sys.exit(1)

    token = get_token(args.user, args.password)
    headers = {"X-Auth-Token": token}

    if args.historical:
        historical_trades(headers, args.symbol, args.date_from, args.date_to, args.date,
                          external=args.external, environment=args.environment)
    else:
        market_data_snapshot(headers, args.symbol, args.entries, args.depth)


if __name__ == "__main__":
    main()
