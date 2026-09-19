#!/usr/bin/env python3
"""
Posiciones de Primary API (Risk API): resumen y detalle.

Uso:
    python scripts/check_positions.py --user USER --password PASS --account TU_CUENTA
    python scripts/check_positions.py --user USER --password PASS --account TU_CUENTA --detail
"""

import argparse
import base64
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


def make_headers(token, user=None, password=None, basic_auth=False):
    headers = {"X-Auth-Token": token}
    if basic_auth and user and password:
        auth = base64.b64encode(f"{user}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {auth}"
    return headers


def format_float(val):
    if val is None:
        return 0.0
    return float(val)


def get_positions(headers, account):
    r = requests.get(
        f"{BASE_URL}/rest/risk/position/getPositions/{account}",
        headers=headers,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        print(f"Error: {data.get('description', data)}", file=sys.stderr)
        return None
    return data.get("positions", [])


def get_detailed_positions(headers, account):
    r = requests.get(
        f"{BASE_URL}/rest/risk/detailedPosition/{account}",
        headers=headers,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        print(f"Error: {data.get('description', data)}", file=sys.stderr)
        return None
    return data.get("detailedPosition", {})


def show_summary(positions):
    if not positions:
        print("No hay posiciones abiertas.")
        return
    print(f"{'Instrumento':<35} {'Compra':<8} {'P.Compra':<12} {'Venta':<8} {'P.Venta':<12} {'Diff Diario':<14} {'Diff Total':<14}")
    print("-" * 105)
    total_buy = total_sell = total_diff = 0
    for p in positions:
        sym = p.get("symbol", "?")
        buy_size = p.get("buySize", 0)
        buy_price = format_float(p.get("buyPrice", 0))
        sell_size = p.get("sellSize", 0)
        sell_price = format_float(p.get("sellPrice", 0))
        daily_diff = format_float(p.get("totalDailyDiff", 0))
        total_diff_pos = format_float(p.get("totalDiff", 0))
        total_buy += buy_size
        total_sell += sell_size
        total_diff += total_diff_pos
        print(f"{sym:<35} {buy_size:<8} {buy_price:<12.4f} {sell_size:<8} {sell_price:<12.4f} {daily_diff:<14.2f} {total_diff_pos:<14.2f}")
    print("-" * 105)
    print(f"{'TOTAL':<35} {total_buy:<8} {'':<12} {total_sell:<8} {'':<12} {'':<14} {total_diff:<14.2f}")


def show_detail(dp):
    if not dp:
        return
    print(f"\n=== POSICIONES DETALLADAS ===")
    print(f"Cuenta: {dp.get('account', '?')}")
    print(f"Daily Diff Plain: {dp.get('totalDailyDiffPlain', 0)}")
    print(f"Market Value: {dp.get('totalMarketValue', 0)}")
    report = dp.get("report", {})
    if not report:
        print("  No hay detalle de posiciones.")
        return
    for contract_type, instruments in report.items():
        print(f"\n--- {contract_type} ---")
        for symbol, info in instruments.items():
            print(f"\n  {symbol}:")
            print(f"    Initial: {info.get('instrumentInitialSize', 0)}  |  Current: {info.get('instrumentCurrentSize', 0)}  |  Filled: {info.get('instrumentFilledSize', 0)}")
            dets = info.get("detailedPositions", [])
            for det in dets:
                print(f"      Market Price: {det.get('marketPrice', '?')}")
                print(f"      Currency: {det.get('currency', '?')}  |  Rate: {det.get('exchangeRate', '?')}")
                print(f"      Buy: {det.get('buyCurrentSize', 0)} @ {det.get('buyInitialPrice', '?')}")
                print(f"      Sell: {det.get('sellCurrentSize', 0)} @ {det.get('sellInitialPrice', '?')}")
                dd = det.get("detailedDailyDiff", {})
                if dd:
                    print(f"      Daily Diff: {dd.get('totalDailyDiff', 0)}  |  Plain: {dd.get('totalDailyDiffPlain', 0)}")


def main():
    parser = argparse.ArgumentParser(description="Posiciones de Primary API")
    parser.add_argument("--user", default=os.getenv("PRIMARY_USER"), help="Usuario (o env PRIMARY_USER)")
    parser.add_argument("--password", default=os.getenv("PRIMARY_PASSWORD"), help="Contraseña (o env PRIMARY_PASSWORD)")
    parser.add_argument("--account", default=os.getenv("PRIMARY_ACCOUNT"), help="Cuenta (o env PRIMARY_ACCOUNT)")
    parser.add_argument("--detail", action="store_true", help="Mostrar posiciones detalladas")
    parser.add_argument("--basic-auth", action="store_true", help="Usar HTTP Basic Auth (requerido en LIVE)")
    args = parser.parse_args()

    if not args.user or not args.password or not args.account:
        parser.print_help()
        print("\nERROR: Se requieren --user, --password y --account (o env PRIMARY_USER, PRIMARY_PASSWORD, PRIMARY_ACCOUNT)")
        sys.exit(1)

    token = get_token(args.user, args.password)
    headers = make_headers(token, args.user, args.password, args.basic_auth)

    print(f"=== POSICIONES: {args.account} ===")
    positions = get_positions(headers, args.account)
    show_summary(positions)

    if args.detail:
        dp = get_detailed_positions(headers, args.account)
        show_detail(dp)


if __name__ == "__main__":
    main()
