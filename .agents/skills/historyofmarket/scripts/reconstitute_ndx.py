"""
Reconstituir los miembros del Nasdaq 100 en una fecha historica dada.

Uso:
    py scripts/reconstitute_ndx.py 2020-01-01
    py scripts/reconstitute_ndx.py 2020-01-01 --json

El script descarga:
  - /api/nasdaq/100.json          (miembros actuales NDX)
  - /api/ndx/changes.json         (historial de adds/removes)

Luego aplica los cambios en reversa desde hoy hasta la fecha objetivo
para determinar la lista de miembros en esa fecha.
"""

import json
import sys
from datetime import datetime, date
from urllib.request import urlopen

BASE = "https://historyofmarket.com"


def fetch_json(path):
    url = f"{BASE}{path}"
    with urlopen(url) as r:
        return json.loads(r.read().decode())


def reconstitute(target_date: date):
    constituents = fetch_json("/api/nasdaq/100.json")
    changes = fetch_json("/api/ndx/changes.json")

    current = {c["ticker"]: c for c in constituents}

    sorted_changes = sorted(
        [c for c in changes if c.get("date")],
        key=lambda x: x["date"],
        reverse=True,
    )

    members = dict(current)

    for ch in sorted_changes:
        ch_date = datetime.strptime(ch["date"], "%Y-%m-%d").date()
        if ch_date < target_date:
            break

        removed_tickers = ch.get("removed", [])
        added_tickers = ch.get("added", [])

        for t in removed_tickers:
            if t in members:
                del members[t]

        for t in added_tickers:
            members.pop(t, None)

    return list(members.keys())


def main():
    if len(sys.argv) < 2:
        print("Uso: py reconstitute_ndx.py YYYY-MM-DD [--json]", file=sys.stderr)
        sys.exit(1)

    target = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    tickers = reconstitute(target)

    if "--json" in sys.argv:
        print(json.dumps({"date": str(target), "members": tickers, "count": len(tickers)}, indent=2))
    else:
        print(f"Nasdaq 100 constituyentes al {target}: {len(tickers)} miembros")
        for t in sorted(tickers):
            print(t)


if __name__ == "__main__":
    main()
