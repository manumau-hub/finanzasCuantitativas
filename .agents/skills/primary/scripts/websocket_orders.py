#!/usr/bin/env python3
"""
WebSocket de Primary API: Execution Reports en tiempo real.

Uso:
    python scripts/websocket_orders.py --user USER --password PASS
    python scripts/websocket_orders.py --user USER --password PASS --account TU_CUENTA
    python scripts/websocket_orders.py --user USER --password PASS --accounts TU_CUENTA1,TU_CUENTA2
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
    if data.get("type") == "or":
        report = data.get("orderReport", {})
        inst = report.get("instrumentId", {})
        symbol = inst.get("symbol", "?")
        status = report.get("status", "?")
        text = report.get("text", "")
        side = report.get("side", "?")
        qty = report.get("orderQty", "?")
        price = report.get("price", "?")
        cl_ord_id = report.get("clOrdId", "?")
        order_id = report.get("orderId", "?")
        print(f"\n[{time.strftime('%H:%M:%S')}] {symbol}")
        print(f"  OrderID: {order_id}  |  clOrdId: {cl_ord_id}")
        print(f"  Status: {status}  |  Side: {side}  |  Qty: {qty}  |  Price: {price}")
        print(f"  Text: {text}")
    else:
        print(f"\n[WS] {json.dumps(data, indent=2)}")


def on_error(ws, error):
    print(f"WS Error: {error}", file=sys.stderr)


def on_close(ws, close_status_code, close_msg):
    print(f"WS Cerrado: {close_status_code} {close_msg}")


def on_open(ws):
    print("WS Conectado. Suscribiendo a execution reports...")
    if ws.accounts:
        if len(ws.accounts) == 1:
            subscribe_msg = {"type": "os", "account": {"id": ws.accounts[0]}}
            print(f"Cuenta: {ws.accounts[0]}")
        else:
            subscribe_msg = {"type": "os", "accounts": [{"id": a} for a in ws.accounts]}
            print(f"Cuentas: {', '.join(ws.accounts)}")
    else:
        subscribe_msg = {"type": "os"}
        print("Todas las cuentas")
    if getattr(ws, 'snapshot_only_active', False):
        subscribe_msg["snapshotOnlyActive"] = True
        print("Modo: solo órdenes activas")
    ws.send(json.dumps(subscribe_msg))
    print("Esperando execution reports... (Ctrl+C para salir)")


def main():
    parser = argparse.ArgumentParser(description="WebSocket Execution Reports de Primary API")
    parser.add_argument("--user", default=os.getenv("PRIMARY_USER"), help="Usuario (o env PRIMARY_USER)")
    parser.add_argument("--password", default=os.getenv("PRIMARY_PASSWORD"), help="Contraseña (o env PRIMARY_PASSWORD)")
    parser.add_argument("--account", default=os.getenv("PRIMARY_ACCOUNT"), help="Cuenta única")
    parser.add_argument("--accounts", help="Cuentas separadas por coma")
    parser.add_argument("--snapshot-only-active", action="store_true", help="Solo órdenes activas")
    parser.add_argument("--timeout", type=int, default=0, help="Tiempo en segundos (0 = infinito)")
    args = parser.parse_args()

    if not args.user or not args.password:
        parser.print_help()
        print("\nERROR: Se requieren --user y --password (o env PRIMARY_USER, PRIMARY_PASSWORD)")
        sys.exit(1)

    token = get_token(args.user, args.password)

    accounts = []
    if args.accounts:
        accounts = [a.strip() for a in args.accounts.split(",")]
    elif args.account:
        accounts = [args.account]

    ws = websocket.WebSocketApp(
        WS_URL,
        header=[f"X-Auth-Token: {token}"],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.accounts = accounts
    ws.snapshot_only_active = args.snapshot_only_active

    print(f"Conectando a {WS_URL}...")
    ws.run_forever()


if __name__ == "__main__":
    main()
