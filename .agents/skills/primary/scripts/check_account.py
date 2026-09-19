#!/usr/bin/env python3
"""
Reporte de cuenta de Primary API (Risk API).

Uso:
    python scripts/check_account.py --user USER --password PASS --account TU_CUENTA
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


def account_report(headers, account):
    r = requests.get(
        f"{BASE_URL}/rest/risk/accountReport/{account}",
        headers=headers,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        print(f"Error: {data.get('description', data)}", file=sys.stderr)
        return
    ad = data["accountData"]
    print(f"=== REPORTE DE CUENTA: {account} ===")
    print(f"  Market Member: {ad.get('marketMember', '?')}")
    print(f"  Member Identity: {ad.get('marketMemberIdentity', '?')}")
    print()
    print(f"  Colateral:          {ad.get('collateral', 0):>16.2f}")
    print(f"  Margen:             {ad.get('margin', 0):>16.2f}")
    print(f"  Disponible colateral: {ad.get('availableToCollateral', 0):>16.2f}")
    print(f"  Portfolio:          {ad.get('portfolio', 0):>16.2f}")
    print(f"  Daily Diff:         {ad.get('dailyDiff', 0):>16.2f}")
    print(f"  Current Cash:       {ad.get('currentCash', 0):>16.2f}")
    print(f"  Uncovered Margin:   {ad.get('uncoveredMargin', 0):>16.2f}")

    detail = ad.get("detailedAccountReports", {})
    if detail:
        print("\n=== SALDOS POR MONEDA ===")
        for report_id, report_data in detail.items():
            cur_balance = report_data.get("currencyBalance", {}).get("detailedCurrencyBalance", {})
            if cur_balance:
                print(f"{'Moneda':<10} {'Consumido':<15} {'Disponible':<15}")
                print("-" * 40)
                for currency, balances in cur_balance.items():
                    print(f"{currency:<10} {balances.get('consumed', 0):<15} {balances.get('available', 0):<15}")

        print("\n=== DISPONIBLE PARA OPERAR ===")
        for report_id, report_data in detail.items():
            op = report_data.get("availableToOperate", {})
            cash = op.get("cash", {})
            print(f"  Total Cash:     {cash.get('totalCash', 0):>16.2f}")
            det = cash.get("detailedCash", {})
            if det:
                for currency, amount in det.items():
                    print(f"    {currency:<12} {amount:>12.2f}")
            print(f"  Movements:      {op.get('movements', 0):>16}")
            credit = op.get('credit')
            print(f"  Credit:         {credit if credit is not None else 0:>16}")
            print(f"  Total Operable: {op.get('total', 0):>16.2f}")


def main():
    parser = argparse.ArgumentParser(description="Reporte de cuenta de Primary API")
    parser.add_argument("--user", default=os.getenv("PRIMARY_USER"), help="Usuario (o env PRIMARY_USER)")
    parser.add_argument("--password", default=os.getenv("PRIMARY_PASSWORD"), help="Contraseña (o env PRIMARY_PASSWORD)")
    parser.add_argument("--account", default=os.getenv("PRIMARY_ACCOUNT"), help="Cuenta (o env PRIMARY_ACCOUNT)")
    parser.add_argument("--basic-auth", action="store_true", help="Usar HTTP Basic Auth (requerido en LIVE)")
    args = parser.parse_args()

    if not args.user or not args.password or not args.account:
        parser.print_help()
        print("\nERROR: Se requieren --user, --password y --account (o env PRIMARY_USER, PRIMARY_PASSWORD, PRIMARY_ACCOUNT)")
        sys.exit(1)

    token = get_token(args.user, args.password)
    headers = make_headers(token, args.user, args.password, args.basic_auth)
    account_report(headers, args.account)


if __name__ == "__main__":
    main()
