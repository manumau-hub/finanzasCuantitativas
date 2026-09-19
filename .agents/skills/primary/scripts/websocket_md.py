#!/usr/bin/env python3
"""
WebSocket de Primary API: Market Data en tiempo real.

Uso:
    python scripts/websocket_md.py --user USER --password PASS --symbols DLR/JUN26,SOJ.ROS/MAY26
    python scripts/websocket_md.py --user USER --password PASS --symbols DLR/JUN26 --entries BI,OF,LA --depth 3
"""

import argparse
import json
import os
import sys
import time

import requests
import websocket

BASE_URL = "https://api.remarkets.primary.com.ar"
WS_URL = "wss://api.remarkets.primary.com.ar/"


def get_token(user, password):
    r = requests.post(
        f"{BASE_URL}/auth/getToken",
        headers={"X-Username": user, "X-Password": password},
    )
    if r.status_code != 200:
        print(f"Error de autenticación: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.headers["X-Auth-Token"]


def on_message(ws, message):
    data = json.loads(message)
    if data.get("type") == "Md":
        inst = data.get("instrumentId", {})
        symbol = inst.get("symbol", "?")
        md = data.get("marketData", {})
        print(f"\n[{time.strftime('%H:%M:%S')}] {symbol}")
        for entry, value in md.items():
            if isinstance(value, list):
                for level in value:
                    print(f"  {entry}: price={level.get('price')} size={level.get('size')}")
            elif isinstance(value, dict):
                print(f"  {entry}: price={value.get('price')} size={value.get('size')}")
            else:
                print(f"  {entry}: {value}")
    elif data.get("type") == "or":
        print(f"\n[Execution Report] {json.dumps(data, indent=2)}")
    else:
        print(f"\n[WS] {json.dumps(data, indent=2)}")


def on_error(ws, error):
    print(f"WS Error: {error}", file=sys.stderr)


def on_close(ws, close_status_code, close_msg):
    print(f"WS Cerrado: {close_status_code} {close_msg}")


def on_open(ws):
    print("WS Conectado. Enviando suscripción...")
    subscribe_msg = {
        "type": "smd",
        "level": 1,
        "entries": ws.entries,
        "products": [{"symbol": s, "marketId": "ROFX"} for s in ws.symbols],
        "depth": ws.depth,
    }
    ws.send(json.dumps(subscribe_msg))
    print(f"Suscrito a: {', '.join(ws.symbols)}")
    print(f"Entries: {', '.join(ws.entries)}  |  Depth: {ws.depth}")
    print("Esperando datos... (Ctrl+C para salir)")


def main():
    parser = argparse.ArgumentParser(description="WebSocket Market Data de Primary API")
    parser.add_argument("--user", default=os.getenv("PRIMARY_USER"), help="Usuario (o env PRIMARY_USER)")
    parser.add_argument("--password", default=os.getenv("PRIMARY_PASSWORD"), help="Contraseña (o env PRIMARY_PASSWORD)")
    parser.add_argument("--symbols", default="DLR/JUN26", help="Símbolos separados por coma")
    parser.add_argument("--entries", default="BI,OF,LA", help="Entries separados por coma")
    parser.add_argument("--depth", type=int, default=1, help="Profundidad del book")
    parser.add_argument("--timeout", type=int, default=0, help="Tiempo en segundos (0 = infinito)")
    args = parser.parse_args()

    if not args.user or not args.password:
        parser.print_help()
        print("\nERROR: Se requieren --user y --password (o env PRIMARY_USER, PRIMARY_PASSWORD)")
        sys.exit(1)

    token = get_token(args.user, args.password)
    symbols = [s.strip() for s in args.symbols.split(",")]
    entries = [e.strip() for e in args.entries.split(",")]

    ws = websocket.WebSocketApp(
        WS_URL,
        header=[f"X-Auth-Token: {token}"],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.symbols = symbols
    ws.entries = entries
    ws.depth = args.depth

    print(f"Conectando a {WS_URL}...")
    ws.run_forever()


if __name__ == "__main__":
    main()
