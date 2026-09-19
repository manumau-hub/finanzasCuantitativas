#!/usr/bin/env python3
"""
Envía y cancela órdenes por WebSocket en Primary API.

Uso:
    python scripts/websocket_send_order.py --user USER --password PASS \
        --symbol DLR/JUN26 --side BUY --qty 1 --price 1450 --account TU_CUENTA

    python scripts/websocket_send_order.py --user USER --password PASS \
        --symbol DLR/JUN26 --side BUY --qty 1 --price 1450 --account TU_CUENTA

    python scripts/websocket_send_order.py --user USER --password PASS \
        --symbol DLR/JUN26 --side SELL --qty 1 --type MARKET --account TU_CUENTA

    python scripts/websocket_send_order.py --user USER --password PASS \
        --symbol DLR/JUN26 --side BUY --qty 1000 --type LIMIT --price 1450 \
        --account TU_CUENTA --all-or-none
"""

import argparse
import json
import os
import sys
import threading
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


class OrderClient:
    def __init__(self, token):
        self.token = token
        self.received = []
        self.done = threading.Event()

    def on_message(self, ws, message):
        data = json.loads(message)
        self.received.append(data)
        msg_type = data.get("type", "")
        if msg_type == "or":
            report = data.get("orderReport", {})
            status = report.get("status", "")
            if status in ("NEW", "REJECTED", "FILLED", "CANCELLED"):
                print(f"\nEstado final: {status}")
                print(json.dumps(data, indent=2))
                self.done.set()
            else:
                print(f"  Estado intermedio: {status} - {report.get('text', '')}")
        elif msg_type == "Md":
            pass
        else:
            print(f"  WS: {json.dumps(data, indent=2)[:200]}")

    def on_error(self, ws, error):
        print(f"WS Error: {error}", file=sys.stderr)
        self.done.set()

    def on_close(self, ws, *args):
        pass

    def on_open(self, ws):
        ws.send(json.dumps(self.msg))
        print(f"Enviado: {json.dumps(self.msg)}")

    def send(self, msg, timeout=15):
        self.msg = msg
        ws = websocket.WebSocketApp(
            WS_URL,
            header=[f"X-Auth-Token: {self.token}"],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        t = threading.Thread(target=ws.run_forever, kwargs={"ping_interval": 30})
        t.daemon = True
        t.start()
        self.done.wait(timeout)
        ws.close()
        return self.received


def main():
    parser = argparse.ArgumentParser(description="Enviar/cancelar órdenes por WebSocket")
    parser.add_argument("--user", default=os.getenv("PRIMARY_USER"))
    parser.add_argument("--password", default=os.getenv("PRIMARY_PASSWORD"))
    parser.add_argument("--account", default=os.getenv("PRIMARY_ACCOUNT"))
    parser.add_argument("--symbol", help="Símbolo del instrumento")
    parser.add_argument("--side", choices=["BUY", "SELL", "buy", "sell"])
    parser.add_argument("--qty", type=int, help="Cantidad de contratos")
    parser.add_argument("--type", dest="ord_type", default="LIMIT", choices=["LIMIT", "MARKET", "limit", "market"])
    parser.add_argument("--price", type=float, help="Precio (requerido para LIMIT)")
    parser.add_argument("--tif", default="DAY", choices=["DAY", "IOC", "FOK", "GTD", "day", "ioc", "fok", "gtd"])
    parser.add_argument("--expire-date", help="Fecha expiración GTD (YYYYMMDD)")
    parser.add_argument("--iceberg", action="store_true", help="Orden iceberg")
    parser.add_argument("--display-qty", type=int, help="Cantidad a divulgar (iceberg)")
    parser.add_argument("--all-or-none", action="store_true", help="Todo o nada (mayorista)")
    parser.add_argument("--ws-clordid", help="ID propio para identificar la orden")
    parser.add_argument("--cancel", action="store_true", help="Modo cancelación")
    parser.add_argument("--clordid", help="clOrdId a cancelar")
    parser.add_argument("--proprietary", default="PBCP", help="Proprietary (default: PBCP)")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar mensaje")
    parser.add_argument("--timeout", type=int, default=15, help="Timeout en segundos")
    args = parser.parse_args()

    if not args.user or not args.password:
        parser.print_help()
        print("\nERROR: Se requieren --user y --password")
        sys.exit(1)

    if args.cancel:
        if not args.clordid:
            print("ERROR: --clordid requerido para cancelar")
            sys.exit(1)
        msg = {"type": "co", "clientId": args.clordid, "proprietary": args.proprietary}
    else:
        if not args.symbol or not args.side or not args.qty or not args.account:
            parser.print_help()
            print("\nERROR: Se requieren --symbol, --side, --qty y --account")
            sys.exit(1)
        if args.ord_type.upper() == "LIMIT" and args.price is None:
            print("ERROR: --price requerido para LIMIT")
            sys.exit(1)

        msg = {
            "type": "no",
            "product": {"marketId": "ROFX", "symbol": args.symbol},
            "quantity": args.qty,
            "side": args.side.upper(),
            "account": args.account,
            "iceberg": args.iceberg,
        }
        if args.price is not None:
            msg["price"] = args.price
        if args.tif.upper() != "DAY":
            msg["timeInForce"] = args.tif.upper()
        if args.expire_date:
            msg["expireDate"] = args.expire_date
        if args.display_qty is not None:
            msg["displayQuantity"] = args.display_qty
        if args.all_or_none:
            msg["allOrNone"] = True
        if args.ws_clordid:
            msg["wsClOrdId"] = args.ws_clordid

    print(f"Mensaje a enviar:\n{json.dumps(msg, indent=2)}")
    if args.dry_run:
        return

    token = get_token(args.user, args.password)
    client = OrderClient(token)
    received = client.send(msg, timeout=args.timeout)

    if not received:
        print("No se recibió respuesta.")
    elif args.cancel:
        print(f"\nCancelación enviada. Responses: {len(received)}")


if __name__ == "__main__":
    main()
