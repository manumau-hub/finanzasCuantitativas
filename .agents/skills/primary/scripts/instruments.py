#!/usr/bin/env python3
"""
Lista segmentos e instrumentos de Primary API (Matba ROFEX).

Uso:
    python scripts/instruments.py --user USER --password PASS
    python scripts/instruments.py --user USER --password PASS --segment DDF --cfi FXXXSX
"""

import argparse
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


def list_segments(headers):
    r = requests.get(f"{BASE_URL}/rest/segment/all", headers=headers)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        print(f"Error: {data}", file=sys.stderr)
        return
    print(f"{'Segmento':<12} {'Market ID':<10}")
    print("-" * 22)
    for seg in data.get("segments", []):
        print(f"{seg['marketSegmentId']:<12} {seg['marketId']:<10}")


def list_instruments(headers, segment=None, cfi=None, detail=False):
    if detail:
        url = f"{BASE_URL}/rest/instruments/details"
    else:
        url = f"{BASE_URL}/rest/instruments/all"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        print(f"Error: {data}", file=sys.stderr)
        return
    instruments = data.get("instruments", [])
    if segment:
        instruments = [i for i in instruments if i.get("segment", {}).get("marketSegmentId") == segment]
    if cfi:
        instruments = [i for i in instruments if i.get("cficode") == cfi]
    if not instruments:
        print("No se encontraron instrumentos.")
        return
    def _fmt(val, default="?"):
        return val if val is not None else default

    if detail:
        print(f"{'Símbolo':<25} {'Segmento':<8} {'CFI':<8} {'Moneda':<6} {'Venc.':<10} {'Min':<8} {'Max':<10}")
        print("-" * 80)
        for inst in instruments:
            sym = inst.get("instrumentId", {}).get("symbol", "") or inst.get("securityDescription", "")
            print(
                f"{_fmt(sym):<25} "
                f"{_fmt(inst.get('segment', {}).get('marketSegmentId')):<8} "
                f"{_fmt(inst.get('cficode')):<8} "
                f"{_fmt(inst.get('currency')):<6} "
                f"{_fmt(inst.get('maturityDate')):<10} "
                f"{_fmt(inst.get('lowLimitPrice')):<8} "
                f"{_fmt(inst.get('highLimitPrice')):<10}"
            )
    else:
        print(f"{'Símbolo':<30} {'Market ID':<8} {'CFI Code':<8}")
        print("-" * 50)
        for inst in instruments:
            sym = inst.get("instrumentId", {}).get("symbol", "?")
            mid = inst.get("instrumentId", {}).get("marketId", "?")
            cfi_code = inst.get("cficode", "?")
            print(f"{sym:<30} {mid:<8} {cfi_code:<8}")
    print(f"\nTotal: {len(instruments)} instrumentos")


def main():
    parser = argparse.ArgumentParser(description="Listar segmentos e instrumentos de Primary API")
    parser.add_argument("--user", default=os.getenv("PRIMARY_USER"), help="Usuario Primary (o env PRIMARY_USER)")
    parser.add_argument("--password", default=os.getenv("PRIMARY_PASSWORD"), help="Contraseña (o env PRIMARY_PASSWORD)")
    parser.add_argument("--segment", help="Filtrar por segmento (DDF, DDA, etc)")
    parser.add_argument("--cfi", help="Filtrar por código CFI (FXXXSX, OCAFXS, etc)")
    parser.add_argument("--detail", action="store_true", help="Mostrar detalle completo de instrumentos")
    parser.add_argument("--segments-only", action="store_true", help="Solo listar segmentos")
    args = parser.parse_args()

    if not args.user or not args.password:
        parser.print_help()
        print("\nERROR: Se requieren --user y --password (o env PRIMARY_USER, PRIMARY_PASSWORD)")
        sys.exit(1)

    token = get_token(args.user, args.password)
    headers = {"X-Auth-Token": token}

    if args.segments_only:
        list_segments(headers)
        return

    print("=== SEGMENTOS ===")
    list_segments(headers)
    print()

    if args.segment or args.cfi:
        print(f"=== INSTRUMENTOS (filtro: segment={args.segment or '*'}, cfi={args.cfi or '*'}) ===")
        list_instruments(headers, segment=args.segment, cfi=args.cfi, detail=args.detail)
    else:
        print("=== TODOS LOS INSTRUMENTOS ===")
        list_instruments(headers, detail=args.detail)


if __name__ == "__main__":
    main()
