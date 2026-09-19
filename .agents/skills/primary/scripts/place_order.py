#!/usr/bin/env python3
"""
Envía una orden a Primary API (Matba ROFEX).

¡CUIDADO! En ambiente live, esta orden es real y se envía al mercado.

Uso:
    # Orden LIMIT de compra
    python scripts/place_order.py --user USER --password PASS \
        --symbol DLR/JUN26 --side BUY --qty 1 --type LIMIT --price 1450 --account TU_CUENTA

    # Orden MARKET de venta
    python scripts/place_order.py --user USER --password PASS \
        --symbol DLR/JUN26 --side SELL --qty 1 --type MARKET --account TU_CUENTA

    # Orden GTD (Good Till Date)
    python scripts/place_order.py --user USER --password PASS \
        --symbol DLR/JUN26 --side BUY --qty 1 --type LIMIT --price 1450 \
        --account TU_CUENTA --tif GTD --expire 20260720

    # Orden ICEBERG
    python scripts/place_order.py --user USER --password PASS \
        --symbol DLR/JUN26 --side BUY --qty 100 --type LIMIT --price 1450 \
        --account TU_CUENTA --iceberg --display-qty 10
"""

import argparse
import os
import sys
import time

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


def get_order_status(headers, cl_ord_id, proprietary):
    r = requests.get(
        f"{BASE_URL}/rest/order/id",
        headers=headers,
        params={"clOrdId": cl_ord_id, "proprietary": proprietary},
    )
    r.raise_for_status()
    return r.json()


def place_order(headers, symbol, side, qty, ord_type, price, account,
                tif="DAY", cancel_previous=False, iceberg=False,
                display_qty=None, expire_date=None):
    params = {
        "marketId": "ROFX",
        "symbol": symbol,
        "side": side.upper(),
        "orderQty": qty,
        "ordType": ord_type.upper(),
        "timeInForce": tif.upper(),
        "account": account,
        "cancelPrevious": str(cancel_previous).lower(),
        "iceberg": str(iceberg).lower(),
    }
    if price is not None and ord_type.upper() == "LIMIT":
        params["price"] = price
    if display_qty is not None:
        params["displayQty"] = display_qty
    if expire_date is not None:
        params["expireDate"] = expire_date

    r = requests.get(
        f"{BASE_URL}/rest/order/newSingleOrder",
        headers=headers,
        params=params,
    )
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Enviar orden a Primary API")
    parser.add_argument("--user", default=os.getenv("PRIMARY_USER"), help="Usuario (o env PRIMARY_USER)")
    parser.add_argument("--password", default=os.getenv("PRIMARY_PASSWORD"), help="Contraseña (o env PRIMARY_PASSWORD)")
    parser.add_argument("--symbol", required=True, help="Símbolo (ej: DLR/JUN26)")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="BUY o SELL")
    parser.add_argument("--qty", required=True, type=int, help="Cantidad de contratos")
    parser.add_argument("--type", dest="ord_type", required=True, choices=["LIMIT", "MARKET", "STOP_LIMIT", "MARKET_TO_LIMIT", "limit", "market", "stop_limit", "market_to_limit"], help="Tipo de orden")
    parser.add_argument("--price", type=float, help="Precio (requerido para LIMIT)")
    parser.add_argument("--account", default=os.getenv("PRIMARY_ACCOUNT"), help="Cuenta (o env PRIMARY_ACCOUNT)")
    parser.add_argument("--tif", default="DAY", choices=["DAY", "IOC", "FOK", "GTD", "day", "ioc", "fok", "gtd"], help="Time in Force (default: DAY)")
    parser.add_argument("--cancel-previous", action="store_true", help="Cancelar órdenes previas del mismo contrato/lado")
    parser.add_argument("--iceberg", action="store_true", help="Orden iceberg")
    parser.add_argument("--display-qty", type=int, help="Cantidad a divulgar (iceberg)")
    parser.add_argument("--expire-date", help="Fecha expiración GTD (YYYYMMDD)")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar parámetros, no enviar")
    args = parser.parse_args()

    if not args.user or not args.password or not args.account:
        parser.print_help()
        print("\nERROR: Se requieren --user, --password y --account (o env PRIMARY_USER, PRIMARY_PASSWORD, PRIMARY_ACCOUNT)")
        sys.exit(1)

    if args.ord_type.upper() == "LIMIT" and args.price is None:
        print("ERROR: --price es requerido para órdenes LIMIT")
        sys.exit(1)

    print(f"=== ORDEN ===")
    print(f"  Symbol:     {args.symbol}")
    print(f"  Side:       {args.side.upper()}")
    print(f"  Qty:        {args.qty}")
    print(f"  Type:       {args.ord_type.upper()}")
    if args.price:
        print(f"  Price:      {args.price}")
    print(f"  Account:    {args.account}")
    print(f"  TIF:        {args.tif.upper()}")
    print(f"  Iceberg:    {args.iceberg}")
    if args.display_qty:
        print(f"  DisplayQty: {args.display_qty}")
    if args.expire_date:
        print(f"  ExpireDate: {args.expire_date}")

    if args.dry_run:
        print("\nDry-run: orden no enviada.")
        return

    confirm = input(f"\n¿Enviar orden? (s/N): ")
    if confirm.lower() != "s":
        print("Cancelado.")
        return

    token = get_token(args.user, args.password)
    headers = {"X-Auth-Token": token}

    result = place_order(
        headers, args.symbol, args.side, args.qty, args.ord_type,
        args.price, args.account, args.tif, args.cancel_previous,
        args.iceberg, args.display_qty, args.expire_date,
    )

    if result.get("status") == "OK":
        cl_ord_id = result["order"]["clientId"]
        proprietary = result["order"].get("proprietary", "PBCP")
        print(f"\nOrden enviada exitosamente!")
        print(f"  clOrdId:     {cl_ord_id}")
        print(f"  proprietary: {proprietary}")

        print("\nConsultando estado inicial...")
        time.sleep(1)
        status = get_order_status(headers, cl_ord_id, proprietary)
        order = status.get("order", {})
        print(f"  Order ID:   {order.get('orderId', 'N/A')}")
        print(f"  Status:     {order.get('status', 'N/A')}")
        print(f"  Texto:      {order.get('text', 'N/A')}")
        if order.get("status") == "REJECTED":
            print(f"\nADVERTENCIA: La orden fue RECHAZADA: {order.get('text', '')}")
    else:
        print(f"\nError al enviar orden: {result}")


if __name__ == "__main__":
    main()
